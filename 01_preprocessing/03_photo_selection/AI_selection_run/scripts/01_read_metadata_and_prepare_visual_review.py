from pathlib import Path
import csv,json,hashlib,math
from collections import Counter
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT.parent
(ROOT/'outputs'/'_inspection').mkdir(parents=True,exist_ok=True)
rows=list(csv.DictReader((BASE/'pool_final.csv').open(encoding='utf-8-sig',newline='')))
metadata=[]
for idx,row in enumerate(rows,1):
    filename=row['filename']; p=BASE/'pool'/filename
    with Image.open(p) as im:
        width,height=im.size
        image_format=im.format
    metadata.append(dict(index=idx,filename=filename,width=width,height=height,short_side=min(width,height),image_format=image_format,file_size=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
name_counts=Counter(r['filename'].casefold() for r in metadata)
if max(name_counts.values())>1: raise RuntimeError('Duplicate filenames require disambiguation without modifying sources.')
(ROOT/'outputs'/'_inspection'/'metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
try: font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
except OSError: font=ImageFont.load_default()
for first in range(0,len(metadata),12):
    batch=metadata[first:first+12]
    cellw=max(r['width'] for r in batch)+12
    cellh=max(r['height'] for r in batch)+36
    canvas=Image.new('RGB',(cellw*3,cellh*math.ceil(len(batch)/3)),(230,230,230))
    draw=ImageDraw.Draw(canvas)
    for i,r in enumerate(batch):
        x=(i%3)*cellw; y=(i//3)*cellh
        draw.text((x+6,y+3),str(r['index']),fill='black',font=font)
        with Image.open(BASE/'pool'/r['filename']) as im:
            canvas.paste(im, (x+6,y+30))
    canvas.save(ROOT/'outputs'/'_inspection'/f'sheet_{first//12+1:03d}.png')
values=sorted(r['short_side'] for r in metadata)
def q(p):
    f=(len(values)-1)*p; i=int(f); return values[i]+(values[min(i+1,len(values)-1)]-values[i])*(f-i)
print(json.dumps(dict(total=len(metadata),pool_files=len(list((BASE/'pool').iterdir())),duplicate_filenames=[],short_side_quantiles=[q(p) for p in [0,.25,.5,.75,1]],bands=[sum(x<330 for x in values),sum(330<=x<=450 for x in values),sum(450<x<=600 for x in values),sum(x>600 for x in values)],sheets=math.ceil(len(metadata)/12)),indent=2))


