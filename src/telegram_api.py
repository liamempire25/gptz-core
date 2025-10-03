import os, httpx

class TelegramAPI:
    def __init__(self, token=None):
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.base = f"https://api.telegram.org/bot{self.token}"

    async def send_message(self, chat_id, text):
        url = f"{self.base}/sendMessage"
        async with httpx.AsyncClient() as c:
            await c.post(url, json={"chat_id": chat_id, "text": text})
