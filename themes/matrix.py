import random
import svgwrite


def render(data, theme, width=600, height=200):
    """
    Render Matrix-style digital rain visualization for contributions.

    Args:
        data (dict): Contribution data
        theme (dict): Theme configuration
        width (int): SVG width
        height (int): SVG height

    Returns:
        str: SVG string
    """

    dwg = svgwrite.Drawing(size=(width, height))

    # Background
    dwg.add(
        dwg.rect(
            insert=(0, 0),
            size=(width, height),
            fill=theme.get("bg_color", "#000000")
        )
    )

    contributions = data.get("contributions", [])

    if not contributions:
        return dwg.tostring()

    max_cols = 60
    cols = min(len(contributions), max_cols)

    col_width = width / cols

    for i in range(cols):

        contrib = contributions[i]
        count = contrib.get("count", 0)

        if count <= 0:
            continue

        # Horizontal position
        x = (i * col_width) + (col_width / 2)

        # Determine rain length based on contribution intensity
        rain_length = max(3, min(10, count))

        # Random animation speed
        dur = f"{random.uniform(3,7)}s"

        for j in range(rain_length):

            # Random matrix character
            char = random.choice(["0", "1"])

            # Slight vertical offset for trail effect
            y_offset = -j * 12

            text = dwg.text(
                char,
                insert=(x, y_offset),
                fill=theme.get("icon_color", "#00ff41"),
                font_size=12,
                font_family="monospace",
                text_anchor="middle",
                opacity=max(0.2, 1 - (j * 0.15))
            )

            # Animate falling effect
            text.add(
                dwg.animate(
                    attributeName="y",
                    from_=str(y_offset),
                    to=str(height + 20),
                    dur=dur,
                    repeatCount="indefinite"
                )
            )

            dwg.add(text)

    return dwg.tostring()