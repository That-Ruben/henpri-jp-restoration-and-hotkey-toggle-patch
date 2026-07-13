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
Option A: run install.bat from inside the game folder (or drag your game
          folder onto install.bat). It auto-detects which version you need.
Option B: manually copy ONE of these into the game folder (next to
          HENPRI.exe):
          - official\HENPRI.pfs.080  if you do NOT use the Translation
            Improvement Patch
          - hip\HENPRI.pfs.080       if you DO have the Translation
            Improvement Patch (HENPRI.pfs.069) installed

Uninstall: delete HENPRI.pfs.080 from the game folder. Saves are not
affected either way.

IMPORTANT - about other patches
-------------------------------
Because of how the Artemis engine loads patch archives, the last archive
overrides whole files, including all languages at once. That is why two
builds exist: each one carries the English text of its base game
(official English, or the Improvement Patch's English).

- If you install the "official" build on top of the Improvement Patch,
  your English text will revert to the official translation.
- If you add or remove the Improvement Patch later, re-run install.bat
  (or swap in the other build) to match.
- If you use some other patch that this mod doesn't know about, it will
  be overridden the same way. Reach out (see below) and a compatible
  build can be made.

Requirements: western release updated to v1.0.2 (GOG/Steam current).

Credits
-------
Patch by That-Ruben. The "hip" build exists for compatibility with the
Improvement/Delocalization Patch by Y0(Sigma)1(Delta) and carries that
patch's English text - credit for that text is theirs.

Issues / contact
----------------
Bug reports and compatibility requests: see the project page (link where
you got this file).
