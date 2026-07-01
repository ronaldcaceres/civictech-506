# Spec 01: Enrollment Validation Rules

**Bounded Context:** Community & Volunteer Lifecycle  
**Process:** Enrollment  
**Version:** 1.0  
**Status:** Draft  
**Author:** Ronald Caceres  
**Date:** 2026-06-30  

---

## 1. Context

This spec defines the automatic data validation rules applied to a New Member
Registration Form submitted via the Civic Tech Moncton platform.

Validation is stateless and pure: given a form payload, it returns either
a success signal or a list of all validation errors found (not just the first).
No database access. No side effects.

---

## 2. Validation Rules (EARS format)

### 2.1 full_name

- **WHEN** the system receives a Registration Form,
  **IF** `full_name` is absent or empty,
  **THEN** the system SHALL add error `"full_name is required"` to the error list.

- **WHEN** the system receives a Registration Form,
  **IF** `full_name` contains fewer than 3 characters,
  **THEN** the system SHALL add error `"full_name must be at least 3 characters"` to the error list.

- **WHEN** the system receives a Registration Form,
  **IF** `full_name` contains digits or special characters,
  **THEN** the system SHALL add error `"full_name must contain only letters and spaces"` to the error list.

### 2.2 email

- **WHEN** the system receives a Registration Form,
  **IF** `email` is absent or empty,
  **THEN** the system SHALL add error `"email is required"` to the error list.

- **WHEN** the system receives a Registration Form,
  **IF** `email` does not match a valid email format (local@domain.tld),
  **THEN** the system SHALL add error `"email format is invalid"` to the error list.

### 2.3 phone (optional field)

- **WHEN** the system receives a Registration Form,
  **IF** `phone` is provided AND does not match the pattern `+1XXXXXXXXXX` or `XXXXXXXXXX` (10 digits),
  **THEN** the system SHALL add error `"phone format is invalid"` to the error list.

### 2.4 skills

- **WHEN** the system receives a Registration Form,
  **IF** `skills` is absent or empty,
  **THEN** the system SHALL add error `"at least one skill is required"` to the error list.

- **WHEN** the system receives a Registration Form,
  **IF** any value in `skills` is not in the predefined list,
  **THEN** the system SHALL add error `"skills contains invalid values: {invalid_values}"` to the error list.

  **Predefined skills:**
  `Python`, `JavaScript`, `Frontend`, `Backend`, `DevOps`, `Data`,
  `Project Management`, `Design`, `Communications`, `Legal`, `Finance`

### 2.5 availability_hours_per_week

- **WHEN** the system receives a Registration Form,
  **IF** `availability_hours_per_week` is absent,
  **THEN** the system SHALL add error `"availability_hours_per_week is required"` to the error list.

- **WHEN** the system receives a Registration Form,
  **IF** `availability_hours_per_week` is less than 1 or greater than 40,
  **THEN** the system SHALL add error `"availability_hours_per_week must be between 1 and 40"` to the error list.

### 2.6 experience_level

- **WHEN** the system receives a Registration Form,
  **IF** `experience_level` is absent or empty,
  **THEN** the system SHALL add error `"experience_level is required"` to the error list.

- **WHEN** the system receives a Registration Form,
  **IF** `experience_level` is not one of `Beginner`, `Intermediate`, `Advanced`,
  **THEN** the system SHALL add error `"experience_level must be Beginner, Intermediate or Advanced"` to the error list.

### 2.7 motivation

- **WHEN** the system receives a Registration Form,
  **IF** `motivation` is absent or empty,
  **THEN** the system SHALL add error `"motivation is required"` to the error list.

- **WHEN** the system receives a Registration Form,
  **IF** `motivation` contains fewer than 20 characters,
  **THEN** the system SHALL add error `"motivation must be at least 20 characters"` to the error list.

### 2.8 linkedin_or_github (optional field)

- **WHEN** the system receives a Registration Form,
  **IF** `linkedin_or_github` is provided AND does not start with `https://`,
  **THEN** the system SHALL add error `"linkedin_or_github must be a valid URL (https://)"` to the error list.

---

## 3. Aggregate behavior

- **WHEN** the system receives a Registration Form,
  **THE SYSTEM SHALL** run ALL validation rules before returning a result.
  Validation MUST NOT stop at the first error found.

- **WHEN** all rules pass with no errors,
  **THEN** the system SHALL return `validation_passed = True` and an empty error list.

- **WHEN** one or more rules fail,
  **THEN** the system SHALL return `validation_passed = False`
  and the complete list of all errors found.

---

## 4. Out of scope for this spec

- Database persistence
- Email notification
- Authentication
- Admin review logic

---

## 5. Derived implementation

This spec derives directly into:
- `modules/community_lifecycle/enrollment/validation.py`
- `tests/enrollment/test_validation.py`