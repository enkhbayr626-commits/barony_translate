from localization import *
from fonts.pixel_cyrillic import build_pixel_font
from PIL import Image,ImageDraw,ImageFont


def add_cyrillic(src,dst):
    # Generate wholly original pixel outlines, including Latin. Local game fonts
    # supply only the target em/line metrics, never redistributed outlines.
    build_pixel_font(src,dst)


def build():
    manual=json.loads((ROOT/'manual_mn.json').read_text('utf-8'))
    seasonal={}
    for f in sorted((ROOT/'manual/themes').glob('*.tsv')):
        seasonal[f.stem]={}
        for line in f.read_text('utf-8').splitlines():
            if not line or line.startswith('#'): continue
            key,value=line.split('\t',1)
            if key in seasonal[f.stem]: raise ValueError('Duplicate seasonal ID: '+key)
            seasonal[f.stem][key]=value.replace('\\n','\n')
    for f in sorted((ROOT/'manual').glob('*.tsv')):
        for line in f.read_text('utf-8').splitlines():
            if not line or line.startswith('#'): continue
            en,mn=line.split('\t',1)
            en=en.replace('\\n','\n')
            mn=mn.replace('\\n','\n')
            if f.name.endswith('.ids.tsv'):
                manual['ids'][en]=mn
                continue
            if en in manual['strings'] and manual['strings'][en]!=mn:
                raise ValueError('Conflicting manual translation: '+en)
            manual['strings'][en]=mn
    cache=json.loads((ROOT/'translation-cache.json').read_text('utf-8')) if (ROOT/'translation-cache.json').exists() else {}
    for en,mn in manual['strings'].items():
        cache[en]=mn
        cache.setdefault(en.lower(),mn.lower()); cache.setdefault(en.upper(),mn.upper())
    original=(SOURCE/'lang/en.txt').read_text('utf-8-sig')
    # Legacy item descriptions construct a name from count, quality, colour and
    # enchantment. Translate this finite grammar while preserving its arguments.
    quality={'broken':'эвдэрсэн','decrepit':'муудсан','worn':'элэгдсэн',
             'serviceable':'хэвийн','excellent':'маш сайн','destroyed':'сүйдсэн',
             'cracked':'цуурсан','rough':'барзгар','flawed':'сэвтэй','flawless':'сэвгүй',
             'evaporated':'ууршсан','cloudy':'булингартай','swirly':'хуйларсан',
             'plain':'энгийн','bubbly':'хөөсөрсөн','shredded':'сэмэрсэн','torn':'урагдсан',
             'faded':'гандсан','marked':'тэмдэгтэй','brand new':'цоо шинэ',
             'rotten':'ялзарсан','mouldy':'хөгцөрсөн','aged':'удсан',
             'slightly aged':'жаахан удсан','fresh':'шинэхэн'}
    prefix=re.compile(r'^(a|an|%d) ('+'|'.join(sorted(map(re.escape,quality),key=len,reverse=True))+r')( .*)$')
    for m in entries(original):
        if 982<=int(m[1])<=1084 and (q:=prefix.fullmatch(m[2])):
            manual['ids'].setdefault(m[1],('%d ' if q[1]=='%d' else '')+quality[q[2]]+q[3])
    for m in entries(original):
        if m[1] in manual['ids']: cache[m[2]]=manual['ids'][m[1]]
    # Honor source outer whitespace, newlines, and printf parameters exactly.
    def tr(s):
        if s not in cache: return s
        v=cache[s]
        meaningful=lambda x:[t for t in TOKEN.findall(x) if not t.isspace()]
        if meaningful(s)!=meaningful(v): raise ValueError('Invalid formatting tokens: '+repr(s)+' => '+repr(v))
        return v
    changed=0; total=0; perfile={}
    for f in sorted(SOURCE.rglob('*')):
        if not f.is_file(): continue
        rel=f.relative_to(SOURCE); n=0
        text=f.read_text('utf-8-sig')
        if f.name=='en.txt' and f.parent.name=='lang':
            overrides=seasonal.get(rel.parts[1],{}) if rel.parts[0]=='themes' else {}
            def repl(m):
                nonlocal n,total,changed
                total+=1; v=overrides.get(m[1],tr(m[2])); n+=v!=m[2]; changed+=v!=m[2]
                meaningful=lambda x:[t for t in TOKEN.findall(x) if not t.isspace()]
                if meaningful(m[2])!=meaningful(v): raise ValueError(f'Invalid seasonal tokens: {rel}:{m[1]}')
                return m[1]+' '+v+'#'
            out=re.sub(r'(?m)^(\d+) ([\s\S]*?)#',repl,text)
        elif f.suffix=='.json':
            obj=json.loads(text)
            contextual={}
            if rel.as_posix()=='data/class_descriptions.json':
                translations=json.loads((ROOT/'manual/classes.json').read_text('utf-8'))
                for classkey,translation in translations.items():
                    original_lines=obj['descriptions'][classkey]['desc']
                    width=max(map(len,original_lines[1:])); count=len(original_lines)-1
                    lines=textwrap.wrap(translation['text'],width=width,break_long_words=False,break_on_hyphens=False)
                    if len(lines)>count: raise ValueError(f'Class description overflows: {classkey}: {len(lines)} > {count}')
                    translated_lines=[translation['name']]+lines+['']*(count-len(lines))
                    for i,line in enumerate(translated_lines): contextual[('descriptions',classkey,'desc',i)]=line
            for p,s in list(walk(obj)):
                if translatable(rel,p,s):
                    total+=1; v=contextual[p] if p in contextual else tr(s)
                    if v!=s: setpath(obj,p,v); n+=1; changed+=1
            # Barony's radial menu readers use a fixed 65,536-byte stack buffer.
            # Compact JSON prevents harmless indentation from overflowing it.
            out=json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n'
        else:
            parts=re.split(r'(\n\s*\n)',text)
            for i,s in enumerate(parts):
                if translatable(rel,(),s):
                    total+=1; v=tr(s); n+=v!=s; changed+=v!=s; parts[i]=v
            out=''.join(parts)
        if n:
            dst=MOD/rel; dst.parent.mkdir(parents=True,exist_ok=True); dst.write_text(out,encoding='utf-8')
            perfile[rel.as_posix()]=n
    # Direct mode preserves pristine originals here; never derive a new font
    # from the already patched active game files.
    fontbase=ROOT/'english-backup' if (ROOT/'english-backup/fonts').is_dir() else GAME
    for f in (fontbase/'fonts').glob('*.ttf'): add_cyrillic(f,MOD/'fonts'/f.name)
    add_cyrillic(fontbase/'lang/en.ttf',MOD/'lang/en.ttf')
    # A plain generated label, without altering any game artwork.
    im=Image.new('RGB',(512,512),'#142536'); draw=ImageDraw.Draw(im)
    draw.rectangle((32,32,480,480),outline='#d3aa5d',width=5)
    draw.rectangle((60,95,452,230),fill='#bd2433'); draw.rectangle((190,95,322,230),fill='#1976bd')
    previewfont=str(MOD/'fonts/pixelmix.ttf')
    draw.text((256,280),'МОНГОЛ ХЭЛ',font=ImageFont.truetype(previewfont,48),anchor='mm',fill='#f4e1b8')
    draw.text((256,350),'BARONY',font=ImageFont.truetype(previewfont,40),anchor='mm',fill='white')
    draw.text((256,410),'ТУРШИЛТЫН ХУВИЛБАР',font=ImageFont.truetype(previewfont,24),anchor='mm',fill='#c5cbd3')
    im.save(MOD/'preview.png')
    report={'translated_units':changed,'source_units':len(source_units()),'files':perfile,'complete':False,'method':'Local manual translation; remaining content is English. No bulk text sent to an external service.'}
    (ROOT/'coverage.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=True,indent=2))
if __name__=='__main__': build()
