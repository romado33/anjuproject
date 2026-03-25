"""Load/save per-adapter endpoint configuration for the Integrations UI (JSON on disk)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Final

from pydantic import BaseModel, Field, ValidationError

# Stable ids aligned with src/integrations/registry.py mock adapters
ADAPTER_IDS: Final[tuple[str, ...]] = (
    "jira",
    "teams",
    "salesforce",
    "netsuite",
    "bamboohr",
    "wiki",
)


class AdapterDefinition(BaseModel):
    """Static metadata for the Integrations screen (not persisted)."""

    adapter_id: str
    title: str
    description: str


ADAPTER_DEFINITIONS: tuple[AdapterDefinition, ...] = (
    AdapterDefinition(
        adapter_id="jira",
        title="Jira Cloud",
        description="Issues, projects, service desk (REST base URL).",
    ),
    AdapterDefinition(
        adapter_id="teams",
        title="Microsoft Teams",
        description="Channel webhooks or Graph API base URL.",
    ),
    AdapterDefinition(
        adapter_id="salesforce",
        title="Salesforce / Veeva CRM",
        description="API version URL or My Domain host.",
    ),
    AdapterDefinition(
        adapter_id="netsuite",
        title="NetSuite",
        description="Account-specific REST or SuiteTalk endpoint.",
    ),
    AdapterDefinition(
        adapter_id="bamboohr",
        title="BambooHR",
        description="Subdomain or API base URL.",
    ),
    AdapterDefinition(
        adapter_id="wiki",
        title="Wiki / Confluence",
        description="Space or checklist API base URL.",
    ),
)


class AdapterConfig(BaseModel):
    """User-editable settings for one adapter."""

    base_url: str = Field(default="", max_length=2048)
    enabled: bool = False
    parameters: dict[str, str] = Field(default_factory=dict)
    notes: str = Field(default="", max_length=4000)


class IntegrationSettingsFile(BaseModel):
    """Persisted document for data/integration_settings.json."""

    version: int = 1
    adapters: dict[str, AdapterConfig] = Field(default_factory=dict)


def default_settings_file() -> IntegrationSettingsFile:
    return IntegrationSettingsFile(
        version=1,
        adapters={aid: AdapterConfig() for aid in ADAPTER_IDS},
    )


def load_integration_settings(path: Path) -> IntegrationSettingsFile:
    """Load from disk; merge with defaults so new adapter keys appear over time."""
    base = default_settings_file()
    if not path.exists():
        return base
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return base
    adapters_in = raw.get("adapters") or {}
    if not isinstance(adapters_in, dict):
        return base
    merged = dict(base.adapters)
    for key in ADAPTER_IDS:
        if key not in adapters_in:
            continue
        patch = adapters_in[key]
        if not isinstance(patch, dict):
            continue
        try:
            merged[key] = AdapterConfig.model_validate({**merged[key].model_dump(), **patch})
        except ValidationError:
            pass
    ver = raw.get("version", 1)
    try:
        version = int(ver)
    except (TypeError, ValueError):
        version = 1
    return IntegrationSettingsFile(version=version, adapters=merged)


def save_integration_settings(path: Path, data: IntegrationSettingsFile) -> None:
    """Atomic write; creates parent directories."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    text = data.model_dump_json(indent=2)
    tmp.write_text(text + "\n", encoding="utf-8")
    tmp.replace(path)
