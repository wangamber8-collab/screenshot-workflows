import os
from dotenv import load_dotenv
from supabase import create_client
import requests
import base64

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

supabase = create_client(os.getenv("DB_URL"), os.getenv("DB_SERVICE_KEY"))

image_url = "https://picsum.photos/200"
image_data = base64.b64encode(requests.get(image_url).content).decode("utf-8")
    

supabase.table("screenshots").insert({
    "image_url": image_url,
    "image_data": image_data
}).execute()

#If insert was successful, print the new record: only description, embedding, workflow_set_id
#should be empty
def print_row() :
    response = supabase.table("screenshots").select("*").eq("image_url", image_url).execute()
    print(response.data)

print_row()

#Ollama test
try:
    r = requests.post(f"{os.getenv('OLLAMA_URL')}/api/generate", json={
        "model": "qwen3-vl:4b",
        "prompt": "In one word, describe what you see in this image",
        "images": [image_data],
        "stream": False
    })
    answer = r.json().get("response", "")
    print(answer)
    
    #Update database
    supabase.table("screenshots").update({"description": answer}).eq("image_url", image_url).execute()
    print_row()
    
except Exception as e:
    print(f"Error: {e}")



