"""Add the Japanese option to the config-screen language row in
list_windows_<lang>.tbl files.

- Adds a `lang_ja` toggle button to groups ui_config1_en/_cn/_tw
- Rewrites p2 (mutual-exclusion lists) on all language buttons
- Appends a new group ui_config1_ja (shown while the game runs in Japanese),
  cloned from ui_config1_en with the obj/toggle roles swapped.
"""
import re
import sys

ORDER = ("en", "cn", "tw", "ja")
X = {"en": 494, "cn": 700, "tw": 906, "ja": 1112}
BTNID = {"en": 23, "cn": 24, "tw": 25, "ja": 26}


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


def patch_file(path_in, path_out):
    with open(path_in, "r", encoding="utf-8", newline="") as f:
        lines = f.readlines()
    for l in ("en", "cn", "tw"):
        patch_group(lines, f"ui_config1_{l}", current=l)

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
