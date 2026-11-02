"""Select with fixed framing/category quotas, then balance visual complexity/brightness.

Run without arguments to draft CSV/QA sheets; --finalize also copies source bytes.
No model scores, perceived attractiveness, or signature-dish preference are used.
"""
from pathlib import Path
from collections import Counter, deque
import csv, json, hashlib, shutil, sys
from PIL import Image, ImageDraw, ImageFont

RUN=Path(__file__).resolve().parents[1]
OUT=RUN/'outputs'
CATS=['rice','noodle','burger','pizza','fried','grill','soup','salad','dessert','drink','other']
GROUPS=['Q1','Q2','Q3','Q4']
BASE_FIELDS=['filename','base_id','width','height','short_side','has_person','has_text','is_collage','quality_ok','category','n_dishes','main_dish_bbox_pct','bbox_note','complexity','angle','brightness','duplicate_of','note']

def read(name):
    with (OUT/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

screen=read('screening.csv')
metadata=read('metadata.csv')
meta={r['filename']:r for r in metadata}
groups=read('candidate_groups.csv')
group_of={r['filename']:r['framing_group'] for r in groups}
candidates=[r for r in screen if not r['excluded_reason']]
quotas=dict(zip(GROUPS,[12,13,12,13]))
available=Counter(r['category'] for r in candidates)
targets={c:0 for c in CATS}
while sum(targets.values())<50:
    for c in CATS:
        if targets[c]<min(16,available[c]):targets[c]+=1
        if sum(targets.values())==50:break

def feasible(rows,cat_left,q_left):
    """Exact max-flow feasibility of remaining category and framing quotas."""
    if sum(cat_left.values())!=sum(q_left.values()):return False
    count=Counter((r['category'],group_of[r['filename']]) for r in rows)
    n=17; sink=16; adj=[[] for _ in range(n)]
    def add(a,b,capacity):
        adj[a].append([b,capacity,len(adj[b])]);adj[b].append([a,0,len(adj[a])-1])
    for i,c in enumerate(CATS,1):
        add(0,i,cat_left[c])
        for j,q in enumerate(GROUPS,12):add(i,j,count[c,q])
    for j,q in enumerate(GROUPS,12):add(j,sink,q_left[q])
    flow=0
    while True:
        parent=[None]*n;parent[0]=(-1,-1);todo=deque([0])
        while todo and parent[sink] is None:
            u=todo.popleft()
            for k,(v,cap,_) in enumerate(adj[u]):
                if cap and parent[v] is None:parent[v]=(u,k);todo.append(v)
        if parent[sink] is None:break
        amount=50;v=sink
        while v: u,k=parent[v];amount=min(amount,adj[u][k][1]);v=u
        v=sink
        while v:
            u,k=parent[v];edge=adj[u][k];edge[1]-=amount;adj[v][edge[2]][1]+=amount;v=u
        flow+=amount
    return flow==sum(cat_left.values())

assert feasible(candidates,targets,quotas)
selected=[];remaining=candidates[:];cat_left=targets.copy();q_left=quotas.copy()
comp=Counter();bright=Counter();multi=0
def resolution(r):
    m=meta[r['filename']]
    return int(m['width'])*int(m['height']),int(m['file_size'])

while len(selected)<50:
    profiles={}
    for r in remaining:
        q=group_of[r['filename']];c=r['category']
        if not cat_left[c] or not q_left[q] or (r['n_dishes']=='3plus' and multi>=15):continue
        profile=(c,q,r['complexity'],r['brightness'],r['n_dishes']=='3plus')
        if profile not in profiles or (resolution(r),-int(meta[r['filename']]['index']))>(resolution(profiles[profile]),-int(meta[profiles[profile]['filename']]['index'])):
            profiles[profile]=r
    ranked=sorted(profiles.values(),key=lambda r:(
        comp[r['complexity']]+bright[r['brightness']],
        max(comp[r['complexity']],bright[r['brightness']]),
        -resolution(r)[0],-resolution(r)[1],int(meta[r['filename']]['index'])))
    chosen=None
    for r in ranked:
        c=r['category'];q=group_of[r['filename']]
        cats_after=cat_left.copy();cats_after[c]-=1
        qs_after=q_left.copy();qs_after[q]-=1
        rest=[x for x in remaining if x['filename']!=r['filename']]
        if multi+(r['n_dishes']=='3plus')==15:rest=[x for x in rest if x['n_dishes']!='3plus']
        if feasible(rest,cats_after,qs_after):chosen=r;break
    assert chosen is not None,'Selection constraints became infeasible'
    selected.append(chosen);remaining.remove(chosen)
    cat_left[chosen['category']]-=1;q_left[group_of[chosen['filename']]]-=1
    comp[chosen['complexity']]+=1;bright[chosen['brightness']]+=1
    multi+=chosen['n_dishes']=='3plus'

def loss(rows):
    cc=Counter(r['complexity'] for r in rows);bb=Counter(r['brightness'] for r in rows)
    return sum(cc[x]**2 for x in ['simple','medium','complex'])+sum(bb[x]**2 for x in ['dark','medium','bright'])

# Single swaps preserve both hard quotas; accept visual balance improvements,
# then larger-resolution/file replacements only when balance is equivalent.
for iteration in range(200):
    current_loss=loss(selected);current_pixels=sum(resolution(r)[0] for r in selected);current_bytes=sum(resolution(r)[1] for r in selected)
    best=None;best_key=(current_loss,-current_pixels,-current_bytes)
    used={r['filename'] for r in selected}
    for i,old in enumerate(selected):
        for new in candidates:
            if new['filename'] in used or new['category']!=old['category'] or group_of[new['filename']]!=group_of[old['filename']]:continue
            if sum(r['n_dishes']=='3plus' for r in selected)-(old['n_dishes']=='3plus')+(new['n_dishes']=='3plus')>15:continue
            trial=selected[:];trial[i]=new
            key=(loss(trial),-(current_pixels-resolution(old)[0]+resolution(new)[0]),-(current_bytes-resolution(old)[1]+resolution(new)[1]))
            if key<best_key:best_key=key;best=(i,new)
    if best is None:break
    selected[best[0]]=best[1]

selected.sort(key=lambda r:(GROUPS.index(group_of[r['filename']]),int(meta[r['filename']]['index'])))
assert len(selected)==len({r['filename'] for r in selected})==50
assert Counter(group_of[r['filename']] for r in selected)==Counter(quotas)
assert Counter(r['category'] for r in selected)==Counter(targets)
assert sum(r['n_dishes']=='3plus' for r in selected)<=15
with (OUT/'selected.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=BASE_FIELDS+['new_path']);writer.writeheader()
    for r in selected:
        row={k:r[k] for k in BASE_FIELDS};row['new_path']=f"selected/{r['category']}/{r['filename']}";writer.writerow(row)

qa=OUT/'visual_review';qa.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
for start in range(0,50,10):
    batch=selected[start:start+10]
    sheet=Image.new('RGB',(1224,5*452),'#eeeeee');draw=ImageDraw.Draw(sheet)
    for k,r in enumerate(batch):
        x=k%2*612;y=k//2*452;m=meta[r['filename']]
        draw.text((x+5,y+2),f"{m['index']} {group_of[r['filename']]} {r['category']} dishes={r['n_dishes']} bbox={r['main_dish_bbox_pct']}",font=font,fill='black')
        draw.text((x+5,y+23),f"{r['complexity']} {r['brightness']} {r['bbox_note']}",font=font,fill='black')
        with Image.open(m['source_path']) as im:sheet.paste(im.convert('RGB'),(x+5,y+48))
    sheet.save(qa/f'selected_{start//10+1:02d}.png')

def distribution(values):
    values=sorted(map(int,values));n=len(values)
    def percentile(q):
        pos=(n-1)*q;lo=int(pos);hi=min(lo+1,n-1)
        return values[lo]+(values[hi]-values[lo])*(pos-lo)
    return {'min':values[0],'q25':percentile(.25),'median':percentile(.5),'q75':percentile(.75),'max':values[-1]}
def bands(values):
    values=list(map(int,values))
    return {'under 330':sum(v<330 for v in values),'330 to 450':sum(330<=v<=450 for v in values),'450 to 600':sum(450<v<=600 for v in values),'over 600':sum(v>600 for v in values)}
def format_counts(counter,order=None):
    return ', '.join(f'{k}: {counter[k]}' for k in (order or sorted(counter)))

audit=json.loads((OUT/'metadata_audit.json').read_text(encoding='utf-8'))
ranges={q:[int(r['main_dish_bbox_pct']) for r in groups if r['framing_group']==q] for q in GROUPS}
cuts=[max(ranges[q]) for q in GROUPS[:3]]
lines=[
'Photo selection summary',
'Input: pool_final.csv; only the listed filenames were screened.',
f"Total image files found in pool: {audit['pool_files']}",
f"Listed images screened: {len(screen)}; unlisted files ignored: {len(audit['ignored_files'])}",
'Ignored filenames: '+', '.join(audit['ignored_files']),
'Duplicate filenames: none; no renaming required.',
'',
'Resolution and file metadata',
'Listed-image shorter side (px): '+format_counts(distribution(r['short_side'] for r in metadata)),
'Listed-image shorter-side bands: '+format_counts(bands(r['short_side'] for r in metadata)),
'Band boundaries: 330-450 inclusive; above 450 through 600 inclusive.',
'Native width (px): '+format_counts(distribution(r['width'] for r in metadata)),
'Native height (px): '+format_counts(distribution(r['height'] for r in metadata)),
'File size (bytes): '+format_counts(distribution(r['file_size'] for r in metadata)),
'Individual native dimensions, byte sizes and SHA-256 hashes are in metadata.csv.',
'',
'Visual screening and exclusion',
'Every listed image was visually inspected. Width_frac and height_frac were estimated separately in increments of 10%, including the main container; arithmetic then rounded to the nearest 5% and clamped to 5-100%. The two estimates remain in visual_annotations.csv.',
'Visible people/body parts, text/marks, collage and unusable quality were screened independently. These are visual judgments; tiny or faint marks may be uncertain.',
'For suitability, non-food scenes, raw ingredient/preparation shots and meals hidden in packaging were treated as quality_ok=no; this interpretation of a usable restaurant-dish stimulus is stated in their notes.',
]
for field,bad in [('has_person','yes'),('has_text','yes'),('is_collage','yes'),('quality_ok','no')]:lines.append(f'Excluded by {field}={bad}: {sum(r[field]==bad for r in screen)}')
lines.extend([
f"Excluded by near-identical duplicate: {sum(bool(r['duplicate_of']) for r in screen)}",
f"Excluded unique union (rules may overlap): {sum(bool(r['excluded_reason']) for r in screen)}",
f'Eligible candidates: {len(candidates)}',
'No exclusions were based on resolution.',
'Exact decoded-pixel duplicates: none. Perceptual-similarity candidates plus visually suspected repeats were compared; decisions are in duplicate_review.csv. Later index 961 repeats the dish/plate at index 944.',
'Excluded scenes with no visible food container use n_dishes=1 solely as a required-schema placeholder; their notes explicitly state that no food container is visible.',
'Categories use the fixed list; sushi is classified as rice and unlisted food types as other. The largest container defines the main dish.',
'',
'Framing groups',
'Eligible candidates were sorted by main_dish_bbox_pct, then original manifest row order. Four rank groups differ in size by at most one. Tied percentages are split by manifest order, so ranges can overlap.',
'Cut points (maximum value in Q1, Q2 and Q3): '+', '.join(f'{v}%' for v in cuts),
])
for q in GROUPS:
    gg=[r for r in groups if r['framing_group']==q]
    lines.append(f"{q}: ranks {gg[0]['rank']}-{gg[-1]['rank']}, candidates {len(gg)}, bbox range {min(ranges[q])}-{max(ranges[q])}%, selected {quotas[q]}")
lines.extend([
'These are rank-based quartiles, not four equally wide percentage intervals. Q4 contains only 100% estimates because of the large tie at that value.',
'',
'Selection method and selected counts',
'Framing quotas are fixed at 12/13/12/13. Category quotas are distributed as evenly as candidate availability permits across the fixed list (maximum 5 in this selection). Remaining allocation feasibility is checked with exact category-to-framing maximum flow.',
'Within those quotas, a deterministic greedy choice and quota-preserving swaps balance complexity and brightness; this is a heuristic rather than a global optimum guarantee. Multi-dish (3plus) count is capped at 15 throughout. Only equally balanced choices use native pixel count, then byte size, as tie-breaks. No attractiveness, memorability score, or signature-dish judgment was used.',
'Selected total: 50',
'Framing groups: '+format_counts(Counter(group_of[r['filename']] for r in selected),GROUPS),
])
for field,order in [('category',CATS),('n_dishes',['1','2','3plus']),('complexity',['simple','medium','complex']),('angle',['top','angled','side']),('brightness',['dark','medium','bright'])]:
    lines.append(field+': '+format_counts(Counter(r[field] for r in selected),order))
lines.extend([
'',
'Selected-image resolution',
'Shorter side (px): '+format_counts(distribution(r['short_side'] for r in selected)),
'Shorter-side bands: '+format_counts(bands(r['short_side'] for r in selected)),
'Native width (px): '+format_counts(distribution(r['width'] for r in selected)),
'Native height (px): '+format_counts(distribution(r['height'] for r in selected)),
'File size (bytes): '+format_counts(distribution(meta[r['filename']]['file_size'] for r in selected)),
'',
'Output and integrity',
'screening.csv: 997 rows; exact requested columns plus excluded_reason.',
'selected.csv: 50 rows; exact base columns plus new_path.',
'Paths in selected.csv are relative to AI_selection_run/.',
'Numbered scripts record first-execution order; after visual QA corrections, scripts 05 and 06 were rerun to rebuild outputs. Final observations are saved in visual_annotations.csv; scripts 03 and the image-review sheets support the manual review rather than an automated vision classifier.',
])
if '--finalize' in sys.argv:
    manifest=RUN.parent/'pool_final.csv'
    assert hashlib.sha256(manifest.read_bytes()).hexdigest()==audit['manifest_sha256']
    for m in metadata:
        assert hashlib.sha256(Path(m['source_path']).read_bytes()).hexdigest()==m['sha256']
    desired={RUN/'selected'/r['category']/r['filename'] for r in selected}
    selected_dir=(RUN/'selected').resolve()
    assert selected_dir.parent==RUN.resolve()
    for existing in selected_dir.rglob('*'):
        if existing.is_file() and existing not in desired:existing.unlink()
    for r in selected:
        source=Path(meta[r['filename']]['source_path']);target=RUN/'selected'/r['category']/r['filename']
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
        assert hashlib.sha256(target.read_bytes()).hexdigest()==meta[r['filename']]['sha256']
    assert len(list(selected_dir.rglob('*.jpg')))==50
    lines.append('50 originals copied byte-for-byte with unchanged filenames, format and resolution into selected/<category>/.')
    lines.append('SHA-256 verified all 997 source files and pool_final.csv unchanged, and all 50 copies identical to their sources.')
else:lines.append('DRAFT: selected originals have not been copied; final visual QA is pending.')
lines.extend([
'',
'Warnings',
'Any framing group contributes fewer than 8 of the 50: '+('yes' if min(quotas.values())<8 else 'no'),
'The highest cut point is above 80: '+('yes' if cuts[2]>80 else 'no'),
'The lowest cut point is above 40: '+('yes' if cuts[0]>40 else 'no'),
'Fewer than 4 categories are represented: '+('yes' if len({r['category'] for r in selected})<4 else 'no'),
])
(OUT/'summary.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('\n'.join(lines[lines.index('Selected total: 50'):lines.index('Selected-image resolution')]))
print('Selected manifest indices:',[int(meta[r['filename']]['index']) for r in selected])
print('QA sheets:',[str(qa/f'selected_{i:02d}.png') for i in range(1,6)])
