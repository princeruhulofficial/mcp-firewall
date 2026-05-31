"""Core data models for mcp-firewall."""

from __future__ import annotations

import time
import uuid
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Action(str, Enum):
    """Policy decision actions."""

    ALLOW = "allow"
    DENY = "deny"
    REDACT = "redact"
    PROMPT = "prompt"  # ask human
    ALERT = "alert"  # allow but alert
    ISSUE_CAPABILITY = "issue_capability"  # mint a scoped, short-lived access grant
    ESCALATE = "escalate"  # route to an external approval workflow
    SANDBOX = "sandbox"  # allow only in an isolated execution environment


class Severity(str, Enum):
    """Alert/finding severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

    @property
    def rank(self) -> int:
        return {"critical": 5, "high": 4, "medium": 3, "low": 2, "info": 1}[self.value]

    def __ge__(self, other: "Severity") -> bool:  # type: ignore[override]
        return self.rank >= other.rank

    def __gt__(self, other: "Severity") -> bool:  # type: ignore[override]
        return self.rank > other.rank

    def __le__(self, other: "Severity") -> bool:  # type: ignore[override]
        return self.rank <= other.rank

    def __lt__(self, other: "Severity") -> bool:  # type: ignore[override]
        return self.rank < other.rank


class PipelineStage(str, Enum):
    """Pipeline stage identifiers."""

    KILL_SWITCH = "kill_switch"
    AGENT_IDENTITY = "agent_identity"
    RATE_LIMITER = "rate_limiter"
    INJECTION = "injection"
    EGRESS = "egress"
    POLICY = "policy"
    CHAIN_DETECTOR = "chain_detector"
    HUMAN_APPROVAL = "human_approval"
    SECRET_SCANNER = "secret_scanner"
    PII_DETECTOR = "pii_detector"
    EXFIL_DETECTOR = "exfil_detector"
    CONTENT_POLICY = "content_policy"


class ToolCallRequest(BaseModel):
    """Represents an incoming MCP tool call request."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    agent_id: str = "unknown"
    timestamp: float = Field(default_factory=time.time)


class ToolCallResponse(BaseModel):
    """Represents an MCP tool call response."""

    request_id: str
    content: list[dict[str, Any]] = Field(default_factory=list)
    is_error: bool = False
    timestamp: float = Field(default_factory=time.time)


class PipelineDecision(BaseModel):
    """Result of a pipeline stage evaluation."""

    stage: PipelineStage
    action: Action
    reason: str = ""
    severity: Severity = Severity.INFO
    details: dict[str, Any] = Field(default_factory=dict)


class RiskAssessment(BaseModel):
    """Risk score attached to an AI action before execution.

    This is the first platform-level primitive for a Zero Trust AI Execution
    Layer: every requested action can be scored before a capability is issued
    or a human approval flow is triggered.
    """

    score: int = Field(default=0, ge=0, le=100)
    severity: Severity = Severity.INFO
    factors: list[str] = Field(default_factory=list)
    requires_approval: bool = False

    @classmethod
    def from_score(cls, score: int, factors: list[str] | None = None) -> RiskAssessment:
        """Create a risk assessment using the default score-to-severity bands."""
        if score >= 90:
            severity = Severity.CRITICAL
        elif score >= 70:
            severity = Severity.HIGH
        elif score >= 40:
            severity = Severity.MEDIUM
        elif score >= 10:
            severity = Severity.LOW
        else:
            severity = Severity.INFO

        return cls(
            score=score,
            severity=severity,
            factors=factors or [],
            requires_approval=score >= 70,
        )


class CapabilityStatus(str, Enum):
    """Lifecycle state for a one-time execution capability."""

    ACTIVE = "active"
    CONSUMED = "consumed"
    REVOKED = "revoked"
    EXPIRED = "expired"


class CapabilityGrant(BaseModel):
    """Short-lived, scoped access grant for one AI action.

    The runtime can issue this after policy and risk evaluation. A tool runner
    should consume it exactly once, or revoke it when the action is cancelled.
    """

    id: str = Field(default_factory=lambda: f"cap_{uuid.uuid4().hex}")
    agent_id: str
    tool_name: str
    scopes: list[str] = Field(default_factory=list)
    resource_constraints: dict[str, Any] = Field(default_factory=dict)
    issued_at: float = Field(default_factory=time.time)
    expires_at: float = Field(default_factory=lambda: time.time() + 60)
    single_use: bool = True
    status: CapabilityStatus = CapabilityStatus.ACTIVE

    @property
    def expired(self) -> bool:
        """Return true when the capability is past its expiry time."""
        return time.time() >= self.expires_at

    @property
    def usable(self) -> bool:
        """Return true when the capability can still authorize execution."""
        return self.status == CapabilityStatus.ACTIVE and not self.expired

    def consume(self) -> None:
        """Mark a single-use capability as consumed after successful execution."""
        if self.single_use:
            self.status = CapabilityStatus.CONSUMED

    def revoke(self) -> None:
        """Revoke this capability before it is used."""
        self.status = CapabilityStatus.REVOKED


class ContextScope(str, Enum):
    """Universal Context Protocol state scopes.

    UCP expands the project beyond MCP tool calls by standardizing the context
    carried across models, agents, tools, applications, and user data.
    """

    USER = "user"
    TASK = "task"
    MEMORY = "memory"
    TOOL = "tool"
    ENVIRONMENT = "environment"
    SESSION = "session"
    AGENT = "agent"


