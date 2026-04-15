# theme_gallery.py
# Resolves Issue #162 — Theme Preview Grid in Streamlit
# Adds a visual "Theme Gallery" so users can see all themes side-by-side
# and select one with a single click instead of using the dropdown.

import streamlit as st


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _generate_mini_svg(theme_name: str, theme: dict) -> str:
    """
    Build a compact 160×100 SVG that visually represents a theme's colour palette.
    Renders a fake stats-card layout (header bar, stat bars, colour swatches) using
    the theme's own bg / border / title / text / icon colours so the preview is
    100 % accurate to the real card output.
    """
    bg          = theme.get("bg_color",     "#0d1117")
    border      = theme.get("border_color", "#30363d")
    title_color = theme.get("title_color",  "#58a6ff")
    text_color  = theme.get("text_color",   "#c9d1d9")
    icon_color  = theme.get("icon_color",   "#8b949e")
    font        = theme.get("font_family",  "Segoe UI, Ubuntu, Sans-Serif")

    # Safely truncate long theme names so they fit inside the mini card
    display_name = theme_name if len(theme_name) <= 11 else theme_name[:10] + "…"

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="160" height="100" viewBox="0 0 160 100">
  <!-- Card background -->
  <rect width="160" height="100" rx="8" fill="{bg}" stroke="{border}" stroke-width="2"/>

  <!-- Header bar mimicking the real card title area -->
  <rect x="8" y="8" width="144" height="20" rx="4" fill="{border}" opacity="0.45"/>
  <text x="16" y="22" font-family="{font}" font-size="9"
        fill="{title_color}" font-weight="bold">{display_name}</text>

  <!-- Fake stat rows: label + filled progress bar -->
  <text x="12" y="44" font-family="{font}" font-size="7" fill="{text_color}" opacity="0.85">Stars</text>
  <rect x="42" y="37" width="80" height="6" rx="3" fill="{border}"      opacity="0.35"/>
  <rect x="42" y="37" width="52" height="6" rx="3" fill="{icon_color}"  opacity="0.90"/>

  <text x="12" y="58" font-family="{font}" font-size="7" fill="{text_color}" opacity="0.85">Commits</text>
  <rect x="42" y="51" width="80" height="6" rx="3" fill="{border}"       opacity="0.35"/>
  <rect x="42" y="51" width="68" height="6" rx="3" fill="{title_color}"  opacity="0.90"/>

  <text x="12" y="72" font-family="{font}" font-size="7" fill="{text_color}" opacity="0.85">PRs</text>
  <rect x="42" y="65" width="80" height="6" rx="3" fill="{border}"      opacity="0.35"/>
  <rect x="42" y="65" width="40" height="6" rx="3" fill="{icon_color}"  opacity="0.90"/>

  <!-- Colour-swatch strip at the bottom — instant palette read -->
  <circle cx="16" cy="88" r="5" fill="{bg}"          stroke="{border}" stroke-width="1.5"/>
  <circle cx="30" cy="88" r="5" fill="{title_color}"/>
  <circle cx="44" cy="88" r="5" fill="{text_color}"/>
  <circle cx="58" cy="88" r="5" fill="{icon_color}"/>
  <circle cx="72" cy="88" r="5" fill="{border}"/>
</svg>"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def render_theme_gallery(all_themes: dict, current_theme: str) -> str | None:
    """
    Render a 4-column visual theme gallery.

    Parameters
    ----------
    all_themes    : dict  — output of ``get_all_themes()`` from themes/styles.py
    current_theme : str   — the theme that is currently active (highlighted in blue)

    Returns
    -------
    str | None  — the name of the theme the user just clicked, or ``None`` if no
                  click happened this Streamlit run.

    How to use in app.py
    --------------------
    from theme_gallery import render_theme_gallery

    # Put this wherever you want the gallery to appear (e.g. after the sidebar
    # selectbox, or in a dedicated "Theme Gallery" tab).
    chosen = render_theme_gallery(all_themes, selected_theme)
    if chosen:
        selected_theme = chosen          # Streamlit will rerun and apply the theme
    """

    st.subheader("🎨 Theme Gallery")
    st.caption("Preview every theme at a glance — click **Select** to apply.")

    # ── Cache the SVG generation so re-runs don't regenerate every card ──────
    @st.cache_data(show_spinner=False)
    def _build_svg_map(themes_snapshot: tuple) -> dict:
        return {
            name: _generate_mini_svg(name, dict(props))
            for name, props in themes_snapshot
        }

    # Convert to a hashable snapshot for the cache key
    themes_snapshot = tuple(
        (name, tuple(sorted(props.items())))
        for name, props in all_themes.items()
    )
    svg_map = _build_svg_map(themes_snapshot)

    # ── Render grid ──────────────────────────────────────────────────────────
    COLS_PER_ROW = 4
    themes_list  = list(all_themes.items())
    selected     = None

    for row_start in range(0, len(themes_list), COLS_PER_ROW):
        row_slice = themes_list[row_start : row_start + COLS_PER_ROW]
        cols      = st.columns(COLS_PER_ROW)

        for col, (theme_name, _) in zip(cols, row_slice):
            is_active  = theme_name == current_theme
            svg_html   = svg_map.get(theme_name, "")

            # Active theme gets a bright blue ring; inactive gets a transparent placeholder
            wrapper_style = (
                "border:2px solid #58a6ff; border-radius:10px; padding:3px;"
                if is_active else
                "border:2px solid transparent; border-radius:10px; padding:3px;"
            )

            with col:
                st.markdown(
                    f'<div style="{wrapper_style}">{svg_html}</div>',
                    unsafe_allow_html=True,
                )

                if is_active:
                    # Show an "Active" badge instead of a redundant button
                    st.markdown(
                        "<p style='text-align:center; color:#58a6ff; font-size:11px;"
                        " font-weight:700; margin:2px 0 6px;'>✓ Active</p>",
                        unsafe_allow_html=True,
                    )
                else:
                    if st.button(
                        "Select",
                        key=f"gallery_select_{theme_name}",
                        use_container_width=True,
                    ):
                        selected = theme_name

    return selected