"""Send messages to a Telegram chat/channel via the Bot API."""

import os

import requests

TELEGRAM_MESSAGE_LIMIT = 4096


class TelegramError(RuntimeError):
    pass


def send_message(text: str) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise TelegramError("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID environment variables are not set")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    for chunk in _split_message(text):
        response = requests.post(
            url,
            data={
                "chat_id": chat_id,
                "text": chunk,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            },
            timeout=30,
        )
        if not response.ok:
            raise TelegramError(f"Telegram API error {response.status_code}: {response.text}")


def _split_message(text: str) -> list[str]:
    if len(text) <= TELEGRAM_MESSAGE_LIMIT:
        return [text]
    chunks = []
    while text:
        chunks.append(text[:TELEGRAM_MESSAGE_LIMIT])
        text = text[TELEGRAM_MESSAGE_LIMIT:]
    return chunks
