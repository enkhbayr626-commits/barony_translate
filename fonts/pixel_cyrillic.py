"""Original, freely redistributable grid fonts for the Mongolian translation.

All outlines below are newly authored rectangles, including Latin glyphs. No
outlines from Arial or Barony's bundled fonts are copied. A local original font
is read only for its em size, line metrics and nominal menu advance.
"""
from pathlib import Path
from fontTools.fontBuilder import FontBuilder
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.boundsPen import BoundsPen

ALPHABET = 'АБВГДЕЁЖЗИЙКЛМНОӨПРСТУҮФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмноөпрстуүфхцчшщъыьэюя'
# Slash-separated rows run from top to bottom; 1 is one filled square.
# This source is the editable design for every generated outline.
LATIN = {
 'A':'01110/10001/10001/11111/10001/10001/10001',
 'B':'11110/10001/10001/11110/10001/10001/11110',
 'C':'01111/10000/10000/10000/10000/10000/01111',
 'D':'11110/10001/10001/10001/10001/10001/11110',
 'E':'11111/10000/10000/11110/10000/10000/11111',
 'F':'11111/10000/10000/11110/10000/10000/10000',
 'G':'01111/10000/10000/10111/10001/10001/01111',
 'H':'10001/10001/10001/11111/10001/10001/10001',
 'I':'11111/00100/00100/00100/00100/00100/11111',
 'J':'00111/00010/00010/00010/10010/10010/01100',
 'K':'10001/10010/10100/11000/10100/10010/10001',
 'L':'10000/10000/10000/10000/10000/10000/11111',
 'M':'10001/11011/10101/10101/10001/10001/10001',
 'N':'10001/11001/11001/10101/10011/10011/10001',
 'O':'01110/10001/10001/10001/10001/10001/01110',
 'P':'11110/10001/10001/11110/10000/10000/10000',
 'Q':'01110/10001/10001/10001/10101/10010/01101',
 'R':'11110/10001/10001/11110/10100/10010/10001',
 'S':'01111/10000/10000/01110/00001/00001/11110',
 'T':'11111/00100/00100/00100/00100/00100/00100',
 'U':'10001/10001/10001/10001/10001/10001/01110',
 'V':'10001/10001/10001/10001/10001/01010/00100',
 'W':'10001/10001/10001/10101/10101/11011/10001',
 'X':'10001/10001/01010/00100/01010/10001/10001',
 'Y':'10001/10001/01010/00100/00100/00100/00100',
 'Z':'11111/00001/00010/00100/01000/10000/11111',
 'a':'01110/00001/01111/10001/01111',
 'b':'10000/10000/11110/10001/10001/10001/11110',
 'c':'01111/10000/10000/10000/01111',
 'd':'00001/00001/01111/10001/10001/10001/01111',
 'e':'01110/10001/11111/10000/01111',
 'f':'00110/01001/01000/11100/01000/01000/01000',
 'g':'01111/10001/10001/01111/00001/10001/01110',
 'h':'10000/10000/11110/10001/10001/10001/10001',
 'i':'00100/00000/01100/00100/00100/00100/01110',
 'j':'00010/00000/00110/00010/00010/10010/01100',
 'k':'10000/10000/10001/10010/11100/10010/10001',
 'l':'01100/00100/00100/00100/00100/00100/01110',
 'm':'11010/10101/10101/10101/10101',
 'n':'11110/10001/10001/10001/10001',
 'o':'01110/10001/10001/10001/01110',
 'p':'11110/10001/10001/11110/10000/10000/10000',
 'q':'01111/10001/10001/01111/00001/00001/00001',
 'r':'10111/11000/10000/10000/10000',
 's':'01111/10000/01110/00001/11110',
 't':'01000/01000/11100/01000/01000/01001/00110',
 'u':'10001/10001/10001/10001/01111',
 'v':'10001/10001/10001/01010/00100',
 'w':'10001/10001/10101/10101/01010',
 'x':'10001/01010/00100/01010/10001',
 'y':'10001/10001/10001/01111/00001/00010/11100',
 'z':'11111/00010/00100/01000/11111',
}
CYRILLIC = {
 'А':LATIN['A'], 'Б':'11111/10000/10000/11110/10001/10001/11110',
 'В':LATIN['B'], 'Г':'11111/10000/10000/10000/10000/10000/10000',
 'Д':'00110/01010/01010/01010/01010/11111/10001',
 'Е':LATIN['E'], 'Ё':'01010/00000/11111/10000/11110/10000/11111',
 'Ж':'10101/10101/01110/00100/01110/10101/10101',
 'З':'11110/00001/00001/01110/00001/00001/11110',
 'И':'10001/10011/10101/10101/11001/10001/10001',
 'Й':'01010/00100/10001/10011/10101/11001/10001',
 'К':LATIN['K'], 'Л':'00111/01001/01001/01001/01001/10001/10001',
 'М':LATIN['M'], 'Н':LATIN['H'], 'О':LATIN['O'],
 'Ө':'01110/10001/10001/11111/10001/10001/01110',
 'П':'11111/10001/10001/10001/10001/10001/10001',
 'Р':LATIN['P'], 'С':LATIN['C'], 'Т':LATIN['T'],
 'У':'10001/10001/10001/01111/00001/00010/11100', 'Ү':LATIN['Y'],
 'Ф':'00100/01110/10101/10101/10101/01110/00100',
 'Х':LATIN['X'], 'Ц':'10010/10010/10010/10010/10010/11111/00001',
 'Ч':'10001/10001/10001/01111/00001/00001/00001',
 'Ш':'10101/10101/10101/10101/10101/10101/11111',
 'Щ':'10101/10101/10101/10101/10101/11111/00001',
 'Ъ':'11000/01000/01000/01110/01001/01001/01110',
 'Ы':'10001/10001/10001/11101/10101/10101/11101',
 'Ь':'10000/10000/10000/11110/10001/10001/11110',
 'Э':'11110/00001/00001/01111/00001/00001/11110',
 'Ю':'10010/10101/10101/11101/10101/10101/10010',
 'Я':'01111/10001/10001/01111/00101/01001/10001',
 'а':LATIN['a'], 'б':'00011/01100/10000/11110/10001/10001/01110',
 'в':'11110/10001/11110/10001/11110', 'г':'11111/10000/10000/10000/10000',
 'д':'00110/01010/01010/11111/10001', 'е':LATIN['e'],
 'ё':'01010/00000/01110/10001/11111/10000/01111',
 'ж':'10101/01110/00100/01110/10101', 'з':'11110/00001/00110/00001/11110',
 'и':'10001/10011/10101/11001/10001',
 'й':'01010/00100/10001/10011/10101/11001/10001',
 'к':'10001/10010/11100/10010/10001', 'л':'00111/01001/01001/10001/10001',
 'м':'10001/11011/10101/10001/10001', 'н':'10001/10001/11111/10001/10001',
 'о':LATIN['o'], 'ө':'01110/10001/11111/10001/01110',
 'п':'11111/10001/10001/10001/10001', 'р':LATIN['p'], 'с':LATIN['c'],
 'т':'11111/00100/00100/00100/00100', 'у':LATIN['y'],
 'ү':'10001/10001/01010/00100/00100/00100/00100',
 'ф':'00100/01110/10101/10101/01110/00100/00100',
 'х':LATIN['x'], 'ц':'10010/10010/10010/10010/11111/00001',
 'ч':'10001/10001/01111/00001/00001', 'ш':'10101/10101/10101/10101/11111',
 'щ':'10101/10101/10101/10101/11111/00001',
 'ъ':'11000/01000/01110/01001/01110', 'ы':'10001/10001/11101/10101/11101',
 'ь':'10000/10000/11110/10001/11110', 'э':'11110/00001/01111/00001/11110',
 'ю':'10010/10101/11101/10101/10010', 'я':'01111/10001/01111/01001/10001',
}
DIGITS = {
 '0':'01110/10001/10011/10101/11001/10001/01110',
 '1':'00100/01100/00100/00100/00100/00100/01110',
 '2':'01110/10001/00001/00010/00100/01000/11111',
 '3':'11110/00001/00001/01110/00001/00001/11110',
 '4':'00010/00110/01010/10010/11111/00010/00010',
 '5':'11111/10000/10000/11110/00001/00001/11110',
 '6':'01110/10000/10000/11110/10001/10001/01110',
 '7':'11111/00001/00010/00100/01000/01000/01000',
 '8':'01110/10001/10001/01110/10001/10001/01110',
 '9':'01110/10001/10001/01111/00001/00001/01110',
}
PUNCTUATION = {
 ' ':'00000/00000/00000/00000/00000/00000/00000',
 '!':'00100/00100/00100/00100/00100/00000/00100',
 '"':'01010/01010/01010/00000/00000/00000/00000',
 '#':'01010/01010/11111/01010/11111/01010/01010',
 '$':'00100/01111/10100/01110/00101/11110/00100',
 '%':'11001/11010/00010/00100/01000/01011/10011',
 '&':'01100/10010/10100/01000/10101/10010/01101',
 "'":'00100/00100/00100/00000/00000/00000/00000',
 '(':'00010/00100/01000/01000/01000/00100/00010',
 ')':'01000/00100/00010/00010/00010/00100/01000',
 '*':'00000/10101/01110/11111/01110/10101/00000',
 '+':'00000/00100/00100/11111/00100/00100/00000',
 ',':'00000/00000/00000/00000/00000/00100/01000',
 '-':'00000/00000/00000/11111/00000/00000/00000',
 '.':'00000/00000/00000/00000/00000/00000/00100',
 '/':'00001/00010/00010/00100/01000/01000/10000',
 ':':'00000/00100/00100/00000/00100/00100/00000',
 ';':'00000/00100/00100/00000/00100/00100/01000',
 '<':'00001/00010/00100/01000/00100/00010/00001',
 '=':'00000/00000/11111/00000/11111/00000/00000',
 '>':'10000/01000/00100/00010/00100/01000/10000',
 '?':'01110/10001/00001/00010/00100/00000/00100',
 '@':'01110/10001/10111/10101/10111/10000/01111',
 '[':'01110/01000/01000/01000/01000/01000/01110',
 '\\':'10000/01000/01000/00100/00010/00010/00001',
 ']':'01110/00010/00010/00010/00010/00010/01110',
 '^':'00100/01010/10001/00000/00000/00000/00000',
 '_':'00000/00000/00000/00000/00000/00000/11111',
 '`':'01000/00100/00010/00000/00000/00000/00000',
 '{':'00011/00100/00100/11000/00100/00100/00011',
 '|':'00100/00100/00100/00100/00100/00100/00100',
 '}':'11000/00100/00100/00011/00100/00100/11000',
 '~':'00000/00000/01001/10110/00000/00000/00000',
 '«':'00000/01010/10100/10100/01010/00000/00000',
 '»':'00000/01010/00101/00101/01010/00000/00000',
 '°':'01100/10010/10010/01100/00000/00000/00000',
 '×':'00000/10001/01010/00100/01010/10001/00000',
 '÷':'00000/00100/00000/11111/00000/00100/00000',
 '±':'00000/00100/11111/00100/00000/11111/00000',
 '©':'01110/10001/10111/10101/10111/10001/01110',
 '®':'01110/10001/11101/11001/11011/10001/01110',
 '♥':'01010/11111/11111/11111/01110/00100/00000',
 '↑':'00100/01110/10101/00100/00100/00100/00100',
 '↓':'00100/00100/00100/00100/10101/01110/00100',
 '←':'00000/00100/01000/11111/01000/00100/00000',
 '→':'00000/00100/00010/11111/00010/00100/00000',
 '✓':'00000/00001/00010/10100/01000/00000/00000',
 '∞':'00000/00000/01010/10101/01010/00000/00000',
 '≤':'00001/00110/11000/00110/00001/00000/11111',
 '≥':'10000/01100/00011/01100/10000/00000/11111',
 '€':'00111/01000/11110/01000/11110/01000/00111',
 '£':'00110/01001/01000/11100/01000/01000/11111',
}
ALIASES={'\u00a0':' ','‘':"'",'’':"'",'‚':',','“':'"','”':'"','„':'"','–':'-','—':'-','−':'-'}
PATTERNS = {**LATIN,**CYRILLIC,**DIGITS,**PUNCTUATION}
for alias,target in ALIASES.items(): PATTERNS[alias]=PATTERNS[target]
PATTERNS['…']='00000/00000/00000/00000/00000/00000/10101'

