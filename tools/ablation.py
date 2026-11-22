"""Reproduce Table 3 on the six development scenarios using the course simulator."""
import csv
import importlib.util
from pathlib import Path
import sys

kit=Path(__file__).resolve().parents[1]
bench=Path(sys.argv[1]).resolve()
output=Path(sys.argv[2])
sys.path.insert(0,str(bench/"src"))
from handover_bench.baselines.a3 import A3Policy
from handover_bench.simulator.scenario import load_scenario
from handover_bench.simulator.engine import run_scenario
from handover_bench.metrics.compute import compute_metrics
from handover_bench.metrics.scoring import compute_score

def policy(path):
    spec=importlib.util.spec_from_file_location(path.stem,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod.StudentPolicy

scenarios=[load_scenario(bench/"data/practice", f"practice-seed{i}") for i in range(1,7)]
policies=[("A3",A3Policy),("V10 unchanged",policy(kit/"review/variants/v10.py")),
          ("Confidence and sustained-risk boundary",policy(kit/"review/variants/confidence.py")),("Add queue memory (VASH-Q)",policy(kit/"submission/algorithm.py"))]
with output.open("x",newline="") as f:
    writer=csv.writer(f);writer.writerow(["policy","development_index","requests","link_failures","outage_pct","on_time_pct"])
    for name,cls in policies:
        metrics=compute_metrics([run_scenario(s,cls) for s in scenarios])["aggregate"]
        if name=="A3": ref=metrics
        row=[name,f'{compute_score(metrics,ref)["score"]:.2f}',metrics["ho_attempts"],metrics["rlf_events"],f'{100*metrics["outage_fraction"]:.3f}',f'{100*metrics["deadline_delivery_ratio"]:.2f}']
        writer.writerow(row);print(*row,sep=" | ")
