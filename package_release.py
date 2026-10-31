"""Generate portable payload checksums and a self-contained Windows ZIP."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parent
PAYLOAD=ROOT/'Barony-Mongolian'
VERSION='0.3.0'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    originals=json.loads((ROOT/'original-hashes.json').read_text('utf-8'))
    records=[]
    for f in sorted(PAYLOAD.rglob('*')):
        if not f.is_file() or f.suffix not in ('.json','.txt','.ttf'): continue
        rel=f.relative_to(PAYLOAD).as_posix()
        original=originals.get(rel)
        if original is None:
            # Source font files are never distributed separately as originals.
            backup=ROOT/'english-backup'/rel
            if backup.exists(): original=sha(backup)
        if original is None: raise ValueError('Missing known English checksum: '+rel)
        records.append({'path':rel,'sha256':sha(f),'originalSha256':original})
    manifest={'schemaVersion':1,'version':VERSION,'gameVersion':'5.0.2.2026.04.03','files':records}
    (ROOT/'package-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    files=[ROOT/x for x in ('README.md','Install-Mongolian.ps1','Uninstall-Mongolian.ps1','package-manifest.json')]
    files += [f for dirname in ('scripts','docs','Barony-Mongolian') for f in (ROOT/dirname).rglob('*') if f.is_file()]
    out=ROOT/'dist'/f'Barony-Mongolian-{VERSION}.zip'
    out.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for f in files: z.write(f,'Barony-Mongolian-'+VERSION+'/'+f.relative_to(ROOT).as_posix())
    (out.parent/(out.name+'.sha256')).write_text(sha(out)+'  '+out.name+'\n',encoding='ascii')
    print(f'Packaged {len(records)} game files; ZIP {out.stat().st_size:,} bytes')

if __name__=='__main__': main()