# Compact five-row capitals keep a two-screen-pixel block in PixelMaz at 16px.
# These are intentional small glyph designs, rather than raster downsampling.
COMPACT = {
 'A':'01110/10001/11111/10001/10001','B':'11110/10001/11110/10001/11110',
 'C':'01111/10000/10000/10000/01111','D':'11110/10001/10001/10001/11110',
 'E':'11111/10000/11110/10000/11111','F':'11111/10000/11110/10000/10000',
 'G':'01111/10000/10111/10001/01111','H':'10001/10001/11111/10001/10001',
 'I':'11111/00100/00100/00100/11111','J':'00111/00010/00010/10010/01100',
 'K':'10001/10010/11100/10010/10001','L':'10000/10000/10000/10000/11111',
 'M':'10001/11011/10101/10001/10001','N':'10001/11001/10101/10011/10001',
 'O':'01110/10001/10001/10001/01110','P':'11110/10001/11110/10000/10000',
 'Q':'01110/10001/10101/10010/01101','R':'11110/10001/11110/10010/10001',
 'S':'01111/10000/01110/00001/11110','T':'11111/00100/00100/00100/00100',
 'U':'10001/10001/10001/10001/01110','V':'10001/10001/10001/01010/00100',
 'W':'10001/10001/10101/10101/01010','X':'10001/01010/00100/01010/10001',
 'Y':'10001/01010/00100/00100/00100','Z':'11111/00010/00100/01000/11111',
 '0':'01110/10011/10101/11001/01110','1':'00100/01100/00100/00100/01110',
 '2':'11110/00001/01110/10000/11111','3':'11110/00001/01110/00001/11110',
 '4':'10010/10010/11111/00010/00010','5':'11111/10000/11110/00001/11110',
 '6':'01111/10000/11110/10001/01110','7':'11111/00001/00010/00100/00100',
 '8':'01110/10001/01110/10001/01110','9':'01110/10001/01111/00001/11110',
 'Б':'11111/10000/11110/10001/11110','Г':'11111/10000/10000/10000/10000',
 'Д':'00110/01010/01010/11111/10001','Ё':'01010/11111/10000/11110/11111',
 'Ж':'10101/01110/00100/01110/10101','З':'11110/00001/01110/00001/11110',
 'И':'10001/10011/10101/11001/10001','Й':'01010/00100/10011/10101/11001',
 'Л':'00111/01001/01001/10001/10001','Ө':'01110/10001/11111/10001/01110',
 'П':'11111/10001/10001/10001/10001','У':'10001/10001/01111/00010/11100',
 'Ф':'00100/01110/10101/01110/00100','Ц':'10010/10010/10010/11111/00001',
 'Ч':'10001/10001/01111/00001/00001','Ш':'10101/10101/10101/10101/11111',
 'Щ':'10101/10101/10101/11111/00001','Ъ':'11000/01000/01110/01001/01110',
 'Ы':'10001/10001/11101/10101/11101','Ь':'10000/10000/11110/10001/11110',
 'Э':'11110/00001/01111/00001/11110','Ю':'10010/10101/11101/10101/10010',
 'Я':'01111/10001/01111/01001/10001',
}
for cy,la in {'А':'A','В':'B','Е':'E','К':'K','М':'M','Н':'H','О':'O','Р':'P','С':'C','Т':'T','Ү':'Y','Х':'X'}.items():
    COMPACT[cy]=COMPACT[la]
