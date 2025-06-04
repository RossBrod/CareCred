# Potential Cheating Methods by a Student and Mitigations

## Overview

This document outlines potential methods by which a student might attempt to game the system for earning unearned tuition or housing credits, and describes effective mitigations to maintain system integrity and trust.

---

## 1. Fake Check-ins (Spoofing GPS Location)

### Description
Student attempts to fake their location to check in at the senior's address without being physically present.

### Mitigations
- Require GPS + Wi-Fi triangulation for check-in.
- Use GPS spoofing detection libraries.
- Check for impossible travel times between sessions.
- Capture real-time image from front-facing camera with geotag.
- Compare location metadata with blockchain-logged values.

---

## 2. Dual Device Fraud

### Description
Student gives a device to someone else to simulate a session or places a device at the senior's home to spoof presence.

### Mitigations
- Require biometric re-authentication at check-in (face match with ID).
- Periodic random check-ins (photo or prompt) during session.
- QR code or NFC check-in at senior's physical location (senior must display or initiate).
- Require both parties to initiate or confirm start/end.

---

## 3. Collusion with the Senior

### Description
Student and senior agree to log a fake session and split the benefit (e.g., student gets credit, senior gets a kickback).

### Mitigations
- Randomized senior feedback verification from third parties (e.g., family, admin).
- Session pattern analysis for anomalies (too frequent, always max duration, odd hours).
- Flag and review highly correlated matches (student always works with same senior).
- Require a rotating match system to limit exclusive pairing.

---

## 4. Logging Longer Time Than Actually Worked

### Description
Student checks in legitimately but logs an extended session without actually staying.

### Mitigations
- Compare expected vs. actual time spent for each task type.
- Use geofencing to auto-end session if student leaves location early.
- Ask the senior for a time confirmation or rating prompt at session end.
- In future: Use IoT devices or passive presence detection (optional, consent-based).

---

## 5. Replaying Past Check-ins or Logs

### Description
Student replays past check-in data to the system to create fake sessions.

### Mitigations
- Use nonce-based session tokens that expire after use.
- Log unique session IDs and timestamps to detect reuse.
- Require real-time validation from both users during the session.

---

## 6. Impersonation

### Description
Another person impersonates the verified student to complete the session.

### Mitigations
- Require selfie photo verification before or during the session.
- Biometric check at registration and periodic spot checks.
- Senior is shown a student photo at confirmation and can flag mismatches.

---

## 7. Session Inflation via Short Task Splitting

### Description
Student splits one short task into multiple fake sessions to inflate credit hours.

### Mitigations
- Enforce minimum session duration (e.g., 30 minutes).
- Prevent multiple check-ins at the same location within a short time span.
- Apply cooldown window between sessions with the same senior.

---

## 8. Hacking or API Abuse

### Description
Student attempts to exploit API endpoints to inject or manipulate session data.

### Mitigations
- Require signed blockchain transactions for session logs.
- Restrict credit calculation to blockchain-verified logs only.
- Monitor logs for unauthorized API calls or strange session patterns.
- Use rate-limiting, authentication, and request signature validation.

---

## Conclusion

Mitigating cheating is essential for maintaining the credibility of the platform. A combination of biometric validation, GPS checks, blockchain immutability, behavior analytics, and random audits can collectively create a robust defense against fraudulent behavior by students.

