"""Compile the visually assigned observations and reviewed duplicate decisions."""
from pathlib import Path
import csv, json
from collections import Counter

RUN = Path(__file__).resolve().parents[1]
OUT = RUN / 'outputs'
BASE_FIELDS = ['filename','base_id','width','height','short_side','has_person','has_text','is_collage','quality_ok','category','n_dishes','main_dish_bbox_pct','bbox_note','complexity','angle','brightness','duplicate_of','note']

def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def write_csv(path, fields, rows):
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

def build():
    metadata = read_csv(OUT / 'metadata.csv')
    observations = read_csv(OUT / 'visual_annotations.csv')
    assert len(metadata) == len(observations) == 997
    assert {int(r['index']) for r in observations} == set(range(1,998))
    by_index = {int(r['index']): r for r in observations}
    # A full-size comparison clarified the food in the foil tray at index 402.
    by_index[402]['category'] = 'fried'
    by_index[402]['description'] = 'Cheese-covered fries in a foil tray'
    write_csv(OUT / 'visual_annotations.csv', list(observations[0]), observations)
    pairs = json.loads((OUT / 'duplicate_review_candidates.json').read_text(encoding='utf-8'))
    decisions = []
    for earlier, later, distance in pairs:
        decisions.append({'earlier_index':earlier,'later_index':later,
                          'earlier_filename':metadata[earlier-1]['filename'],
                          'later_filename':metadata[later-1]['filename'],
                          'phash_distance':distance,
                          'near_identical':'yes' if (earlier,later)==(944,961) else 'no',
                          'reason':'Same rectangular mushroom pizza and plate, alternate angle/crop' if (earlier,later)==(944,961) else 'Visually distinct food, container or arrangement'})
    write_csv(OUT / 'duplicate_review.csv', list(decisions[0]), decisions)
    duplicate_of = {961:metadata[943]['filename']}
    rows = []
    for m in metadata:
        index = int(m['index']); a = by_index[index]; flags = a['flags']
        bbox = max(5,min(100,5*((int(a['width_frac'])*int(a['height_frac'])+250)//500)))
        note = a['description'].rstrip('. ')
        if a['bbox_note']=='no food container visible':
            note += '; no food container is visible and n_dishes=1 is a required-schema placeholder'
        note += '.'
        row = dict(filename=m['filename'], base_id=Path(m['filename']).stem,
                   width=m['width'],height=m['height'],short_side=m['short_side'],
                   has_person='yes' if 'p' in flags else 'no',
                   has_text='yes' if 't' in flags else 'no',
                   is_collage='yes' if 'c' in flags else 'no',
                   quality_ok='no' if 'q' in flags else 'yes',
                   category=a['category'],n_dishes=a['n_dishes'],main_dish_bbox_pct=bbox,
                   bbox_note=a['bbox_note'],complexity=a['complexity'],angle=a['angle'],
                   brightness=a['brightness'],duplicate_of=duplicate_of.get(index,''),note=note)
        reasons = [f'{key}={bad}' for key,bad in [('has_person','yes'),('has_text','yes'),('is_collage','yes'),('quality_ok','no')] if row[key]==bad]
        if row['duplicate_of']: reasons.append('duplicate_of='+row['duplicate_of'])
        row['excluded_reason'] = '; '.join(reasons)
        rows.append(row)
    write_csv(OUT / 'screening.csv', BASE_FIELDS+['excluded_reason'],rows)
    survivors = sorted((r for r in rows if not r['excluded_reason']),key=lambda r:(int(r['main_dish_bbox_pct']),next(int(m['index']) for m in metadata if m['filename']==r['filename'])))
    n = len(survivors); groups=[]; start=0
    for group in range(4):
        size = n//4 + (group < n%4)
        for rank,r in enumerate(survivors[start:start+size],start+1):
            groups.append(dict(filename=r['filename'],rank=rank,framing_group=f'Q{group+1}',main_dish_bbox_pct=r['main_dish_bbox_pct']))
        start += size
    write_csv(OUT / 'candidate_groups.csv',['filename','rank','framing_group','main_dish_bbox_pct'],groups)
    print('Screened:',len(rows),'Excluded:',len(rows)-n,'Eligible:',n)
    print('Eligible categories:',dict(Counter(r['category'] for r in survivors)))
    for g in ['Q1','Q2','Q3','Q4']:
        names = {x['filename'] for x in groups if x['framing_group']==g}
        pool=[r for r in survivors if r['filename'] in names]
        print(g,len(pool),'bbox',min(int(r['main_dish_bbox_pct']) for r in pool),max(int(r['main_dish_bbox_pct']) for r in pool),'categories',dict(Counter(r['category'] for r in pool)))
    for field in ['complexity','brightness','n_dishes']:
        print(field,dict(Counter(r[field] for r in survivors)))

if __name__ == '__main__':
    build()
