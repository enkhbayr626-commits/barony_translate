# Validation — 2026-10-29

Target game: Barony v5.0.2.2026.04.03, Windows.

- Build contains 5,727 changed text fields and 10 original pixel font files.
- `python -X utf8 validate_mod.py` passed: 27 JSON files, 5,948 base/seasonal
  language entries, unchanged formatting arguments and gameplay structure,
  109 verified English file hashes.
- Both radial menu JSON files remain below the game's fixed 65,536-byte reader limit.
- All fonts cover every printable character in the shipped payload, including
  Mongolian Ө/ө/Ү/ү. Geometry checks confirm rectangular, straight pixel outlines,
  no imported composite glyphs, and glyphs within their line and advance bounds.
- The preview PNG was rendered from the actual generated TTF files and visually inspected.
- Installer integration tests passed under Windows PowerShell 5.1: first install,
  wrong-version rejection, repeat install, package update, retired files, rollback,
  corrupt payload/backups, unknown game edits, path confinement, uninstall/reinstall,
  unchanged saves and executable.
- A live 39-file install → English restore → reinstall passed on the installed game.
  Backup and installed hashes were verified after both restore and reinstall.
- The game launched with the new files and progressed through main-menu asset loading.
  Further screen inspection was stopped when the user pressed Escape in Computer Use.
  A complete gameplay/layout review of every translated screen remains outstanding.

This is a partial translation. A successful installer/font check does not mean all
English content has been translated or every screen has been visually reviewed.

Re-run the Windows installer integration tests:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tests/test_install.ps1
```
