"""
Enrollment Validation Tests
Spec: specs/enrollment/01_validation_rules.md
"""

from modules.community_lifecycle.enrollment.validation import (
    validate_registration_form,
    ValidationResult,
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def valid_form() -> dict:
    """Returns a complete, valid registration form.
    Use this as a base and override specific fields in each test."""
    return {
        "full_name": "Ronald Caceres",
        "email": "ronald.caceres@gmail.com",
        "phone": "5065551234",
        "skills": ["Python", "Backend"],
        "availability_hours_per_week": 10,
        "experience_level": "Intermediate",
        "motivation": "I want to contribute to my community through technology.",
        "linkedin_or_github": "https://github.com/ronaldcaceres",
    }


# ── Happy path ─────────────────────────────────────────────────────────────────

def test_valid_form_passes():
    result = validate_registration_form(valid_form())
    assert result.validation_passed is True
    assert result.errors == []

# ── full_name ──────────────────────────────────────────────────────────────────

def test_full_name_required():
    form = valid_form()
    form["full_name"] = ""
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "full_name is required" in result.errors


def test_full_name_none():
    form = valid_form()
    form["full_name"] = None
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "full_name is required" in result.errors


def test_full_name_too_short():
    form = valid_form()
    form["full_name"] = "RR"
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "full_name must be at least 3 characters" in result.errors


def test_full_name_with_numbers():
    form = valid_form()
    form["full_name"] = "Ronald2"
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "full_name must contain only letters and spaces" in result.errors


def test_full_name_with_french_accents():
    form = valid_form()
    form["full_name"] = "René Tremblay"
    result = validate_registration_form(form)
    assert result.validation_passed is True
    assert result.errors == []


def test_full_name_with_leading_spaces():
    form = valid_form()
    form["full_name"] = "  Ronald Caceres  "
    result = validate_registration_form(form)
    assert result.validation_passed is True
    assert result.errors == []

# ── email ──────────────────────────────────────────────────────────────────────

def test_email_required():
    form = valid_form()
    form["email"] = ""
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "email is required" in result.errors


def test_email_invalid_format():
    form = valid_form()
    form["email"] = "not-an-email"
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "email format is invalid" in result.errors


def test_email_missing_domain():
    form = valid_form()
    form["email"] = "ronald@"
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "email format is invalid" in result.errors


def test_email_missing_local_part():
    form = valid_form()
    form["email"] = "@gmail.com"
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "email format is invalid" in result.errors


# ── phone ──────────────────────────────────────────────────────────────────────

def test_phone_optional_when_absent():
    form = valid_form()
    del form["phone"]
    result = validate_registration_form(form)
    assert result.validation_passed is True
    assert result.errors == []


def test_phone_valid_with_country_code():
    form = valid_form()
    form["phone"] = "+15065551234"
    result = validate_registration_form(form)
    assert result.validation_passed is True
    assert result.errors == []


def test_phone_invalid_format():
    form = valid_form()
    form["phone"] = "123"
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "phone format is invalid" in result.errors


# ── skills ─────────────────────────────────────────────────────────────────────

def test_skills_required():
    form = valid_form()
    form["skills"] = []
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "at least one skill is required" in result.errors


def test_skills_invalid_value():
    form = valid_form()
    form["skills"] = ["Python", "Cooking"]
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "skills contains invalid values: Cooking" in result.errors


def test_skills_all_valid():
    form = valid_form()
    form["skills"] = ["Python", "DevOps", "Design"]
    result = validate_registration_form(form)
    assert result.validation_passed is True
    assert result.errors == []


# ── availability_hours_per_week ────────────────────────────────────────────────

def test_availability_required():
    form = valid_form()
    del form["availability_hours_per_week"]
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "availability_hours_per_week is required" in result.errors


def test_availability_below_minimum():
    form = valid_form()
    form["availability_hours_per_week"] = 0
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "availability_hours_per_week must be between 1 and 40" in result.errors


def test_availability_above_maximum():
    form = valid_form()
    form["availability_hours_per_week"] = 41
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "availability_hours_per_week must be between 1 and 40" in result.errors


def test_availability_bool_rejected():
    form = valid_form()
    form["availability_hours_per_week"] = True
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "availability_hours_per_week must be a number" in result.errors


# ── experience_level ───────────────────────────────────────────────────────────

def test_experience_level_required():
    form = valid_form()
    form["experience_level"] = ""
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "experience_level is required" in result.errors


def test_experience_level_invalid():
    form = valid_form()
    form["experience_level"] = "Expert"
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "experience_level must be Beginner, Intermediate or Advanced" in result.errors


def test_experience_level_valid_values():
    for level in ["Beginner", "Intermediate", "Advanced"]:
        form = valid_form()
        form["experience_level"] = level
        result = validate_registration_form(form)
        assert result.validation_passed is True, f"Expected {level} to be valid"


# ── motivation ─────────────────────────────────────────────────────────────────

def test_motivation_required():
    form = valid_form()
    form["motivation"] = ""
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "motivation is required" in result.errors


def test_motivation_too_short():
    form = valid_form()
    form["motivation"] = "Too short"
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "motivation must be at least 20 characters" in result.errors


# ── linkedin_or_github ─────────────────────────────────────────────────────────

def test_linkedin_optional_when_absent():
    form = valid_form()
    del form["linkedin_or_github"]
    result = validate_registration_form(form)
    assert result.validation_passed is True
    assert result.errors == []


def test_linkedin_invalid_url():
    form = valid_form()
    form["linkedin_or_github"] = "github.com/ronald"
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "linkedin_or_github must be a valid URL (https://)" in result.errors


def test_linkedin_valid_url():
    form = valid_form()
    form["linkedin_or_github"] = "https://linkedin.com/in/ronaldcaceres"
    result = validate_registration_form(form)
    assert result.validation_passed is True
    assert result.errors == []


# ── aggregate behavior ─────────────────────────────────────────────────────────

def test_all_rules_run_no_fail_fast():
    """Verifies that ALL validation rules run even when multiple fields fail."""
    form = {
        "full_name": "",
        "email": "",
        "skills": [],
        "availability_hours_per_week": None,
        "experience_level": "",
        "motivation": "",
    }
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert len(result.errors) >= 6