from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from app.schemas.schemas import PDFGenerateResponse
from app.services.pdf_service import PDFGenerationService
from app.config.redis_client import redis_client
from app.config.settings import settings
from datetime import datetime
import uuid
import os

router = APIRouter(prefix="/api/v1/pdf", tags=["pdf"])


def _build_pdf(session_id: str):
    lab_results = redis_client.get_json(f"lab_results:{session_id}")
    organ_scores = redis_client.get_json(f"organ_scores:{session_id}")
    if not lab_results:
        raise HTTPException(status_code=404, detail="Lab results not found")
    if not organ_scores:
        raise HTTPException(status_code=404, detail="Organ scores not calculated")

    session_data = {"lab_results": lab_results}
    os.makedirs(settings.PDF_OUTPUT_DIR, exist_ok=True)
    return PDFGenerationService.generate_pdf(session_data, organ_scores, settings.PDF_OUTPUT_DIR)


@router.post("/generate/{session_id}", response_model=PDFGenerateResponse)
async def generate_pdf(session_id: str):
    """Generate a PDF report and keep the source session in Redis."""
    try:
        pdf_path = _build_pdf(session_id)
        pdf_id = str(uuid.uuid4())
        pdf_metadata = {
            "pdf_id": pdf_id,
            "session_id": session_id,
            "pdf_path": pdf_path,
            "filename": os.path.basename(pdf_path),
            "generation_date": datetime.now().isoformat()
        }
        redis_client.set_json(f"pdf:{pdf_id}", pdf_metadata, ttl=86400)

        # Uploaded binary and extracted source text are deleted after PDF creation.
        redis_client.delete(f"file:{session_id}")
        redis_client.delete(f"extracted_text:{session_id}")

        return PDFGenerateResponse(
            pdf_id=pdf_id,
            pdf_url=f"/api/v1/pdf/{pdf_id}",
            message="PDF generated successfully. Uploaded report data has been deleted for privacy.",
            generation_date=datetime.now()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


def _serve_pdf(pdf_id: str, download: bool = False):
    metadata = redis_client.get_json(f"pdf:{pdf_id}")
    if not metadata:
        raise HTTPException(status_code=404, detail="PDF not found or expired")

    pdf_path = metadata.get("pdf_path", "")
    # Vercel instances are ephemeral. Rebuild the PDF when the previous /tmp
    # file is no longer present, using only the sanitized Redis session data.
    if not os.path.exists(pdf_path):
        pdf_path = _build_pdf(metadata["session_id"])

    headers = {"Content-Disposition": f"attachment; filename={metadata['filename']}"} if download else None
    return FileResponse(pdf_path, media_type="application/pdf", filename=metadata["filename"], headers=headers)


@router.get("/{pdf_id}")
async def get_pdf(pdf_id: str):
    return _serve_pdf(pdf_id, download=False)


@router.get("/{pdf_id}/download")
async def download_pdf(pdf_id: str):
    return _serve_pdf(pdf_id, download=True)


@router.delete("/{pdf_id}")
async def delete_pdf(pdf_id: str):
    metadata = redis_client.get_json(f"pdf:{pdf_id}")
    if not metadata:
        raise HTTPException(status_code=404, detail="PDF not found")

    pdf_path = metadata.get("pdf_path", "")
    if pdf_path and os.path.exists(pdf_path):
        os.remove(pdf_path)
    redis_client.delete(f"pdf:{pdf_id}")
    return JSONResponse({"message": "PDF file deleted successfully"})
