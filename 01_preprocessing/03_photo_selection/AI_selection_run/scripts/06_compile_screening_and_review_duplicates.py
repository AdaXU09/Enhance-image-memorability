from pathlib import Path
import csv,json,hashlib,math
from collections import Counter
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
TMP=ROOT/'outputs'/'_inspection'
metadata=json.loads((TMP/'metadata.json').read_text(encoding='utf-8'))
annotations=[]
for i in range(1,5):
    annotations.extend(json.loads((TMP/f'batch_{i}.json').read_text(encoding='utf-8')))
assert len(annotations)==997
assert sorted(int(a[0]) for a in annotations)==list(range(1,998))
COLUMNS=['filename','base_id','width','height','short_side','has_person','has_text','is_collage','quality_ok','category','n_dishes','main_dish_bbox_pct','bbox_note','complexity','angle','brightness','duplicate_of','note']
rows=[]
for a in annotations:
    assert len(a)==16,a
    idx,p,t,c,q,cat,n,wf,hf,bn,co,an,br,dup,note,identity=a
    idx=int(idx); m=metadata[idx-1]
    wf=int(wf);hf=int(hf);assert wf in range(10,101,10) and hf in range(10,101,10)
    bbox=max(5,min(100,5*math.floor((wf*hf/100)/5+.5)))
    vals=[m['filename'],Path(m['filename']).stem,m['width'],m['height'],m['short_side'],p,t,c,q,cat,n,bbox,bn,co,an,br,metadata[int(dup)-1]['filename'] if dup else '',note]
    r=dict(zip(COLUMNS,vals));r.update(index=idx,identity=identity,width_frac=wf,height_frac=hf)
    rows.append(r)
(TMP/'review_rows.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
with (ROOT/'outputs'/'file_metadata.csv').open('w',newline='',encoding='utf-8-sig') as f:
    cols=['filename','width','height','short_side','file_size','image_format','sha256']
    out=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore');out.writeheader();out.writerows(metadata)
# In-memory comparison signatures only; originals and final copies are never re-encoded.
N=32
x=np.arange(N); k=np.arange(8)[:,None]
basis=np.cos(np.pi*(2*x+1)*k/(2*N))
ph=[];dh=[]
for m in metadata:
    with Image.open(ROOT.parent/'pool'/m['filename']) as im:
        a=np.asarray(im.convert('L').resize((N,N)),dtype=float)
        dct=basis@a@basis.T
        block=dct.flatten()[1:];bits=block>np.median(block)
        ph.append(sum(int(v)<<j for j,v in enumerate(bits)))
        a=np.asarray(im.convert('L').resize((9,8)),dtype=float)
        bits=(a[:,1:]>a[:,:-1]).flatten()
        dh.append(sum(int(v)<<j for j,v in enumerate(bits)))
pairs=[]
for j in range(1,len(metadata)):
    for i in range(j):
        pd=(ph[i]^ph[j]).bit_count();dd=(dh[i]^dh[j]).bit_count()
        if pd<=8 or dd<=7: pairs.append(dict(earlier=i+1,later=j+1,phash_distance=pd,dhash_distance=dd))
(TMP/'duplicate_candidates.json').write_text(json.dumps(pairs,indent=2),encoding='utf-8')
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
for batch_first in range(0,len(pairs),5):
    batch=pairs[batch_first:batch_first+5]
    cellw=max(m['width'] for m in metadata)+12
    cellh=max(m['height'] for m in metadata)+30
    canvas=Image.new('RGB',(cellw*2,cellh*len(batch)),(230,230,230));draw=ImageDraw.Draw(canvas)
    for j,pair in enumerate(batch):
        for col,key in enumerate(['earlier','later']):
            m=metadata[pair[key]-1];x=col*cellw;y=j*cellh
            draw.text((x+5,y+3),f"{m['index']} p={pair['phash_distance']} d={pair['dhash_distance']}",font=font,fill='black')
            with Image.open(ROOT.parent/'pool'/m['filename']) as im:canvas.paste(im,(x+5,y+27))
    canvas.save(TMP/f"duplicates_{batch_first//5+1:03d}.png")
eligible=[r for r in rows if r['has_person']=='no' and r['has_text']=='no' and r['is_collage']=='no' and r['quality_ok']=='yes' and not r['duplicate_of'] and 'main dish ambiguous' not in r['bbox_note']]
print(json.dumps(dict(rows=len(rows),eligible=len(eligible),duplicate_candidate_pairs=pairs,category=Counter(r['category'] for r in eligible),framing=Counter(r['main_dish_bbox_pct'] for r in eligible),complexity=Counter(r['complexity'] for r in eligible)),indent=2))

