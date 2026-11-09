from pathlib import Path
import csv,json,math,hashlib,random,re
from collections import Counter,defaultdict
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
TMP=ROOT/'outputs'/'_inspection'
CONFIG=json.loads(r'''{"bbox":{"10":[70,50],"20":[60,50],"93":[90,40],"135":[70,40],"142":[80,80],"154":[50,60],"213":[80,70],"228":[50,60],"251":[90,40],"271":[100,90],"309":[90,40],"313":[80,50],"323":[60,80],"341":[90,40],"344":[90,70],"346":[80,80],"364":[100,60],"380":[100,80],"381":[100,90],"407":[80,90],"410":[70,60],"430":[90,100],"440":[70,60],"476":[50,40],"497":[50,90],"518":[60,50],"588":[40,40],"604":[100,40],"611":[90,70],"623":[70,70],"632":[70,60],"679":[90,50],"717":[90,80],"727":[60,40],"768":[100,70],"769":[70,50],"781":[50,60],"786":[60,60],"853":[100,100],"923":[60,50],"940":[40,40],"958":[50,60],"968":[90,80],"969":[80,70],"974":[100,80],"984":[100,70]},"fields":{"81":{"complexity":"complex"},"103":{"category":"noodle"},"178":{"category":"noodle"},"220":{"has_text":"yes","n_dishes":"3plus"},"227":{"note":"Two bread cubes on forks are coated with melted yellow cheese."},"228":{"category":"soup","has_person":"yes"},"234":{"has_text":"yes"},"254":{"complexity":"medium"},"264":{"bbox_note":"main dish ambiguous"},"313":{"bbox_note":"no serving container; on griddle"},"346":{"bbox_note":"cropped at edge"},"353":{"has_text":"yes"},"357":{"note":"A split roast meat sandwich is served with cheese-covered fries."},"361":{"complexity":"medium"},"381":{"bbox_note":"cropped at edge"},"502":{"complexity":"complex"},"518":{"bbox_note":"cropped at edge"},"525":{"has_text":"yes"},"693":{"n_dishes":"3plus"},"717":{"bbox_note":""},"786":{"bbox_note":"main dish ambiguous"},"855":{"bbox_note":"main dish ambiguous","category":"dessert","note":"A food spread includes mochi sweets salads chips and a drink."},"940":{"bbox_note":"no separate plate visible; on counter"},"960":{"complexity":"complex"},"969":{"has_text":"yes"},"974":{"has_person":"yes","complexity":"medium","note":"A pepperoni mushroom onion and artichoke pizza has a possible cropped diner at upper right."}},"groups":[[224,236,765],[153,364,460],[215,865],[616,696],[580,794,951],[81,102],[26,275,609],[140,664],[350,763],[5,805],[68,506],[82,793],[220,405],[376,677],[155,258],[294,984],[754,759],[705,743],[353,649,935],[157,251],[944,961],[62,803],[213,675],[83,519],[227,781]],"selection_avoid":[163,661,632]}''')
rows=json.loads((TMP/'review_rows.json').read_text(encoding='utf-8'))
CATEGORIES=['rice','noodle','burger','pizza','fried','grill','soup','salad','dessert','drink','other']
for r in rows:
    idx=str(r['index'])
    if idx in CONFIG['bbox']:
        r['width_frac'],r['height_frac']=CONFIG['bbox'][idx]
    r.update(CONFIG['fields'].get(idx,{}))
    # Apply one convention consistently across the four visual batches.
    food=r['note'].lower()
    if re.search(r'\bsushi\b|\bnigiri\b|\bmaki\b|\bgunkan\b|\btacos?\b',food):
        r['category']='other'
    if 'enchilada' in food:r['category']='burger'
    r['main_dish_bbox_pct']=max(5,min(100,5*math.floor(r['width_frac']*r['height_frac']/500+.5)))
    if r['index']==961:r['duplicate_of']=rows[943]['filename']
    reasons=[]
    for key in ['has_person','has_text','is_collage']:
        if r[key]=='yes':reasons.append(key)
    if r['quality_ok']=='no':reasons.append('quality_ok=no')
    if r['duplicate_of']:reasons.append('duplicate_of')
    if 'main dish ambiguous' in r['bbox_note']:reasons.append('main dish ambiguous')
    r['excluded_reason']='; '.join(reasons)
    r['food_group']=r['identity'].strip().lower()
for g in CONFIG['groups']:
    for idx in g:rows[idx-1]['food_group']='reviewed_group_'+str(g[0])
