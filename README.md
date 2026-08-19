# ResumeAI

ResumeAI is an ML/NLP-powered Resume-to-Job Intelligence Platform designed to extract content, normalize skills, analyze candidate-job fit, and provide explainable match insights.

## Features

### 1. Resume Document Parsing
- Accepts uploaded resume documents in **PDF** and **DOCX** formats.
- Performs text extraction, character counting, and page counting (`page_count` is provided for PDF files and returned as `null` for DOCX files).
- Validates file types and content integrity with clean error handling.

### 2. Skill Extraction v1 (Rule/Taxonomy-Based Baseline)
- Extracts explicit skills from raw text using a controlled skill taxonomy across categories (Programming Languages, Web Development, Databases, Machine Learning / AI, Data, DevOps / Cloud, Tools / Version Control).
- Maps variations and aliases (e.g. `postgres`, `psql` -> `PostgreSQL`; `reactjs`, `react.js` -> `React`; `sklearn` -> `scikit-learn`).
- Uses boundary-safe regex matching to prevent false positives (e.g., prevents "Java" matching inside "JavaScript").
- Accurately parses punctuation-sensitive skills (`C++`, `C#`, `.NET`, `Node.js`).
- Deduplicates canonical skill outputs while preserving text appearance ordering.
- Returns canonical skill lists and extensible structured details with evidence snippets for explainability.

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
│   │       ├── resume.py # Resume upload and parsing endpoint
│   │       └── skill.py  # Skill extraction endpoint
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py   # Application settings & environment configuration
│   │   └── taxonomy.py # Controlled skill taxonomy & alias dictionary
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── resume.py   # Pydantic schemas for document parsing
│   │   └── skill.py    # Pydantic schemas for skill extraction
│   └── services/
│       ├── __init__.py
│       ├── document_parser.py   # Modular PDF & DOCX text extraction service
│       ├── document_validator.py# File extension and content validation
│       └── skill_extractor.py   # Rule/taxonomy-based skill extraction engine
└── tests/
    ├── __init__.py
    ├── conftest.py            # Test client & sample document byte fixtures
    ├── test_document_parser.py# Unit tests for document parser & validator
    ├── test_resume_api.py     # Integration tests for document upload API
    ├── test_skill_extractor.py# Unit tests for skill extraction engine
    └── test_skill_api.py      # Integration tests for skill extraction API
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
- **Skill Extraction Endpoint**: `POST http://127.0.0.1:8000/api/v1/resume/skills`
- **Interactive OpenAPI Documentation**: `http://127.0.0.1:8000/docs`

#### Sample Skill Extraction Request (`curl`):
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/resume/skills" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Built web applications using Python, React.js, and PostgreSQL."
     }'
```

#### Sample Response:
```json
{
  "skills": [
    "Python",
    "React",
    "PostgreSQL"
  ],
  "extracted_skills": [
    {
      "skill": "Python",
      "matched_alias": "Python",
      "category": "Programming Languages",
      "evidence": "applications using Python, React.js, and"
    },
    {
      "skill": "React",
      "matched_alias": "React.js",
      "category": "Web Development",
      "evidence": "Python, React.js, and PostgreSQL."
    },
    {
      "skill": "PostgreSQL",
      "matched_alias": "PostgreSQL",
      "category": "Databases",
      "evidence": "React.js, and PostgreSQL."
    }
  ]
}
```
