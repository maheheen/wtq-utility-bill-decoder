"""Sanity-check the two output CSVs before zipping. Usage: python tools/verify_outputs.py [--l1 P] [--l2 P] [--t1 P] [--t2 P]"""
import argparse, csv, json, sys

KEYS = ["provider","tariff","sanctioned_load_kw","bill_month","reading_date","issue_date","due_date",
        "previous_reading","current_reading","units_consumed","charges","total_charges","taxes",
        "total_taxes","current_bill","arrears","payable_within_due_date","payable_after_due_date"]
NUM = ["sanctioned_load_kw","previous_reading","current_reading","units_consumed","total_charges",
       "total_taxes","current_bill","arrears","payable_within_due_date","payable_after_due_date"]
CHARGE = {"energy","fixed","fpa","quarterly_adjustment","surcharge","meter_rent","subsidy","other"}
TAX = {"gst","electricity_duty","income_tax","municipal_tax","other_tax"}

def read(p):
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def isnum(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--l1", default="../output/level1.csv")
    ap.add_argument("--l2", default="../output/level2.csv")
    ap.add_argument("--t1", default="../data/test/csv/level1.csv")
    ap.add_argument("--t2", default="../data/test/csv/level2.csv")
    a = ap.parse_args()
    errs = []
    l1, l2 = read(a.l1), read(a.l2)
    try:
        t1, t2 = read(a.t1), read(a.t2)
    except FileNotFoundError:
        t1 = t2 = None
        print("note: templates not found, skipping order/row checks against templates")
    if t1 is not None:
        if [r["bill_id"] for r in l1] != [r["bill_id"] for r in t1]:
            errs.append("level1 bill_id order or count differs from template")
        k = lambda rows: [(r["bill_id"], r["question_id"], r["question"]) for r in rows]
        if k(l2) != k(t2):
            errs.append("level2 bill_id/question_id/question differ from template (order, count or text)")
    for r in l1:
        b = r["bill_id"]
        if not r["json"].strip():
            errs.append(f"{b}: empty json"); continue
        if "\n" in r["json"]:
            errs.append(f"{b}: json has line breaks")
        try:
            d = json.loads(r["json"])
        except Exception as e:
            errs.append(f"{b}: invalid json ({e})"); continue
        for k_ in KEYS:
            if k_ not in d: errs.append(f"{b}: missing key {k_}")
        for k_ in NUM:
            if d.get(k_) is not None and not isnum(d[k_]): errs.append(f"{b}: {k_} not a number")
        if d.get("provider") not in {"KE","LESCO","IESCO"}: errs.append(f"{b}: bad provider {d.get('provider')}")
        for c in d.get("charges") or []:
            if c.get("type") not in CHARGE or not isnum(c.get("amount")): errs.append(f"{b}: bad charge {c}")
        for t in d.get("taxes") or []:
            if t.get("type") not in TAX or not isnum(t.get("amount")): errs.append(f"{b}: bad tax {t}")
    for r in l2:
        if not (r["answer"] or "").strip():
            errs.append(f"{r['bill_id']} {r['question_id']}: empty answer")
    print(f"level1 rows: {len(l1)} (expect 10), level2 rows: {len(l2)} (expect 120)")
    if len(l1) != 10 or len(l2) != 120: errs.append("row count wrong")
    if errs:
        print("PROBLEMS:"); [print(" -", e) for e in errs[:60]]; sys.exit(1)
    print("OK")

if __name__ == "__main__":
    main()
