import os
import requests
import difflib
from datetime import datetime

URL = "https://iplist.opencck.org/?format=bat&data=cidr4&site=pornhub.com&site=youtube.com&site=chatgpt.com&site=instagram.com"
DATA_FILE_PATH = "/app/data/data.bat"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

def send_telegram_message(message: str):
    """Отправить текстовое сообщение в телеграм."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Не заданы TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID. Сообщение не отправлено.")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print("Сообщение успешно отправлено в телеграм.")
    except Exception as e:
        print(f"Ошибка при отправке сообщения в телеграм: {e}")

def send_telegram_file(file_path: str, caption: str = ""):
    """Отправить файл (document) в телеграм."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Не заданы TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID. Файл не отправлен.")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "caption": caption
    }

    # Открываем файл для отправки
    with open(file_path, "rb") as f:
        files = {"document": f}
        try:
            response = requests.post(url, files=files, data=data)
            response.raise_for_status()
            print("Файл успешно отправлен в телеграм.")
        except Exception as e:
            print(f"Ошибка при отправке файла в телеграм: {e}")

def main():
    # Шаг 1. Пытаемся скачать новые данные
    try:
        response = requests.get(URL, timeout=30)
        response.raise_for_status()
        new_data = response.text
    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        # В любом случае отправляем уведомление
        send_telegram_message("Синхронизация завершена с ошибкой при скачивании данных.")
        return

    new_lines = new_data.splitlines()
    new_lines_set = set(new_lines)

    # Шаг 2. Проверяем, существует ли файл с предыдущими данными
    if not os.path.exists(DATA_FILE_PATH):
        # Файла нет — всё, что скачали, считаем новыми строками
        added_lines_count = len(new_lines)
        
        # Сохраняем файл
        os.makedirs(os.path.dirname(DATA_FILE_PATH), exist_ok=True)
        with open(DATA_FILE_PATH, "w", encoding="utf-8") as f:
            f.write(new_data)

        print(f"Файл не найден. Создали новый файл. Добавлено строк: {added_lines_count}.")
        send_telegram_message(f"Синхронизация прошла успешно. Создан новый файл. Добавлено строк: {added_lines_count}.")
        return

    # Шаг 3. Если файл есть, читаем старые данные
    with open(DATA_FILE_PATH, "r", encoding="utf-8") as f:
        old_data = f.read()

    old_lines = old_data.splitlines()
    old_lines_set = set(old_lines)

    # Считаем, сколько новых строк появилось
    added_lines = new_lines_set - old_lines_set
    added_lines_count = len(added_lines)

    # Шаг 4. Сравниваем старые и новые данные
    if old_data == new_data:
        # Никаких изменений по сравнению со старой версией,
        # но всё равно отправим сообщение с added_lines_count (будет 0)
        print("Данные не изменились.")
        send_telegram_message(f"Синхронизация прошла успешно. Новых строк: {added_lines_count}.")
        return
    else:
        # Есть отличия, значит часть строк могла добавиться, часть удалиться

        # Сохраним новый файл с пометкой времени
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        changed_file_path = f"/app/data/data_{timestamp}.bat"
        with open(changed_file_path, "w", encoding="utf-8") as f:
            f.write(new_data)

        # Отправим файл в телеграм
        caption_text = (
            "Обнаружены изменения в списке IP.\n"
            f"Новых строк: {added_lines_count}.\nНиже – полный обновлённый файл."
        )
        send_telegram_file(changed_file_path, caption=caption_text)

        # Перезапишем основной файл
        with open(DATA_FILE_PATH, "w", encoding="utf-8") as f:
            f.write(new_data)

        print(f"Обновлён файл данными. Новых строк: {added_lines_count}.")
        send_telegram_message(f"Синхронизация прошла успешно. Новых строк: {added_lines_count}.")

if __name__ == "__main__":
    main()
