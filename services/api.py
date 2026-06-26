from fastapi import FastAPI, Header, HTTPException
import os
from services.celery_app import app as celery_app
from pydantic import BaseModel

app = FastAPI()
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

class EnqueueRequest(BaseModel):
    screenshot_id : str

@app.post("/enqueue/vision")
async def enqueue_vision(request: EnqueueRequest, x_webhook_secret: str = Header(None)):
    if x_webhook_secret != WEBHOOK_SECRET:
        raise HTTPException(
            status_code = 401,
            detail = "Invalid request"
        )
    else:
        celery_app.send_task(
            "vision.process",
            args = [request.screenshot_id],
            queue = "vision"
        )
        return {"status": "queued"}


