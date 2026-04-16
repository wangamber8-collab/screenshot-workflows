# Establish a connection to the database
import os
from dotenv import load_dotenv
from supabase import create_client
import pathlib 
load_dotenv(pathlib.Path(__file__).parent.parent / '.env')
supabase = create_client(os.getenv("DB_URL"), os.getenv("DB_SERVICE_KEY"))