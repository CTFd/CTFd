FROM python:3.9-slim

# добавить в контейнер команду ping
RUN apt-get update && \
    apt-get install -y iputils-ping && \
    rm -rf /var/lib/apt/lists/*


RUN pip install Flask

WORKDIR /app

COPY . /app

EXPOSE 5001

CMD ["python", "app.py"]
