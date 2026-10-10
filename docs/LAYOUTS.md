Section 8 (extra data) of each bill lives in docs/EXTRAS.md.

# DECISION RULES (apply to every bill)

From the guide (certain):
- Combined tax line with no breakdown (IESCO, LESCO): taxes = [], total_taxes = that amount.
- CR suffix or minus sign means negative. "54770CR" -> -54770.
- Subsidies are negative even if printed without a minus sign.
- Skip charge lines printed as 0 or blank.
- Late-payment amounts: use the highest printed number.
- Hidden or unreadable field -> null. Never guess.

My calls (judgment, best guess):
- IESCO and LESCO charges: "Total Electricity Charges" -> energy; "Subsidies" -> subsidy (negative); "Net Electricity Charges" is the printed subtotal, so it goes in total_charges and NOT as a charge entry. IESCO "Total FPA" (non-zero) -> fpa.
- KE: current_bill is the "Electricity Charges for current month" total (charges plus taxes), not the "Electricity Charges" subtotal.
- Not charges, never include: opening balance, payments/adjustment, previous or remaining dues, outstanding balance, net metering benefit, late payment surcharge (5%) and (10%) lines.
- Payable after due date printed as text like "NOT TO BE PAID" with no number -> null.
- Several meter rows (net metering bills): units_consumed = the printed "Current Month N units" figure if one exists; otherwise use the first meter row for previous reading, current reading and units.
- Never take Level 1 values from the usage history or bill history tables.

Checks rule: subtotal sums only hold on K-Electric style layouts. On IESCO and LESCO a mismatch is expected. Checks must log a warning and retry at most once, never loop, never override the printed value.

# LAYOUTS.md

Layout notes for 5 sample Pakistani electricity bills. Values are as printed. Identity fields (name, address, CNIC, account, reference, consumer, meter numbers) are deliberately omitted. "unreadable" means the value could not be read from the image. Blank-printed lines are listed as "skip".

Section key per bill: 1 field locations, 2 charges and taxes lines, 3 printed subtotals, 4 traps, 5 hidden fields, 6 Urdu labels, 7 hard-to-read areas, 8 extra data.

---

## IESCO_0004

Islamabad Electric Supply Company. Single page, flat screenshot, clear. Bill month SEP 26.

### 1. Field locations
- Tariff: CONSUMER DETAIL block, bottom-right cell, label "TARIFF" -> A-1A(01)
- Cell left of it, label "TARIFF CATEGORY" -> Domestic (not the tariff code)
- Sanctioned load: CONSUMER DETAIL, top-right cell, label "SAN LOAD" -> 3
- Cell below it, label "CURR MDI" -> blank
- Billing month: right panel, top, label "BILL MONTH" -> SEP 26
- Reading date: right panel, label "READING DATE" -> 25 SEP 26
- Issue date: right panel, beside reading date, label "ISSUE DATE" -> 26 SEP 26
- Due date: right panel, below, label "DUE DATE" -> 08 OCT 26
- Previous reading: METER INFO strip, label "PREVIOUS READING" -> 9301
- Current reading: METER INFO strip, label "PRESENT READING" -> 9459
- Units consumed: METER INFO strip, label "UNITS" -> 158
- MF -> 1
- One meter row only

### 2. Charges and taxes lines
Section: BILL CHARGES BREAKDOWN (RS.), left column then right column.

Charges lines (left column, in print order):
- Total Electricity Charges: 6102
- Subsidies: 3332 (printed positive, no minus sign)
- Net Electricity Charges 84.76 %: 2770

Taxes lines:
- Taxes 15.24 %: 498 (single combined line, no breakdown)

Other left-column line:
- Current Bill: 3267

Right column lines:
- Arrears: 0 (skip)
- Installment: 0 (skip)
- Adjustments: 0 (skip)
- W.E Credit: 0 (skip)
- Lock Open Credit: 0 (skip)
- Total FPA: 267 (non-zero)

Grand Total (bottom, left): 3535

### 3. Printed subtotals
- Charges subtotal: Net Electricity Charges 2770 (Total Electricity Charges 6102 is before subsidy)
- Taxes subtotal: 498
- Current Bill: 3267
- Arrears: 0, no CR marking
- Total FPA: 267
- Grand Total: 3535
- Payable within due date: 3535 (right panel, label "PAYABLE WITHIN DUE DATE")
- LP SURCHARGE: 139 (Till 12-OCT-26 column), 277 (After 12-OCT-26 column)
- Payable after due date: Till 12-OCT-26 -> 3,674; After 12-OCT-26 -> 3,812
- Highest late amount: 3,812
- Arithmetic as printed: 6102 - 3332 = 2770; 2770 + 498 = 3268 vs printed 3267; 3267 + 267 = 3534 vs printed 3535 (1-rupee gaps)

