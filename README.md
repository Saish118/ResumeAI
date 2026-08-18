# ResumeAI

ResumeAI is an ML/NLP-powered Resume-to-Job Intelligence Platform designed to extract content, normalize skills, analyze candidate-job fit, and provide explainable match insights.

## Project Structure

```
ResumeAI/
├── .gitignore          # Git ignore rules for Python, virtualenv, macOS, and IDEs
├── README.md           # Project documentation and quickstart guide
├── requirements.txt    # Minimal dependencies for the backend
└── app/
    ├── __init__.py     # ResumeAI package marker
    ├── main.py         # FastAPI application entry point
    ├── api/
    │   ├── __init__.py
    │   └── v1/
    │       ├── __init__.py
    │       └── health.py # Health check endpoints
    └── core/
        ├── __init__.py
        └── config.py   # Application settings & environment configuration
```

## Quickstart Guide

### 1. Prerequisites
- Python 3.9+ installed on your system.

### 2. Create & Activate Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Backend Server
```bash
uvicorn app.main:app --reload --port 8000
```
The server will start at `http://127.0.0.1:8000`.

### 5. Test Endpoints
- **Health Check**: `GET http://127.0.0.1:8000/health` or `GET http://127.0.0.1:8000/api/v1/health`
- **Interactive OpenAPI Documentation**: `http://127.0.0.1:8000/docs`
