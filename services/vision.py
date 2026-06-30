import os
from db.client import supabase
import requests
import base64
from services.celery_app import app
from services.embedding import set_embedding


def get_response(image_data : str) -> str:
    #image_data: base-64 encoded string of the image
    #returns the image description or empty string on failure
    prompt = "Describe this screenshot in one concise paragraph. Focus on: what application is open, what the user is trying to accomplish, which UI elements are involved, and what action is being performed. Do not describe colors, fonts, or visual design. Write as if briefing someone who cannot see the screen."
    try:
        response = requests.post(f"{os.getenv('OLLAMA_URL')}/api/generate", json={
            "model": "qwen3-vl:4b",
            "prompt": prompt,
            "images" : [image_data],
            "stream": False
        })
        #print(f"Raw response: {response.json()}")
        print("done")
        return response.json().get("response", "")
    except Exception as e:
        print(f"Error: {e}")
        return ""

def convert_base64(image_url) :
    #image_url: image url
    #returns the base64 image
    with requests.get(image_url) as response:
        return base64.b64encode(response.content).decode("utf-8")

@app.task(name="vision.process")
def process_screenshot(screenshot_id) :
    #fetches unprocessed screenshot, gets the description, and updates the database
    response = (
        supabase.table("screenshots")
        .select("image_url")
        .eq("id", screenshot_id)
        .eq("status", "pending")
        .execute()
    )

    if not response.data:
        print(f"No screenshot found with ID {screenshot_id} or screenshot shouldn't be on queue")
        return

    image = response.data[0]

    try:
        converted = convert_base64(image["image_url"])
    except Exception as e:
        print("Error converting image")
        supabase.table("screenshots").update({"status" : "failed"}).eq("id", screenshot_id).execute()
        return
        
    description = get_response(converted)

    if description:
        supabase.table("screenshots").update({
            "description": description,
            "status": "vision_done"
        }).eq("id", screenshot_id).execute()

        set_embedding.delay(screenshot_id)
    else :
        supabase.table("screenshots").update({"status" : "failed"}).eq("id", screenshot_id).execute()


