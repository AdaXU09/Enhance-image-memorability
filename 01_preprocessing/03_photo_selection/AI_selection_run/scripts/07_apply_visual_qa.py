"""Corrections from a second, native-resolution inspection of selected images."""
from pathlib import Path
import csv,json
RUN=Path(__file__).resolve().parents[1]
path=RUN/'outputs'/'visual_annotations.csv'
with path.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
changes={
78:dict(width_frac='70',height_frac='60'),
129:dict(n_dishes='3plus'),
165:dict(n_dishes='2'),
212:dict(flags='t'),
270:dict(category='dessert',n_dishes='2',width_frac='90',height_frac='80',description='Ice cream with espresso in a white cup beside a metal coffee jug'),
281:dict(n_dishes='3plus'),
494:dict(width_frac='90',height_frac='70'),
598:dict(category='salad',width_frac='100',height_frac='90',description='A large salad plate beside baked onion soup and a sauce cup'),
691:dict(width_frac='40',height_frac='60',bbox_note='main dish ambiguous; cropped at edge'),
711:dict(flags='t'),
768:dict(width_frac='100',height_frac='70'),
}
log=[]
for r in rows:
    i=int(r['index'])
    if i in changes:
        before={k:r[k] for k in changes[i]};r.update(changes[i])
        log.append(dict(index=i,before=before,after=changes[i]))
with path.open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(RUN/'outputs'/'visual_qa_corrections.json').write_text(json.dumps(log,indent=2),encoding='utf-8')
print('Applied visual QA corrections:',list(changes))