class ActionPhase(str, Enum):
    """Standardized UCP action lifecycle phases."""

    READ_CONTEXT = "read_context"
    PROPOSE_ACTION = "propose_action"
    VALIDATE_ACTION = "validate_action"
    EXECUTE_ACTION = "execute_action"
    COMPLETE_ACTION = "complete_action"


class ContextRecord(BaseModel):
    """A portable context item for a UCP envelope.

    Each record has a scope, subject, structured data, optional sensitivity,
    and optional expiry so context can move across AI systems safely.
    """

    id: str = Field(default_factory=lambda: f"ctx_{uuid.uuid4().hex}")
    scope: ContextScope
    subject_id: str = ""
    data: dict[str, Any] = Field(default_factory=dict)
    version: int = 1
    sensitivity: Severity = Severity.INFO
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    expires_at: float | None = None

    @property
    def expired(self) -> bool:
        """Return true when the context record is past its expiry time."""
        return self.expires_at is not None and time.time() >= self.expires_at


class UCPEnvelope(BaseModel):
    """Universal Context Protocol envelope for one AI action.

    The envelope packages context state, proposed action, risk, policy decisions,
    and capability grants into one standard structure that is not limited to MCP.
    """

    protocol: str = "ucp"
    version: int = 1
    id: str = Field(default_factory=lambda: f"ucp_{uuid.uuid4().hex}")
    phase: ActionPhase = ActionPhase.PROPOSE_ACTION
    session_id: str = Field(default_factory=lambda: f"sess_{uuid.uuid4().hex}")
    user_id: str = ""
    agent_id: str = ""
    model_id: str = ""
    contexts: list[ContextRecord] = Field(default_factory=list)
    proposed_action: ToolCallRequest | None = None
    risk: RiskAssessment | None = None
    decisions: list[PipelineDecision] = Field(default_factory=list)
    capability: CapabilityGrant | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: float = Field(default_factory=time.time)

    def active_contexts(self, scope: ContextScope | None = None) -> list[ContextRecord]:
        """Return non-expired contexts, optionally filtered by scope."""
        records = [record for record in self.contexts if not record.expired]
        if scope is None:
            return records
        return [record for record in records if record.scope == scope]

    def add_context(self, record: ContextRecord) -> None:
        """Append a context record to the envelope."""
        self.contexts.append(record)


class AuditEvent(BaseModel):
    """Immutable audit log entry."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = Field(default_factory=time.time)
    agent_id: str = "unknown"
    tool_name: str = ""
    arguments_hash: str = ""  # SHA-256 of arguments (not raw for privacy)
    decision: Action = Action.ALLOW
    stage: PipelineStage | None = None
    reason: str = ""
    severity: Severity = Severity.INFO
    latency_ms: float = 0.0
    previous_hash: str = ""  # hash chain


class GatewayConfig(BaseModel):
    """Top-level gateway configuration."""

    version: int = 1
    default_action: Action = Action.PROMPT
    kill_switch: KillSwitchConfig = Field(default_factory=lambda: KillSwitchConfig())
    rate_limit: RateLimitConfig = Field(default_factory=lambda: RateLimitConfig())
    injection: InjectionConfig = Field(default_factory=lambda: InjectionConfig())
    egress: EgressConfig = Field(default_factory=lambda: EgressConfig())
    secrets: SecretScanConfig = Field(default_factory=lambda: SecretScanConfig())
    pii: PIIConfig = Field(default_factory=lambda: PIIConfig())
    agents: dict[str, AgentConfig] = Field(default_factory=dict)
    rules: list[RuleConfig] = Field(default_factory=list)
    audit: AuditConfig = Field(default_factory=lambda: AuditConfig())


class KillSwitchConfig(BaseModel):
    """Kill switch configuration."""

    enabled: bool = True
    file_path: str = ".mcp-firewall-kill"


class RateLimitConfig(BaseModel):
    """Global rate limit configuration."""

    enabled: bool = True
    max_calls: int = 200
    window_seconds: int = 60


class InjectionConfig(BaseModel):
    """Injection detection configuration."""

    enabled: bool = True
    sensitivity: str = "medium"  # low, medium, high


class EgressConfig(BaseModel):
    """Egress control configuration."""

    enabled: bool = True
    block_private_ips: bool = True
    block_cloud_metadata: bool = True


class SecretScanConfig(BaseModel):
    """Secret scanning configuration."""

    enabled: bool = True
    action: Action = Action.REDACT


class PIIConfig(BaseModel):
    """PII detection configuration."""

    enabled: bool = False  # off by default
    action: Action = Action.REDACT


class AgentConfig(BaseModel):
    """Per-agent RBAC configuration."""

    allow: list[str] = Field(default_factory=list)
    deny: list[str] = Field(default_factory=list)
    rate_limit: str | None = None  # e.g. "100/min"
    require_approval: list[str] = Field(default_factory=list)


class RuleConfig(BaseModel):
    """Individual policy rule."""

    name: str
    tool: str = "*"
    match: dict[str, Any] = Field(default_factory=dict)
    action: Action = Action.DENY
    message: str = ""
    rate_limit: dict[str, int] | None = None


class AuditConfig(BaseModel):
    """Audit logging configuration."""

    enabled: bool = True
    path: str = "mcp-firewall.audit.jsonl"
    sign: bool = False  # Ed25519 signing (Phase 4)
    max_size_mb: int = 100
