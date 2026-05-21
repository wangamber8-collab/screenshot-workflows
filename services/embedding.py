import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.client import supabase
from dotenv import load_dotenv
import requests

load_dotenv()

def get_embeddings() :
    #fetches vision_done screenshots, gets their embeddings, and updates the database
    response = supabase.table("screenshots").select("*").eq("status", "vision_done").execute()
    images = response.data
    for image in images :
        try:
            model_response = requests.post(f"{os.getenv('OLLAMA_URL')}/api/embeddings", json={
                "model": "nomic-embed-text:latest",
                "input": image["description"]
            })
            embedding = model_response.json().get("embeddings", [])[0]

            if embedding:
                supabase.table("screenshots").update({
                    "embedding": embedding
                }).eq("id", image["id"]).execute()
            else :
                supabase.table("screenshots").update({"status" : "failed"}).eq("id", image["id"]).execute()
        except Exception as e:
            print(f"Error getting embedding: {e}")
            supabase.table("screenshots").update({"status" : "failed"}).eq("id", image["id"]).execute()

            
