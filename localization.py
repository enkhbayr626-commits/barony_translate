"""Build a reversible Mongolian content mod from the installed Barony assets."""
from pathlib import Path
import json, re, hashlib, shutil, textwrap, collections, os
ROOT=Path(__file__).resolve().parent
GAME=Path(os.environ.get('BARONY_PATH',r'C:\Program Files (x86)\Steam\steamapps\common\Barony'))
SOURCE=ROOT/'source'
MOD=ROOT/'Barony-Mongolian'
DATA_FILES=['achievements','callout_wheel','charsheet','class_descriptions','follower_wheel','HUD_settings','monster_data','race_descriptions','skillsheet_entries','status_effects','tutorial_strings']
# A bare percentage followed by prose ("20% to...") is not a printf argument.
# These assets do not use printf's optional space flag.
TOKEN=re.compile(r'%(?:\d+\$)?[-+#0]*(?:\d+|\*)?(?:\.(?:\d*|\*))?(?:hh|ll|[hljztL])?[diuoxXfFeEgGaAcspn]|%%|%|\$|#+|\^|\*[0-9]+|\r\n|\n|\t')
def walk(x,path=()):
    if isinstance(x,dict):
        for k,v in x.items(): yield from walk(v,path+(k,))
    elif isinstance(x,list):
        for i,v in enumerate(x): yield from walk(v,path+(i,))
    elif isinstance(x,str): yield path,x
def setpath(obj,path,v):
    for p in path[:-1]: obj=obj[p]
    obj[path[-1]]=v
def entries(txt):
    # Leading IDs and # terminators are the game's parser contract.
    return list(re.finditer(r'(?m)^(\d+) ([\s\S]*?)#',txt))
def snapshot():
    state=ROOT/'direct-language-state.json'
    if state.exists() and json.loads(state.read_text('utf-8')).get('active'):
        raise RuntimeError('Restore English before refreshing original source snapshots; direct Mongolian is active.')
    portable=GAME/'.barony-mongolian-backup/manifest.json'
    if portable.exists() and json.loads(portable.read_text('utf-8-sig')).get('state')!='restored':
        raise RuntimeError('Uninstall Mongolian before refreshing English source snapshots.')
    files=[GAME/'lang/en.txt']+list((GAME/'lang').rglob('*.json'))
    files += [GAME/'data'/f'{s}.json' for s in DATA_FILES]
    files += list((GAME/'data/story').glob('*.json'))
    files += [f for f in (GAME/'data/scripts').rglob('script.json')]
    files += list((GAME/'books').glob('*.txt'))
    for theme in ('scarony','merry'):
        files += [GAME/'themes'/theme/'lang/en.txt',GAME/'themes'/theme/'lang/item_names.json',GAME/'themes'/theme/'items/item_tooltips.json']
    manifest={}
    for f in files:
        rel=f.relative_to(GAME); dst=SOURCE/rel
        dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(f,dst)
        manifest[rel.as_posix()]=hashlib.sha256(f.read_bytes()).hexdigest()
    f=GAME/'items/item_tooltips.json'; dst=SOURCE/'items/item_tooltips.json'
    dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(f,dst)
    manifest['items/item_tooltips.json']=hashlib.sha256(f.read_bytes()).hexdigest()
    for f in list((GAME/'fonts').glob('*.ttf'))+[GAME/'lang/en.ttf']:
        manifest[f.relative_to(GAME).as_posix()]=hashlib.sha256(f.read_bytes()).hexdigest()
    (ROOT/'original-hashes.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('Snapshotted',len(manifest),'files')
def translatable(rel,p,s):
    if not re.search('[A-Za-z]',s): return False
    if s.startswith('DEPRECATED') or re.fullmatch(r'(?:NULL|null|UNKNOWN|unnamed)',s): return False
    key=next((v for v in reversed(p) if isinstance(v,str)),'')
    rel=rel.as_posix()
    if rel.startswith('themes/'):
        rel='/'.join(rel.split('/')[2:])
    if rel.startswith('lang/compendium_lang/contents_'): return False  # Values are internal navigation IDs; keys are labels.
    if rel.startswith('lang/'):
        return key not in ('comment',)
    if rel.startswith('books/'): return True
    if '/story/' in rel: return p[0]=='text'
    if '/scripts/' in rel: return key in ('sign','message','bubble_dialogue','bubble_grave','bubble_sign')
    fn=Path(rel).stem
    if fn=='achievements': return key in ('name','description')
    if fn=='callout_wheel': return key in ('text','msg_says','msg_emote','msg_emote_you','msg_emote_to_you') or p[0]=='help_strings'
    if fn=='charsheet': return not ('path' in key or 'width' in key)
    if fn=='class_descriptions': return key=='desc'
    if fn=='follower_wheel': return key=='text'
    if fn=='HUD_settings': return key in ('text','title')
    if fn=='monster_data': return key.startswith('localized_')
    if fn=='race_descriptions': return key in ('title','left_align','right_align')
    if fn=='skillsheet_entries': return key in ('name','description','legend_text','title','title_short','shortname','value','alchemy_potion_names_to_filter')
    if fn=='status_effects': return key in ('name','desc')
    if fn=='tutorial_strings': return True
    if fn=='item_tooltips':
        if key in ('icon_path','conditional_attribute'): return False
        if s.startswith('template_') or re.fullmatch(r'[A-Z][A-Z0-9_]+',s): return False
        return True
    return False
def source_units():
    result=[]
    for f in sorted(SOURCE.rglob('*')):
        if not f.is_file(): continue
        rel=f.relative_to(SOURCE)
        if f.name=='en.txt' and f.parent.name=='lang':
            for m in entries(f.read_text('utf-8-sig')):
                if translatable(rel,(),m[2]): result.append((rel,('id',int(m[1])),m[2]))
        elif f.suffix=='.json':
            obj=json.loads(f.read_text('utf-8-sig'))
            if rel.parent.as_posix()=='lang/compendium_lang' and f.name.startswith('contents_'):
                for section,rows in obj.items():
                    if not isinstance(rows,list): continue
                    for i,row in enumerate(rows):
                        for key in row: result.append((rel,('display_key',section,i),key))
                continue
            for p,s in walk(obj):
                if translatable(rel,p,s): result.append((rel,p,s))
        else:
            text=f.read_text('utf-8-sig')
            # Books are translated as paragraphs, retaining their existing filenames.
            for i,s in enumerate(re.split(r'(\n\s*\n)',text)):
                if translatable(rel,(),s): result.append((rel,('paragraph',i),s))
    return result
def catalog():
    units=source_units(); strings=list(dict.fromkeys(s for _,_,s in units))
    (ROOT/'catalog.json').write_text(json.dumps(strings,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Text units:',len(units),'Unique:',len(strings),'Characters:',sum(map(len,strings)))
    for rel,n in collections.Counter(str(r) for r,_,_ in units).most_common(12): print(n,rel)
if __name__=='__main__':
    import sys
    if 'snapshot' in sys.argv: snapshot()
    catalog()