# Lowercase forms remain distinct, with compact ascenders and accents.
COMPACT.update({ch:pattern for ch,pattern in PATTERNS.items() if ch.islower() and len(pattern.split('/'))==5})
COMPACT.update({
 'b':'10000/10000/11110/10001/11110','d':'00001/00001/01111/10001/01111',
 'f':'00110/01000/11100/01000/01000','g':'01111/10001/01111/00001/11110',
 'h':'10000/10000/11110/10001/10001','i':'00100/00000/01100/00100/01110',
 'j':'00010/00000/00010/10010/01100','k':'10000/10000/10010/11100/10010',
 'l':'01100/00100/00100/00100/01110','p':'11110/10001/11110/10000/10000',
 'q':'01111/10001/01111/00001/00001','t':'01000/11100/01000/01000/00110',
 'y':'10001/10001/01111/00010/11100','б':'00111/01000/11110/10001/01110',
 'ё':'01010/01110/11111/10000/01111','й':'01010/00100/10011/10101/11001',
 'р':'11110/10001/11110/10000/10000','у':'10001/10001/01111/00010/11100',
 'ү':'10001/01010/00100/00100/00100','ф':'00100/01110/10101/01110/00100',
 'ц':'10010/10010/10010/11111/00001','щ':'10101/10101/10101/11111/00001',
})
for ch,pattern in PATTERNS.items():
    if ch not in COMPACT:
        lines=pattern.split('/')
        COMPACT[ch]='/'.join(lines[i] for i in (0,2,3,4,6)) if len(lines)==7 else pattern
