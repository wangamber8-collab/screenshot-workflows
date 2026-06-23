import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.client import supabase
import requests
import json
import numpy as np
from services.celery_app import app

def get_label(description):
    #description: screenshot description
    #returns a label for a given description
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

def get_centroid(v1, v2, n):
    #v1: new embedding that is being added to the cluster
    #v2: current centroid of cluster
    #n: number of items in cluster
    #Calculates the new centroid for cluster
    embedding = np.array(json.loads(v1), dtype=np.float32)
    centroid = np.array(json.loads(v2), dtype=np.float32)
    return (centroid * n + embedding)/(n + 1)

@app.task(name="grouping.process")
def set_group(screenshot_id) :
    #finds the right workflow group for screenshot or creates a new one
    row = supabase.table("screenshots").select("embedding, description, user_id").eq("id", screenshot_id).execute().data[0]
    threshold = 0.8

    result = supabase.rpc(
        "match_cluster", 
        {"new_embedding": row["embedding"], "match_user_id": row["user_id"], "threshold" : threshold}
    ).execute()

    if not result.data:
        #new group
        label = get_label(row["description"])

        new_row = supabase.table("workflow_sets").insert({
            "label": label,
            "user_id": row["user_id"],
            "centroid": row["embedding"]
        }).execute()

        supabase.table("screenshots").update({
            "workflow_set_id": new_row.data[0]["id"],
            "status": "grouping_done"
        }).eq("id", screenshot_id).execute()
    else:
        #add to existing group
        group = result.data[0]
        screenshots_count = group["screenshot_count"]
        centroid = get_centroid(row["embedding"], group["centroid"], screenshots_count)

        new_row = supabase.table("workflow_sets").update({
            "screenshot_count": screenshots_count + 1,
            "centroid": centroid.tolist()
        }).eq("id", group["id"]).execute()

        supabase.table("screenshots").update({
            "workflow_set_id": group["id"],
            "status": "grouping_done"
        }).eq("id", screenshot_id).execute()           

