# ResumeAI

ResumeAI is an ML/NLP-powered Resume-to-Job Intelligence Platform designed to extract content, normalize skills, analyze candidate-job fit, and provide explainable match insights.

## Features

### 1. Resume Document Parsing
- Accepts uploaded resume documents in **PDF** and **DOCX** formats.
- Performs text extraction, character counting, and page counting (`page_count` is provided for PDF files and returned as `null` for DOCX files).
- Validates file types and content integrity with clean error handling.

## Project Structure

```
ResumeAI/
├── .gitignore          # Git ignore rules for Python, virtualenv, macOS, and IDEs
├── README.md           # Project documentation and quickstart guide
├── requirements.txt    # Application dependencies
├── app/
│   ├── __init__.py     # ResumeAI package marker
│   ├── main.py         # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── health.py # Health check endpoints
│   │       └── resume.py # Resume upload and parsing endpoint
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py   # Application settings & environment configuration
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── resume.py   # Pydantic schemas for request/response validation
│   └── services/
│       ├── __init__.py
│       ├── document_parser.py   # Modular PDF & DOCX text extraction service
│       └── document_validator.py# File extension and content validation
└── tests/
    ├── __init__.py
    ├── conftest.py            # Test client & sample document byte fixtures
    ├── test_document_parser.py# Unit tests for validator and parser services
    └── test_resume_api.py     # Integration tests for upload API endpoint
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

### 5. Run Automated Tests
```bash
pytest -v
```

### 6. Test Endpoints
- **Health Check**: `GET http://127.0.0.1:8000/health` or `GET http://127.0.0.1:8000/api/v1/health`
- **Resume Parse Endpoint**: `POST http://127.0.0.1:8000/api/v1/resume/parse`
- **Interactive OpenAPI Documentation**: `http://127.0.0.1:8000/docs`

#### Sample Resume Upload via `curl`:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/resume/parse" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@/path/to/your/resume.pdf"
```
