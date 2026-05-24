# Pawdentify 🐶

## Overview

Pawdentify is a dog breed identification app built with a Streamlit user interface and a FastAPI backend. Users upload a dog photo, receive the top breed prediction, view a GradCAM heatmap, and chat with a breed-aware assistant.

## Features

- Dog breed classification with a trained EfficientNet model
- GradCAM visualization overlay for prediction explainability
- Breed information lookup and chat assistance
- Streamlit UI for image upload, camera capture, and results display
- FastAPI backend for prediction and GradCAM inference

## Tech Stack

- Python 3.13
- Streamlit
- FastAPI
- Uvicorn
- PyTorch / Torchvision / timm
- Pillow
- OpenCV
- Groq API for chatbot interactions
- Docker / Docker Compose

## Project Architecture

- `app.py` — Streamlit front-end entrypoint
- `backend/main.py` — FastAPI app exposing `/predict`, `/gradcam`, and `/chat`
- `backend/predictor.py` — loads the saved model and performs breed prediction
- `backend/gradcam.py` — generates GradCAM heatmaps for predicted classes
- `backend/chatbot.py` — optional Groq-backed chat helper
- `sections/` — Streamlit UI components for header, upload, result card, GradCAM, and chatbot
- `startup.sh` — combined backend + frontend startup for Docker/Hugging Face Spaces

## Workflow

1. User opens the Streamlit app on `7860`
2. User uploads or captures a dog image
3. Frontend sends the image to the backend at `http://127.0.0.1:8000/predict`
4. Backend returns the top breed and confidence scores
5. Frontend requests a GradCAM overlay from `http://127.0.0.1:8000/gradcam`
6. User can ask breed-related questions through the built-in chatbot

## Local Development

1. Clone the repository:
   ```powershell
   git clone https://github.com/TadikondaMythri/Pawdentify.git
   cd Pawdentify
   ```
2. Create and activate a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and set your values if needed.
5. Run the backend:
   ```powershell
   uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```
6. In a second terminal, run the frontend:
   ```powershell
   .\venv\Scripts\Activate.ps1
   streamlit run app.py --server.address 0.0.0.0 --server.port 7860
   ```
7. Open the app at `http://localhost:7860`

## Docker Deployment

1. Ensure Docker is installed.
2. Copy `.env.example` to `.env` and set `GROQ_API_KEY`.
3. Start the services:
   ```powershell
   docker compose up --build
   ```
4. View the app at `http://localhost:7860`

> For Hugging Face Spaces, Streamlit must run on `7860` while FastAPI stays on `8000` internally.
