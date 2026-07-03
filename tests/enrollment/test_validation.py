"""
Enrollment Validation Tests
Spec: specs/enrollment/01_validation_rules.md (v2.0)
"""

from modules.community_lifecycle.enrollment.validation import (
    validate_registration_form,
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def valid_form() -> dict:
    """Returns a complete, valid registration form (spec v2.0).
    Use this as a base and override specific fields in each test."""
    return {
        "first_name": "Ronald",
        "last_name": "Caceres",
        "email": "ronald.caceres@gmail.com",
        "phone": "5065551234",
        "address": "123 Main Street, Moncton, NB",
    }


# ── Happy path ─────────────────────────────────────────────────────────────────

def test_valid_form_passes():
    result = validate_registration_form(valid_form())
    assert result.validation_passed is True
    assert result.errors == []


# ── first_name ─────────────────────────────────────────────────────────────────

def test_first_name_required():
    form = valid_form()
    form["first_name"] = ""
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "first_name is required" in result.errors


def test_first_name_none():
    form = valid_form()
    form["first_name"] = None
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "first_name is required" in result.errors


def test_first_name_too_short():
    form = valid_form()
    form["first_name"] = "R"
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "first_name must be at least 2 characters" in result.errors


def test_first_name_two_chars_valid():
    form = valid_form()
    form["first_name"] = "Li"
    result = validate_registration_form(form)
    assert result.validation_passed is True


def test_first_name_with_numbers():
    form = valid_form()
    form["first_name"] = "Ronald2"
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "first_name must contain only letters and spaces" in result.errors


def test_first_name_with_french_accents():
    form = valid_form()
    form["first_name"] = "René"
    result = validate_registration_form(form)
    assert result.validation_passed is True


# ── last_name ──────────────────────────────────────────────────────────────────

def test_last_name_required():
    form = valid_form()
    form["last_name"] = ""
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "last_name is required" in result.errors


def test_last_name_too_short():
    form = valid_form()
    form["last_name"] = "N"
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "last_name must be at least 2 characters" in result.errors


def test_last_name_two_chars_valid():
    form = valid_form()
    form["last_name"] = "Ng"
    result = validate_registration_form(form)
    assert result.validation_passed is True


def test_last_name_with_special_characters():
    form = valid_form()
    form["last_name"] = "Caceres!"
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "last_name must contain only letters and spaces" in result.errors


def test_last_name_with_french_accents():
    form = valid_form()
    form["last_name"] = "Tremblay-Côté".replace("-", " ")  # spaces allowed, hyphens not (v2.0)
    result = validate_registration_form(form)
    assert result.validation_passed is True


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


# ── phone (REQUIRED in v2.0) ───────────────────────────────────────────────────

def test_phone_required():
    form = valid_form()
    form["phone"] = ""
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "phone is required" in result.errors


def test_phone_absent_key():
    form = valid_form()
    del form["phone"]
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "phone is required" in result.errors


def test_phone_valid_with_country_code():
    form = valid_form()
    form["phone"] = "+15065551234"
    result = validate_registration_form(form)
    assert result.validation_passed is True


def test_phone_valid_with_spaces_and_dashes():
    form = valid_form()
    form["phone"] = "506-555-1234"
    result = validate_registration_form(form)
    assert result.validation_passed is True


def test_phone_invalid_format():
    form = valid_form()
    form["phone"] = "123"
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "phone format is invalid" in result.errors


# ── address (NEW in v2.0) ──────────────────────────────────────────────────────

def test_address_required():
    form = valid_form()
    form["address"] = ""
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "address is required" in result.errors


def test_address_absent_key():
    form = valid_form()
    del form["address"]
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "address is required" in result.errors


def test_address_too_short():
    form = valid_form()
    form["address"] = "abc"
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "address must be at least 5 characters" in result.errors


def test_address_free_text_valid():
    form = valid_form()
    form["address"] = "45 Botsford St, Apt 2B, Moncton NB E1C 4X1"
    result = validate_registration_form(form)
    assert result.validation_passed is True


# ── aggregate behavior ─────────────────────────────────────────────────────────

def test_all_rules_run_no_fail_fast():
    """Verifies that ALL validation rules run even when every field fails."""
    form = {
        "first_name": "",
        "last_name": "",
        "email": "",
        "phone": "",
        "address": "",
    }
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert len(result.errors) == 5  # exactly one "required" error per field


def test_empty_form_all_required_errors():
    result = validate_registration_form({})
    assert result.validation_passed is False
    assert "first_name is required" in result.errors
    assert "last_name is required" in result.errors
    assert "email is required" in result.errors
    assert "phone is required" in result.errors
    assert "address is required" in result.errors