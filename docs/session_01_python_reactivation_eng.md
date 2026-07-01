# Session 01 — Python Reactivation
## Civic Tech Moncton 506 — Study Notes

**Date:** 2026-06-30  
**Project:** civictech-506  
**Goal:** Python reactivation + development environment setup + first real module

---

## PART 1 — Development Environment

### Installed and verified stack

| Tool | Version | Purpose |
|---|---|---|
| Ubuntu | 26.04 LTS "Resolute" | Base operating system |
| Git | 2.53.0 | Version control |
| Python | 3.13.14 and 3.14.6 | Main language |
| uv | 0.11.26 | Package and virtual environment manager |
| Docker | 29.6.1 | Containers (Phase 2) |
| Docker Compose | v5.2.0 | Orchestrate multiple containers |
| Claude Code | v2.1.197 + Sonnet 4.6 | AI coding agent |
| VS Code | — | Main IDE |

---

### `uv` — the modern Python manager

`uv` replaces `pip`, `venv`, `pyenv` and `poetry` in a single tool. It is 10-100x faster than pip.

```bash
# Create a new project
uv init project-name --python 3.13
cd project-name

# Add dependencies
uv add fastapi pandas requests

# Run a script
uv run main.py

# Run Python interactively
uv run python
```

**Why not use the system Python on Ubuntu:**
Ubuntu uses Python internally for the operating system. Modifying it can break the system. `uv` creates isolated environments per project — the system Python is never touched.

---

### Project folder structure

```
civictech-506/
├── shared/
│   └── domain/
│       └── person.py              # Minimal Shared Kernel (PersonId, email, name)
├── modules/
│   └── community_lifecycle/        # Bounded Context 1
│       ├── domain/
│       │   ├── member.py
│       │   └── value_objects.py
│       └── enrollment/             # Current process
│           ├── models.py
│           ├── enums.py
│           ├── validation.py       ← built today
│           ├── repository.py
│           ├── service.py
│           └── routes.py
├── specs/
│   └── enrollment/
│       └── 01_validation_rules.md  ← first SDD document
├── api/
│   └── main.py
└── tests/
```

---

### Git — professional branch structure

```
main      ← production, always stable
staging   ← pre-production, integration and testing
dev       ← active development, daily working base
feature/* ← one branch per feature, merged to dev
```

**Workflow:**
```
feature/my-feature → dev → staging → main
```

**Essential commands:**
```bash
# Create and switch to a new branch
git checkout -b feature/branch-name

# View all branches
git branch -a

# Push branch to remote
git push -u origin feature/branch-name

# Pull changes from remote
git pull origin dev

# One-time global configuration
git config --global pull.rebase false
git config --global user.email "you@email.com"
git config --global user.name "Your Name"
```

**SSH to GitHub:**
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "you@email.com"

# Print public key to copy to GitHub
cat ~/.ssh/id_ed25519.pub

# Verify connection
ssh -T git@github.com
```

---

## PART 2 — Architecture and Design

### Why Modular Monolith (not Microservices)

Microservices solve problems of **organizational scale** (multiple teams deploying independently) and **differentiated traffic scale**. For a single developer with a bounded domain, the cost outweighs the benefit:

- Service-to-service communication (HTTP, message queues) — unnecessary complexity
- Distributed transactions — consistency problems
- Harder debugging — the bug might be in the network
- DevOps work multiplied by N services

**The right decision:** Modular Monolith with well-defined bounded contexts. If the project grows and there is a real need to scale, the modules are already ready to be extracted as services — without refactoring the domain.

---

### Domain-Driven Design (DDD) — Bounded Contexts

A **bounded context** is a boundary where a ubiquitous language (business terms) has a specific and consistent meaning.

**The 4 bounded contexts of civictech-506:**

| Context | Processes | Core Entity |
|---|---|---|
| Community & Volunteer Lifecycle | Enrollment, Onboarding, Engagement, Recognition | `Member` |
| Challenge Intake & Project Delivery | Challenge Intake, Project Scoping, Solution Dev, Delivery | `Project` |
| Community Partnerships & Outreach | Institutional Partnerships, Events, Advocacy, PR | `Partnership` / `Event` |
| Governance & Operations | Strategic Planning, Resources, Compliance, Performance | `Resource` / `Metric` |

**Shared Kernel** — the minimum that is truly universal:
```python
# shared/domain/person.py
# ONLY identity: PersonId, email, full_name. Nothing else.
```

Each context has its own "view" of a person with the data that matters to it, related by `PersonId`. This avoids the "God Object" anti-pattern.

**Enrollment is NOT a bounded context** — it is a process within `Community & Volunteer Lifecycle`.

---

### Lightweight Spec-Driven Development (SDD)

SDD is a methodology where the specification — not the code — is the source of truth.

**The flow we use:**
```
Specify → Plan → Implement
```

**EARS notation** (Easy Approach to Requirements Syntax):
```
WHEN [condition], IF [situation], THEN [the system SHALL do X]
```

Real example:
```
WHEN the system receives a Registration Form,
IF full_name contains fewer than 3 characters,
THEN the system SHALL add the error "full_name must be at least 3 characters"
```

**Structure in the repo:**
```
specs/
└── enrollment/
    ├── 01_validation_rules.md    ← current spec
    ├── 02_application_lifecycle.md
    └── 03_api_contracts.md
