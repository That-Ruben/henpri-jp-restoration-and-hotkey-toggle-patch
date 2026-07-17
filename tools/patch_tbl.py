"""Add the Japanese option to the config-screen language row in
list_windows_<lang>.tbl files.

- Adds a `lang_ja` toggle button to groups ui_config1_en/_cn/_tw
- Rewrites p2 (mutual-exclusion lists) on all language buttons
- Appends a new group ui_config1_ja (shown while the game runs in Japanese),
  cloned from ui_config1_en with the obj/toggle roles swapped.
- Adds sub01/sub02 font entries for the dual-language display (K key):
  smaller text above the message text, using the JP-capable main-text font
  for every entry since the sub slot always holds ja or en.
- Fixes the ja backlog text geometry: the remaster shifted backlog text
  right (left=397) to clear the now-solid speaker portrait, but only for
  the shipped languages; the ja sub-entries kept the old JP layout
  (left=130) where the portrait was faded out behind the text.
"""
import re
import sys

ORDER = ("en", "cn", "tw", "ja")
X = {"en": 494, "cn": 700, "tw": 906, "ja": 1112}
BTNID = {"en": 23, "cn": 24, "tw": 25, "ja": 26}

SUB_ATTRS = ('left=408, top=550, width=800, height=110, align="left", '
             'color="0xffffff", outline=2, outlinecolor="0x000000", '
             'spacetop=0, spacemiddle=-8, spacebottom=-4, kerning=-2, '
             'show="none", indent="indent", hung=1, ruby="font06", '
             'rubysize=13, rubyoutline=1, prohibit=1, layered=1,},')


def sub_block(name, repl=()):
    rows = []
    for lang, size in (("ja", 28), ("en", 27), ("tw", 28), ("cn", 28)):
        attrs = SUB_ATTRS
        for old, new in repl:
            attrs = attrs.replace(old, new)
        rows.append(f'\t\t\t{lang} = {{ face="font06", size={size}, ' + attrs)
    return [f"\t\t{name} = {{"] + rows + ["\t\t},"]


def lang_line(lang, obj):
    others = "|".join("lang_" + o for o in ORDER if o != lang)
    common = (f'\t\tlang_{lang} = {{ name="lang_{lang}", '
              f'file="config1/bt_language_{lang}", id="z.bt.{BTNID[lang]}", '
              f'x={X[lang]}, y=518, w=182, h=48, ')
    mid = (f'def="language", exec="config_toggle", p1="{lang}", '
           f'p2="{others}", p3="{lang}", p4="conf_langchange", '
           f'dir="height", cx="0", ')
    if obj:
        return (common + 'com="obj", ' + mid +
                'cy="100", cw="182", ch="50", clip="0,100,182,48", '
                'clip_d="0,250,182,48", },')
    return (common + 'com="toggle", ' + mid +
            'cy="0", cw="182", ch="50", clip="0,0,182,48", '
            'clip_a="0,50,182,48", clip_c="0,100,182,48", '
            'clip_d="0,150,182,48", },')


def find_group(lines, name):
    start = None
    for i, ln in enumerate(lines):
        if re.match(rf"\t{name}\s*=\s*\{{\s*$", ln):
            start = i
        elif start is not None and ln.rstrip("\r\n") == "\t},":
            return start, i
    raise ValueError(f"group {name} not found")


def patch_group(lines, gname, current):
    """Rewrite the language-button lines inside one ui_config1_* group."""
    start, end = find_group(lines, gname)
    body = lines[start : end + 1]
    eol = "\r\n" if body[0].endswith("\r\n") else "\n"
    out = []
    seen = set()
    for ln in body:
        m = re.match(r"\t\tlang_(en|cn|tw|ja) = ", ln)
        if m:
            l = m.group(1)
            seen.add(l)
            out.append(lang_line(l, obj=(l == current)) + eol)
            if l == "tw" and "ja" not in seen and current != "ja":
                out.append(lang_line("ja", obj=False) + eol)
                seen.add("ja")
        else:
            out.append(ln)
    if "ja" not in seen:
        raise ValueError(f"{gname}: no tw line to anchor ja insertion")
    lines[start : end + 1] = out


def insert_sub_entries(lines):
    """Insert sub01/sub02 before every adv01/adv02 font entry (the font
    sections appear twice per tbl; Lua last-wins, both get the entries)."""
    eol = "\r\n" if lines[0].endswith("\r\n") else "\n"
    out = []
    n1 = n2 = 0
    for ln in lines:
        if ln.startswith("\t\tadv01 = {"):
            out.extend(s + eol for s in sub_block("sub01"))
            n1 += 1
        elif ln.startswith("\t\tadv02 = {"):
            out.extend(s + eol for s in sub_block(
                "sub02", (("left=408", "left=1200"), ("top=550", "top=2070"),
                          ("width=800", "width=820"))))
            n2 += 1
        out.append(ln)
    assert n1 >= 1, "no adv01 font entry found"
    lines[:] = out
    print(f"  sub01 x{n1}, sub02 x{n2}")


# old-JP-layout ja geometry -> remaster geometry (matching cn/tw)
BLOG_JA_FIX = (
    ("left=130, top=13, width=600", "left=397, top=0, width=600"),   # logname
    ("left=130, top=58, width=800", "left=397, top=36, width=800"),  # backlog
)


def fix_backlog_ja(lines):
    n = 0
    for i, ln in enumerate(lines):
        for old, new in BLOG_JA_FIX:
            if old in ln:
                lines[i] = ln.replace(old, new)
                n += 1
    assert n == 4, f"expected 4 ja backlog-geometry lines, fixed {n}"
    print(f"  ja backlog geometry x{n}")


def patch_file(path_in, path_out):
    with open(path_in, "r", encoding="utf-8", newline="") as f:
        lines = f.readlines()
    for l in ("en", "cn", "tw"):
        patch_group(lines, f"ui_config1_{l}", current=l)
    insert_sub_entries(lines)
    fix_backlog_ja(lines)

    # build ui_config1_ja from the (patched) en group
    start, end = find_group(lines, "ui_config1_en")
    eol = "\r\n" if lines[start].endswith("\r\n") else "\n"
    ja_group = [f"\tui_config1_ja = {{{eol}"]
    for ln in lines[start + 1 : end + 1]:
        m = re.match(r"\t\tlang_(en|cn|tw|ja) = ", ln)
        if m:
            l = m.group(1)
            ja_group.append(lang_line(l, obj=(l == "ja")) + eol)
        else:
            ja_group.append(ln)
    # insert after ui_config1_tw group
    ts, te = find_group(lines, "ui_config1_tw")
    lines[te + 1 : te + 1] = ja_group
    with open(path_out, "w", encoding="utf-8", newline="") as f:
        f.writelines(lines)
    print(f"patched {path_out}")


if __name__ == "__main__":
    patch_file(sys.argv[1], sys.argv[2])
