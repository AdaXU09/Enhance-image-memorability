from pathlib import Path
import csv,json,math
from PIL import Image, ImageDraw, ImageFont
RUN=Path(__file__).resolve().parents[1]
with (RUN/'outputs'/'metadata.csv').open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
review=RUN/'outputs'/'visual_review';review.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
for start in range(0,len(rows),25):
    batch=rows[start:start+25];cw=max(int(r['width']) for r in batch)+12;ch=max(int(r['height']) for r in batch)+40
    sheet=Image.new('RGB',(cw*5,ch*math.ceil(len(batch)/5)),'#eeeeee');d=ImageDraw.Draw(sheet)
    for j,r in enumerate(batch):
        x=(j%5)*cw;y=(j//5)*ch
        with Image.open(r['source_path']) as im: sheet.paste(im.convert('RGB'),(x+6,y+34))
        d.text((x+6,y+3),f"{int(r['index']):03d}  {r['filename'][:12]}",font=font,fill='black')
    sheet.save(review/f"sheet_{start//25+1:02d}.png")
hashes=[]
for r in rows:
    with Image.open(r['source_path']) as im:
        small=im.convert('L').resize((9,8))
        a=list(small.getdata());bits=0
        for y in range(8):
            for x in range(8): bits=(bits<<1)|int(a[y*9+x]>a[y*9+x+1])
        hashes.append(bits)
pairs=[]
for j in range(len(hashes)):
    for i in range(j):
        distance=(hashes[i]^hashes[j]).bit_count()
        if distance<=6: pairs.append(dict(first=i+1,later=j+1,dhash_distance=distance))
(RUN/'outputs'/'near_duplicate_candidates.json').write_text(json.dumps(pairs,indent=2),encoding='utf-8')
print('Created',math.ceil(len(rows)/25),'native-resolution contact sheets.')
print('Largest width and height:',max(int(r['width']) for r in rows),max(int(r['height']) for r in rows))
print('Near duplicate candidates:',pairs)
