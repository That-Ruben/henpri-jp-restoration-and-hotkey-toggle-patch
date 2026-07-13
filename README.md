# HENPRI Japanese Language Restoration

Restores the **Japanese text option** in the western (Shiravune) release of
*HENPRI / HENTAI PRISON* (Artemis engine).

The western release still ships the entire Japanese infrastructure — fonts,
UI string tables, `pc/ja/` assets, and a `ja` slot in every one of the
73,276 dialogue text blocks — but the Japanese dialogue itself was replaced
with a placeholder and the language option was hidden. This project restores
it:

- **Japanese as a 4th language** in Config → WINDOW → LANGUAGE
- **Instant JP⇄EN toggle** with the **L** key, mid-scene, backlog included
- Restored authentic Japanese UI art (config screens, loading screen, …)
- The new hotkey is documented on the Config → KEYBOARD screen

## Installing the patch

Grab the released zip (see the pinned links), then copy **one** file into
the game folder, next to `HENPRI.exe`:

- `HENPRI.pfs.080` — the standard version.
- `HENPRI.pfs.081` — if you have the fan-made
  [Improvement/Delocalization Patch](https://www.reddit.com/r/visualnovels/comments/1uqz332/henpri_hentai_prison_improvement_delocalization)
  (`HENPRI.pfs.069`) installed, use this one instead. It keeps that patch's
  English script.

Works with the Steam, GOG and JAST versions (on Steam, install the free
adult patch first). Uninstall: delete the file again. Saves are unaffected.

**Why two builds?** The Artemis engine overrides *whole files*, and script
files carry every language's text together — so any patch necessarily ships
an English text base along with the Japanese. `.080` carries the official
English, `.081` carries the Improvement Patch's English. You can even
install both: `.081` wins while present, so deleting/restoring it switches
your English translation (the Japanese is identical in both). If you use
another script patch this project doesn't know about, open an issue — a
compatible build is easy to make.

## This repository

**No game data is distributed here** — only the toolchain and documentation
to build the patch from game copies you own.

### Building it yourself

Requirements:

- The **western release**, updated to v1.0.2
- The **Japanese release**, updated via its `Updater.exe` (tested at v1.0.7 —
  the JP updater still works and is required; the disc version 1.0.0 scripts
  differ slightly from the western text base)
- Python 3.10+ with `Pillow`

```
python tools/build_all.py <WESTERN_GAME_DIR> <JP_GAME_DIR>
```

Outputs `dist/HENPRI.pfs.080` and (if `HENPRI.pfs.069` is present in the
western folder) `dist/HENPRI.pfs.081`. The build is deterministic —
identical inputs produce byte-identical patches.

### How it works (short version)

- `pfs.py` — reader/writer for Artemis pf6/pf8 archives (pf8 XOR-encrypts
  file data with the SHA1 of the archive index)
- `astlib.py` / `align.py` — parser for the Lua-table `.ast` scenario
  scripts; western and JP builds use different block labels, so blocks are
  paired per file by document order and verified with voice-file anchors and
  page counts (73,275/73,275 blocks verified)
- `inject_ja.py` — splices the raw Japanese subtree from the JP scripts into
  each western text block's `ja` slot, byte-surgically (all other languages
  remain byte-identical to the base)
- `patch_tbl.py` / `patch_system.py` — add the 日本語 config button, the
  `L` hotkey binding, and the toggle function to the engine's Lua/tbl data
- `ja_assets.py` — restores `pc/ja/` UI images the localization replaced
  with English ones (detected by hash comparison against the JP release)
- `edit_keyboard.py` — draws the L key onto the keyboard help screen

## Credits

Patch by **That-Ruben**. Tools are MIT-licensed (see LICENSE).

The Improvement/Delocalization Patch, whose English script is included in
`HENPRI.pfs.081`, is by **Y0Σ1Δ**.
