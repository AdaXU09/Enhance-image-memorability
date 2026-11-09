from pathlib import Path
import csv,json,hashlib,shutil,math
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
TMP=ROOT/'outputs'/'_inspection'
rows=json.loads((TMP/'final_screening_rows.json').read_text(encoding='utf-8'))
chosen=json.loads((TMP/'provisional_selection.json').read_text(encoding='utf-8'))
AUDIT=json.loads(r'''{"bbox":{"28":[50,70],"48":[50,80],"416":[70,70],"480":[90,50],"649":[70,90],"653":[100,100],"704":[100,80],"834":[90,90],"835":[70,90],"909":[80,70],"992":[100,70]},"fields":{"28":{"bbox_note":"no serving container; on grill"},"48":{"complexity":"medium"},"386":{"has_text":"yes"},"480":{"complexity":"complex"},"834":{"n_dishes":"2"},"909":{"n_dishes":"3plus"}},"groups":[[213,534,675],[48,361]]}''')
REVIEWED=set([1,8,10,14,20,26,27,28,40,45,48,57,62,67,75,77,81,83,93,98,103,135,142,145,151,153,154,160,161,162,163,170,173,179,183,185,203,207,213,215,217,220,221,227,228,234,235,237,245,251,256,257,260,268,281,286,287,300,305,309,311,313,322,329,336,338,341,344,346,350,353,357,358,361,363,369,371,386,400,407,410,416,421,426,430,433,438,440,446,455,462,466,476,480,494,497,502,506,518,519,522,523,525,534,538,540,547,548,558,561,569,572,574,579,588,589,595,598,599,601,604,611,613,619,623,633,638,649,653,659,662,675,679,688,693,702,704,705,715,717,727,730,735,741,750,755,762,768,769,781,786,788,789,803,818,827,834,835,845,847,852,853,857,864,867,869,871,873,879,883,890,898,908,909,917,922,923,940,950,958,960,968,974,989,992,995])
AVOID={163,661,632}
for r in rows:
    idx=str(r['index'])
    if idx in AUDIT['bbox']:r['width_frac'],r['height_frac']=AUDIT['bbox'][idx]
    r.update(AUDIT['fields'].get(idx,{}))
    r['main_dish_bbox_pct']=max(5,min(100,5*math.floor(r['width_frac']*r['height_frac']/500+.5)))
    reasons=[]
    for key in ['has_person','has_text','is_collage']:
        if r[key]=='yes':reasons.append(key)
    if r['quality_ok']=='no':reasons.append('quality_ok=no')
    if r['duplicate_of']:reasons.append('duplicate_of')
    if 'main dish ambiguous' in r['bbox_note']:reasons.append('main dish ambiguous')
    r['excluded_reason']='; '.join(reasons)
for group in AUDIT['groups']:
    for idx in group:rows[idx-1]['food_group']='final_review_group_'+str(group[0])
fresh={r['index']:r for r in rows}
original=[fresh[r['index']] for r in chosen]
chosen=[];removed=[];seen=set()
for r in original:
    if r['excluded_reason'] or r['food_group'] in seen:
        removed.append(r)
    else:
        chosen.append(r);seen.add(r['food_group'])
# Keep the hard multi-dish cap after corrected dish counts.
while sum(r['n_dishes']=='3plus' for r in chosen)>45:
    options=[r for r in chosen if r['n_dishes']=='3plus']
    def repairability(r):
        return sum(q['index'] in REVIEWED and not q['excluded_reason'] and q['n_dishes']!='3plus' and q['main_dish_bbox_pct']==r['main_dish_bbox_pct'] for q in rows)
    old=max(options,key=lambda r:(repairability(r),r['main_dish_bbox_pct'],r['filename']))
    chosen.remove(old);removed.append(old)
def balance_cost(items):
    return tuple(sum(n*n for n in Counter(r[key] for r in items).values()) for key in ['category','complexity','brightness'])
