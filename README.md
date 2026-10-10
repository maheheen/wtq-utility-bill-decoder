# Utility Bill Decoder (WTQ Build Track)

Reads electricity bill images from K-Electric, LESCO and IESCO. Level 1 extracts structured details as JSON. Level 2 answers 12 customer questions per bill in plain English, grounded in the numbers on the bill.

## Requirements
Python 3.14.3 (tested on this version)

## Setup
```
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then put your real API key in .env
```

## Run
On a folder of bill images plus the two CSV templates:
```
python -m src.run --bills ../data/test/bills --level1 ../data/test/csv/level1.csv --level2 ../data/test/csv/level2.csv --out ../output
```
This writes `level1.csv` and `level2.csv` into the output folder. Results are cached in `.cache/`, so a rerun gives the same answers. Delete `.cache/` to force fresh model calls.

Check the output:
```
python tools/verify_outputs.py
```

## How it works
1. Vision extraction of each bill into a fixed JSON schema (model temperature 0 where supported), validated with pydantic.
2. Printed values are taken as printed and never rewritten by code. Results are cached on disk by hash of image, prompt, model and schema, so reruns give the same answer.
3. A second extraction pulls the extras needed for questions (usage history, payment history, printed percentage split, slab lines).
4. Python computes derived numbers (shares, averages, counts, late surcharge). The LLM never does arithmetic.
5. One call per bill answers all 12 questions from the validated data and the computed facts sheet. Missing information is stated, never guessed.
6. CSVs are written with the csv library using the supplied templates, keeping order and columns.

## Error handling
Retries with backoff on API errors and rate limits. A bill that fails completely still produces a valid null-filled JSON and an honest answer, never an empty cell.

## AI usage
- Models called by the solution: gemini-3.5-flash-lite via Google (MODEL_PROVIDER=google, MODEL_NAME=gemini-3.5-flash-lite, same as .env.example). Three calls per bill: Level 1 extraction (image), extras extraction (image), Level 2 answers (text).
- APIs: Google Gemini API through the google-genai Python SDK
- Services: none
- Local OCR libraries: none
- AI tools used to write the code:
  - Claude Code (Sonnet)
  - Claude chat (planning and project kit)
  - <other chat used for layout notes>

## Project layout
```
src/       pipeline code
tools/     verify_outputs.py, make_zip.py, make_fake_templates.py
tests/     golden test for KESC_0008 (run: pytest)
docs/      spec, plan, layout notes
```
