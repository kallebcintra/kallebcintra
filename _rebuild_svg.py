"""Rebuild SVGs: keys left-aligned, values right-aligned to a shared end column."""
from pathlib import Path
from lxml import etree

ascii_path = Path(
    r"c:\Users\cassi\.cursor\projects\c-Users-cassi-Documents-projetos-pessoais-kallebcintra"
    r"\attachments\bb28c8fa-d9f1-4836-be56-88d892ceaa9b\ascii-art.txt"
)
lines = [l.rstrip("\n") for l in ascii_path.read_text(encoding="utf-8").splitlines()]
while lines and not lines[-1].strip():
    lines.pop()
COL_W = max(len(l) for l in lines)
lines = [l.ljust(COL_W) for l in lines]

WIDTH = 985
HEIGHT = 530
INFO_X = 390
PAD = 15
# Fixed printable width of each info line (from ". " / title through last value char).
# Values are right-aligned inside this width; dots absorb the slack.
LINE_WIDTH = 58

LEFT_BUDGET = INFO_X - PAD - 40
RAW_ASCII_W = COL_W * (16 * 0.55 * 1.09)
ASCII_SCALE = LEFT_BUDGET / RAW_ASCII_W
ASCII_START_Y = 30
ASCII_END_Y = 510
ASCII_STEP = (ASCII_END_Y - ASCII_START_Y) / ((len(lines) - 1) * ASCII_SCALE)

THEMES = {
    "light_mode.svg": {
        "bg": "#f6f8fa",
        "fg": "#24292f",
        "key": "#953800",
        "value": "#0a3069",
        "add": "#1a7f37",
        "del": "#cf222e",
        "cc": "#c2cfde",
    },
    "dark_mode.svg": {
        "bg": "#161b22",
        "fg": "#c9d1d9",
        "key": "#ffa657",
        "value": "#a5d6ff",
        "add": "#3fb950",
        "del": "#f85149",
        "cc": "#616e7f",
    },
}


def make_dots(prefix_len: int, value_len: int) -> str:
    """Dots (+ surrounding spaces) so prefix+dots+value == LINE_WIDTH."""
    room = LINE_WIDTH - prefix_len - value_len
    if room <= 0:
        return ""
    if room == 1:
        return " "
    if room == 2:
        return "  "
    # " " + dots + " "
    n = room - 2
    return " " + ("." * n) + " "


def make_sep(title: str) -> str:
    """Dashes after a section title so the line ends on LINE_WIDTH."""
    room = LINE_WIDTH - len(title)
    if room <= 0:
        return ""
    if room == 1:
        return " "
    # leading space + dashes (em dash lookalike of Andrew's separators)
    return " " + ("—" * (room - 1))


def append_tspan(parent, text=None, class_=None, id_=None, x=None, y=None):
    t = etree.SubElement(parent, "tspan")
    if x is not None:
        t.set("x", str(x))
    if y is not None:
        t.set("y", str(y))
    if class_:
        t.set("class", class_)
    if id_:
        t.set("id", id_)
    if text is not None:
        t.text = text
    return t