### 4. Traps
- Subsidies 3332 printed without minus, sits between Total and Net lines; reduces charges (must be negative)
- Total Electricity Charges 6102 is gross, not the bill amount
- Taxes: one combined amount (498), no GST/duty split
- Total FPA 267 sits in right column among zero lines; not included in Current Bill sum; included in Grand Total
- Zero lines to skip: Arrears, Installment, Adjustments, W.E Credit, Lock Open Credit
- Late "Till" date (12-OCT-26) differs from Due Date (08 OCT 26)
- Printed twice: bill month, due date, payable within due date 3535, payable after due date 3,674 / 3,812 (right panel and bottom stub)
- 3332 printed again in the cream note box (as subsidy)
- 267 printed again in the cream note box (as FPA)

### 5. Hidden by grey box
- None of the nine target fields hidden
- Grey boxes cover: top-right header block (below the 1Link-1Bill line), QR area in right panel, small box right of the cream note, box at top-right of the bottom stub
- Name & Address cell shows no readable value
- Blank, not grey: Status, Curr MDI, Deferred Amount, Outstanding Install.

### 6. Urdu labels
- مقررہ تاریخ = due date
- مقررہ تاریخ تک واجب الادا = payable within due date
- مقررہ تاریخ کے بعد واجب الادا = payable after due date
- Urdu beside each charge line: small, unreadable
- Yellow box: Urdu + English "TEXT Reference No to 8118 or Call 118" (contact instruction, no amounts)
- Top-right Urdu line: pay via 1Link-1Bill, code 111444 (payment instruction)
- Bottom stub Urdu line: government energy programme promo + https://efan.gov.pk/ (no billing data)

### 7. Hard to read
- Cream note box, 2 Urdu lines, small print; partly legible
- Meter photo (right panel): overlay text unreadable, meter digits unreadable
- Rotated vertical text beside the QR box: unreadable
- Bottom stub, far right small text: unreadable
- Bill History table: small but readable

---

## KESC_0004

K-Electric (KE). Single page, flat, high resolution. Bill month Jun-26. Net-metering style bill with 4 register rows.

### 1. Field locations
- Tariff: top-right "Customer Information" box, label "Tariff" -> A1-R
- Sanctioned load: same box, label "Sanc Load" -> 10 (next line "Conn Load" -> 10)
- Billing month: top-left under logo, "Bill Month: Jun-26"
- Issue date: top-left beside bill month, "Issue Date: 29-Jun-2026"
- Reading date: Bill Calculation panel, first line, "Reading Date: 25-Jun-26" (no other reading-date label)
- Due date: orange box top-right, label "Due Date" -> 13th Jul 2026
- Previous reading: "Electricity You Have Used" table, column "Previous Reading"
- Current reading: same table, column "Current Reading"
- Units consumed: same table, column "Units (KWh)"; also orange box "Current Month 901 units"
- Table rows (Previous / Current / Units / MDI):
  - Energy - Off Peak: 1163.29 / 1923.73 / 760.44 / 4.686
  - Energy - Peak: 402.35 / 542.85 / 140.5 / 3.354
  - Import Energy Off Peak: 10865.55 / 12238.4 / 1372.85 / 9.402
  - Import Energy Peak: 4.97 / 6.53 / 1.56 / 0.794
- Billed units appear in Bill Calculation as Variable Off Peak 760.44 and Variable Peak 140.50; summary box says 901 units

### 2. Charges and taxes lines
Section: "Bill Calculation" panel, right side, columns Units / Rate / Amount.

Charges lines (in print order):
- Fixed Charges: 5 x 675.0000 = 3,375.00
- Variable Off Peak: 760.44 x 34.5300 = 26,257.99
- Variable Peak: 140.50 x 46.8500 = 6,582.43
- Uniform Quarterly Adjustment: 726.57 x -1.9857 = -1,442.74
- Uniform Quarterly Adjustment: 174.37 x 0.3504 = 61.10
- FCA :Apr-26: 297.46 x 1.1907 = 354.19
- Additional Surcharge (PHL): 900.94 x 3.2300 = 2,910.04
- Subtotal bar "Electricity Charges": 38,098.01

