# Establish a connection to the database
import os
from supabase import create_client

supabase = create_client(os.getenv("DB_URL"), os.getenv("DB_SERVICE_KEY"))