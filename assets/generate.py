"""Generate self-contained profile SVGs with outlined, portable typography.

Requires fonttools and the IBM Plex Sans Condensed, IBM Plex Mono, and Lato
fonts installed locally. Run from this directory with an optional output path.
"""

from html import escape
from pathlib import Path
import math
import subprocess
import sys

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont


OUTPUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent
OUTPUT.mkdir(parents=True, exist_ok=True)


def font(family):
    path = subprocess.check_output(["fc-match", "-f", "%{file}", family], text=True).strip()
    value = TTFont(path)
    return value, value.getGlyphSet(), value.getBestCmap(), value["head"].unitsPerEm


FONTS = {
    "display": font("IBM Plex Sans Condensed:style=Bold"),
    "mono": font("IBM Plex Mono:style=Regular"),
    "body": font("Lato:style=Regular"),
}

THEMES = {
    "dark": dict(bg="#101813", panel="#16221B", ink="#F4F1E6", muted="#ADBCAD",
                 line="#34473B", accent="#F8C86C", coral="#FF936D", mint="#A7D7BC"),
    "light": dict(bg="#F6F3E9", panel="#EBEBDD", ink="#1B3025", muted="#526454",
                  line="#CDD6C6", accent="#A86112", coral="#C55832", mint="#3B755A"),
}


class SVG:
    def __init__(self, width, height, title, description, theme):
        self.width, self.height, self.c = width, height, THEMES[theme]
        self.defs, self.body = {}, []
        self.title, self.description = title, description

    def add(self, value):
        self.body.append(value)

    def rect(self, x, y, w, h, fill, radius=0, stroke=None, opacity=1):
        border = f' stroke="{stroke}"' if stroke else ""
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" '
                 f'fill="{fill}" opacity="{opacity}"{border}/>')

    def circle(self, x, y, radius, fill, stroke=None, width=1):
        border = f' stroke="{stroke}" stroke-width="{width}"' if stroke else ""
        self.add(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{fill}"{border}/>')

    def line(self, x1, y1, x2, y2, color, width=1):
        self.add(f'<path d="M{x1} {y1}L{x2} {y2}" fill="none" stroke="{color}" '
                 f'stroke-width="{width}" stroke-linecap="round"/>')

    def text(self, x, y, value, size, color=None, face="body", spacing=0):
        _, glyphs, cmap, units = FONTS[face]
        scale, cursor = size / units, 0
        uses = []
        for character in value:
            name = cmap.get(ord(character))
            if not name:
                raise ValueError(f"Missing {character!r} in {face}")
            glyph = glyphs[name]
            identity = f"{face}-{ord(character):x}"
            if identity not in self.defs:
                pen = SVGPathPen(glyphs)
                glyph.draw(pen)
                self.defs[identity] = f'<path id="{identity}" d="{pen.getCommands()}"/>'
            uses.append(f'<use xlink:href="#{identity}" transform="translate({cursor:.3f} 0)"/>')
            cursor += glyph.width + spacing / scale
        self.add(f'<g fill="{color or self.c["ink"]}" transform="translate({x} {y}) '
                 f'scale({scale:.5f} {-scale:.5f})">{"".join(uses)}</g>')

    def frame(self):
        self.rect(0.5, 0.5, self.width - 1, self.height - 1, self.c["bg"], 12, self.c["line"])

    def save(self, name):
        value = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
                 f'width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}" '
                 f'role="img" aria-labelledby="title desc">'
                 f'<title id="title">{escape(self.title)}</title>'
                 f'<desc id="desc">{escape(self.description)}</desc>'
                 f'<defs>{"".join(self.defs.values())}</defs>{"".join(self.body)}</svg>\n')
        (OUTPUT / name).write_text(value)


