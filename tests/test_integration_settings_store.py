"""Round-trip tests for integration settings JSON."""

from __future__ import annotations

import json
from pathlib import Path

from config.integration_settings_store import (
    AdapterConfig,
    IntegrationSettingsFile,
    default_settings_file,
    load_integration_settings,
    save_integration_settings,
)


def test_default_settings_has_all_adapters() -> None:
    d = default_settings_file()
    assert len(d.adapters) == 6
    assert all(not c.enabled for c in d.adapters.values())


def test_save_load_roundtrip(tmp_path: Path) -> None:
    p = tmp_path / "integration_settings.json"
    merged = dict(default_settings_file().adapters)
    merged["jira"] = AdapterConfig(
        base_url="https://example.atlassian.net",
        enabled=True,
        parameters={"project_key": "OPS"},
        notes="demo",
    )
    save_integration_settings(p, IntegrationSettingsFile(version=1, adapters=merged))

    loaded = load_integration_settings(p)
    jira = loaded.adapters["jira"]
    assert jira.base_url == "https://example.atlassian.net"
    assert jira.enabled is True
    assert jira.parameters == {"project_key": "OPS"}
    assert jira.notes == "demo"


def test_load_merges_partial_file(tmp_path: Path) -> None:
    p = tmp_path / "integration_settings.json"
    p.write_text(
        json.dumps(
            {
                "version": 1,
                "adapters": {
                    "teams": {
                        "base_url": "https://hooks.example.com",
                        "enabled": True,
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    loaded = load_integration_settings(p)
    assert loaded.adapters["teams"].base_url == "https://hooks.example.com"
    assert loaded.adapters["teams"].enabled is True
    assert loaded.adapters["jira"].enabled is False
