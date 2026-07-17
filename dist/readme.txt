HENPRI - Japanese Language Restoration Patch
=============================================
v2.1 - by That-Ruben

Makes HENPRI / HENTAI PRISON readable in Japanese, English, or both at
once. The western (Shiravune) release already contains parts of the
Japanese version (UI, fonts) but not the text itself; the missing text
is restored from the Japanese release (v1.0.7).

Should be compatible with Steam, GOG, and Jast versions. 
(For the Steam version, make sure you have the adult patch installed first)

Features
--------
- Japanese added as a 4th language: Config > WINDOW > LANGUAGE
- Instant JP/EN toggle in-game: press L (works mid-scene, also switches
  the backlog retroactively)
- Dual language display: press K to also show the other language in a
  smaller font above the text. The engine contains this feature
  unfinished and disabled; the patch completes and enables it. It is
  off by default.
- Restored Japanese UI art (config screens, loading screen, etc.)

Note: if K does nothing after loading a save made with an older version
of this patch, it will work after opening the backlog once. 
Saves made from then on are fine.

Install
-------
Copy ONE file into the game folder (next to HENPRI.exe):

  HENPRI.pfs.080  - the standard version.

  HENPRI.pfs.081  - if you have the fan-made "Improvement/Delocalization
                    Patch" (HENPRI.pfs.069) installed, use this one
                    instead. It keeps that patch's English script.

Uninstall: delete the file(s) again. Saves are not affected either way.

Advanced: you can install both. .081 takes priority while present, so
deleting/restoring .081 switches between the two English translations
(restart the game after switching). Japanese is identical in both.

IMPORTANT - about other patches
-------------------------------
Because of how the Artemis engine loads patch archives, the last archive
overrides whole files, including all languages at once. That is why two
builds exist: each carries the English text of its base game.

- Installing .080 alone on top of the Improvement Patch will revert your
  English text to the official translation (use .081 instead).
- If you use some other script patch that this mod doesn't know about,
  it will be overridden the same way. Reach out (see below) and a
  compatible build can be made.


Version history
---------------
v2.1 (2026-07-17) - added character portraits to Japanese backlog
                  - adjusted menu bar close delay from 5s to 1s
v2 (2026-07-16) - dual language display added (K key)
v1 (2026-07-13) - first release

Credits
-------
Patch by That-Ruben.
The Improvement/Delocalization Patch, whose English script is included
in HENPRI.pfs.081, is by Y0Σ1Δ.

Issues / contact
----------------
Bug reports and compatibility requests:
https://github.com/That-Ruben/henpri-jp-restoration-and-hotkey-toggle-patch
