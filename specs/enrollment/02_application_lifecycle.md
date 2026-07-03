# Spec 02: Application Lifecycle

**Bounded Context:** Community & Volunteer Lifecycle
**Process:** Enrollment
**Version:** 1.0
**Status:** Draft
**Author:** Ronald Caceres
**Date:** 2026-07-01
**Source process:** docs/processes/enrollment_process.png

---

## 1. Context

This spec defines the lifecycle of an enrollment Application: its states,
the allowed transitions between them, and the rules governing resubmission.

**Key design decision (2026-07-01):** the correction loop reuses the SAME
Application entity transitioning back to SUBMITTED — not a new Application
per attempt. Full traceability is achieved through a status transition
history, not through entity duplication. Rationale: matches the business
process (BPMN correction loop), one row per applicant, simpler queries,
clearer member experience. Rejected alternative (new Application per
submission / event sourcing) adds complexity without a legal or business
requirement to justify it.

---

## 2. States

| State | Meaning |
|---|---|
| `SUBMITTED` | Form received, validation not yet run |
| `VALIDATION_FAILED` | Validation found errors; waiting for member correction |
| `STORED` | Validation passed; application saved, awaiting admin review |
| `APPROVED` | Admin approved the application (terminal state) |
| `REJECTED` | Admin rejected the application (terminal state) |

---

## 3. Allowed transitions (EARS format)

### 3.1 Submission and validation

- WHEN a member submits a Registration Form,
  THEN the system SHALL create an Application in state `SUBMITTED`.

- WHEN an Application is in `SUBMITTED` AND validation runs AND validation fails,
  THEN the system SHALL transition the Application to `VALIDATION_FAILED`.

- WHEN an Application is in `SUBMITTED` AND validation runs AND validation passes,
  THEN the system SHALL transition the Application to `STORED`.

### 3.2 Correction loop

- WHEN an Application is in `VALIDATION_FAILED` AND the member resubmits corrected data,
  THEN the system SHALL update the Application data AND transition it back to `SUBMITTED`.

- WHEN an Application is in `STORED` (under admin review),
  IF the member attempts to modify or resubmit,
  THEN the system SHALL reject the modification with error
  `"application is under review and cannot be modified"`.

### 3.3 Admin review and verification checklist

The admin verifies three items in person (documents are NOT uploaded to the
system; the member presents them physically). The system only records the
verification facts.

**Checklist items:** `volunteer_id`, `photograph`, `home_address`

- WHEN an Application is in `STORED` AND an admin marks a checklist item as verified,
  THEN the system SHALL record the item, the admin identity, and the timestamp.

- WHEN an Application is NOT in `STORED`,
  IF an admin attempts to mark a checklist item,
  THEN the system SHALL reject it with error
  `"checklist can only be updated while application is under review"`.

- WHEN an Application is in `STORED` AND an admin attempts to approve it,
  IF any checklist item is not verified,
  THEN the system SHALL reject the approval with error
  `"all verification checks must be completed before approval"`
  AND the Application SHALL remain in `STORED`.

- WHEN an Application is in `STORED` AND ALL checklist items are verified
  AND an admin approves it,
  THEN the system SHALL transition the Application to `APPROVED`.

- WHEN an Application is in `STORED` AND an admin rejects it,
  THEN the system SHALL transition the Application to `REJECTED`.
  (Rejection does NOT require the checklist to be complete — an admin can
  reject at any point during review.)

### 3.4 Terminal states

- WHEN an Application is in `APPROVED` or `REJECTED`,
  IF any transition is attempted on it,
  THEN the system SHALL reject the transition with error
  `"application is in a terminal state"`.

- WHEN a member whose Application was `REJECTED` wants to apply again,
  THEN the system SHALL require a NEW Application (the rejected one remains
  closed and immutable for audit purposes).

### 3.5 Invalid transitions (catch-all)

- WHEN any transition not explicitly allowed in sections 3.1–3.3 is attempted,
  THEN the system SHALL reject it with error
  `"invalid transition from {current_state} to {target_state}"`
  AND the Application state SHALL remain unchanged.

---

## 4. Transition history

- WHEN any state transition succeeds,
  THEN the system SHALL record: application_id, from_status, to_status,
  timestamp, triggered_by (`member` | `system` | `admin`), and optional notes
  (e.g., validation errors for that attempt).

---

## 5. Transition matrix (summary)

| From \ To | SUBMITTED | VALIDATION_FAILED | STORED | APPROVED | REJECTED |
|---|---|---|---|---|---|
| SUBMITTED | — | ✅ system | ✅ system | ❌ | ❌ |
| VALIDATION_FAILED | ✅ member | — | ❌ | ❌ | ❌ |
| STORED | ❌ | ❌ | — | ✅ admin (requires full checklist) | ✅ admin |
| APPROVED | ❌ | ❌ | ❌ | — | ❌ |
| REJECTED | ❌ | ❌ | ❌ | ❌ | — |

---

## 6. Out of scope for this spec

- Database persistence (repository layer)
- Email notifications
- API endpoints
- Admin authentication/authorization

---

## 7. Derived implementation

This spec derives directly into:
- `modules/community_lifecycle/enrollment/enums.py` (ApplicationStatus)
- `modules/community_lifecycle/enrollment/models.py` (Application + transition logic)
- `tests/enrollment/test_application_lifecycle.py`
- Verification checklist model (part of models.py or its own module)