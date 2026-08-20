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

### 3. Candidate Work Experience Extraction
- Analyzes employment date ranges (e.g. `Jan 2022 - Present`, `01/2020 - 12/2022`) and explicit experience statements (`3+ years of experience`).
- Scopes extraction to work experience sections and merges overlapping employment intervals to calculate accurate total candidate experience years.
- Handles internships, freshers, current jobs, and ambiguous date patterns (defaulting to `null`).

### 4. Job Description Processing v1
- Ingests raw job description text and an optional job title, converting it into structured job requirements.
- Reuses the shared skill taxonomy and extraction engine without duplicating skill rules.
- Classifies extracted skills into **Required** (e.g. `required`, `must have`, `essential`) vs. **Preferred** (e.g. `preferred`, `nice to have`, `bonus`, `plus`).
- Extracts numeric minimum years of experience using pattern matching (e.g. `2+ years`, `3-5 years`, `minimum 4 years`).
- Generates sentence-level evidence snippets for each requirement.

### 5. Semantic Similarity Service v1
- Computes dense vector embeddings and cosine similarity between text strings using `sentence-transformers`.
- Uses pre-trained model **`all-MiniLM-L6-v2`** to capture semantic meaning beyond exact keyword matching.
- Leverages a lazy singleton pattern to load model weights once and reuse them across requests.

### 6. Resume ↔ Job Matching Engine v1
- Compares structured resume data against job description requirements to compute an explainable overall match analysis bounded between **0 and 100**.
- **Exact Skill Matching**: Evaluates canonical skill overlap (matched/missing required & preferred skills).
- **Experience Fit Assessment**: Compares candidate experience against minimum required years (`matched`, `below_requirement`, or `unknown`).
- **Requirement-Level Semantic Evidence Matching**: Computes sentence-level semantic similarity between job requirements and candidate resume evidence snippets.

### 7. PostgreSQL Persistence & History APIs
- Persists structured records for `ResumeAnalysis`, `JobAnalysis`, and `MatchAnalysis` with foreign key relationships.
- Exposes queryable history API endpoints (`GET /api/v1/history/resumes`, `/jobs`, `/matches`, `/matches/{id}`).
- Uses SQLAlchemy 2.x ORM with `psycopg3` driver and environment-driven `DATABASE_URL` configuration.

---

## Local PostgreSQL Setup & Configuration

### 1. Install PostgreSQL (macOS via Homebrew)
If PostgreSQL is not already installed:
```bash
brew install postgresql@16
```

### 2. Start PostgreSQL Service
```bash
brew services start postgresql@16
```

### 3. Create ResumeAI Database
```bash
createdb resumeai
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and set your local PostgreSQL database URL:
```bash
cp .env.example .env
```
Edit `.env`:
```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/resumeai
```
*(Note: Do NOT commit `.env` to Git. `.env` is ignored in `.gitignore`.)*

### 5. Start Backend Server & Verify Database Connection
```bash
uvicorn app.main:app --reload --port 8000
```
On application startup, SQLAlchemy will automatically initialize all required database tables (`resume_analyses`, `job_analyses`, `match_analyses`).

---

## Quickstart Guide

### 1. Frontend Web App (React + Vite)
```bash
npm install
npm run dev
```

### 2. Backend Server (FastAPI)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Run Automated Tests
```bash
pytest -v
```

---

## API Endpoints Overview
- **Health Check**: `GET /health`
- **Resume Parse Endpoint**: `POST /api/v1/resume/parse`
- **Experience Extraction Endpoint**: `POST /api/v1/resume/experience`
- **Skill Extraction Endpoint**: `POST /api/v1/resume/skills`
- **Job Description Processing Endpoint**: `POST /api/v1/job-description/process`
- **Semantic Similarity Endpoint**: `POST /api/v1/similarity`
- **Resume ↔ Job Match Endpoint**: `POST /api/v1/match`
- **ML Role Classification Endpoint**: `POST /api/v1/role/predict`
- **Resume Analysis History**: `GET /api/v1/history/resumes`
- **Job Description History**: `GET /api/v1/history/jobs`
- **Match Evaluation History**: `GET /api/v1/history/matches`
- **Match Record Detail**: `GET /api/v1/history/matches/{match_id}`
- **Interactive OpenAPI Documentation**: `http://127.0.0.1:8000/docs`
