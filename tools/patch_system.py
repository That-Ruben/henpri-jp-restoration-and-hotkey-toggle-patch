"""Produce patched engine files for the mod (beyond the language tbls):

  analysis/patched_sys/list_windows.tbl   (from .069's copy)
     - advkey: bind L (keycode 76) to new LANG action in both duplicate
       advkey blocks (Lua last-wins, we patch both for consistency)
     - LANG action -> lang_toggle_jaen (added to system/msg/lang.lua)
     - backlog_max 100 -> 200

  analysis/patched_sys/lang.lua           (from base pfs system/msg/lang.lua)
     - adds lang_toggle_jaen(): toggles main language ja <-> en
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AN = os.path.join(ROOT, "analysis")
BACKLOG_MAX = 100

# script/tbl base: "extracted_060" (official English) or "extracted_069"
# (Improvement Patch English); output dir set alongside.
BASE_EXTRACT = sys.argv[1] if len(sys.argv) > 1 else "extracted_060"
OUT_NAME = sys.argv[2] if len(sys.argv) > 2 else "patched_sys"
OUT = os.path.join(AN, OUT_NAME)

TOGGLE_FUNC = (
    "----------------------------------------\n"
    "-- 言語トグル ja<->en (language mod)\n"
    "-- conf_langchange と同様に main/sub/ui を揃えて切り替える\n"
    "function lang_toggle_jaen()\n"
    "\tlocal nm = get_language() == \"ja\" and \"en\" or \"ja\"\n"
    "\tif not init.lang[nm] then return end\n"
    "\tse_ok()\n"
    "\tset_language(\"main\", nm)\n"
    "\tset_language(\"sub\", nm)\n"
    "\tset_language(\"ui\", nm)\n"
    "\tlang_redraw()\n"
    "\tasyssave()\n"
    "end\n"
    "----------------------------------------\n"
)


def patch_tbl():
    src = os.path.join(AN, BASE_EXTRACT, "system", "table", "list_windows.tbl")
    with open(src, "r", encoding="utf-8", newline="") as f:
        t = f.read()

    n = t.count('def={[1]={btn="CLICK"')
    assert n == 2, f"expected 2 advkey def blocks, found {n}"
    assert "[76]=" not in t, "keycode 76 already bound"
    t = t.replace('def={[1]={btn="CLICK"',
                  'def={[76]={btn="L",adv="LANG"},[1]={btn="CLICK"')

    n = t.count("tbl={CLICK=\"adv_click\"")
    assert n == 2, f"expected 2 advkey tbl blocks, found {n}"
    assert "LANG=" not in t
    t = t.replace('tbl={CLICK="adv_click"',
                  'tbl={LANG="lang_toggle_jaen",CLICK="adv_click"')

    # Optional: raise the backlog rolling-window cap (stock 100). Left at
    # stock — user preference; the log stack lives inside save files, so a
    # bigger cap only deepens history for text read *after* the change.
    if BACKLOG_MAX != 100:
        t, n = re.subn(r"^backlog_max=100,(?=\r?\n)",
                       f"backlog_max={BACKLOG_MAX},", t, flags=re.M)
        assert n == 1, f"backlog_max edit applied {n} times"

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "list_windows.tbl"), "w",
              encoding="utf-8", newline="") as f:
        f.write(t)
    print(f"patched list_windows.tbl (L-key toggle, LANG action, "
          f"backlog_max={BACKLOG_MAX})")


def patch_lang_lua():
    src = os.path.join(AN, "extracted_base", "system", "msg", "lang.lua")
    with open(src, "r", encoding="utf-8", newline="") as f:
        t = f.read()
    assert "lang_toggle_jaen" not in t
    t += TOGGLE_FUNC
    with open(os.path.join(OUT, "lang.lua"), "w",
              encoding="utf-8", newline="") as f:
        f.write(t)
    print("patched lang.lua (+lang_toggle_jaen)")


if __name__ == "__main__":
    patch_tbl()
    patch_lang_lua()