COMPACT.update({'!':'00100/00100/00100/00000/00100',
                '?':'11110/00001/00110/00000/00100',
                ':':'00000/00100/00000/00100/00000',
                ';':'00000/00100/00000/00100/01000'})


def _metrics(source):
    f=TTFont(source)
    cmap=f.getBestCmap(); gs=f.getGlyphSet(); bounds=BoundsPen(gs)
    gs[cmap[ord('H')]].draw(bounds)
    _,baseline,_,cap_top=bounds.bounds
    advance=f['hmtx'][cmap[ord('A')]][0]
    result=(f['head'].unitsPerEm,f['hhea'].ascent,f['hhea'].descent,
            round(baseline),round(cap_top-baseline),advance)
    f.close()
    return result


def build_pixel_font(source,destination):
    """Create an original font matching a local game's nominal line metrics."""
    source=Path(source); destination=Path(destination)
    upem,ascender,descender,baseline,cap_height,advance=_metrics(source)
    compact='maz' in source.name.lower()
    # PixelMaz needs its original five-row size for clean 16px rasterization.
    rows=5 if compact else 7
    step_y=cap_height/rows
    step_x=(advance-(advance/6))/5
    glyph_order=['.notdef']+[f'uni{ord(ch):04X}' for ch in sorted(PATTERNS,key=ord)]
    cmap={ord(ch):f'uni{ord(ch):04X}' for ch in PATTERNS}
    glyphs={}; metrics={}
    all_patterns={'.notdef':'11111/10001/10101/10001/11111' if compact else '11111/10001/10101/10101/10101/10001/11111'}
    all_patterns.update({cmap[ord(ch)]:COMPACT.get(ch,pattern) if compact else pattern for ch,pattern in PATTERNS.items()})
    for name,pattern in all_patterns.items():
        grid=pattern.split('/')
        n=len(grid)
        # Normal lowercase has five rows; ascenders/descenders use seven.
        sy=step_y if compact or n==7 else min(step_y,cap_height/7)
        top=baseline+sy*n
        ch=next((chr(cp) for cp,g in cmap.items() if g==name),'')
        if not compact and ch in 'gpqyрҳуүфцщ':
            top=baseline+sy*5
        bottom=top-sy*n
        if bottom<descender:
            top+=descender-bottom
        if top>ascender:
            sy=min(sy,(ascender-descender)/n); top=ascender
        x_offset=round((advance-step_x*5)/2)
        pen=TTGlyphPen(None)
        # Merge each horizontal run. Every contour is an axis-aligned rectangle.
        for y,row in enumerate(grid):
            x=0
            while x<len(row):
                if row[x]!='1': x+=1; continue
                start=x
                while x<len(row) and row[x]=='1': x+=1
                x0=round(x_offset+start*step_x); x1=round(x_offset+x*step_x)
                y1=round(top-y*sy); y0=round(top-(y+1)*sy)
                pen.moveTo((x0,y0)); pen.lineTo((x0,y1)); pen.lineTo((x1,y1)); pen.lineTo((x1,y0)); pen.closePath()
        glyphs[name]=pen.glyph(); metrics[name]=(advance,x_offset)
    builder=FontBuilder(upem,isTTF=True)
    builder.setupGlyphOrder(glyph_order); builder.setupCharacterMap(cmap)
    builder.setupGlyf(glyphs); builder.setupHorizontalMetrics(metrics)
    builder.setupHorizontalHeader(ascent=ascender,descent=descender,lineGap=0)
    style='Compact' if compact else 'Regular'
    family='Barony Mongolian Pixel'
    builder.setupNameTable({
        'familyName':family,'styleName':style,
        'uniqueFontIdentifier':f'{family}-{source.stem}-1.0',
        'fullName':f'{family} {source.stem}',
        'psName':f'BaronyMongolianPixel-{source.stem.replace("_", "").replace(" ", "")}',
        'version':'Version 1.000',
        'copyright':'Original grid outlines (c) 2026 Barony Mongolian contributors.',
        'licenseDescription':'MIT License. All glyph outlines are original grid designs; no game or Microsoft font outlines are included.',
        'licenseInfoURL':'https://opensource.org/license/mit',
    })
    builder.setupOS2(sTypoAscender=ascender,sTypoDescender=descender,sTypoLineGap=0,
                     usWinAscent=max(0,ascender),usWinDescent=max(0,-descender),
                     sxHeight=round(step_y*5),sCapHeight=cap_height,
                     fsType=0)
    builder.setupPost(isFixedPitch=1)
    builder.setupMaxp()
    builder.font['head'].created=builder.font['head'].modified=2082844800
    builder.font.recalcTimestamp=False
    destination.parent.mkdir(parents=True,exist_ok=True)
    builder.save(destination)
    assert_pixel_font(destination)
    print('Original pixel font:',source.name,len(cmap),'glyphs')


