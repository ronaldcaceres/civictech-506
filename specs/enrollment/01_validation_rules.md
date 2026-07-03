# Spec 01: Enrollment Validation Rules

**Bounded Context:** Community & Volunteer Lifecycle
**Process:** Enrollment
**Version:** 2.0
**Status:** Active
**Author:** Ronald Caceres
**Date:** 2026-07-02
**Source process:** docs/processes/enrollment_process.png

---

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-06-30 | Initial draft with proposed fields |
| 2.0 | 2026-07-02 | Aligned with the real organizational Registration Form: `full_name` split into `first_name` + `last_name`; `phone` now required; `address` added (free text, required); removed `skills`, `availability_hours_per_week`, `experience_level`, `motivation`, `linkedin_or_github` (moved to the Onboarding process). |

---

## 1. Context

This spec defines the automatic data validation rules applied to a New Member
Registration Form submitted via the Civic Tech Moncton platform.

Validation is stateless and pure: given a form payload, it returns either
a success signal or a list of all validation errors found (not just the first).
No database access. No side effects.

**Note:** stateful validations (e.g., duplicate email prevention) are NOT
part of this spec — they belong to the service layer and are defined in
Spec 02, section 3.1.

---

## 2. Registration Form fields

All five fields are REQUIRED.

| Field | Type | Rule |
|---|---|---|
| `first_name` | string | Required, min 2 chars, letters and spaces only (including French accents) |
| `last_name` | string | Required, min 2 chars, letters and spaces only (including French accents) |
| `email` | string | Required, valid email format |
| `phone` | string | Required, format `+1XXXXXXXXXX` or `XXXXXXXXXX` (10 digits) |
| `address` | string | Required, free text, min 5 chars |

---

## 3. Validation Rules (EARS format)

### 3.1 first_name

- WHEN the system receives a Registration Form,
  IF `first_name` is absent or empty,
  THEN the system SHALL add error `"first_name is required"` to the error list.

- WHEN the system receives a Registration Form,
  IF `first_name` contains fewer than 2 characters,
  THEN the system SHALL add error `"first_name must be at least 2 characters"` to the error list.

- WHEN the system receives a Registration Form,
  IF `first_name` contains digits or special characters,
  THEN the system SHALL add error `"first_name must contain only letters and spaces"` to the error list.

### 3.2 last_name

- WHEN the system receives a Registration Form,
  IF `last_name` is absent or empty,
  THEN the system SHALL add error `"last_name is required"` to the error list.

- WHEN the system receives a Registration Form,
  IF `last_name` contains fewer than 2 characters,
  THEN the system SHALL add error `"last_name must be at least 2 characters"` to the error list.

- WHEN the system receives a Registration Form,
  IF `last_name` contains digits or special characters,
  THEN the system SHALL add error `"last_name must contain only letters and spaces"` to the error list.

### 3.3 email

- WHEN the system receives a Registration Form,
  IF `email` is absent or empty,
  THEN the system SHALL add error `"email is required"` to the error list.

- WHEN the system receives a Registration Form,
  IF `email` does not match a valid email format (local@domain.tld),
  THEN the system SHALL add error `"email format is invalid"` to the error list.

### 3.4 phone (now REQUIRED — changed in v2.0)

- WHEN the system receives a Registration Form,
  IF `phone` is absent or empty,
  THEN the system SHALL add error `"phone is required"` to the error list.

- WHEN the system receives a Registration Form,
  IF `phone` does not match the pattern `+1XXXXXXXXXX` or `XXXXXXXXXX` (10 digits),
  THEN the system SHALL add error `"phone format is invalid"` to the error list.

### 3.5 address (new in v2.0)

- WHEN the system receives a Registration Form,
  IF `address` is absent or empty,
  THEN the system SHALL add error `"address is required"` to the error list.

- WHEN the system receives a Registration Form,
  IF `address` contains fewer than 5 characters,
  THEN the system SHALL add error `"address must be at least 5 characters"` to the error list.

---

## 4. Aggregate behavior

- WHEN the system receives a Registration Form,
  THE SYSTEM SHALL run ALL validation rules before returning a result.
  Validation MUST NOT stop at the first error found.

- WHEN all rules pass with no errors,
  THEN the system SHALL return `validation_passed = True` and an empty error list.

- WHEN one or more rules fail,
  THEN the system SHALL return `validation_passed = False`
  and the complete list of all errors found.

---

## 5. Out of scope for this spec

- Duplicate email prevention (stateful — see Spec 02, section 3.1)
- Database persistence
- Email notification
- Authentication
- Admin review logic

---

## 6. Derived implementation

This spec derives directly into:
- `modules/community_lifecycle/enrollment/validation.py`
- `tests/enrollment/test_validation.py`