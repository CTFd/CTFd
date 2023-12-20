FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc libsqlite3-dev

COPY . /app

RUN pip install Flask pysqlite3

EXPOSE 5002

CMD ["python", "app.py"]

