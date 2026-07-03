"""
Enrollment Validation Rules
Spec: specs/enrollment/01_validation_rules.md (v2.0)

Pure, stateless validation. No DB. No side effects.
Given a form payload → returns validation result + all errors found.
"""

import re
from dataclasses import dataclass, field

@dataclass
class ValidationResult:
    validation_passed: bool = False
    errors: list[str] = field(default_factory=list)

def validate_first_name(first_name: str | None, errors: list[str]) -> None:
    if not first_name or not first_name.strip():
        errors.append("first_name is required")
        return
    first_name = first_name.strip()
    if len(first_name) < 2:
        errors.append("first_name must be at least 2 characters")
    if not re.match(r"^[a-zA-ZÀ-ÿ\s]+$", first_name):
        errors.append("first_name must contain only letters and spaces")

def validate_last_name(last_name: str | None, errors: list[str]) -> None:
    if not last_name or not last_name.strip():
        errors.append("last_name is required")
        return
    last_name = last_name.strip()
    if len(last_name) < 2:
        errors.append("last_name must be at least 2 characters")
    if not re.match(r"^[a-zA-ZÀ-ÿ\s]+$", last_name):
        errors.append("last_name must contain only letters and spaces")

def validate_email(email: str | None, errors: list[str]) -> None:
    if not email or not email.strip():
        errors.append("email is required")
        return
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email.strip()):
        errors.append("email format is invalid")

def validate_phone(phone: str | None, errors: list[str]) -> None:
    if not phone or not phone.strip():
        errors.append("phone is required")
        return
    pattern = r"^(\+1)?\d{10}$"
    if not re.match(pattern, phone.strip().replace(" ", "").replace("-", "")):
        errors.append("phone format is invalid")

def validate_address(address: str | None, errors: list[str]) -> None:
    if not address or not address.strip():
        errors.append("address is required")
        return
    if len(address.strip()) < 5:
        errors.append("address must be at least 5 characters")

def validate_registration_form(form: dict) -> ValidationResult:
    result = ValidationResult()
    validate_first_name(form.get("first_name"), result.errors)
    validate_last_name(form.get("last_name"), result.errors)
    validate_email(form.get("email"), result.errors)
    validate_phone(form.get("phone"), result.errors)
    validate_address(form.get("address"), result.errors)
    result.validation_passed = len(result.errors) == 0
    return result