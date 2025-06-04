# Payment Allocation and Disbursement Specification

## Overview

This document describes the process that occurs once payments have been received from government agencies. The program must allocate those funds to individual students based on their verified service, apply any administrative commissions if applicable, and then disburse those funds toward students' housing or tuition obligations.

---

## Objectives

- Match incoming payments to verified student service records.
- Apply commission (if applicable) before crediting student accounts.
- Ensure transparency and auditability in credit application.
- Facilitate disbursement to designated housing and education institutions.
- Only show finalized credits to students after successful allocation.

---

## Process Phases

### 1. Receipt of Payment

- Admin marks a payment as received for a specific reporting period (e.g., April 2025).
- Payment is tagged with:
  - Total amount
  - Source (e.g., federal program, state agency)
  - Date received
  - Related report reference (e.g., Report ID)

---

### 2. Allocation to Students

- Payment is distributed proportionally based on verified service hours per student from the corresponding report.
- Allocation formula:
  
#### student_allocation = (student_verified_hours / total_reported_hours) * total_payment_received
---

- Each student’s allocation is recorded as a ledger entry, including:
- Student ID
- Allocated amount
- Related session period
- Report ID
- Blockchain log reference

---

### 3. Commission Deduction (Optional)

- If an admin commission or platform fee is enabled, apply it at this stage.
- Commission can be:
- Flat fee per student
- Percentage of credited amount

- Final credit to student:

#### net_credit = student_allocation - admin_fee

- Deducted commission is logged for transparency.

---

### 4. Final Credit Confirmation

- After allocations and fees:
- Credit is **applied** to student ledger.
- Student receives a notification and sees the amount in their dashboard.

- Status of each entry: `PENDING -> APPLIED -> DISBURSED`

---

### 5. Disbursement to Housing and Tuition

- Students designate in advance how their credit should be applied:
- % to housing
- % to tuition

- Admin or financial integration API initiates disbursement:
- Export disbursement files (or API calls) to university billing systems
- Export disbursement files to partnered housing providers

- Example:
- $300 net credit
- 60% housing ($180) → Sent to housing vendor
- 40% tuition ($120) → Sent to university billing

---

### 6. Audit Logging

All financial events are logged with:
- Student ID
- Original payment ID
- Session report reference
- Amount allocated
- Commission taken
- Disbursement details (date, target, method)

---

## Student Experience

- Student only sees credit **after payment is received and allocated**.
- Dashboard shows:
- Verified hours
- Credit earned (before and after commission)
- Payment source (e.g., “Federal Grant - April 2025”)
- Credit applied to housing/tuition with breakdown
- Option to update future split preferences

---

## Admin Tools

- Dashboard to match incoming payments to reports
- Reallocation or manual adjustment override
- Commission configuration (global or student-level)
- Export-ready disbursement files (CSV, JSON)
- History of all disbursements with status

---

## Future Enhancements

- Real-time API integration with universities and housing providers
- Student-configurable credit routing rules
- Commission invoicing and analytics
- Digital signature receipts for disbursements

