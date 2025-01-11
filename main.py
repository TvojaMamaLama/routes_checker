import os
import requests
import difflib
from datetime import datetime

# URL, откуда берем данные
URL = "https://iplist.opencck.org/?format=bat&data=cidr4&site=pornhub.com&site=youtube.com&site=chatgpt.com&site=instagram.com"

# Основной файл с предыдущими данными
DATA_FILE_PATH = "/app/data/data.bat"

# Телеграм-бот и чат
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
    files = {"document": open(file_path, "rb")}
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "caption": caption
    }

    try:
        response = requests.post(url, files=files, data=data)
        response.raise_for_status()
        print("Файл успешно отправлен в телеграм.")
    except Exception as e:
        print(f"Ошибка при отправке файла в телеграм: {e}")
    finally:
        files["document"].close()

def main():
    # 1. Скачиваем новые данные
    try:
        response = requests.get(URL, timeout=30)
        response.raise_for_status()
        new_data = response.text
    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        return

    # 2. Проверяем, существует ли ранее сохранённый файл
    if not os.path.exists(DATA_FILE_PATH):
        # Файла нет - создаём и записываем новые данные
        os.makedirs(os.path.dirname(DATA_FILE_PATH), exist_ok=True)
        with open(DATA_FILE_PATH, "w", encoding="utf-8") as f:
            f.write(new_data)
        print("Файл не найден. Создали новый файл с полученными данными.")
        return

    # 3. Если файл есть, сравниваем
    with open(DATA_FILE_PATH, "r", encoding="utf-8") as f:
        old_data = f.read()

    if old_data == new_data:
        print("Данные не изменились. Никаких действий не требуется.")
        return
    else:
        # Найдём отличие (опционально, чтобы отправить короткое текстовое сообщение)
        diff_lines = difflib.unified_diff(
            old_data.splitlines(),
            new_data.splitlines(),
            fromfile="old_data.bat",
            tofile="new_data.bat",
            lineterm=""
        )
        diff_text = "\n".join(diff_lines)

        # Сохраним обновленные данные в новый файл (в том же виде)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        changed_file_path = f"/app/data/data_{timestamp}.bat"
        with open(changed_file_path, "w", encoding="utf-8") as f:
            f.write(new_data)

        # Отправим файл в телеграм
        caption_text = "Обнаружены изменения в списке IP.\nНиже – содержимое нового файла.\n\n"
        send_telegram_file(changed_file_path, caption=caption_text)

        # (Опционально) можем ещё отправить дифф текстом:
        # send_telegram_message("Обнаружены изменения:\n" + diff_text)

        # Перезаписываем основной файл новыми данными
        with open(DATA_FILE_PATH, "w", encoding="utf-8") as f:
            f.write(new_data)

        print("Файл обновлён новыми данными и отправлен в телеграм.")

if __name__ == "__main__":
    main()
