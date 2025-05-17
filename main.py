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

# Konfiguration der Streamlit-Seite
st.set_page_config(page_title="Rabattoptionen", layout="wide")

# Abrufen der aktuellen URL und Extrahieren des Hash-Codes
url = st_javascript("await fetch('').then(r => window.parent.location.href)") 
hash_code = url.split("/")[-1]
decision = url.split("/")[-2]
hash_code = 'diuekwfgbk3rwegb24'  # Temporärer Wert für den Hash-Code
  
# Erstellen des Supabase-Clients
client = create_supabase_client()

decision = 'decline'

if decision == "accept":
    accept(hash_code, client)
    
elif decision == "decline":
    # Laden des Header-Logos
    decline(client, hash_code)