def assert_pixel_font(path):
    """Verify coverage, line box and the actual grid-based outline geometry."""
    f=TTFont(path); cmap=f.getBestCmap()
    assert all(ord(c) in cmap for c in ALPHABET+'ӨөҮү'+''.join(chr(i) for i in range(32,127)))
    assert all(f['name'].getDebugName(n) and 'Barony Mongolian Pixel' in f['name'].getDebugName(n) for n in (1,4))
    for name in f.getGlyphOrder():
        g=f['glyf'][name]
        assert not g.isComposite(),(path,name,'Composite includes unknown outlines')
        if not g.numberOfContours: continue
        coords,ends,flags=g.getCoordinates(f['glyf'])
        assert all(flag&1 for flag in flags),(path,name,'Curve in pixel font')
        start=0
        for end in ends:
            points=list(coords[start:end+1]); start=end+1
            assert len(points)==4,(path,name,'Non-rectangular pixel contour')
            for (x0,y0),(x1,y1) in zip(points,points[1:]+points[:1]):
                assert (x0==x1) != (y0==y1),(path,name,'Diagonal or empty segment')
        g.recalcBounds(f['glyf'])
        assert g.yMin>=f['hhea'].descent and g.yMax<=f['hhea'].ascent,(path,name,'Outside line box')
        assert g.xMin>=0 and g.xMax<=f['hmtx'][name][0],(path,name,'Outside advance')
    f.close()


