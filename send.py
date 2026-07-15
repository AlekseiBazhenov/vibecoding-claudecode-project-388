#!/usr/bin/env python3
"""Отправка текстового сообщения в Telegram через Bot API.

Навык `tracker` формирует короткую человекочитаемую сводку значимых изменений
цен (одна строка на изменение) и передаёт её этому скрипту, а тот отправляет
сообщение в Telegram.

Использование:
    python send.py "текст сообщения"
    echo "текст сообщения" | python send.py

Сообщение берётся из аргументов командной строки (все аргументы объединяются
через пробел). Если аргументов нет — читается из stdin.

Конфигурация через переменные окружения:
    TELEGRAM_BOT_TOKEN  — токен бота (обязательно).
    TELEGRAM_CHAT_ID    — идентификатор чата/канала получателя (обязательно).

Используется только стандартная библиотека Python — внешних зависимостей нет.
"""
import json
import os
import sys
import urllib.error
import urllib.request


def read_message() -> str:
    """Взять сообщение из argv, а при их отсутствии — из stdin."""
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:]).strip()
    return sys.stdin.read().strip()


def send(text: str) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    missing = [
        name
        for name, value in (
            ("TELEGRAM_BOT_TOKEN", token),
            ("TELEGRAM_CHAT_ID", chat_id),
        )
        if not value
    ]
    if missing:
        sys.exit("Не заданы переменные окружения: " + ", ".join(missing))

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": text}).encode("utf-8")
    request = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(request) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", "replace")
        sys.exit(f"Telegram API вернул ошибку {exc.code}: {details}")
    except urllib.error.URLError as exc:
        sys.exit(f"Не удалось связаться с Telegram API: {exc.reason}")

    if not body.get("ok"):
        sys.exit(f"Telegram API отклонил сообщение: {body}")


def main() -> None:
    text = read_message()
    if not text:
        sys.exit("Пустое сообщение — отправлять нечего.")
    send(text)


if __name__ == "__main__":
    main()
