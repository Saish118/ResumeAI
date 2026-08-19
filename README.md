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

### 3. Job Description Processing v1
- Ingests raw job description text and an optional job title, converting it into structured job requirements.
- Reuses the shared skill taxonomy and extraction engine without duplicating skill rules.
- Classifies extracted skills into **Required** (e.g. `required`, `must have`, `essential`) vs. **Preferred** (e.g. `preferred`, `nice to have`, `bonus`, `plus`).
- Extracts numeric minimum years of experience using pattern matching (e.g. `2+ years`, `3-5 years`, `minimum 4 years`).
- Generates sentence-level evidence snippets for each requirement.

### 4. Semantic Similarity Service v1
- Computes dense vector embeddings and cosine similarity between text strings using `sentence-transformers`.
- Uses pre-trained model **`all-MiniLM-L6-v2`** to capture semantic meaning beyond exact keyword matching (e.g., matching "Built REST APIs using FastAPI" with "Developed backend services").
- Leverages a lazy singleton pattern to load model weights once and reuse them across requests.
- Returns normalized similarity scores (`0.0` to `1.0`) with graceful handling for empty/whitespace inputs.

### 5. Resume ↔ Job Matching Engine v1
- Compares structured resume data against job description requirements to compute an explainable overall match analysis bounded between **0 and 100**.
- **Exact Skill Matching**: Evaluates canonical skill overlap, producing lists of matched/missing required skills and matched/missing preferred skills.
- **Experience Fit Assessment**: Compares candidate experience against minimum required years (`matched`, `below_requirement`, or `unknown` when unavailable).
- **Requirement-Level Semantic Evidence Matching**: Computes sentence-level semantic similarity between job requirements and candidate resume evidence snippets.
- **Configurable Scoring Weights**:
  - Required Skills: **50%**
  - Preferred Skills: **20%**
  - Semantic Evidence: **20%**
  - Experience Fit: **10%**
  > **Note on Initial Baseline Weights**: The default weights are initial configurable baseline heuristic assumptions and will require empirical evaluation and tuning against real-world candidate benchmark data in future iterations.

### 6. ML Role Classification Service v1
- Predicts a candidate's likely job role category (across 24 taxonomy categories) using a trained **TF-IDF + Logistic Regression** machine learning pipeline.
- Loads the pre-trained pipeline artifact (`models/role_classifier.joblib`) via lazy singleton loading to prevent retraining or reloading per request.
- **Baseline Evaluation Results**:
  - **Test Accuracy**: **64.79%** (`0.6479`)
  - **Macro F1 Score**: **0.60**
  - **Weighted F1 Score**: **0.63**
  > **Note on Baseline Results**: These metrics represent baseline evaluation results on the dataset (`opensporks/resumes`, 2,481 usable resumes) and serve as a baseline benchmark for future iterative improvements.

## Project Structure

```
ResumeAI/
├── .gitignore          # Git ignore rules for Python, virtualenv, macOS, IDEs, and model artifacts
├── README.md           # Project documentation and quickstart guide
├── requirements.txt    # Application dependencies
├── ml_training.py      # Offline model training & evaluation script
├── models/
│   └── role_classifier.joblib  # Serialized scikit-learn pipeline artifact (git-ignored)
├── app/
│   ├── __init__.py     # ResumeAI package marker
│   ├── main.py         # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── health.py     # Health check endpoints
│   │       ├── resume.py     # Resume upload and parsing endpoint
│   │       ├── skill.py      # Skill extraction endpoint
│   │       ├── job.py        # Job description processing endpoint
│   │       ├── similarity.py # Semantic similarity endpoint
│   │       ├── match.py      # Resume to job matching endpoint
│   │       └── role.py       # ML Role classification endpoint
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py   # Application settings & environment configuration
│   │   └── taxonomy.py # Controlled skill taxonomy & alias dictionary
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── resume.py     # Pydantic schemas for document parsing
│   │   ├── skill.py      # Pydantic schemas for skill extraction
│   │   ├── job.py        # Pydantic schemas for job description processing
│   │   ├── similarity.py # Pydantic schemas for semantic similarity
│   │   ├── match.py      # Pydantic schemas for matching engine
│   │   └── role.py       # Pydantic schemas for role classification
│   └── services/
│       ├── __init__.py
│       ├── document_parser.py   # Modular PDF & DOCX text extraction service
│       ├── document_validator.py# File extension and content validation
│       ├── skill_extractor.py   # Rule/taxonomy-based skill extraction engine
│       ├── job_processor.py     # Job description requirements processing service
│       ├── similarity_service.py# Sentence Transformer semantic similarity service
│       ├── matching_engine.py   # Explainable resume to job matching engine
│       └── role_classifier.py   # Serialized ML pipeline role classification service
└── tests/
    ├── __init__.py
    ├── conftest.py               # Test client & sample document byte fixtures
    ├── test_document_parser.py   # Unit tests for document parser & validator
    ├── test_resume_api.py        # Integration tests for document upload API
    ├── test_skill_extractor.py   # Unit tests for skill extraction engine
    ├── test_skill_api.py         # Integration tests for skill extraction API
    ├── test_job_processor.py     # Unit tests for job description processor
    ├── test_job_api.py           # Integration tests for job description API
    ├── test_similarity_service.py# Unit tests for similarity service
    ├── test_similarity_api.py    # Integration tests for similarity API
    ├── test_matching_engine.py   # Unit tests for matching engine service
    ├── test_match_api.py         # Integration tests for matching API
    ├── test_role_classifier.py   # Unit tests for role classifier service
    └── test_role_api.py          # Integration tests for role prediction API
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

### 4. Train Model Artifact (Offline Script)
```bash
python ml_training.py
```
This trains the model pipeline and serializes it to `models/role_classifier.joblib`.

### 5. Run the Backend Server
```bash
uvicorn app.main:app --reload --port 8000
```
The server will start at `http://127.0.0.1:8000`.

### 6. Run Automated Tests
```bash
pytest -v
```

### 7. Test Endpoints
- **Health Check**: `GET http://127.0.0.1:8000/health` or `GET http://127.0.0.1:8000/api/v1/health`
- **Resume Parse Endpoint**: `POST http://127.0.0.1:8000/api/v1/resume/parse`
- **Skill Extraction Endpoint**: `POST http://127.0.0.1:8000/api/v1/resume/skills`
- **Job Description Processing Endpoint**: `POST http://127.0.0.1:8000/api/v1/job-description/process`
- **Semantic Similarity Endpoint**: `POST http://127.0.0.1:8000/api/v1/similarity`
- **Resume ↔ Job Match Endpoint**: `POST http://127.0.0.1:8000/api/v1/match`
- **ML Role Classification Endpoint**: `POST http://127.0.0.1:8000/api/v1/role/predict`
- **Interactive OpenAPI Documentation**: `http://127.0.0.1:8000/docs`

#### Sample ML Role Classification Request (`curl`):
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/role/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Experienced Senior Software Engineer proficient in Python, C++, distributed microservices architecture, and Linux kernel development."
     }'
```

#### Sample Response:
```json
{
  "predicted_role": "ENGINEERING",
  "confidence": 0.0791
}
```
