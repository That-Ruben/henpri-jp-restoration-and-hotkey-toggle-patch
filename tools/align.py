"""Order-based alignment between western and JP-release .ast scripts.

Western and JP builds use different block-label schemes, so blocks are
paired by document order among text-bearing blocks, then verified with
voice-file anchors and page counts. Spoiler-safe: never prints text.

analyze(path) -> (source_text, [block dicts in document order])
pair_and_verify(west, jp)  -> (pairs, problems)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from astlib import Parser, LuaTable

LANGS = ("ja", "en", "cn", "tw")


def analyze(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        text = f.read()
    idx = text.find("ast")
    p = Parser(text)
    p.i = text.find("{", idx)
    spans = {}

    def hook(ks, s, e):
        if len(ks) == 3 and ks[1] == "text" and ks[2] in LANGS:
            spans[(ks[0], ks[2])] = (s, e)

    p.span_hook = hook
    tbl = p.parse_table()

    blocks = []
    savetitles = []
    for kind, k in tbl.order:
        if kind != "h":
            continue
        b = tbl.hash[k]
        if not isinstance(b, LuaTable):
            continue
        # savetitle command entries (positional command tables)
        for cmd in b.array:
            if (isinstance(cmd, LuaTable) and cmd.array
                    and cmd.array[0] == "savetitle"):
                savetitles.append({
                    "label": k,
                    "text": cmd.hash.get("text"),
                    "ja": cmd.hash.get("ja"),
                })
        tx = b.hash.get("text")
        if not isinstance(tx, LuaTable):
            continue
        entry = {"label": k, "pages": {}, "vo": []}
        vo = tx.hash.get("vo")
        if isinstance(vo, LuaTable):
            entry["vo"] = [v.hash.get("file") for v in vo.array
                           if isinstance(v, LuaTable)]
        for ln in LANGS:
            v = tx.hash.get(ln)
            if isinstance(v, LuaTable):
                entry["pages"][ln] = len(v.array)
                entry[ln + "_span"] = spans.get((k, ln))
        if entry["pages"]:
            blocks.append(entry)
    return text, blocks, savetitles


def pair_and_verify(name, west_blocks, jp_blocks):
    """Returns (pairs, problems). pairs = list of (west_block, jp_block)."""
    problems = []
    w = [b for b in west_blocks if "ja" in b["pages"]]
    j = [b for b in jp_blocks if "ja" in b["pages"]]
    if len(w) != len(j):
        problems.append(f"{name}: text-block count west={len(w)} jp={len(j)}")
        return [], problems
    pairs = []
    for wb, jb in zip(w, j):
        tag = f"{name}:{wb['label']}<->{jb['label']}"
        if wb["vo"] != jb["vo"]:
            problems.append(f"{tag}: vo anchors differ {wb['vo']} vs {jb['vo']}")
            continue
        if wb["pages"].get("en") != jb["pages"]["ja"]:
            problems.append(
                f"{tag}: page count en={wb['pages'].get('en')} "
                f"jp-ja={jb['pages']['ja']}")
            continue
        pairs.append((wb, jb))
    return pairs, problems
