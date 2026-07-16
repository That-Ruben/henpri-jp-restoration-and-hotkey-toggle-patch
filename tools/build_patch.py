"""Assemble the language-mod patch archive (HENPRI.pfs.070).

Contents:
  script/*.ast                       ja-injected scripts (test or real JP text)
  system/table/list_windows_*.tbl    patched: 4th language button (ja)
  pc/<lang>/config1/bt_language_ja.png   generated button (all 4 langs)
  pc/ja/config1/bt_language_{en,cn,tw}.png  copied from pc/en set

Usage: python build_patch.py SCRIPT_DIR OUT_PFS [TBL_DIR] [SYS_DIR]
  TBL_DIR: dir with patched list_windows_<lang>.tbl (default analysis/patched_tbl)
  SYS_DIR: dir with patched list_windows.tbl + lang.lua (default analysis/patched_sys)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pfs import PfsArchive, write_pf8

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AN = os.path.join(ROOT, "analysis")


def add_dir_files(files, disk_dir, arc_prefix, ext):
    for name in sorted(os.listdir(disk_dir)):
        if not name.endswith(ext):
            continue
        with open(os.path.join(disk_dir, name), "rb") as f:
            files.append((arc_prefix + name, f.read()))


def main(script_dir, out_pfs, tbl_dir=None, sys_dir=None):
    files = []
    add_dir_files(files, script_dir, "script\\", ".ast")
    n_scripts = len(files)
    add_dir_files(files, tbl_dir or os.path.join(AN, "patched_tbl"),
                  "system\\table\\", ".tbl")
    n_tbls = len(files) - n_scripts
    assert n_tbls == 4, f"expected 4 language tbls, got {n_tbls}"
    # engine tweaks: L-key language toggle + backlog_max (see patch_system.py)
    sysdir = sys_dir or os.path.join(AN, "patched_sys")
    with open(os.path.join(sysdir, "list_windows.tbl"), "rb") as f:
        files.append(("system\\table\\list_windows.tbl", f.read()))
    with open(os.path.join(sysdir, "lang.lua"), "rb") as f:
        files.append(("system\\msg\\lang.lua", f.read()))
    with open(os.path.join(sysdir, "message.lua"), "rb") as f:
        files.append(("system\\msg\\message.lua", f.read()))
    with open(os.path.join(sysdir, "adv_mw.lua"), "rb") as f:
        files.append(("system\\extend\\adv_mw.lua", f.read()))

    with open(os.path.join(AN, "bt_language_ja.png"), "rb") as f:
        bt_ja = f.read()
    for lang in ("ja", "en", "cn", "tw"):
        files.append((f"pc\\{lang}\\config1\\bt_language_ja.png", bt_ja))

    # authentic JP UI assets restored over anglicized western ja files
    restore_root = os.path.join(AN, "ja_restore")
    for dirpath, _, names in os.walk(restore_root):
        for fn in sorted(names):
            rel = os.path.relpath(os.path.join(dirpath, fn), restore_root)
            with open(os.path.join(dirpath, fn), "rb") as f:
                files.append((rel.replace(os.sep, "\\"), f.read()))

    # ja config screen also needs the other three buttons (never shipped for ja)
    base = PfsArchive(os.path.join(ROOT, "HENPRI", "HENPRI.pfs"))
    for lang in ("en", "cn", "tw"):
        data = base.read(f"pc\\en\\config1\\bt_language_{lang}.png")
        files.append((f"pc\\ja\\config1\\bt_language_{lang}.png", data))
    base.close()

    # keyboard-help images with the L-key legend (added after ja_restore so
    # the edited ja image supersedes the plain restored one via dedup below)
    kb_root = os.path.join(AN, "kb_edit")
    if os.path.isdir(kb_root):
        for dirpath, _, names in os.walk(kb_root):
            for fn in sorted(names):
                rel = os.path.relpath(os.path.join(dirpath, fn), kb_root)
                with open(os.path.join(dirpath, fn), "rb") as f:
                    files.append((rel.replace(os.sep, "\\"), f.read()))

    # dedup, last occurrence wins
    seen = {}
    for name, data in files:
        seen[name] = data
    files = list(seen.items())

    write_pf8(out_pfs, files)
    size = os.path.getsize(out_pfs)
    print(f"wrote {out_pfs}: {len(files)} files ({n_scripts} scripts), "
          f"{size/1e6:.1f} MB")

    # read-back verification with our own reader
    a = PfsArchive(out_pfs)
    assert len(a.entries) == len(files)
    for (name, data), e in zip(files, a.entries):
        assert e.name == name and a.read(e) == data, name
    a.close()
    print("read-back verification OK")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2],
         sys.argv[3] if len(sys.argv) > 3 else None,
         sys.argv[4] if len(sys.argv) > 4 else None)
