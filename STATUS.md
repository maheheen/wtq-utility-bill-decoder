# STATUS (update after every milestone, max 10 lines. This is the handoff file between tools.)

Current model in .env: google / gemini-3.5-flash-lite, temperature 0 works fine (change if bake-off says so)
Tool in use now: Claude Code
Last updated: UI added (optional), real test run written to ../output

## Milestones
- [x] M0, M1, M2, M4, M5, M6 done. Real test run: ../output/level1.csv + level2.csv, verify_outputs.py says OK (10 / 120 rows)
- [x] UI: python -m src.ui (stdlib http.server + src/ui_page.html, no new deps), tested upload, samples, bad file, dark mode
- [ ] M3 checks.py + uncached two-run consistency test (not built; README makes no claim about re-reads)
- [ ] M7 rerun diff with .cache/ cleared, eyeball test bills vs images, fill README "<other chat ...>" line, make_zip.py, upload once
Known issues: Python 3.14.3 documented; only google provider wired; test-bill answers not yet reviewed by a human.
