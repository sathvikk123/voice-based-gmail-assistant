import streamlit as st
from gtts import gTTS
import os
import sys

# IMPORTANT: This makes python detect modules folder
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from modules.gmail_api import gmail_login, get_latest_emails, send_email


def speak(text):
    tts = gTTS(text=text, lang="en")
    tts.save("output.mp3")
    st.audio("output.mp3", format="audio/mp3")


st.set_page_config(page_title="Voice Gmail Assistant", layout="centered")

st.title("📧🎙 Voice-Based Gmail Assistant")
st.write("Connect Gmail and read/send emails using this app.")

st.warning("⚠️ Put client_secret.json inside credentials/ folder before connecting Gmail.")

# Connect Gmail
if st.button("🔐 Connect Gmail"):
    try:
        service = gmail_login()
        st.session_state["gmail_service"] = service
        st.success("Gmail connected successfully ✅")
        speak("Gmail connected successfully")
    except Exception as e:
        st.error(f"Error: {e}")

# If connected
if "gmail_service" in st.session_state:
    service = st.session_state["gmail_service"]

    st.subheader("📩 Latest Emails")

    if st.button("📥 Load Latest 5 Emails"):
        try:
            emails = get_latest_emails(service, max_results=5)
            st.session_state["emails"] = emails
            st.success("Loaded latest emails ✅")
        except Exception as e:
            st.error(f"Error: {e}")

    if "emails" in st.session_state:
        for i, mail in enumerate(st.session_state["emails"]):
            with st.expander(f"{i+1}) {mail['subject']}"):
                st.write("**From:**", mail["from"])
                st.write("**Snippet:**", mail["snippet"])

                if st.button(f"🔊 Speak Email {i+1}", key=f"speak_{i}"):
                    speak("Subject is " + mail["subject"])
                    speak("Message is " + mail["snippet"])

    st.divider()

    st.subheader("✉️ Send Email")

    to_email = st.text_input("To Email")
    subject = st.text_input("Subject")
    body = st.text_area("Message", height=120)

    if st.button("📤 Send Email"):
        if not to_email or not subject or not body:
            st.error("Please fill To Email, Subject and Message.")
        else:
            try:
                send_email(service, to_email, subject, body)
                st.success("Email sent successfully ✅")
                speak("Email sent successfully")
            except Exception as e:
                st.error(f"Error: {e}")
