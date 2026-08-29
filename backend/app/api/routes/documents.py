from fastapi import APIRouter, HTTPException, Request, UploadFile, status

from app.core.file_validation import FileValidationError, validate_upload
from app.core.logging import logger
from app.core.security import limiter
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

    return {
        "filename": file.filename,
        "size_bytes": len(contents),
        "content_type": content_type,
        "status": "received",
        "extracted_text": extracted_text,
    }
