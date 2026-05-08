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
        # Implementation goes here
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
          "chat_id": chat_id,
          "text": message,
          "parse_mode": "Markdown" # Allows basic formatting like *bold*
      }
        response = requests.post(url, data=payload)
        return response.json()



