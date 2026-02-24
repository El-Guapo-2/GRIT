"""
GRIT - 8-Bit Bitmap Font System
Renders text using a hand-crafted pixel font for authentic retro style.
Every glyph is defined on a 5×7 pixel grid.
"""

import pygame

# ─── 5×7 Pixel Glyph Definitions ──────────────────────────
# Each glyph is 5 columns × 7 rows. '#' = pixel, ' ' = empty.
_GLYPHS = {
    'A': [
        " ### ",
        "#   #",
        "#   #",
        "#####",
        "#   #",
        "#   #",
        "#   #",
    ],
    'B': [
        "#### ",
        "#   #",
        "#   #",
        "#### ",
        "#   #",
        "#   #",
        "#### ",
    ],
    'C': [
        " ### ",
        "#   #",
        "#    ",
        "#    ",
        "#    ",
        "#   #",
        " ### ",
    ],
    'D': [
        "#### ",
        "#   #",
        "#   #",
        "#   #",
        "#   #",
        "#   #",
        "#### ",
    ],
    'E': [
        "#####",
        "#    ",
        "#    ",
        "#### ",
        "#    ",
        "#    ",
        "#####",
    ],
    'F': [
        "#####",
        "#    ",
        "#    ",
        "#### ",
        "#    ",
        "#    ",
        "#    ",
    ],
    'G': [
        " ### ",
        "#   #",
        "#    ",
        "# ###",
        "#   #",
        "#   #",
        " ### ",
    ],
    'H': [
        "#   #",
        "#   #",
        "#   #",
        "#####",
        "#   #",
        "#   #",
        "#   #",
    ],
    'I': [
        "#####",
        "  #  ",
        "  #  ",
        "  #  ",
        "  #  ",
        "  #  ",
        "#####",
    ],
    'J': [
        "  ###",
        "   # ",
        "   # ",
        "   # ",
        "   # ",
        "#  # ",
        " ## ",
    ],
    'K': [
        "#   #",
        "#  # ",
        "# #  ",
        "##   ",
        "# #  ",
        "#  # ",
        "#   #",
    ],
    'L': [
        "#    ",
        "#    ",
        "#    ",
        "#    ",
        "#    ",
        "#    ",
        "#####",
    ],
    'M': [
        "#   #",
        "## ##",
        "# # #",
        "# # #",
        "#   #",
        "#   #",
        "#   #",
    ],
    'N': [
        "#   #",
        "##  #",
        "# # #",
        "# # #",
        "#  ##",
        "#  ##",
        "#   #",
    ],
    'O': [
        " ### ",
        "#   #",
        "#   #",
        "#   #",
        "#   #",
        "#   #",
        " ### ",
    ],
    'P': [
        "#### ",
        "#   #",
        "#   #",
        "#### ",
        "#    ",
        "#    ",
        "#    ",
    ],
    'Q': [
        " ### ",
        "#   #",
        "#   #",
        "#   #",
        "# # #",
        "#  # ",
        " ## #",
    ],
    'R': [
        "#### ",
        "#   #",
        "#   #",
        "#### ",
        "# #  ",
        "#  # ",
        "#   #",
    ],
    'S': [
        " ### ",
        "#   #",
        "#    ",
        " ### ",
        "    #",
        "#   #",
        " ### ",
    ],
    'T': [
        "#####",
        "  #  ",
        "  #  ",
        "  #  ",
        "  #  ",
        "  #  ",
        "  #  ",
    ],
    'U': [
        "#   #",
        "#   #",
        "#   #",
        "#   #",
        "#   #",
        "#   #",
        " ### ",
    ],
    'V': [
        "#   #",
        "#   #",
        "#   #",
        "#   #",
        "#   #",
        " # # ",
        "  #  ",
    ],
    'W': [
        "#   #",
        "#   #",
        "#   #",
        "# # #",
        "# # #",
        "## ##",
        "#   #",
    ],
    'X': [
        "#   #",
        "#   #",
        " # # ",
        "  #  ",
        " # # ",
        "#   #",
        "#   #",
    ],
    'Y': [
        "#   #",
        "#   #",
        " # # ",
        "  #  ",
        "  #  ",
        "  #  ",
        "  #  ",
    ],
    'Z': [
        "#####",
        "    #",
        "   # ",
        "  #  ",
        " #   ",
        "#    ",
        "#####",
    ],
    '0': [
        " ### ",
        "#   #",
        "#  ##",
        "# # #",
        "##  #",
        "#   #",
        " ### ",
    ],
    '1': [
        "  #  ",
        " ##  ",
        "  #  ",
        "  #  ",
        "  #  ",
        "  #  ",
        "#####",
    ],
    '2': [
        " ### ",
        "#   #",
        "    #",
        "  ## ",
        " #   ",
        "#    ",
        "#####",
    ],
    '3': [
        " ### ",
        "#   #",
        "    #",
        "  ## ",
        "    #",
        "#   #",
        " ### ",
    ],
    '4': [
        "   # ",
        "  ## ",
        " # # ",
        "#  # ",
        "#####",
        "   # ",
        "   # ",
    ],
    '5': [
        "#####",
        "#    ",
        "#### ",
        "    #",
        "    #",
        "#   #",
        " ### ",
    ],
    '6': [
        " ### ",
        "#    ",
        "#    ",
        "#### ",
        "#   #",
        "#   #",
        " ### ",
    ],
    '7': [
        "#####",
        "    #",
        "   # ",
        "  #  ",
        "  #  ",
        "  #  ",
        "  #  ",
    ],
    '8': [
        " ### ",
        "#   #",
        "#   #",
        " ### ",
        "#   #",
        "#   #",
        " ### ",
    ],
    '9': [
        " ### ",
        "#   #",
        "#   #",
        " ####",
        "    #",
        "    #",
        " ### ",
    ],
    ' ': [
        "     ",
        "     ",
        "     ",
        "     ",
        "     ",
        "     ",
        "     ",
    ],
    '.': [
        "     ",
        "     ",
        "     ",
        "     ",
        "     ",
        " ##  ",
        " ##  ",
    ],
    ',': [
        "     ",
        "     ",
        "     ",
        "     ",
        "  ## ",
        "  #  ",
        " #   ",
    ],
    ':': [
        "     ",
        " ##  ",
        " ##  ",
        "     ",
        " ##  ",
        " ##  ",
        "     ",
    ],
    ';': [
        "     ",
        " ##  ",
        " ##  ",
        "     ",
        " ##  ",
        "  #  ",
        " #   ",
    ],
    '!': [
        "  #  ",
        "  #  ",
        "  #  ",
        "  #  ",
        "  #  ",
        "     ",
        "  #  ",
    ],
    '?': [
        " ### ",
        "#   #",
        "    #",
        "  ## ",
        "  #  ",
        "     ",
        "  #  ",
    ],
    '-': [
        "     ",
        "     ",
        "     ",
        "#####",
        "     ",
        "     ",
        "     ",
    ],
    '+': [
        "     ",
        "  #  ",
        "  #  ",
        "#####",
        "  #  ",
        "  #  ",
        "     ",
    ],
    '/': [
        "    #",
        "   # ",
        "   # ",
        "  #  ",
        " #   ",
        " #   ",
        "#    ",
    ],
    '(': [
        "  #  ",
        " #   ",
        "#    ",
        "#    ",
        "#    ",
        " #   ",
        "  #  ",
    ],
    ')': [
        "  #  ",
        "   # ",
        "    #",
        "    #",
        "    #",
        "   # ",
        "  #  ",
    ],
    '[': [
        " ### ",
        " #   ",
        " #   ",
        " #   ",
        " #   ",
        " #   ",
        " ### ",
    ],
    ']': [
        " ### ",
        "   # ",
        "   # ",
        "   # ",
        "   # ",
        "   # ",
        " ### ",
    ],
    '#': [
        " # # ",
        " # # ",
        "#####",
        " # # ",
        "#####",
        " # # ",
        " # # ",
    ],
    '*': [
        "     ",
        "# # #",
        " ### ",
        "#####",
        " ### ",
        "# # #",
        "     ",
    ],
    "'": [
        "  #  ",
        "  #  ",
        " #   ",
        "     ",
        "     ",
        "     ",
        "     ",
    ],
    '"': [
        " # # ",
        " # # ",
        "     ",
        "     ",
        "     ",
        "     ",
        "     ",
    ],
    '=': [
        "     ",
        "     ",
        "#####",
        "     ",
        "#####",
        "     ",
        "     ",
    ],
    '_': [
        "     ",
        "     ",
        "     ",
        "     ",
        "     ",
        "     ",
        "#####",
    ],
    '<': [
        "   # ",
        "  #  ",
        " #   ",
        "#    ",
        " #   ",
        "  #  ",
        "   # ",
    ],
    '>': [
        " #   ",
        "  #  ",
        "   # ",
        "    #",
        "   # ",
        "  #  ",
        " #   ",
    ],
    '|': [
        "  #  ",
        "  #  ",
        "  #  ",
        "  #  ",
        "  #  ",
        "  #  ",
        "  #  ",
    ],
    '%': [
        "##  #",
        "## # ",
        "  #  ",
        "  #  ",
        "  #  ",
        " # ##",
        "#  ##",
    ],
    '@': [
        " ### ",
        "#   #",
        "# ###",
        "# # #",
        "# ## ",
        "#    ",
        " ####",
    ],
    '^': [
        "  #  ",
        " # # ",
        "#   #",
        "     ",
        "     ",
        "     ",
        "     ",
    ],
    '&': [
        " ##  ",
        "#  # ",
        "#  # ",
        " ##  ",
        "# # #",
        "#  # ",
        " ## #",
    ],
    '~': [
        "     ",
        "     ",
        " #   ",
        "# # #",
        "   # ",
        "     ",
        "     ",
    ],
    '{': [
        "   # ",
        "  #  ",
        "  #  ",
        " #   ",
        "  #  ",
        "  #  ",
        "   # ",
    ],
    '}': [
        " #   ",
        "  #  ",
        "  #  ",
        "   # ",
        "  #  ",
        "  #  ",
        " #   ",
    ],
}

