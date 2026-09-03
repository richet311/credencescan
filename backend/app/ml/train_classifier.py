import csv
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

DATA_PATH = Path(__file__).parent / "data" / "synthetic_documents.csv"
MODEL_DIR = Path(__file__).parent / "model"
MODEL_PATH = MODEL_DIR / "classifier.joblib"


def load_dataset() -> tuple[list[str], list[str]]:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"{DATA_PATH} not found. Run `python -m app.ml.generate_dataset` first."
        )

    texts, labels = [], []
    with DATA_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            texts.append(row["text"])
            labels.append(row["label"])
    return texts, labels


def train() -> None:
    texts, labels = load_dataset()
    x_train, x_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )

    pipeline = Pipeline(
        [
            ("tfidf", TfidfVectorizer(max_features=2000, ngram_range=(1, 2))),
            ("clf", LogisticRegression(max_iter=1000)),
        ]
    )
    pipeline.fit(x_train, y_train)

    predictions = pipeline.predict(x_test)
    print(classification_report(y_test, predictions))

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"Saved trained classifier to {MODEL_PATH}")


if __name__ == "__main__":
    train()
