import os
import streamlit as st
import re
from groq import Groq


def format_bot_text(text):
    """Format bot responses for HTML display."""
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'^[\*\-] (.+)', r'• \1', text, flags=re.MULTILINE)
    text = text.replace('\n', '<br/>')
    return text


def show_chatbot():
    """Display and handle the chatbot UI."""
    
    # Initialize session state keys once
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "detected_breed" not in st.session_state:
        st.session_state.detected_breed = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Show welcome message if no messages yet
    if not st.session_state.messages:
        breed = st.session_state.detected_breed
        if breed:
            welcome = f"Hi! Your dog is a <strong>{breed}</strong>. Ask me anything about this breed or any other dog! 🐾"
        else:
            welcome = "Hi! I'm your <strong>Dog Expert Assistant</strong>. Ask me anything about dog breeds, care, training or health! 🐾"
        st.session_state.messages = [{"role": "bot", "text": welcome}]

    # CSS Styling (unchanged from original)
    st.markdown("""
    <style>
    .pw-chat-label {
        font-size:0.68rem; color:#555;
        text-transform:uppercase;
        letter-spacing:1.2px;
        margin-bottom:10px;
    }
    .pw-chat-outer {
        background:#1a1a1a;
        border:0.5px solid #2a2a2a;
        border-radius:16px;
        overflow:hidden;
        margin-bottom:0;
    }
    .pw-chat-header {
        background:linear-gradient(135deg,#f97316,#fb923c);
        padding:12px 16px;
        display:flex; align-items:center; gap:8px;
        font-size:0.88rem; font-weight:700; color:white;
    }
    .pw-chat-icon {
        width:28px; height:28px;
        background:rgba(255,255,255,0.2);
        border-radius:50%;
        display:flex; align-items:center;
        justify-content:center;
        font-size:0.9rem;
    }
    .pw-chat-messages {
        padding:14px;
        display:flex; flex-direction:column; gap:10px;
        min-height:200px; max-height:300px;
        overflow-y:auto;
        scrollbar-width:thin;
        scrollbar-color:#2a2a2a transparent;
    }
    .pw-msg-bot {
        background:#242424; border:0.5px solid #2a2a2a;
        color:#d0d0d0; padding:10px 13px;
        border-radius:13px 13px 13px 3px;
        font-size:0.84rem; line-height:1.6;
        max-width:85%; word-wrap:break-word;
    }
    .pw-msg-bot strong { color:#f97316; }
    .pw-msg-user {
        background:linear-gradient(135deg,#f97316,#fb923c);
        color:white; padding:10px 13px;
        border-radius:13px 13px 3px 13px;
        font-size:0.84rem; line-height:1.6;
        max-width:85%; word-wrap:break-word;
        align-self:flex-end; margin-left:auto;
    }
    .pw-input-wrap {
        background:#141414;
        padding:10px 12px;
        border-radius:0 0 16px 16px;
    }
    .pw-input-wrap .stTextInput > div > div > input {
        background:#242424 !important;
        border:0.5px solid #333 !important;
        border-radius:10px !important;
        color:#f0f0f0 !important;
        font-size:0.85rem !important;
        padding:9px 13px !important;
    }
    .pw-input-wrap .stTextInput > div > div > input:focus {
        border-color:#f97316 !important;
        box-shadow:none !important;
    }
    .pw-input-wrap .stTextInput label { display:none !important; }
    .pw-input-wrap div[data-testid="stFormSubmitButton"] > button {
        background:#f97316 !important;
        color:white !important;
        border:none !important;
        border-radius:10px !important;
        font-size:1rem !important;
        padding:9px 16px !important;
        width:100% !important;
    }
    .pw-input-wrap div[data-testid="stFormSubmitButton"] > button:hover {
        background:#ea6a0a !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div class="pw-chat-label">🐾 Dog Expert Chatbot</div>
    """, unsafe_allow_html=True)

    # Chat messages display
    msgs_html = "".join([
        f'<div class="{"pw-msg-bot" if m["role"]=="bot" else "pw-msg-user"}">'
        f'{m["text"]}</div>'
        for m in st.session_state.messages
    ])

    st.markdown(f"""
    <div class="pw-chat-outer">
        <div class="pw-chat-header">
            <div class="pw-chat-icon">🐾</div>
            Pawdentify Assistant
        </div>
        <div class="pw-chat-messages">
            {msgs_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Input form
    st.markdown('<div class="pw-input-wrap">', unsafe_allow_html=True)
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input(
                "message",
                placeholder="Ask about any dog breed...",
                label_visibility="collapsed"
            )
        with col2:
            send = st.form_submit_button("➤")
    st.markdown('</div>', unsafe_allow_html=True)

    # Process user input
    if send and user_input.strip():
        question = user_input.strip()

        # Add user message to display
        st.session_state.messages.append({
            "role": "user", "text": question
        })

        # Add user message to history for model context
        st.session_state.chat_history.append({
            "role": "user", "content": question
        })

        with st.spinner("Thinking..."):
            try: 
                api_key = os.getenv("GROQ_API_KEY", "")
                if not api_key:
                    st.session_state.messages.append({
                        "role": "bot",
                        "text": "Error: Groq API key not set. Set GROQ_API_KEY in your environment."
                    })
                else:
                    # Create Groq client
                    client = Groq(api_key=api_key)

                    # Build messages for API call
                    messages = [
                        {
                            "role": "system",
                            "content": """You are a friendly dog expert assistant.
Answer questions about dog breeds, dog care, training, health, and anything related to dogs.
Keep answers concise, friendly and helpful.
Remember the previous messages in the conversation."""
                        }
                    ]

                    # Add chat history
                    messages.extend(st.session_state.chat_history)

                    # Add breed context if available
                    if st.session_state.detected_breed and len(messages) > 1:
                        messages[-1]["content"] = (
                            f"User's dog breed: {st.session_state.detected_breed}\n"
                            f"Question: {question}"
                        )

                    # Call Groq API
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=messages,
                        max_tokens=500
                    )

                    # Extract answer
                    raw_answer = response.choices[0].message.content

                    # Add assistant message to history (plain text)
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": raw_answer
                    })

                    # Format and add to display
                    formatted_answer = format_bot_text(raw_answer)
                    st.session_state.messages.append({
                        "role": "bot",
                        "text": formatted_answer
                    })

            except Exception as e:
                st.session_state.messages.append({
                    "role": "bot",
                    "text": f"Error: {str(e)}"
                })

        # Rerun to show new messages
        st.rerun()
