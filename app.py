import os
from dotenv import load_dotenv

load_dotenv()

import streamlit as st
from sections.header      import show_header
from sections.upload      import show_upload
from sections.result_card import show_result_card
from sections.gradcam     import show_gradcam
from sections.chatbot     import show_chatbot

st.set_page_config(
    page_title="Pawdentify — Snap a photo. Identify the breed.",
    page_icon="logo.png",
    layout="centered"
)

for key, val in {
    "uploaded_image": None,
    "gradcam_bytes" : None,
    "prediction"    : None,
    "detected_breed": None,
    "messages"      : [],
    "chat_history"  : [],
    "show_camera"   : False,
    "show_gradcam"  : False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

show_header()
show_upload()
show_result_card()
show_gradcam()
show_chatbot()