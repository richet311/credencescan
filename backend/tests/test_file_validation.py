import io

import pytest
from fastapi import UploadFile

from app.core.file_validation import FileValidationError, validate_upload


def _make_upload(data: bytes, filename: str = "test.pdf") -> UploadFile:
    return UploadFile(file=io.BytesIO(data), filename=filename)


async def test_valid_pdf_signature_accepted():
    upload = _make_upload(b"%PDF-1.4 minimal pdf content")
    contents, content_type = await validate_upload(upload)
    assert content_type == "application/pdf"
    assert contents.startswith(b"%PDF")


async def test_valid_png_signature_accepted():
    data = b"\x89PNG\r\n\x1a\n" + b"rest of png bytes"
    upload = _make_upload(data, filename="test.png")
    _, content_type = await validate_upload(upload)
    assert content_type == "image/png"


async def test_empty_file_rejected():
    upload = _make_upload(b"")
    with pytest.raises(FileValidationError, match="empty"):
        await validate_upload(upload)


async def test_wrong_signature_rejected():
    upload = _make_upload(b"just plain text, not a real file")
    with pytest.raises(FileValidationError, match="Unsupported file type"):
        await validate_upload(upload)


async def test_oversized_file_rejected(monkeypatch):
    from app.core import file_validation

    monkeypatch.setattr(file_validation.settings, "max_upload_size_bytes", 10)
    upload = _make_upload(b"%PDF-1.4" + b"0" * 100)
    with pytest.raises(FileValidationError, match="exceeds"):
        await validate_upload(upload)
