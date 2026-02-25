# 📄 Resume Analyzer API

An AI-powered resume analysis API built with **FastAPI** and **Groq (LLaMA)** that provides ATS compatibility scoring, keyword analysis, and actionable feedback — with optional PDF report generation.

---

## ✨ Features

- 📊 **ATS Score** — Get a 0–100 ATS compatibility score for any resume
- 💪 **Strengths Analysis** — Identify what's working well in the resume
- 🔧 **Improvement Areas** — Pinpoint weaknesses to address
- 🔑 **Missing Keywords** — Detect keywords absent from the resume (especially vs. a job description)
- 💡 **Actionable Suggestions** — Concrete steps to improve the resume
- 📥 **PDF Report Download** — Generate a professional PDF report of the analysis
- 🛡️ **Resume Validation** — Rejects non-resume documents automatically

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| AI Model | Groq API (LLaMA 3 8B) |
| PDF Parsing | PyPDF2 |
| PDF Generation | ReportLab |
| Validation | Pydantic v2 |
| Config | pydantic-settings |
| Server | Uvicorn |

---

## 📁 Project Structure

```
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── health.py        # Health check endpoint
│   │       ├── resume.py        # Resume analysis endpoint
│   │       └── report.py        # PDF report download endpoint
│   ├── core/
│   │   ├── config.py            # Environment-based configuration
│   │   ├── logging.py           # Centralized logging
│   │   └── security.py          # CORS, sanitization utilities
│   ├── exceptions/              # Custom exception classes
│   ├── schemas/
│   │   ├── resume.py            # AnalysisResult model
│   │   └── response.py          # Standard response models
│   ├── services/
│   │   ├── analysis_service.py  # Orchestrates the full workflow
│   │   ├── groq_service.py      # Groq API integration
│   │   ├── pdf_service.py       # PDF text extraction
│   │   └── pdf_report_service.py# PDF report generation
│   ├── utils/
│   │   ├── helpers.py           # Text cleaning utilities
│   │   ├── resume_validator.py  # Resume content validation
│   │   └── validators.py        # File upload validation
│   └── main.py                  # FastAPI app entrypoint
├── tests/
├── .env.example
├── requirements.txt
├── runtime.txt
└── run.py
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- A [Groq API key](https://console.groq.com/)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/resume-analyzer-api.git
cd resume-analyzer-api

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file in the root directory:

```env
# Application
APP_NAME=Resume Analyzer API
APP_VERSION=1.0.0
DEBUG=false
ENVIRONMENT=production

# Server
HOST=0.0.0.0
PORT=5000

# Groq API
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=llama3-8b-8192
GROQ_MAX_TOKENS=2000
GROQ_TEMPERATURE=0.7

# CORS (comma-separated origins, or leave empty for *)
ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend.com

# File Uploads
MAX_FILE_SIZE_MB=10

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Running the Server

```bash
python run.py
```

The API will be available at `http://localhost:5000`.

For development with auto-reload, set `DEBUG=true` in your `.env` and the server will reload on file changes. Swagger docs will also be available at `http://localhost:5000/docs`.

---

## 📡 API Endpoints

### `GET /health`
Returns the application health status.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production"
}
```

---

### `POST /api/analyze`
Analyzes a resume PDF and returns structured feedback.

**Request:** `multipart/form-data`

| Field | Type | Required | Description |
|---|---|---|---|
| `resume` | File (PDF) | ✅ Yes | Resume PDF (max 10MB) |
| `jobDescription` | String | ❌ No | Job description for targeted analysis |

**Response:**
```json
{
  "atsScore": 75,
  "strengths": [
    "Clear professional summary",
    "Quantified achievements with metrics"
  ],
  "improvements": [
    "Add more technical skills",
    "Include certifications"
  ],
  "missingKeywords": [
    "Project Management",
    "Agile"
  ],
  "suggestions": [
    "Use consistent action verbs",
    "Add a technical skills section"
  ]
}
```

---

### `POST /api/download-report`
Generates and downloads a PDF report from an existing analysis result.

**Request Body:** The `AnalysisResult` JSON object returned from `/api/analyze`

**Response:** A downloadable PDF file (`application/pdf`)

---

## ⚙️ How It Works

```
User uploads PDF
      ↓
File Validation (size, type)
      ↓
PDF Text Extraction (PyPDF2)
      ↓
Resume Validation (keyword scoring)
      ↓
AI Analysis via Groq API (LLaMA 3)
      ↓
Structured JSON Response
      ↓
(Optional) PDF Report Generation (ReportLab)
```

---

## 🧪 Running Tests

```bash
pytest tests/
```

---

## 🔒 Security Notes

- API keys are loaded from environment variables — never hardcoded
- File uploads are validated for type and size before processing
- Filenames are sanitized to prevent path traversal attacks
- CORS origins are configurable via environment variables

---

## 📦 Deployment

This project includes a `runtime.txt` specifying Python 3.11.9, making it compatible with platforms like **Railway**, **Render**, or **Heroku**.

Make sure to set all required environment variables (especially `GROQ_API_KEY`) in your deployment platform's settings.

---

## 📄 License

This project is licensed under the MIT License.
