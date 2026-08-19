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

### 7. React + Vite Web Dashboard (Frontend Shell & Upload UI)
- Clean, light, professional user interface built with **React 18** and **Vite**.
- Simple hero messaging: *"Understand Your Resume. Match Better Jobs."*
- Interactive drag-and-drop resume upload zone supporting **PDF** and **DOCX** documents up to 10MB.
- File status display card with file size formatting and clear remove/change actions.
- Client-side validation for unsupported file types and size limits with clean user alerts.
- Structured analysis result cards prepared for future backend data (*Predicted Role*, *Job Match Score*, *Skills Found*, *Missing Skills*, *Key Insights*).

## Project Structure

```
ResumeAI/
├── .gitignore          # Git ignore rules for Python, Node, macOS, IDEs, and model artifacts
├── README.md           # Project documentation and quickstart guide
├── requirements.txt    # Python backend dependencies
├── package.json        # Node frontend dependencies & build scripts
├── vite.config.js      # Vite dev server and build configuration
├── index.html          # HTML entry point with Inter typography
├── src/                # Frontend React source code
│   ├── main.jsx        # React entry point
│   ├── App.jsx         # Main application container
│   ├── index.css       # Clean Vanilla CSS design system
│   └── components/
│       ├── Header.jsx          # Header with logo & minimal navigation
│       ├── HeroSection.jsx     # Clean hero copy section
│       ├── ResumeUploader.jsx  # Drag-and-drop & file upload card
│       ├── AnalysisButton.jsx  # Primary action button with spinner
│       ├── ResultCard.jsx      # Reusable result card container
│       └── ResultsSection.jsx  # 5 structured result placeholder cards
├── app/                # Python FastAPI Backend
│   ├── main.py         # FastAPI application entry point
│   ├── api/v1/         # Endpoint routers (health, resume, skill, job, similarity, match, role)
│   ├── core/           # Config & taxonomy
│   ├── schemas/        # Pydantic request/response schemas
│   └── services/       # Parsing, extraction, matching & ML services
├── models/
│   └── role_classifier.joblib  # Serialized scikit-learn pipeline artifact (git-ignored)
└── tests/              # Pytest backend test suite (71 passing tests)
```

## Quickstart Guide

### 1. Frontend Web App (React + Vite)

#### Prerequisites
- Node.js 18+ and `npm` installed on your system.

#### Install Frontend Dependencies
```bash
npm install
```

#### Run Frontend Development Server
```bash
npm run dev
```
The frontend dev server will start at `http://localhost:3000`.

#### Build Frontend for Production
```bash
npm run build
```
Generates production-optimized bundle files in `dist/`.

---

### 2. Backend Server (FastAPI)

#### Prerequisites
- Python 3.9+ installed on your system.

#### Create & Activate Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Install Backend Dependencies
```bash
pip install -r requirements.txt
```

#### Train Model Artifact (Offline Script)
```bash
python ml_training.py
```

#### Run the Backend Server
```bash
uvicorn app.main:app --reload --port 8000
```
The backend server will start at `http://127.0.0.1:8000`.

#### Run Automated Tests
```bash
pytest -v
```

### 3. API Endpoints Overview
- **Health Check**: `GET http://127.0.0.1:8000/health`
- **Resume Parse Endpoint**: `POST http://127.0.0.1:8000/api/v1/resume/parse`
- **Skill Extraction Endpoint**: `POST http://127.0.0.1:8000/api/v1/resume/skills`
- **Job Description Processing Endpoint**: `POST http://127.0.0.1:8000/api/v1/job-description/process`
- **Semantic Similarity Endpoint**: `POST http://127.0.0.1:8000/api/v1/similarity`
- **Resume ↔ Job Match Endpoint**: `POST http://127.0.0.1:8000/api/v1/match`
- **ML Role Classification Endpoint**: `POST http://127.0.0.1:8000/api/v1/role/predict`
- **Interactive OpenAPI Documentation**: `http://127.0.0.1:8000/docs`
