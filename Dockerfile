FROM python:3.9-slim

# Установим cron
RUN apt-get update && apt-get install -y cron

# Создадим рабочую директорию
WORKDIR /app

# Скопируем requirements.txt и установим зависимости
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Скопируем основной скрипт и crontab
COPY main.py main.py
COPY crontab /etc/cron.d/simple-cron

# Права на cron-файл и регистрация
RUN chmod 0644 /etc/cron.d/simple-cron
RUN crontab /etc/cron.d/simple-cron

# Создадим лог-файл
RUN touch /var/log/cron.log

# Запуск: cron + tail лога
CMD cron && tail -f /var/log/cron.log
