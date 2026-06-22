import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.client import supabase
import requests
from sklearn.metrics.pairwise import cosine_similarity
import json


def get_embeddings() :
    #fetches vision_done screenshots, gets their embeddings
    response = supabase.table("screenshots").select("id, embedding, description, user_id").eq("status", "embedding_done").order("processed_at", desc = False).execute()
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

    users = {}
    for row in rows:
        users.setdefault(row["user_id"], []).append(row)

    threshold = 0.75
    
    for user_id, user_rows in users.items():
        #set first group
        first = user_rows[0]
        group_label = get_label(first["description"])
        print(group_label)

        result = supabase.table("workflow_sets").insert({
            "label": group_label,
            "user_id": user_id
        }).execute()

        most_recent_id = result.data[0]["id"]
        curr_group_count = 1

        supabase.table("screenshots").update({
            "workflow_set_id": most_recent_id,
            "status": "grouping_done"
        }).eq("id", first["id"]).execute()

        for i in range(1, len(user_rows)) :
            x = user_rows[i-1]["embedding"]
            y = user_rows[i]["embedding"]
            similarity = cosine_similarity([json.loads(x)], [json.loads(y)])[0][0]

            if similarity > threshold :
                #same group
                curr_group_count += 1
                supabase.table("screenshots").update({
                    "workflow_set_id": most_recent_id,
                    "status": "grouping_done"
                }).eq("id", user_rows[i]["id"]).execute()

                supabase.table("workflow_sets").update({
                    "screenshot_count": curr_group_count
                }).eq("id", most_recent_id).execute()
            else :
                #new group
                new_label = get_label(user_rows[i]["description"])
                print(new_label)

                result = supabase.table("workflow_sets").insert({
                    "label": new_label,
                    "user_id": user_id
                }).execute()

                most_recent_id = result.data[0]["id"]
                curr_group_count = 1

                supabase.table("screenshots").update({
                    "workflow_set_id": most_recent_id,
                    "status": "grouping_done"
                }).eq("id", user_rows[i]["id"]).execute()

if __name__ == "__main__":
    set_groups()


