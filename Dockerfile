# 1. Берем актуальный и легкий образ Python (3.12 slim)
FROM python:3.12-slim

# 2. Настраиваем поведение Python в контейнере:
# Запрещаем создание .pyc файлов и включаем моментальный вывод логов в консоль
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3. Задаем рабочую директорию внутри контейнера
WORKDIR /app

# 4. Устанавливаем системные зависимости (нужны для работы PostgreSQL и сборки пакетов)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# 5. Копируем только файл зависимостей и устанавливаем библиотеки (используем кэш слоев)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 6. Копируем весь код проекта в рабочую директорию
COPY . .

# 7. Создаем непривилегированного пользователя для безопасности (важно для продакшена)
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app
USER appuser

# 8. Указываем порт, который слушает приложение
EXPOSE 8000

# 9. Команда запуска по умолчанию (для разработки оставляем runserver, 
# но в docker-compose для продакшена легко переопределим на gunicorn)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
