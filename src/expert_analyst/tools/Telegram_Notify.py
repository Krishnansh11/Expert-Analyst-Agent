from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import requests
import os
from dotenv import load_dotenv

load_dotenv(override=True)


class TelegramNotificationInput(BaseModel):
    """A message to be sent to the user"""
    message: str = Field(..., description="The message to be sent to the user.")

class TelegramNotificationTool(BaseTool):
    name: str = "Send a Telegram Notification"
    description: str = (
        "This tool is used to send a Telegram Notification to the user"
    )
    args_schema: Type[BaseModel] = TelegramNotificationInput

    def _run(self, message: str) -> str:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if not token or not chat_id:
            return (
                "Telegram config missing: set TELEGRAM_BOT_TOKEN and "
                "TELEGRAM_CHAT_ID in environment secrets."
            )

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",  # Allows basic formatting like *bold*
        }

        try:
            response = requests.post(url, data=payload, timeout=20)
            response.raise_for_status()
            data = response.json()
            if not data.get("ok"):
                return f"Telegram API error: {data}"
            return "Telegram notification sent successfully."
        except requests.RequestException as exc:
            return f"Telegram send failed: {exc}"