Taxes lines:
- Electricity Duty: 520.85
- Sales Tax u/s 3(1)*: 6,951.39
- Subtotal bar "Taxes and Duties": 7,472.24

Zero or blank lines inside Bill Calculation: none

### 3. Printed subtotals
- Charges subtotal: 38,098.01
- Taxes subtotal: 7,472.24
- Current bill: 45,570.25 (dark bar "Electricity Charges for current month"; again "Current Bill Amount"; again orange box "Current Month Rs.45,570.25")
- Net Metering Benefit: -114,640.13 (orange Current Month box and Bill Calculation list)
- Opening Balance: -91,877.02
- Previous Dues: -91,877.02 (negative, minus sign, no CR text; credit)
- Remaining Dues: -91,877.02
- Outstanding Balance: -160,946.90
- Payable within due date: Rs. 0 (orange "Amount Due" box); "Till 13-Jul-2026 Rs.0.00" in Due Date box
- Payable after due date: "Till 14-Jul-26-16-Jul-26 Rs.0" and "After 16-Jul-26 Rs.0" (Due Date box shows Rs.0.00 for the 14-16 Jul window)
- Highest late amount: 0 (all late amounts printed as 0)

### 4. Traps
- "Electricity Charges" appears twice with different meaning: 38,098.01 (grey subtotal, charges only) vs "Electricity Charges for current month" 45,570.25 (charges + taxes)
- "Uniform Quarterly Adjustment" printed twice: first amount negative (-1,442.74, rate -1.9857), second positive (61.10)
- Opening Balance, Previous Dues, Remaining Dues all -91,877.02; not charges
- Previous Dues is negative = credit balance
- Net Metering Benefit -114,640.13 is a credit, not a charge or tax
- Outstanding Balance -160,946.90 is not the amount due
- Amount Due printed as 0 despite 45,570.25 current bill
- 4 register rows with different units; only Variable Off Peak 760.44 and Variable Peak 140.50 are billed in the calculation
- Import Energy rows (1372.85, 1.56) are not billed lines
- Units 900.94 appears as Additional Surcharge units; 901 in summary box
- Bottom stub Due Date column shows "14-Jul-26-16-Jul-26" (late window), not 13-Jul
- Printed twice: current bill (3 places), energy charges and taxes (Bill Calculation and bottom-left icons), late amounts (summary box, stub)

### 5. Hidden by grey box
- None of the nine target fields hidden
- Grey boxes cover: name/address block under bill month; top-centre block (barcode area, "Scan With Banking App" text above it); Contract No value; Invoice No value; Tenant CNIC/NTN/STRN; Consumer No; Meter No; stub fields (Account/Contract/Invoice values, wide bar at stub bottom)
- Security Deposit digits partly covered (reads 2080.00, top of digits covered)
- Customer Type value partly covered ("NM" visible)
- Blank: Dispatch ID, User Name

### 6. Urdu labels
- واجب الادا رقم = amount due
- موجودہ مہینہ = current month
- گزشتہ بقایاجات = previous dues
- مقررہ تاریخ = due date
- مقررہ تاریخ کے بعد واجب الادا رقم = amount payable after due date
- صارف کی معلومات = customer information
- آپ کی استعمال شدہ بجلی = electricity you have used
- آپ کے موجودہ بل کا حساب = your current bill calculation
- بلنگ اور ادائیگی کی تفصیل = billing and payment history
- برائے کرم مقررہ تاریخ تک بل ادا کر کے بچت کریں = please pay by due date and save
- Footer Urdu: same disclaimer as English footer (bill is for recovering electricity charges; name/address is not proof of ownership)

### 7. Hard to read
- 13 Month Usage History: unit numbers rotated 90 degrees inside bars
- Billing & Payment History: small print
- Urdu footer: small
- Footnote "* Sales Tax Act, 1990- ** Income Tax Ordinance, 2001": tiny
- Bottom stub text: small

---

## KESC_0008

K-Electric (KE). Same template as KESC_0004. Single page, flat, high resolution. Bill month Apr-26. Single energy register.

### 1. Field locations
- Tariff: "Customer Information" box top-right, label "Tariff" -> A1-R
- Sanctioned load: same box, label "Sanc Load" -> 3 (next line "Conn Load" -> 3)
- Billing month: top-left, "Bill Month: Apr-26"
- Issue date: top-left, "Issue Date: 07-Apr-2026"
- Reading date: Bill Calculation header line, "Reading Date: 03-Apr-26"
- Due date: orange box top-right, label "Due Date" -> 21st Apr 2026
- Previous reading: "Electricity You Have Used" table, column "Previous Reading" -> 8819
- Current reading: column "Current Reading" -> 8970
- Units consumed: column "Units (KWh)" -> 151; also orange box "Current Month 151 units"
- Only one row: "Energy"; MDI (KW) column blank
- Customer Type in same box: STAR

