import os, json, asyncio
from db import ChronicleDB
from telegram_api import TelegramAPI
from bitwarden_helper import BitwardenHelper
from meme_scanner import MemeScanner
import openai

class Orchestrator:
    def __init__(self):
        self.env = os.environ
        self.db = ChronicleDB()
        self.telegram = TelegramAPI(token=os.getenv("TELEGRAM_BOT_TOKEN"))
        self.bw = BitwardenHelper()
        self.meme_scanner = MemeScanner(self.db, self.bw)
        self.openai_key = os.getenv("OPENAI_API_KEY")

    async def startup(self):
        # init DB
        self.db.connect()
        # set openai key for library
        openai.api_key = self.openai_key
        # start background tasks (meme scanner loop)
        asyncio.create_task(self._meme_scan_loop())
        print("Orchestrator started")

    async def handle_telegram_update(self, update_json):
        # basic router
        msg = update_json.get("message", {})
        text = msg.get("text", "")
        chat_id = msg.get("chat", {}).get("id")
        # log the message
        await self.db.log_event("telegram_inbound", update_json)
        if text.startswith("/status"):
            await self.telegram.send_message(chat_id, "GPT-Z Control Core: online")
            return {"ok": True}
        if text.startswith("/scan_meme"):
            hits = await self.meme_scanner.scan_once()
            await self.telegram.send_message(chat_id, f"Found {len(hits)} hits. See Chronicle.")
            return {"ok": True}
        # fallback: forward to LLM for a short response
        resp = await self.ask_openai(f"User: {text}\nReply concisely as GPT-Z.")
        await self.telegram.send_message(chat_id, resp[:4000])
        return {"ok": True}

    async def ask_openai(self, prompt):
        import openai
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role":"system","content":"You are GPT-Z."},{"role":"user","content":prompt}],
            max_tokens=600
        )
        return resp["choices"][0]["message"]["content"]

    async def _meme_scan_loop(self):
        # simple scheduler: run scanner every X seconds (configurable)
        import time
        interval = int(os.getenv("MEME_SCAN_INTERVAL", 60))
        while True:
            try:
                hits = await self.meme_scanner.scan_once()
                if hits:
                    # log and notify admin chat
                    await self.db.log_event("meme_hits", hits)
                    # notify a pre-configured admin chat id
                    admin_chat = int(os.getenv("ADMIN_TELEGRAM_CHAT_ID", "0"))
                    if admin_chat:
                        await self.telegram.send_message(admin_chat, f"Meme hits: {json.dumps(hits)[:3000]}")
            except Exception as e:
                await self.db.log_event("meme_scan_error", {"error": str(e)})
            await asyncio.sleep(interval)
