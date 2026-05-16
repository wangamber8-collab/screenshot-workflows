from db.client import supabase
import os

def ingest_screenshots(folder_path):
    for filename in os.listdir(folder_path):
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.heic','.svg', '.raw')):
            continue
        
        file_path = os.path.join(folder_path, filename)

        with open(file_path, 'rb') as f:
            supabase.storage.from_('screenshots').upload(filename, f)
        signed = supabase.storage.from_('screenshots').create_signed_url(filename, 60*60*24*7) #7 day url
        url = signed['signedURL']

        supabase.table("screenshots").insert({
            "image_url": url,
            "status": "pending"
        })


        
