FROM python:3.9-slim

WORKDIR /app

COPY . /app

# Установка зависимостей в контейнер
RUN pip install Flask

# Открыть порт для приложения
EXPOSE 5000

# Run app.py when the container launches
CMD ["python", "app.py"]