```

**Rule for using Cursor/Claude Code in Phase 1:**
- ✅ Use the chat as a **tutor** ("why does this work?", "how does this compare to C#?")
- ❌ Don't let the agent write the core logic for you — you lose the learning

---

## PART 3 — Python Concepts Learned

### 1. `set` vs `list` — O(1) vs O(n)

```python
# list — searches element by element (O(n))
"Python" in ["Python", "JavaScript", "Frontend"]  # checks one by one

# set — hash table, instant lookup (O(1))
"Python" in {"Python", "JavaScript", "Frontend"}  # goes directly to the value
```

**C# equivalent:**
```csharp
var list = new List<string> { "Python" };
list.Contains("Python");  // O(n)

var set = new HashSet<string> { "Python" };
set.Contains("Python");  // O(1)
```

**Practical rule:** If you only need to ask "is this element here?" and order doesn't matter → use `set`.

---

### 2. `@dataclass` and `field(default_factory=list)`

```python
from dataclasses import dataclass, field

@dataclass
class ValidationResult:
    validation_passed: bool = False
    errors: list[str] = field(default_factory=list)  # ← correct
    # errors: list[str] = []  # ← DANGEROUS, never do this
```

**Why `= []` is dangerous — the Mutable Default Argument Trap:**

```python
# With = [] (WRONG)
r1 = ValidationResult()
r2 = ValidationResult()
r1.errors.append("email is required")
print(r2.errors)  # ["email is required"] ← SAME shared object

# With field(default_factory=list) (RIGHT)
r1 = ValidationResult()
r2 = ValidationResult()
r1.errors.append("email is required")
print(r2.errors)  # [] ← its own list, correct
```

**The trap:** in Python, `= []` in a class creates ONE single list at class definition time, shared by ALL instances. `default_factory=list` creates a fresh list for each new instance.

**Applies to all mutable objects as defaults:** `list`, `dict`, `set`.

**C# equivalent:**
```csharp
// C# creates a new list per instance automatically
public List<string> Errors { get; set; } = new List<string>();
// Python needs to specify this explicitly with default_factory
```

---

### 3. Type hints — `str | None`

```python
# Python 3.10+ — the | operator means "can be this type OR this other one"
def validate_full_name(name: str | None, errors: list[str]) -> None:
    ...
```

**C# equivalent:**
```csharp
void ValidateFullName(string? name, List<string> errors) { }
```

`-> None` = `void` in C#.

Types are optional at runtime in Python, but we declare them to:
- Let Pylance/Ruff catch errors while you write
- Document intent
- Testing tools use them to generate test cases automatically

---

### 4. `re.match()` — Regular expressions

```python
import re

# Validate name — letters only (including French accents) and spaces
re.match(r"^[a-zA-ZÀ-ÿ\s]+$", name)

# Validate email
pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
re.match(pattern, email)

# Validate Canadian phone number
re.match(r"^(\+1)?\d{10}$", phone)
```

**Breakdown of the name pattern:**
| Part | Meaning |
|---|---|
| `^` | From the first character |
| `[a-zA-Z]` | Uppercase and lowercase letters |
| `À-ÿ` | Extended Latin characters (accents, diacritics, ç) |
| `\s` | Spaces |
| `+` | One or more characters |
| `$` | Until the last character |

**Why regex and not `"@" in email`:**
`"@" in email` approves `"@gmail.com"`, `"ronald@"`, `"ronald@@gmail"` — all invalid. The regex requires full structure: local part + @ + domain + extension.

---

### 5. `.strip()` — equivalent to `.Trim()` in C#

```python
"  ronald@gmail.com  ".strip()   # → "ronald@gmail.com"
"  hello  ".lstrip()             # → "hello  " (left side only)
"  hello  ".rstrip()             # → "  hello" (right side only)
```

| C# | Python |
|---|---|
| `.Trim()` | `.strip()` |
| `.TrimStart()` | `.lstrip()` |
| `.TrimEnd()` | `.rstrip()` |

**Why use it in validation:** users often add accidental spaces when typing or copy-pasting. Without `.strip()`, `"ronald@gmail.com "` (with trailing space) would fail validation even though the email is correct.

---

### 6. Set Comprehension

```python
# Set comprehension — produces a set
invalid = {s for s in skills if s not in VALID_SKILLS}

# C# equivalent (LINQ)
var invalid = skills.Where(s => !validSkills.Contains(s)).ToHashSet();

# Python equivalent without comprehension (explicit loop)
invalid = set()
for s in skills:
    if s not in VALID_SKILLS:
        invalid.add(s)
```

**Structure of any comprehension:**
```python
{expression for variable in iterable if condition}
#  ↑ what      ↑ where it comes from   ↑ optional filter
```

**The three flavors:**
```python
[s for s in skills if ...]    # list comprehension → produces list
{s for s in skills if ...}    # set comprehension  → produces set
{k: v for k, v in d.items()}  # dict comprehension → produces dict
```

---

### 7. `.get()` vs `[]` on dictionaries

```python
form = {"email": "ronald@gmail.com"}