### 2. Charges and taxes lines
Section: "Bill Calculation" panel, columns Units / Rate / Amount.

Charges lines:
- Fixed Charges: 3.00 x 300.0000 = 900.00
- Variable Upto 100 Units (Protected): 100.00 x 10.5400 = 1,054.00
- Variable Upto 200 Units (Protected): 51.00 x 13.0100 = 663.51
- Uniform Quarterly Adjustment: 151.00 x 0.3504 = 52.91
- FCA :Feb-26: 88 x 1.4235 = 125.27
- Additional Surcharge (PHL): 151.00 x 0.4300 = 64.93
- Subtotal bar "Electricity Charges": 2,860.62

Taxes lines:
- Electricity Duty: 29.41
- Sales Tax u/s 3(1)*: 520.21
- MUCT (KMC): 20.00
- Subtotal bar "Taxes and Duties": 569.62

Zero or blank lines: none

### 3. Printed subtotals
- Charges subtotal: 2,860.62
- Taxes subtotal: 569.62
- Current bill: 3,430.24 (dark bar "Electricity Charges for current month"; "Current Bill Amount"; orange box "Rs.3,430.24")
- Opening Balance: 2,576.47
- Payments/Adjustment: -2,577.00
- Previous Dues: -0.53 (minus sign, no CR text; tiny credit)
- Remaining Dues: -0.53
- Payable within due date: 3,430 (orange box "Rs. 3,430"; "Amount Payable within Due Date 3,430")
- Late Payment Surcharge (5%): 143.03
- Late Payment Surcharge (10%): 286.06
- Payable 22-Apr to 24-Apr with 5% LPS: 3,574
- Payable after 24-Apr-26 with 10% LPS: 3,716
- Highest late amount: 3,716

### 4. Traps
- Opening Balance 2,576.47 is a previous balance, not a charge
- Payments/Adjustment -2,577.00 is a payment, not a charge
- Previous Dues -0.53 is a credit
- Late Payment Surcharge (5%) and (10%) lines look like charges but are conditional late amounts, not part of the current bill
- "Electricity Charges" (2,860.62, charges only) vs "Electricity Charges for current month" (3,430.24, charges + taxes)
- Orange box under Due Date: "Till 21-Apr-2026 Rs.286.06" and "Till 22-Apr - 24-Apr Rs.143.03" equal the LPS lines, not payable amounts
- "PAID" stamp box printed over the header: "Amount: 3430"; payment marker, not a charge
- Printed twice: 3,430 / 3,430.24 current amount (several places); late amounts 3,574 / 3,716 (Bill Calculation, orange box, stub); energy 2,860.62 and taxes 569.62 (Bill Calculation and bottom-left icons)
- Variable lines carry "(Protected)" in the label

### 5. Hidden by grey box
- None of the nine target fields hidden
- Grey boxes cover: name/address block; barcode block top-centre; Contract No; Invoice No; Consumer No; Meter No; stub values (account, contract, invoice)
- PAID stamp: payment ID line hidden, top of stamp partly covered; "Amount: 3430" readable
- Security Deposit partly covered (reads 175.00, top of digits covered)
- Blank: Dispatch ID, User Name, Tenant CNIC/NTN/STRN

### 6. Urdu labels
- Same Urdu headings as KESC_0004:
  - واجب الادا رقم = amount due
  - موجودہ مہینہ = current month
  - گزشتہ بقایاجات = previous dues
  - مقررہ تاریخ = due date
  - مقررہ تاریخ کے بعد واجب الادا رقم = amount payable after due date
  - آپ کی استعمال شدہ بجلی = electricity you have used
  - آپ کے موجودہ بل کا حساب = your current bill calculation
  - بلنگ اور ادائیگی کی تفصیل = billing and payment history
  - برائے کرم مقررہ تاریخ تک بل ادا کر کے بچت کریں = please pay by due date and save

### 7. Hard to read
- 13 Month Usage History: numbers rotated 90 degrees inside bars
- PAID stamp: partly covered by grey boxes
- Billing & Payment History: small
- Urdu footer, footnote: small

---

## LESCO_0005

