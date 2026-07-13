"""Alignment audit western vs JP scripts. Stats only, no story text.

Usage: python audit_jp.py WEST_DIR JP_DIR
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from align import analyze, pair_and_verify

def main(west_dir, jp_dir):
    west_files = sorted(f for f in os.listdir(west_dir) if f.endswith(".ast"))
    jp_files = set(f for f in os.listdir(jp_dir) if f.endswith(".ast"))
    tot = dict(files_ok=0, files_partial=0, files_missing=0,
               blocks_paired=0, blocks_failed=0,
               savetitle_match=0, savetitle_diff=0)
    problems = []
    for name in west_files:
        if not name.startswith("d"):
            continue  # brandlogo/gamestart/pack have no dialogue
        if name not in jp_files:
            tot["files_missing"] += 1
            problems.append(f"{name}: not in JP release")
            continue
        _, wb, wst = analyze(os.path.join(west_dir, name))
        _, jb, jst = analyze(os.path.join(jp_dir, name))
        pairs, probs = pair_and_verify(name, wb, jb)
        tot["blocks_paired"] += len(pairs)
        nfail = sum(1 for b in wb if "ja" in b["pages"]) - len(pairs)
        tot["blocks_failed"] += nfail
        if probs:
            tot["files_partial"] += 1
            problems += probs
        else:
            tot["files_ok"] += 1
        # savetitle comparison: western ja= attr vs JP text= (both ordered)
        for ws, js in zip(wst, jst):
            if ws.get("ja") == js.get("text"):
                tot["savetitle_match"] += 1
            else:
                tot["savetitle_diff"] += 1
                problems.append(f"{name}: savetitle differs (west ja= vs jp text=)")
        if len(wst) != len(jst):
            problems.append(f"{name}: savetitle count {len(wst)} vs {len(jst)}")
    print("== aggregate ==")
    for k, v in tot.items():
        print(f"{k:18} {v}")
    print(f"\n== problems ({len(problems)}) ==")
    for p in problems[:60]:
        print(p)
    if len(problems) > 60:
        print(f"... and {len(problems)-60} more")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
