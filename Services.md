# Core Modules & Services Architecture

---

## 1.  Authentication & Identity Service

### Responsibilities
- Student & senior registration/login
- Email & phone verification
- OAuth (Google/School SSO support)
- Multi-factor authentication
- Session management (JWT, refresh tokens)

---

## 2.  Verification & Onboarding Service

### Responsibilities
- ID upload & verification
- Student enrollment check (school API or document upload)
- Background check integration (via external API)
- Admin approval workflow
- Status tracker ("Pending", "Verified", "Rejected")

---

## 3.  Profile Management Service

### Responsibilities
- Manage student/senior bios, skills, languages
- Availability calendar setup
- Matching preferences
- Profile image uploads
- Edit/update personal data

---

## 4.  Calendar & Availability Service

### Responsibilities
- Weekly calendar view (syncs with external calendars optionally)
- Time slot offering and reservation
- Conflict detection
- Session lifecycle tracking: scheduled → confirmed → completed
- Rescheduling and cancellation policy logic

---

## 5.  Matching & Recommendation Engine

### Responsibilities
- Matching algorithm:
  - Location proximity
  - Availability overlap
  - Skills/task compatibility
  - Rating thresholds
  - Senior/student preferences
- Suggestions queue per user
- Smart matching triggers (e.g., auto-pairing)

---

## 6.  Geolocation & Check-in Service

### Responsibilities
- Validate GPS location during check-in/out
- Ensure student is physically at senior's location
- Track duration and log coordinates
- Prevent spoofing (e.g., anti-GPS-fake checks)

---

## 7.  Blockchain Logging Service

### Responsibilities
- Serialize session metadata:
  - Hashed student/senior IDs
  - Timestamps
  - Location data
  - Task hash
- Digitally sign records (user keys or app keypair)
- Publish session log to public blockchain
- Provide on-chain verification viewer (read-only API)

---

## 8.  Ratings & Review Service

### Responsibilities
- 5-star rating + optional comment per session
- Store historical ratings per user
- Calculate average scores
- Flag poor ratings for admin review
- Affect matching logic and trust score

---

## 9.  Credit Accrual & Ledger Service

### Responsibilities
- Track eligible service time (only if blockchain-logged)
- Convert hours to $ value (admin-defined rate)
- Maintain credit ledger per student
- Export payout reports to:
  - University billing (tuition)
  - Housing provider (rent)
- Display credit dashboard in-app

---

## 10.  Notification & Messaging Service

### Responsibilities
- In-app chat (moderated, no phone number exchange)
- Push notifications for:
  - Match requests
  - Session reminders
  - Approval status
- SMS/email for critical actions

---

## 11.  Admin & Oversight Portal

### Responsibilities
- Approve/reject users
- Monitor flagged ratings & abuse
- View blockchain session logs
- Credit disbursement approvals
- Analytics dashboard:
  - Total hours logged
  - Participation by region
  - User growth trends

---

## 12.  Monitoring & Compliance Service

### Responsibilities
- Log session integrity violations (e.g., GPS spoofing)
- Trigger audits for suspicious activity
- Escalation rules for flagged users
- Policy change broadcasting

