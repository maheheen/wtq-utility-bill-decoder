# WTQ Utility Bill Decoder

Timed competition build. Be fast, small, and boring. Spec is in docs/SPEC.md (read it once per session, never the PDF). Progress is in STATUS.md (read it first, update it after each milestone).

## Goal
CLI that reads electricity bill images (K-Electric, LESCO, IESCO) and fills two CSV templates:
- Level 1: one JSON object per bill (extraction)
- Level 2: one plain-English answer per bill and question (explanation)

## Hard rules
- The solution may call ONLY these models: claude-haiku-4-5, gemini-3.5-flash-lite, gemini-3.1-flash-lite, gpt-4.1-mini, gpt-5-mini. Anything else is disqualification.
- Banned: Azure prebuilt-invoice, Textract AnalyzeExpense, Mindee or any invoice/receipt extraction service. Local OCR (Tesseract, PaddleOCR) is allowed but optional.
- CSVs must be produced by the code. Never hand-edit results.
- Never output personal identifiers (names, addresses, CNIC, account, reference, consumer or meter numbers).
- No API keys in code or in the repo. Read them from .env. Keep .env.example current.
- Python 3.14.3 (tested on this version), requirements.txt with exact versions (package==x.y.z).
- Rerun on the same bill must give the same answer: temperature 0 where the model supports it (GPT-5 mini does not), fixed prompts, disk cache, sorted keys.
- Level 1 values are extracted AS PRINTED. Checks may trigger a re-read, but code never "corrects" a printed amount.

## How to work (token discipline)
- Read STATUS.md first. Do not re-read files you just wrote. Do not print whole files or long logs, use head/tail.
- Do not open bill images unless I ask. My notes on layouts are in docs/LAYOUTS.md.
- One module at a time. Run the smallest test that proves it works.
- Plain code, few dependencies: pydantic, python-dotenv, pillow, tenacity, plus the provider SDKs I actually use.
- After each milestone: update STATUS.md (max 10 lines) and git commit.
- If you hit a design choice, pick the simpler option and tell me in one line.

## Layout
src/config.py     env and model settings
src/llm.py        one function: call(model_cfg, system, user_text, image_path, schema) -> dict, with retries
src/extract.py    Level 1 extraction + extras extraction (usage history, billing history, printed split)
src/checks.py     consistency checks that flag, never rewrite
src/facts.py      derived numbers computed in code for Level 2
src/qa.py         Level 2 answers (one call per bill, all questions at once)
src/run.py        CLI entry, fills both CSVs
tools/            verify_outputs.py and make_zip.py (already written, do not rewrite)
tests/            golden test for KESC_0008
