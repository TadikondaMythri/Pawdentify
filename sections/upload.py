import os
import streamlit as st
import requests
from PIL import Image
import io

def show_upload():

    st.markdown("""
    <style>
    .pw-upload-box {
        border:1.5px dashed #333;
        border-radius:16px;
        padding:5px 20px 4px;
        text-align:center;
        background:#181818;
        margin-bottom:12px;
    }
    .pw-upload-icon { font-size:2rem; margin-bottom:6px; }
    .pw-upload-title {
        font-size:0.95rem; font-weight:600;
        color:#e0e0e0; margin-bottom:4px;
    }
    .pw-upload-sub {
        font-size:0.78rem; color:#555;
        margin-bottom:16px;
    }

    /* First column button = outline */
    div[data-testid="stHorizontalBlock"]
    > div:first-child
    div[data-testid="stButton"] > button {
        background:transparent !important;
        color:#f97316 !important;
        border:1.5px solid #f97316 !important;
        border-radius:10px !important;
        font-weight:600 !important;
        font-size:0.88rem !important;
        padding:5px 0 !important;
        width:100% !important;
        transition:background 0.2s !important;
    }
    div[data-testid="stHorizontalBlock"]
    > div:first-child
    div[data-testid="stButton"] > button:hover {
        background:rgba(249,115,22,0.2) !important;
        color:white !important;
    }

    /* Second column button = outline */
    div[data-testid="stHorizontalBlock"]
    > div:nth-child(2)
    div[data-testid="stButton"] > button {
        background:transparent !important;
        color:#f97316 !important;
        border:1.5px solid #f97316 !important;
        border-radius:10px !important;
        font-weight:600 !important;
        font-size:0.88rem !important;
        padding:5px 0 !important;
        width:100% !important;
        transition:background 0.2s !important;
    }
    div[data-testid="stHorizontalBlock"]
    > div:nth-child(2)
    div[data-testid="stButton"] > button:hover {
        background:rgba(249,115,22,0.2) !important;
        color:white !important;
    }

    /* Back button */
    div[data-testid="stButton"] > button {
        background:transparent !important;
        color:#f97316 !important;
        border:1px solid #f97316 !important;
        border-radius:8px !important;
        font-size:0.82rem !important;
        padding:6px 14px !important;
        width:auto !important;
    }

    /* File uploader */
    [data-testid="stFileUploaderDropzone"] {
        background:#1e1e1e !important;
        border:1.5px dashed #2a2a2a !important;
        border-radius:12px !important;
    }
    [data-testid="stFileUploaderDropzone"] * { color:#666 !important; }

    /* Spinner */
    .stSpinner > div { border-top-color:#f97316 !important; }

    @media (max-width:600px) {
        div[data-testid="stHorizontalBlock"] { flex-direction:column; }
    }
    </style>
    """, unsafe_allow_html=True)

    # Session state
    for key, val in {
        "uploaded_image": None,
        "gradcam_bytes" : None,
        "prediction"    : None,
        "detected_breed": None,
        "messages"      : [],
        "show_camera"   : False,
        "show_gallery"  : False,
    }.items():
        if key not in st.session_state:
            st.session_state[key] = val

    # Upload box 
    st.markdown("""
    <div class="pw-upload-box">
        <div class="pw-upload-icon">☁️</div>
        <div class="pw-upload-title">Upload a dog photo</div>
        <div class="pw-upload-sub">
            Supports JPG, PNG, webp — or take one with your camera
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Streamlit buttons — styled via CSS to look like design
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📷 Take a photo",
                    key="btn_camera",
                    use_container_width=True):
            st.session_state.show_camera = True
            st.session_state.show_gallery = False
            st.rerun()
    with col2:
        if st.button("📁 Upload from gallery",
                    key="btn_gallery",
                    use_container_width=True):
            st.session_state.show_camera = False
            st.session_state.show_gallery = True
            st.rerun()

    # Show selected input method only after the user chooses it
    camera_image = None
    uploaded_file = None

    if st.session_state.show_camera:
        camera_image = st.camera_input(
            "Take a photo",
            label_visibility="collapsed"
        )
        if st.button("← Back to upload", key="btn_back"):
            st.session_state.show_camera = False
            st.session_state.show_gallery = False
            st.rerun()
    elif st.session_state.show_gallery:
        uploaded_file = st.file_uploader(
            "Choose image",
            type=["jpg","jpeg","png", "webp"],
            label_visibility="collapsed"
        )

    # Process image
    image_source = camera_image if camera_image else uploaded_file

    if image_source:
        image_bytes = image_source.read()

        if st.session_state.uploaded_image is None or st.session_state.uploaded_image != image_bytes:
            try:
                Image.open(io.BytesIO(image_bytes))
            except Exception:
                st.error("Invalid image. Please try again.")
                return

            st.session_state.uploaded_image = image_bytes
            st.session_state.gradcam_bytes  = None
            st.session_state.prediction     = None

            api_base_url = os.getenv("API_BASE_URL", "https://mythritadikonda-pawdentify-backend.hf.space/")
            with st.spinner("🔍 Analyzing your dog..."):
                try:
                    pred_resp = requests.post(
                        f"{api_base_url}/predict",
                        files={"file":("image.jpg", image_bytes, "image/jpeg")}
                    )
                    pred_resp.raise_for_status()
                    data = pred_resp.json()

                    gc_resp = requests.post(
                        f"{api_base_url}/gradcam",
                        files={"file":("image.jpg", image_bytes, "image/jpeg")}
                    )
                    gc_resp.raise_for_status()

                    st.session_state.prediction     = data
                    st.session_state.detected_breed = data["top_breed"]
                    st.session_state.gradcam_bytes  = gc_resp.content

                    greeting = f"Hi! Your dog is a {data['top_breed']}. Ask me anything! 🐾"
                    st.session_state.messages.append({
                        "role": "bot",
                        "text": f"Hi! Your dog is a <strong>{data['top_breed']}</strong>. Ask me anything! 🐾"
                    })
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": greeting
                    })

                except Exception as e:
                    st.error(
                        f"❌ Backend error: {e}\n"
                        f"API_BASE_URL={api_base_url}\n"
                        "Make sure uvicorn backend.main:app --host 0.0.0.0 --port 8000 is running."
                    )