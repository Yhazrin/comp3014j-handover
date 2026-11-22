"""Produce the report's Table 2 and the three-policy summary from official CLI output."""
import csv, hashlib, json, sys
from pathlib import Path

def export(folder, policy):
    read = lambda name: json.loads((folder / name / "results.json").read_text())
    q, example = read("queue"), read("starter")
    a3, student, starter = q["a3_baseline"], q["student"], example["student"]
    for run in (a3, student, starter):
        if run["status"] != "valid":
            raise ValueError("Official evaluator returned an invalid run: " + str(run["errors"]))
    assert q["scenario_ids"] == example["scenario_ids"]
    scores = {k: v["score"]["score"] for k, v in (("starter",starter),("A3",a3),("VASH-Q",student))}
    compare = {v["scenario_id"]: v for v in a3["metrics"]["per_scenario"]}
    rows = []
    for s in sorted(student["metrics"]["per_scenario"], key=lambda x: int(x["scenario_id"].rsplit("seed",1)[1])):
        b = compare[s["scenario_id"]]
        rows.append((int(s["scenario_id"].rsplit("seed",1)[1]), f'{s["score"]["score"]:.2f}',
                     f'{s["ho_attempts"]-b["ho_attempts"]:+d}',
                     f'{100*(s["outage_fraction"]-b["outage_fraction"]):+.3f}',
                     f'{100*(s["deadline_delivery_ratio"]-b["deadline_delivery_ratio"]):+.3f}'))
    with (folder/"table2.csv").open("w", newline="") as f:
        writer=csv.writer(f); writer.writerow(["seed","index","request_change","outage_change_pp","on_time_change_pp"]); writer.writerows(rows)
    (folder/"table2-rows.tex").write_text("".join(f"{i} & {s} & ${a}$ & ${o}$ & ${t}$ "+chr(92)*2+"\n" for i,s,a,o,t in rows))
    agg=student["metrics"]["aggregate"]
    receipt={"scope":"complete public practice suite", "sha256":hashlib.sha256(policy.read_bytes()).hexdigest(),
             "scenarios":len(rows),"scores":scores,"requests":agg["ho_attempts"],"outage_pct":100*agg["outage_fraction"]}
    (folder/"summary.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(f'Starter {scores["starter"]:.2f} | A3 {scores["A3"]:.2f} | VASH-Q {scores["VASH-Q"]:.2f} | {len(rows)} scenarios | {agg["ho_attempts"]} requests | outage {receipt["outage_pct"]:.4f}%')
    print("Evaluated SHA-256:", receipt["sha256"])

if __name__=="__main__":
    export(Path(sys.argv[1]), Path(sys.argv[2]))
