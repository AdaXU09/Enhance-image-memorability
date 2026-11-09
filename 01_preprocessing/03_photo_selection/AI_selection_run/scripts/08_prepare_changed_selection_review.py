from pathlib import Path
import json,math
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
TMP=ROOT/'outputs'/'_inspection'
PASS1_IDS=[1,8,10,14,20,26,27,40,45,57,62,67,75,81,83,93,98,103,135,145,151,153,154,161,162,163,170,173,179,183,185,203,207,213,215,217,220,221,227,228,234,235,237,245,251,256,257,260,268,286,287,300,305,309,311,313,329,338,341,344,346,350,353,357,361,363,369,400,407,410,426,430,438,440,446,455,462,466,476,494,497,502,506,518,519,522,523,525,538,547,558,561,572,574,579,588,595,598,599,601,604,611,613,623,633,638,659,662,675,679,688,693,702,705,717,727,730,735,741,755,762,768,769,781,786,789,803,818,845,847,853,857,864,867,869,871,873,879,883,890,908,917,922,923,940,950,958,960,968,974]
current=json.loads((TMP/'provisional_selection.json').read_text(encoding='utf-8'))
old=set(PASS1_IDS)
new=[r for r in current if r['index'] not in old]
(TMP/'new_selection_review.json').write_text(json.dumps(new,indent=2),encoding='utf-8')
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
for first in range(0,len(new),10):
    batch=new[first:first+10]
    cellw=max(r['width'] for r in batch)+12
    cellh=max(r['height'] for r in batch)+36
    canvas=Image.new('RGB',(cellw*2,cellh*math.ceil(len(batch)/2)),(230,230,230))
    draw=ImageDraw.Draw(canvas)
    for j,r in enumerate(batch):
        x=j%2*cellw;y=j//2*cellh
        draw.text((x+5,y+3),f"{r['index']} {r['category']} {r['width_frac']}x{r['height_frac']}={r['main_dish_bbox_pct']}",font=font,fill='black')
        with Image.open(ROOT.parent/'pool'/r['filename']) as im:canvas.paste(im,(x+5,y+30))
    canvas.save(TMP/f'changed_review_{first//10+1:02d}.png')
print('New selection count:',len(new))
print('\n'.join(str(r['index'])+' | '+r['category']+' | '+r['note'] for r in new))


