"""Shared Streamlit styling for a minimal, professional UI."""

from __future__ import annotations

from typing import Literal

import streamlit as st

BreadcrumbStep = Literal["overview", "intake", "review"]

_BREADCRUMB: tuple[tuple[BreadcrumbStep, str, str], ...] = (
    ("overview", "pages/0_Home.py", "Home"),
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
            st.page_link("pages/0_Home.py", label="← Home", use_container_width=True)
        except Exception:
            st.caption("Home")
    with c2:
        st.caption(
            "**Policy & privacy** — architecture and compliance context. "
            "Open from the sidebar anytime; it is not part of the intake → review steps."
        )


def render_luminee_sidebar_promo() -> None:
    """Anju Luminee + Protocol Summarizer (configurable URLs via settings / .env)."""
    from config.settings import get_settings

    s = get_settings()
    # Single markdown blocks reduce Streamlit sidebar vertical gaps vs many st.sidebar calls.
    # No leading "---": st.navigation already separates page links from custom sidebar content.
    st.sidebar.markdown(
        "### Luminee\n\n"
        "*Build trials in days, not months*\n\n"
        "Luminee is an **AI ecosystem** of virtual assistants that ingests protocols and "
        "auto-creates trial-ready databases, edit checks, and validation artifacts — cutting "
        "build time by up to **90%**."
    )
    st.sidebar.link_button(
        "Book a demo",
        s.luminee_book_demo_url,
        type="primary",
        use_container_width=True,
    )
    st.sidebar.markdown(
        "#### Introducing the Protocol Summarizer\n\n"
        "Designed with **clinical sites** in mind, the Protocol Summarizer transforms complex "
        "trial protocols into clear, site-focused summaries highlighting operational and "
        "patient-impact insights. **Reduce review burden. Improve alignment. Move faster.**\n\n"
        "Offered at **no cost** as a commitment to supporting the clinical trial ecosystem — "
        "available for self sign-up today. Try it **free** through the **Luminee Hub**."
    )
    st.sidebar.link_button(
        "Try the Free Protocol Summarizer",
        s.luminee_protocol_summarizer_url,
        type="primary",
        use_container_width=True,
    )


def inject_theme() -> None:
    st.markdown(
        """
        <style>
          /* Anju-aligned palette (navy wordmark, blue→violet gradient accent, cool surfaces) */
          :root {
            --anju-navy: #1B2A4A;
            --anju-navy-hover: #243A5C;
            --anju-navy-border: #141C33;
            --anju-royal: #2563EB;
            --anju-violet: #6D28D9;
            --anju-text-muted: #5C6578;
            --anju-surface: #FAFBFF;
            --anju-surface-tint: linear-gradient(135deg, #EEF2FF 0%, #F5F3FF 100%);
            --anju-border-soft: #D7DFEA;
          }

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
          div[data-testid="stMetricValue"] { font-size: 1.2rem; color: var(--anju-navy) !important; }
          h1 {
            font-weight: 650;
            letter-spacing: -0.02em;
            color: var(--anju-navy) !important;
          }
          h2, h3 {
            color: var(--anju-navy) !important;
          }
          .stCaption { color: var(--anju-text-muted) !important; }
          p.demo-breadcrumb-label,
          .demo-breadcrumb-label {
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: var(--anju-text-muted);
            margin: 0.35rem 0 8px 0 !important;
            padding-top: 0.25rem;
          }
          p.demo-reference-nav-label,
          .demo-reference-nav-label {
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: var(--anju-text-muted);
            margin: 0.35rem 0 8px 0 !important;
            padding-top: 0.25rem;
          }
          span.crumb-current {
            display: block;
            text-align: center;
            font-weight: 700;
            font-size: 0.92rem;
            color: var(--anju-navy);
            background: var(--anju-surface-tint);
            border: 1px solid var(--anju-navy);
            border-radius: 0.5rem;
            padding: 0.45rem 0.5rem;
            box-shadow: 0 1px 0 rgba(37, 99, 235, 0.12);
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
            border: 1px solid var(--anju-border-soft);
            border-radius: 12px;
            padding: 14px 16px;
            margin: 8px 0 14px 0;
            background: var(--anju-surface);
          }
          .demo-kpi {
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: var(--anju-text-muted);
            margin-bottom: 4px;
          }
          .demo-value {
            font-size: 1.05rem;
            font-weight: 600;
            color: var(--anju-navy);
          }
          /* Primary CTAs: deep navy (Anju header-style), white label */
          div[data-testid="stBaseButton-primary"] button {
            background-color: var(--anju-navy) !important;
            border: 1px solid var(--anju-navy-border) !important;
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
            background-color: var(--anju-navy-hover) !important;
            border-color: var(--anju-navy) !important;
          }
          div[data-testid="stBaseButton-primary"] button:hover p,
          div[data-testid="stBaseButton-primary"] button:hover span {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
          }
          div[data-testid="stBaseButton-primary"] button:focus-visible {
            box-shadow: 0 0 0 2px #FFFFFF, 0 0 0 4px var(--anju-royal) !important;
          }
          /* Page links: airy indigo/lavender fill, navy frame (secondary CTA family) */
          div[data-testid="stPageLink-NavLink"] a,
          div[data-testid="stPageLink"] a {
            background: linear-gradient(135deg, #EEF2FF 0%, #EDE9FE 100%) !important;
            border: 2px solid var(--anju-navy) !important;
            color: var(--anju-navy) !important;
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
            color: var(--anju-navy) !important;
            -webkit-text-fill-color: var(--anju-navy) !important;
          }
          div[data-testid="stPageLink-NavLink"] a:hover,
          div[data-testid="stPageLink"] a:hover,
          div[data-testid="stPageLink-NavLink"] a:hover p,
          div[data-testid="stPageLink"] a:hover p,
          div[data-testid="stPageLink-NavLink"] a:hover span,
          div[data-testid="stPageLink"] a:hover span {
            background: linear-gradient(135deg, #E0E7FF 0%, #DDD6FE 100%) !important;
            color: var(--anju-navy) !important;
            -webkit-text-fill-color: var(--anju-navy) !important;
            border-color: var(--anju-violet) !important;
          }
          /* Primary link-style buttons (e.g. st.link_button type=primary in sidebar) */
          section[data-testid="stSidebar"] div[data-testid="stBaseButton-primary"] button {
            background: linear-gradient(135deg, var(--anju-royal) 0%, var(--anju-violet) 100%) !important;
            border: 1px solid #1D4ED8 !important;
          }
          section[data-testid="stSidebar"] div[data-testid="stBaseButton-primary"] button:hover {
            background: linear-gradient(135deg, #1D4ED8 0%, #5B21B6 100%) !important;
            border-color: #5B21B6 !important;
          }
          /* Tighten first promo heading under native nav (avoid a tall empty band) */
          section[data-testid="stSidebar"] h3 {
            margin-top: 0 !important;
            margin-bottom: 0.35rem !important;
          }
          section[data-testid="stSidebar"] h4 {
            margin-top: 0.65rem !important;
            margin-bottom: 0.35rem !important;
          }
          section[data-testid="stSidebar"] hr {
            margin: 0.4rem 0 !important;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_config(title: str) -> None:
    """Wide layout, no decorative page icon (keeps sidebar professional)."""
    st.set_page_config(page_title=title, layout="wide", initial_sidebar_state="expanded")
