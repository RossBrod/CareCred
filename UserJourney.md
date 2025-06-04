# 🧭 User Journey Spec: Student-Senior Credit Exchange App

##  User Roles
- **Student**: Volunteers time to earn tuition/housing credits.
- **Senior Citizen**: Receives assistance; helps award time credits via app.
- **Admin**: Approves users, monitors system, oversees credit issuance.

---

##  Student Journey

### 1.  Registration & Verification
- Sign up with college email.
- Upload government-issued ID + proof of enrollment.
- Undergo background check.
- Admin review → “Verified” status.

### 2.  Profile Setup
- Add photo, bio, skills, spoken languages.
- Set weekly availability via in-app calendar.
- Choose matching preference:
  - Be selected by seniors.
  - Actively request to help seniors.

### 3.  Matching & Scheduling
- Browse verified seniors or receive matches.
- View open time slots.
- Mutual confirmation required for session to be scheduled.
- Session appears on synced calendar.

### 4.  Check-in & Session Execution
- Arrive at senior’s location.
- **Check-in with GPS verification** via smartphone.
- Help senior (companionship, errands, tech help, etc.).
- Check-out at end of session.

### 5.  Blockchain Time Logging
- Upon check-out:
  - Student and senior confirm session.
  - App writes session data to **public blockchain**:
    - Anonymized IDs (hashed)
    - Time in/out, GPS, duration
    - Session hash
    - Digital signatures
  - Entry is **permanent and public**.

### 6.  Rating & Review
- Student rates senior.
- Senior rates student.
- Poor ratings lower priority in future matching.

### 7.  Credit Accrual
- Verified hours auto-converted into $ credits.
- Credits applied **directly** to:
  - Tuition account
  - Housing provider
- View credit balance and transaction history in app.

---

## Senior Citizen Journey

### 1.  Registration & Verification
- Sign up with simple form + ID.
- Submit program eligibility document.
- Optional: assisted onboarding by support staff.

### 2.  Profile Setup
- Add photo, bio, languages, types of help needed.
- Set weekly availability via calendar.
- Preferences for student type (age, gender, etc.).

### 3.  Matching & Scheduling
- Browse verified students or wait to be contacted.
- Confirm or propose session requests.
- Confirm final session in app.

### 4.  Session Completion
- Student checks in/out on location.
- Senior confirms session completion.
- Leave rating and optional feedback.

---

##  Admin/Coordinator Workflow

- Approve or reject student registrations.
- Integrate with background check provider.
- Monitor flagged users & session integrity.
- Distribute credits to institutions.
- View analytics: hours served, sessions completed, user activity.

---

##  Blockchain Role Summary

| Event | Blockchain Use |
|-------|----------------|
| Session Completion | Time log recorded immutably |
| Data Stored | Hashed user IDs, GPS, time, task hash |
| Integrity | Public, transparent, tamper-proof ledger |
| Credit Basis | Only blockchain-logged sessions count |

---

## 📱 Core App Features (per role)

### Student
- Calendar
- Match browser
- GPS check-in/out
- Blockchain session log viewer
- Credit dashboard
- Messaging

### Senior
- Simple calendar
- Student browser
- Session confirm/rate
- Help/support button

---

##  Matching Algorithm Factors
- Location proximity
- Availability overlap
- Rating score
- Task compatibility
- User preferences

---

##  Safeguards
- ID + background check
- GPS-verified location check-in
- Blockchain log = only source of truth
- In-app communication only
- Flag/report system
- Two-strike removal policy

