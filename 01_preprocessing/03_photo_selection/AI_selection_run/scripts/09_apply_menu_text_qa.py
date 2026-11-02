"""Full-size inspection identifies the printed menu beside the olives."""
from pathlib import Path
import csv
RUN=Path(__file__).resolve().parents[1]
path=RUN/'outputs'/'visual_annotations.csv'
with path.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
row=next(r for r in rows if r['index']=='173')
row['flags']='t'
row['description']='Olives and vegetables in a brown bowl beside a printed menu and drinks'
with path.open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print('Marked printed menu text at index 173.')