form["full_name"]        # → KeyError if key doesn't exist ← crash
form.get("full_name")    # → None if key doesn't exist ← safe
```

**C# equivalent:**
```csharp
dict.TryGetValue("full_name", out var value) ? value : null;
```

**Practical rule:** when the dict comes from external input (form, API, JSON), always use `.get()` — you can't guarantee the user sent all fields.

---

### 8. `isinstance` + the `bool` subclassing `int` quirk

```python
# In Python, bool is a subclass of int — surprising for C# developers
isinstance(True, int)   # → True
isinstance(False, int)  # → True
True == 1               # → True
False == 0              # → True
True + True             # → 2

# The silent bug
hours = True
isinstance(hours, int)           # → True ← passes the type check
hours < 1 or hours > 40         # → False (True == 1, between 1 and 40)
# result: True passes as "1 hour" ← wrong
```

**The fix — explicitly exclude bool:**
```python
if not isinstance(hours, int) or isinstance(hours, bool):
    errors.append("availability_hours_per_week must be a number")
```

**In C# this problem doesn't exist** — `bool` and `int` are completely separate types, the compiler won't allow it.

---

### 9. `__init__.py` — why it exists

For Python to recognize a folder as an **importable package**, it needs an `__init__.py` file (can be empty).

```bash
# Without __init__.py
from modules.community_lifecycle.enrollment.validation import ...
# → ModuleNotFoundError

# With __init__.py in each folder of the path
touch modules/__init__.py
touch modules/community_lifecycle/__init__.py
touch modules/community_lifecycle/enrollment/__init__.py
# → works correctly
```

**How Python translates an import to a file path:**
```python
from modules.community_lifecycle.enrollment.validation import validate_registration_form
#    ↓
#    modules/community_lifecycle/enrollment/validation.py
```

Each dot is a folder separator. The last name is the `.py` file.

---

### 10. Error accumulator pattern

Instead of returning an error list per function and concatenating at the end, we pass the same list to all functions:

```python
# All functions receive and modify the SAME list
def validate_full_name(name: str | None, errors: list[str]) -> None:
    errors.append("error here if it fails")

def validate_registration_form(form: dict) -> ValidationResult:
    result = ValidationResult()
    validate_full_name(form.get("full_name"), result.errors)
    validate_email(form.get("email"), result.errors)
    # ... more validations ...
    result.validation_passed = len(result.errors) == 0
    return result
```

**Why:** the spec says "run ALL rules before returning". With the accumulator, when the last function finishes, you already have all errors — no extra concatenation needed.

---

### 11. Local vs global fail-fast

```python
# GLOBAL fail-fast — forbidden by the spec
# (do not stop between different fields)

# LOCAL fail-fast — correct within a single field
def validate_full_name(name: str | None, errors: list[str]) -> None:
    if not name or not name.strip():
        errors.append("full_name is required")
        return  # ← exits the function, NOT the whole validation
    # If we get here, name exists — it makes sense to check length and format
    if len(name) < 3:
        errors.append("full_name must be at least 3 characters")
```

**The rule:** between fields → no fail-fast. Within a field → fail-fast after the fundamental error (no point checking length if the field is empty).

---

### 12. Required field vs optional field — patterns

```python
# REQUIRED field — absence = error
def validate_full_name(name: str | None, errors: list[str]) -> None:
    if not name or not name.strip():
        errors.append("full_name is required")
        return  # exits with error added

# OPTIONAL field — absence = ok
def validate_phone(phone: str | None, errors: list[str]) -> None:
    if not phone or not phone.strip():
        return  # exits without error — valid to not have a phone
    # If we get here, the field was provided — validate format
    if not re.match(pattern, phone.strip()):
        errors.append("phone format is invalid")
```

---

## PART 4 — The complete `validation.py` file

```python
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


def validate_full_name(name: str | None, errors: list[str]) -> None:
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
        return
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
        return
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
```

---

## PART 5 — Next Steps

### Next session
- **Formal tests with `pytest`** — verify that `validation.py` meets the spec point by point
- This closes the SDD cycle: spec → code → tests

### Overall plan (reminder)
| Weeks | Focus | Deliverable |
|---|---|---|
| 1-4 | Python + domain | validation.py ✅, models.py, enums.py, FastAPI |
| 5-9 | Docker + AWS | Containerized app in the cloud |
| 10-13 | LLMs / RAG / Agents | AI integration |
| 14-16 | Portfolio + narrative | Complete project + gap pitch |

### Reference resources
- **Fred Baptiste Python Deep Dive Part 1** (Udemy) — search: "mutable default", "dataclass", "closures"
- **Real Python** (realpython.com) — targeted tutorials per concept
- **FastAPI official tutorial** (fastapi.tiangolo.com) — week 3
- **Kaggle Pandas micro-course** — week 3

---

*Document generated: 2026-06-30 | civictech-506 | Session 01*
