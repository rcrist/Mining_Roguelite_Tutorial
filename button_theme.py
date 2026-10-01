"""Shared styles for UI buttons."""

import arcade
from math import cos, sin, pi
from arcade.gui import UIFlatButton

CORNER_RADIUS = 5

class RoundedButton(UIFlatButton):
    """A themed flat button with 5 px rounded corners."""

    def do_render(self, surface):
        self.prepare_render(surface)
        surface.clear()
        style = self.get_current_style()
        if style is None:
            raise ValueError(f"No style found for state {self.get_current_state()}")
        self._apply_style(style)
        width, height = self.content_width, self.content_height
        radius = min(CORNER_RADIUS, width / 2, height / 2)

        def fill(inset, color):
            if color is None or width <= 2 * inset or height <= 2 * inset:
                return
            r = max(0, radius - inset)
            points = []
            for cx, cy, start in (
                (width - inset - r, height - inset - r, 0),
                (inset + r, height - inset - r, pi / 2),
                (inset + r, inset + r, pi),
                (width - inset - r, inset + r, 3 * pi / 2),
            ):
                for step in range(9):
                    angle = start + step * pi / 16
                    points.append((cx + r * cos(angle), cy + r * sin(angle)))
            arcade.draw_polygon_filled(points, color)

        border_width = style.get("border_width", 0)
        border_color = style.get("border")
        if border_color and border_width:
            fill(0, border_color)
            fill(border_width, style.get("bg"))
        else:
            fill(0, style.get("bg"))

button_style = {
    state: UIFlatButton.UIStyle(
        font_name="m5x7", font_size=12,
        font_color=arcade.color.WHITE, bg=(56, 115, 163, 255),
        border=arcade.color.WHITE,
        border_width=1 if state in ("hover", "press") else 0,
    )
    for state in ("normal", "hover", "press", "disabled")
}
