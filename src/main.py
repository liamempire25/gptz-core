from fastapi import FastAPI, Request
import asyncio
from orchestrator import Orchestrator

app = FastAPI()
orch = Orchestrator()

@app.on_event("startup")
async def startup():
    await orch.startup()

@app.post("/webhook/telegram")
async def telegram_webhook(req: Request):
    data = await req.json()
    return await orch.handle_telegram_update(data)

@app.get("/health")
def health():
    return {"status":"ok"}
