"""
Enrollment Enums
Spec: specs/enrollment/02_application_lifecycle.md (v1.0)

Application lifecycle states and related enumerations.
"""

from enum import StrEnum

class ApplicationStatus(StrEnum):
    """Lifecycle states of an enrollment Application.
    APPROVED and REJECTED are terminal states (spec 02, section 3.4).
    """

    SUBMITTED = "SUBMITTED"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    STORED = "STORED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class TransitionActor(StrEnum):
    """Actors that can trigger a transition in the Application lifecycle.
    Spec 02, section 4.
    """

    MEMBER = "member"
    SYSTEM = "system"
    ADMIN = "admin"