from pathlib import Path
import csv,sys
RUN=Path(__file__).resolve().parents[1]
cats=dict(r='rice',n='noodle',b='burger',p='pizza',f='fried',g='grill',u='soup',s='salad',e='dessert',d='drink',o='other')
fields=['index','category','n_dishes','width_frac','height_frac','complexity','angle','brightness','flags','bbox_note','description']
records=[]
for line in sys.stdin.read().strip().splitlines():
    v=line.split(' ',9)
    if len(v)!=10: raise ValueError(line)
    i,c,n,wh,complexity,angle,bright,flags,bbox,desc=v
    w,h=map(int,wh.split('x'))
    records.append(dict(zip(fields,[int(i),cats[c],'3plus' if n=='3' else n,w*10,h*10,dict(s='simple',m='medium',c='complex')[complexity],dict(t='top',a='angled',s='side')[angle],dict(d='dark',m='medium',b='bright')[bright],'' if flags=='-' else flags,dict(C='cropped at edge',A='main dish ambiguous',N='no food container visible',B='container boundary unclear',D='main dish ambiguous; cropped at edge').get(bbox,'' if bbox=='-' else bbox),desc])))
p=RUN/'outputs'/'visual_annotations.csv'
if p.exists():
    with p.open(encoding='utf-8-sig',newline='') as f: old=list(csv.DictReader(f))
else: old=[]
indices={int(x['index']) for x in old}
if any(r['index'] in indices for r in records): raise ValueError('Duplicate annotation index')
with p.open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(old+records)
print(f'Recorded {len(records)} visual observations; total {len(old)+len(records)}.')
