"""New map-consistent mobility and radio innovations, not a reconstruction of the private data.
Statistical calibration uses public seeds 1--6. Never imported by a submitted policy."""
from pathlib import Path
import numpy as np,pandas as pd
import sys,math,json,hashlib
out=Path(__file__).resolve().parent
root=out.parent;sys.path.insert(0,str(root/'course/benchmark/src'))
from handover_bench.simulator.scenario import Cell,RadioMeasurement,Packet,MobilitySample,Scenario
from handover_bench.simulator.engine import run_scenario
from handover_bench.metrics.compute import compute_metrics
from handover_bench.metrics.scoring import compute_score
from handover_bench.baselines.a3 import A3Policy
cal=root/'course/benchmark/data/practice'
def calibration():
 cells=[Cell(**r) for r in pd.read_csv(cal/'cells.csv').to_dict('records')]
 mob=pd.read_csv(cal/'mobility.csv');tr=pd.read_csv(cal/'traffic.csv')
 ids={f'practice-seed{i}' for i in range(1,7)}
 mob=mob[mob.scenario_id.isin(ids)];tr=tr[tr.scenario_id.isin(ids)]
 group=['scenario_id','ue_id']
 meta=mob.groupby(group).agg(mode=('mode','first'),n=('time_ms','size'),v=('speed_mps','median'),z=('z_m','median'))
 # Retain scalar session characteristics but never copy a route or packet schedule.
 pairs=tr.groupby(group).deadline_ms.apply(lambda v:tuple(sorted(set(v))));meta['apps']=pairs
 # Packet characteristics differ even at the same deadline for the three app mixes.
 tr=tr.join(pairs.rename('apps'),on=group).sort_values(group+['arrival_time_ms'])
 pools={}
 for (apps,deadline),f in tr.groupby(['apps','deadline_ms']):
  gaps=f.groupby(group).arrival_time_ms.diff().dropna().to_numpy().astype(int).clip(1)
  pools[(apps,deadline)]=(gaps,f.size_bytes.to_numpy())
 return cells,list(meta.itertuples(index=False)),pools
def simulate(seed,model):
 cells,templates,pools=model;rng=np.random.default_rng(seed);mob={};radio={};modes={};packets=[]
 sites=np.array([[c.x_m,c.y_m,c.height_m] for c in cells]);grid=list(range(0,30000,200))
 for u in range(60):
  uid=f'u{u}';record=templates[rng.integers(len(templates))];mode=record.mode
  n=min(150,int(record.n));delta=record.v*.2;first=int(rng.integers(151-n));last=(first+n)*200
  pos=rng.uniform(0,1200,size=2);angle=rng.uniform(0,2*math.pi);shadow=rng.normal(0,4,len(cells));rho=math.exp(-delta/50)
  mob[uid]={};radio[uid]={};modes[uid]=mode
  for i in range(n):
   t=200*(first+i)
   if i:
    angle+=rng.normal(0,{'pedestrian':.15,'cyclist':.07,'bus':.01,'car':.035,'train':0.,'uav':.09}[mode])
    pos+=delta*np.array([math.cos(angle),math.sin(angle)])
    if pos[0]<0 or pos[0]>1200:pos[0]=abs((pos[0]+1200)%2400-1200);angle=math.pi-angle
    if pos[1]<0 or pos[1]>1200:pos[1]=abs((pos[1]+1200)%2400-1200);angle=-angle
    shadow=rho*shadow+rng.normal(0,4*math.sqrt(1-rho*rho),len(cells))
   xyz=np.r_[pos,record.z];rsrp=11.-35*np.log10(np.maximum(8.,np.linalg.norm(sites-xyz,axis=1)))+shadow
   pw=10**(rsrp/10);snr=10*np.log10(pw/(pw.sum()+1.e-10-pw))
   radio[uid][t]=[RadioMeasurement(c.cell_id,float(p),float(s)) for c,p,s in zip(cells,rsrp,snr)]
   mob[uid][t]=MobilitySample(True,*map(float,xyz),float(record.v),float(math.degrees(angle)%360))
  for deadline in record.apps:
   gaps,sizes=pools[(record.apps,deadline)];t=first*200+int(rng.integers(max(1,int(np.mean(gaps)))));i=0
   while t<last:
    packets.append(Packet(f'{uid}-{deadline}-{i}',uid,t,int(rng.choice(sizes)),int(deadline)));t+=int(rng.choice(gaps));i+=1
 return Scenario(f'fresh-{seed}',200,grid,{c.cell_id:c for c in cells},sorted(mob),modes,mob,radio,packets)
