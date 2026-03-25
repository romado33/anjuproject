"""Configure adapter endpoints and parameters (persisted JSON; execution remains mock until wired)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from app.ui_theme import inject_theme, page_config, render_luminee_sidebar_promo
from config.integration_settings_store import (
    ADAPTER_DEFINITIONS,
    AdapterConfig,
    IntegrationSettingsFile,
    load_integration_settings,
    save_integration_settings,
)
from config.logging_config import configure_logging
from config.settings import get_settings

configure_logging(get_settings().log_level)
page_config("Integrations")
inject_theme()
render_luminee_sidebar_promo()

settings = get_settings()
store_path = settings.integration_settings_full_path()


def _params_json_valid(text: str) -> tuple[bool, dict[str, str] | None, str]:
    raw = text.strip() or "{}"
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return False, None, str(exc)
    if not isinstance(data, dict):
        return False, None, "Parameters must be a JSON object (key/value pairs)."
    out: dict[str, str] = {}
    for k, v in data.items():
        if not isinstance(k, str):
            return False, None, "All parameter keys must be strings."
        if not isinstance(v, str):
            return False, None, f"Value for {k!r} must be a string (use quotes in JSON)."
        out[k] = v
    return True, out, ""


st.title("Integrations")
st.caption(
    "Define **base URLs** and **parameters** for each downstream adapter. "
    "This app still runs **mock** executions; production wiring would read this file via `Settings`."
)

st.info(
    f"Settings file: `{store_path}` (from **INTEGRATION_SETTINGS_PATH** or default). "
    "Do not commit real secrets—use environment-specific files or a secret store in production."
)

loaded = load_integration_settings(store_path)

with st.form("integration_settings_form"):
    st.markdown("### Adapter configuration")
    for defn in ADAPTER_DEFINITIONS:
        cfg = loaded.adapters.get(defn.adapter_id) or AdapterConfig()
        with st.expander(f"{defn.title} (`{defn.adapter_id}`)", expanded=False):
            st.caption(defn.description)
            st.checkbox(
                "Enabled for routing / execution",
                value=cfg.enabled,
                key=f"integ_en_{defn.adapter_id}",
            )
            st.text_input(
                "Base URL",
                value=cfg.base_url,
                placeholder="https://your-instance.example.com/...",
                key=f"integ_base_{defn.adapter_id}",
                help="REST or webhook root; no credentials here—use parameters or a vault.",
            )
            params_default = json.dumps(cfg.parameters, indent=2) if cfg.parameters else "{}"
            params_txt = st.text_area(
                "Parameters (JSON object of string values)",
                value=params_default,
                height=120,
                key=f"integ_params_{defn.adapter_id}",
                help="Examples: API version, project key, channel id — as quoted strings.",
            )
            st.text_area(
                "Notes (internal)",
                value=cfg.notes,
                height=68,
                key=f"integ_notes_{defn.adapter_id}",
            )
            ok, _, err = _params_json_valid(params_txt)
            if not ok:
                st.error(f"Invalid parameters JSON: {err}")

    save = st.form_submit_button("Save integration settings", type="primary", use_container_width=True)

if save:
    # Re-read form: on submit, collected may still hold old cfg if validation failed — rebuild from session state
    adapters_out: dict[str, AdapterConfig] = {}
    valid = True
    for defn in ADAPTER_DEFINITIONS:
        en = st.session_state.get(f"integ_en_{defn.adapter_id}", False)
        base = str(st.session_state.get(f"integ_base_{defn.adapter_id}", "")).strip()
        params_txt = str(st.session_state.get(f"integ_params_{defn.adapter_id}", "{}"))
        notes = str(st.session_state.get(f"integ_notes_{defn.adapter_id}", "")).strip()
        ok, parsed, err = _params_json_valid(params_txt)
        if not ok:
            st.error(f"{defn.title}: invalid parameters JSON — {err}")
            valid = False
            continue
        adapters_out[defn.adapter_id] = AdapterConfig(
            base_url=base,
            enabled=bool(en),
            parameters=parsed or {},
            notes=notes,
        )
    if valid:
        doc = IntegrationSettingsFile(version=1, adapters=adapters_out)
        try:
            save_integration_settings(store_path, doc)
        except OSError as exc:
            st.error(f"Could not write settings file: {exc}")
        else:
            for defn in ADAPTER_DEFINITIONS:
                for prefix in ("integ_en_", "integ_base_", "integ_params_", "integ_notes_"):
                    k = f"{prefix}{defn.adapter_id}"
                    if k in st.session_state:
                        del st.session_state[k]
            st.success("Saved integration settings.")
            st.rerun()

with st.expander("Example parameters JSON", expanded=False):
    st.code(
        """{
  "api_version": "v1",
  "project_key": "OPS",
  "webhook_secret_env": "TEAMS_WEBHOOK_URL"
}""",
        language="json",
    )
    st.caption("Store secret *names* in parameters; resolve real secrets from your environment or vault at runtime.")
