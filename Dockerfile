FROM python:3.10-alpine3.17
WORKDIR /usr/src/app
COPY reqieremnts.txt ./
RUN pip install -r reqieremnts.txt

EXPOSE 8080

CMD ["python3", "main.py"]
