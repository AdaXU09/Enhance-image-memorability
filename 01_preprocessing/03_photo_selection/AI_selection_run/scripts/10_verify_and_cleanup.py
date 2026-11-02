"""Validate the final deliverables, byte integrity and required constraints; remove review PNGs."""
from pathlib import Path
from collections import Counter
import csv,json,hashlib,shutil
from PIL import Image
RUN=Path(__file__).resolve().parents[1]
OUT=RUN/'outputs'
BASE=['filename','base_id','width','height','short_side','has_person','has_text','is_collage','quality_ok','category','n_dishes','main_dish_bbox_pct','bbox_note','complexity','angle','brightness','duplicate_of','note']
def read(name):
    with (OUT/name).open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
    return fields,rows
fields,screen=read('screening.csv');assert fields==BASE+['excluded_reason']
fields,selected=read('selected.csv');assert fields==BASE+['new_path']
_,metadata=read('metadata.csv');meta={r['filename']:r for r in metadata}
_,annotations=read('visual_annotations.csv');observations={int(r['index']):r for r in annotations}
_,groups=read('candidate_groups.csv');q={r['filename']:r['framing_group'] for r in groups}
audit=json.loads((OUT/'metadata_audit.json').read_text(encoding='utf-8'))
assert len(screen)==997 and len(meta)==997 and len({r['filename'] for r in screen})==997
assert set(meta)=={r['filename'] for r in screen}
assert len(selected)==len({r['filename'] for r in selected})==50
allowed={'has_person':{'yes','no'},'has_text':{'yes','no'},'is_collage':{'yes','no'},'quality_ok':{'yes','no'},
         'category':{'rice','noodle','burger','pizza','fried','grill','soup','salad','dessert','drink','other'},
         'n_dishes':{'1','2','3plus'},'complexity':{'simple','medium','complex'},'angle':{'top','angled','side'},'brightness':{'dark','medium','bright'}}
for r in screen:
    assert r['base_id']==Path(r['filename']).stem
    for field,values in allowed.items():assert r[field] in values,(r['filename'],field)
    a=observations[int(meta[r['filename']]['index'])]
    w,h=int(a['width_frac']),int(a['height_frac'])
    assert w in range(10,101,10) and h in range(10,101,10)
    assert int(r['main_dish_bbox_pct'])==max(5,min(100,5*((w*h+250)//500)))
    excluded=(r['has_person']=='yes' or r['has_text']=='yes' or r['is_collage']=='yes' or r['quality_ok']=='no' or bool(r['duplicate_of']))
    assert bool(r['excluded_reason'])==excluded
    if r['duplicate_of']:assert int(meta[r['duplicate_of']]['index'])<int(meta[r['filename']]['index'])
screen_by_name={r['filename']:r for r in screen}
for r in selected:
    assert not screen_by_name[r['filename']]['excluded_reason']
    assert all(r[k]==screen_by_name[r['filename']][k] for k in BASE)
    assert r['new_path']==f"selected/{r['category']}/{r['filename']}"
    destination=(RUN/r['new_path']).resolve()
    assert destination.is_relative_to((RUN/'selected').resolve())
    assert destination.is_file()
    assert hashlib.sha256(destination.read_bytes()).hexdigest()==meta[r['filename']]['sha256']
    with Image.open(destination) as im:assert im.size==(int(r['width']),int(r['height'])) and im.format=='JPEG'
framing=Counter(q[r['filename']] for r in selected)
assert framing==Counter({'Q1':12,'Q2':13,'Q3':12,'Q4':13})
categories=Counter(r['category'] for r in selected)
assert max(categories.values())<=16 and len(categories)>=4
assert sum(r['n_dishes']=='3plus' for r in selected)<=15
assert len({r['complexity'] for r in selected})==3 and len({r['brightness'] for r in selected})==3
assert len(list((RUN/'selected').rglob('*.jpg')))==50
for m in metadata:
    assert hashlib.sha256(Path(m['source_path']).read_bytes()).hexdigest()==m['sha256']
assert hashlib.sha256((RUN.parent/'pool_final.csv').read_bytes()).hexdigest()==audit['manifest_sha256']
summary=(OUT/'summary.txt').read_text(encoding='utf-8')
assert 'DRAFT:' not in summary
warnings=summary.split('\nWarnings\n')[1].strip().splitlines()
assert len(warnings)==4 and all(r.endswith((': yes',': no')) for r in warnings)
# A second native-resolution visual check has covered every final selection.
reviewed={48,78,91,93,103,129,145,173,212,242,257,270,454,466,691,735,768,13,75,137,162,183,217,281,291,351,494,582,598,601,611,711,806,984,67,98,196,221,527,579,600,731,761,773,799,946,965,70,116,158,163,165,166,294,327,431,510,615,789,833,839,864,921,931,956}
assert {int(meta[r['filename']]['index']) for r in selected}.issubset(reviewed)
report={'status':'passed','screened':len(screen),'excluded_unique':sum(bool(r['excluded_reason']) for r in screen),'eligible':len(groups),'selected':50,
        'framing_groups':dict(framing),'categories':dict(categories),'threeplus':sum(r['n_dishes']=='3plus' for r in selected),
        'exact_csv_columns':True,'source_and_manifest_hashes_unchanged':True,'copied_bytes_identical':True,'native_resolution_and_format_preserved':True,'selected_visual_qa_complete':True}
temporary=(OUT/'visual_review').resolve()
assert temporary.parent==OUT.resolve() and temporary.name=='visual_review' and temporary.is_relative_to(RUN.resolve())
if temporary.exists():
    # OneDrive may set the directory's Windows read-only attribute.
    temporary.chmod(0o700)
    shutil.rmtree(temporary)
report['temporary_review_images_removed']=True
(OUT/'final_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
