"""Pydantic models for the internal case router lifecycle."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

RedactionPolicy = Literal["standard", "strict"]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ProductLine(str, Enum):
    TRIALMASTER = "TrialMaster"
    IRMS_MAX = "IRMS MAX"
    TA_SCAN = "TA Scan"
    MULTIPLE = "Multiple / Cross-product"
    UNKNOWN = "Unknown"


class IssueType(str, Enum):
    BUG = "bug"
    CONFIGURATION = "configuration_request"
    TRAINING = "training"
    MIGRATION = "migration"
    DATA_QUESTION = "data_question"
    IMPLEMENTATION = "implementation"
    COMPLIANCE = "compliance"
    OTHER = "other"


class Urgency(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CaseStatus(str, Enum):
    INTAKE = "intake"
    CLASSIFYING = "classifying"
    RETRIEVING = "retrieving"
    ROUTING = "routing"
    PLANNING = "planning"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"


class ActionType(str, Enum):
    JIRA_ISSUE = "create_jira_issue"
    TEAMS_NOTIFICATION = "send_teams_notification"
    SALESFORCE_ACTIVITY = "salesforce_activity"
    NETSUITE_TIME_OR_PROJECT = "netsuite_project_note"
    BAMBOOHR_TASK = "bamboohr_onboarding_task"
    IMPLEMENTATION_CHECKLIST = "implementation_checklist"


class CaseIntake(BaseModel):
    """Raw request from a channel (email, portal, Teams, etc.)."""

    request_text: str = Field(..., min_length=10, max_length=50_000)
    source_channel: str = Field(default="demo_ui", max_length=200)
    submitter_name: str | None = Field(default=None, max_length=200)
    submitter_email: str | None = Field(default=None, max_length=320)
    external_reference: str | None = Field(default=None, max_length=500)
    redact_pii: bool = Field(
        default=False,
        description="If true, mask emails/phones in text sent to LLM/embeddings (demo).",
    )
    redaction_policy: RedactionPolicy = Field(
        default="standard",
        description="standard: email/phone; strict: also trial/site-style tokens (demo).",
    )

    @field_validator("request_text")
    @classmethod
    def strip_text(cls, v: str) -> str:
        t = v.strip()
        if len(t) < 10:
            raise ValueError("request_text must be at least 10 characters after trim")
        return t


class Classification(BaseModel):
    """Structured output from the classification agent."""

    product: ProductLine
    issue_type: IssueType
    urgency: Urgency
    sentiment: str = Field(..., max_length=32)
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str = Field(..., max_length=8_000)
    keywords: list[str] = Field(default_factory=list, max_length=50)


class RoutingDecision(BaseModel):
    """Target team and SLA from the routing agent."""

    target_team: str = Field(..., max_length=200)
    queue_name: str = Field(..., max_length=200)
    priority_label: str = Field(..., max_length=64)
    sla_hours: int = Field(..., ge=1, le=720)
    escalation_recommended: bool = False
    reasoning: str = Field(..., max_length=8_000)


class ProposedAction(BaseModel):
    """A single downstream action (maps to AnjuBUS-style adapters in production)."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    action_type: ActionType
    target_system: str = Field(..., max_length=120)
    title: str = Field(..., max_length=500)
    payload: dict[str, Any] = Field(default_factory=dict)
    reasoning: str = Field(..., max_length=8_000)
    requires_approval: bool = True


class AuditEntry(BaseModel):
    """Immutable audit record for compliance-style traceability."""

    step: str = Field(..., max_length=120)
    detail: str = Field(..., max_length=16_000)
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=utc_now)


class ApprovalDecision(BaseModel):
    """Human decision on a proposed action."""

    action_id: str
    decision: Literal["approved", "modified", "rejected"]
    reviewer: str = Field(default="demo_reviewer", max_length=200)
    notes: str | None = Field(default=None, max_length=4_000)
    modified_payload: dict[str, Any] | None = None
    decided_at: datetime = Field(default_factory=utc_now)


class CaseRecord(BaseModel):
    """Full case persisted for UI and analytics."""

    case_id: str = Field(default_factory=lambda: str(uuid4()))
    status: CaseStatus = CaseStatus.INTAKE
    intake: CaseIntake
    #: When set, LLM/RAG use this instead of intake.request_text (data minimization).
    redacted_request_text: str | None = None
    classification: Classification | None = None
    rag_context: list[dict[str, Any]] = Field(default_factory=list)
    routing: RoutingDecision | None = None
    proposed_actions: list[ProposedAction] = Field(default_factory=list)
    approvals: list[ApprovalDecision] = Field(default_factory=list)
    execution_results: list[dict[str, Any]] = Field(default_factory=list)
    audit_trail: list[AuditEntry] = Field(default_factory=list)
    error_message: str | None = None
    #: Policy / operator controls (demo)
    restricted_mode: bool = False
    restricted_signals: list[str] = Field(default_factory=list)
    llm_allowed: bool = True
    rag_skipped: bool | None = None
    rag_influence_summary: str | None = None
    risk_tier: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    def append_audit(self, step: str, detail: str, **meta: Any) -> None:
        self.audit_trail.append(AuditEntry(step=step, detail=detail, metadata=meta))
        self.updated_at = utc_now()

    def text_for_llm(self) -> str:
        """Text passed to models and embedding queries; may be redacted."""
        if self.redacted_request_text is not None:
            return self.redacted_request_text
        return self.intake.request_text
