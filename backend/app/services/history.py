from collections import deque
from datetime import datetime, timezone

_history: deque[dict] = deque(maxlen=50)


def record_analysis(
    filename: str,
    document_type: str | None,
    confidence: float | None,
    insights: list[str],
) -> None:
    _history.appendleft(
        {
            "filename": filename,
            "document_type": document_type,
            "confidence": confidence,
            "insights": insights,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        }
    )


def get_history() -> list[dict]:
    return list(_history)
