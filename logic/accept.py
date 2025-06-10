import streamlit as st
from PIL import Image
from datetime import datetime   
from functions.fetch_data_from_database import fetch_data_from_database
from dotenv import load_dotenv
load_dotenv()
from streamlit_javascript import st_javascript
from logic.send_telegram_message import send_telegram_message
from functions.get_signed_logo_url import get_signed_logo_url

def accept(hash_code, client):

# Aktualisieren der Datenbank mit Zeitstempel und Erlaubnis

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    client.table("Locality").update({"last_allowed_at": timestamp}).eq("hash_code", str(hash_code)).execute()
    client.table("Locality").update({"allowed_after_request": True}).eq("hash_code", str(hash_code)).execute()
    
    # Abrufen der Daten aus der Datenbank
    locality_data, discount_data = fetch_data_from_database(hash_code, client, True)

    # Extrahieren relevanter Informationen aus den Daten
    locality_id = locality_data["locality_id"].values[0]
    locality_name = locality_data["name"].values[0]
    email = locality_data["email_from_website"].values[0] if locality_data["email_from_website"].values[0] != None else locality_data["email_from_osm"].values[0]
    phone_number = locality_data["phone_number"].values[0]
    is_wheelchair_accessible = locality_data["wheelchair_accessible"].values[0]

    try:
        send_telegram_message(f"AKZEPTIERT: {locality_name}")
    except Exception as e:
        print("Fehler beim Senden der Telegram-Nachricht:", e)

    client.table("LocalityBackup").upsert({
        "hash_code": locality_id,
        "last_allowed_at": timestamp
    }).execute()

    # Laden des Header-Logos
    header_logo = Image.open("media/HeaderDanke.png")

    # Anzeige des Header-Bildes
    col1, col2, col3 = st.columns([3, 6, 3])
    with col2:
        st.image(header_logo, width=600, use_container_width=True)

    # Begrüßungstext
    st.markdown("""
        <div style='text-align: center; margin-top: 20px;'>
            <h1 style='font-size: 45px;'>Vielen Dank für Ihre Unterstützung!</h1>
            <p style='font-size: 30px; max-width: 800px; margin: 0 auto;'>
                Ihre Hilfe macht dieses Projekt möglich.
            </p>
            <p style='font-size: 22px; max-width: 1400px; margin: 0 auto; padding-top: 60px; padding-bottom: 60px;'>
                Unten können Sie einsehen, welche Informationen wir in unsere App integrieren werden und diese gegebenenfalls anpassen.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Anzeige der Rabattoptionen
    col1, col2, col3 = st.columns([1, 9, 1])
    with col2:
        st.title("Identifizierte Rabattoptionen")

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

        discount_id_dict = {}
        option_name_dict = {}
        discounted_price_dict = {}
        standard_price_dict = {}
        companion_price_dict = {}
        required_disability_degree_dict = {}
        selected_disability_marks_dict = {}

        # Iteration über die Rabattdaten
        for i, row in discount_data.iterrows():
            cols = st.columns(6)

            # Rabatt-ID
            discount_id_dict[i] = row["discount_id"]

            # Extrahieren der ausgewählten Merkzeichen
            selected_marks = []
            for mark in ["mark_ag", "mark_b", "mark_bl", "mark_h", "mark_gl", "mark_g", "mark_tb"]:
                if row[mark] == 1:
                    selected_marks.append(mark.replace("mark_", "").upper())

            # Eingabefelder für die Rabattoptionen
            with cols[0]:
                option_name_dict[i] = st.text_input(r'''$\textsf{Name}$''', value=row["name_of_option"], key=f"name_{i}")
                if len(option_name_dict[i]) > 50:
                    st.error("Name darf nicht länger als 50 Zeichen sein.")
            with cols[1]:
                discounted_price_dict[i] = st.number_input(r'''$\textsf{Ermäßigter Preis}$''', value=float(row["discounted_price"]), step=0.5, key=f"price_disc_{i}")
                if discounted_price_dict[i] < 0:
                    st.error("Ermäßigter Preis muss größer gleich 0 sein.")
            with cols[2]:
                standard_price_dict[i] = st.number_input(r'''$\textsf{Normalpreis}$''', value=float(row["standard_price"]), step=0.5, key=f"price_norm_{i}")
                if standard_price_dict[i] < 0:
                    st.error("Normalpreis muss größer gleich 0 sein.")
                if standard_price_dict[i] <= discounted_price_dict[i]:
                    st.error("Normalpreis muss größer als Ermäßigter Preis sein.")
            with cols[3]:
                companion_price = float(row["companion_price"]) if float(row["companion_price"]) != -1 else float(row["standard_price"])

                companion_price_dict[i] = st.number_input(r'''$\textsf{Preis Begleitperson}$''', value=companion_price, step=0.5, key=f"price_comp_{i}")
                if companion_price_dict[i] < 0:
                    st.error("Preis Begleitperson muss größer gleich 0 sein.")
                if companion_price_dict[i] > standard_price_dict[i]:
                    st.error("Preis Begleitperson darf nicht über Normalpreis sein.")
            with cols[4]:
                required_disability_degree_dict[i] = st.number_input(r'''$\textsf{Erforderlicher GDB}$''', value=row["degree_of_disability"], step=10, key=f"gdb_{i}")
                if required_disability_degree_dict[i] < 20 or required_disability_degree_dict[i] > 100:
                    st.error("Der Grad der Behinderung muss größer gleich 20 sein und darf nicht größer als 100 sein.")
            with cols[5]:
                selected_disability_marks_dict[i] = st.multiselect(r'''$\textsf{Merkzeichen}$''', disability_marks, key=f"merkzeichen_{i}", default=selected_marks)

        # Trennlinie
        st.markdown("---")
        st.title("Medien")

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

            BUCKET_NAME = "localitylogos"

            existing_logo_url = get_signed_logo_url(locality_id, client, BUCKET_NAME)

        
            # 📤 Upload-Feld
            logo_upload = st.file_uploader(
                r'''$\textsf{Logo hochladen \textit{(optional)}}$''',
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

            background_upload = st.file_uploader(r'''$\textsf{Hintergrundbild hochladen \textit{(optional)}}$''', type=["png", "jpg", "jpeg"], key="bg")

            # 📦 Upload-Logik für Hintergrundbil
            BUCKET_NAME_BG = "localitybackground"
            if background_upload is not None:
                file_ext = background_upload.name.split('.')[-1]
                filename = f"{locality_id}_background.{file_ext}"
                file_bytes = background_upload.read()

                # Alte Dateien löschen
                try:
                    existing_files = client.storage.from_(BUCKET_NAME_BG).list()
                    for file in existing_files:
                        if file["name"].startswith(locality_id) and "background" in file["name"]:
                            delete_res = client.storage.from_(BUCKET_NAME_BG).remove([file["name"]])
                            if delete_res[0].get("error"):
                                st.warning("Fehler beim Löschen der alten Datei.")
                except Exception as e:
                    st.warning(f"Fehler beim Löschen der Datei: {e}")

                # Upload
                upload_res = client.storage.from_(BUCKET_NAME_BG).upload(
                    filename, file_bytes, {"content-type": background_upload.type}
                ).json()

                if upload_res.get("error") is None:
                    signed_url = client.storage.from_(BUCKET_NAME_BG).create_signed_url(filename, 3600)
                    if "signedURL" in signed_url:
                        st.image(signed_url["signedURL"], caption="Hochgeladenes Hintergrundbild", width=250)
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


        with col2:
            # Vorschau eines Beispielbildes
            preview_image = Image.open("media/VorherNachher.png")
            st.image(preview_image, width=600, use_container_width=True)

        # Trennlinie
        st.markdown("---")
        st.title("Weitere Informationen")

        # Eingabefelder für weitere Informationen
        locality_name_input = st.text_area(r'''$\textsf{Name der Lokalität}$''', value=locality_name)
        if len(locality_name_input) > 30:
            st.error("Der Name darf nicht länger als 30 Zeichen sein.")
        if len(locality_name_input) < 3:
            st.error("Der Name muss mindestens 3 Zeichen lang sein.")
        description_text = st.text_area(r'''$\textsf{Beschreibungstext \textit{(max 300 Zeichen, optional)}}$''')
        if len(description_text) > 300:
            st.error("Der Informationstext darf nicht länger als 300 Zeichen sein.")
        if len(description_text) < 20 and len(description_text) > 0:
            st.error("Der Informationstext muss mindestens 20 Zeichen lang sein.")
        phone_number_input = st.text_area(r'''$\textsf{Telefonnummer \textit{(optional)}}$''', value=phone_number)
        email_input = st.text_area(r'''$\textsf{E-Mail-Adresse \textit{(optional)}}$''', value=email)
        is_barrier_free = st.checkbox(r'''$\textsf{Barrierefrei}$''', value=is_wheelchair_accessible, key="barrier_free")

        # Speichern-Button
        col1, col2, col3 = st.columns([5, 2, 5])
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
            if st.button(r'''$\textsf{\Large Daten speichern}$''', key="save_button", help="Klicken Sie hier, um die Daten zu speichern"):


                # Speichern der Daten in der Datenbank
                client.table("Locality").update({
                    "name": locality_name_input,
                    "description": description_text if description_text else None,
                    "email_from_website": email_input,
                    "phone_number": phone_number_input,
                    "wheelchair_accessible": is_barrier_free
                }).eq("hash_code", str(hash_code)).execute()
                for i, row in discount_data.iterrows():
                    print("Updating discount ID:", discount_id_dict[i])
                    print("Row filter (was):", row['discount_id'])

                    client.table("LocalityDiscount").update({
                        "discount_id": discount_id_dict[i],
                        "name_of_option": option_name_dict[i],
                        "discounted_price": discounted_price_dict[i],
                        "standard_price": standard_price_dict[i],
                        "companion_price": companion_price_dict[i],
                        "degree_of_disability": required_disability_degree_dict[i],
                        "mark_ag": 1 if "AG" in selected_disability_marks_dict[i] else 0,
                        "mark_b": 1 if "B" in selected_disability_marks_dict[i] else 0,
                        "mark_bl": 1 if "BL" in selected_disability_marks_dict[i] else 0,
                        "mark_h": 1 if "H" in selected_disability_marks_dict[i] else 0,
                        "mark_gl": 1 if "GL" in selected_disability_marks_dict[i] else 0,
                        "mark_g": 1 if "G" in selected_disability_marks_dict[i] else 0,
                        "mark_tb": 1 if "TB" in selected_disability_marks_dict[i] else 0,
                        "confirmed_by_locality": True
                    }).eq("discount_id", int(discount_id_dict[i])).execute()
                st.success("Daten wurden gespeichert!")