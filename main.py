import streamlit as st
from PIL import Image
from datetime import datetime   
from functions.fetch_data_from_database import fetch_data_from_database
from functions.create_supabase_client import create_supabase_client
from dotenv import load_dotenv
load_dotenv()
from streamlit_javascript import st_javascript

# Konfiguration der Streamlit-Seite
st.set_page_config(page_title="Rabattoptionen", layout="wide")

# Abrufen der aktuellen URL und Extrahieren des Hash-Codes
url = st_javascript("await fetch('').then(r => window.parent.location.href)")
hash_code = url.split("/")[-1]
hash_code = 'diuekwfgbk3rwegb24'  # Temporärer Wert für den Hash-Code

# Erstellen des Supabase-Clients
client = create_supabase_client()

# Aktualisieren der Datenbank mit Zeitstempel und Erlaubnis
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
client.table("Locality").update({"last_allowed_at": timestamp}).eq("hash_code", str(hash_code)).execute()
client.table("Locality").update({"allowed_after_request": True}).eq("hash_code", str(hash_code)).execute()

# Abrufen der Daten aus der Datenbank
locality_data, discount_data = fetch_data_from_database(hash_code, client)
st.write(locality_data)
st.write(discount_data)

# Extrahieren relevanter Informationen aus den Daten
locality_id = locality_data["locality_id"].values[0]
locality_name = locality_data["name"].values[0]
email = locality_data["email_from_website"].values[0] if locality_data["email_from_website"].values[0] != None else locality_data["email_from_osm"].values[0]
phone_number = locality_data["phone_number"].values[0]
is_wheelchair_accessible = locality_data["wheelchair_accessible"].values[0]

# Laden des Header-Logos
header_logo = Image.open("media/HeaderDanke.png")

# Anzeige des Header-Bildes
col1, col2, col3 = st.columns([4, 6, 4])
with col2:
    st.image(header_logo, width=600, use_container_width=True)

# Begrüßungstext
st.markdown("""
    <div style='text-align: center; margin-top: 20px;'>
        <h1 style='font-size: 55px;'>Vielen Dank für Ihre Unterstützung!</h1>
        <p style='font-size: 35px; max-width: 800px; margin: 0 auto;'>
            Ihre Hilfe macht dieses Projekt nur möglich.
        </p>
        <p style='font-size: 26px; max-width: 1400px; margin: 0 auto; padding-top: 60px; padding-bottom: 60px;'>
            Unten können Sie einsehen, welche Informationen wir in unsere App integrieren werden und diese gegebenenfalls anpassen.
        </p>
    </div>
""", unsafe_allow_html=True)

