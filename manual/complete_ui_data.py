from pathlib import Path
import json,functools,re,localization as l
ROOT=Path(__file__).resolve().parents[1]
TRANS={}
for file in (ROOT/'manual').glob('ui_*.tsv'):
 for line in file.read_text('utf-8').splitlines():
  if not line or line.startswith('//'):continue
  a,b=line.split('\t',1); TRANS[a.replace('\\n','\n').replace('\\t','\t')]=b.replace('\\n','\n').replace('\\t','\t')
for file in (ROOT/'source/data').glob('callout_wheel.json'):
 for _, s in l.walk(json.loads(file.read_text('utf-8-sig'))):
  if s.startswith('%s"'):
   inner=s[3:];suffix='"' if inner.endswith('"') else ''
   core=inner[:-1] if suffix else inner
   if core in TRANS: TRANS[s]='%s"'+TRANS[core]+suffix
achsrc=json.loads((ROOT/'source/data/achievements.json').read_text('utf-8-sig'))
achunits=[s for p,s in l.walk(achsrc) if l.translatable(Path('data/achievements.json'),p,s)]
for line in (ROOT/'manual/ui_achievements.rows').read_text('utf-8-sig').splitlines():
 i,name,desc=line.split('\t');i=int(i);TRANS[achunits[i*2]]=name;TRANS[achunits[i*2+1]]=desc.replace('хороo','хороо').replace('онo','оно')
files=list((ROOT/'source/data').glob('*.json'))+list((ROOT/'source/data/scripts').rglob('script.json'))+list((ROOT/'source/items').glob('*.json'))
for file in files:
 rel=file.relative_to(ROOT/'source'); base=ROOT/'Barony-Mongolian'/rel; dest=ROOT/'manual/overrides'/rel
 source=json.loads(file.read_text('utf-8-sig')); obj=json.loads((dest if dest.exists() else base if base.exists() else file).read_text('utf-8-sig'))
 for p,s in l.walk(source):
  if not l.translatable(rel,p,s):continue
  if s in TRANS:l.setpath(obj,p,TRANS[s])
 dest.parent.mkdir(exist_ok=True,parents=True);dest.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n','utf-8')
print('Mappings:',len(TRANS))
