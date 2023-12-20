FROM python:3.9-slim

WORKDIR /app


COPY . /app

RUN apt-get update && apt-get install -y gcc libsqlite3-dev

# ^ добавить поддержку sqlite v

RUN pip install Flask pysqlite3 python-dotenv

EXPOSE 5002

CMD ["python", "app.py"]

