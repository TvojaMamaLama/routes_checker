FROM python:3.9-slim

# Установим cron
RUN apt-get update && apt-get install -y cron

# Создадим рабочую директорию
WORKDIR /app

# Скопируем requirements.txt и установим зависимости
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Скопируем основной скрипт, crontab и entrypoint
COPY main.py main.py
COPY crontab /etc/cron.d/simple-cron
COPY entrypoint.sh /entrypoint.sh

# Права на cron-файл, entrypoint и регистрация
RUN chmod 0644 /etc/cron.d/simple-cron
RUN crontab /etc/cron.d/simple-cron
RUN chmod +x /entrypoint.sh

# Создадим лог-файл
RUN touch /var/log/cron.log

# Вместо запуска сразу cron, используем наш entrypoint
CMD ["/entrypoint.sh"]
