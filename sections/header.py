import os
import streamlit as st
import base64

def show_header():

    # Load local logo from repo root
    logo_path = os.path.join(os.path.dirname(__file__), "..", "logo.png")
    logo_path = os.path.abspath(logo_path)
    logo = ""
    if os.path.isfile(logo_path):
        try:
            with open(logo_path, "rb") as f:
                logo_b64 = base64.b64encode(f.read()).decode("utf-8")
                logo = f"data:image/png;base64,{logo_b64}"
        except Exception:
            logo = ""

    logo_html = f'<img class="pw-logo" src="{logo}" alt="Pawdentify"/>' if logo else ""

    # CSS
    st.markdown("""
    <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    .stApp { background:#111111 !important; color:#f0f0f0 !important; }
    #MainMenu, footer, header { visibility:hidden; }
    .block-container {
        padding-top:0 !important;
        padding-bottom:1rem !important;
        max-width:700px !important;
    }

    .pw-header {
        background:#1a1a1a;
        border-bottom:2px solid #f97316;
        padding:12px 20px;
        display:flex;
        align-items:center;
        gap:12px;
        margin:-1rem -1rem 1.5rem -1rem;
        position:sticky;
        top:0;
        z-index:100;
    }
    .pw-logo {
        width:40px; height:40px;
        border-radius:50%;
        object-fit:cover;
        flex-shrink:0;
    }
    .pw-header-title {
        font-size:1.2rem;
        font-weight:700;
        color:#f97316;
        letter-spacing:0.3px;
        line-height:1.2;
    }
    .pw-header-sub {
        font-size:0.75rem;
        color:#888;
        margin-top:1px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header HTML
    st.markdown(f"""
    <div class="pw-header">
        {logo_html}
        <div>
            <div class="pw-header-title">Pawdentify</div>
            <div class="pw-header-sub">Snap a photo. Identify the breed.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)