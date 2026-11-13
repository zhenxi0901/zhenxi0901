#!/usr/bin/env python3
"""Animated SVGs for the zhenxi0901 GitHub profile README.

    python3 animations.py OUT_DIR

writes four images into OUT_DIR:

  canary-dark.svg, canary-light.svg
      The last year of GitHub contributions, rolled out like a release. Every week
      starts on a dim "v1"; a canary then moves 1% -> 5% -> 25% -> 50% -> 100% of the
      weeks onto their real colours, with a traffic bar, a stage label, a final
      "rollout complete" stamp and the live health of the portfolio site.

  terminal-dark.svg, terminal-light.svg
      A terminal window that types `curl -s <site>` and prints the site's real
      plain-text answer.

Inputs
  * GitHub GraphQL API, authenticated with GITHUB_TOKEN or GH_TOKEN (required).
  * The portfolio site: its text card for curl (required), /api/status and /api/slo
    (optional: any part that cannot be read is left out of the health readout).

If a required input cannot be fetched, the script exits with status 1 before writing
anything, so a scheduled workflow keeps the previous images.

The SVGs are made for <img> tags behind GitHub's image proxy: no scripts, no external
references, no foreignObject. Each animation is one exact loop (every step sits inside a
single cycle; nothing relies on animation-delay), and prefers-reduced-motion shows the
final frame without motion.

Standard library only.
"""

from __future__ import annotations

import http.client
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date

# ---------------------------------------------------------------------------
# What to fetch
# ---------------------------------------------------------------------------

GITHUB_USER = "zhenxi0901"
SITE_HOST = "portfolio-emsghin2iq-as.a.run.app"
SITE = "https://" + SITE_HOST
GRAPHQL_URL = "https://api.github.com/graphql"
CONTRIBUTIONS_QUERY = (
    'query { user(login: "%s") { contributionsCollection { contributionCalendar { '
    "totalContributions weeks { contributionDays { date contributionCount weekday } } "
    "} } } }" % GITHUB_USER
)
# The site answers curl with a plain-text card, so ask exactly the way curl does.
CURL_HEADERS = {"User-Agent": "curl/8.5.0", "Accept": "*/*"}
API_HEADERS = {"User-Agent": "profile-animations", "Accept": "application/json"}

# The command the terminal types (the card itself is fetched over https).
# With the scheme: without it curl gets a redirect and prints nothing, and people copy this.
PROMPT_COMMAND = "curl -s https://" + SITE_HOST

# The SVGs end up on a public profile: refuse to publish a card that suddenly
# contains an email address or a phone number (the workflow then keeps the old one).
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"\+\d[\d ()-]{7,}\d")

MAX_SVG_BYTES = 150_000

# ---------------------------------------------------------------------------
# Look
# ---------------------------------------------------------------------------

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
SANS = "-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
# Advance of one character of the mono stack, in em. Mono text gets an explicit
# textLength (chars * MONO_EM * size), so columns line up whichever font is installed.
MONO_EM = 0.6

THEMES = {
    "dark": {
        "bg": "#0d1117",
        "panel": "#161b22",
        "border": "#30363d",
        "text": "#e6edf3",
        "muted": "#8b949e",
        "accent": "#c2f75c",
        "accent_bg": "#1a2e05",
        "levels": ("#161b22", "#1a2e05", "#3a5a0b", "#6b9a14", "#c2f75c"),
        # v1, the "old version": the same five levels, greyed out and dimmed
        "old_levels": ("#11161d", "#1c2129", "#282e37", "#383f49", "#4e5661"),
        "old_bar": "#21262d",
        "flash": "#c2f75c",
        "flash_peak": 0.45,
        "dots": ("#ff5f57", "#febc2e", "#28c840"),
    },
    "light": {
        "bg": "#ffffff",
        "panel": "#f6f8fa",
        "border": "#d0d7de",
        "text": "#1f2328",
        "muted": "#59636e",
        "accent": "#3f6212",
        "accent_bg": "#ecfccb",
        "levels": ("#ebedf0", "#d9f99d", "#a3e635", "#65a30d", "#3f6212"),
        "old_levels": ("#f3f4f6", "#e8ebee", "#dadee3", "#c5ccd3", "#a9b2bc"),
        "old_bar": "#e3e7eb",
        "flash": "#84cc16",
        "flash_peak": 0.5,
        "dots": ("#ff5f57", "#febc2e", "#28c840"),
    },
}

# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def esc(text: str) -> str:
    """Escape text for XML content and attribute values."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def num(value: float) -> str:
    """A compact number for SVG and CSS (two decimals at most, no trailing zeros)."""
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    return "0" if text in ("", "-0") else text


def mono_width(text: str, size: float) -> float:
    return len(text) * MONO_EM * size


def mono_text(x: float, y: float, text: str, size: float, attrs: str = "") -> str:
    """One run of monospaced text pinned to its exact width."""
    return (
        f'<text x="{num(x)}" y="{num(y)}" font-size="{num(size)}" '
        f'textLength="{num(mono_width(text, size))}"{attrs}>{esc(text)}</text>'
    )


def svg_document(width: float, height: float, ident: str, title: str, desc: str, body: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{num(width)}" height="{num(height)}" '
        f'viewBox="0 0 {num(width)} {num(height)}" role="img" '
        f'aria-labelledby="{ident}-title {ident}-desc">\n'
        f'<title id="{ident}-title">{esc(title)}</title>\n'
        f'<desc id="{ident}-desc">{esc(desc)}</desc>\n'
        f"{body}\n</svg>\n"
    )


# ---------------------------------------------------------------------------
# Fetching
# ---------------------------------------------------------------------------


class FetchError(Exception):
    """A required input could not be fetched or understood."""


def fetch(url: str, headers: dict, body: bytes | None = None,
          attempts: int = 3, timeout: float = 20.0) -> bytes:
    """GET (or POST when a body is given), retrying transient failures."""
    for attempt in range(1, attempts + 1):
        try:
            request = urllib.request.Request(url, data=body, headers=headers)
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except urllib.error.HTTPError as err:
            # A 4xx (bad token, not found) will not fix itself; only retry 429 and 5xx.
            if (400 <= err.code < 500 and err.code != 429) or attempt == attempts:
                raise FetchError(f"{url}: HTTP {err.code}") from err
        except (urllib.error.URLError, OSError, http.client.HTTPException) as err:
            if attempt == attempts:
                raise FetchError(f"{url}: {err}") from err
        time.sleep(2 * attempt)
    raise AssertionError("unreachable")


@dataclass
class Calendar:
    total: int
    weeks: list  # one list per week of (iso_date, count, weekday) tuples


def fetch_calendar(token: str) -> Calendar:
    headers = {
        "Authorization": f"bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "profile-animations",
    }
    raw = fetch(GRAPHQL_URL, headers, json.dumps({"query": CONTRIBUTIONS_QUERY}).encode())
    try:
        payload = json.loads(raw)
        if payload.get("errors"):
            raise FetchError(f"GraphQL errors: {payload['errors']}")
        calendar = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]
        weeks = []
        for week in calendar["weeks"]:
            days = [
                (day["date"], int(day["contributionCount"]), int(day["weekday"]))
                for day in week["contributionDays"]
            ]
            if days:
                weeks.append(days)
        total = int(calendar["totalContributions"])
    except (KeyError, TypeError, ValueError) as err:
        raise FetchError(f"unexpected GraphQL answer: {err!r}") from err
    if not weeks:
        raise FetchError("the contribution calendar is empty")
    return Calendar(total, weeks)


def fetch_card_text() -> str:
    text = fetch(SITE + "/", CURL_HEADERS).decode("utf-8", errors="replace")
    start = text.lstrip()[:20].lower()
    if not text.strip() or start.startswith(("<!doctype", "<html")):
        raise FetchError("the site did not answer curl with a text card")
    return text


def fetch_optional_json(url: str) -> dict | None:
    try:
        data = json.loads(fetch(url, API_HEADERS, attempts=2, timeout=10))
    except (FetchError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


@dataclass
class Health:
    # Readout pieces such as [("p95 ", "muted"), ("6.2 ms", "text")], one list per part.
    parts: list
    # True when /api/status answered "ok"; the final stamp only says "healthy" then.
    healthy: bool


def format_ms(ms: float) -> str:
    return f"{ms:.1f}" if ms < 10 else f"{ms:.0f}"


def format_availability(fraction: float) -> str:
    # Round down, as SLO reports do: 99.9995% is not 100%.
    if fraction >= 1:
        return "100%"
    return f"{math.floor(fraction * 10000) / 100:.2f}%"


def read_health() -> Health:
    """The live readout. Each endpoint is optional; a failed one just drops its parts."""
    status = fetch_optional_json(SITE + "/api/status")
    slo = fetch_optional_json(SITE + "/api/slo")
    parts = []
    healthy = False
    if status:
        healthy = status.get("status", "ok") == "ok"
        latency = status.get("latency_ms")
        p95 = latency.get("p95") if isinstance(latency, dict) else None
        if is_number(p95) and p95 >= 0:
            parts.append([("p95 ", "muted"), (f"{format_ms(p95)} ms", "text")])
    if slo and slo.get("available") is True and is_number(slo.get("availability")):
        parts.append([(format_availability(slo["availability"]), "text"), (" up", "muted")])
    if status:
        commit = status.get("commit")
        if isinstance(commit, str) and re.fullmatch(r"[0-9a-f]{7,40}", commit):
            parts.append([("commit ", "muted"), (commit[:7], "text")])
    return Health(parts, healthy)


# ---------------------------------------------------------------------------
# The text card: ANSI colours -> styled cells -> wrapped rows
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Cell:
    ch: str
    tone: str  # "text", "muted" or "accent"
    bold: bool


SPACE = Cell(" ", "text", False)
SGR_RE = re.compile(r"\x1b\[([0-9;]*)m")
OTHER_ESCAPE_RE = re.compile(r"\x1b(?:\][^\x07\x1b]*(?:\x07|\x1b\\)|\[[0-9;?<=>!]*[ -/]*[@-~]|[@-_])")


def is_green_256(n: int) -> bool:
    """Is xterm-256 colour n a green or lime (the site's accent)?"""
    if n in (2, 10):
        return True
    if 16 <= n <= 231:
        r, g, b = (n - 16) // 36, (n - 16) // 6 % 6, (n - 16) % 6
        return g > r and g > b
    return False


def apply_sgr(params: str, bold: bool, dim: bool, colour: str | None):
    """Update (bold, dim, colour) for one SGR sequence. Colour is None, "green" or "other"."""
    codes = [int(p) if p else 0 for p in params.split(";")] if params else [0]
    i = 0
    while i < len(codes):
        code = codes[i]
        if code == 0:
            bold, dim, colour = False, False, None
        elif code == 1:
            bold = True
        elif code == 2:
            dim = True
        elif code == 22:
            bold = dim = False
        elif code == 39:
            colour = None
        elif 30 <= code <= 37 or 90 <= code <= 97:
            colour = "green" if code in (32, 92) else "other"
        elif code in (38, 48):  # extended colour: 5;n or 2;r;g;b
            mode = codes[i + 1] if i + 1 < len(codes) else None
            args = codes[i + 2:i + 3] if mode == 5 else codes[i + 2:i + 5] if mode == 2 else []
            if code == 38 and mode == 5 and len(args) == 1:
                colour = "green" if is_green_256(args[0]) else "other"
            elif code == 38 and mode == 2 and len(args) == 3:
                colour = "green" if args[1] > max(args[0], args[2]) else "other"
            i += 1 + len(args)
        i += 1
    return bold, dim, colour


def parse_ansi_line(line: str) -> list:
    """Turn one line of terminal output into cells. Greens become the accent, dim
    becomes muted, bold stays bold; every other escape sequence is dropped."""
    cells = []
    bold = dim = False
    colour = None
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == "\x1b":
            match = SGR_RE.match(line, i)
            if match:
                bold, dim, colour = apply_sgr(match.group(1), bold, dim, colour)
                i = match.end()
                continue
            match = OTHER_ESCAPE_RE.match(line, i)
            i = match.end() if match else i + 1
            continue
        if ch == "\t":
            cells.extend([SPACE] * (8 - len(cells) % 8))
        elif ch.isprintable():  # drops control characters, which XML would reject
            tone = "accent" if colour == "green" else "muted" if dim else "text"
            cells.append(Cell(ch, tone, bold))
        i += 1
    return cells


def plain(cells: list) -> str:
    return "".join(cell.ch for cell in cells)


def strip_cells(cells: list, left: bool = True, right: bool = True) -> list:
    start, end = 0, len(cells)
    while left and start < end and cells[start].ch == " ":
        start += 1
    while right and end > start and cells[end - 1].ch == " ":
        end -= 1
    return cells[start:end]


def find_break(text: str, width: int):
    """Where to fold a too-long row: (index, kind). Prefers a column gap (2+ spaces),
    then a space after punctuation, then any space; falls back to a hard cut."""
    start = len(text) - len(text.lstrip(" "))
    gaps, after_punct, spaces = [], [], []
    for i in range(start + 1, min(len(text), width + 1)):
        if text[i] != " " or text[i - 1] == " ":
            continue  # only the first space of each run is a candidate
        if text[i:i + 2] == "  ":
            gaps.append(i)
        elif text[i - 1] in ",;:.":
            after_punct.append(i)
        spaces.append(i)
    # A break must leave a reasonably long first row, or the result looks ragged.
    for kind, candidates, shortest in (
        ("gap", gaps, width // 3),
        ("punct", after_punct, width // 2),
        ("space", spaces, start + 1),
    ):
        fitting = [i for i in candidates if i >= shortest]
        if fitting:
            return max(fitting), kind
    return width, "hard"


LABEL_RE = re.compile(r" *\S+(?: \S+)*? {2,}(?=\S)")


def hanging_indent(text: str, indent: int, kind: str, width: int) -> int:
    """Indent of continuation rows: a description pushed under its command gets +4,
    a 'label   value' line continues under the value, prose keeps its indent."""
    if kind == "gap":
        return indent + 4
    label = LABEL_RE.match(text)
    if label and label.end() <= width // 3:
        return label.end()
    return indent


def wrap(cells: list, width: int) -> list:
    """Fold one logical line into rows of at most `width` columns."""
    text = plain(cells)
    if len(text) <= width:
        return [cells]
    indent = len(text) - len(text.lstrip(" "))
    rows, hang, rest = [], None, cells
    while len(rest) > width:
        cut, kind = find_break(plain(rest), width)
        if hang is None:
            hang = min(hanging_indent(text, indent, kind, width), width // 2)
        if cut <= (hang if rows else indent):  # no progress possible: hard cut
            cut = width
        rows.append(strip_cells(rest[:cut], left=False))
        rest = [SPACE] * hang + strip_cells(rest[cut:], right=False)
    rows.append(rest)
    return rows


@dataclass
class Card:
    rows: list   # rows of cells, already wrapped; [] is a blank row
    lines: list  # the plain text of the logical lines shown, for the description


def parse_card(text: str, width: int = 76, max_rows: int = 20) -> Card:
    """Strip ANSI codes, wrap to `width` columns and keep at most `max_rows` rows,
    cutting only between logical lines."""
    lines = [strip_cells(parse_ansi_line(line), left=False)
             for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    # Trim blank lines at both ends and squeeze runs of blank lines into one.
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    squeezed = []
    for cells in lines:
        if cells or (squeezed and squeezed[-1]):
            squeezed.append(cells)

    rows, shown = [], []
    for cells in squeezed:
        wrapped = wrap(cells, width) if cells else [[]]
        if len(rows) + len(wrapped) > max_rows:
            break
        rows.extend(wrapped)
        shown.append(plain(cells).strip())
    while rows and not rows[-1]:
        rows.pop()
    while shown and not shown[-1]:
        shown.pop()

    everything = "\n".join(shown)
    if EMAIL_RE.search(everything) or PHONE_RE.search(everything):
        raise FetchError("the text card contains an email address or a phone number")
    if not rows:
        raise FetchError("the text card is empty")
    return Card(rows, shown)


def text_pieces(cells: list) -> list:
    """Split a row into (column, text, tone, bold) pieces. A piece has one style, no
    leading or trailing spaces and no double spaces, so placing it at its column
    with an exact textLength reproduces the terminal layout."""
    pieces, i, n = [], 0, len(cells)
    while i < n:
        if cells[i].ch == " ":
            i += 1
            continue
        style = (cells[i].tone, cells[i].bold)
        j = i
        while j + 1 < n:
            nxt = cells[j + 1]
            if nxt.ch != " " and (nxt.tone, nxt.bold) == style:
                j += 1
            elif (nxt.ch == " " and j + 2 < n and cells[j + 2].ch != " "
                  and (cells[j + 2].tone, cells[j + 2].bold) == style):
                j += 2  # a single space inside a same-styled run
            else:
                break
        pieces.append((i, plain(cells[i:j + 1]), style[0], style[1]))
        i = j + 1
    return pieces


# ---------------------------------------------------------------------------
# Animation helpers
# ---------------------------------------------------------------------------


def pct(seconds: float, cycle: float) -> str:
    return num(100 * seconds / cycle) + "%"


def keyframes(name: str, stops: list, cycle: float) -> str:
    """CSS @keyframes from (seconds, declarations) stops inside one cycle.
    Neighbouring stops with the same declarations share one selector."""
    blocks = []
    for seconds, decl in stops:
        if blocks and blocks[-1][1] == decl:
            blocks[-1][0].append(pct(seconds, cycle))
        else:
            blocks.append(([pct(seconds, cycle)], decl))
    body = "".join(f"{','.join(times)}{{{decl}}}" for times, decl in blocks)
    return f"@keyframes {name}{{{body}}}"


def smil_discrete(attribute: str, steps: list, cycle: float) -> str:
    """A SMIL <animate> that jumps between values at given seconds of one cycle.
    steps: [(seconds, value)], starting at 0 and strictly increasing."""
    values = ";".join(str(value) for _, value in steps)
    times = ";".join(f"{seconds / cycle:.4f}".rstrip("0").rstrip(".") or "0" for seconds, _ in steps)
    return (
        f'<animate attributeName="{attribute}" calcMode="discrete" dur="{num(cycle)}s" '
        f'repeatCount="indefinite" values="{values}" keyTimes="{times}"/>'
    )


# ---------------------------------------------------------------------------
# 1. Canary rollout
# ---------------------------------------------------------------------------

CANARY_W = 860
CELL, GAP = 11, 3
PITCH = CELL + GAP
WEEKDAY_GUTTER = 30
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()

CANARY_CYCLE = 14.0
# (share of the weeks on the new version, second at which that stage starts)
CANARY_STAGES = ((0.01, 1.4), (0.05, 2.6), (0.25, 3.8), (0.50, 5.3), (1.00, 6.9))
COLUMN_STAGGER = 0.045  # seconds between neighbouring columns of one stage
COLUMN_FADE = 0.3       # how long one column takes to switch to its real colours
FLASH_PEAK_AT = 0.08    # each switching column flashes the accent colour briefly
FLASH_LENGTH = 0.7
STAMP_AT = 8.7
ROLLBACK = (11.7, 12.5)  # everything fades back to v1, ready for the next loop
LABEL_FADE = 0.15


def quartile_bounds(counts: list) -> tuple:
    """Upper bounds of levels 1-3: quartiles of the non-zero days (roughly GitHub's rule)."""
    busy = sorted(c for c in counts if c > 0)
    if not busy:
        return (0, 0, 0)

    def quartile(q: float) -> int:
        return busy[max(0, math.ceil(q * len(busy)) - 1)]

    return quartile(0.25), quartile(0.5), quartile(0.75)


def level_of(count: int, bounds: tuple) -> int:
    if count <= 0:
        return 0
    for level, bound in enumerate(bounds, start=1):
        if count <= bound:
            return level
    return 4


def column_flip_times(ncols: int) -> list:
    """Second at which each week column switches to v2: stage by stage, left to right,
    with a small stagger inside each stage."""
    flips, done = [0.0] * ncols, 0
    for share, start in CANARY_STAGES:
        upto = min(ncols, max(done + 1, math.ceil(share * ncols)))
        for k, col in enumerate(range(done, upto)):
            flips[col] = start + k * COLUMN_STAGGER
        done = upto
    return flips


def month_labels(weeks: list) -> list:
    """(column, name) for the first week of each month, skipping crowded labels."""
    labels, previous = [], None
    for col, week in enumerate(weeks):
        month = date.fromisoformat(week[0][0]).month
        if month != previous:
            labels.append((col, MONTHS[month - 1]))
            previous = month
    return [label for k, label in enumerate(labels)
            if k + 1 == len(labels) or labels[k + 1][0] - label[0] >= 3]


def pill(x: float, yc: float, runs: list, size: float, fill: str, stroke: str) -> tuple:
    """A rounded label: runs are (text, attrs) pieces of one mono line. Returns (svg, width)."""
    text = "".join(t for t, _ in runs)
    pad, height = 10, 22
    width = mono_width(text, size) + 2 * pad
    spans = "".join(f"<tspan{attrs}>{esc(t)}</tspan>" for t, attrs in runs)
    svg = (
        f'<rect x="{num(x + .5)}" y="{num(yc - height / 2 + .5)}" width="{num(width - 1)}" '
        f'height="{height - 1}" rx="{num((height - 1) / 2)}" fill="{fill}" stroke="{stroke}"/>'
        f'<text x="{num(x + pad)}" y="{num(yc + size * 0.36)}" font-size="{num(size)}" '
        f'textLength="{num(mono_width(text, size))}" class="fm">{spans}</text>'
    )
    return svg, width


def build_canary(cal: Calendar, health: Health, theme: str) -> str:
    th = THEMES[theme]
    weeks = cal.weeks
    ncols = len(weeks)
    bounds = quartile_bounds([count for week in weeks for _, count, _ in week])

    # Layout: weekday gutter + grid, centred; header above, traffic bar and footer below.
    grid_w, grid_h = ncols * PITCH - GAP, 7 * PITCH - GAP
    left = round((CANARY_W - WEEKDAY_GUTTER - grid_w) / 2)
    right = left + WEEKDAY_GUTTER + grid_w
    gx, gy = left + WEEKDAY_GUTTER, 62
    bar_y, bar_h = gy + grid_h + 9, 4
    foot = bar_y + bar_h + 23  # centre line of the footer row
    height = foot + 25

    flips = column_flip_times(ncols)
    cycle = CANARY_CYCLE
    rb_start, rb_end = ROLLBACK

    css = [
        f".fs{{font-family:{SANS}}}.fm{{font-family:{MONO}}}",
        f".ct{{fill:{th['text']}}}.cm{{fill:{th['muted']}}}.ca{{fill:{th['accent']}}}",
        ".stamp{transform-box:fill-box;transform-origin:50% 50%}",
        ".pulse{animation:pulse 2s ease-in-out infinite}"
        "@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}",
        # Everything in the rollout shares one cycle; each element only names its keyframes.
        f".a{{animation:{num(cycle)}s ease-out infinite}}",
    ]

    def animate(cls: str, stops: list) -> None:
        """Keyframes for elements with class "a <cls>" (the rule below must follow .a)."""
        css.append(f".{cls}{{animation-name:{cls}}}")
        css.append(keyframes(cls, stops, cycle))

    # Each column has its own keyframes with its flip time inside them, so every
    # column runs the same 14 s loop in phase and the restart is seamless.
    peak = th["flash_peak"]
    for col, flip in enumerate(flips):
        animate(f"k{col}", [
            (0, "opacity:0"), (flip, "opacity:0"), (flip + COLUMN_FADE, "opacity:1"),
            (rb_start, "opacity:1"), (rb_end, "opacity:0"), (cycle, "opacity:0"),
        ])
        animate(f"f{col}", [
            (0, "opacity:0"), (flip, "opacity:0"), (flip + FLASH_PEAK_AT, f"opacity:{peak}"),
            (flip + FLASH_LENGTH, "opacity:0"), (cycle, "opacity:0"),
        ])

    # Stage labels: one visible at a time; the base (non-animated) state shows the
    # final one, which is what prefers-reduced-motion displays.
    starts = [start for _, start in CANARY_STAGES] + [STAMP_AT]
    stamp_out = rb_start + 0.4  # the stamp fades out as the rollback begins...
    animate("l0", [             # ...and "v1 serving 100%" takes its place
        (0, "opacity:1"), (starts[0] - LABEL_FADE, "opacity:1"), (starts[0], "opacity:0"),
        (stamp_out, "opacity:0"), (stamp_out + LABEL_FADE, "opacity:1"), (cycle, "opacity:1"),
    ])
    for k in range(len(CANARY_STAGES)):
        start, end = starts[k], starts[k + 1]
        animate(f"l{k + 1}", [
            (0, "opacity:0"), (start, "opacity:0"), (start + LABEL_FADE, "opacity:1"),
            (end - LABEL_FADE, "opacity:1"), (end, "opacity:0"), (cycle, "opacity:0"),
        ])
    hidden = "opacity:0;transform:scale(1.35) rotate(-5deg)"
    landing = "opacity:1;transform:scale(.97) rotate(-1deg)"
    landed = "opacity:1;transform:scale(1) rotate(0deg)"
    gone = "opacity:0;transform:scale(1) rotate(0deg)"
    animate("st", [
        (0, hidden), (STAMP_AT, hidden), (STAMP_AT + 0.16, landing), (STAMP_AT + 0.3, landed),
        (rb_start, landed), (stamp_out, gone), (cycle, gone),
    ])
    css.append("@media (prefers-reduced-motion:reduce){*{animation:none!important}}")

    out = [f"<style>{''.join(css)}</style>"]
    out.append(f'<rect x=".5" y=".5" width="{CANARY_W - 1}" height="{height - 1}" rx="8" '
               f'fill="{th["bg"]}" stroke="{th["border"]}"/>')

    # Header: title on the left, colour legend on the right.
    out.append(
        f'<text x="{left}" y="31" font-size="13" class="fs">'
        f'<tspan class="ca" font-weight="700">canary rollout</tspan>'
        f'<tspan class="cm"> · </tspan><tspan class="ct">{esc(GITHUB_USER)}</tspan>'
        f'<tspan class="cm"> · </tspan><tspan class="ct" font-weight="600">{cal.total:,}</tspan>'
        f'<tspan class="cm"> contributions in the last year</tspan></text>'
    )
    x = right
    for label, colour in (("v2 new", th["levels"][4]), ("v1 old", th["old_levels"][4])):
        x -= mono_width(label, 11)
        out.append(mono_text(x, 31, label, 11, ' class="fm cm"'))
        x -= 15
        out.append(f'<rect x="{num(x)}" y="22" width="10" height="10" rx="2" fill="{colour}"/>')
        x -= 14

    # Month and weekday labels, like GitHub's own graph.
    for col, name in month_labels(weeks):
        out.append(f'<text x="{gx + col * PITCH}" y="{gy - 8}" font-size="10" '
                   f'class="fs cm">{name}</text>')
    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        out.append(f'<text x="{gx - 7}" y="{gy + row * PITCH + 9}" font-size="10" '
                   f'text-anchor="end" class="fs cm">{name}</text>')
    out.append(f'<text x="{gx - 7}" y="{num(bar_y + bar_h + 1.5)}" font-size="10" '
               f'text-anchor="end" class="fs ca">v2</text>')

    # Shared shapes, reused with <use> to keep the file small: one cell per level for
    # v1 ("o") and v2 ("n"), a whole week of empty days per layer, the two traffic-bar
    # segments and the flash that covers a whole week.
    defs = []
    for layer, colours in (("o", th["old_levels"]), ("n", th["levels"])):
        defs += [f'<rect id="{layer}{i}" width="{CELL}" height="{CELL}" rx="2" fill="{c}"/>'
                 for i, c in enumerate(colours)]
        defs.append(f'<g id="{layer}w">'
                    + "".join(f'<use href="#{layer}0" y="{r * PITCH}"/>' for r in range(7)) + "</g>")
    defs.append(f'<rect id="ob" width="{CELL}" height="{bar_h}" rx="1" fill="{th["old_bar"]}"/>')
    defs.append(f'<rect id="nb" width="{CELL}" height="{bar_h}" rx="1" fill="{th["accent"]}"/>')
    defs.append(f'<rect id="fw" width="{CELL + 2}" height="{grid_h + 2}" rx="3"/>')
    out.append(f"<defs>{''.join(defs)}</defs>")

    def week_cells(layer: str, week: list, x: int) -> str:
        """One week of one layer. A complete week starts from the shared column of empty
        days and draws only its busy days on top; partial weeks are drawn day by day."""
        days = [(wd, level_of(count, bounds)) for _, count, wd in week]
        parts = []
        if len(days) == 7:
            parts.append(f'<use href="#{layer}w" x="{x}" y="{gy}"/>')
            days = [(wd, level) for wd, level in days if level]
        parts += [f'<use href="#{layer}{level}" x="{x}" y="{gy + wd * PITCH}"/>' for wd, level in days]
        return "".join(parts)

    # v1: every week, dimmed, plus the grey track of the traffic bar. Always visible.
    old = []
    for col, week in enumerate(weeks):
        x = gx + col * PITCH
        old.append(week_cells("o", week, x) + f'<use href="#ob" x="{x}" y="{bar_y}"/>')
    out.append(f"<g>{''.join(old)}</g>")

    # v2: one group per week (real colours + its slice of the traffic bar). The base
    # state is the final one; the animation hides each group until its column flips.
    new = []
    for col, week in enumerate(weeks):
        x = gx + col * PITCH
        new.append(f'<g class="a k{col}">{week_cells("n", week, x)}'
                   f'<use href="#nb" x="{x}" y="{bar_y}"/></g>')
    out.append(f"<g>{''.join(new)}</g>")

    # The accent flash that sweeps over each column as it switches (hidden at rest).
    flashes = []
    for col, week in enumerate(weeks):
        x = gx + col * PITCH - 1
        if len(week) == 7:
            flashes.append(f'<use href="#fw" x="{x}" y="{gy - 1}" opacity="0" class="a f{col}"/>')
        else:
            top = gy + min(wd for _, _, wd in week) * PITCH - 1
            bottom = gy + max(wd for _, _, wd in week) * PITCH + CELL + 1
            flashes.append(f'<rect x="{x}" y="{top}" width="{CELL + 2}" height="{bottom - top}" '
                           f'rx="3" opacity="0" class="a f{col}"/>')
    out.append(f'<g fill="{th["flash"]}">{"".join(flashes)}</g>')

    # Footer left: the stage label (v1 serving, canary N%, then the stamp).
    plate = dict(fill=th["panel"], stroke=th["border"])
    svg, _ = pill(left, foot, [("v1", ' class="ct"'), (" serving 100%", ' class="cm"')], 12, **plate)
    out.append(f'<g class="a l0" opacity="0">{svg}</g>')
    for k, (share, _) in enumerate(CANARY_STAGES):
        svg, _ = pill(left, foot, [("canary ", ' class="ct"'),
                                   (f"{share:.0%}", ' class="ca" font-weight="700"')], 12, **plate)
        out.append(f'<g class="a l{k + 1}" opacity="0">{svg}</g>')

    stamp_text = "rollout complete · healthy" if health.healthy else "rollout complete"
    stamp_size, sh = 12.5, 26
    sw = mono_width(stamp_text, stamp_size) + 44
    sy = foot - sh / 2
    out.append(
        f'<g class="a stamp st"><rect x="{num(left + .75)}" y="{num(sy + .75)}" width="{num(sw - 1.5)}" '
        f'height="{num(sh - 1.5)}" rx="5" fill="{th["accent_bg"]}" stroke="{th["accent"]}" '
        f'stroke-width="1.5"/>'
        f'<path d="M{num(left + 11)} {num(foot + .5)}l3.5 3.5 7-7.5" fill="none" '
        f'stroke="{th["accent"]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
        + mono_text(left + 30, foot + stamp_size * 0.36, stamp_text, stamp_size,
                    ' class="fm ca" font-weight="700"')
        + "</g>"
    )

    # Footer right: live health readout, right-aligned, pinned to its exact width.
    if health.parts:
        runs = [("health: ", "muted")]
        for k, part in enumerate(health.parts):
            if k:
                runs.append((" · ", "muted"))
            runs.extend(part)
        text = "".join(t for t, _ in runs)
        readout_size = 11.5
        width = mono_width(text, readout_size)
        spans = "".join(f'<tspan class="c{tone[0]}">{esc(t)}</tspan>' for t, tone in runs)
        out.append(f'<circle cx="{num(right - width - 9)}" cy="{num(foot)}" r="3.5" '
                   f'class="ca pulse"/>')
        out.append(f'<text x="{num(right - width)}" y="{num(foot + readout_size * 0.36)}" '
                   f'font-size="{num(readout_size)}" textLength="{num(width)}" class="fm">{spans}</text>')

    readout = ", ".join("".join(t for t, _ in part) for part in health.parts)
    desc = (
        f"Li ZhenXi's last year of GitHub contributions ({cal.total:,}), shown as a canary "
        f"rollout: each week starts on a dim old version and switches to its real colour in "
        f"stages of 1%, 5%, 25%, 50% and 100% of the weeks, while a traffic bar fills up, "
        f"ending with the stamp '{stamp_text}'."
        + (f" Live health of the portfolio site: {readout}." if readout else "")
    )
    return svg_document(CANARY_W, height, "canary", f"Canary rollout of {GITHUB_USER}'s contributions",
                        desc, "\n".join(out))


# ---------------------------------------------------------------------------
# 2. Terminal replay
# ---------------------------------------------------------------------------

TERM_W = 720
TERM_CYCLE = 15.0
TERM_FONT = 14
TERM_CW = TERM_FONT * MONO_EM  # 8.4 px per column
TERM_LH = 19
TERM_BLANK = 10                # blank lines are drawn at about half height
TITLE_H = 34
PAD_X, PAD_TOP, PAD_BOTTOM = 22, 14, 16
BASELINE = 14                  # from the top of a row
TYPE_START = 0.8               # first keystroke
ENTER_PAUSE = 0.4              # after the last keystroke
FIRST_OUTPUT = 0.25            # after Enter
ROW_DELAY, BLANK_DELAY = 0.06, 0.03
CLEAR_AT = 14.5                # screen clears; the empty prompt waits for the next loop
BLINK = 0.5


def keystroke_gap(index: int, ch: str) -> float:
    """Seconds before the next keystroke: steady, with small repeatable variations
    (no randomness, so unchanged data gives byte-identical files)."""
    wobble = ((index * 37) % 11) / 10 - 0.5  # -0.5 .. +0.5
    gap = 0.055 + 0.02 * wobble
    if ch in " -.":
        gap += 0.03
    return gap


def build_terminal(card: Card, theme: str) -> str:
    th = THEMES[theme]
    cw, cycle = TERM_CW, TERM_CYCLE

    # Rows: the command, the card (blank rows kept, at half height) and a new prompt.
    rows = [("cmd", None), ("blank", None)]
    rows += [("out", cells) if cells else ("blank", None) for cells in card.rows]
    rows += [("blank", None), ("prompt", None)]
    tops, y = [], TITLE_H + PAD_TOP
    for kind, _ in rows:
        tops.append(y)
        y += TERM_BLANK if kind == "blank" else TERM_LH
    height = y + PAD_BOTTOM

    # Timeline, in seconds of one cycle.
    keys, t = [], TYPE_START
    for i, ch in enumerate(PROMPT_COMMAND):
        keys.append(t)
        t += keystroke_gap(i, ch)
    enter = keys[-1] + ENTER_PAUSE
    appear, t = {}, enter + FIRST_OUTPUT
    for index, (kind, _) in enumerate(rows):
        if index == 0:
            continue
        appear[index] = t
        t += BLANK_DELAY if kind == "blank" else ROW_DELAY
    prompt_at = appear[len(rows) - 1]

    def row_svg(cells: list, top: float) -> str:
        parts = []
        for col, text, tone, bold in text_pieces(cells):
            weight = ' font-weight="700"' if bold else ""
            parts.append(mono_text(PAD_X + col * cw, top + BASELINE, text, TERM_FONT,
                                   f' class="c{tone[0]}"{weight}'))
        return "".join(parts)

    def dollar(top: float) -> str:
        return mono_text(PAD_X, top + BASELINE, "$", TERM_FONT, ' class="ca" font-weight="700"')

    def cursor(col: int, top: float, extra: str = "", children: str = "") -> str:
        # fill-opacity softens the block; plain opacity is left free for showing/hiding it
        return (f'<rect x="{num(PAD_X + col * cw)}" y="{top + 2}" width="{num(cw)}" height="16" '
                f'class="ca" fill-opacity=".85"{extra}>{children}</rect>')

    command = [Cell(ch, "text", False) for ch in PROMPT_COMMAND]
    cmd_top, prompt_top = tops[0], tops[-1]
    n = len(PROMPT_COMMAND)

    # ---- animated version (SMIL, one 15 s cycle; base values are the final frame) ----
    motion = []
    widths = [(0, 0)] + [(k, num((i + 1) * cw)) for i, k in enumerate(keys)] + [(CLEAR_AT, 0)]
    motion.append(
        f'<clipPath id="typed"><rect x="{num(PAD_X + 2 * cw)}" y="{cmd_top}" '
        f'width="{num(n * cw)}" height="{TERM_LH}">'
        + smil_discrete("width", widths, cycle) + "</rect></clipPath>"
    )
    motion.append(f'<g clip-path="url(#typed)">{row_svg([SPACE, SPACE] + command, cmd_top)}</g>')
    # The typing cursor follows the typed text, blinks while idle, hides after Enter.
    xs = ([(0, num(PAD_X + 2 * cw))] + [(k, num(PAD_X + (i + 3) * cw)) for i, k in enumerate(keys)]
          + [(CLEAR_AT, num(PAD_X + 2 * cw))])
    shown = [(0, 1), (TYPE_START / 2, 0), (keys[0], 1), (enter, 0), (CLEAR_AT, 1)]
    motion.append(cursor(2, cmd_top, ' opacity="0"',
                         smil_discrete("x", xs, cycle) + smil_discrete("opacity", shown, cycle)))
    for index, (kind, cells) in enumerate(rows):
        if kind == "out":
            visible = smil_discrete("opacity", [(0, 0), (appear[index], 1), (CLEAR_AT, 0)], cycle)
            motion.append(f"<g>{visible}{row_svg(cells, tops[index])}</g>")
    visible = smil_discrete("opacity", [(0, 0), (prompt_at, 1), (CLEAR_AT, 0)], cycle)
    motion.append(f"<g>{visible}{dollar(prompt_top)}</g>")
    blink, t, on = [(0, 0)], prompt_at, 1
    while t < CLEAR_AT - 0.05:  # keep keyTimes clearly apart after rounding
        blink.append((t, on))
        on, t = 1 - on, t + BLINK
    blink.append((CLEAR_AT, 0))
    motion.append(cursor(2, prompt_top, "", smil_discrete("opacity", blink, cycle)))

    # ---- still version: the final frame, shown instead under reduced motion ----
    still = [row_svg([SPACE, SPACE] + command, cmd_top)]
    still += [row_svg(cells, tops[i]) for i, (kind, cells) in enumerate(rows) if kind == "out"]
    still += [dollar(prompt_top), cursor(2, prompt_top)]

    radius = 8
    css = (
        f".fs{{font-family:{SANS}}}.fm{{font-family:{MONO}}}"
        f".ct{{fill:{th['text']}}}.cm{{fill:{th['muted']}}}.ca{{fill:{th['accent']}}}"
        ".still{display:none}"
        "@media (prefers-reduced-motion:reduce){.motion{display:none}.still{display:inline}}"
    )
    body = [
        f"<style>{css}</style>",
        f'<rect x=".5" y=".5" width="{TERM_W - 1}" height="{height - 1}" rx="{radius}" fill="{th["bg"]}"/>',
        f'<path d="M.5 {TITLE_H}V{radius + .5}a{radius} {radius} 0 0 1 {radius} -{radius}'
        f'H{TERM_W - radius - .5}a{radius} {radius} 0 0 1 {radius} {radius}V{TITLE_H}Z" '
        f'fill="{th["panel"]}"/>',
        f'<path d="M.5 {TITLE_H + .5}H{TERM_W - .5}" stroke="{th["border"]}"/>',
        f'<rect x=".5" y=".5" width="{TERM_W - 1}" height="{height - 1}" rx="{radius}" fill="none" '
        f'stroke="{th["border"]}"/>',
        "".join(f'<circle cx="{18 + 20 * i}" cy="{TITLE_H / 2}" r="6" fill="{c}"/>'
                for i, c in enumerate(th["dots"])),
        f'<text x="{TERM_W / 2}" y="{TITLE_H / 2 + 4}" font-size="12" text-anchor="middle" '
        f'class="fs cm">zhenxi@profile: ~</text>',
        f'<g class="fm" font-size="{TERM_FONT}">',
        dollar(cmd_top),
        f'<g class="motion">{"".join(motion)}</g>',
        f'<g class="still">{"".join(still)}</g>',
        "</g>",
    ]
    desc = (
        f"A terminal types {PROMPT_COMMAND} and prints the live site's text card:\n"
        + "\n".join(card.lines)
    )
    return svg_document(TERM_W, height, "terminal", f"$ {PROMPT_COMMAND}", desc, "\n".join(body))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def write_all(out_dir: str, files: dict) -> None:
    """Write every file next to its target first, then swap them all in."""
    os.makedirs(out_dir, exist_ok=True)
    staged = []
    for name, content in files.items():
        tmp = os.path.join(out_dir, f".{name}.tmp")
        with open(tmp, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        staged.append((tmp, os.path.join(out_dir, name)))
    for tmp, final in staged:
        os.replace(tmp, final)


def main(argv: list) -> int:
    if len(argv) != 2:
        print("usage: animations.py OUT_DIR", file=sys.stderr)
        return 2
    out_dir = argv[1]
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        print("error: set GITHUB_TOKEN or GH_TOKEN; nothing written", file=sys.stderr)
        return 1
    try:
        calendar = fetch_calendar(token)
        card = parse_card(fetch_card_text())
    except FetchError as err:
        print(f"error: {err}; nothing written, the previous images stay", file=sys.stderr)
        return 1
    health = read_health()

    files = {}
    for theme in THEMES:
        files[f"canary-{theme}.svg"] = build_canary(calendar, health, theme)
        files[f"terminal-{theme}.svg"] = build_terminal(card, theme)
    too_big = [name for name, svg in files.items() if len(svg.encode()) > MAX_SVG_BYTES]
    if too_big:
        print(f"error: {', '.join(too_big)} over {MAX_SVG_BYTES} bytes; nothing written",
              file=sys.stderr)
        return 1

    write_all(out_dir, files)
    for name, svg in files.items():
        print(f"wrote {os.path.join(out_dir, name)} ({len(svg.encode()):,} bytes)")
    if not health.parts:
        print("note: health readout left out (status and SLO unavailable)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
