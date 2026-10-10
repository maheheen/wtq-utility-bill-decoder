"""CLI: python -m src.run --bills DIR --level1 TEMPLATE --level2 TEMPLATE --out DIR
Fills both CSV templates, one bill at a time. Never leaves an empty cell."""
import argparse
import csv
import json
import logging
import sys
from collections import defaultdict
from pathlib import Path

from src.config import load_config
from src.extract import Level1, extract_extras, extract_l1
from src.facts import compute_facts
from src.qa import answer_bill

log = logging.getLogger("run")
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
FAIL_ANSWER = "I could not read this bill reliably, so I cannot answer this question from it."
EMPTY_EXTRAS = {"usage_history": [], "payment_history": [], "printed_split": {"energy_pct": None, "taxes_pct": None},
                "slab_lines": [], "late_payment": [], "notes": []}


def null_l1() -> dict:
    d = {k: None for k in Level1.model_fields}
    d["charges"], d["taxes"] = [], []
    return d


def read_csv(path: Path) -> tuple[list[str], list[dict]]:
    with open(path, newline="", encoding="utf-8-sig") as f:
        r = csv.DictReader(f)
        return list(r.fieldnames), list(r)


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def find_image(bills: Path, bill_id: str) -> Path | None:
    for p in sorted(bills.iterdir()):
        if p.stem == bill_id and p.suffix.lower() in IMAGE_EXTS:
            return p
    return None


def process_bill(cfg, image: Path | None, questions: list[tuple[str, str]]) -> tuple[dict, dict]:
    l1 = None
    if image is not None:
        try:
            l1 = extract_l1(image, cfg)
        except Exception as e:
            log.warning("level 1 failed for %s: %s: %s", image.name, type(e).__name__, str(e)[:200])
    if l1 is None:
        return null_l1(), {qid: FAIL_ANSWER for qid, _ in questions}
    try:
        extras = extract_extras(image, cfg)
    except Exception as e:
        log.warning("extras failed for %s: %s: %s", image.name, type(e).__name__, str(e)[:200])
        extras = EMPTY_EXTRAS
    return l1, answer_bill(cfg, l1, extras, compute_facts(l1, extras), questions)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bills", default="../data/test/bills", help="folder of bill images")
    ap.add_argument("--level1", default="../data/test/csv/level1.csv", help="level1 template")
    ap.add_argument("--level2", default="../data/test/csv/level2.csv", help="level2 template")
    ap.add_argument("--out", default="../output", help="output folder for level1.csv and level2.csv")
    a = ap.parse_args(argv)
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s", stream=sys.stderr)
    log.setLevel(logging.INFO)

    cfg = load_config()
    bills = Path(a.bills)
    f1, rows1 = read_csv(Path(a.level1))
    f2, rows2 = read_csv(Path(a.level2))
    qs = defaultdict(list)
    for r in rows2:
        qs[r["bill_id"]].append((r["question_id"], r["question"]))

    results = {}
    for r in rows1:
        bid = r["bill_id"]
        if bid in results:
            continue
        image = find_image(bills, bid)
        if image is None:
            log.warning("no image for %s in %s", bid, bills)
        results[bid] = process_bill(cfg, image, qs.get(bid, []))
        log.info("done %s", bid)

    for r in rows1:
        r["json"] = json.dumps(results[r["bill_id"]][0], sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    for r in rows2:
        bid = r["bill_id"]
        r["answer"] = (results.get(bid, (None, {}))[1].get(r["question_id"]) or FAIL_ANSWER)
    out = Path(a.out)
    write_csv(out / "level1.csv", f1, rows1)
    write_csv(out / "level2.csv", f2, rows2)
    log.info("wrote %s and %s", out / "level1.csv", out / "level2.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
