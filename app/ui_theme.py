"""Shared Streamlit styling for a minimal, professional UI."""

from __future__ import annotations

from typing import Literal

import streamlit as st

BreadcrumbStep = Literal["overview", "intake", "review"]

_BREADCRUMB: tuple[tuple[BreadcrumbStep, str, str], ...] = (
    ("overview", "Home.py", "Overview"),
    ("intake", "pages/1_Case_intake.py", "Case intake"),
    ("review", "pages/2_Review_case_actions.py", "Review case actions"),
)


def render_process_breadcrumb(*, current: BreadcrumbStep) -> None:
    """Case workflow only: overview → case intake → review actions (not reference docs)."""
    st.markdown(
        '<p class="demo-breadcrumb-label">Case workflow</p>',
        unsafe_allow_html=True,
    )
    n = len(_BREADCRUMB)
    weights = []
    for i in range(n):
        weights.append(1)
        if i < n - 1:
            weights.append(0.12)
    cols = st.columns(weights)
    col_idx = 0
    for i, (step_key, path, label) in enumerate(_BREADCRUMB):
        with cols[col_idx]:
            if step_key == current:
                st.markdown(
                    f'<span class="crumb-current">{label}</span>',
                    unsafe_allow_html=True,
                )
            else:
                try:
                    st.page_link(path, label=label, use_container_width=True)
                except Exception:
                    st.caption(label)
        col_idx += 1
        if i < n - 1:
            with cols[col_idx]:
                st.markdown('<span class="crumb-sep">›</span>', unsafe_allow_html=True)
            col_idx += 1


def render_policy_reference_nav() -> None:
    """Policy & privacy is reference material — separate from the case workflow breadcrumb."""
    st.markdown(
        '<p class="demo-reference-nav-label">Reference</p>',
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns([1, 2.2])
    with c1:
        try:
            st.page_link("Home.py", label="← Overview", use_container_width=True)
        except Exception:
            st.caption("Overview")
    with c2:
        st.caption(
            "**Policy & privacy** — architecture and compliance context. "
            "Open from the sidebar anytime; it is not part of the intake → review steps."
        )


def inject_theme() -> None:
    st.markdown(
        """
        <style>
          /* Extra top room so the first row (workflow nav) is not clipped by app chrome */
          .block-container {
            padding-top: 2.5rem !important;
            max-width: 1120px;
          }
          @media (max-width: 768px) {
            .block-container { padding-top: 2rem !important; }
          }
          section[data-testid="stMain"] > div {
            padding-top: 0.85rem;
          }
          div[data-testid="stMetricValue"] { font-size: 1.2rem; }
          h1 { font-weight: 650; letter-spacing: -0.02em; }
          .stCaption { color: rgba(49,51,63,0.75); }
          p.demo-breadcrumb-label,
          .demo-breadcrumb-label {
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #5C6470;
            margin: 0.35rem 0 8px 0 !important;
            padding-top: 0.25rem;
          }
          p.demo-reference-nav-label,
          .demo-reference-nav-label {
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #5C6470;
            margin: 0.35rem 0 8px 0 !important;
            padding-top: 0.25rem;
          }
          span.crumb-current {
            display: block;
            text-align: center;
            font-weight: 700;
            font-size: 0.92rem;
            color: #063845;
            background: #E8F4F6;
            border: 1px solid #0D6B7A;
            border-radius: 0.5rem;
            padding: 0.45rem 0.5rem;
          }
          span.crumb-sep {
            display: flex;
            align-items: center;
            justify-content: center;
            color: #9CA3AF;
            font-size: 1.1rem;
            padding-top: 0.35rem;
          }
          .demo-card {
            border: 1px solid #E7EAF1;
            border-radius: 12px;
            padding: 14px 16px;
            margin: 8px 0 14px 0;
            background: #FAFBFD;
          }
          .demo-kpi {
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: #5C6470;
            margin-bottom: 4px;
          }
          .demo-value {
            font-size: 1.05rem;
            font-weight: 600;
            color: #1F2633;
          }
          /* Solid primary buttons — label text stays white (nested p/span) */
          div[data-testid="stBaseButton-primary"] button {
            background-color: #0D6B7A !important;
            border: 1px solid #0A5A66 !important;
            color: #FFFFFF !important;
            font-weight: 600 !important;
          }
          div[data-testid="stBaseButton-primary"] button p,
          div[data-testid="stBaseButton-primary"] button span,
          div[data-testid="stBaseButton-primary"] button div {
            background: transparent !important;
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
          }
          div[data-testid="stBaseButton-primary"] button:hover {
            background-color: #0A5A66 !important;
            border-color: #084854 !important;
          }
          div[data-testid="stBaseButton-primary"] button:hover p,
          div[data-testid="stBaseButton-primary"] button:hover span {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
          }
          div[data-testid="stBaseButton-primary"] button:focus-visible {
            box-shadow: 0 0 0 2px #FFFFFF, 0 0 0 4px #0D6B7A !important;
          }
          /* Page navigation links: outlined / light fill for readable dark text */
          div[data-testid="stPageLink-NavLink"] a,
          div[data-testid="stPageLink"] a {
            background-color: #F0F9FA !important;
            border: 2px solid #0D6B7A !important;
            color: #063845 !important;
            font-weight: 600 !important;
            border-radius: 0.5rem;
            padding: 0.5rem 0.75rem !important;
            text-decoration: none !important;
            display: block;
            text-align: center;
          }
          div[data-testid="stPageLink-NavLink"] a p,
          div[data-testid="stPageLink"] a p,
          div[data-testid="stPageLink-NavLink"] a span,
          div[data-testid="stPageLink"] a span {
            color: #063845 !important;
            -webkit-text-fill-color: #063845 !important;
          }
          div[data-testid="stPageLink-NavLink"] a:hover,
          div[data-testid="stPageLink"] a:hover,
          div[data-testid="stPageLink-NavLink"] a:hover p,
          div[data-testid="stPageLink"] a:hover p,
          div[data-testid="stPageLink-NavLink"] a:hover span,
          div[data-testid="stPageLink"] a:hover span {
            background-color: #D8EFF2 !important;
            color: #052830 !important;
            -webkit-text-fill-color: #052830 !important;
            border-color: #0A5A66 !important;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_config(title: str) -> None:
    """Wide layout, no decorative page icon (keeps sidebar professional)."""
    st.set_page_config(page_title=title, layout="wide", initial_sidebar_state="expanded")
