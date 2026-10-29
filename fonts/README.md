# Barony Mongolian Pixel

The generated fonts use original rectangle-based glyph designs from
`pixel_cyrillic.py`, under the MIT license in `LICENSE.txt`. They do not contain
outlines copied from the game, Arial, or any other third-party font.

Coverage includes printable ASCII, all Mongolian Cyrillic letters (including
Ө/ө and Ү/ү), and common punctuation and symbols. PixelMaz menu files use a
compact five-row design; the other files use a seven-row design. Each generated
font uses one consistent cell advance and matches the original file's em size,
ascender and descender so the game's font scale and line spacing still apply.

The generator reads locally installed game fonts only to obtain those metrics.
No original game font is required by an end user installing the built package.

`assert_pixel_font()` checks every outline: no curves, composites or diagonal
edges are permitted, every contour is a rectangle, and all outlines fit the
line box and cell advance. `render_preview()` renders the resulting TTF files
at game sizes, followed by a nearest-neighbor enlargement of the same pixels.
