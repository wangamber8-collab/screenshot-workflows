#Testing screenshot similarity to find the best threshold
from sklearn.metrics.pairwise import cosine_similarity
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.client import supabase
import json

responses = supabase.table("screenshots").select("id, embedding").eq("status", "embedding_done").execute()
images = responses.data

for i in range(len(images) - 1):
    for j in range(i + 1, len(images)):
        x = images[i]["embedding"]
        y = images[j]["embedding"]
        similarity = cosine_similarity([json.loads(x)], [json.loads(y)])[0][0]
        print(f"{images[i]['id'][:8]} vs {images[j]['id'][:8]}: {similarity:.3f}")