eligible=[r for r in rows if not r['excluded_reason']]
assert len(eligible)>=150
def band(r):return min(4,(r['main_dish_bbox_pct']-5)//20)
def waterfill(caps,total):
    result={k:0 for k in sorted(caps)}
    for _ in range(total):
        available=[k for k in result if result[k]<caps[k]]
        assert available
        k=min(available,key=lambda k:(result[k],k))
        result[k]+=1
    return result
# Resolve food-identity collisions using scarce framing first, then complexity.
raw_pool=[r for r in eligible if r['index'] not in CONFIG.get('selection_avoid',[])]
frequencies=Counter(r['main_dish_bbox_pct'] for r in raw_pool)
groups=defaultdict(list)
for r in raw_pool:groups[r['food_group']].append(r)
rank_complexity={'complex':0,'medium':1,'simple':2}
selection_pool=[min(g,key=lambda r:(frequencies[r['main_dish_bbox_pct']],r['main_dish_bbox_pct'],rank_complexity[r['complexity']],hashlib.sha256(r['filename'].encode()).hexdigest())) for g in groups.values()]
band_caps=Counter(band(r) for r in selection_pool)
band_targets=waterfill(band_caps,150)
quotas={}
for b,target in band_targets.items():
    caps=Counter(r['main_dish_bbox_pct'] for r in selection_pool if band(r)==b)
    quotas.update(waterfill(caps,target))
cells={v:[r for r in selection_pool if r['main_dish_bbox_pct']==v] for v in quotas}
# Stable tie order unrelated to sharpness, memorability, composition or attractiveness.
for cell in cells.values():cell.sort(key=lambda r:hashlib.sha256(r['filename'].encode()).hexdigest())
def counts(selection):
    return tuple(Counter(r[k] for r in selection) for k in ['category','complexity','brightness'])
def objective(selection):
    cc,co,br=counts(selection)
    return (sum(cc[k]**2 for k in CATEGORIES),
            sum(co[k]**2 for k in ['simple','medium','complex']),
            sum(br[k]**2 for k in ['dark','medium','bright']))
def valid(selection):
    cc,_,_=counts(selection)
    return max(cc.values(),default=0)<=50 and sum(r['n_dishes']=='3plus' for r in selection)<=45 and len({r['food_group'] for r in selection})==len(selection)
selection=[]
for value in sorted(quotas,key=lambda v:(len(cells[v])/quotas[v],v)):
    for _ in range(quotas[value]):
        used={r['index'] for r in selection}
        options=[r for r in cells[value] if r['index'] not in used and valid(selection+[r])]
        assert options,('Cannot fill cell',value)
        chosen=min(options,key=lambda r:objective(selection+[r]))
        selection.append(chosen)
# Improve lower-priority balances while keeping every exact framing count fixed.
for iteration in range(250):
    before=objective(selection);best=before;best_move=None
    used={r['index'] for r in selection}
    for pos,old in enumerate(selection):
        reduced=selection[:pos]+selection[pos+1:]
        groups={r['food_group'] for r in reduced}
        cats=Counter(r['category'] for r in reduced)
        many=sum(r['n_dishes']=='3plus' for r in reduced)
        for new in cells[old['main_dish_bbox_pct']]:
            if new['index'] in used or new['food_group'] in groups or cats[new['category']]>=50 or many+(new['n_dishes']=='3plus')>45:continue
            cost=objective(reduced+[new])
            if cost<best:best=cost;best_move=(pos,new)
    if best_move is None:break
    selection[best_move[0]]=best_move[1]
selection.sort(key=lambda r:(CATEGORIES.index(r['category']),r['main_dish_bbox_pct'],r['filename']))
assert len(selection)==150 and valid(selection)
assert Counter(r['main_dish_bbox_pct'] for r in selection)==Counter(quotas)
(TMP/'final_screening_rows.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
(TMP/'provisional_selection.json').write_text(json.dumps(selection,indent=2),encoding='utf-8')
(TMP/'selection_plan.json').write_text(json.dumps(dict(band_targets=band_targets,exact_bbox_targets=quotas,objective=objective(selection),iterations=iteration),indent=2),encoding='utf-8')
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
for first in range(0,150,10):
    batch=selection[first:first+10]
    cellw=max(r['width'] for r in batch)+12
    cellh=max(r['height'] for r in batch)+36
    canvas=Image.new('RGB',(cellw*2,cellh*5),(230,230,230));draw=ImageDraw.Draw(canvas)
    for j,r in enumerate(batch):
        x=(j%2)*cellw;y=(j//2)*cellh
        draw.text((x+5,y+3),f"{r['index']} {r['category']} {r['width_frac']}x{r['height_frac']}={r['main_dish_bbox_pct']}",font=font,fill='black')
        with Image.open(ROOT.parent/'pool'/r['filename']) as im:canvas.paste(im,(x+5,y+30))
    canvas.save(TMP/f'selected_review_{first//10+1:02d}.png')
print(json.dumps(dict(eligible=len(eligible),band_targets=band_targets,bbox_targets=quotas,category=Counter(r['category'] for r in selection),complexity=Counter(r['complexity'] for r in selection),brightness=Counter(r['brightness'] for r in selection),n_dishes=Counter(r['n_dishes'] for r in selection),below40=sum(r['main_dish_bbox_pct']<40 for r in selection)),indent=2))
print('\n'.join(str(r['index'])+' | '+r['category']+' | '+str(r['main_dish_bbox_pct'])+' | '+r['note'] for r in selection))

