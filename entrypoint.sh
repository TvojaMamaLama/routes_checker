#!/bin/bash

echo "Запуск скрипта при старте контейнера..."
python /app/main.py

echo "Запускаем cron..."
cron

echo "Ожидаем события, выводим логи cron:"
tail -f /var/log/cron.log
