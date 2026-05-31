import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.client import supabase
import requests
from sklearn.metrics.pairwise import cosine_similarity
import json


def get_embeddings() :
    #fetches vision_done screenshots, gets their embeddings
    response = supabase.table("screenshots").select("id, embedding, description").eq("status", "embedding_done").order("processed_at", desc = False).execute()
    return response.data

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

def set_groups() :
    #Sets groups for screenshots based on embedding similarity and updates the database.
    rows = get_embeddings()

    #ensure there are at least 1 row to compare
    if len(rows) == 0:
        return

    #set first group
    first = rows[0]
    group_label = get_label(first["description"])

    threshold = 0.75
    
    #set first group
    first = rows[0]
    group_label = get_label(first["description"])

    result = supabase.table("workflow_sets").insert({
        "label": group_label
    }).execute()

    most_recent_id = result.data[0]["id"]
    curr_group_count = 1

    supabase.table("screenshots").update({
        "workflow_set_id": most_recent_id,
        "status": "grouping_done"
    }).eq("id", first["id"]).execute()

    for i in range(1, len(rows)) :
        x = rows[i-1]["embedding"]
        y = rows[i]["embedding"]
        similarity = cosine_similarity([json.loads(x)], [json.loads(y)])[0][0]

        if similarity > threshold :
            #same group
            curr_group_count += 1
            supabase.table("screenshots").update({
                "workflow_set_id": most_recent_id,
                "status": "grouping_done"
            }).eq("id", rows[i]["id"]).execute()

            supabase.table("workflow_sets").update({
                "screenshot_count": curr_group_count
            }).eq("id", most_recent_id).execute()
        else :
            #new group
            new_label = get_label(rows[i]["description"])

            result = supabase.table("workflow_sets").insert({
                "label": new_label
            }).execute()

            most_recent_id = result.data[0]["id"]
            curr_group_count = 1

            supabase.table("screenshots").update({
                "workflow_set_id": most_recent_id,
                "status": "grouping_done"
            }).eq("id", rows[i]["id"]).execute()

if __name__ == "__main__":
    set_groups()


