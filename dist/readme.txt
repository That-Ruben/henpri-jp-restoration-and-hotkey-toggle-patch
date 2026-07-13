HENPRI - Japanese Language Restoration Patch
=============================================
by That-Ruben

Restores the Japanese text option in the western (Shiravune) release of
HENPRI / HENTAI PRISON. The Japanese script, UI and fonts are already
partially present in the western release; this patch restores the missing
Japanese text (sourced from the Japanese release, v1.0.7) and re-enables
the language option.

Features
--------
- Japanese added as a 4th language: Config > WINDOW > LANGUAGE
- Instant JP/EN toggle in-game: press L (works mid-scene, also switches
  the backlog retroactively)
- Restored Japanese UI art (config screens, loading screen, etc.)
- The L key is documented on the Config > KEYBOARD screen

Install
-------
Copy ONE file into the game folder (next to HENPRI.exe):

  HENPRI.pfs.080  - if you do NOT use the Translation Improvement Patch
  HENPRI.pfs.081  - if you DO have the Translation Improvement Patch
                    (HENPRI.pfs.069) installed; this build keeps its
                    improved English text

(The Improvement/Delocalization Patch is by Y0Σ1Δ; the .081
build exists for compatibility with it and carries that patch's English
text - credit for that text is theirs.)

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

Requirements: western release updated to v1.0.2 (GOG/Steam current).

Credits
-------
Patch by That-Ruben.

Issues / contact
----------------
Bug reports and compatibility requests:
https://github.com/That-Ruben/henpri-jp-restoration-and-hotkey-toggle-patch
