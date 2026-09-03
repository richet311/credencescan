from fastapi import UploadFile

from app.core.config import settings

ALLOWED_SIGNATURES = {
    b"%PDF": "application/pdf",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"\xff\xd8\xff": "image/jpeg",
}


CHUNK_SIZE = 64 * 1024


class FileValidationError(Exception):
    pass


async def validate_upload(file: UploadFile) -> tuple[bytes, str]:
    """Reads the upload in bounded chunks so an oversized file is rejected
    before it's ever fully buffered in memory, rather than after."""
    max_size = settings.max_upload_size_bytes
    limit_mb = max_size // (1024 * 1024)

    chunks = []
    total = 0
    while True:
        chunk = await file.read(CHUNK_SIZE)
        if not chunk:
            break
        total += len(chunk)
        if total > max_size:
            raise FileValidationError(f"File exceeds the {limit_mb}MB limit.")
        chunks.append(chunk)

    contents = b"".join(chunks)

    if len(contents) == 0:
        raise FileValidationError("Uploaded file is empty.")

    for signature, content_type in ALLOWED_SIGNATURES.items():
        if contents.startswith(signature):
            return contents, content_type

    raise FileValidationError(
        "Unsupported file type. Only PDF, PNG, and JPEG are accepted."
    )