# Lowercase maps to uppercase for simplicity
for c in 'abcdefghijklmnopqrstuvwxyz':
    _GLYPHS[c] = _GLYPHS[c.upper()]

GLYPH_W = 5
GLYPH_H = 7


# ─── Glyph Surface Cache ──────────────────────────────────
_surf_cache = {}


def _get_glyph_surf(char, scale, color):
    """Get or create a cached surface for a single glyph."""
    key = (char, scale, color)
    if key in _surf_cache:
        return _surf_cache[key]

    pattern = _GLYPHS.get(char)
    if pattern is None:
        # Unknown char → empty
        pattern = _GLYPHS[' ']

    w = GLYPH_W * scale
    h = GLYPH_H * scale
    surf = pygame.Surface((w, h), pygame.SRCALPHA)

    for row_i, row in enumerate(pattern):
        for col_i, c in enumerate(row):
            if c == '#':
                pygame.draw.rect(surf, color,
                                 (col_i * scale, row_i * scale, scale, scale))

    _surf_cache[key] = surf
    return surf


def clear_cache():
    """Clear the glyph cache (call on font setting changes)."""
    _surf_cache.clear()


# ─── Public API ────────────────────────────────────────────
def measure(text, scale=1, spacing=1):
    """Return (width, height) of rendered text."""
    if not text:
        return (0, 0)
    char_w = GLYPH_W * scale + spacing
    w = len(text) * char_w - spacing
    h = GLYPH_H * scale
    return (w, h)


