"""Force deterministic offline mode for tests (ignore local .env keys)."""

from __future__ import annotations

import os

os.environ["OFFLINE_DEMO"] = "true"
os.environ["OPENAI_API_KEY"] = ""
