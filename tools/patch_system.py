"""Produce patched engine files for the mod (beyond the language tbls):

  analysis/<OUT>/list_windows.tbl   (from the variant's base copy)
     - advkey: bind L (keycode 76) to LANG and K (keycode 75) to SUBV in
       both duplicate advkey blocks (Lua last-wins, we patch both)
     - LANG -> lang_toggle_jaen, SUBV -> sublang_toggle (both in lang.lua)

  analysis/<OUT>/lang.lua           (from base pfs system/msg/lang.lua)
     - lang_toggle_jaen(): toggles main language ja <-> en; the sub
       language is set to the opposite so the dual display always pairs
       the two languages
     - sublang_toggle(): K key; shows/hides the engine's dormant
       dual-language display (off by default, session-only)

  analysis/<OUT>/message.lua        (from base pfs system/msg/message.lua)
     - finishes the engine's half-implemented sub-language rendering:
       the sub layer renders the sub language (not the main one), and is
       bottom-anchored a fixed distance above the main text

  analysis/<OUT>/adv_mw.lua         (from base pfs system/extend/adv_mw.lua)
     - the sub layer's font is assigned unconditionally, so the K toggle
       works even though the dual display starts off
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
    "----------------------------------------\r\n"
    "-- 言語トグル ja<->en (language mod)\r\n"
    "-- conf_langchange と同様に main/ui を切り替える。subは反対言語に\r\n"
    "-- 揃えて、二言語表示(Kキー)が常に日英ペアになるようにする\r\n"
    "function lang_toggle_jaen()\r\n"
    "\tlocal nm = get_language() == \"ja\" and \"en\" or \"ja\"\r\n"
    "\tif not init.lang[nm] then return end\r\n"
    "\tse_ok()\r\n"
    "\tset_language(\"main\", nm)\r\n"
    "\tset_language(\"sub\", nm == \"ja\" and \"en\" or \"ja\")\r\n"
    "\tset_language(\"ui\", nm)\r\n"
    "\tlang_redraw()\r\n"
    "\tasyssave()\r\n"
    "end\r\n"
    "----------------------------------------\r\n"
    "-- 二言語表示の切替 Kキー (language mod)\r\n"
    "-- エンジン休眠機能 game_sublangview を実行時に切り替える。\r\n"
    "-- デフォルトはオフ、セッション内のみ有効\r\n"
    "function sublang_toggle()\r\n"
    "\tif init.game_sublangview == \"on\" then\r\n"
    "\t\tinit.game_sublangview = \"off\"\r\n"
    "\t\tinit.game_sublangblog = \"off\"\r\n"
    "\t\tlocal id = mw_getmsgid(\"sub\")\r\n"
    "\t\te:tag{\"chgmsg\", id=(id)}\r\n"
    "\t\te:tag{\"rp\"}\r\n"
    "\t\te:tag{\"/chgmsg\"}\r\n"
    "\telse\r\n"
    "\t\tinit.game_sublangview = \"on\"\r\n"
    "\t\tinit.game_sublangblog = \"on\"\r\n"
    "\t\tlocal ln = get_language()\r\n"
    "\t\tlocal sb = get_language(\"sub\")\r\n"
    "\t\tif not sb or sb == ln then\r\n"
    "\t\t\tset_language(\"sub\", ln == \"ja\" and \"en\" or \"ja\")\r\n"
    "\t\tend\r\n"
    "\tend\r\n"
    "\tse_ok()\r\n"
    "\tlang_redraw()\r\n"
    "end\r\n"
    "----------------------------------------\r\n"
)

SUBPOS_FUNC = (
    "----------------------------------------\r\n"
    "-- sub本文を本文の上に下端固定で配置する (language mod)\r\n"
    "function mw_subposition()\r\n"
    "\tlocal id = mw_getmsgid(\"sub\")\r\n"
    "\te:tag{\"chgmsg\", id=(id)}\r\n"
    "\te:tag{\"var\", system=\"get_message_layer_height\", name=\"t.tmp.subh\"}\r\n"
    "\tlocal h = e:var(\"t.tmp.subh\") or 0\r\n"
    "\te:tag{\"/chgmsg\"}\r\n"
    "\t-- 下端 = フォントtop(550) + レイヤtop + h を644に固定\r\n"
    "\te:tag{\"lyprop\", id=(id), top=(644 - 550 - h)}\r\n"
    "end\r\n"
)


def patch_tbl():
    src = os.path.join(AN, BASE_EXTRACT, "system", "table", "list_windows.tbl")
    with open(src, "r", encoding="utf-8", newline="") as f:
        t = f.read()

    n = t.count('def={[1]={btn="CLICK"')
    assert n == 2, f"expected 2 advkey def blocks, found {n}"
    assert "[76]=" not in t and "[75]=" not in t, "keycode already bound"
    t = t.replace('def={[1]={btn="CLICK"',
                  'def={[76]={btn="L",adv="LANG"},'
                  '[75]={btn="K",adv="SUBV"},[1]={btn="CLICK"')

    n = t.count("tbl={CLICK=\"adv_click\"")
    assert n == 2, f"expected 2 advkey tbl blocks, found {n}"
    assert "LANG=" not in t and "SUBV=" not in t
    t = t.replace('tbl={CLICK="adv_click"',
                  'tbl={SUBV="sublang_toggle",LANG="lang_toggle_jaen",'
                  'CLICK="adv_click"')

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
    print(f"patched list_windows.tbl (L+K key bindings, "
          f"backlog_max={BACKLOG_MAX})")


def patch_lang_lua():
    src = os.path.join(AN, "extracted_base", "system", "msg", "lang.lua")
    with open(src, "r", encoding="utf-8", newline="") as f:
        t = f.read()
    assert "lang_toggle_jaen" not in t and "sublang_toggle" not in t
    t += TOGGLE_FUNC
    with open(os.path.join(OUT, "lang.lua"), "w",
              encoding="utf-8", newline="") as f:
        f.write(t)
    print("patched lang.lua (+lang_toggle_jaen, +sublang_toggle)")


def patch_message_lua():
    """The base engine shipped the dual-language display half-finished:
    mw_textloop ignored its lang parameter (the sub layer rendered the main
    language) and the sub layer was positioned below the main text. Fix
    both; the sub layer is bottom-anchored above the main text instead."""
    src = os.path.join(AN, "extracted_base", "system", "msg", "message.lua")
    with open(src, "r", encoding="utf-8", newline="") as f:
        t = f.read()

    old = "\tlocal v = getTextBlockFloat(p.text)"
    assert t.count(old) == 1
    t = t.replace(old, "\tlocal v = getTextBlockFloat(p.text, nil, p.lang)")

    old = ("function getTextBlockFloat(p, mode)\r\n"
           "\tlocal r  = nil\r\n"
           "\tlocal z  = p.float or {}\r\n"
           "\tlocal ln = get_language(true)")
    assert t.count(old) == 1, "getTextBlockFloat anchor not found"
    t = t.replace(old, (
        "function getTextBlockFloat(p, mode, lang)\r\n"
        "\tlocal r  = nil\r\n"
        "\tlocal z  = p.float or {}\r\n"
        "\tlocal ln = lang and p[lang] and lang or get_language(true)"))

    old = '\t\testag{"lyprop", id=(id), top=(r)}'
    assert t.count(old) == 1
    t = t.replace(old, '\t\testag{"mw_subposition"}')
    t += SUBPOS_FUNC

    with open(os.path.join(OUT, "message.lua"), "w",
              encoding="utf-8", newline="") as f:
        f.write(t)
    print("patched message.lua (sub language + bottom anchor)")


def patch_adv_mw_lua():
    """Assign the sub layer's font unconditionally so the K toggle can turn
    the dual display on mid-session (stock code only assigned it when the
    display was already on at window creation)."""
    src = os.path.join(AN, "extracted_base", "system", "extend", "adv_mw.lua")
    with open(src, "r", encoding="utf-8", newline="") as f:
        t = f.read()
    old = ("\tlocal tb = { adv=1, name=1 }\r\n"
           '\tif init.game_sublangview == "on" then tb.sub = 1 end\t-- sub')
    assert t.count(old) == 1, "adv_mw font anchor not found"
    t = t.replace(old, "\tlocal tb = { adv=1, name=1, sub=1 }"
                       "\t-- sub font always set (language mod)")
    with open(os.path.join(OUT, "adv_mw.lua"), "w",
              encoding="utf-8", newline="") as f:
        f.write(t)
    print("patched adv_mw.lua (sub font always assigned)")


if __name__ == "__main__":
    patch_tbl()
    patch_lang_lua()
    patch_message_lua()
    patch_adv_mw_lua()
