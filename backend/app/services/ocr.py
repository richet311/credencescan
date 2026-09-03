import pymupdf
import easyocr

from app.core.logging import logger

_reader: easyocr.Reader | None = None
_reader_load_error: str | None = None


class OcrExtractionError(Exception):
    pass


def get_reader() -> easyocr.Reader:
    """Loads the OCR model once and caches the result, including a prior
    failure, so a resource-constrained host doesn't retry (and re-fail) a
    slow load on every single request."""
    global _reader, _reader_load_error

    if _reader_load_error is not None:
        raise OcrExtractionError(_reader_load_error)

    if _reader is None:
        logger.info("Loading OCR model (first call only)...")
        try:
            _reader = easyocr.Reader(["en"], gpu=False, verbose=False)
        except Exception as exc:
            _reader_load_error = f"OCR model failed to load: {exc}"
            logger.error(_reader_load_error)
            raise OcrExtractionError(_reader_load_error) from exc

    return _reader


def _ocr_image_bytes(image_bytes: bytes) -> str:
    reader = get_reader()
    try:
        lines = reader.readtext(image_bytes, detail=0, paragraph=True)
    except Exception as exc:
        raise OcrExtractionError(f"OCR failed: {exc}") from exc
    return "\n".join(lines).strip()


def _extract_pdf_text(pdf_bytes: bytes) -> str:
    try:
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    except Exception as exc:
        raise OcrExtractionError(f"Could not open PDF: {exc}") from exc

    with doc:
        text_layers = [page.get_text().strip() for page in doc]

        if any(text_layers):
            return "\n".join(text for text in text_layers if text)

        rendered_pages = []
        for page in doc:
            pixmap = page.get_pixmap(dpi=200)
            rendered_pages.append(_ocr_image_bytes(pixmap.tobytes("png")))
        return "\n".join(rendered_pages).strip()


def extract_text(contents: bytes, content_type: str) -> str:
    if content_type == "application/pdf":
        return _extract_pdf_text(contents)
    return _ocr_image_bytes(contents)
