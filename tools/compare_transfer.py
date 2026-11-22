"""Compare a frozen candidate and VASH-Q on identical freshly generated mobility and traffic."""
import argparse
import hashlib
import json
import importlib.util
from pathlib import Path

from synthetic_mobility import (A3Policy, calibration, simulate, run_scenario, compute_metrics, compute_score)

ROOT = Path(__file__).resolve().parents[1]
def policy(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.StudentPolicy

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--start', type=int, required=True)
    p.add_argument('--count', type=int, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.count < 1 or a.output.exists():
        p.error('choose a positive count and a new output path')
    q = ROOT/'submission/algorithm.py'
    paths = {'VASH-Q':q, 'candidate':a.candidate}
    policies = {'A3':A3Policy, 'VASH-Q':policy(q,'group25_q'), 'candidate':policy(a.candidate,'group25_candidate')}
    model = calibration()
    runs = {k:[] for k in policies}
    ids = list(range(a.start,a.start+a.count))
    for i in ids:
        sc = simulate(i,model)
        for k, cls in policies.items():
            runs[k].append(run_scenario(sc,cls))
    ms = {k:compute_metrics(x) for k,x in runs.items()}
    scores = {k:compute_score(x['aggregate'],ms['A3']['aggregate'])['score'] for k,x in ms.items()}
    rows = []
    for i, seed in enumerate(ids):
        ref=ms['A3']['per_scenario'][i]
        rows.append({'seed':seed, **{k:compute_score(m['per_scenario'][i],ref)['score'] for k,m in ms.items()}})
    record={'scope':'Synthetic, calibrated on public seeds 1–6; not a private grade. Each suite uses its own A3.','seeds':ids,
            'sha256':{k:hashlib.sha256(path.read_bytes()).hexdigest() for k,path in paths.items()},
            'scores':scores,'candidate_minus_Q':round(scores['candidate']-scores['VASH-Q'],2),
            'aggregate':{k:m['aggregate'] for k,m in ms.items()},'per_seed':rows}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(record,indent=2)+'\n')
    print('A3 %.2f | VASH-Q %.2f | candidate %.2f | delta %+.2f' % (scores['A3'],scores['VASH-Q'],scores['candidate'],record['candidate_minus_Q']))
if __name__=='__main__':main()
