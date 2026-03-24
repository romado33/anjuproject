"""Shared Streamlit styling for a minimal, professional UI."""

from __future__ import annotations

import streamlit as st


def inject_theme() -> None:
    st.markdown(
        """
        <style>
          .block-container { padding-top: 1rem; max-width: 1200px; }
          div[data-testid="stMetricValue"] { font-size: 1.35rem; }
          h1 { font-weight: 600; letter-spacing: -0.02em; }
          .stCaption { color: rgba(49,51,63,0.75); }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_config(title: str) -> None:
    """Wide layout, no decorative page icon (keeps sidebar professional)."""
    st.set_page_config(page_title=title, layout="wide", initial_sidebar_state="expanded")
