# STATUS (update after every milestone, max 10 lines. This is the handoff file between tools.)

Current model in .env: google / gemini-3.5-flash-lite, temperature 0 works fine (change if bake-off says so)
Tool in use now: Claude Code
Last updated: M2 done

## Milestones
- [x] M0 setup: venv, requirements, .env, test API call works
- [x] M1 llm.py + config.py (google only wired, disk cache in .cache/, openai/anthropic raise NotImplementedError)
- [x] M2 extract.py Level 1 on 5 train bills, golden test passes on KESC_0008
- [ ] M3 checks.py + rerun consistency (two runs identical, cache already done)
- [ ] M4 extras + facts.py + qa.py
- [ ] M5 run.py CLI fills both CSVs, verify_outputs.py passes on fake templates
- [ ] M6 README, .env.example, requirements pinned
- [ ] M7 test run at 12:30, rerun diff, zip, upload

## Known issues
- .venv is Python 3.14.3, rule says 3.12 (not installed). LESCO_0005 tariff came back "A-1b(03)", notes say "A-1b(03)T".