Lahore Electric Supply Company. Phone photo of printed bill: tilted, perspective skew, uneven lighting. Bill month JUL 2026. "NET METERING CONNECTION" printed under Meter Info. Credit bill.

### 1. Field locations
- Tariff: CONSUMER DETAIL, right cell, label "TARIFF" -> reads A-1b(03)T; characters after "A-" partly unclear; value overlaps the "TARIFF CATEGORY" value
- Tariff Category: label "TARIFF CATEGORY" -> DOMESTIC (printed overlapping the label text)
- Sanctioned load: CONSUMER DETAIL, label "SAN LOAD" -> 10
- MDI: label "MDI" (below SAN LOAD) -> 5
- Billing month: right panel, label "BILL MONTH" -> JUL 2026
- Reading date: right panel, label "READING DATE" -> 17 JUL 26
- Issue date: right panel, beside reading date, label "ISSUE DATE" -> 20 JUL 26
- Due date: right panel, label "DUE DATE" -> 30 JUL 26
- METER INFO block, columns PREVIOUS READING / PRESENT READING / UNITS, MF 1 on every row, 4 rows with no row labels:
  - Row 1: 11561 / 12578 / 1,017
  - Row 2: 3260 / 3562 / 302
  - Row 3: 21822 / 22859 / 1,037
  - Row 4: 5 / 5 / units blank
- Which row is the billed reading: not labelled on the bill

### 2. Charges and taxes lines
Section: BILL CHARGES BREAKDOWN (RS.). Value column is tilted; values sit slightly above their labels.

Charges lines:
- Total Electricity Charges: 17,367.77
- Subsidies: blank (skip)
- Net Electricity Charges: 17,367.77

Taxes lines:
- Taxes: 3,358.23 (single combined line, no breakdown)

Other lines:
- Current Bill: 20726
- Grand Total: 54770CR
- Arrears (right column): -75496
- Installment: blank (skip)
- Adjustments: blank (skip)

### 3. Printed subtotals
- Charges subtotal: Net Electricity Charges 17,367.77
- Taxes subtotal: 3,358.23
- Current Bill: 20726
- Arrears: -75496 (negative; credit)
- Grand Total: 54770CR ("CR" suffix = credit)
- Payable within due date: 54770CR
- LP SURCHARGE: 0 and 0 (columns "Upto 03/08/26" and "After 03/08/26")
- Payable after due date: printed "NOT TO BE PAID"
- Highest late amount: none printed as a number (LP surcharge 0 / 0)

### 4. Traps
- Arrears -75496 is a credit, not a charge
- Grand Total 54770CR is a credit balance, not an amount due; "CR" suffix
- Payable within due date also 54770CR
- Payable after due date has text "NOT TO BE PAID", no number
- Total Electricity Charges and Net Electricity Charges both 17,367.77 (printed twice)
- Taxes: combined 3,358.23, no breakdown
- Subsidies, Installment, Adjustments blank
- Value column misaligned with labels (tilt); 5 values for 6 left-column labels
- Current Bill has no comma (20726); Grand Total has "CR" attached
- 4 meter rows, no labels; row 4 has no units
- Bill history units are negative on most rows (net metering)
- Bill history JUN 26 bill -75,496 matches the Arrears value

### 5. Hidden by grey box
- None of the nine target fields hidden
- Grey boxes cover: top-right of header; Reference No; Consumer ID; Transformer; Feeder; Name & Address; most of Sub Division; QR box in right panel
- Blank, not grey: Category, Status, Installment, Adjustments, Subsidies, Deferred Amount, Outstanding Installments
- Cream box under Grand Total: empty

### 6. Urdu labels
- مقررہ تاریخ = due date
- سابقہ ریڈنگ = previous reading
- موجودہ ریڈنگ = present reading
- یونٹ = units
- کل چارجز = total charges
- رعایت = subsidies
- نیٹ چارجز = net charges
- ٹیکس = taxes (small print)
- موجودہ بل = current bill
- کل واجبات = grand total
- بقایاجات = arrears
- قسط = installment
- تصحیح = adjustment (small print)
- Red header line: report billing error/fault; Power Smart Mobile App, SMS 8118, call 118
- Under QR: scan QR code to see charge details (چارجز کی تفصیل دیکھنے کے لیے QR کوڈ سکین کریں)

### 7. Hard to read
- Whole photo tilted; perspective skew; shadow on left edge
- Bill History header row is overprinted by the first data row (JUL 25 values collide with column headers)
- Meter photos (bottom right): overlay text unreadable; meter display digits unreadable
- Tariff value overlaps Tariff Category value
- Urdu labels: small
- Bill charge values sit above their labels

