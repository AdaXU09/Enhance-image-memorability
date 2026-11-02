from pathlib import Path
import csv,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
RUN=Path(__file__).resolve().parents[1]
with (RUN/'outputs'/'metadata.csv').open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
h=[]
k=np.arange(32)[:,None];n=np.arange(32)[None,:]
transform=np.cos(np.pi*(n+.5)*k/32)*np.sqrt(2/32)
transform[0,:]=1/np.sqrt(32)
for r in rows:
    with Image.open(r['source_path']) as im: a=np.array(im.convert('L').resize((32,32)),dtype=float)
    vals=(transform@a@transform.T)[:8,:8].ravel(); med=np.median(vals[1:]);bits=0
    for v in vals:bits=(bits<<1)|int(v>med)
    h.append(bits)
pairs=[]
for j in range(len(h)):
    for i in range(j):
        distance=(h[i]^h[j]).bit_count()
        if distance<=14:pairs.append((i+1,j+1,distance))
extra=[(944,961,-1),(336,435,-1),(402,550,-1),(237,433,-1),(599,728,-1)]
seen={(p[0],p[1]) for p in pairs}
pairs += [p for p in extra if (p[0],p[1]) not in seen]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',23)
(RUN/'outputs'/'visual_review').mkdir(exist_ok=True)
for start in range(0,len(pairs),8):
    sheet=Image.new('RGB',(1224,435*min(8,len(pairs)-start)),'#eeeeee');draw=ImageDraw.Draw(sheet)
    for y,(i,j,distance) in enumerate(pairs[start:start+8]):
        for x,idx in enumerate([i,j]):
            r=rows[idx-1]
            draw.text((x*612+6,y*435+2),f'{idx}: {r["filename"][:16]}  pHash {distance}',font=font,fill='black')
            with Image.open(r['source_path']) as im:sheet.paste(im.convert('RGB'),(x*612+6,y*435+32))
    sheet.save(RUN/'outputs'/'visual_review'/f'duplicates_{start//8+1:02d}.png')
(RUN/'outputs'/'duplicate_review_candidates.json').write_text(json.dumps(pairs,indent=2),encoding='utf-8')
print('Perceptual similarity pairs for visual review:',pairs)
