# Credit Tracking Specification

## Overview

This document outlines the specification for basic credit tracking in the student-senior service application. The credit tracking module is responsible for converting verified service hours into tuition or housing credit and displaying this information transparently to the student.

---

## Objectives

- Track the number of verified hours a student has completed.
- Convert hours into monetary credit using a fixed rate.
- Display earned credits in a clear and accessible format.
- Ensure all tracked hours are backed by blockchain-logged sessions.

---

## Credit Calculation Model

### Formula

#### credit_amount = total_verified_hours * hourly_credit_rate

### Example

- Hourly Rate: $15/hour
- Verified Hours: 22.5
- Earned Credit: 22.5 * $15 = $337.50

---

## Data Sources

- **Blockchain Logs**: Immutable records of verified sessions.
- **Internal Ledger**: Mirrors blockchain records for efficient UI rendering and credit summary.

---

## Student Dashboard Display

The credit tracking information shown to the student will include:

### Summary Card

| Field                 | Description                             |
|-----------------------|-----------------------------------------|
| Total Verified Hours  | Number of hours logged via blockchain   |
| Hourly Credit Rate    | Admin-defined rate (e.g., $15/hour)     |
| Total Earned Credit   | Current credit total based on hours     |
| Pending Credit Hours  | Sessions awaiting verification           |
| Next Payout Date      | Optional (if payouts are scheduled)     |

### Session Breakdown Table

| Date       | Duration (min) | Task Type     | Verified | Credit Earned |
|------------|----------------|---------------|----------|----------------|
| 2025-06-01 | 90             | Companionship | Yes      | $22.50         |
| 2025-06-03 | 120            | Errands       | Yes      | $30.00         |

---

## Admin Configuration Options

- Hourly credit rate per region or user group
- Maximum weekly/monthly credit caps
- Institution-specific credit routing (e.g., tuition vs. housing)

---

## Data Validation Rules

- Only sessions confirmed by both student and senior
- Must be recorded on the blockchain
- Must pass location/time integrity checks
- Admins can manually override or approve borderline sessions

---

## Future Enhancements

- Allow credit splitting between tuition and housing
- Implement reward badges or tiered incentives
- Enable export to PDF or integration with university billing systems

---

## API Endpoints (Simplified)

- `GET /api/credits/:student_id`
  - Returns total verified hours, credit earned, session list

- `POST /api/credits/sync`
  - Fetches new session logs from blockchain and updates ledger

- `PUT /api/credits/admin-adjust`
  - Admin manually adjusts credit balance (with reason)

---

## Dependencies

- Blockchain Logging Service
- User Identity Verification
- Session Validation Engine
- Admin Dashboard (for override capabilities)

