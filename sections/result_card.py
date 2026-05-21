import streamlit as st
import base64

def show_result_card():

    if not st.session_state.get("prediction") or \
    not st.session_state.get("uploaded_image"):
        return

    st.markdown("""
    <style>
    .pw-result-card {
        background:#1a1a1a;
        border:0.5px solid #2a2a2a;
        border-radius:16px;
        padding:20px;
        margin-bottom:14px;
    }
    .pw-result-label {
        font-size:0.68rem; color:#555;
        text-transform:uppercase;
        letter-spacing:1.2px; margin-bottom:14px;
    }
    .pw-result-layout {
        display:flex; gap:16px; align-items:flex-start;
    }
    .pw-dog-thumb {
        width:120px; height:180px;
        border-radius:12px; object-fit:cover;
        border:0.5px solid #2a2a2a; flex-shrink:0;
    }
    .pw-result-right { flex:1; min-width:0; }
    .pw-breed-row {
        display:flex;
        align-items:center;
        gap:10px;
        flex-wrap:wrap;
        margin-bottom:14px;
    }
    .pw-breed-name {
        font-size:1.5rem; font-weight:800;
        color:#f97316;
        margin-bottom:6px; line-height:1.2;
    }
    .pw-confidence {
        display:inline-block;
        background:rgba(249,115,22,0.12);
        color:#f97316;
        border:0.5px solid #f97316;
        padding:3px 11px; border-radius:20px;
        font-size:0.78rem; font-weight:600;
        margin-bottom:14px;
    }
    .pw-info-grid {
        display:grid;
        grid-template-columns:1fr 1fr;
        gap:7px;
    }
    .pw-info-item {
        background:#252525;
        border:0.5px solid #2a2a2a;
        border-radius:10px;
        padding:9px 11px;
        display:flex; align-items:flex-start; gap:7px;
        transition:border-color 0.2s;
    }
    .pw-info-item:hover { border-color:#f97316; }
    .pw-info-icon { font-size:0.95rem; margin-top:1px; }
    .pw-info-label {
        font-size:0.62rem; color:#555;
        text-transform:uppercase;
        letter-spacing:0.8px; margin-bottom:2px;
    }
    .pw-info-val {
        font-size:0.84rem; color:#e0e0e0; font-weight:600;
    }
    @media (max-width:600px) {
        .pw-result-layout { flex-direction:column; }
        .pw-dog-thumb { width:100%; height:180px; }
        .pw-breed-name { font-size:1.2rem; }
    }
    </style>
    """, unsafe_allow_html=True)

    data       = st.session_state.prediction
    breed      = data["top_breed"]
    confidence = data["confidence"]
    info       = data["breed_info"]
    img_b64    = base64.b64encode(
                    st.session_state.uploaded_image
                ).decode()

    html = f"""
    <div class="pw-result-card">
        <div class="pw-result-label">Result</div>
        <div class="pw-result-layout">
            <img class="pw-dog-thumb"
                src="data:image/jpeg;base64,{img_b64}"
                alt="Dog photo"/>
            <div class="pw-result-right">
                <div class="pw-breed-row">
                    <div class="pw-breed-name">{breed}</div>
                    <div class="pw-confidence">{confidence}% match</div>
                </div>
                <div class="pw-info-grid">
                    <div class="pw-info-item">
                        <div class="pw-info-icon">📍</div>
                        <div>
                            <div class="pw-info-label">Origin</div>
                            <div class="pw-info-val">{info['origin']}</div>
                        </div>
                    </div>
                    <div class="pw-info-item">
                        <div class="pw-info-icon">📏</div>
                        <div>
                            <div class="pw-info-label">Size</div>
                            <div class="pw-info-val">{info['size']}</div>
                        </div>
                    </div>
                    <div class="pw-info-item">
                        <div class="pw-info-icon">⏳</div>
                        <div>
                            <div class="pw-info-label">Lifespan</div>
                            <div class="pw-info-val">{info['lifespan']}</div>
                        </div>
                    </div>
                    <div class="pw-info-item">
                        <div class="pw-info-icon">🎭</div>
                        <div>
                            <div class="pw-info-label">Temperament</div>
                            <div class="pw-info-val">{info['temperament']}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)