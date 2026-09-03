from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status

from app.core.deps import get_current_user
from app.core.file_validation import FileValidationError, validate_upload
from app.core.logging import logger
from app.core.security import limiter
from app.services.classifier import ClassifierNotTrainedError, classify_document
from app.services.history import get_history, record_analysis
from app.services.insights import extract_fields, generate_insights
from app.services.ocr import OcrExtractionError, extract_text

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload")
@limiter.limit("10/minute")
async def upload_document(request: Request, file: UploadFile):
    try:
        contents, content_type = await validate_upload(file)
    except FileValidationError as exc:
        logger.warning("Rejected upload '%s': %s", file.filename, exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc

    logger.info("Accepted upload '%s' (%d bytes)", file.filename, len(contents))

    try:
        extracted_text = extract_text(contents, content_type)
    except OcrExtractionError as exc:
        logger.error("Text extraction failed for '%s': %s", file.filename, exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not extract text from this file.",
        ) from exc

    document_type = None
    confidence = None
    try:
        classification = classify_document(extracted_text)
        document_type = classification["document_type"]
        confidence = classification["confidence"]
    except ClassifierNotTrainedError as exc:
        logger.warning("Classification skipped for '%s': %s", file.filename, exc)

    fields = extract_fields(extracted_text)
    insights = generate_insights(fields)

    record_analysis(
        filename=file.filename,
        document_type=document_type,
        confidence=confidence,
        insights=insights,
    )

    return {
        "filename": file.filename,
        "size_bytes": len(contents),
        "content_type": content_type,
        "status": "received",
        "extracted_text": extracted_text,
        "document_type": document_type,
        "confidence": confidence,
        "fields": fields,
        "insights": insights,
    }


@router.get("/history")
@limiter.limit("30/minute")
async def document_history(request: Request, user: str = Depends(get_current_user)):
    return {"history": get_history()}
