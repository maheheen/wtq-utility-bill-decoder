# STATUS (update after every milestone, max 10 lines. This is the handoff file between tools.)

Current model in .env: google / gemini-3.5-flash-lite, temperature 0 works fine (change if bake-off says so)
Tool in use now: Claude Code
Last updated: M4 + M5 done, dry run on fake templates OK

## Milestones
- [x] M0 setup  - [x] M1 llm.py + config.py (google only wired, cache in .cache/)
- [x] M2 extract.py Level 1, golden test passes on KESC_0008, tariff copied char by char
- [ ] M3 checks.py + rerun consistency (no re-read logic yet, two runs identical not yet tested uncached)
- [x] M4 extract_extras + facts.py + qa.py (one call per bill, retry missing answers once, then honest fallback)
- [x] M5 run.py: python -m src.run --bills ../data/train/bills --level1 T1 --level2 T2 --out OUT; verify passes except row count (5 bills, not 10)
- [ ] M6 README, requirements pinned, Python 3.12 vs venv 3.14 decision  - [ ] M7 test run at 12:30, rerun diff, zip, upload
Known issues: venv is Python 3.14.3 (rule says 3.12). Fake templates: python tools/make_fake_templates.py (-> ../output/fake).
Next: read the real 12 questions at 12:30, add any missing facts; M3 checks.
