"""Build the HENPRI Japanese-restoration patch from your own game copies.

Requires:
  - the western release (GOG/Steam), updated to v1.0.2
  - the Japanese release, updated via its Updater.exe (tested with v1.0.7)
  - Python 3.10+ with Pillow

Usage:
  python tools/build_all.py <WESTERN_GAME_DIR> <JP_GAME_DIR>

The script creates directory junctions HENPRI/ and HENPRI_JP/ next to
tools/ (the layout the individual tools expect), extracts what it needs
into analysis/, and writes dist/HENPRI.pfs.080 (official English base) and
dist/HENPRI.pfs.081 (Improvement Patch English base; built only if the
western folder contains HENPRI.pfs.069).
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
AN = os.path.join(ROOT, "analysis")


def run(*args):
    print("+", " ".join(args))
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    subprocess.run([sys.executable] + list(args), check=True, cwd=ROOT,
                   env=env)


def ensure_junction(link, target):
    if os.path.exists(link):
        return
    subprocess.run(["cmd", "/c", "mklink", "/J", link, target], check=True)


def main(west, jp):
    ensure_junction(os.path.join(ROOT, "HENPRI"), os.path.abspath(west))
    ensure_junction(os.path.join(ROOT, "HENPRI_JP"), os.path.abspath(jp))
    pfs = os.path.join(TOOLS, "pfs.py")

    # 1. extract western sources
    run(pfs, "extract", "HENPRI/HENPRI.pfs", "analysis/extracted_base",
        "system", ".ini", ".lua", "bt_language", "rounded-x-mgenplus-1p-bold")
    os.makedirs(os.path.join(AN, "fonts", "font", "hp"), exist_ok=True)
    src = os.path.join(AN, "extracted_base", "font", "hp",
                       "rounded-x-mgenplus-1p-bold.ttf")
    dst = os.path.join(AN, "fonts", "font", "hp",
                       "rounded-x-mgenplus-1p-bold.ttf")
    if os.path.exists(src) and not os.path.exists(dst):
        os.replace(src, dst)
    run(pfs, "extract", "HENPRI/HENPRI.pfs.060", "analysis/extracted_060",
        "script\\", "system")
    hip = os.path.exists(os.path.join(ROOT, "HENPRI", "HENPRI.pfs.069"))
    if hip:
        run(pfs, "extract", "HENPRI/HENPRI.pfs.069", "analysis/extracted_069",
            "script\\", "system")

    # 2. extract JP effective scripts
    run(os.path.join(TOOLS, "extract_jp_latest.py"))

    # 3. UI pieces: 日本語 button, restored ja assets, keyboard-help edit
    run(os.path.join(TOOLS, "make_button.py"),
        "analysis/extracted_base/pc/en/config1/bt_language_cn.png",
        "analysis/bt_language_ja.png",
        "analysis/fonts/font/hp/rounded-x-mgenplus-1p-bold.ttf")
    run(os.path.join(TOOLS, "ja_assets.py"), "--restore")
    run(os.path.join(TOOLS, "edit_keyboard.py"))

    # 4. per-variant scripts + tbls + build
    # (variant, base extract, output suffix): .080 official EN, .081 the
    # Improvement Patch's EN
    variants = [("official", "extracted_060", "080")]
    if hip:
        variants.append(("hip", "extracted_069", "081"))
    for name, base, suffix in variants:
        inj = f"analysis/jp_inject_{name}/script"
        tbl = f"analysis/patched_tbl_{name}"
        sysd = f"analysis/patched_sys_{name}"
        run(os.path.join(TOOLS, "inject_ja.py"), "--from-jp",
            "analysis/extracted_jp_latest/script", f"analysis/{base}/script",
            inj)
        os.makedirs(os.path.join(ROOT, tbl), exist_ok=True)
        run(os.path.join(TOOLS, "patch_tbl.py"),
            f"analysis/{base}/system/table/list_windows_en.tbl",
            f"{tbl}/list_windows_en.tbl")
        for lang in ("cn", "tw", "ja"):
            run(os.path.join(TOOLS, "patch_tbl.py"),
                f"analysis/extracted_060/system/table/list_windows_{lang}.tbl",
                f"{tbl}/list_windows_{lang}.tbl")
        run(os.path.join(TOOLS, "patch_system.py"), base,
            os.path.basename(sysd))
        os.makedirs(os.path.join(ROOT, "dist"), exist_ok=True)
        run(os.path.join(TOOLS, "build_patch.py"), inj,
            f"dist/HENPRI.pfs.{suffix}", tbl, sysd)
    print("\nDone. Patches in dist/.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2])
