import streamlit as st
from PIL import Image
from datetime import datetime   
from functions.fetch_data_from_database import fetch_data_from_database
from functions.create_supabase_client import create_supabase_client
from dotenv import load_dotenv
load_dotenv()
from streamlit_javascript import st_javascript
from functions.get_signed_logo_url import get_signed_logo_url
from logic.accept import accept
from logic.decline import decline
import time

# Konfiguration der Streamlit-Seite
st.set_page_config(page_title="Rabattoptionen", layout="wide")

# Abrufen der aktuellen URL und Extrahieren des Hash-Codes
url = str(st_javascript("await fetch('').then(r => window.parent.location.href)")) 

time.sleep(1)
link = url.split("/")[-1]
if len(url.split("/")) > 0:

    hash_code = link.split('#')[1]
    decision = link.split('#')[0]

    # Erstellen des Supabase-Clients
    client = create_supabase_client()



    if "accept" in decision:
        accept(hash_code, client)
        
    elif "decline" in decision:
        # Laden des Header-Logos
        decline(client, hash_code)