def render_preview(font_root,output):
    """Render actual generated TTF files at normal game sizes and 4x zoom."""
    from PIL import Image,ImageDraw,ImageFont
    font_root=Path(font_root); output=Path(output)
    samples=[('fonts/pixel_maz_multiline.ttf',16,'ТОГЛОХ  ТОХИРГОО  ГАРАХ'),
             ('fonts/pixel_maz_multiline.ttf',16,'Монгол хэл: Өвөл, үүр, ёс, шинэ аялал.'),
             ('fonts/pixelmix.ttf',16,'АБВГДЕЁЖЗИЙКЛМНОӨПРСТУҮФХЦЧШЩЪЫЬЭЮЯ'),
             ('fonts/pixelmix.ttf',16,'абвгдеёжзийклмноөпрстуүфхцчшщъыьэюя'),
             ('lang/en.ttf',24,'English 123  +20%  HP/MP  Монгол Өө Үү')]
    im=Image.new('RGB',(1120,720),'#142536'); d=ImageDraw.Draw(im)
    # Labels also use the generated font, so the proof contains no OS-font art.
    label_font=ImageFont.truetype(str(font_root/'fonts/pixelmix.ttf'),12)
    d.text((24,18),'BARONY MONGOLIAN / ORIGINAL PIXEL FONT',font=label_font,fill='#d3aa5d')
    y=55
    for path,size,text in samples:
        d.text((24,y),f'{Path(path).name} / {size}px',font=label_font,fill='#99aebd')
        font=ImageFont.truetype(str(font_root/path),size)
        d.text((24,y+21),text,font=font,fill='#f4e1b8')
        line=Image.new('RGB',(268,23),'#142536'); ld=ImageDraw.Draw(line)
        ld.text((0,-1),text,font=font,fill='#f4e1b8')
        im.paste(line.resize((1072,92),resample=Image.Resampling.NEAREST),(24,y+46))
        y+=130
    output.parent.mkdir(parents=True,exist_ok=True); im.save(output)


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_root',type=Path); parser.add_argument('destination_root',type=Path)
    parser.add_argument('--preview',type=Path)
    args=parser.parse_args()
    for p in sorted((args.source_root/'fonts').glob('*.ttf')):
        build_pixel_font(p,args.destination_root/'fonts'/p.name)
    build_pixel_font(args.source_root/'lang/en.ttf',args.destination_root/'lang/en.ttf')
    if args.preview: render_preview(args.destination_root,args.preview)
