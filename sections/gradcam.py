import streamlit as st
import base64

def show_gradcam():

    # ── Init session state FIRST ──────────────────────
    if "show_gradcam" not in st.session_state:
        st.session_state.show_gradcam = False

    # ── Only show if prediction and gradcam exist ─────
    if not st.session_state.get("prediction") or \
    not st.session_state.get("gradcam_bytes"):
        return

    breed = st.session_state.prediction["top_breed"]

    st.markdown("""
    <style>
    .pw-gc-card {
        background:#1a1a1a;
        border:0.5px solid #2a2a2a;
        border-radius:16px;
        padding:22px 20px;
        margin-bottom:14px;
    }
    .pw-gc-label {
        font-size:0.68rem; color:#555;
        text-transform:uppercase;
        letter-spacing:1.2px; margin-bottom:12px;
    }
    .pw-gc-question {
        font-size:1rem; font-weight:700;
        color:#f0f0f0; margin-bottom:8px;
        line-height:1.4;
    }
    .pw-gc-sub {
        font-size:0.78rem; color:#666;
        line-height:1.6;
    }

    /* Reveal button */
    div[data-testid="stButton"] > button {
        background:transparent !important;
        color:#f97316 !important;
        border:1.5px solid #f97316 !important;
        border-radius:10px !important;
        font-weight:600 !important;
        font-size:0.88rem !important;
        padding:10px 24px !important;
        width:auto !important;
        transition:all 0.2s !important;
    }
    div[data-testid="stButton"] > button:hover {
        background:rgba(249,115,22,0.1) !important;
        transform:translateY(-1px) !important;
    }

    /* Heatmap result */
    .pw-gc-result {
        display:flex; gap:16px;
        align-items:flex-start;
        margin-top:4px;
        padding-top:3px;
    }
    .pw-gc-img-box {
        width:150px; height:130px;
        border-radius:12px; overflow:hidden;
        flex-shrink:0; border:0.5px solid #2a2a2a;
    }
    .pw-gc-img-box img {
        width:100%; height:100%; object-fit:cover;
    }
    .pw-gc-info { flex:1; }
    .pw-gc-info-title {
        font-size:0.9rem; font-weight:700;
        color:#e0e0e0; margin-bottom:5px;
    }
    .pw-gc-info-sub {
        font-size:0.76rem; color:#666;
        line-height:1.6; margin-bottom:12px;
    }
    .pw-legend { display:flex; gap:10px; flex-wrap:wrap; }
    .pw-legend-item {
        display:flex; align-items:center;
        gap:4px; font-size:0.74rem; color:#888;
    }
    .pw-legend-dot { width:9px; height:9px; border-radius:50%; }

    @media (max-width:600px) {
        .pw-gc-result { flex-direction:column; }
        .pw-gc-img-box { width:100%; height:180px; }
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="pw-gc-card">
        <div class="pw-gc-question">
            🔍 Curious how the AI identified this breed?
        </div>
        <div class="pw-gc-sub">
            Every prediction has a reason. The AI didn't just guess —
            it locked on to specific visual features of
            <strong style="color:#f97316">{breed}</strong>
            to make its decision. Dare to see inside the AI's mind ?
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Reveal button ─────────────────────────────────
    if not st.session_state.show_gradcam:
        if st.button("🔥 Reveal AI Focus Map", key="reveal_gc"):
            st.session_state.show_gradcam = True
            st.rerun()

    # ── Heatmap ─────────────────────
    if st.session_state.show_gradcam:
        gc_b64 = base64.b64encode(
            st.session_state.gradcam_bytes).decode()

        st.markdown(f"""
        <div class="pw-gc-card">
            <div class="pw-gc-result">
                <div class="pw-gc-img-box">
                    <img src="data:image/png;base64,{gc_b64}"
                        alt="GradCAM heatmap"/>
                </div>
                <div class="pw-gc-info">
                    <div class="pw-gc-info-title">
                        AI Attention Heatmap
                    </div>
                    <div class="pw-gc-info-sub">
                        The brighter the region, the more the AI
                        focused on it. These are the exact features
                        that gave away the breed!
                    </div>
                    <div class="pw-legend">
                        <div class="pw-legend-item">
                            <div class="pw-legend-dot"
                                style="background:#ff3c00;"></div>
                            High focus
                        </div>
                        <div class="pw-legend-item">
                            <div class="pw-legend-dot"
                                style="background:#ff9600;"></div>
                            Medium
                        </div>
                        <div class="pw-legend-item">
                            <div class="pw-legend-dot"
                                style="background:#0044ff;"></div>
                            Low focus
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)