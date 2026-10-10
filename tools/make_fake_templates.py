"""Build fake level1/level2 templates from a folder of bills, for dry runs.
Usage: python tools/make_fake_templates.py [--bills ../data/train/bills] [--out ../output/fake]"""
import argparse
import csv
from pathlib import Path

QUESTIONS = [
    "How many units did I use this month, and how does that compare with my average of the previous months on the bill?",
    "How much of my current bill is taxes and duties, in rupees and as a percentage?",
    "What percentage of my current bill is energy charges?",
    "What is my effective cost per unit this month?",
    "How much more would I pay if I pay after the due date, and what is that as a percentage?",
    "How many of the previous months were above 200 units?",
    "Which month had the highest usage and which had the lowest in the history shown?",
    "How did this month's usage change compared with last month?",
    "List each charge on this bill with its amount.",
    "Are there any arrears or credits carried forward, and what do they mean?",
    "How much did I pay in recent months compared with what was billed?",
    "Is anything needed to understand this bill missing or unreadable on it?",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bills", default="../data/train/bills")
    ap.add_argument("--out", default="../output/fake")
    a = ap.parse_args()
    ids = sorted({p.stem for p in Path(a.bills).iterdir() if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}})
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "template_level1.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["bill_id", "json"])
        w.writerows([b, ""] for b in ids)
    with open(out / "template_level2.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["bill_id", "question_id", "question", "answer"])
        w.writerows([b, f"Q{i}", q, ""] for b in ids for i, q in enumerate(QUESTIONS, 1))
    print(f"{len(ids)} bills, {len(ids) * len(QUESTIONS)} level2 rows -> {out}")


if __name__ == "__main__":
    main()
