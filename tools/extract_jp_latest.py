"""Extract the effective (last-wins) script set from the JP install."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pfs import PfsArchive

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORDER = ["", ".000", ".001", ".002", ".003", ".010", ".011", ".012", ".013",
         ".014", ".020", ".021", ".022", ".030", ".040", ".050", ".060",
         ".061", ".070"]
OUT = os.path.join(ROOT, "analysis", "extracted_jp_latest")


def main():
    eff = {}
    for s in ORDER:
        p = os.path.join(ROOT, "HENPRI_JP", "HENPRI.pfs" + s)
        if not os.path.exists(p):
            continue
        a = PfsArchive(p)
        for e in a.entries:
            if e.name.startswith("script\\"):
                eff[e.name] = p
        a.close()
    print("effective scripts:", len(eff))
    from collections import Counter
    for arc, cnt in sorted(Counter(eff.values()).items()):
        print("  %-28s %d" % (os.path.basename(arc) +
                              arc[-5:].replace("s", ""), cnt))

    by_arc = {}
    for name, p in eff.items():
        by_arc.setdefault(p, set()).add(name)
    os.makedirs(os.path.join(OUT, "script"), exist_ok=True)
    for p, names in by_arc.items():
        a = PfsArchive(p)
        for e in a.entries:
            if e.name in names:
                dest = os.path.join(OUT, e.name.replace("\\", os.sep))
                with open(dest, "wb") as f:
                    f.write(a.read(e))
        a.close()
    print("extracted:", len(os.listdir(os.path.join(OUT, "script"))))


if __name__ == "__main__":
    main()
