from pathlib import Path

import joblib

MODEL_PATH = Path(__file__).resolve().parent.parent / "ml" / "model" / "classifier.joblib"

_model = None


class ClassifierNotTrainedError(Exception):
    pass


def get_model():
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            raise ClassifierNotTrainedError(
                "No trained classifier found. Run `python -m app.ml.generate_dataset` "
                "and `python -m app.ml.train_classifier` first."
            )
        _model = joblib.load(MODEL_PATH)
    return _model


def classify_document(text: str) -> dict:
    model = get_model()
    label = model.predict([text])[0]
    confidence = float(max(model.predict_proba([text])[0]))
    return {"document_type": label, "confidence": round(confidence, 4)}
