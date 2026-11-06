"""Recreate the predeclared 1-6 / 7-10 split without overwriting prior copies."""
import argparse, csv, os
from pathlib import Path
root = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--bench', type=Path, default=Path(os.environ.get('BENCH_ROOT', str(root.parent / 'COMP3014J Assignment/student/handover-bench'))))
p.add_argument('--output', type=Path, default=root / 'suites')
a = p.parse_args()
if a.output.exists():
    p.error('output already exists; keep recorded splits or choose a fresh --output')
for name in ['cells', 'mobility', 'radio', 'traffic']:
    with (a.bench / 'data/practice' / (name + '.csv')).open(newline='') as f:
        reader = csv.DictReader(f)
        fields, rows = reader.fieldnames, list(reader)
    for split, nums in [('train', range(1, 7)), ('validation', range(7, 11))]:
        ids = {f'practice-seed{i}' for i in nums}
        out = a.output / split / (name + '.csv')
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(row for row in rows if 'scenario_id' not in fields or row['scenario_id'] in ids)
        print(out.resolve())
