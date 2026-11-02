"""The full-size review identifies a raw preparation shot unsuitable as a dish stimulus."""
from pathlib import Path
import csv,json
RUN=Path(__file__).resolve().parents[1]
path=RUN/'outputs'/'visual_annotations.csv'
with path.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
row=next(r for r in rows if r['index']=='163')
row['flags']='q'
row['description']='Uncooked filled pasta on a preparation tray, unsuitable as a served restaurant dish stimulus'
with path.open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(RUN/'outputs'/'followup_visual_qa.json').write_text(json.dumps({'index':163,'quality_ok':'no','reason':'Raw preparation rather than a served restaurant dish'},indent=2),encoding='utf-8')
print('Marked index 163 unsuitable for this stimulus task.')
