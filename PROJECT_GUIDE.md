# LegalEase implementation guide

## Why the project is split into backend/frontend

The source specification explicitly calls for Streamlit for user interaction, FastAPI for API handling, a Gemini generator module, and formatting modules for DOCX/PDF/TXT. The implementation keeps those responsibilities separate so each layer can be tested independently.

## Backend responsibilities

- `main.py`: creates FastAPI, CORS and router.
- `routes.py`: HTTP endpoints.
- `schemas.py`: request/response validation.
- `config.py`: `.env` configuration.
- `ai_core/gemini_generator.py`: all Gemini-specific code.
- `services/export_service.py`: document rendering.
- `utils/text.py`: sanitization and term parsing.

## API endpoints

### GET `/`

Basic service information.

### GET `/api/v1/health`

Health and configured model information.

### POST `/api/v1/generate`

Example request:

```json
{
  "document_type": "Employment Contract",
  "parties": "Jane Doe (Employee), Example Corp (Employer)",
  "terms": "Salary is paid monthly;Employee will maintain confidentiality;Either party may terminate with 30 days notice",
  "effective_date": "2026-09-24",
  "jurisdiction": "Tamil Nadu, India",
  "special_instructions": "Use clear numbered clauses."
}
```

### POST `/api/v1/export/txt`

Returns UTF-8 plain text.

### POST `/api/v1/export/docx`

Returns a Word document with Times New Roman formatting, title, optional logo, key-terms table and footer.

### POST `/api/v1/export/pdf`

Returns a PDF with a branded header/footer and formatted sections.

## How Gemini is integrated

The generator creates a structured prompt containing:

- document type
- parties
- effective date
- jurisdiction
- terms
- special instructions

The system instruction tells the model not to fabricate missing facts and to produce a draft rather than legal advice.

The API key remains in the backend environment.

## Demo mode

`DEMO_MODE=true` bypasses the external Gemini API and generates a deterministic legal-draft template. This is intentional: it makes local UI, API and export testing possible without a paid/external model call.

## Production hardening ideas

For a production deployment, add:

- authentication and authorization
- rate limiting
- audit logging with data minimization
- encrypted storage if documents are persisted
- malware scanning for uploaded files
- a secure object store for generated documents
- secrets management
- structured observability
- organization-specific legal review workflows
- model/provider allow-listing
- prompt-injection and data-loss controls
- jurisdiction-specific validation
- human review before document execution

The supplied project documentation describes the application as secure/scalable, but it does not specify an authentication, database, encryption, or audit architecture. Those features are therefore not silently invented here.
