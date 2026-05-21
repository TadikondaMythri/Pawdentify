"""
Backend chatbot module for handling LLM interactions.
The frontend calls Groq directly, so this is a backup/optional backend route.
"""
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


def ask_chatbot(question: str, breed: str = None, history: list = None):
    """
    Ask the chatbot a question.
    
    Args:
        question: User's question
        breed: Detected dog breed (optional)
        history: List of previous messages (optional)
    
    Returns:
        Response text from Groq
    """
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        return "Error: GROQ_API_KEY environment variable is not set."

    client = Groq(api_key=api_key)

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
    if history:
        messages.extend(history)

    # Add breed context
    if breed:
        question = f"User's dog breed: {breed}\nQuestion: {question}"

    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        max_tokens=500
    )

    return response.choices[0].message.content

