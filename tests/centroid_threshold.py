import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.client import supabase
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

threshold = 0.8
rows = supabase.table("screenshots").select("id, embedding").execute()
groups = []

for row in rows.data:
    embedding = np.array(json.loads(row["embedding"]), dtype = np.float32)

    if not groups:
        groups.append({"centroid": embedding, "members": [row["id"][:8]]})
        continue
    
    centroids = np.array([group["centroid"] for group in groups])
    scores = cosine_similarity([embedding], centroids)[0]
    best_idx = np.argmax(scores)
    best_score = scores[best_idx]

    if best_score >= threshold:
        g = groups[best_idx]
        n = len(g["members"])
        g["centroid"] = (g["centroid"] * n + embedding) / (n + 1)
        g["members"].append(row["id"][:8])
    else:
        groups.append({"centroid": embedding, "members": [row["id"][:8]]})

for i, group in enumerate(groups):
    print(f"Group {i+1}: {group['members']}")
