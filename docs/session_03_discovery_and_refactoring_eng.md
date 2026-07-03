# Session 03 — Requirements Discovery & Test-Driven Refactoring
## Civic Tech Moncton 506 — Study Notes

**Date:** 2026-07-02  
**Project:** civictech-506  
**Goal:** Complete the Application Lifecycle spec with real business rules, align the validation module with the organization's real Registration Form, and execute a full test-driven refactor.

---

## PART 1 — Requirements Discovery (the FDE skill in action)

This session was mostly about **discovery**: extracting real business rules that were not visible in the original diagrams. This is the core consulting skill of a Forward Deployed Engineer.

### Rules discovered this session

**1. The admin review is a verification checklist, not a simple button.**
The admin physically verifies three items against the data the member entered:
- `volunteer_id` → verifies first/last name
- `photograph` → verifies identity
- `home_address` → verifies the address field

Documents are NOT uploaded — the member presents them in person; the system only records the verification facts (who verified, what, when).

**2. The checklist BLOCKS approval.**
The system must reject an approval attempt if any checklist item is unverified. Rejection, however, does NOT require a complete checklist — an admin can reject at any point (asymmetry by design).

**3. Rejection reason is auto-generated.**
If checklist items are unverified at rejection time, the system generates the reason automatically (e.g., "unverified: photograph, home_address"). The admin may add optional notes.

**4. Duplicate applications were a real operational problem.**
Members created multiple enrollment applications when they mistyped their name. Mitigation: duplicate prevention **by email** — but state-aware:
- Active application exists (`SUBMITTED`/`VALIDATION_FAILED`/`STORED`) → block
- `APPROVED` exists → block with "already enrolled" message
- Only `REJECTED` exists → allow (consistent with re-application rule)

**Known limitation documented:** if the member mistypes the EMAIL itself, this check cannot detect the duplicate. Accepted risk for v1. *Lesson: declaring what the system does NOT cover is a mark of a professional spec.*

**5. The real Registration Form is simpler than the proposed one.**
Real fields (all REQUIRED): `first_name`, `last_name`, `email`, `phone`, `address`.
The fields `skills`, `availability_hours_per_week`, `experience_level`, `motivation`, `linkedin_or_github` belong to the **Onboarding** process, not Enrollment.

**6. Approval triggers a chain of effects (handoff to Onboarding).**
On `APPROVED`: send approval email → create user account → enable basic access → send welcome email inviting to the onboarding portal.
Design decision: **business decisions are not reversed by technical failures** — if account creation fails, the application stays `APPROVED` and the failure is logged for manual resolution.

### Key architectural insight

Stateless vs stateful validation:

| | Stateless (validation.py) | Stateful (service layer) |
|---|---|---|
| Looks at | Only the form payload | Existing data (DB) |
| Example | "is email well-formed?" | "does this email already have an application?" |
| Lives in | Spec 01 / validation.py | Spec 02 / service.py (future) |

Duplicate prevention is stateful → it belongs to the service layer, NOT to the pure validation module. This preserves the "No DB. No side effects." contract of validation.py.

---

## PART 2 — Spec versioning with a changelog

When requirements change, the spec gets a **new version with a changelog** — the history of the decision stays visible:

```markdown
## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-06-30 | Initial draft with proposed fields |
| 2.0 | 2026-07-02 | Aligned with the real organizational Registration Form: ... |
```

The changelog answers the future question "why did this change?" without archaeology through Git history.

---

## PART 3 — Test-Driven Refactoring (the main technique of this session)

### The counterintuitive order

When the spec changes, the refactor follows this order:

```
1. Update the SPEC        (the contract changes first)
2. Update the TESTS       (tests now encode the new contract)
3. Run pytest             (RED — massive failures, and that's CORRECT)
4. Refactor the CODE      (guided by the red tests)
5. Run pytest             (GREEN — refactor complete and verified)
```

**Why tests before code:** the red tests become an exact map of the work. Each FAILED tells you precisely what the code doesn't do yet. When everything is green, you have PROOF the refactor is complete — not a feeling, a verification.

### Our numbers this session

```
After updating tests:  22 failed, 5 passed   ← the map
After refactoring:     27 passed              ← the proof
```

**Revealing detail:** the 5 tests that survived the red phase were the `email` tests (unchanged between v1/v2) and `phone_invalid_format` (same error message in both versions). Tests tell you what survives a spec change with surgical precision.

### The refactor map (what changed in validation.py)

```
DELETED:   validate_full_name, validate_skills, validate_availability,
           validate_experience_level, validate_motivation,
           validate_linkedin_or_github
           + constants VALID_SKILLS, VALID_EXPERIENCE_LEVELS (dead code)

CREATED:   validate_first_name, validate_last_name, validate_address

MODIFIED:  validate_phone (optional → required)

UNTOUCHED: validate_email, ValidationResult, imports

UPDATED:   validate_registration_form (orchestrator with the 5 real fields)
```

### The optional → required pattern change

This was the conceptual change in `validate_phone`:

```python
# v1 — OPTIONAL field: absence is fine, exit silently
def validate_phone(phone, errors):
    if not phone or not phone.strip():
        return                    # ← no error, just exit

# v2 — REQUIRED field: absence IS an error
def validate_phone(phone, errors):
    if not phone or not phone.strip():
        errors.append("phone is required")   # ← the one-line difference
        return
```

### Dead code must die

After deleting the functions that used `VALID_SKILLS` and `VALID_EXPERIENCE_LEVELS`, the constants became dead code. Dead code is debt: the next reader will search for where it's used and find nothing. Deleting it is part of the refactor, not an optional cleanup.

---

## PART 4 — Design decisions worth remembering

**1. Minimum 2 characters for names (not 3).**
Real surnames like "Li", "Ng", "Wu" exist. Validation rules must accommodate real-world data, not idealized data.

**2. Same Application entity through the correction loop.**
The correction loop reuses the same Application transitioning back to `SUBMITTED` — not a new Application per attempt. Traceability comes from a **transition history table**, not entity duplication:

```
ApplicationStatusTransition
├── application_id
├── from_status / to_status
├── timestamp
├── triggered_by  (member | system | admin)
└── notes
```

**3. Freeze data during review.**
A member cannot modify an application in `STORED` — the admin must not evaluate a moving target.

**4. Terminal states are immutable.**
`APPROVED` and `REJECTED` reject all transitions. Re-application after rejection = NEW application; the rejected one stays closed for audit.

---

## PART 5 — Zsh environment note

After switching from bash to Zsh, `uv` disappeared (`command not found`). Cause: the installer added `uv` to bash's PATH (`~/.bashrc`), but Zsh reads `~/.zshrc`.

Fix (permanent):
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

*Lesson: when switching shells, PATH customizations must be migrated. Each shell has its own config file.*

---

## PART 6 — Current project state

```
Spec 01 v2.0 ✅ → validation.py v2 ✅ → 27 tests ✅  (merged via PR)
Spec 02 v1.0 ✅ → enums.py + models.py ⬜  ← NEXT SESSION
```

**Pending check:** verify on GitHub that the spec 02 PR was actually merged to dev (an old PR may still be open — the Pull Requests tab showed 1 open).

### Next session preview
- `enums.py` — `ApplicationStatus` using Python's `Enum`/`StrEnum` (new concept, maps to C# `enum` with extras)
- `models.py` — the `Application` state machine implementing the transition matrix from spec 02 section 5
- `tests/enrollment/test_application_lifecycle.py`

---

*Document generated: 2026-07-02 | civictech-506 | Session 03*
