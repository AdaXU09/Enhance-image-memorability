from pathlib import Path
from collections import Counter
import csv, json, hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'AI_selection_run'
with (ROOT/'pool_final.csv').open(encoding='utf-8-sig',newline='') as f:
    source=list(csv.DictReader(f))
all_files=[p for p in (ROOT/'pool').rglob('*') if p.is_file()]
lookup={}
for p in all_files: lookup.setdefault(p.name,[]).append(p)
rows=[]
seen=Counter()
for i,row in enumerate(source,1):
    name=row['filename']; seen[name]+=1
    if seen[name]>1: raise RuntimeError('Duplicate manifest name requires review: '+name)
    paths=lookup.get(name,[])
    if len(paths)!=1: raise RuntimeError(f'{name}: {len(paths)} matching files')
    p=paths[0]
    with Image.open(p) as im:
        im.load(); w,h=im.size
        pixel_hash=hashlib.sha256(im.tobytes()).hexdigest()
    rows.append(dict(index=i,filename=name,original_filename=name,width=w,height=h,short_side=min(w,h),file_size=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),pixel_sha256=pixel_hash,source_path=str(p)))
with (RUN/'outputs'/'metadata.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
def percentile(values,q):
    s=sorted(values); x=(len(s)-1)*q; i=int(x);return s[i]+(s[min(i+1,len(s)-1)]-s[i])*(x-i)
v=[r['short_side'] for r in rows]
bands={'under 330':sum(x<330 for x in v),'330 to 450':sum(330<=x<=450 for x in v),'450 to 600':sum(450<x<=600 for x in v),'over 600':sum(x>600 for x in v)}
pixel_counts=Counter(r['pixel_sha256'] for r in rows)
audit=dict(pool_files=len(all_files),listed_files=len(rows),ignored_files=sorted(set(p.name for p in all_files)-set(r['filename'] for r in rows)),duplicate_filenames={k:[str(p) for p in ps] for k,ps in lookup.items() if len(ps)>1},duplicate_manifest_filenames=[k for k,n in seen.items() if n>1],short_side=dict(min=min(v),q25=percentile(v,.25),median=percentile(v,.5),q75=percentile(v,.75),max=max(v)),bands=bands,exact_pixel_duplicate_groups=[[r['index'] for r in rows if r['pixel_sha256']==k] for k,n in pixel_counts.items() if n>1],manifest_sha256=hashlib.sha256((ROOT/'pool_final.csv').read_bytes()).hexdigest())
(RUN/'outputs'/'metadata_audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
print(json.dumps(audit,indent=2))
