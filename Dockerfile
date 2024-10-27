# Используем базовый образ Python
FROM python:3.12-slim

# Устанавливаем зависимости
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код бота в контейнер
COPY ./app /app
COPY alembic /app/alembic
COPY alembic.ini /app

# RUN alembic upgrade head

# Запускаем бота
CMD ["python", "/app/app.py"]