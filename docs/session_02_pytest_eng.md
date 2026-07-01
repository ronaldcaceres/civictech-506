# Session 02 — Testing with pytest
## Civic Tech Moncton 506 — Study Notes

**Date:** 2026-07-01  
**Project:** civictech-506  
**Goal:** Write a formal test suite for `validation.py`, closing the SDD cycle

---

## PART 1 — What is pytest and why we use it

`pytest` is the most widely used testing framework in the Python ecosystem. It verifies that our code behaves as the specification requires.

**Install it as a development dependency:**
```bash
uv add pytest --dev
```

`--dev` means pytest is only needed during development, not in production. It is the equivalent of `devDependencies` in npm.

**Verify installation:**
```bash
uv run pytest --version
```

**Run the test suite:**
```bash
# Run a specific file
uv run pytest tests/enrollment/test_validation.py -v

# Run all tests in the tests/ folder
uv run pytest tests/ -v
```

The `-v` flag means "verbose" — it shows each test name and its result, instead of just a dot per test.

---

## PART 2 — How pytest finds and runs tests

pytest follows three automatic rules — no configuration required:

1. Looks for **files** that start with `test_`
2. Inside those files, looks for **functions** that start with `test_`
3. Runs those functions and reports pass/fail

**This is why naming matters:**
```python
def valid_form():          # ← does NOT start with test_ → pytest IGNORES it
def test_valid_form_passes():  # ← starts with test_ → pytest RUNS it
```

**Comparison with C#:**
```csharp
// C# — requires a class, attributes, and a test runner
[TestClass]
public class ValidationTests
{
    [TestMethod]
    public void TestFullName() { ... }
}
```
```python
# Python/pytest — just a function with the correct name. No class, no attributes.
def test_full_name():
    ...
```

pytest is significantly simpler than NUnit or xUnit — no boilerplate.

---

## PART 3 — The `assert` statement

pytest uses Python's built-in `assert` keyword. If the condition is `True`, the test passes silently. If it is `False`, the test fails and pytest shows a detailed message.

```python
def test_valid_form_passes():
    result = validate_registration_form(valid_form())
    assert result.validation_passed is True
    assert result.errors == []
```

**Comparison with C#:**
```csharp
// C# — explicit assertion methods
Assert.IsTrue(result.ValidationPassed);
Assert.AreEqual(0, result.Errors.Count);
```
```python
# Python — plain assert with any boolean expression
assert result.validation_passed is True
assert result.errors == []
```

**Common assertion patterns used in this session:**
```python
assert result.validation_passed is True      # boolean check
assert result.errors == []                     # equality check
assert "error message" in result.errors        # membership check (is X in the list?)
assert len(result.errors) >= 6                 # comparison check
```

**Why `is True` and not `== True`:**
`is` checks identity (same object in memory), `==` checks equality (same value). For booleans and `None`, always use `is` — it is the Pythonic convention and slightly more strict.

---

## PART 4 — The helper function pattern

Instead of rebuilding the entire form in every test, we create one helper that returns a known valid form. Each test starts from that base and overrides only the field it wants to test.

```python
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
```

**How each test uses it:**
```python
def test_full_name_too_short():
    form = valid_form()           # start from a valid form
    form["full_name"] = "RR"     # override ONLY the field under test
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "full_name must be at least 3 characters" in result.errors
```

**Why this matters:**
- Each test focuses on **one thing only** — one field, one rule
- If validation logic changes, you update the base form in one place
- Tests stay readable and short

In C# this is often done with a `[TestInitialize]` method or a builder pattern. In pytest, a simple helper function is enough.

---

## PART 5 — Types of tests we wrote

A complete test suite covers more than just the happy path. We wrote 30 tests across these categories:

### 5.1 Happy path
Confirms that valid input passes.
```python
def test_valid_form_passes():
    result = validate_registration_form(valid_form())
    assert result.validation_passed is True
```

### 5.2 Required fields
Confirms that missing required fields produce errors.
```python
def test_full_name_required():
    form = valid_form()
    form["full_name"] = ""
    result = validate_registration_form(form)
    assert "full_name is required" in result.errors
```

### 5.3 Optional fields
Confirms that optional fields are valid when absent.
```python
def test_phone_optional_when_absent():
    form = valid_form()
    del form["phone"]            # remove the key entirely
    result = validate_registration_form(form)
    assert result.validation_passed is True
```

### 5.4 Boundary values
Tests the exact edges of a numeric range.
```python
def test_availability_below_minimum():   # 0 (just below 1)
    form["availability_hours_per_week"] = 0
    # ... expect error

def test_availability_above_maximum():   # 41 (just above 40)
    form["availability_hours_per_week"] = 41
    # ... expect error
```
Boundary testing catches "off-by-one" bugs — the most common numeric errors.

