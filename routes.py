from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from .ai_core.gemini_generator import GeminiDocumentGenerator
from .config import get_settings
from .schemas import DocumentRequest, ExportRequest, GenerateResponse
from .services.export_service import format_docx, format_pdf
from .utils.text import sanitize_text

router = APIRouter(prefix="/api/v1", tags=["LegalEase"])
settings = get_settings()
generator = GeminiDocumentGenerator(settings)


@router.get("/health")
def api_health():
    return {
        "status": "ok",
        "service": "LegalEase API",
        "model": settings.gemini_model,
        "demo_mode": settings.demo_mode,
    }


@router.post("/generate", response_model=GenerateResponse)
def generate_document(request: DocumentRequest):
    try:
        text = generator.generate_document(request)
        return GenerateResponse(
            document_type=request.document_type,
            text=sanitize_text(text),
            model=settings.gemini_model,
            demo_mode=settings.demo_mode or generator.client is None,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Document generation failed: {exc}",
        ) from exc


@router.post("/export/txt")
def export_txt(request: ExportRequest):
    content = sanitize_text(request.text).encode("utf-8")
    return Response(
        content=content,
        media_type="text/plain; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{_filename(request.document_type)}.txt"'
        },
    )


@router.post("/export/docx")
def export_docx(request: ExportRequest):
    try:
        content = format_docx(
            text=request.text,
            doc_type=request.document_type,
            terms=request.terms,
            company_name=request.company_name,
            footer_text=request.footer_text,
            logo_data_url=request.logo_data_url,
        )
        return Response(
            content=content,
            media_type=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            headers={
                "Content-Disposition": (
                    f'attachment; filename="{_filename(request.document_type)}.docx"'
                )
            },
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"DOCX export failed: {exc}") from exc


@router.post("/export/pdf")
def export_pdf(request: ExportRequest):
    try:
        content = format_pdf(
            text=request.text,
            doc_type=request.document_type,
            terms=request.terms,
            company_name=request.company_name,
            footer_text=request.footer_text,
            logo_data_url=request.logo_data_url,
        )
        return Response(
            content=content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": (
                    f'attachment; filename="{_filename(request.document_type)}.pdf"'
                )
            },
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"PDF export failed: {exc}") from exc


def _filename(document_type: str) -> str:
    safe = "".join(
        char.lower() if char.isalnum() else "_"
        for char in document_type.strip()
    )
    return safe.strip("_") or "legalease_document"
