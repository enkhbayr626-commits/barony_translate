from localization import *
from fontTools.ttLib import TTFont

def validate():
    report={'json_files':0,'language_entries':0,'changed_strings':0,'fonts':0,'original_files_verified':0}
    direct=json.loads((ROOT/'direct-language-state.json').read_text('utf-8')) if (ROOT/'direct-language-state.json').exists() else None
    def original_path(rel):
        rel=Path(rel).as_posix()
        for base in (ROOT/'english-backup',GAME/'.barony-mongolian-backup/originals'):
            if (base/rel).is_file(): return base/rel
        return GAME/rel
    critical=lambda s:[t for t in TOKEN.findall(s) if not t.isspace()]
    for f in MOD.rglob('*.json'):
        rel=f.relative_to(MOD)
        if rel.as_posix() in ('data/callout_wheel.json','data/follower_wheel.json'):
            assert f.stat().st_size<65536,('Exceeds Barony radial JSON buffer',rel)
        src=json.loads((SOURCE/rel).read_text('utf-8-sig')); dst=json.loads(f.read_text('utf-8'))
        def cmp(a,b,p=()):
            assert type(a)==type(b),(rel,p,'changed type')
            if isinstance(a,dict):
                assert list(a)==list(b),(rel,p,'changed keys')
                for k in a: cmp(a[k],b[k],p+(k,))
            elif isinstance(a,list):
                assert len(a)==len(b),(rel,p,'changed list size')
                for i,(x,y) in enumerate(zip(a,b)): cmp(x,y,p+(i,))
            elif a!=b:
                assert isinstance(a,str) and translatable(rel,p,a),(rel,p,'changed technical data')
                assert critical(a)==critical(b),(rel,p,'changed control tokens')
                report['changed_strings']+=1
        cmp(src,dst); report['json_files']+=1
        if rel.as_posix()=='data/class_descriptions.json':
            for key,entry in src['descriptions'].items():
                if not entry['desc']: continue
                cols=max(map(len,entry['desc'][1:]))
                assert all(len(line)<=cols for line in dst['descriptions'][key]['desc'][1:]),('Class text exceeds original line width',key)
        if rel.as_posix()=='data/race_descriptions.json':
            for key,entry in src['descriptions'].items():
                cols=max(map(len,entry['left_align']+entry['right_align']))
                actual=dst['descriptions'][key]
                assert all(len(line)<=cols for line in actual['left_align']+actual['right_align']),('Race text exceeds original column width',key)
    for f in MOD.rglob('en.txt'):
        rel=f.relative_to(MOD)
        src=entries((SOURCE/rel).read_text('utf-8-sig'))
        dst=entries(f.read_text('utf-8'))
        assert [m[1] for m in src]==[m[1] for m in dst], ('Language IDs missing/reordered',rel)
        for a,b in zip(src,dst):
            assert critical(a[2])==critical(b[2]),('Printf/control token changed',rel,a[1])
            assert len(b[2].encode('utf-8'))<8192,('Entry exceeds parser buffer',rel,a[1])
            report['changed_strings']+=a[2]!=b[2]
        report['language_entries']+=len(dst)
    from fonts.pixel_cyrillic import assert_pixel_font
    for f in MOD.rglob('*.ttf'):
        assert_pixel_font(f)
        font=TTFont(f); original=TTFont(original_path(f.relative_to(MOD)))
        assert font['hhea'].ascent==original['hhea'].ascent and font['hhea'].descent==original['hhea'].descent
        assert font['head'].unitsPerEm==original['head'].unitsPerEm
        report['fonts']+=1
    for rel,digest in json.loads((ROOT/'original-hashes.json').read_text()).items():
        assert hashlib.sha256(original_path(rel).read_bytes()).hexdigest()==digest,'Modified original '+rel
        report['original_files_verified']+=1
    if direct:
        from direct_language import verify
        verify()
        report['direct_mongolian_active']=direct['active']
    portable=GAME/'.barony-mongolian-backup/manifest.json'
    if portable.exists():
        state=json.loads(portable.read_text('utf-8-sig'))
        for rec in state['files']:
            expected=rec['installedSha256'] if state['state']=='active' else rec['originalSha256']
            assert hashlib.sha256((GAME/rec['path']).read_bytes()).hexdigest()==expected,('Portable installed file mismatch',rec['path'])
            assert hashlib.sha256((portable.parent/'originals'/rec['path']).read_bytes()).hexdigest()==rec['originalSha256'],('Portable backup mismatch',rec['path'])
        report['portable_installer_state']=state['state']
    (ROOT/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
if __name__=='__main__': validate()
