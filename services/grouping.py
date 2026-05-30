import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.client import supabase
import requests
from sklearn.metrics.pairwise import cosine_similarity


def get_embeddings() :
    #fetches vision_done screenshots, gets their embeddings
    response = supabase.table("screenshots").select("id, embedding, description").eq("status", "embedding_done").order("created_at", desc = False).execute()
    return response.data

def get_label(description):
    #generates a label for a given description
    prompt = f"Given this screenshot description, generate a short 4-6 word label that summarizes the workflow being performed. Be specific about the application and action. Respond with only the label, no explanation. Description: {description}"
    try:
        response = requests.post(f"{os.getenv('OLLAMA_URL')}/api/generate", json={
            "model": "qwen3-vl:4b",
            "prompt": prompt,
            "stream": False
        })
        return response.json().get("response", "")
    except Exception as e:
        print(f"Error generating label: {e}")
        return ""

def get_cosine() :
    rows = get_embeddings()
    
    #set first group
    first = rows[0]
    group_label = get_label(first["description"])
    
    threshold = 0.75
    #ensure there are at least 2 rows to compare
    if len(rows) < 2:
        return
    for i in range(len(rows) - 1) :
        x = rows[i]
        y = rows[i + 1]
        similarity = cosine_similarity([x["embedding"]], [y["embedding"]])[0][0]
        


