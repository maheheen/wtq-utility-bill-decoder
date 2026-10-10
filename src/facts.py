"""Derived numbers for Level 2, computed in code so the LLM never does arithmetic."""
import re
from statistics import mean

THRESHOLDS = (100, 150, 200, 250, 300, 400, 500)
_MONTH = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


def _num(x):
    return x if isinstance(x, (int, float)) and not isinstance(x, bool) else None


def _r(x, nd=2):
    return None if x is None else round(x, nd)


def _pct(part, whole):
    return _r(part / whole * 100) if part is not None and whole else None


def _month_units(extras: dict) -> list[tuple[str, float]]:
    rows = {}
    for m in extras.get("usage_history") or []:
        if _MONTH.match(m.get("month") or "") and _num(m.get("units")) is not None:
            rows[m["month"]] = m["units"]
    return sorted(rows.items())


def compute_facts(l1: dict, extras: dict) -> dict:
    f: dict = {}
    cb, tc, tt = _num(l1.get("current_bill")), _num(l1.get("total_charges")), _num(l1.get("total_taxes"))
    units = _num(l1.get("units_consumed"))

    if l1.get("charges"):
        f["charges_sum_as_printed"] = _r(sum(c["amount"] for c in l1["charges"]))
    if l1.get("taxes"):
        f["taxes_sum_as_printed"] = _r(sum(t["amount"] for t in l1["taxes"]))

    both = tc + tt if tc is not None and tt is not None else None
    f["energy_share_pct_of_charges_plus_taxes"] = _pct(tc, both)
    f["tax_share_pct_of_charges_plus_taxes"] = _pct(tt, both)
    f["charges_pct_of_current_bill"] = _pct(tc, cb)
    f["tax_pct_of_current_bill"] = _pct(tt, cb)
    f["cost_per_unit_current_bill_over_units"] = _r(cb / units) if cb is not None and units and units > 0 else None

    within, after = _num(l1.get("payable_within_due_date")), _num(l1.get("payable_after_due_date"))
    if within is not None and after is not None and within > 0:
        f["late_surcharge_amount"] = _r(after - within)
        f["late_surcharge_pct_of_within_due_date"] = _pct(after - within, within)

    cur = l1.get("bill_month")
    usage = _month_units(extras)
    prev = [(m, u) for m, u in usage if m != cur]
    f["previous_months_in_history"] = len(prev)
    if prev:
        avg = mean(u for _, u in prev)
        f["previous_months_average_units"] = _r(avg)
        hi, lo = max(prev, key=lambda x: x[1]), min(prev, key=lambda x: x[1])
        f["highest_previous_month"] = {"month": hi[0], "units": hi[1]}
        f["lowest_previous_month"] = {"month": lo[0], "units": lo[1]}
        if units is not None:
            f["current_minus_average_units"] = _r(units - avg)
            f["current_vs_average_pct"] = _pct(units - avg, avg) if avg > 0 else None
            allm = prev + [(cur or "current", units)]
            hi, lo = max(allm, key=lambda x: x[1]), min(allm, key=lambda x: x[1])
            f["highest_month_including_current"] = {"month": hi[0], "units": hi[1]}
            f["lowest_month_including_current"] = {"month": lo[0], "units": lo[1]}
        earlier = [(m, u) for m, u in prev if cur is None or m < cur]
        if earlier and units is not None:
            lm, lu = earlier[-1]
            f["last_month"] = {"month": lm, "units": lu}
            f["change_vs_last_month_units"] = _r(units - lu)
            f["change_vs_last_month_pct"] = _pct(units - lu, lu) if lu > 0 else None
        f["months_above_threshold"] = {
            str(t): {
                "previous_months": [{"month": m, "units": u} for m, u in prev if u > t],
                "count_previous": sum(1 for _, u in prev if u > t),
                "current_month_exceeds": None if units is None else units > t,
            }
            for t in THRESHOLDS
        }

    pay = [p for p in extras.get("payment_history") or [] if _MONTH.match(p.get("month") or "")]
    both_pay = [p for p in pay if _num(p.get("billed")) is not None and _num(p.get("paid")) is not None]
    if pay:
        f["payment_history_summary"] = {
            "months_listed": len(pay),
            "months_with_no_payment_shown": [p["month"] for p in pay if _num(p.get("paid")) is None],
            # payments print in whole rupees, so gaps under 1 are rounding
            "months_paid_less_than_billed": [p["month"] for p in both_pay if p["paid"] < p["billed"] - 1],
            "total_billed_where_payment_shown": _r(sum(p["billed"] for p in both_pay)),
            "total_paid_where_payment_shown": _r(sum(p["paid"] for p in both_pay)),
        }

    slabs = []
    for s in extras.get("slab_lines") or []:
        u, r, a = _num(s.get("units")), _num(s.get("rate")), _num(s.get("amount"))
        slabs.append({
            "label": s.get("label"), "units": u, "rate": r, "printed_amount": a,
            "units_times_rate": _r(u * r) if u is not None and r is not None else None,
            "pct_of_total_charges": _pct(a, tc),
        })
    if slabs:
        f["slab_lines"] = slabs

    f["printed_split_pct"] = extras.get("printed_split")
    return f
