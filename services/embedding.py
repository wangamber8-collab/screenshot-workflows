import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.client import supabase
import requests
from services.celery_app import app
from services.grouping.tasks import set_group

@app.task(name="embedding.process")
def set_embedding(screenshot_id) :
    #fetches vision_done screenshots, gets their embeddings, and updates the database
    response = (
        supabase.table("screenshots")
        .select("description")
        .eq("id", screenshot_id)
        .eq("status", "vision_done").execute()
    )

    if not response.data:
        print(f"No screenshot found with ID {screenshot_id} or screenshot shouldn't be on queue")
        return

    image = response.data[0]
    try:
        model_response = requests.post(f"{os.getenv('OLLAMA_URL')}/api/embeddings", json={
            "model": "nomic-embed-text:latest",
            "prompt": image["description"]
        })
        embedding = model_response.json().get("embedding", [])

        if embedding:
            supabase.table("screenshots").update({
                "embedding": embedding,
                "status" : "embedding_done"
            }).eq("id", screenshot_id).execute()

            set_group.delay(screenshot_id)
        else :
            supabase.table("screenshots").update({"status" : "failed"}).eq("id", screenshot_id).execute()
    except Exception as e:
        print(f"Error getting embedding: {e}")
        supabase.table("screenshots").update({"status" : "failed"}).eq("id", screenshot_id).execute()          
