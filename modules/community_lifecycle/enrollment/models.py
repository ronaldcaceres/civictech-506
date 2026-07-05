"""
Enrollment Domain Models
Spec: specs/enrollment/02_application_lifecycle.md (v1.0)

Application entity with state machine transition logic.
The model protects its own invariants: state changes only
through transition_to(), which enforces the allowed matrix.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from modules.community_lifecycle.enrollment.enums import (
    ApplicationStatus,
    TransitionActor,
)


class InvalidTransitionError(Exception):
    """Raised when an Application transition violates the allowed matrix (spec 02, 3.6)."""


ALLOWED_TRANSITIONS: dict[ApplicationStatus, set[ApplicationStatus]] = {
    ApplicationStatus.SUBMITTED: {
        ApplicationStatus.VALIDATION_FAILED,
        ApplicationStatus.STORED,
    },
    ApplicationStatus.VALIDATION_FAILED: {ApplicationStatus.SUBMITTED},
    ApplicationStatus.STORED: {ApplicationStatus.APPROVED, ApplicationStatus.REJECTED},
    ApplicationStatus.APPROVED: set(),
    ApplicationStatus.REJECTED: set(),
}


@dataclass
class StatusTransition:
    """One recorded state change (spec 02, section 4)."""

    from_status: ApplicationStatus
    to_status: ApplicationStatus
    triggered_by: TransitionActor
    timestamp: datetime
    notes: str | None = None


@dataclass
class Application:
    """Enrollment application with protected state machine."""

    form_data: dict
    status: ApplicationStatus = ApplicationStatus.SUBMITTED
    history: list[StatusTransition] = field(default_factory=list)

    def can_transition_to(self, target: ApplicationStatus) -> bool:
        return target in ALLOWED_TRANSITIONS[self.status]

    def transition_to(
        self,
        target: ApplicationStatus,
        actor: TransitionActor,
        notes: str | None = None,
    ) -> None:
        if not self.can_transition_to(target):
            raise InvalidTransitionError(
                f"invalid transition from {self.status} to {target}"
            )
        transition = StatusTransition(
            from_status=self.status,
            to_status=target,
            triggered_by=actor,
            timestamp=datetime.now(timezone.utc),
            notes=notes,
        )
        self.history.append(transition)
        self.status = target
