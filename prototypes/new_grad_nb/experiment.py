"""Standalone experiment; no imports from or changes to the application."""

import argparse
import json
from pathlib import Path

LABELS = ["experienced_only", "new_grad_friendly"]


def load_records(path):
    records = []
    seen_ids = set()
    duplicates = {}
    with path.open(encoding="utf-8-sig") as source:
        for line_number, line in enumerate(source, 1):
            if not line.strip():
                continue
            record = json.loads(line)
            if record.get("manual_label") in (None, "", "unknown"):
                continue
            if record["manual_label"] not in LABELS:
                raise ValueError(f"Line {line_number}: invalid manual_label")
            for field in ("record_id", "company_group_id", "duplicate_group_id",
                          "title", "description_text"):
                if not isinstance(record.get(field), str) or not record[field].strip():
                    raise ValueError(f"Line {line_number}: missing/non-text {field}")
            if record["record_id"] in seen_ids:
                raise ValueError(f"Line {line_number}: duplicate record_id")
            seen_ids.add(record["record_id"])
            group = record["duplicate_group_id"]
            signature = (record["company_group_id"], record["manual_label"])
            if group in duplicates:
                if duplicates[group] != signature:
                    raise ValueError(f"Line {line_number}: inconsistent duplicate group")
                continue
            duplicates[group] = signature
            records.append(record)
    if {record["manual_label"] for record in records} != set(LABELS):
        raise ValueError("Reviewed data must contain both classes")
    return records


def train(args):
    import joblib
    from sklearn.dummy import DummyClassifier
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.metrics import classification_report, confusion_matrix
    from sklearn.model_selection import GroupShuffleSplit
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import Pipeline

    records = load_records(args.data)
    texts = [r["title"] + "\n" + r["description_text"] for r in records]
    labels = [r["manual_label"] for r in records]
    groups = [r["company_group_id"] for r in records]
    split = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=args.seed)
    train_indices, test_indices = next(split.split(texts, labels, groups))
    for indices in (train_indices, test_indices):
        if {labels[i] for i in indices} != set(LABELS):
            raise ValueError("Both training and held-out companies must contain both classes")
    model = Pipeline([
        ("vectorizer", CountVectorizer(lowercase=True, ngram_range=(1, 2))),
        ("classifier", MultinomialNB(alpha=1.0)),
    ])
    model.fit([texts[i] for i in train_indices], [labels[i] for i in train_indices])
    truth = [labels[i] for i in test_indices]
    predicted = model.predict([texts[i] for i in test_indices])
    baseline = DummyClassifier(strategy="most_frequent")
    baseline.fit([[0] for _ in train_indices], [labels[i] for i in train_indices])
    report = {
        "version": "new-grad-nb-v1", "seed": args.seed,
        "training_records": [records[i]["record_id"] for i in train_indices],
        "evaluation_records": [records[i]["record_id"] for i in test_indices],
        "metrics": classification_report(truth, predicted, labels=LABELS,
                                         output_dict=True, zero_division=0),
        "confusion_matrix_labels": LABELS,
        "confusion_matrix": confusion_matrix(truth, predicted, labels=LABELS).tolist(),
        "baseline": classification_report(
            truth, baseline.predict([[0] for _ in test_indices]),
            labels=LABELS, output_dict=True, zero_division=0),
    }
    args.output.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "version": report["version"]}, args.output / "model.joblib")
    (args.output / "evaluation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


def predict(args):
    import joblib

    artifact = joblib.load(args.model)
    text = args.text_file.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError("Posting text must not be blank")
    print(json.dumps({"label": artifact["model"].predict([text])[0],
                      "version": artifact["version"], "experimental": True}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    training = commands.add_parser("train")
    training.add_argument("--data", type=Path, required=True)
    training.add_argument("--output", type=Path, default=Path("artifacts"))
    training.add_argument("--seed", type=int, default=42)
    training.set_defaults(run=train)
    prediction = commands.add_parser("predict")
    prediction.add_argument("--text-file", type=Path, required=True)
    prediction.add_argument("--model", type=Path, default=Path("artifacts/model.joblib"))
    prediction.set_defaults(run=predict)
    args = parser.parse_args()
    try:
        args.run(args)
    except (ValueError, OSError, ImportError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
