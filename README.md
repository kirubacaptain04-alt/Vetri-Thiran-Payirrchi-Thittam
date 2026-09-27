# LegalEase — AI-Powered Legal Document Generator

LegalEase is a full-stack application based on the supplied project specification: Streamlit frontend, FastAPI backend, Gemini-powered generation, editable preview, and TXT/DOCX/PDF export.

## Important modernization

The supplied specification names `gemini-1.5-pro` and the older `google-generativeai` SDK. The implementation here uses Google's current `google-genai` Python SDK and makes the model configurable through `GEMINI_MODEL`. The default is `gemini-3.8-flash`, while you can set another model available to your Gemini API account in `.env`.

Official Gemini documentation currently shows the Python pattern `from google import genai` and `client.models.generate_content(...)`. See the links in the project documentation/source notes.

## Architecture

```text
Browser
  |
  v
Streamlit frontend :8501
  |
  | HTTP JSON
  v
FastAPI backend :8000
  |
  +--> GeminiDocumentGenerator --> Gemini API
  |
  +--> ExportService --> TXT / DOCX / PDF
```

## Features

- Employment contracts, NDAs, leases, service agreements, offer letters, and custom document types.
- Structured input: document type, parties, terms, effective date, optional jurisdiction and special instructions.
- Gemini generation with a legal-drafting system prompt.
- Demo mode when no API key is available.
- Editable document preview.
- TXT, DOCX and PDF export.
- Optional company name, logo and footer branding.
- Terms table in DOCX.
- Branded header/footer in PDF.
- FastAPI validation and CORS.
- Health endpoint.
- Unit/API tests.
- Docker Compose for local containerized startup.

## 1. Prerequisites

- Python 3.11 or newer
- VS Code
- A Gemini API key if you want real AI generation
- Optional: Docker Desktop

## 2. VS Code setup

Open the `LegalEase` folder in VS Code.

Create a virtual environment:

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### macOS/Linux

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your API key:

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.8-flash
DEMO_MODE=false
BACKEND_URL=http://127.0.0.1:8000
```

If you do not have a key yet, use:

```env
DEMO_MODE=true
```

This lets you test the complete UI/export workflow without calling Gemini.

## 3. Run the backend

Terminal 1:

```bash
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Check:

- API root: `http://127.0.0.1:8000/`
- Health: `http://127.0.0.1:8000/health`
- Swagger: `http://127.0.0.1:8000/docs`

## 4. Run the frontend

Terminal 2, with the same virtual environment:

```bash
streamlit run frontend/app.py --server.port 8501
```

Open:

```text
http://localhost:8501
```

## 5. End-to-end test

1. Select or type a document type.
2. Enter parties.
3. Enter terms separated by semicolons.
4. Enter an effective date.
5. Optionally enter jurisdiction, company name, footer and upload a logo.
6. Click **Generate Document**.
7. Edit the generated text if needed.
8. Download TXT, DOCX or PDF.
9. Open the generated files and verify headings, clauses, branding and footer.

## 6. API test with curl

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d "{\"document_type\":\"NDA\",\"parties\":\"Alice Smith (Disclosing Party), Example Corp (Receiving Party)\",\"terms\":\"Confidential information must be protected;Agreement starts on 2026-09-24;Either party may terminate on 15 days notice\",\"effective_date\":\"2026-09-24\"}"
```

## 7. Automated tests

With the virtual environment active:

```bash
pytest -q
```

The tests run with `DEMO_MODE=true` so they do not require an API key.

## 8. Docker

```bash
docker compose up --build
```

Then open:

- Frontend: `http://localhost:8501`
- Backend: `http://localhost:8000/docs`

For real Gemini generation, put the key in `.env` before starting Docker Compose.

## 9. Project structure

```text
LegalEase/
├── backend/
│   ├── __init__.py
│   └── app/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       ├── schemas.py
│       ├── routes.py
│       ├── ai_core/
│       │   ├── __init__.py
│       │   └── gemini_generator.py
│       ├── services/
│       │   ├── __init__.py
│       │   └── export_service.py
│       └── utils/
│           ├── __init__.py
│           └── text.py
├── frontend/
│   └── app.py
├── assets/
│   └── .gitkeep
├── tests/
│   ├── __init__.py
│   └── test_api.py
├── .env.example
├── .gitignore
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Security notes

- Never commit `.env`.
- Keep the Gemini API key only on the backend.
- Do not place the API key in Streamlit code.
- This project generates legal-information drafts and should not be treated as a substitute for review by a qualified lawyer.
- Do not send confidential client material to an external model unless your organization's policies and the applicable law permit it.

## Troubleshooting

### `Connection refused` in Streamlit

Make sure FastAPI is running on port 8000.

### Gemini errors

Check `GEMINI_API_KEY`, model availability, billing/quota and the value of `GEMINI_MODEL`.

### PowerShell blocks activation

Run PowerShell as appropriate for your machine and, if permitted by your organization, use:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate the environment again.

### PDF has unusual characters

The PDF exporter deliberately normalizes typography to a PDF-safe character set when using the built-in FPDF font. This prevents broken glyphs on machines without a Unicode font.
