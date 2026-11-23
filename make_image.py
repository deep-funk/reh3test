#!/usr/bin/env python3
"""Render the 24 November 2026 front page. Deterministic: no clock, no random, no network."""

import itertools
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SIZE = 1024
MARGIN = 54
MEASURE = SIZE - 2 * MARGIN

INK = "#101012"
PAPER = "#f8f3e6"
ACCENT = "#aa2020"
HAIR = "#c6c1b8"
GREY = "#5f5b54"

FONT_DIR = Path("/usr/share/fonts/truetype/liberation")
BOLD = str(FONT_DIR / "LiberationSans-Bold.ttf")
REGULAR = str(FONT_DIR / "LiberationSans-Regular.ttf")

LEAD = "Markets hold their breath as the chip war widens"
CAPTION = "VOLUME THINS AS TRADERS WAIT ON GUIDANCE"
COLUMNS = [
    ("CHIP RULES", "Brussels and Washington add curbs; suppliers brace."),
    ("STORMS", "Gulf grids stage rolling blackouts as lines come down."),
    ("EXCHANGES", "The thinnest session in eleven weeks."),
]
FOOTER = "DRAWN FROM THE DAY'S REPORTING \u00b7 NO NETWORK"

BAR_HEIGHTS = [24, 36, 30, 45, 54, 41, 57, 70, 63, 77, 69, 84, 62, 48, 39, 32]


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap_words(words, fnt, width):
    lines, cur = [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if fnt.getlength(trial) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    while len(lines) > 1 and len(lines[-1].split()) == 1 and len(lines[-2].split()) > 2:
        lines[-1] = lines[-2].split()[-1] + " " + lines[-1]
        lines[-2] = " ".join(lines[-2].split()[:-1])
    return lines


def fit_lead(draw):
    """Largest size whose 2-3 line wrap reaches 88% of the measure with no lone word."""
    words = LEAD.split()
    floor = 0.88 * MEASURE
    for size in range(70, 39, -1):
        fnt = font(BOLD, size)
        best = None
        for count in (2, 3):
            for cuts in itertools.combinations(range(1, len(words)), count - 1):
                bounds = (0,) + cuts + (len(words),)
                lines = [" ".join(words[a:b]) for a, b in zip(bounds, bounds[1:])]
                if any(len(line.split()) == 1 for line in lines):
                    continue
                widths = [fnt.getlength(line) for line in lines]
                if max(widths) > MEASURE:
                    continue
                if max(widths) < floor:
                    continue
                score = (max(widths), min(widths))
                if best is None or score > best[0]:
                    best = (score, lines)
        if best:
            return size, best[1]
    return 40, wrap_words(words, font(BOLD, 40), MEASURE)


def main():
    img = Image.new("RGB", (SIZE, SIZE), PAPER)
    draw = ImageDraw.Draw(img)

    lead_size, lead_lines = fit_lead(draw)
    lead_leading = round(lead_size * 1.11)
    f_lead = font(BOLD, lead_size)
    f_mast = font(BOLD, 50)
    f_world = font(BOLD, 22)
    f_date = font(REGULAR, 20)
    f_tick = font(REGULAR, 12)
    f_caption = font(REGULAR, 17)
    f_kicker = font(BOLD, 15)
    f_body = font(REGULAR, 34)
    f_foot = font(REGULAR, 17)

    # Top bar.
    draw.rectangle((0, 0, SIZE, 11), fill=INK)

    # Masthead band.
    draw.text((MARGIN, 18), "THE DAY", font=f_mast, fill=INK)
    draw.text((SIZE - MARGIN, 22), "WORLD NEWS", font=f_world, fill=ACCENT, anchor="ra")
    draw.text((SIZE - MARGIN, 52), "24 NOVEMBER 2026", font=f_date, fill=GREY, anchor="ra")

    draw.rectangle((MARGIN, 92, SIZE - MARGIN, 95), fill=INK)

    # Lead headline, filling the measure.
    y = 114
    for line in lead_lines:
        draw.text((MARGIN, y), line, font=f_lead, fill=INK)
        y += lead_leading

    draw.line((MARGIN, 282, SIZE - MARGIN, 282), fill=HAIR, width=1)

    # Volume strip.
    base = 396
    cell = MEASURE / len(BAR_HEIGHTS)
    bar_w = 49
    for i, height in enumerate(BAR_HEIGHTS):
        x0 = MARGIN + i * cell + (cell - bar_w) / 2
        colour = ACCENT if i >= len(BAR_HEIGHTS) - 3 else INK
        draw.rectangle((round(x0), base - height, round(x0 + bar_w), base), fill=colour)
    draw.rectangle((MARGIN, base, SIZE - MARGIN, base + 1), fill=INK)

    # Tick row.
    ticks = ["00", "06", "12", "18"]
    for i, tick in enumerate(ticks):
        x = MARGIN + (MEASURE - f_tick.getlength(tick)) * i / 3
        draw.text((x, 403), tick, font=f_tick, fill=GREY)

    draw.text((MARGIN, 428), CAPTION, font=f_caption, fill=GREY)

    draw.rectangle((MARGIN, 452, SIZE - MARGIN, 453), fill=INK)

    # Three columns, centred in the lower well.
    gutter = 24
    col_w = (MEASURE - 2 * gutter) / 3
    blocks = []
    for _, body in COLUMNS:
        blocks.append(wrap_words(body.split(), f_body, col_w))
    block_h = [30 + len(lines) * 41 for lines in blocks]
    top = 470 + (906 - 470 - max(block_h)) // 2

    for i, ((kicker, _), lines) in enumerate(zip(COLUMNS, blocks)):
        x = MARGIN + i * (col_w + gutter)
        draw.rectangle((round(x), top + 8, round(x) + 9, top + 17), fill=ACCENT)
        draw.text((round(x) + 16, top), kicker, font=f_kicker, fill=INK)
        cy = top + 30
        for line in lines:
            draw.text((round(x), cy), line, font=f_body, fill=INK)
            cy += 41

    draw.rectangle((MARGIN, 916, SIZE - MARGIN, 917), fill=INK)
    draw.text((MARGIN, 942), FOOTER, font=f_foot, fill=GREY)

    img.save("entry.png", format="PNG", optimize=True)


if __name__ == "__main__":
    main()