def draw(surface, text, x, y, color=(210, 210, 215), scale=1, spacing=1,
         center=False, right=False, shadow=False, shadow_color=(0, 0, 0, 100)):
    """Draw text using the pixel font.

    Args:
        surface: Target pygame surface.
        text: String to render.
        x, y: Position (depends on alignment).
        color: RGB or RGBA color tuple.
        scale: Pixel size multiplier (1=tiny, 2=normal, 3=large).
        spacing: Pixels between characters.
        center: If True, x/y is center point.
        right: If True, x is right edge.
        shadow: If True, draw a drop shadow.
        shadow_color: RGBA color for shadow.
    """
    if not text:
        return pygame.Rect(x, y, 0, 0)

    text = str(text)
    tw, th = measure(text, scale, spacing)

    if center:
        dx = x - tw // 2
        dy = y - th // 2
    elif right:
        dx = x - tw
        dy = y
    else:
        dx = x
        dy = y

    char_w = GLYPH_W * scale + spacing

    if shadow:
        offset = max(1, scale // 2)
        for i, ch in enumerate(text):
            gs = _get_glyph_surf(ch, scale, shadow_color if len(shadow_color) == 4 else (*shadow_color, 100))
            surface.blit(gs, (dx + i * char_w + offset, dy + offset))

    for i, ch in enumerate(text):
        gs = _get_glyph_surf(ch, scale, color)
        surface.blit(gs, (dx + i * char_w, dy))

    return pygame.Rect(dx, dy, tw, th)


def draw_wrapped(surface, text, x, y, max_width, color=(210, 210, 215),
                 scale=1, spacing=1, line_spacing=2, center=False):
    """Draw text that wraps at max_width."""
    words = text.split(' ')
    lines = []
    current = ""
    for word in words:
        test = current + (" " if current else "") + word
        tw, _ = measure(test, scale, spacing)
        if tw > max_width and current:
            lines.append(current)
            current = word
        else:
            current = test
    if current:
        lines.append(current)

    line_h = GLYPH_H * scale + line_spacing
    total_h = len(lines) * line_h

    for i, line in enumerate(lines):
        ly = y + i * line_h
        if center:
            draw(surface, line, x, ly, color, scale, spacing, center=True)
        else:
            draw(surface, line, x, ly, color, scale, spacing)

    return total_h


# ─── PixelFont Class (convenience wrapper) ─────────────────
class PixelFont:
    """Object-oriented wrapper for a specific font scale.

    Usage:
        font = PixelFont(scale=2)
        font.draw(surface, "HELLO", 100, 50, (255, 255, 255), center=True)
    """

    def __init__(self, scale=1, spacing=1):
        self.scale = scale
        self.spacing = spacing

    def draw(self, surface, text, x, y, color=(210, 210, 215),
             center=False, right=False, shadow=False, shadow_color=(0, 0, 0, 100)):
        return draw(surface, text, x, y, color, self.scale, self.spacing,
                    center, right, shadow, shadow_color)

    def draw_wrapped(self, surface, text, x, y, max_width, color=(210, 210, 215),
                     line_spacing=2, center=False):
        return draw_wrapped(surface, text, x, y, max_width, color,
                            self.scale, self.spacing, line_spacing, center)

    def measure(self, text):
        return measure(text, self.scale, self.spacing)