for old in removed:
    used={r['index'] for r in chosen};groups={r['food_group'] for r in chosen}
    counts=Counter(r['category'] for r in chosen)
    many=sum(r['n_dishes']=='3plus' for r in chosen)
    options=[r for r in rows if r['index'] in REVIEWED and r['index'] not in used and r['index'] not in AVOID and not r['excluded_reason'] and r['food_group'] not in groups and counts[r['category']]<50 and many+(r['n_dishes']=='3plus')<=45]
    assert options,('No reviewed repair for',old['index'])
    new=min(options,key=lambda r:(abs(r['main_dish_bbox_pct']-old['main_dish_bbox_pct']),balance_cost(chosen+[r]),hashlib.sha256(r['filename'].encode()).hexdigest()))
    chosen.append(new)
assert len(chosen)==150 and all(r['index'] in REVIEWED for r in chosen)
chosen.sort(key=lambda r:(['rice','noodle','burger','pizza','fried','grill','soup','salad','dessert','drink','other'].index(r['category']),r['main_dish_bbox_pct'],r['filename']))
(TMP/'final_screening_rows.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
(TMP/'final_selection.json').write_text(json.dumps(chosen,indent=2),encoding='utf-8')

metadata=json.loads((TMP/'metadata.json').read_text(encoding='utf-8'))
plan=json.loads((TMP/'selection_plan.json').read_text(encoding='utf-8'))
COLUMNS=['filename','base_id','width','height','short_side','has_person','has_text','is_collage','quality_ok','category','n_dishes','main_dish_bbox_pct','bbox_note','complexity','angle','brightness','duplicate_of','note']
CATEGORIES=['rice','noodle','burger','pizza','fried','grill','soup','salad','dessert','drink','other']
assert len(rows)==997 and len({r['filename'] for r in rows})==997
assert len(chosen)==150 and len({r['filename'] for r in chosen})==150
assert len({r['food_group'] for r in chosen})==150
for r in rows:
    assert r['category'] in CATEGORIES
    assert r['n_dishes'] in ['1','2','3plus']
    assert r['complexity'] in ['simple','medium','complex']
    assert r['angle'] in ['top','side','angled']
    assert r['brightness'] in ['dark','medium','bright']
    assert 5<=r['main_dish_bbox_pct']<=100 and r['main_dish_bbox_pct']%5==0
    for k in ['has_person','has_text','is_collage','quality_ok']:assert r[k] in ['yes','no']
    assert r['width']==metadata[r['index']-1]['width']
    assert r['height']==metadata[r['index']-1]['height']
    assert r['short_side']==min(r['width'],r['height'])
    assert bool(r['excluded_reason'])==(r['has_person']=='yes' or r['has_text']=='yes' or r['is_collage']=='yes' or r['quality_ok']=='no' or bool(r['duplicate_of']) or 'main dish ambiguous' in r['bbox_note'])
assert all(not r['excluded_reason'] for r in chosen)
cc=Counter(r['category'] for r in chosen)
assert max(cc.values())<=50 and len(cc)>=4
assert sum(r['n_dishes']=='3plus' for r in chosen)<=45
for m in metadata:
    p=ROOT.parent/'pool'/m['filename']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==m['sha256'],('Source changed',p)
for r in chosen:
    source=ROOT.parent/'pool'/r['filename']
    destination=ROOT/'selected'/r['category']/r['filename']
    destination.parent.mkdir(parents=True,exist_ok=True)
    if destination.exists():
        assert hashlib.sha256(destination.read_bytes()).hexdigest()==hashlib.sha256(source.read_bytes()).hexdigest(),('Unexpected destination',destination)
    else:shutil.copy2(source,destination)
    assert destination.read_bytes()==source.read_bytes()
    r['new_path']=destination.relative_to(ROOT).as_posix()
actual_copies={p.relative_to(ROOT).as_posix() for p in (ROOT/'selected').rglob('*') if p.is_file()}
assert actual_copies=={r['new_path'] for r in chosen}
def write_csv(path,data,cols):
    with path.open('w',newline='',encoding='utf-8-sig') as f:
        out=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore');out.writeheader();out.writerows(data)
write_csv(ROOT/'outputs'/'screening.csv',rows,COLUMNS+['excluded_reason'])
write_csv(ROOT/'outputs'/'selected.csv',chosen,COLUMNS+['new_path'])
# Reopen exports; check exact schema, row count, and image key joins.
for name,cols,expected in [('screening.csv',COLUMNS+['excluded_reason'],997),('selected.csv',COLUMNS+['new_path'],150)]:
    with (ROOT/'outputs'/name).open(encoding='utf-8-sig',newline='') as f:
        rd=csv.DictReader(f);assert rd.fieldnames==cols;exported=list(rd);assert len(exported)==expected
def quantiles(values):
    v=sorted(values)
    def q(p):
        f=(len(v)-1)*p;i=int(f)
        return v[i]+(v[min(i+1,len(v)-1)]-v[i])*(f-i)
    return [q(p) for p in [0,.25,.5,.75,1]]
def qline(values):
    return ', '.join(f'{label}={value:g}' for label,value in zip(['minimum','25th percentile','median','75th percentile','maximum'],quantiles(values)))
def bands(values):
    return [sum(x<330 for x in values),sum(330<=x<=450 for x in values),sum(450<x<=600 for x in values),sum(x>600 for x in values)]
eligible=[r for r in rows if not r['excluded_reason']]
excluded=[r for r in rows if r['excluded_reason']]
reason_counts=Counter(reason for r in excluded for reason in r['excluded_reason'].split('; '))
below40=sum(r['main_dish_bbox_pct']<40 for r in chosen)
lines=[
'Photo selection summary',
'',
'Completed all five steps for the photographs listed in pool_final.csv.',
f'Listed rows and files found: {len(rows)}. Pool folder files: 1000; the three unlisted files were ignored.',
'Duplicate filenames: none. No filenames were renamed.',
'',
'1 Resolution and file metadata',
'All dimensions and byte sizes were read directly from each image file with code.',
'All listed images shorter side (pixels): '+qline([r['short_side'] for r in rows])+'.',
'Shorter-side bands (<330, 330-450 inclusive, >450-600 inclusive, >600): '+str(bands([r['short_side'] for r in rows]))+'.',
'Per-file dimensions, byte sizes, actual encoding, and SHA-256 checksums are recorded in file_metadata.csv.',
'Resolution was not used to exclude or rank any image.',
'',
'2 Visual screening',
'Every one of the 997 listed photographs was visually inspected. Selected images and all initially loose framing estimates received a further visual audit.',
'The numbered annotation scripts retain the separately estimated width_frac and height_frac values and food-identity labels. Scripts 07 and 09 retain audit corrections and conservative food-identity groups.',
'Bounding rectangles include the visible main food and its own serving container; separate dishes, drinks, utensils, and tables are excluded. Width and height were rounded separately to tens, multiplied, then rounded half up to a multiple of five with a minimum of five.',
'Category conventions were applied consistently: sushi and nigiri and open tacos are other; rolled burritos and enchiladas are burger; macaroni and other pasta are noodle; spinach curry served as a stew is soup.',
'For unusable nonfood/empty-container images, the required n_dishes field has no zero option. Such records retain 1 as a schema placeholder and are excluded by quality and/or main-dish ambiguity; this does not affect the selection.',
'',
'3 Exclusions',
f'Total excluded (unique photographs): {len(excluded)}. Remaining candidates: {len(eligible)}.',
'Counts below overlap when a photograph violates more than one rule:']
for reason in ['has_person','has_text','is_collage','quality_ok=no','duplicate_of','main dish ambiguous']:
    lines.append(f'  {reason}: {reason_counts[reason]}')
lines.extend([
'No exclusion was based on resolution or a desire to keep attractive photographs.',
'',
'4 Selection method and achieved spread',
'The selection contains exactly 150 photographs. Framing was balanced first using water-filled counts across five bands (5-20,25-40,45-60,65-80,85-100), then across available five-point values within each band. Scarce framing values were retained as far as the available distinct candidates permitted.',
'Within the planned framing counts, selection balanced categories, enforced conservative food-identity groups, and improved complexity and brightness balance using same-framing swaps. A final visual audit corrected individual frames and replaced rejected photographs only with images that had already received a second visual check. The achieved distributions below include these corrections. Filename hashes supplied deterministic tie-breaking; automatic memorability, sharpness, saturation, and attractiveness scores were not used.',
'Raw, unprepared ingredient photographs were not selected as restaurant dishes; they retain their screening eligibility unless an explicit exclusion rule applies. Descriptions use the food itself. Conservative collision groups prevent selecting two effectively indistinguishable main dishes. Other dishes served on the same main plate can distinguish meals; background objects cannot.',
'Final framing band counts: '+', '.join(f'{label}: {sum(lo<=r["main_dish_bbox_pct"]<=hi for r in chosen)}' for label,lo,hi in [('5-20',5,20),('25-40',25,40),('45-60',45,60),('65-80',65,80),('85-100',85,100)])+'.',
'Remaining candidates main_dish_bbox_pct: '+qline([r['main_dish_bbox_pct'] for r in eligible])+'.',
'Selected main_dish_bbox_pct: '+qline([r['main_dish_bbox_pct'] for r in chosen])+'.',
'Exact selected framing counts: '+', '.join(f'{k}={v}' for k,v in sorted(Counter(r['main_dish_bbox_pct'] for r in chosen).items()))+'.',
f'Selected photographs below 40: {below40}/150 ({below40/150:.1%}). Remaining candidates below 40: {sum(r["main_dish_bbox_pct"]<40 for r in eligible)}.',
f'Largest category count: {max(cc.values())}/150 (limit 50). Categories represented: {len(cc)}.',
f'Selected n_dishes=3plus: {sum(r["n_dishes"]=="3plus" for r in chosen)}/150 (limit 45).',
'',
'Selected category counts:'])
for cat in CATEGORIES:lines.append(f'  {cat}: {cc[cat]}')
for key,levels in [('angle',['top','side','angled']),('brightness',['dark','medium','bright']),('complexity',['simple','medium','complex']),('n_dishes',['1','2','3plus'])]:
    count=Counter(r[key] for r in chosen)
    lines.extend(['',f'Selected {key} counts:']+[f'  {level}: {count[level]}' for level in levels])
lines.extend([
'',
'5 Selected resolution and copy verification',
'Selected shorter side (pixels): '+qline([r['short_side'] for r in chosen])+'.',
'Selected shorter-side bands (<330,330-450 inclusive,>450-600 inclusive,>600): '+str(bands([r['short_side'] for r in chosen]))+'.',
'Selected width (pixels): '+qline([r['width'] for r in chosen])+'.',
'Selected height (pixels): '+qline([r['height'] for r in chosen])+'.',
'All 150 copies were verified byte-for-byte against their original files. All 997 source image checksums match the metadata pass. No image was retouched, cropped, resized, compressed, or re-encoded. Temporary inspection canvases did not alter source images or selected copies.',
'Two source files have PNG encoding despite .jpg names (listed in file_metadata.csv); original bytes and filenames are preserved.',
'CSV schemas, 997 screening rows, 150 selected rows, filenames, categories, framing increments, exclusion consistency, category caps, multi-dish cap, food-identity uniqueness, relative paths, and exactly 150 copied files passed validation.',
'Quantiles use linear interpolation at (n-1)*p.',
'',
'Warnings',
'Fewer than 4 categories are represented: '+('yes' if len(cc)<4 else 'no'),
'Fewer than a quarter of the selected photographs have main_dish_bbox_pct below 40: '+('yes' if below40<37.5 else 'no')
])
(ROOT/'outputs'/'summary.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps(dict(screening_rows=len(rows),selected_rows=len(chosen),remaining=len(eligible),excluded=len(excluded),copied=len(actual_copies),selected_framing_quantiles=quantiles([r['main_dish_bbox_pct'] for r in chosen]),below40=below40,category=dict(cc),validation='passed'),indent=2))