# Anzeige der Rabattoptionen
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    st.title("🎯 Identifizierte Rabattoptionen")

    # Styling für Eingabefelder
    st.markdown(
        """
        <style>
        .stTextInput {
            margin: 0px 40px 40px 40px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Liste der Merkzeichen
    disability_marks = ["AG", "B", "BL", "H", "GL", "G", "TB"]

    # Iteration über die Rabattdaten
    for i, row in discount_data.iterrows():
        cols = st.columns(6)

        # Extrahieren der ausgewählten Merkzeichen
        selected_marks = []
        for mark in ["mark_ag", "mark_b", "mark_bl", "mark_h", "mark_gl", "mark_g", "mark_tb"]:
            if row[mark] == 1:
                selected_marks.append(mark.replace("mark_", "").upper())

        # Eingabefelder für die Rabattoptionen
        with cols[0]:
            option_name = st.text_input(r'''$\textsf{\Large Name}$''', value=row["name_of_option"], key=f"name_{i}")
            if len(option_name) > 50:
                st.error("Name darf nicht länger als 50 Zeichen sein.")
        with cols[1]:
            discounted_price = st.number_input(r'''$\textsf{\Large Ermäßigter Preis}$''', value=float(row["discounted_price"]), step=0.5, key=f"price_disc_{i}")
            if discounted_price < 0:
                st.error("Ermäßigter Preis muss größer gleich 0 sein.")
        with cols[2]:
            standard_price = st.number_input(r'''$\textsf{\Large Normalpreis}$''', value=float(row["standard_price"]), step=0.5, key=f"price_norm_{i}")
            if standard_price < 0:
                st.error("Normalpreis muss größer gleich 0 sein.")
            if standard_price <= discounted_price:
                st.error("Normalpreis muss größer als Ermäßigter Preis sein.")
        with cols[3]:
            companion_price = st.number_input(r'''$\textsf{\Large Preis Begleitperson}$''', value=float(row["companion_price"]), step=0.5, key=f"price_comp_{i}")
            if companion_price < 0:
                st.error("Preis Begleitperson muss größer gleich 0 sein.")
            if companion_price > standard_price:
                st.error("Preis Begleitperson darf nicht über Normalpreis sein.")
        with cols[4]:
            required_disability_degree = st.number_input(r'''$\textsf{\Large Erforderlicher GDB}$''', value=row["degree_of_disability"], step=10, key=f"gdb_{i}")
            if required_disability_degree < 20 or required_disability_degree > 100:
                st.error("Der Grad der Behinderung muss größer gleich 20 sein und darf nicht größer als 100 sein.")
        with cols[5]:
            selected_disability_marks = st.multiselect(r'''$\textsf{\Large Merkzeichen}$''', disability_marks, key=f"merkzeichen_{i}", default=selected_marks)

    # Trennlinie
    st.markdown("---")
    st.title("🖼️ Medien")

    # Medien-Upload-Bereich
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown(
            """
            <style>
            .stTextInput {
                margin: 0px 40px 40px 40px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        def get_signed_logo_url():
            possible_exts = ["png", "jpg", "jpeg"]
            for ext in possible_exts:
                filename = f"{locality_id}.{ext}"
                try:
                    res = client.storage.from_(BUCKET_NAME).create_signed_url(
                        filename, expires_in=3600  # 1 Stunde gültig
                    ).json()
                    if "signedURL" in res:
                        return res["signedURL"]
                except:
                    pass
            return None

        existing_logo_url = get_signed_logo_url()

        BUCKET_NAME = "localitylogos"

        # 📤 Upload-Feld
        logo_upload = st.file_uploader(
            r'''$\textsf{\Large 1. Logo hochladen \textit{(optional)}}$''',
            type=["png", "jpg", "jpeg"],
            key="logo"
        )

        # 🖼️ Aktuelles Logo anzeigen
        if existing_logo_url:
            st.markdown("Aktuelles Logo:")
            st.image(existing_logo_url, width=250)

        # 📦 Upload-Logik
        if logo_upload is not None:
            file_ext = logo_upload.name.split('.')[-1]
            filename = f"{locality_id}.{file_ext}"
            file_bytes = logo_upload.read()

            # Alte Dateien löschen
            try:
                existing_files = client.storage.from_(BUCKET_NAME).list()
                for file in existing_files:
                    if file["name"].startswith(locality_id):
                        delete_res = client.storage.from_(BUCKET_NAME).remove([file["name"]])
                        if delete_res[0].get("error"):
                            st.warning("Fehler beim Löschen der alten Datei.")
            except Exception as e:
                st.warning(f"Fehler beim Löschen der Datei: {e}")

            # Upload
            upload_res = client.storage.from_(BUCKET_NAME).upload(
                filename, file_bytes, {"content-type": logo_upload.type}
            ).json()

            if upload_res.get("error") is None:
                signed_url = client.storage.from_(BUCKET_NAME).create_signed_url(filename, 3600)
                if "signedURL" in signed_url:
                    st.image(signed_url["signedURL"], caption="Hochgeladenes Logo", width=250)
                else:
                    st.warning("Upload ok, aber konnte keine URL erzeugen.")
            else:
                st.error(f"Fehler beim Upload: {upload_res['error']['message']}")

        st.markdown(
            """
            <style>
            .stFileUploader {
                margin: 0px 40px 40px 40px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        background_upload = st.file_uploader(r'''$\textsf{\Large 2. Hintergrundbild hochladen \textit{(optional)}}$''', type=["png", "jpg", "jpeg"], key="bg")

        st.markdown(
            """
            <style>
            .stFileUploader {
                margin: 0px 40px 40px 40px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        additional_images = st.file_uploader(r'''$\textsf{\Large 3. Weitere Bilder hochladen \textit{(max. 3, optional)}}$''', type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="more_imgs")

        if additional_images and len(additional_images) > 3:
            st.warning("Bitte nicht mehr als 3 Bilder hochladen.")

    with col2:
        # Vorschau eines Beispielbildes
        preview_image = Image.open("media/VorherNachher.png")
        st.image(preview_image, width=600, use_container_width=True)

    # Trennlinie
    st.markdown("---")
    st.title("ℹ️ Weitere Informationen")

    # Eingabefelder für weitere Informationen
    locality_name_input = st.text_area(r'''$\textsf{\Large Name der Lokalität}$''', value=locality_name)
    if len(locality_name_input) > 30:
        st.error("Der Name darf nicht länger als 30 Zeichen sein.")
    if len(locality_name_input) < 3:
        st.error("Der Name muss mindestens 3 Zeichen lang sein.")
    description_text = st.text_area(r'''$\textsf{\Large Beschreibungstext \textit{(max 300 Zeichen, optional)}}$''')
    if len(description_text) > 300:
        st.error("Der Informationstext darf nicht länger als 300 Zeichen sein.")
    if len(description_text) < 20 and len(description_text) > 0:
        st.error("Der Informationstext muss mindestens 20 Zeichen lang sein.")
    phone_number_input = st.text_area(r'''$\textsf{\Large Telefonnummer \textit{(optional)}}$''', value=phone_number)
    email_input = st.text_area(r'''$\textsf{\Large E-Mail-Adresse \textit{(optional)}}$''', value=email)
    st.checkbox(r'''$\textsf{\Large Barrierefrei}$''', value=is_wheelchair_accessible, key="barrier_free")

    # Speichern-Button
    col1, col2, col3 = st.columns([5, 3, 5])
    with col2:
        st.markdown(
            """
            <style>
            .stButton {
                margin-top: 40px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        if st.button(r'''$\textsf{\Large Daten speichern ✅}$''', key="save_button", help="Klicken Sie hier, um die Daten zu speichern"):
            st.success("Daten wurden gespeichert!")
