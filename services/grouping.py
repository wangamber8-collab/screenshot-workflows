import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.client import supabase
import requests
from sklearn.metrics.pairwise import cosine_similarity


def get_embeddings() :
    #fetches vision_done screenshots, gets their embeddings
    response = supabase.table("screenshots").select("id, embedding").eq("status", "embedding_done").execute()
    return response.data

def get_cosine() :
    rows = get_embeddings()
    #ensure there are at least 2 rows to compare
    if len(rows) < 2:
        return
    for i in range(len(rows) - 1) :
        x = rows[i]
        y = rows[i + 1]
        similarity = cosine_similarity([x["embedding"]], [y["embedding"]])[0][0]
        #best threshold for now is 0.75

