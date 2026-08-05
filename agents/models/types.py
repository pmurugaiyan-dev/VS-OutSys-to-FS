"""Type definitions for migration agents."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class MigrationStatus(Enum):
    """Status of migration or component."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ModuleState:
    """State of a single module during migration."""
    name: str
    status: MigrationStatus = MigrationStatus.PENDING
    extraction_status: MigrationStatus = MigrationStatus.PENDING
    generation_status: MigrationStatus = MigrationStatus.PENDING
    validation_status: MigrationStatus = MigrationStatus.PENDING
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    artifacts: Dict[str, str] = field(default_factory=dict)


@dataclass
class MigrationState:
    """Overall state of the migration process."""
    migration_id: str
    source_path: str
    output_path: str
    target_namespace: str = "MyApp"
    status: MigrationStatus = MigrationStatus.PENDING
    current_phase: str = "initialization"
    modules: List[ModuleState] = field(default_factory=list)
    migration_order: List[str] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParsedModule:
    """Parsed OutSystems module data."""
    module_name: str
    module_type: str
    entities: List[Dict] = field(default_factory=list)
    static_entities: List[Dict] = field(default_factory=list)
    relationships: List[Dict] = field(default_factory=list)
    indexes: List[Dict] = field(default_factory=list)
    structures: List[Dict] = field(default_factory=list)
    server_actions: List[Dict] = field(default_factory=list)
    client_actions: List[Dict] = field(default_factory=list)
    aggregates: List[Dict] = field(default_factory=list)
    screens: List[Dict] = field(default_factory=list)
    web_blocks: List[Dict] = field(default_factory=list)
    rest_consumes: List[Dict] = field(default_factory=list)
    rest_exposes: List[Dict] = field(default_factory=list)
    timers: List[Dict] = field(default_factory=list)
    processes: List[Dict] = field(default_factory=list)
    roles: List[Dict] = field(default_factory=list)
    site_properties: List[Dict] = field(default_factory=list)
    resources: List[Dict] = field(default_factory=list)
    extensions: List[Dict] = field(default_factory=list)
    dependencies: List[Dict] = field(default_factory=list)


@dataclass
class AnalysisResult:
    """Result from the Analyzer Agent."""
    modules: List[str]
    complexity_scores: Dict[str, float]
    total_complexity: float
    complexity_level: str
    migration_order: List[str]
    dependency_graph: Dict[str, List[str]]
    risk_assessment: List[Dict]
    statistics: Dict[str, int]


@dataclass
class BuildResult:
    """Result from compilation."""
    success: bool
    output: str = ""
    errors: List[Dict] = field(default_factory=list)
    warnings: List[Dict] = field(default_factory=list)


@dataclass
class TestResult:
    """Result from test execution."""
    success: bool
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    output: str = ""


@dataclass
class ValidationResult:
    """Result from migration validation."""
    is_complete: bool
    entities: Dict[str, Any] = field(default_factory=dict)
    services: Dict[str, Any] = field(default_factory=dict)
    screens: Dict[str, Any] = field(default_factory=dict)
    integrations: Dict[str, Any] = field(default_factory=dict)
    missing_components: List[str] = field(default_factory=list)
