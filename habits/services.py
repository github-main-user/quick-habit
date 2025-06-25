import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def send_telegram_message(chat_id: int, text: str) -> None:
    """
    Sends a message to a telegram chat by given chat_id.
    Requires the token to be set in settings.
    Raises exception for status.
    """

    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN isn't set, can't send the message")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}

    response = requests.post(url, payload)
    response.raise_for_status()
