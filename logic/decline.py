import streamlit as st
from PIL import Image
from dotenv import load_dotenv
from datetime import datetime
from logic.send_telegram_message import send_telegram_message
from functions.fetch_data_from_database import fetch_data_from_database
load_dotenv()


def decline(client, hash_code):

    header_logo = Image.open("media/ablehnung.png")

    locality_data = fetch_data_from_database(hash_code, client, False)

    locality_name = locality_data["name"].values[0]

    try:
        send_telegram_message(f"ABGELEHNT: {locality_name}")
    except Exception as e:
        print("Fehler beim Senden der Telegram-Nachricht:", e)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    client.table("Locality").update({"allowed_after_request": False, "last_disallowed_at": timestamp}).eq("hash_code", hash_code).execute()
    client.table("Locality").update({"last_disallowed_at": timestamp}).eq("hash_code", hash_code).execute()

    client.table("LocalityBackup").upsert({
        "hash_code": hash_code,
        "last_disallowed_at": timestamp
        })

    # Anzeige des Header-Bildes
    col1, col2, col3 = st.columns([3, 8, 3])
    with col2:
        col1, col2, col3 = st.columns([1, 4, 1])
        with col2:
            st.image(header_logo, width=10, use_container_width=True)

        # Begrüßungstext
        st.markdown("""
            <div style='text-align: center; margin-top: 20px;'>
                <h1 style='font-size: 55px;'>Wir haben Ihre Entscheidung erhalten</h1>
                <p style='font-size: 35px; max-width: 800px; margin: 0 auto;'>
                    und werden Sie nicht in Discountable integrieren.
                </p>
                
            </div>
        """, unsafe_allow_html=True)

        st.markdown(
            """
            <br>
            <br>
            <br>
            <p style='font-size: 26px; max-width: 1300px;'>
                    Falls Sie Ihre Meinung ändern, können Sie es uns über den Button unten mitteilen. So würden Sie nicht nur den Menschen mit Beeinträchtigung helfen, sondern auch Ihre Sichtbarkeit aufwandsfrei und kostenlos erhöhen.
                </p>
            """,
            unsafe_allow_html=True
        )

        #margin:
        st.markdown("<br><br>", unsafe_allow_html=True)

        

        col1, col2, col3 = st.columns([2, 2, 2])
        with col2:
            # button:
            st.markdown(f"""
                <style>
                .link-button {{
                    background-color: #44a4ec;
                    color: #FFFFFF;
                    padding: 0.75em;
                    border-radius: 0.5em;
                    text-align: center;
                    font-size: 23px;
                    font-weight: bold;
                    font-family: 'Segoe UI', sans-serif;
                    width: fit-content;
                    transition: all 0.2s ease;
                }}
                .link-button:hover {{
                    background-color: #FFFFFF;
                    color: #44a4ec;
                    transform: scale(1.03);
                    border: 3px solid #44a4ec;

                    cursor: pointer;
                }}
                </style>

                <a href="https://welcome.discountable.info/accept#{hash_code}" style="text-decoration: none;">
                    <div class="link-button">
                        Meinung ändern
                    </div>
                </a>
                """, unsafe_allow_html=True)