def build(path: str, theme: dict) -> None:
    svg = etree.Element("svg", nsmap={None: "http://www.w3.org/2000/svg"})
    svg.set("font-family", "ConsolasFallback,Consolas,monospace")
    svg.set("width", f"{WIDTH}px")
    svg.set("height", f"{HEIGHT}px")
    svg.set("font-size", "16px")

    style = etree.SubElement(svg, "style")
    style.text = f"""
@font-face {{
src: local('Consolas'), local('Consolas Bold');
font-family: 'ConsolasFallback';
font-display: swap;
-webkit-size-adjust: 109%;
size-adjust: 109%;
}}
.key {{fill: {theme['key']};}}
.value {{fill: {theme['value']};}}
.addColor {{fill: {theme['add']};}}
.delColor {{fill: {theme['del']};}}
.cc {{fill: {theme['cc']};}}
text, tspan {{white-space: pre;}}
"""
    rect = etree.SubElement(svg, "rect")
    rect.set("width", f"{WIDTH}px")
    rect.set("height", f"{HEIGHT}px")
    rect.set("fill", theme["bg"])
    rect.set("rx", "15")

    group = etree.SubElement(svg, "g")
    group.set("transform", f"translate({PAD},{ASCII_START_Y}) scale({ASCII_SCALE:.5f})")
    ascii_text = etree.SubElement(group, "text")
    ascii_text.set("fill", theme["fg"])
    ascii_text.set("class", "ascii")
    for i, line in enumerate(lines):
        t = etree.SubElement(ascii_text, "tspan")
        t.set("x", "0")
        t.set("y", f"{i * ASCII_STEP:.2f}")
        t.text = line

    info = etree.SubElement(svg, "text")
    info.set("x", str(INFO_X))
    info.set("y", "30")
    info.set("fill", theme["fg"])

    def field(y, keys, value, value_id=None, dots_id=None):
        key_text = ".".join(keys)
        prefix = f". {key_text}:"
        dots = make_dots(len(prefix), len(value))
        assert len(prefix) + len(dots) + len(value) == LINE_WIDTH, (
            key_text, len(prefix), len(dots), len(value),
            len(prefix) + len(dots) + len(value),
        )
        append_tspan(info, ". ", class_="cc", x=INFO_X, y=y)
        for i, k in enumerate(keys):
            kt = append_tspan(info, k, class_="key")
            if i < len(keys) - 1:
                kt.tail = "."
            else:
                kt.tail = ":"
        append_tspan(info, dots, class_="cc", id_=dots_id)
        append_tspan(info, value, class_="value", id_=value_id)

    def blank(y):
        append_tspan(info, ". ", class_="cc", x=INFO_X, y=y)

    def section(y, title):
        sep = make_sep(title)
        assert len(title) + len(sep) == LINE_WIDTH, (title, len(title) + len(sep))
        t = append_tspan(info, title, x=INFO_X, y=y)
        t.tail = sep

    # Title — right edge matches value column
    title = "kalleb@cintra"
    title_sep = make_sep(title)
    assert len(title) + len(title_sep) == LINE_WIDTH
    t = append_tspan(info, title, x=INFO_X, y=30)
    t.tail = title_sep

    field(50, ["OS"], "Windows 11")
    field(70, ["Uptime"], "23 years, 1 month, 20 days", value_id="age_data", dots_id="age_data_dots")
    field(90, ["Host"], "getCoders / CEIA")
    field(110, ["Kernel"], "FDE & AI Engineer")
    field(130, ["IDE"], "Cursor, IntelliJ IDEA")
    blank(150)
    field(170, ["Languages", "Programming"], "Java, TypeScript, Python, C")
    field(190, ["Languages", "Computer"], "HTML, CSS, Angular, Docker")
    field(210, ["Languages", "Real"], "Portuguese, English (C1)")
    blank(230)
    blank(250)
    blank(270)
    section(310, "- Contact")
    field(330, ["Email", "Personal"], "mateuskallebswe@gmail.com")
    field(350, ["LinkedIn"], "Mateus Kalleb Cintra Bastos")
    field(370, ["Instagram"], "kallebcintra")
    section(450, "- GitHub Stats")

    def fit_stats(y, parts_builder):
        """Build a stats line and pad leading dots so the line ends on LINE_WIDTH."""
        # parts_builder returns list of (kind, text, id) and we measure plain length
        raise NotImplementedError

    # Stats: build plain string length then inject leading filler after ". "
    def stats_line(y, build_fn):
        """build_fn(row_append) adds tspans; returns total printable length of added content."""
        # First pass: construct offline to measure — simpler to hardcode known layouts
        pass

    # --- Repos line ---
    # Template: ". Repos: {dots1}{repo} {{Contributed: {contrib}}} | Stars:{dots2}{stars}"
    # Keep internal structure; pad with repo_data_dots / star_data_dots so TOTAL == LINE_WIDTH
    repo, contrib, stars = "0", "0", "0"
    # Fixed pieces (without the adjustable dots)
    # ". Repos:" + dots1 + repo + " {Contributed: " + contrib + "} | Stars:" + dots2 + stars
    fixed_without_dots = (
        len(". Repos:")
        + len(repo)
        + len(" {Contributed: ")
        + len(contrib)
        + len("} | Stars:")
        + len(stars)
    )
    # Split remaining room between the two dot fields (favor star dots like Andrew)
    room = LINE_WIDTH - fixed_without_dots
    # minimum " " for each dots field if room is tight
    d1_room = max(2, min(6, room // 3))
    d2_room = max(2, room - d1_room)

    def dots_n(room_n):
        if room_n <= 0:
            return ""
        if room_n == 1:
            return " "
        if room_n == 2:
            return "  "
        return " " + ("." * (room_n - 2)) + " "

    d1 = dots_n(d1_room)
    d2 = dots_n(d2_room)
    assert fixed_without_dots + len(d1) + len(d2) == LINE_WIDTH, (
        fixed_without_dots, len(d1), len(d2), fixed_without_dots + len(d1) + len(d2)
    )

    append_tspan(info, ". ", class_="cc", x=INFO_X, y=470)
    t = append_tspan(info, "Repos", class_="key")
    t.tail = ":"
    append_tspan(info, d1, class_="cc", id_="repo_data_dots")
    v = append_tspan(info, repo, class_="value", id_="repo_data")
    v.tail = " {"
    t = append_tspan(info, "Contributed", class_="key")
    t.tail = ": "
    v = append_tspan(info, contrib, class_="value", id_="contrib_data")
    v.tail = "} | "
    t = append_tspan(info, "Stars", class_="key")
    t.tail = ":"
    append_tspan(info, d2, class_="cc", id_="star_data_dots")
    append_tspan(info, stars, class_="value", id_="star_data")

    # --- Commits line ---
    commits, followers = "0", "0"
    fixed_without_dots = (
        len(". Commmits:")
        + len(commits)
        + len(" | Followers:")
        + len(followers)
    )
    room = LINE_WIDTH - fixed_without_dots
    d1_room = max(2, room // 2)
    d2_room = max(2, room - d1_room)
    d1, d2 = dots_n(d1_room), dots_n(d2_room)
    # Adjust if off-by due to rounding
    while fixed_without_dots + len(d1) + len(d2) < LINE_WIDTH:
        d2 = dots_n(len(d2) + 1) if d2 else dots_n(3)
    while fixed_without_dots + len(d1) + len(d2) > LINE_WIDTH and len(d2) > 2:
        d2 = dots_n(len(d2) - 1)
    assert fixed_without_dots + len(d1) + len(d2) == LINE_WIDTH, (
        fixed_without_dots + len(d1) + len(d2)
    )

    append_tspan(info, ". ", class_="cc", x=INFO_X, y=490)
    t = append_tspan(info, "Commmits", class_="key")
    t.tail = ":"
    append_tspan(info, d1, class_="cc", id_="commit_data_dots")
    v = append_tspan(info, commits, class_="value", id_="commit_data")
    v.tail = " | "
    t = append_tspan(info, "Followers", class_="key")
    t.tail = ":"
    append_tspan(info, d2, class_="cc", id_="follower_data_dots")
    append_tspan(info, followers, class_="value", id_="follower_data")

    # --- LOC line ---
    loc, loc_add, loc_del = "0", "0", "0"
    # ". Lines of Code on GitHub:" + dots + loc + " ( " + add + "++" + ", " + del_dots + del + "--" + " )"
    fixed_without_dots = (
        len(". Lines of Code on GitHub:")
        + len(loc)
        + len(" ( ")
        + len(loc_add)
        + len("++")
        + len(", ")
        + len(loc_del)
        + len("--")
        + len(" )")
    )
    # loc_del_dots is a separate small spacer; keep as single space in fixed, absorb rest in loc_data_dots
    # Actually fixed above includes no loc_del_dots. Andrew has loc_del_dots as " " sometimes.
    # Include a 1-char del spacer in the adjustable part.
    room = LINE_WIDTH - fixed_without_dots - 1  # reserve 1 for loc_del_dots
    d_loc = dots_n(max(2, room))
    # tweak
    while fixed_without_dots + len(d_loc) + 1 < LINE_WIDTH:
        d_loc = dots_n(len(d_loc) + 1) if d_loc else dots_n(3)
    while fixed_without_dots + len(d_loc) + 1 > LINE_WIDTH and len(d_loc) > 0:
        d_loc = d_loc[1:] if len(d_loc) > 1 else ""
    assert fixed_without_dots + len(d_loc) + 1 == LINE_WIDTH, (
        fixed_without_dots + len(d_loc) + 1
    )

    append_tspan(info, ". ", class_="cc", x=INFO_X, y=510)
    t = append_tspan(info, "Lines of Code on GitHub", class_="key")
    t.tail = ":"
    append_tspan(info, d_loc, class_="cc", id_="loc_data_dots")
    v = append_tspan(info, loc, class_="value", id_="loc_data")
    v.tail = " ( "
    append_tspan(info, loc_add, class_="addColor", id_="loc_add")
    t = append_tspan(info, "++", class_="addColor")
    t.tail = ", "
    append_tspan(info, " ", id_="loc_del_dots")
    append_tspan(info, loc_del, class_="delColor", id_="loc_del")
    t = append_tspan(info, "--", class_="delColor")
    t.tail = " )"

    etree.ElementTree(svg).write(path, encoding="utf-8", xml_declaration=True)
    print(f"wrote {path} scale={ASCII_SCALE:.3f} line_width={LINE_WIDTH}")


def main():
    ids = [
        "age_data", "age_data_dots", "repo_data", "repo_data_dots", "contrib_data",
        "star_data", "star_data_dots", "commit_data", "commit_data_dots",
        "follower_data", "follower_data_dots", "loc_data", "loc_data_dots",
        "loc_add", "loc_del", "loc_del_dots",
    ]
    for fname, theme in THEMES.items():
        build(fname, theme)
        root = etree.parse(fname).getroot()
        for eid in ids:
            assert root.find(f".//*[@id='{eid}']") is not None, f"{fname} missing {eid}"
        print(fname, "ok")


if __name__ == "__main__":
    main()