### 5.5 Format validation
Tests that invalid formats are rejected.
```python
def test_email_missing_domain():
    form["email"] = "ronald@"     # missing domain
    # ... expect "email format is invalid"

def test_email_missing_local_part():
    form["email"] = "@gmail.com"  # missing local part
    # ... expect "email format is invalid"
```

### 5.6 Edge cases specific to our domain
```python
def test_full_name_with_french_accents():  # René must be valid (bilingual city)
    form["full_name"] = "René Tremblay"
    assert result.validation_passed is True

def test_availability_bool_rejected():       # True must NOT count as 1
    form["availability_hours_per_week"] = True
    assert "availability_hours_per_week must be a number" in result.errors
```

### 5.7 Looping over multiple valid values
```python
def test_experience_level_valid_values():
    for level in ["Beginner", "Intermediate", "Advanced"]:
        form = valid_form()
        form["experience_level"] = level
        result = validate_registration_form(form)
        assert result.validation_passed is True, f"Expected {level} to be valid"
```
Note the message after the comma — it prints only if the assertion fails, telling you exactly which value broke.

### 5.8 Aggregate behavior
Verifies the "no fail-fast" rule from the spec.
```python
def test_all_rules_run_no_fail_fast():
    """Verifies that ALL rules run even when multiple fields fail."""
    form = {
        "full_name": "", "email": "", "skills": [],
        "availability_hours_per_week": None,
        "experience_level": "", "motivation": "",
    }
    result = validate_registration_form(form)
    assert len(result.errors) >= 6   # all 6 required fields report their error
```

---

## PART 6 — Reading pytest output when a test fails

pytest failure messages are precise. This is the real bug we caught in this session:

```
AssertionError: assert 'full_name is required' in ['full name is required']
#                        ↑ underscore (expected)   ↑ space (actual)
```

pytest tells you:
- What you expected: `'full_name is required'` (with underscore)
- What the code returned: `'full name is required'` (with space)
- Exactly which line failed

**The bug:** `validation.py` had `"full name is required"` (space) instead of `"full_name is required"` (underscore). The manual test missed it because we read the output quickly; pytest caught it instantly.

**Why this bug mattered:** an API client expecting the field name `full_name` in the error response would never match `full name`. This kind of silent inconsistency breaks contracts between systems — exactly the kind of thing tests exist to prevent.

---

## PART 7 — The SDD cycle, now complete

```
Spec (01_validation_rules.md)      ← defines WHAT the system must do
  → Code (validation.py)            ← implements the rules
    → Tests (test_validation.py)    ← verifies the code meets the spec
      → Bug found and fixed ✅
```

Every test traces back to a rule in the spec. This traceability is what makes the codebase professional and maintainable.

---

## PART 8 — Git workflow used this session

```bash
# Create feature branch
git checkout -b feature/enrollment-validation-test

# Stage and commit
git add tests/ modules/community_lifecycle/enrollment/validation.py
git commit -m "test: add enrollment validation test suite (30 tests, all passing)"

# Push
git push origin feature/enrollment-validation-test

# On GitHub: create PR → base branch dev → merge

# Sync local dev
git checkout dev
git pull origin dev
```

**Commands learned about git fetch:**
```bash
git fetch                          # updates info about ALL remote branches
git fetch origin branch-name       # updates info about ONE specific branch
git fetch origin branch -- file    # extracts a specific file from a remote branch

# Inspect before pulling
git log dev..origin/dev --oneline  # commits on remote you don't have locally
git diff dev origin/dev            # file differences
```

**Key distinction:**
- `git fetch` = look at what changed on the remote, without touching local code
- `git pull` = fetch + merge into current branch

---

## PART 9 — Next steps

### Next session
- **Domain modeling** — `Application` model, `ApplicationStatus` enum, the state machine (`PENDING → STORED → APPROVED/REJECTED`)
- This corresponds to `specs/enrollment/02_application_lifecycle.md` (to be created)

### Overall plan (reminder)
| Weeks | Focus | Deliverable |
|---|---|---|
| 1-4 | Python + domain | validation.py ✅, tests ✅, models.py, enums.py, FastAPI |
| 5-9 | Docker + AWS | Containerized app in the cloud |
| 10-13 | LLMs / RAG / Agents | AI integration |
| 14-16 | Portfolio + narrative | Complete project + gap pitch |

### Reference resources
- **pytest official docs** (docs.pytest.org) — the definitive reference
- **Real Python — "Getting Started With pytest"** — practical tutorial
- **Fred Baptiste Python Deep Dive** — for deeper Python concepts as needed

---

*Document generated: 2026-07-01 | civictech-506 | Session 02*
