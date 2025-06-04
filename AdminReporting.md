# Program Admin Reporting Specification for Government Reimbursement

## Overview

This document describes the reporting responsibilities and data structure required for program administrators to generate reimbursement reports for government agencies. These reports document verified student work and the corresponding credits earned, serving as a basis for funding or reimbursement.

---

## Objectives

- Provide an accurate, verifiable summary of student service hours.
- Break down session data by student, task type, and duration.
- Align with transparency and compliance requirements for public funding.
- Ensure that all data in reports is backed by blockchain-verified records.

---

## Reporting Phase Scope

This specification covers the **generation and preparation** of reports. It does **not** yet include integration or direct submission to any government agency systems.

---

## Report Types

### 1. Summary Report (By Time Period)
Used for high-level funding justification.

#### Fields:
- Reporting period (e.g., Month/Quarter)
- Total students who participated
- Total seniors served
- Total verified hours
- Total credit amount issued
- Average session length
- Total funding amount requested

---

### 2. Student Service Breakdown
Detailed log of each student's activity.

#### Fields:
- Student ID (anonymized or hashed)
- Student name (optional, depending on agency)
- Number of verified sessions
- Total verified hours
- Credit earned ($)
- Task categories (counts per type)
- Date range of activity

---

### 3. Session-Level Detail Report
Comprehensive, line-by-line report of all sessions during the period.

#### Fields:
- Session ID
- Student ID (hashed)
- Senior ID (hashed)
- Task type
- Date
- Start time / End time
- Duration (minutes)
- Location (zip code or district)
- Rating summary
- Credit value assigned
- Blockchain transaction ID (for audit traceability)

---

## Report Formats

- CSV (for tabular data exchange)
- PDF (for signed, human-readable summary)
- JSON (for possible future integrations)
- Exported files are timestamped and stored for audit compliance

---

## Data Sources

- Internal credit ledger
- Blockchain-verified session logs
- User metadata (anonymized where required)
- Admin adjustments log (for overrides or credit corrections)

---

## Generation Process

1. Admin selects reporting period (e.g., April 1 – April 30).
2. System pulls all blockchain-verified sessions in that window.
3. Applies credit conversion rules.
4. Groups data by report type (summary, student, session).
5. Report preview available for admin review.
6. Admin exports to desired format (CSV, PDF).
7. Reports are archived and optionally signed.

---

## Audit & Verification Tools

- Each session in the report links to a unique blockchain transaction ID.
- Admin can export blockchain logs in raw format for verification.
- Built-in flags for:
  - Suspicious durations
  - Incomplete check-ins
  - Manually adjusted credits

---

## Future Enhancements

- Custom report templates per agency
- Scheduled automatic report generation
- Secure report delivery to agency portals
- Compliance flags per jurisdiction (e.g., HIPAA, FERPA, regional audit standards)

---

## Security & Access

- Reports accessible only to verified admin users
- Exported reports are stored in secure, tamper-evident storage
- All report generation actions are logged for audit trails

