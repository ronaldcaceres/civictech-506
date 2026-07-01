"""
Enrollment Validation Rules
Spec: specs/enrollment/01_validation_rules.md

Pure, stateless validation. No DB. No side effects.
Given a form payload → returns validation result + all errors found.
"""

import re
from dataclasses import dataclass, field

# Predefined valid skills (spec section 2.4)
VALID_SKILLS = {
    "Python", "JavaScript", "Frontend", "Backend", "DevOps",
    "Data", "Project Management", "Design", "Communications",
    "Legal", "Finance"
}

# Valid experience levels (spec section 2.6)
VALID_EXPERIENCE_LEVELS = {"Beginner", "Intermediate", "Advanced"}

@dataclass
class ValidationResult:
    validation_passed: bool = False
    errors: list[str] = field(default_factory=list)

def validate_full_name(name: str | None, errors: list[str])-> None:
    if not name or not name.strip():
        errors.append("full_name is required")
        return
    name = name.strip()
    if len(name) < 3:
        errors.append("full_name must be at least 3 characters")
    if not re.match(r"^[a-zA-ZÀ-ÿ\s]+$", name):
        errors.append("full_name must contain only letters and spaces")

def validate_email(email: str | None, errors: list[str]) -> None:
    if not email or not email.strip():
        errors.append("email is required")
        return
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email.strip()):
        errors.append("email format is invalid")

def validate_phone(phone: str | None, errors: list[str]) -> None:
    if not phone or not phone.strip():
        return  # opcional — si no viene, no hay error
    pattern = r"^(\+1)?\d{10}$"
    if not re.match(pattern, phone.strip().replace(" ", "").replace("-", "")):
        errors.append("phone format is invalid")

def validate_skills(skills: list[str] | None, errors: list[str]) -> None:
    if not skills:
        errors.append("at least one skill is required")
        return
    invalid = {s for s in skills if s not in VALID_SKILLS}
    if invalid:
        errors.append(f"skills contains invalid values: {', '.join(sorted(invalid))}")

def validate_availability(hours: int | None, errors: list[str]) -> None:
    if hours is None:
        errors.append("availability_hours_per_week is required")
        return
    if not isinstance(hours, int) or isinstance(hours, bool):
        errors.append("availability_hours_per_week must be a number")
        return
    if hours < 1 or hours > 40:
        errors.append("availability_hours_per_week must be between 1 and 40")


def validate_experience_level(level: str | None, errors: list[str]) -> None:
    if not level or not level.strip():
        errors.append("experience_level is required")
        return
    if level.strip() not in VALID_EXPERIENCE_LEVELS:
        errors.append("experience_level must be Beginner, Intermediate or Advanced")

def validate_motivation(motivation: str | None, errors: list[str]) -> None:
    if not motivation or not motivation.strip():
        errors.append("motivation is required")
        return
    if len(motivation.strip()) < 20:
        errors.append("motivation must be at least 20 characters")


def validate_linkedin_or_github(url: str | None, errors: list[str]) -> None:
    if not url or not url.strip():
        return  # opcional — si no viene, no hay error
    if not url.strip().startswith("https://"):
        errors.append("linkedin_or_github must be a valid URL (https://)")

def validate_registration_form(form: dict) -> ValidationResult:
    result = ValidationResult()

    validate_full_name(form.get("full_name"), result.errors)
    validate_email(form.get("email"), result.errors)
    validate_phone(form.get("phone"), result.errors)
    validate_skills(form.get("skills"), result.errors)
    validate_availability(form.get("availability_hours_per_week"), result.errors)
    validate_experience_level(form.get("experience_level"), result.errors)
    validate_motivation(form.get("motivation"), result.errors)
    validate_linkedin_or_github(form.get("linkedin_or_github"), result.errors)

    result.validation_passed = len(result.errors) == 0
    return result