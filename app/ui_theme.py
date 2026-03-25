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
        '<div class="workflow-breadcrumb-heading">'
        '<p class="workflow-breadcrumb-label">Case workflow</p>'
        '<div class="anju-brand-accent-bar" aria-hidden="true"></div>'
        "</div>",
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
    for i, (step_key, _path, label) in enumerate(_BREADCRUMB):
        with cols[col_idx]:
            if step_key == current:
                st.markdown(
                    f'<span class="crumb-current-text">{label}</span>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<span class="crumb-plain">{label}</span>',
                    unsafe_allow_html=True,
                )
        col_idx += 1
        if i < n - 1:
            with cols[col_idx]:
                st.markdown('<span class="crumb-sep">›</span>', unsafe_allow_html=True)
            col_idx += 1


def render_policy_reference_nav() -> None:
    """Policy & privacy is reference material — separate from the case workflow breadcrumb."""
    st.markdown(
        '<p class="workflow-reference-nav-label">Reference</p>',
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
        "Explore Luminee",
        s.luminee_booking_url,
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
          /* Anju logo palette (assets/anju-software-log.svg) + navy UI surfaces */
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
            /* Logo primaries */
            --anju-logo-blue-deep: #0000AC;
            --anju-logo-blue-bright: #004FEC;
            --anju-logo-cyan: #00CAF9;
            --anju-logo-magenta: #D400C8;
            --anju-brand-gradient: linear-gradient(
              90deg,
              var(--anju-logo-blue-deep) 0%,
              var(--anju-logo-cyan) 38%,
              var(--anju-logo-magenta) 68%,
              var(--anju-logo-blue-bright) 100%
            );
            --anju-brand-gradient-soft: linear-gradient(
              135deg,
              color-mix(in srgb, var(--anju-logo-blue-deep) 12%, white) 0%,
              color-mix(in srgb, var(--anju-logo-cyan) 10%, white) 45%,
              color-mix(in srgb, var(--anju-logo-magenta) 8%, white) 100%
            );
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
          /* Subtle brand wash behind main content */
          section[data-testid="stMain"] {
            background: radial-gradient(
              120% 80% at 0% -10%,
              color-mix(in srgb, var(--anju-logo-blue-bright) 7%, transparent),
              transparent 55%
            ),
            radial-gradient(
              90% 60% at 100% 0%,
              color-mix(in srgb, var(--anju-logo-cyan) 5%, transparent),
              transparent 50%
            );
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
          .workflow-breadcrumb-heading {
            margin-bottom: 0;
          }
          p.workflow-breadcrumb-label,
          .workflow-breadcrumb-label {
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: var(--anju-text-muted);
            margin: 0.35rem 0 4px 0 !important;
            padding-top: 0.25rem;
          }
          .anju-brand-accent-bar {
            height: 3px;
            width: min(100%, 320px);
            border-radius: 2px;
            background: var(--anju-brand-gradient);
            margin: 0 0 12px 0;
            box-shadow: 0 1px 6px color-mix(in srgb, var(--anju-logo-blue-bright) 25%, transparent);
          }
          p.workflow-reference-nav-label,
          .workflow-reference-nav-label {
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: var(--anju-text-muted);
            margin: 0.35rem 0 8px 0 !important;
            padding-top: 0.25rem;
          }
          /* Case workflow breadcrumb: text only (use sidebar to change pages) */
          span.crumb-current-text {
            display: block;
            text-align: center;
            font-weight: 700;
            font-size: 0.95rem;
            color: var(--anju-logo-blue-deep);
            text-shadow: 0 1px 0 color-mix(in srgb, var(--anju-logo-cyan) 28%, transparent);
          }
          span.crumb-plain {
            display: block;
            text-align: center;
            font-weight: 500;
            font-size: 0.95rem;
            color: var(--anju-text-muted);
          }
          span.crumb-sep {
            display: flex;
            align-items: center;
            justify-content: center;
            color: #9CA3AF;
            font-size: 1.1rem;
            padding-top: 0.35rem;
          }
          .workflow-card {
            border: 1px solid var(--anju-border-soft);
            border-radius: 12px;
            padding: 14px 16px;
            margin: 8px 0 14px 0;
            background: var(--anju-surface);
          }
          .workflow-kpi {
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: var(--anju-text-muted);
            margin-bottom: 4px;
          }
          .workflow-value {
            font-size: 1.05rem;
            font-weight: 600;
            color: var(--anju-navy);
          }
          /* Primary CTAs: logo-aligned blue gradient (main); white label */
          div[data-testid="stBaseButton-primary"] button {
            background: linear-gradient(
              135deg,
              var(--anju-logo-blue-deep) 0%,
              var(--anju-logo-blue-bright) 100%
            ) !important;
            border: 1px solid color-mix(in srgb, var(--anju-logo-blue-deep) 85%, black) !important;
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
            background: linear-gradient(
              135deg,
              color-mix(in srgb, var(--anju-logo-blue-deep) 92%, white) 0%,
              color-mix(in srgb, var(--anju-logo-cyan) 45%, var(--anju-logo-blue-bright)) 100%
            ) !important;
            border-color: var(--anju-logo-cyan) !important;
          }
          div[data-testid="stBaseButton-primary"] button:hover p,
          div[data-testid="stBaseButton-primary"] button:hover span {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
          }
          div[data-testid="stBaseButton-primary"] button:focus-visible {
            box-shadow: 0 0 0 2px #FFFFFF, 0 0 0 4px var(--anju-logo-cyan) !important;
          }
          /* Page links: airy indigo/lavender fill, navy frame (secondary CTA family) */
          div[data-testid="stPageLink-NavLink"] a,
          div[data-testid="stPageLink"] a {
            background: var(--anju-brand-gradient-soft) !important;
            border: 2px solid color-mix(in srgb, var(--anju-logo-blue-deep) 55%, var(--anju-border-soft)) !important;
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
            background: linear-gradient(
              135deg,
              color-mix(in srgb, var(--anju-logo-cyan) 18%, white) 0%,
              color-mix(in srgb, var(--anju-logo-magenta) 12%, white) 100%
            ) !important;
            color: var(--anju-navy) !important;
            -webkit-text-fill-color: var(--anju-navy) !important;
            border-color: var(--anju-logo-blue-bright) !important;
          }
          /* Primary link-style buttons (e.g. st.link_button type=primary in sidebar) — full logo spectrum */
          section[data-testid="stSidebar"] div[data-testid="stBaseButton-primary"] button {
            background: var(--anju-brand-gradient) !important;
            border: 1px solid var(--anju-logo-blue-deep) !important;
          }
          section[data-testid="stSidebar"] div[data-testid="stBaseButton-primary"] button:hover {
            background: linear-gradient(
              90deg,
              color-mix(in srgb, var(--anju-logo-blue-deep) 88%, white) 0%,
              color-mix(in srgb, var(--anju-logo-cyan) 70%, var(--anju-logo-blue-bright)) 50%,
              color-mix(in srgb, var(--anju-logo-magenta) 75%, var(--anju-logo-blue-bright)) 100%
            ) !important;
            border-color: var(--anju-logo-cyan) !important;
          }
          /* Sidebar: subtle brand tint (follows system / Streamlit theme) */
          section[data-testid="stSidebar"] {
            background: linear-gradient(
              180deg,
              color-mix(in srgb, var(--anju-logo-blue-bright) 6%, Canvas) 0%,
              Canvas 32%
            ) !important;
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
