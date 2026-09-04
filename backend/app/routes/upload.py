from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.schemas.schemas import UploadResponse, ProcessingStatus
from app.services.extraction_service import TextExtractionService
from app.config.redis_client import redis_client
from app.config.settings import settings
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/v1/reports", tags=["upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_report(file: UploadFile = File(...)):
    """Upload pathology report for analysis"""

    # Validate file type
    allowed_types = ["application/pdf", "text/plain", "image/jpeg", "image/png",
                     "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]

    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="File type not supported")

    # Read file content
    file_content = await file.read()

    # Validate file size
    if len(file_content) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")

    # Create session
    session_id = str(uuid.uuid4())

    # Store file in Redis temporarily
    file_key = f"file:{session_id}"
    redis_client.set_bytes(file_key, file_content, ttl=settings.SESSION_TTL)

    # Store metadata
    metadata = {
        "filename": file.filename,
        "file_size": len(file_content),
        "content_type": file.content_type,
        "upload_time": datetime.now().isoformat(),
        "status": "uploaded"
    }
    redis_client.set_json(f"metadata:{session_id}", metadata, ttl=settings.SESSION_TTL)

    # Extract text immediately
    try:
        extracted_text, extraction_method = TextExtractionService.extract_text(
            file_content, file.content_type
        )

        if not extracted_text or len(extracted_text.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Unable to extract text from file. Please ensure the file is readable."
            )

        # Clean text
        cleaned_text = TextExtractionService.clean_text(extracted_text)

        # Store extracted text
        redis_client.set_json(
            f"extracted_text:{session_id}",
            {"text": cleaned_text, "method": extraction_method},
            ttl=settings.SESSION_TTL
        )

        # Update status
        metadata["status"] = "extracted"
        redis_client.set_json(f"metadata:{session_id}", metadata, ttl=settings.SESSION_TTL)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text extraction failed: {str(e)}")

    return UploadResponse(
        session_id=session_id,
        filename=file.filename,
        file_size=len(file_content),
        status="processing",
        message="File uploaded successfully and text extracted"
    )


@router.get("/status/{session_id}", response_model=ProcessingStatus)
async def get_status(session_id: str):
    """Get processing status for a session"""

    metadata = redis_client.get_json(f"metadata:{session_id}")

    if not metadata:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    status = metadata.get("status", "unknown")

    if status == "uploaded":
        stage = "upload"
        progress = 100
        message = "File uploaded successfully"
    elif status == "extracted":
        stage = "extraction"
        progress = 100
        message = "Text extracted successfully"
    elif status == "analyzed":
        stage = "analysis"
        progress = 100
        message = "Lab tests analyzed successfully"
    elif status == "completed":
        stage = "completed"
        progress = 100
        message = "Processing completed"
    else:
        stage = "upload"
        progress = 0
        message = "Processing..."

    return ProcessingStatus(
        session_id=session_id,
        stage=stage,
        progress=progress,
        message=message
    )


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete session data"""

    # Delete all related keys
    redis_client.delete(f"file:{session_id}")
    redis_client.delete(f"metadata:{session_id}")
    redis_client.delete(f"extracted_text:{session_id}")
    redis_client.delete(f"lab_results:{session_id}")
    redis_client.delete(f"organ_scores:{session_id}")

    return JSONResponse({"message": "Session deleted successfully"})
