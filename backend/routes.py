from fastapi import APIRouter, HTTPException

from backend.models import DocumentRequest
from ai_core.gemini_generator import GeminiDocumentGenerator


router = APIRouter()

generator = GeminiDocumentGenerator()


@router.post("/generate")
def generate_document(request: DocumentRequest):
    """
    Generate a legal document from the supplied information.
    """

    try:
        document = generator.generate_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            effective_date=request.effective_date,
            jurisdiction=request.jurisdiction,
            additional_instructions=request.additional_instructions,
        )

        return {
            "success": True,
            "document_type": request.document_type,
            "content": document,
            "mode": generator.mode,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc