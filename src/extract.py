"""Level 1 extraction: one vision call per bill, validated against a strict schema. Never corrects printed values."""
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from src import llm
from src.config import ModelCfg

ChargeType = Literal["energy", "fixed", "fpa", "quarterly_adjustment", "surcharge", "meter_rent", "subsidy", "other"]
TaxType = Literal["gst", "electricity_duty", "income_tax", "municipal_tax", "other_tax"]


class Charge(BaseModel):
    type: ChargeType
    amount: float


class Tax(BaseModel):
    type: TaxType
    amount: float


class Level1(BaseModel):
    provider: Literal["KE", "LESCO", "IESCO"] | None
    tariff: str | None
    sanctioned_load_kw: float | None
    bill_month: str | None
    reading_date: str | None
    issue_date: str | None
    due_date: str | None
    previous_reading: float | None
    current_reading: float | None
    units_consumed: float | None
    charges: list[Charge]
    total_charges: float | None
    taxes: list[Tax]
    total_taxes: float | None
    current_bill: float | None
    arrears: float | None
    payable_within_due_date: float | None
    payable_after_due_date: float | None


SYSTEM = """You read one Pakistani electricity bill image (K-Electric, LESCO or IESCO) and return a JSON object that matches the schema. The bill may be a scan, screenshot or tilted photo, and may be partly in Urdu.

GENERAL RULES
- Every field is always present. Use null for anything that is not printed, is blank, is under a grey box, or is unreadable. Never guess. A correct null is a correct answer.
- Extract values AS PRINTED. Never recalculate, round, correct or reconcile any amount.
- Money and readings are JSON numbers without commas or currency: "Rs. 19,964" -> 19964.
- A "CR" suffix or a minus sign means negative: "38209CR" -> -38209.
- Dates: "22nd Sep 2026", "22-Sep-26" or "22 SEP 26" -> "2026-09-22". bill_month is "YYYY-MM": "MAR 2026" or "Mar-26" -> "2026-03".
- Output no personal identifiers (the schema has none): no names, addresses, CNIC, account, reference, consumer or meter numbers.
- Never take any field from a usage history, bill history or billing and payment history table. Those are only for past months.

FIELDS
- provider: "KE" for K-Electric, "LESCO", "IESCO".
- tariff: the value next to the label "Tariff" exactly as printed (A1-R, A-1a(01)). Not "Tariff Category" (Domestic, Commercial).
- sanctioned_load_kw: label Sanc Load, S.Load, San Load.
- reading_date, issue_date, due_date: by their labels. due_date is the last date to pay without late payment surcharge, not a later "upto" or "till" date in the late-payment columns.
- previous_reading, current_reading, units_consumed: the meter reading table of this month. units_consumed is the units billed this month as printed. If several meter rows exist (net metering), units_consumed is the printed "Current Month N units" figure when one exists, otherwise use the first meter row for previous reading, current reading and units.
- charges: one entry per line in the charges section, in print order. Skip lines that are blank or printed as 0. Keep separate entries when the same type repeats.
- total_charges: the printed charges subtotal, null if none is printed.
- taxes: one entry per line in the tax or government section. Classify by SECTION, not by line name. If only one combined tax amount is printed with no breakdown (typical LESCO, IESCO), taxes is [] and that amount goes in total_taxes.
- total_taxes: the printed taxes subtotal, null if none is printed.
- current_bill: the printed amount for the current month.
- arrears: previous dues carried forward ("Arrears", "Previous Dues"), keeping the printed sign. null if blank.
- payable_within_due_date: amount payable by the due date as printed (may be negative or 0).
- payable_after_due_date: if several late amounts are printed, use the highest. If the bill prints text such as "NOT TO BE PAID" instead of a number, null.

CHARGE TYPES
energy: cost of units (Variable Upto ... Units, Cost of Electricity, Energy Charges, Total Electricity Charges)
fixed: fixed charges
fpa: fuel price adjustment, use for both FPA and FCA (also IESCO "Total FPA" when not zero)
quarterly_adjustment: QTA, Uniform Quarterly Adjustment
surcharge: Additional Surcharge (PHL), F.C Surcharge
meter_rent: meter rent or service rent
subsidy: government subsidy or relief, always NEGATIVE even if printed without a minus sign
other: any other charge line

TAX TYPES
gst: sales tax or GST, including GST on FPA
electricity_duty: ED
income_tax: income tax
municipal_tax: municipal or local charges printed under taxes, such as MUCT (KMC)
other_tax: extra tax, further tax, TV fee and similar

LAYOUT RULES
- LESCO and IESCO: "Total Electricity Charges" is an energy charge, "Subsidies" is a subsidy (negative). "Net Electricity Charges" is the printed subtotal, so it goes in total_charges and is NOT a charge entry.
- K-Electric: current_bill is the dark bar "Electricity Charges for current month" (charges plus taxes), not the "Electricity Charges" subtotal bar. The subtotal bar "Electricity Charges" is total_charges and "Taxes and Duties" is total_taxes.
- Never include as charges or taxes: opening balance, payments/adjustment, previous or remaining dues, outstanding balance, net metering benefit, late payment surcharge (5%) and (10%) lines, LP SURCHARGE columns, grand total.
"""

USER = "Extract the Level 1 JSON for this bill."


def _clean(value):
    """Whole floats become ints, keys are sorted, so reruns serialise identically."""
    if isinstance(value, dict):
        return {k: _clean(value[k]) for k in sorted(value)}
    if isinstance(value, list):
        return [_clean(v) for v in value]
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def extract_l1(image_path: str | Path, cfg: ModelCfg) -> dict:
    raw = llm.call(cfg, SYSTEM, USER, image_path, Level1.model_json_schema())
    return _clean(Level1.model_validate(raw).model_dump())