---

## LESCO_0006

Lahore Electric Supply Company, "ELECTRICITY CONSUMER BILL (GEN)". Phone photo of printed bill: tilted, crumpled paper, glare, purple/blue tint, blurry lower half. Bill month AUG 2026.

### 1. Field locations
- Tariff: CONSUMER DETAIL, right cell, label "TARIFF" -> A-2a(04)
- Tariff Category: label "TARIFF CATEGORY" -> COMMERCIAL (printed overlapping the label)
- Sanctioned load: CONSUMER DETAIL, label "SAN LOAD" -> 1
- MDI: label "MDI" -> 1
- Billing month: right panel, label "BILL MONTH" -> AUG 2026
- Reading date: right panel, label "READING DATE" -> 26 AUG 26
- Issue date: right panel, label "ISSUE DATE" -> 29 AUG 26
- Due date: right panel, label "DUE DATE" -> 09 SEP 26
- Previous reading: METER INFO, label "PREVIOUS READING" -> 22238
- Current reading: METER INFO, label "PRESENT READING" -> 22303
- Units consumed: METER INFO, label "UNITS" -> 65
- MF -> 1
- One meter row only; label "STATUS:" next to meter number is blank

### 2. Charges and taxes lines
Section: BILL CHARGES BREAKDOWN (RS.).

Charges lines:
- Total Electricity Charges: 3,777.49
- Subsidies: blank (skip)
- Net Electricity Charges: 3,777.49

Taxes lines:
- Taxes: 1,723.51 (single combined line, no breakdown)

Other lines:
- Current Bill: 5501
- Grand Total: 44912
- Arrears (right column): printed "39411 / 2" (trailing "/ 2" unclear; read as 39411)
- Installment: blank (skip)
- Adjustments: blank (skip)

### 3. Printed subtotals
- Charges subtotal: Net Electricity Charges 3,777.49
- Taxes subtotal: 1,723.51
- Current Bill: 5501
- Arrears: 39411 (positive, no CR marking; trailing "/ 2" unclear)
- Grand Total: 44912
- Payable within due date: 44912 (right panel)
- LP SURCHARGE: 176 (Upto 14/09/26 column), 351 (After 14/09/26 column)
- Payable after due date: Upto 14/09/26 -> 45088; After 14/09/26 -> 45263
- Highest late amount: 45263

### 4. Traps
- Arrears 39411 is previous unpaid balance, not a charge; included in Grand Total
- Grand Total 44912 includes arrears; Current Bill is 5501
- Payable within due date 44912 repeats Grand Total
- Total Electricity Charges and Net Electricity Charges both 3,777.49 (printed twice)
- Taxes: combined 1,723.51, no breakdown
- LP surcharge values (176, 351) are late-payment amounts, not charges
- Late "Upto" date (14/09/26) differs from Due Date (09 SEP 26)
- Subsidies, Installment, Adjustments blank
- Arrears printed with "/ 2" suffix
- Value column slightly misaligned with labels (tilt)

### 5. Hidden by grey box
- None of the nine target fields hidden
- Grey boxes cover: top-right of header; Reference No; Transformer; Consumer ID; Feeder Code; Name & Address; Sub Division; QR box in right panel; lower-right box above meter photo
- Meter number, STATUS: visible or blank (meter number omitted by rule)
- Blank, not grey: Category, Subsidies, Installment, Adjustments, Deferred Amount, Outstanding Installments

### 6. Urdu labels
- مقررہ تاریخ = due date
- سابقہ ریڈنگ = previous reading
- موجودہ ریڈنگ = present reading
- یونٹ = units
- کل چارجز = total charges
- رعایت = subsidies
- نیٹ چارجز = net charges
- ٹیکس = taxes (small print)
- موجودہ بل = current bill
- کل واجبات = grand total
- بقایاجات = arrears
- قسط = installment
- تصحیح = adjustment (small print)
- Red header line: report billing error/fault; Power Smart Mobile App, SMS 8118, call 118
- Under QR: scan QR code to see charge details

### 7. Hard to read
- Photo tilted, crumpled paper, glare, purple/blue tint
- Lower half (Bill History) blurry
- Meter photo (bottom right): caption overlay and meter digits unreadable
- Arrears value "39411 / 2": trailing part unclear
- Tariff Category value overlaps label text
- Urdu labels small
