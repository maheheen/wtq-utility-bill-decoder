# SPEC (condensed from the WTQ Participant Guide)

Input: bill image (K-Electric, LESCO or IESCO). Scanned, screenshot or photo. Some are tilted or partly Urdu. Names, addresses and IDs are covered by grey boxes.
Schedule: 10:30 train bills (5, no answers). 12:30 test bills (10) plus level1.csv and level2.csv templates. ZIP upload by 1:30 PM. ONE submission only.

## Level 1 JSON (every field always present, null when unavailable)
{
 "provider": "KE | LESCO | IESCO",
 "tariff": "string as printed",
 "sanctioned_load_kw": number,
 "bill_month": "YYYY-MM",
 "reading_date": "YYYY-MM-DD",
 "issue_date": "YYYY-MM-DD",
 "due_date": "YYYY-MM-DD",
 "previous_reading": number,
 "current_reading": number,
 "units_consumed": number,
 "charges": [{"type": "energy|fixed|fpa|quarterly_adjustment|surcharge|meter_rent|subsidy|other", "amount": number}],
 "total_charges": number,
 "taxes": [{"type": "gst|electricity_duty|income_tax|municipal_tax|other_tax", "amount": number}],
 "total_taxes": number,
 "current_bill": number,
 "arrears": number,
 "payable_within_due_date": number,
 "payable_after_due_date": number
}

## Extraction rules
- Extract as printed. Do not recalculate, round or correct amounts.
- Numbers in PKR as JSON numbers. "Rs. 19,964" -> 19964. No quoted numbers.
- Credits and subsidies are negative. "38209CR" -> -38209.
- Dates: "22nd Sep 2026" -> 2026-09-22. "MAR 2026" -> 2026-03.
- null for anything not printed, blank, under a grey box or unreadable. A correct null scores as correct. Never guess. Empty list is [].
- No personal identifiers.
- K-Electric file names say KESC, but provider value is "KE".

## Field notes
- tariff: exactly as printed (A1-R, A-1a(01)).
- sanctioned_load_kw: label Sanc Load, S.Load or San Load.
- due_date: last date to pay without late payment surcharge.
- units_consumed: units billed this month, as printed.
- charges: one entry per line in the charges section. Skip blank lines and lines printed as 0. Keep separate entries when the same type repeats.
- total_charges / total_taxes: printed subtotal, null if no subtotal is printed.
- taxes: one entry per line in the tax or government section. Classify by SECTION, not by name. If only a combined tax amount is printed, taxes = [] and put the amount in total_taxes.
- arrears: previous dues carried forward, keep printed sign, null if blank.
- payable_after_due_date: if several late amounts are shown, use the highest.

## Charge types
energy: cost of units (Variable Upto ... Units, Cost of Electricity, Energy Charges)
fixed: fixed charges
fpa: fuel price adjustment, use for both FPA and FCA
quarterly_adjustment: QTA, Uniform Quarterly Adjustment
surcharge: Additional Surcharge (PHL), F.C Surcharge
meter_rent: meter rent or service rent
subsidy: government subsidy or relief, NEGATIVE amount
other: any other charge line

## Tax types
gst: sales tax or GST, including GST on FPA
electricity_duty: ED
income_tax: income tax
municipal_tax: municipal or local charges printed under taxes, such as KE MUCT (KMC)
other_tax: extra tax, further tax, TV fee, etc.

## Golden example: KESC_0008 (see tests/golden/KESC_0008.json)
Bill has two energy lines, previous dues are a credit so arrears is -0.53, and the highest late amount (3716) is used.

## Level 2
- 12 questions (Q1 to Q12), same for every bill. 10 test bills -> 120 rows.
- Answer in plain English using only information on the bill. Always English even when the bill has Urdu.
- Numbers must be right (averages, differences, counts, percentages, estimates). Use code for calculations.
- Do not use outside tariff or rate information. If the bill does not show a needed value, say so.
- Label estimates and say how they were calculated.
- If a question is ambiguous, state the meaning used or answer both.
- No personal identifiers.
- Style of a good answer: "Taxes and duties total PKR 569.62 out of your current bill of PKR 3,430.24, or about 16.6%. The bill shows a split of 83.39% energy charges and 16.61% taxes. The tax lines are sales tax (PKR 520.21), electricity duty (PKR 29.41), and MUCT (KMC) (PKR 20.00)."
- Another: "Two of the 12 previous months exceeded 200 units: July 2025 (239) and August 2025 (203). The current month used 151 units, so the count is two whether or not the current month is included."

## CSV rules
- Keep column names and row order. Do not add or remove rows. Do not change bill_id, question_id, question.
- UTF-8. Use the csv library for quoting.
- level1.csv columns: bill_id, json (JSON on ONE line, quotes doubled by the csv library). 10 rows.
- level2.csv columns: bill_id, question_id, question, answer. 120 rows.
- No empty json or answer cells.
- bill_id is the image filename without extension (KESC_0002 = bills/KESC_0002.png).

## ZIP (max 15 MB, upload once)
output/level1.csv, output/level2.csv
source/README.md, source/.env.example, source/requirements.txt (or package.json + lock), all code
demo/demo.mp4 (optional, max 3 min, up to +5 points)
README: setup steps, exact run command on a folder of bills, Python version, AI usage section (models, APIs, services, AI coding tools; write "none" where unused). List must match the code.
.env.example uses real non-secret values for MODEL_PROVIDER and MODEL_NAME, placeholder for API_KEY. No real keys or .env in the ZIP.

## Scoring (100 + 5)
Level 1 extraction 30 (text and dates exact, numbers within +-1, missing required fields and invented values lose points)
Level 2 answers 30 (LLM judge: correct, specific, grounded, honest about missing info)
Engineering quality 15 (clean code, graceful error handling)
AI design 15 (thoughtful reliable use of AI, model used where it adds most value)
Completeness and reproducibility 10 (works end to end, easy to set up and run)
Demo video bonus 5
