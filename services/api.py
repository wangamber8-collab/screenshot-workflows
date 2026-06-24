from fastapi import FastAPI, Header, HTTPException
from dotenv import load_dotenv #temporary
import os
from celery_app import app as celery_app

load_dotenv()

app = FastAPI()
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

@app.post("/enqueue/vision")
async def enqueue_vision(screenshot_id: str, x_webhook_secret: str = Header(None)):
    if x_webhook_secret != WEBHOOK_SECRET:
        raise HTTPException(
            status_code = 401,
            detail = "Invalid request"
        )
    else:
        celery_app.send_task(
            "vision.process",
            args = [screenshot_id],
            queue = "vision"
        )
        return {"status": "queued"}


