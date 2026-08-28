from fastapi import APIRouter, HTTPException, Request, UploadFile, status

from app.core.file_validation import FileValidationError, validate_upload
from app.core.logging import logger
from app.core.security import limiter

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload")
@limiter.limit("10/minute")
async def upload_document(request: Request, file: UploadFile):
    try:
        contents = await validate_upload(file)
    except FileValidationError as exc:
        logger.warning("Rejected upload '%s': %s", file.filename, exc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    logger.info("Accepted upload '%s' (%d bytes)", file.filename, len(contents))

    return {
        "filename": file.filename,
        "size_bytes": len(contents),
        "status": "received",
    }
