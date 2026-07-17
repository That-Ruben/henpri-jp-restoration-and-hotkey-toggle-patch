"""Audit western pc/ja UI assets against the authentic JP release.

Effective file = last occurrence across the archive load order.
A western ja asset is 'anglicized' when its bytes equal the western en/cn/tw
asset at the same relative path. Where the JP release has a different,
authentic file at the same path, stage it for restoration.

Usage: python ja_assets.py            (report)
       python ja_assets.py --restore  (write analysis/ja_restore/... tree)
"""
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pfs import PfsArchive

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WEST = [f"HENPRI/HENPRI.pfs{s}" for s in
        ["", ".000", ".010", ".011", ".012", ".013", ".014", ".020",
         ".060", ".061", ".069"]]
JP = [f"HENPRI_JP/HENPRI.pfs{s}" for s in
      ["", ".000", ".001", ".002", ".003", ".010", ".011", ".012", ".013",
       ".014", ".020", ".021", ".022", ".030", ".040", ".050", ".060",
       ".061", ".070"]]


def effective(archives, prefix):
    """path -> (archive, entry) for last-wins effective files under prefix."""
    out = {}
    for ap in archives:
        full = os.path.join(ROOT, ap)
        if not os.path.exists(full):
            continue
        a = PfsArchive(full)
        for e in a.entries:
            if e.name.lower().startswith(prefix):
                out[e.name.lower()] = (full, e.name)
        a.close()
    return out


def read_one(full, name):
    a = PfsArchive(full)
    data = a.read(name)
    a.close()
    return data


# JP uses different filenames for these; restore under the western name.
RENAMES = {
    "pc\\ja\\config2\\bg_config2.png": "pc\\ja\\config2\\bg_config2_02.png",
    "pc\\ja\\config3\\bg_config3.png": "pc\\ja\\config3\\bg_config3_03.png",
}

# Pin to a specific JP archive instead of last-wins. The 1.0.7 config1 bg
# (.061) adds a キャッシュ（サポート） row whose buttons don't exist in the
# western engine build; the 1.0.0 art matches the options we actually offer.
PINS = {
    "pc\\ja\\config1\\bg_config1.png": "HENPRI_JP/HENPRI.pfs",
}

# Functional art with no language content: identical to en/cn/tw by design,
# so byte-equality is not evidence of anglicization. The backlog portrait
# mask in particular must stay the western version — the JP release's is an
# older format the remaster engine can't use (portraits become invisible).
EXCLUDES = {
    "pc\\ja\\blog\\maskblog.png",
}


def main(restore=False):
    west_ja = effective(WEST, "pc\\ja\\")
    jp_ja = effective(JP, "pc\\ja\\")
    west_other = {}
    for lang in ("en", "cn", "tw"):
        west_other[lang] = effective(WEST, f"pc\\{lang}\\")

    n = dict(total=len(west_ja), anglicized=0, restorable=0, jp_missing=0,
             distinct_ok=0, jp_same=0)
    restorable = []
    for path, (arc, name) in sorted(west_ja.items()):
        if path in EXCLUDES:
            n["distinct_ok"] += 1
            continue
        data = read_one(arc, name)
        h = hashlib.md5(data).hexdigest()
        angl = False
        for lang in ("en", "cn", "tw"):
            other = west_other[lang].get(path.replace("\\ja\\", f"\\{lang}\\"))
            if other and hashlib.md5(read_one(*other)).hexdigest() == h:
                angl = True
                break
        if not angl:
            n["distinct_ok"] += 1
            continue
        n["anglicized"] += 1
        jp = jp_ja.get(path) or jp_ja.get(RENAMES.get(path, "").lower())
        if path in PINS:
            pin = os.path.join(ROOT, PINS[path])
            src = jp_ja.get(path)
            jp = (pin, src[1]) if src else None
        if jp is None:
            n["jp_missing"] += 1
            print(f"ANGLICIZED, no JP source: {path}")
            continue
        jdata = read_one(*jp)
        if hashlib.md5(jdata).hexdigest() == h:
            n["jp_same"] += 1  # JP file identical anyway -> not anglicized
            continue
        n["restorable"] += 1
        restorable.append((path, jdata))
        print(f"RESTORE: {path}  ({len(data)} -> {len(jdata)} bytes, from "
              f"{os.path.basename(jp[0])})")

    print("\n== summary ==")
    for k, v in n.items():
        print(f"{k:12} {v}")

    if restore:
        outroot = os.path.join(ROOT, "analysis", "ja_restore")
        for path, jdata in restorable:
            dest = os.path.join(outroot, path.replace("\\", os.sep))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "wb") as f:
                f.write(jdata)
        print(f"wrote {len(restorable)} files under {outroot}")


if __name__ == "__main__":
    main(restore="--restore" in sys.argv)
