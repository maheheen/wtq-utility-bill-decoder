# STATUS (update after every milestone, max 10 lines. This is the handoff file between tools.)

Current model in .env: google / gemini-3.5-flash-lite, temperature 0 works fine (change if bake-off says so)
Tool in use now: Claude Code
Last updated: M6 done

## Milestones
- [x] M0 setup  - [x] M1 llm.py + config.py  - [x] M2 extract.py Level 1 (golden test passes)  - [x] M4 extras + facts + qa
- [ ] M3 checks.py + uncached rerun consistency test (not built; README no longer claims re-read checks)
- [x] M5 run.py: python -m src.run --bills B --level1 T1 --level2 T2 --out OUT (dry run on ../output/fake OK, verify only fails row count 5 vs 10)
- [x] M6 README (Python 3.14.3, AI usage from real code), requirements pinned to pip freeze, .env.example, .gitignore .env.*
- [ ] M7 test run at 12:30, rerun diff, zip, upload
Known issues: README line "<other chat used for layout notes>" is for the user to fill in before zipping.
Next: read the real 12 questions at 12:30, add missing facts; M3 if time.
