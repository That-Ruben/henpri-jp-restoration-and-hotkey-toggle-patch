"""Structural audit of western-release scripts (no story text in output).

Per script: block count, text-block count, language coverage, whether ja
slots are placeholders, page-count mismatches between languages, and names
(name= keys) usage.
"""
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from astlib import parse_ast_file, block_text_summary, LuaTable, PLACEHOLDER

LANGS = ["ja", "en", "cn", "tw"]


def audit(paths):
    grand = dict(files=0, blocks=0, textblocks=0, ja_placeholder=0, ja_real=0,
                 missing_lang=0, pagecount_mismatch=0, parse_errors=0)
    problems = []
    for path in sorted(paths):
        name = os.path.basename(path)
        try:
            _, ast, _ = parse_ast_file(path)
        except Exception as exc:
            grand["parse_errors"] += 1
            problems.append(f"{name}: PARSE ERROR {exc}")
            continue
        grand["files"] += 1
        for label, block in ast.hash.items():
            if not isinstance(block, LuaTable):
                continue
            grand["blocks"] += 1
            tx = block_text_summary(block)
            if tx is None:
                continue
            grand["textblocks"] += 1
            missing = [l for l in LANGS if l not in tx]
            if missing:
                grand["missing_lang"] += 1
                problems.append(f"{name}:{label}: missing langs {missing}")
            # ja placeholder check: look at raw strings
            raw = block.hash["text"].hash.get("ja")
            if isinstance(raw, LuaTable):
                strings = []
                for page in raw.array:
                    if isinstance(page, LuaTable):
                        strings += [x for x in page.array if isinstance(x, str)]
                if strings and all(s == PLACEHOLDER for s in strings):
                    grand["ja_placeholder"] += 1
                elif strings:
                    grand["ja_real"] += 1
                    problems.append(f"{name}:{label}: ja has non-placeholder text")
            # page count comparison en vs cn vs tw
            counts = {l: len(v) for l, v in tx.items() if l in LANGS}
            if len(set(counts.values())) > 1:
                grand["pagecount_mismatch"] += 1
                problems.append(f"{name}:{label}: page counts differ {counts}")
    print("== aggregate ==")
    for k, v in grand.items():
        print(f"{k:20} {v}")
    print(f"\n== problems ({len(problems)}) ==")
    for p in problems[:80]:
        print(p)
    if len(problems) > 80:
        print(f"... and {len(problems) - 80} more")


if __name__ == "__main__":
    audit(glob.glob(sys.argv[1]))
