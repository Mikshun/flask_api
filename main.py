import json
from dataclasses import dataclass

import requests
from flask import Flask, request
from flask_restful import Api, Resource
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

app = Flask(__name__)
api = Api(app)
engine = create_engine("postgresql+psycopg2://admin:admin@pgdb/victorine")

Session = sessionmaker(bind=engine)

session = Session()

Base = declarative_base()


@dataclass
class Question(Base):
    __tablename__ = 'victorine'

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer)
    question = Column(String)
    answer = Column(String)
    created_at = Column(DateTime)

    def __repr__(self):
        return f"{self.question_id},{self.question},{self.answer},{self.created_at}"

    def to_json(self):
        return {c.name: getattr(self, c.name) if c.name != 'created_at' else str(getattr(self, c.name)) for c in
                self.__table__.columns}


Base.metadata.create_all(bind=engine)


# noinspection PyArgumentList
def add_record(user: dict) -> None:
    new_record = Question(
        question_id=user.get('id'),
        question=user.get('question'),
        answer=user.get('answer'),
        created_at=user.get('created_at')
    )
    session.add(new_record)
    session.commit()

    return None


def get_all_records():
    records = session.query(Question).all()
    record_list = []
    for record in records:
        record_list.append(record.to_json())
    return record_list


def get_record(name) -> list:
    return len(session.query(Question).filter(Question.question_id == f'{name}').all())


def validator(check):
    if get_record(check.get('id')) == 0:
        return add_record(check)
    else:
        api_req = requests.get(f'https://jservice.io/api/random?count=1').text
        api_res = json.loads(api_req)
        return validator(api_res[0])


class Record(Resource):
    def get(self):
        return get_all_records(), 200

    def post(self):
        data = request.json.get('questions_num')
        if data:
            api_req = requests.get(f'https://jservice.io/api/random?count={data}').text
            api_res = json.loads(api_req)

        for question in api_res:
            validator(question)

        if len(session.query(Question).all()) > 1:
            return session.query(Question).order_by(Question.id.desc())[1].to_json(), 201
        else:
            return None, 201


api.add_resource(Record, '/api/user')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
