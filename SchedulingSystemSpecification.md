# Scheduling System Specification

## Overview

This document describes the scheduling system for the student-senior service platform. The scheduling feature allows both students and senior citizens to input their availability, request sessions, and confirm appointments. It ensures coordination, prevents conflicts, and supports session lifecycle management.

---

## Objectives
- Enable both students and seniors to define their availability.
- Provide a mechanism for either party to request and schedule a session.
- Handle session conflicts, changes, and cancellations.
---

## Core Concepts

### Availability
- Defined as recurring time slots or specific dates/times when a user is free.
- Users can set availability by:
  - Day of week + time range (e.g., Mondays 2–6 PM)
  - Specific date and time (e.g., June 10th, 9–11 AM)

### Session Request
- A proposed time window for a session between one student and one senior.
- Can be initiated by either user.
- Requires mutual confirmation to become scheduled.

### Session Statuses
- Pending: Requested, awaiting confirmation.
- Confirmed: Both parties agreed.
- Completed: Session finished and verified.
- Cancelled: Cancelled before session time.
- Expired: Time passed with no confirmation.

---

## Scheduling Workflow

### 1. Setting Availability

#### Student
- Enters availability during onboarding or via calendar page.
- Can offer general availability or propose specific open time blocks.
- Option to auto-match when slots overlap with senior availability.

#### Senior
- Sets preferred days and times for assistance.
- May request one-off availability for specific needs (e.g., a doctor visit).

---

### 2. Session Request Flow

#### Option 1: Student-Initiated
- Student browses seniors with overlapping time.
- Sends a session proposal (date, time, task type).
- Senior receives notification and can accept or suggest an alternative.

#### Option 2: Senior-Initiated
- Senior browses available students.
- Sends session request for a time matching the student’s availability.
- Student confirms or negotiates.
---
### 3. Conflict Handling

- App prevents users from booking overlapping sessions.
- Users receive real-time feedback if selected times conflict with existing sessions.
- Manual overrides allowed only for admins.

---

### 4. Calendar Management

- Each user has a personal in-app calendar view.
- Confirmed sessions are automatically added.
- Supports reminders via notifications (24hr, 1hr before).
- Time zone support included.

---

### 5. Session Lifecycle Management

- Before session: Both users get reminders.
- Start: Student checks in at location using GPS.
- End: Student checks out; senior confirms.
- Session marked as "Completed" and eligible for credit logging.

---

## Time Format and Constraints

- Time format: ISO 8601 (UTC-based storage, local display).
- Session length: Minimum 30 minutes, max configurable by admin.
- Default buffer time between sessions: 15 minutes (configurable).

---

## Advanced Features (Later Phase)

- Calendar sync with Google, Apple, Outlook
- Smart availability prediction based on past behavior
- Auto-matching engine for students with seniors needing help that week
- Waitlisting for fully booked time slots

---

## API Endpoints (Simplified)

- `POST /api/availability` – Add or update availability
- `GET /api/matches` – Return potential matches based on availability
- `POST /api/session/request` – Create new session request
- `PUT /api/session/respond` – Accept, reject, or reschedule session
- `GET /api/calendar/:user_id` – Return full calendar view

---

## Admin Controls

- Override any session
- View scheduling stats (gaps, cancellations)
- Configure session policies (duration, lead time, buffer)

---

## Security & Validation

- All sessions require mutual confirmation
- Location must match expected for check-in
- Cancellations logged with reason (visible in history)

---

## Data Integrity Rules

- No double-booking allowed
- Past availability cannot be modified
- Expired pending requests auto-decline after configurable period

