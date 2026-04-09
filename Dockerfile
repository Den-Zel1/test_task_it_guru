FROM python:3.12-slim-bookworm

# Системные зависимости для Postgres
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Устанавливаем библиотеки напрямую через pip
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    sqlalchemy \
    psycopg2-binary \
    python-dotenv \
    pydantic

# Копируем все файлы проекта (.env, main.py, models.py и т.д.)
COPY . .

# Запуск сервера
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
