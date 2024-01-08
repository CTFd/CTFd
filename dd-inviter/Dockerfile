FROM python:3.9-slim-buster as build

RUN pip install requests

WORKDIR /app

#COPY inviter.py /app

COPY . .

CMD [ "python", "/app/inviter.py" ]