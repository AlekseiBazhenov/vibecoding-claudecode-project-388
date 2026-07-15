#!/usr/bin/env python3
"""Отправка сообщения в Telegram через Bot API.

Использует только стандартную библиотеку (urllib), без внешних зависимостей.
Токен и chat id берутся из переменных окружения:
    TELEGRAM_BOT_TOKEN  — токен бота (от @BotFather)
    TELEGRAM_CHAT_ID    — идентификатор чата/пользователя

Запуск:
    python send.py "текст сообщения"
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


def send_message(token: str, chat_id: str, text: str) -> dict:
    """Отправляет сообщение и возвращает разобранный ответ Telegram API."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode("utf-8")

    request = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    if len(sys.argv) != 2 or not sys.argv[1].strip():
        print('Использование: python send.py "текст сообщения"', file=sys.stderr)
        return 2

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
        print(
            "Не заданы переменные окружения: " + ", ".join(missing),
            file=sys.stderr,
        )
        return 2

    text = sys.argv[1]

    try:
        result = send_message(token, chat_id, text)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"Ошибка HTTP {exc.code}: {body}", file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"Сетевая ошибка: {exc.reason}", file=sys.stderr)
        return 1

    if not result.get("ok"):
        print(f"Telegram API вернул ошибку: {result}", file=sys.stderr)
        return 1

    print("Сообщение отправлено.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
