# New-graduate friendliness prototype

An isolated experiment for predicting whether a software engineering posting welcomes
new graduates. It does not predict interview outcomes or personal eligibility, and is
not imported by the KavEmploy backend or frontend.

## Setup

Run from this directory in PowerShell. Use a separate environment:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Data

Place researched JSONL files in `data/raw/` and reviewed files in `data/reviewed/`.
These directories are ignored by Git except for their placeholder files. Do not commit
collected descriptions, personal research notes, or model artifacts by default.

Each line must contain a JSON object with:

- `record_id`: unique posting identifier
- `company_group_id`: consistent company identifier (used for evaluation splitting)
- `duplicate_group_id`: shared identifier for duplicate/near-duplicate postings
- `title` and `description_text`: original posting text
- `manual_label`: `new_grad_friendly`, `experienced_only`, or `unknown`
- `source_url`, `collected_at`, and label evidence/notes for your audit trail

The trainer uses only manually labeled friendly/experienced-only records. Unknown or
unreviewed records are excluded. Keep duplicate groups within one company group;
duplicate records are reduced to one example, and conflicting duplicate labels fail
validation. AI suggestions must not be copied automatically into `manual_label`.

## Experiment

```powershell
.\.venv\Scripts\python.exe experiment.py train --data data/reviewed/postings.jsonl
.\.venv\Scripts\python.exe experiment.py predict --text-file posting.txt
```

Training uses title and description counts with Multinomial Naive Bayes. Company
groups are held out from training. The report includes per-class precision/recall,
confusion matrices, and a majority-class baseline. A split missing either class fails
with a clear error: collect broader data instead of trusting that evaluation.

Outputs go to `artifacts/`: `model.joblib` and `evaluation.json`. No real dataset or
trained model is included. Predictions are experimental labels, not calibrated
probabilities. A company split does not remove all company cues from descriptions.
One holdout is preliminary evidence; repeat evaluation across datasets before integration.

## Future integration

Keep this prototype independent while collecting data and checking whether it improves
on the existing rule-based classifier. Later, extract its prediction interface into a
backend service returning a label, model version, and evaluation metadata. Retain
graduation eligibility and personal fit as separate results. Never load an untrusted
joblib artifact; only use models you trained locally.
