# Pawdentify Deployment

This repository contains a Streamlit front-end and a FastAPI backend for dog breed classification and GradCAM visualization.

## Local development

1. Create a Python virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Set your Groq API key and backend URL for local development:
   ```powershell
   $env:GROQ_API_KEY = "your_groq_api_key_here"
   $env:API_BASE_URL = "http://127.0.0.1:8000"
   ```
4. Run the backend:
   ```powershell
   uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```
5. In a second terminal, run the front-end:
   ```powershell
   streamlit run app.py --server.address 0.0.0.0 --server.port 8501
   ```
6. Open the app at `http://localhost:8501`

## Docker deployment

> Requires Docker Desktop / Docker CLI installed on Windows.

1. Copy `.env.example` to `.env` and set `GROQ_API_KEY`.
2. Build and start the services:
   ```powershell
   docker compose up --build
   ```
3. View the app at `http://localhost:8501`

## Notes

- The Streamlit UI now reads the backend URL from `API_BASE_URL`.
- The Groq API key is loaded from `GROQ_API_KEY`.
- The backend service is exposed on port `8000`, and the front-end on port `8501`.
