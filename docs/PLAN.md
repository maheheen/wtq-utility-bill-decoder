# PLAN

## Principle
60 of 100 points are accuracy, 10 more are "same answer on rerun". So: correctness and consistency first, UI last (a UI is optional and only if everything else is done).

## Pipeline per bill
1. extract_l1: vision call with strict JSON schema, temperature 0 where supported. Pydantic validates types. Result cached on disk by hash(image + prompt + model).
2. extract_extras: second vision call for things L2 needs but L1 does not hold: monthly usage history (month, units), billing and payment history (month, billed, paid), the printed energy/tax percentage split, slab lines with units and rate, message board text. Cached the same way. Not written to level1.csv.
3. checks: units = current - previous, charges sum vs total_charges, taxes sum vs total_taxes, current_bill vs total_charges + total_taxes (when all exist). On mismatch, ONE re-read of the failing fields with the mismatch described. If still failing, keep the printed reading and log a warning. Code never overwrites a printed value.
4. facts: Python computes derived numbers: tax share %, energy share %, cost per unit (current_bill / units), late surcharge amount and % (after - within), months above any threshold, history average, current vs average, highest and lowest month, change vs last month, per-slab cost lines.
5. qa: one call per bill that answers all 12 questions as JSON {Q1: "...", ...}. Input: the L1 JSON, extras, facts sheet and the questions. Rules from SPEC section "Level 2" go in the system prompt. Missing key or invalid JSON -> retry that bill once, then per-question fallback.
6. writer: fill the templates with the csv library, keep order and original columns. If a bill fails completely, write a valid null-filled JSON and an honest answer like "I could not read this bill reliably", never an empty cell.
7. verify_outputs.py then make_zip.py.

## Model choice
Build with one provider switch in .env. Bake-off on the 5 train bills (golden check on KESC_0008, eyeball the other four against the image), run each candidate twice and diff.
- Start with gemini-3.5-flash-lite (free tier, 15 req/min, 500/day, plenty for 10 bills).
- If it misses tilted or Urdu bills, switch to gpt-4.1-mini or claude-haiku-4-5 by changing two env vars.
- Free tier rate limit: use a small worker pool (max 3) plus retry with backoff.
- Only one model is stated at submission, so finish on one.

## AI design story (write this in README, judges read it)
Two-stage pipeline: vision extraction into a constrained schema, then reasoning over validated structured data. Arithmetic is done in code, not by the LLM. Checks catch misreads without rewriting printed values. Caching and temperature 0 give reproducibility. The model is used for reading and for language, code for everything numeric.

## Timeline (clock from the guide)
10:30 to 10:45  setup: test API call, folders, drop this kit in, look at all 5 bills yourself and fill docs/LAYOUTS.md
10:45 to 11:00  Claude Code plan mode, scaffolding (config, llm, run skeleton, CSV writer)
11:00 to 11:45  Level 1 working on all 5 train bills, golden test passes on KESC_0008
11:45 to 12:15  extras, facts, Level 2, verify script
12:15 to 12:30  README, .env.example, pin requirements, dry run with fake templates built from train bills
12:30 to 12:40  download test data, READ THE 12 QUESTIONS, add any missing facts (10 min max)
12:40 to 12:55  full run, then rerun and diff for consistency
12:55 to 1:15   screen record a run (under 3 min, small file), verify_outputs, make_zip, open the ZIP
1:15 to 1:25    upload. Do not wait for 1:29.
