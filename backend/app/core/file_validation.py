from fastapi import UploadFile

from app.core.config import settings

ALLOWED_SIGNATURES = {
    b"%PDF": "application/pdf",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"\xff\xd8\xff": "image/jpeg",
}


class FileValidationError(Exception):
    pass


async def validate_upload(file: UploadFile) -> tuple[bytes, str]:
    contents = await file.read()

    if len(contents) == 0:
        raise FileValidationError("Uploaded file is empty.")

    if len(contents) > settings.max_upload_size_bytes:
        limit_mb = settings.max_upload_size_bytes // (1024 * 1024)
        raise FileValidationError(f"File exceeds the {limit_mb}MB limit.")

    for signature, content_type in ALLOWED_SIGNATURES.items():
        if contents.startswith(signature):
            return contents, content_type

    raise FileValidationError(
        "Unsupported file type. Only PDF, PNG, and JPEG are accepted."
    )