def hero(theme):
    svg = SVG(960, 336, "Vinz — design, code, and AI",
              "Senior product designer and creative technologist based in Sicily, Italy, working remotely across Europe.", theme)
    c = svg.c
    svg.frame()
    for x in (32, 248, 464, 680, 928):
        svg.line(x, 24, x, 312, c["line"], 0.5)
    svg.line(32, 64, 928, 64, c["line"], 0.5)
    svg.line(32, 274, 928, 274, c["line"], 0.5)
    svg.text(48, 46, "INDEPENDENT / DESIGN & TECHNOLOGY", 12, c["muted"], "mono", 0.6)
    svg.text(48, 211, "VINZ.", 172, c["ink"], "display", -2)
    svg.text(52, 250, "DESIGN WITH INTENT. BUILD WITH CURIOSITY.", 13, c["muted"], "mono", 0.1)
    svg.circle(55, 303, 4, c["mint"])
    svg.text(70, 308, "SICILY, ITALY", 13, c["ink"], "mono", 0.4)
    svg.text(300, 308, "REMOTE EUROPE", 13, c["muted"], "mono", 0.4)
    svg.text(836, 46, "VZ / 01", 12, c["muted"], "mono")

    # A little solar system: citrus colors, orbital geometry, no external assets.
    svg.circle(768, 168, 104, "none", c["line"])
    svg.circle(768, 168, 76, "none", c["line"])
    svg.add(f'<ellipse cx="768" cy="168" rx="153" ry="55" fill="none" '
            f'stroke="{c["mint"]}" stroke-width="1.2" transform="rotate(-24 768 168)"/>')
    svg.circle(768, 168, 52, c["coral"])
    svg.add(f'<path d="M768 116A52 52 0 0 0 768 220Z" fill="{c["accent"]}"/>')
    svg.circle(768, 168, 24, c["bg"])
    for angle in range(0, 360, 45):
        radians = math.radians(angle)
        svg.line(768 + math.cos(radians) * 31, 168 + math.sin(radians) * 31,
                 768 + math.cos(radians) * 45, 168 + math.sin(radians) * 45, c["bg"], 1.2)
    svg.circle(884, 119, 9, c["mint"])
    svg.circle(655, 214, 5, c["accent"])
    svg.line(899, 222, 899, 236, c["accent"], 1.2)
    svg.line(892, 229, 906, 229, c["accent"], 1.2)
    svg.circle(689, 94, 2, c["mint"])
    svg.text(703, 257, "DESIGN / CODE / AI", 11, c["muted"], "mono", 0.3)
    svg.save(f"profile-hero-{theme}.svg")


def session_hub(theme):
    svg = SVG(960, 224, "Agent Session Hub",
              "An open-source Rust session browser for Codex CLI, Claude Code, and OpenCode. Terminal illustration with fictional sessions.", theme)
    c = svg.c
    svg.frame()
    svg.text(30, 34, "01 / OPEN-SOURCED PROJECT", 11, c["muted"], "mono", 0.4)
    svg.text(30, 102, "Agent Session Hub", 53, c["ink"], "display")
    svg.text(32, 140, "Your coding sessions. One command away.", 19, c["muted"])
    svg.line(32, 177, 60, 177, c["accent"], 3)
    svg.text(76, 182, "RUST / FZF / CROSS-PLATFORM", 11, c["muted"], "mono", 0.3)
    svg.rect(583, 34, 344, 158, c["panel"], 8, c["line"])
    svg.circle(600, 51, 3, c["coral"])
    svg.circle(613, 51, 3, c["accent"])
    svg.circle(626, 51, 3, c["mint"])
    svg.text(601, 85, "$ csx", 16, c["ink"], "mono")
    svg.text(601, 111, "[2 chats + 3 agents] atlas", 12, c["muted"], "mono")
    svg.rect(596, 123, 317, 25, c["line"], 3)
    svg.text(605, 140, "> Fix account recovery", 12, c["mint"], "mono")
    svg.text(605, 171, "  Prepare the next release", 12, c["muted"], "mono")
    svg.save(f"project-session-hub-{theme}.svg")


def desktop_project(name, theme):
    is_git = name == "gitpop"
    title = "GitPop" if is_git else "PhrasePoP"
    svg = SVG(470, 200, title,
              "AI-assisted Git workflows from the Windows context menu." if is_git
              else "A desktop assistant for rewriting text and drafting replies.", theme)
    c = svg.c
    svg.frame()
    svg.text(24, 31, "02 / DEVELOPER TOOLS" if is_git else "03 / EVERYDAY AI", 10, c["muted"], "mono", 0.2)
    svg.text(24, 91, title, 46, c["ink"], "display")
    svg.text(26, 124, "A smaller surface for Git." if is_git else "Better words. Less friction.", 17, c["muted"])
    svg.text(26, 174, "TAURI / RUST / REACT", 10, c["muted"], "mono", 0.3)
    if is_git:
        svg.line(374, 63, 374, 125, c["mint"], 3)
        svg.add(f'<path d="M374 110Q374 89 397 89Q420 89 420 65" fill="none" stroke="{c["mint"]}" stroke-width="3"/>')
        svg.circle(374, 60, 7, c["panel"], c["accent"], 3)
        svg.circle(420, 60, 7, c["panel"], c["mint"], 3)
        svg.circle(374, 129, 7, c["coral"])
    else:
        svg.rect(342, 61, 93, 58, c["panel"], 6, c["line"])
        svg.rect(352, 75, 57, 9, c["accent"], 2)
        svg.line(352, 99, 393, 99, c["muted"], 2)
        svg.line(418, 81, 418, 105, c["mint"], 2)
        svg.line(413, 81, 423, 81, c["mint"], 2)
        svg.line(413, 105, 423, 105, c["mint"], 2)
        svg.line(433, 39, 433, 51, c["coral"], 2)
        svg.line(427, 45, 439, 45, c["coral"], 2)
    svg.save(f"project-{name}-{theme}.svg")


for theme in THEMES:
    hero(theme)
    session_hub(theme)
    desktop_project("gitpop", theme)
    desktop_project("phrasepop", theme)
