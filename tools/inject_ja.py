"""Surgically replace the `ja = {...}` regions inside text blocks of western
.ast scripts, leaving every other byte untouched.

Modes:
  --from-lang en   : copy each block's en subtree into ja (pipeline test)
  --from-jp DIR    : real injection from JP-release scripts. Western and JP
                     builds use different block-label schemes, so blocks are
                     paired per file by sequence alignment over signatures
                     (voice-file anchors + page count). Verified pairs get
                     the raw JP ja subtree; unpaired blocks (JP 1.0.0 vs
                     western 1.0.2 drift) and files absent from the JP
                     release fall back to a copy of the English subtree.
                     Chapter titles (savetitle ja= attrs) are updated from
                     the JP text= values when they differ.

Prints per-file stats only; never prints scenario text (spoiler-safe).
"""
import argparse
import difflib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from align import analyze

SAVETITLE_JA = re.compile(r'("savetitle"[^\n]*? ja=")((?:[^"\\]|\\.)*)(")')


def splice(text, replacements):
    out = []
    pos = 0
    for start, end, new in sorted(replacements):
        assert start >= pos, "overlapping replacements"
        out.append(text[pos:start])
        out.append(new)
        pos = end
    out.append(text[pos:])
    return "".join(out)


def en_fallback(wtext, blocks):
    """replacements copying en subtree into ja for the given blocks."""
    reps = []
    n = 0
    for b in blocks:
        if "ja_span" in b and "en_span" in b:
            s, e = b["ja_span"]
            new = wtext[b["en_span"][0] : b["en_span"][1]]
            if wtext[s:e] != new:
                reps.append((s, e, new))
                n += 1
    return reps, n


def inject_from_jp(west_path, jp_path, out_path):
    wtext, wblocks, wst = analyze(west_path)
    stats = dict(jp=0, fallback=0, savetitle=0)

    if jp_path is None:
        reps, stats["fallback"] = en_fallback(
            wtext, [b for b in wblocks if "ja" in b["pages"]])
    else:
        jtext, jblocks, jst = analyze(jp_path)
        w = [b for b in wblocks if "ja" in b["pages"]]
        j = [b for b in jblocks if "ja" in b["pages"]]
        sig_w = [(tuple(b["vo"]), b["pages"].get("en")) for b in w]
        sig_j = [(tuple(b["vo"]), b["pages"].get("ja")) for b in j]
        sm = difflib.SequenceMatcher(None, sig_w, sig_j, autojunk=False)
        paired_w, paired_j = set(), set()
        reps = []

        def take(wi, ji):
            wb, jb = w[wi], j[ji]
            s, e = wb["ja_span"]
            reps.append((s, e, jtext[jb["ja_span"][0] : jb["ja_span"][1]]))
            paired_w.add(wi)
            paired_j.add(ji)
            stats["jp"] += 1

        opcodes = sm.get_opcodes()
        for op, a1, a2, b1, b2 in opcodes:
            if op == "equal":
                for k in range(a2 - a1):
                    take(a1 + k, b1 + k)

        # recovery pass 1: officially moved/reordered lines keep their voice
        # file; a voice tuple is globally unique within a script, so an
        # unpaired western block with the same nonempty vo tuple and page
        # count as exactly one unpaired JP block is the same line relocated.
        jp_by_vo = {}
        for ji in range(len(j)):
            if ji not in paired_j and j[ji]["vo"]:
                jp_by_vo.setdefault(tuple(j[ji]["vo"]), []).append(ji)
        for wi in range(len(w)):
            if wi in paired_w or not w[wi]["vo"]:
                continue
            cand = jp_by_vo.get(tuple(w[wi]["vo"]), [])
            cand = [ji for ji in cand if ji not in paired_j]
            if (len(cand) == 1
                    and w[wi]["pages"].get("en") == j[cand[0]]["pages"]["ja"]):
                take(wi, cand[0])

        # recovery pass 2: inside one replace region, a single remaining
        # unvoiced block on each side with equal page counts is an adjacent
        # reorder (verified by reading such cases) — pair them.
        for op, a1, a2, b1, b2 in opcodes:
            if op != "replace":
                continue
            ws_left = [i for i in range(a1, a2)
                       if i not in paired_w and not w[i]["vo"]]
            js_left = [i for i in range(b1, b2)
                       if i not in paired_j and not j[i]["vo"]]
            if (len(ws_left) == 1 and len(js_left) == 1
                    and w[ws_left[0]]["pages"].get("en")
                    == j[js_left[0]]["pages"]["ja"]):
                take(ws_left[0], js_left[0])

        fb, nfb = en_fallback(
            wtext, [w[i] for i in range(len(w)) if i not in paired_w])
        reps += fb
        stats["fallback"] = nfb

    result = splice(wtext, reps)

    # chapter titles: ordered savetitle correspondence. The regex hits only
    # western-style lines carrying a ja= attribute; pair those (in document
    # order) with the JP text= values at the same savetitle positions.
    if jp_path is not None and len(wst) == len(jst):
        new_titles = [js.get("text") for ws, js in zip(wst, jst)
                      if ws.get("ja") is not None]
        if len(SAVETITLE_JA.findall(result)) == len(new_titles):
            idx = [0]

            def sub(m):
                t = new_titles[idx[0]]
                idx[0] += 1
                if not isinstance(t, str) or m.group(2) == t:
                    return m.group(0)
                stats["savetitle"] += 1
                return m.group(1) + t + m.group(3)

            result = SAVETITLE_JA.sub(sub, result)

    return _write(out_path, result), stats


def _write(out_path, result):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        f.write(result)
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-lang", choices=("en",))
    ap.add_argument("--from-jp", metavar="JP_DIR")
    ap.add_argument("src_dir")
    ap.add_argument("out_dir")
    args = ap.parse_args()
    if not args.from_lang and not args.from_jp:
        ap.error("need --from-lang or --from-jp")

    total = dict(files=0, jp=0, fallback=0, savetitle=0, files_no_jp=0)
    for name in sorted(os.listdir(args.src_dir)):
        if not name.endswith(".ast"):
            continue
        src = os.path.join(args.src_dir, name)
        out = os.path.join(args.out_dir, name)
        jp = None
        if args.from_jp:
            cand = os.path.join(args.from_jp, name)
            if os.path.exists(cand):
                jp = cand
            else:
                total["files_no_jp"] += 1
        _, stats = inject_from_jp(src, jp, out)
        total["files"] += 1
        for k in ("jp", "fallback", "savetitle"):
            total[k] += stats[k]
    print(f"files={total['files']} jp_injected={total['jp']} "
          f"en_fallback={total['fallback']} savetitles={total['savetitle']} "
          f"files_without_jp_source={total['files_no_jp']}")


if __name__ == "__main__":
    main()
