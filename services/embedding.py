import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.client import supabase
from dotenv import load_dotenv

load_dotenv()

response = supabase.table("screenshots").select("*").eq("status", "vision_done").execute()
images = response.data
