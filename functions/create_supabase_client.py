import os
from supabase import create_client, Client
from dotenv import load_dotenv

def create_supabase_client():
    load_dotenv()

    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)

    return supabase
