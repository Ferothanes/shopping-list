from __future__ import annotations

import streamlit as st


def apply_styles() -> None:
    st.markdown(
        """
<style>
:root {
    --bg: #1F3D2B;
    --card: #F9FAF7;
    --primary: #E63946;
    --secondary: #2F8F5B;
    --text-dark: #3A2E2A;
    --text-light: #F9FAF7;
}

body {
    background: var(--bg);
    color: var(--text-light);
}

.item-chip {
    background: var(--card);
    border-radius: 999px;
    padding: 6px 12px;
    font-size: 0.9rem;
    border: 1px solid var(--secondary);
    text-align: center;
    margin-bottom: 8px;
    color: var(--text-dark);
}
</style>
""",
        unsafe_allow_html=True,
    )
