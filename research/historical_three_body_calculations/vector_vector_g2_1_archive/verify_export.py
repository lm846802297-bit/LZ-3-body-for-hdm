import csv
import math
from pathlib import Path

root=Path(__file__).resolve().parent/'g2_output'
required=['ER_keV','rate_zero','rate_pole','pole_over_zero']
for number in range(1,5):
    with (root/f'benchmark_{number}_g2_compare.csv').open(newline='',encoding='ascii') as f:
        reader=csv.DictReader(f)
        assert reader.fieldnames==required,(number,reader.fieldnames)
        rows=list(reader)
    assert len(rows)==83,(number,len(rows))
    last=-1.
    used=0
    for row in rows:
        er=float(row['ER_keV']); zero=float(row['rate_zero']); pole=float(row['rate_pole'])
        assert er>last and zero>=0 and pole>=0,(number,row)
        if zero>0:
            assert math.isclose(float(row['pole_over_zero']),pole/zero,rel_tol=1e-12),(number,row)
            used+=1
        else:
            assert pole==0 and row['pole_over_zero']=='NA',(number,row)
        last=er
    print(f'PASS benchmark {number}: {len(rows)} points, {used} valid ratios')
with (root/'pole_widths.csv').open(newline='',encoding='ascii') as f: widths=list(csv.DictReader(f))
assert len(widths)==4 and abs(float(widths[1]['gamma_keV'])/151.8239115787696-1)<1e-12
print('PASS pole-width table and portable CSV format')
