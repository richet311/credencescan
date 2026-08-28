from fastapi import UploadFile

from app.core.config import settings

ALLOWED_SIGNATURES = {
    b"%PDF": "application/pdf",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"\xff\xd8\xff": "image/jpeg",
}


class FileValidationError(Exception):
    pass


async def validate_upload(file: UploadFile) -> bytes:
    contents = await file.read()

    if len(contents) == 0:
        raise FileValidationError("Uploaded file is empty.")

    if len(contents) > settings.max_upload_size_bytes:
        limit_mb = settings.max_upload_size_bytes // (1024 * 1024)
        raise FileValidationError(f"File exceeds the {limit_mb}MB limit.")

    if not any(contents.startswith(signature) for signature in ALLOWED_SIGNATURES):
        raise FileValidationError(
            "Unsupported file type. Only PDF, PNG, and JPEG are accepted."
        )

    return contents
