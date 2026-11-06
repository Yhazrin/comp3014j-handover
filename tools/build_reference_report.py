"""Build the evidence-aligned VASH learning report; six body pages + reproduction appendix + references."""
from pathlib import Path
import json, hashlib, html, math
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Preformatted, Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.graphics.shapes import Drawing, Rect, String, Line
root=Path(__file__).resolve().parents[1]
read=lambda f:json.loads((root/f).read_text())
r=read('experiments/v10_full/results.json');a=r['a3_baseline']['metrics']['aggregate'];m=r['student']['metrics']['aggregate']
ab=read('experiments/ablations_reference.json');rt=read('evidence/runtime_check_full.json')
train_a3=read('experiments/baseline_py311_train/results.json')['a3_baseline']['metrics']['aggregate']
run_record=read('evidence/RELEASE_REPRODUCTION.json')
code=root/'submission/algorithm.py';sha=hashlib.sha256(code.read_bytes()).hexdigest()
assert sha=='63ce1efe2435389fe0b07f07f8f7c633b011415ea2b81bb173e75d899f1a8321'
navy=colors.HexColor('#123047');teal=colors.HexColor('#176e76');grey=colors.HexColor('#52616b');light=colors.HexColor('#edf3f5');red=colors.HexColor('#a34c3a')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='B',fontName='Helvetica',fontSize=9.8,leading=13.7,spaceAfter=8,textColor=navy))
styles.add(ParagraphStyle(name='S',fontName='Helvetica',fontSize=8.2,leading=11.2,spaceAfter=5,textColor=navy))
styles.add(ParagraphStyle(name='C',fontName='Courier',fontSize=8.2,leading=11.4,spaceAfter=9,textColor=navy))
styles.add(ParagraphStyle(name='Kicker',fontName='Helvetica-Bold',fontSize=9,leading=13,spaceAfter=8,textColor=teal))
for n in ['Title','Heading1','Heading2']:
 styles[n].textColor=navy
styles['Title'].fontSize=27;styles['Title'].leading=31;styles['Title'].spaceAfter=13
styles['Heading1'].fontSize=17;styles['Heading1'].leading=22;styles['Heading1'].spaceAfter=11
styles['Heading2'].fontSize=11;styles['Heading2'].leading=15;styles['Heading2'].spaceBefore=7;styles['Heading2'].spaceAfter=6
story=[]
def p(t,s='B'):story.append(Paragraph(t,styles[s]))
def h(t):p(t,'Heading1')
def sub(t):p(t,'Heading2')
def page():story.append(PageBreak())
def codeblock(t):story.append(Preformatted(t,styles['C']))
def table(headers,rows,widths):
 data=[[Paragraph(str(v),styles['S']) for v in headers]]+[[Paragraph(str(v),styles['S']) for v in row] for row in rows]
 t=Table(data,colWidths=[x*mm for x in widths],repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),light),('LINEBELOW',(0,0),(-1,0),1,teal),('LINEBELOW',(0,1),(-1,-1),.35,colors.HexColor('#dae2e6')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
 story.extend([t,Spacer(1,8)])
def callout(t):
 q=Table([[Paragraph(t,styles['B'])]],colWidths=[170*mm]);q.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),light),('BOX',(0,0),(-1,-1),.5,colors.HexColor('#c9d8df')),('LEFTPADDING',(0,0),(-1,-1),11),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),3)]));story.extend([q,Spacer(1,11)])

p('COMP3014J / PERFORMANCE OF COMPUTER SYSTEMS','Kicker')
p('Volatility-Aware<br/>Safety Handover','Title')
p('VASH 1.0 | Public-suite evaluation | Report revision 2','Kicker')
p('COMP3014J group-report learning exemplar | 23 October 2026<br/>Brightspace group: GROUP_ID | Members: MEMBER_1; MEMBER_2; MEMBER_3<br/>Actual names, student numbers and contributions are to be completed by the group.','S')
callout('<b>Abstract.</b> VASH combines current serving-SINR inference with volatility-discounted target selection. Across ten supplied public scenarios, its composite index is <b>126.13</b> versus A3=100 and the always-stay sample=84.93. It reduces handover requests from 345 to 153 and average outage from 1.090% to 0.732%, with no observed failures or ping-pongs. Deadline delivery falls by 1.165 percentage points. The evidence supports a switching-overhead/QoS trade-off, not uniform improvement.')
h('1. Objective and policy design')
p('The supplied starter always stays; A3 uses relative power, hysteresis and time-to-trigger. Neither directly asks whether the current source is still usable or whether a stronger neighbour is volatile. Avoiding all handovers can cause radio-link failure, while unnecessary requests consume service time. The objective is to improve the published composite index without hiding its constituent QoS trade-offs [1-4].')
p('<b>Hypothesis.</b> A causal policy that keeps a usable source and switches to a sufficiently stable target can reduce switching and failure costs. VASH combines current serving-SINR inference, a target-volatility discount, coarse speed regimes and a backlog trigger. This is a new decision rule in <b>StudentPolicy.reset</b> and <b>StudentPolicy.decide</b>, not a change to the simulator or score.')
sub('Recovering a missing current measurement')
p('The interface exposes serving RSRP, neighbour RSRP and neighbour SINR, but not serving SINR. Let P_s and P_j be linear received powers, gamma_j a neighbour SINR, and T the common total received power plus noise. Under the simultaneous common-interference model:')
codeblock('gamma_j = P_j / (T - P_j)\nx_j = T/P_s = 10**((RSRP_j-RSRP_s)/10) * (1+10**(-SINR_j/10))\nSINR_s[dB] = -10 * log10(median_j(x_j) - 1)')
p('This uses permitted current observations, not hidden or future state. The assumption is model-specific. If the inferred total is at most 1, or max(x_j)/min(x_j) is at least 1.12, the code clears risk history and falls back to a conservative power-margin rule. Missing or unusable candidates yield stay. The fallback is protection, not proof of real-network accuracy.','B')

page();h('1. Decision rule and implementation')
sub('State and target risk')
p('Each UE owns its history, exponentially weighted increment variance, serving-cell ID, risk-start time and last-request time. For a cell observed again after delta replay steps, variance is 0.85 times its old value plus 0.15 times (SINR change)<super>2</super>/max(1,delta); a new cell starts at 1 dB<super>2</super>. Histories are replaced with the current observed set, preventing growth with trace length.')
codeblock('target_quality[j] = SINR[j] - k(speed) * sqrt(variance[j])\nsource_boundary  = -8 + margin(speed)')
table(['Observed speed (m/s)','Source margin (dB)','Target floor (dB)','Discount k'],[['speed &lt; 3','-1','-4','0.5'],['3 &lt;= speed &lt; 15','+1','-2','1.5'],['speed &gt;= 15','0','-3','1.0']],[55,40,40,35])
p('When queue_backlog_bytes is at least 100,000, source_boundary rises to at least -6 dB. The radio-risk timer starts below -8 dB, clears above -6 dB and resets on a serving-cell change. A risk state lasting at least 800 ms relaxes the target-quality floor to -6 dB. The timer is a hysteretic policy heuristic, not a copy of the engine N310/T310 state.')
sub('Pseudocode for the normal branch')
codeblock('1. Validate current source/candidates and infer source SINR.\n2. Update instance-local variance and the hysteretic risk timer.\n3. Choose speed parameters; adjust boundary for queue backlog.\n4. Keep targets whose risk-discounted quality reaches the floor.\n5. Select highest quality (lexical cell ID breaks exact ties).\n6. Request handover only if:\n     source SINR < boundary, target SINR - source SINR > 3 dB,\n     and time since last request >= 1000 ms.\n   Otherwise stay; record the time when a request is issued.')
p('Fallback selects the strongest eligible neighbour only when its RSRP advantage exceeds 6 dB, its SINR is at least 0 dB and the same cooldown has elapsed. Cell IDs are opaque keys/tie-breakers, not scenario lookup keys. The policy does not use UE identity, absolute position, routes, future samples, cross-UE mutable state or filesystem/network access.')
sub('Cost and timing')
p('For K current candidates, decision time is O(K log K), dominated by median sorting; persistent memory is O(K). The file is 5,401 bytes and imports only math and statistics. On the public 200 ms replay grid, a request retains source service on that step, incurs execution interruption on the next, and can use the target on the following step. The original engine still decides failures and packet delivery [3].')

page();h('2. Reproducible experimental setup')
p('Benchmark v0.1.0 and its default configuration are unchanged. All official release comparisons use CPython 3.11.15, NumPy 2.4.6 and pandas 3.1.0 on an Apple M5 arm64 Mac, with one-thread numerical-library settings. Early exploration also used CPython 3.12.14; the release was re-evaluated on 3.11. VASH is deterministic. Offline learned-model experiments used random seed 3014 but their models and dependencies are not in the submission.')
table(['Evaluation stage','Selection status','Index'],[['V10, seeds 1-6','Development / repeatedly tuned','131.97'],['V09, seeds 7-10','First blind evaluation after V09 freeze','115.27'],['V10, seeds 7-10','Reused holdout, NOT a fresh blind test','115.13'],['V10, all 10 public scenarios','Includes development data','126.13'],['Original starter, all 10','Same engine and input as V10','84.93']],[64,82,24])
p('<b>Chronology matters.</b> The 1-6 / 7-10 split was fixed before tuning. V09 was frozen before its first holdout run. A later <i>development-only</i> controlled ablation removed the source-variance trigger and improved 131.62 to 131.97, producing V10. V10 then reused the same holdout. Its result is reported, but it cannot restore an untouched validation set. No subsequent parameter search used that holdout.')
sub('Selection method and alternatives')
p('Training-only searches compared safety thresholds, look-ahead, smoothing, target-dependent margins, volatility, tabular value iteration, distilled predictors, speed regimes, backlog and short-horizon outage rules. Selection maximised the published index on seeds 1-6. Static rules reached 130.43; volatility rules 131.20; motion 131.53; backlog 131.62; removing source-variance adaptation reached 131.97. Numerous correlated trials create selection optimism, not independent confirmations. We do not report a misleading confidence interval over those trials.')
sub('Command and traceability')
p('The included reproduce.sh sets PYTHONPATH to the supplied benchmark source and runs the following command with absolute input/output paths. Its output directory must be new. The full original practice CSVs, not a filtered split, are used for the final public score.','B')
codeblock('python -m handover_bench.cli evaluate \\\n  --algorithm submission/algorithm.py \\\n  --suite "$BENCH_ROOT/data/practice" --output "$NEW_OUTPUT"')
p('<b>Frozen candidate SHA-256</b><br/>'+sha,'S')
p('The original sample SHA-256 is ccc4e95cf945e5db4ef3ce2224507938c0fc14961fb568efcdbf0def5fd7c811. The recorded patch reconstructs V10. A separate rollback copy restores the sample hash and reproduces 84.93 (exit 0); V10 gives 126.13 (exit 0) on identical inputs. The source package is preserved, and commands plus literal stdout/stderr are retained in VERIFICATION.txt.','S')

page();h('3. Results against A3')
keys=[('Goodput ratio','goodput_ratio','lower / worse'),('Deadline delivery ratio','deadline_delivery_ratio','lower / worse'),('Outage fraction','outage_fraction','lower / better'),('RLF / UE-minute','rlf_per_ue_min','lower / better'),('HO failures / UE-minute','ho_failures_per_ue_min','lower / better'),('Ping-pong / UE-minute','ping_pong_per_ue_min','lower / better'),('HO attempts / UE-minute','ho_attempts_per_ue_min','lower / better')]
table(['Scored KPI','A3','VASH','Change','Interpretation'],[[n,f'{a[k]:.6f}',f'{m[k]:.6f}',f'{m[k]-a[k]:+.6f}',i] for n,k,i in keys]+[['Composite index','100.00','126.13','+26.13','higher / better']],[54,28,28,30,30])
p('First three KPI rows are fractions; changes are absolute differences. Rates are events per active UE-minute. Average each KPI equally across scenarios before scoring. In table order, weights are (0.30, 0.20, 0.20, 0.15, 0.05, 0.05, 0.05); epsilon is 0.02 for fractions and 0.05 for rates [1,3].','S')
codeblock('S = 100 * exp(sum_i w_i * log(r_i))\n'
          'r_i = (VASH_i+eps_i)/(A3_i+eps_i)  for higher-is-better\n'
          'r_i = (A3_i+eps_i)/(VASH_i+eps_i)  for lower-is-better')
sub('Per-scenario diagnostics (same frozen V10)')
ss=sorted(r['student']['metrics']['per_scenario'],key=lambda x:int(x['scenario_id'].split('seed')[1]));am={s['scenario_id']:s for s in r['a3_baseline']['metrics']['per_scenario']}
table(['Seed / use','Index','HO attempts','Outage','Deadline change'],[[f'{int(s["scenario_id"].split("seed")[1])} / '+('dev' if int(s['scenario_id'].split('seed')[1])<=6 else 'reused'),f'{s["score"]["score"]:.2f}',s['ho_attempts'],f'{s["outage_fraction"]:.5f}',f'{100*(s["deadline_delivery_ratio"]-am[s["scenario_id"]]["deadline_delivery_ratio"]):+.3f} pp'] for s in ss],[43,25,33,30,39])
p('No V10 RLF, HO failure or ping-pong was observed in these ten scenarios. V10 made 153 requests: 149 completed and four remained ongoing at the end. A3 made 345: 325 completed, three failed and 17 remained ongoing; it recorded three RLFs and 32 ping-pongs. A displayed success rate of 1.0 does not mean every request finished. Finite zero-event counts do not establish zero failure probability.','S')

page();h('4. Evidence for the improvement')
p('The following ablations use only development seeds 1-6, exactly one mechanism removed at a time, with all other parameters and simulator conditions fixed. They support local design choices, not independent generalisation claims.')
labels={'frozen':'V10 reference','without_motion_regimes':'Remove motion regimes','without_backlog_trigger':'Remove backlog trigger','without_target_risk_discount':'Remove target risk discount','without_cooldown':'Remove cooldown','without_emergency_relaxation':'Remove emergency relaxation'}
table(['Controlled variant','Index','HO attempts','RLF','Outage'],[['A3 (same development split)','100.00',train_a3['ho_attempts'],train_a3['rlf_events'],f'{train_a3["outage_fraction"]:.5f}']]+[[labels[x['variant']],f'{x["score"]["score"]:.2f}',x['metrics']['aggregate']['ho_attempts'],x['metrics']['aggregate']['rlf_events'],f'{x["metrics"]["aggregate"]["outage_fraction"]:.5f}'] for x in ab],[77,24,27,16,26])
p('Target risk discount and emergency relaxation have the largest observed effects: removing either introduces an RLF and materially lowers the index. Motion and backlog rules give smaller development improvements; these gains may not survive new traces. Removing cooldown changes neither score nor event counts here, so this experiment does <b>not</b> show that cooldown caused zero ping-pongs. It remains a conservative guard.')
sub('Which full-public score components changed?')
d=Drawing(170*mm,157);x0=133;scale=2900
for i,(key,c) in enumerate(r['student']['score']['components'].items()):
 y=139-i*19;v=c['weighted_log_contribution'];col=teal if v>=0 else red
 d.add(String(0,y+2,key.replace('_',' '),fontName='Helvetica',fontSize=8,fillColor=navy))
 d.add(Rect(x0+min(0,v)*scale,y,max(abs(v)*scale,.7),9,fillColor=col,strokeColor=None))
 d.add(String(415,y+1,f'{v:+.5f}',fontName='Helvetica',fontSize=8,fillColor=navy))
d.add(Line(x0,15,x0,151,strokeColor=grey,strokeWidth=.6));story.append(d)
p('Figure 1. Contributions to log(S/100), not additive index-point gains. The sum is 0.23211; exponentiating and multiplying by 100 gives 126.13. Negative bars expose service regressions rather than hiding them behind the composite.','S')
sub('Unsuccessful ideas informed simplification')
p('Linear look-ahead and smoothing did not beat the best static safety result. Tabular learning and distilled predictors did not beat the simpler volatility rule. Source-variance adaptation was removed after its training ablation improved the score; a zero-weight load-ranking term was also removed. No model parameters, route tables or future-informed teacher trajectories are shipped. An offline future-aware diagnostic is not a legal submitted policy or a causal performance result.')

page();h('5. Regressions, limitations and generalisation')
sub('The index improved, but service quality did not improve uniformly')
p(f'Both scored higher-is-better KPIs decreased: goodput by {100*(a["goodput_ratio"]-m["goodput_ratio"]):.4f} percentage points and deadline delivery by {100*(a["deadline_delivery_ratio"]-m["deadline_delivery_ratio"]):.4f} points. Their score factors are 0.999782 and 0.997550. Mean per-scenario p99 packet delay rose from {a["delay_p99_ms"]:.2f} to {m["delay_p99_ms"]:.2f} ms; this is not a pooled-packet p99. Lower switching interruption came with more attached-but-radio-unusable time: radio-outage fraction rose from {a["radio_outage_fraction"]:.6f} to {m["radio_outage_fraction"]:.6f}.')
p('Seed 8 has the lowest relative index (109.12), while seed 7 has the lowest absolute deadline-delivery ratio (0.87269). Seed 4 has the highest relative index (153.31) but the largest deadline regression (-4.835 percentage points). Seed 2 also has slightly worse outage than A3 (+0.000218). These cases show why a high relative index is not equivalent to uniformly better QoS.')
sub('Selection and deployment limits')
p('Only six development and four reused holdout traces are available. Repeated selection risks overfitting. The train/holdout gap is also reference-dependent: A3 has three failures on development but none on holdout, so eliminating failures offers no equivalent gain there. We cannot attribute the entire gap to overfitting or claim the private suite will resemble either subset. The full-public result contains training data.')
p('The SINR inference assumes synchronous, mutually consistent radio measurements. Delayed or differently filtered reports could invalidate it. Increment variance is a heuristic, not a calibrated failure probability; abrupt fading, different speeds/traffic or a shifted report delay may defeat the thresholds. VASH does not optimise fairness or coordinate UEs. None of these simulated results is a real-network guarantee.')
sub('Observed resource use, not a private-sandbox guarantee')
p(f'On this Mac, {rt["decide_calls"]:,} measured decide calls averaged {rt["decide_ms_mean"]:.6f} ms (p99 {rt["decide_ms_p99"]:.6f} ms; max {rt["decide_ms_max"]:.6f} ms). Maximum reset time was {rt["reset_ms_max"]:.6f} ms. Candidate-only replay including CSV loading took {rt["suite_wall_seconds_including_csv_load"]:.3f} s across ten scenarios; the slowest scenario took {max(rt["scenario_wall_seconds_including_csv_load"].values()):.3f} s. This excludes interpreter startup and separate baseline evaluation. Whole-process peak RSS was {rt["process_peak_rss_mib"]:.2f} MiB. Six direct missing/invalid-input checks returned stay; separate UE instances had independent state. These are local observations, not an emulation of the marking sandbox.')
sub('Conclusion')
p('VASH improves the public A3-relative index from 100 to 126.13 by avoiding unnecessary switching and observed failure events. The target-volatility discount and emergency relaxation have the strongest controlled support in development. The accompanying loss in deadline delivery is material and is reported explicitly. A compact causal rule is sufficient to outperform both public references here, but repeated development selection and the reused holdout limit generalisation claims.')
h('6. Sources and development disclosure')
p('The course supplied the starter/interface, simulator, datasets, baselines and scoring definitions [1-4]. The exemplar adds serving-SINR reconstruction with a consistency fallback, instance-local risk ranking and controlled evaluation; it does not claim ownership of the benchmark. OpenAI Codex/ChatGPT assisted derivation, code, offline search, execution, interpretation and drafting. The actual three-person group must provide true identities/contributions, understand the submitted work and retain this tool-use disclosure. Suggested roles in LEARNING_GUIDE.md are not completed-work claims.')

page();h('Appendix A. Public-run verification and reproduction')
callout('<b>Run validity.</b> The frozen file was evaluated successfully on all ten public scenarios: status valid, zero scenario errors, exit status 0 and empty stderr. The packaged reproduce.sh independently reproduced all recorded student metrics. This confirms execution on supplied public data; private assessment is performed by the instructor, not required to reproduce this report.')
sub('Clean-environment reproduction')
p('Use Python 3.11 and the original course package. Keep APlus_Study beside COMP3014J Assignment, or set BENCH_ROOT to your actual handover-bench directory. From inside APlus_Study:')
codeblock('python3.11 -m venv .venv\n'
          '.venv/bin/python -m pip install -r requirements-evaluation.txt\n'
          'export BENCH_ROOT="../COMP3014J Assignment/student/handover-bench"\n'
          './reproduce.sh')
p('The script exports PYTHONPATH, disables bytecode writes into the course source, sets numerical-library thread counts to one, and creates a new output directory. It refuses to overwrite prior results. Evaluation requires NumPy/pandas; VASH itself uses only math/statistics. SciPy and scikit-learn were offline research dependencies, not runtime dependencies.')
sub('Literal excerpt from the successful reproduction')
codeblock('Your score:  126.13\n'
          'A3 baseline: 100.0 (reference)\n'
          'Never hand over: 84.93 (comparison reference)\n'
          'Delta:       +26.13')
p('Source: evidence/RELEASE_REPRODUCTION.json. The record includes the full command, working directory, stdout, empty stderr and exit status 0. Results are in experiments/release_reproduction/results.json. Its student metrics equal experiments/v10_full/results.json; only runtime/output-location metadata need differ. The algorithm SHA-256 on page 3 identifies the evaluated file.','S')
sub('What the public evidence establishes')
table(['Check','Observed result','Boundary'],[['Full public execution','10/10 scenarios; no errors; S=126.13','Not an unseen-data score'],['Allowed implementation','5,401 bytes; math/statistics; per-UE state','No model/data files needed by the policy'],['Targeted runtime checks','Six missing/invalid-input cases return stay','Not exhaustive testing of arbitrary inputs'],['Rollback / preservation','Original sample restored to identical hash; 84.93','Original 33 package files unchanged']],[47,69,54])
sub('Reproducing the split without confusing validation roles')
p('The release stores the already-completed development and holdout results. In a fresh unpacked copy, tools/prepare_splits.py reconstructs seeds 1-6 and 7-10 from the supplied CSVs; it refuses to overwrite an existing output. Point the same official evaluate command at suites/train or suites/validation. Re-running seeds 7-10 reproduces the reused holdout; it does not create a new blind test.')
p('No private dataset is needed for any command above. The report makes empirical claims about the supplied public suite, while the instructor retains responsibility for final private assessment and report grading.','S')

page();h('References and reproducibility index')
refs=[('[1]','COMP3014J Assignment Document 1: Instructions. Supplied 2026 course document. Submission constraints, assessment split and index-to-grade intervals.'),('[2]','COMP3014J Assignment Document 2: Background. Supplied 2026 course document. Handover context and benchmark interpretation.'),('[3]','Provided handover-bench v0.1.0. README.md; docs/assumptions.md; docs/metrics.md; src/handover_bench/config.py; simulator/engine.py; metrics/compute.py; metrics/scoring.py. All used as local primary sources; original hashes retained.'),('[4]','Provided docs/report_template.md and examples/algorithm.py. Report structure and interface/starter comparison. The candidate replaces the always-stay decision mechanism.')]
for k,v in refs:p('<b>'+k+'</b> '+html.escape(v))
sub('Evidence map (paths relative to the study folder)')
table(['Claim','Recorded material'],[['Frozen algorithm and provenance','submission/algorithm.py; evidence/FREEZE_V10.json'],['First blind versus reused holdout','evidence/FREEZE_V09.json; experiments/v09_validation/results.json; experiments/v10_reused_holdout/results.json'],['Full-public score and seven KPIs','experiments/v10_full/results.json and dashboard.html'],['Controlled development variants','experiments/ablations_reference.json; experiments/reference_ablations/'],['Resource measurements and edge cases','evidence/runtime_check_full.json'],['Original, modified, rollback transaction','evidence/VERIFICATION.txt; DIFF.patch; ROLLBACK.sh; pristine_algorithm.py'],['Independent wrapper reproduction','evidence/RELEASE_REPRODUCTION.json; experiments/release_reproduction/results.json'],['One-command reproduction','README.md; reproduce.sh; requirements-evaluation.txt']],[60,110])
sub('Group ownership and archive use')
p('For a three-person group, algorithm reasoning, reproducible experimentation and results/limitations analysis provide complementary responsibilities. Record actual contributions only. Final assessment uses unseen instructor scenarios; this does not prevent public verification, report completion or submission of a well-explained algorithm.')
p('Supplementary research: SCORE_BOUND_NOTE.md retains the fixed-public-suite ceiling study separately. It is separate from the submitted policy and does not predict the private grade.','S')

def footer(c,doc):
 c.setStrokeColor(colors.HexColor('#d5e1e6'));c.line(20*mm,18*mm,190*mm,18*mm)
 c.setFont('Helvetica',7.5);c.setFillColor(grey);c.drawString(20*mm,13*mm,'VASH 1.0 / Report revision 2 / Public-suite experimental study')
 c.drawRightString(190*mm,13*mm,f'{doc.page} / 8')
 if doc.page>1:
  c.setFont('Helvetica-Bold',7.5);c.setFillColor(teal);c.drawString(20*mm,285*mm,'COMP3014J   /   FROZEN REFERENCE V10')
out=root/'submission/report.pdf'
SimpleDocTemplate(str(out),pagesize=(210*mm,297*mm),rightMargin=20*mm,leftMargin=20*mm,topMargin=21*mm,bottomMargin=24*mm,title='VASH: Volatility-Aware Safety Handover',author='AI-assisted learning exemplar; actual group details pending').build(story,onFirstPage=footer,onLaterPages=footer)
from pypdf import PdfReader
reader=PdfReader(out);assert len(reader.pages)==8, len(reader.pages)
text='\n'.join(x.extract_text() for x in reader.pages)
for t in ['126.13','131.97','115.13','Run validity','Sources and development disclosure']:assert t in text,t
import pypdfium2 as pdfium
preview=root/'evidence/report_preview_revision_2';preview.mkdir(exist_ok=True)
pdf=pdfium.PdfDocument(str(out))
for i in range(len(pdf)):pdf[i].render(scale=1.4).to_pil().save(preview/f'page-{i+1}.png')
meta={'path':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bytes':out.stat().st_size,'pages':len(pdf),'body_pages':6,'appendix_pages':1,'references_and_index_pages':1,'algorithm_sha256':sha,'all_pages_rendered':True,'visual_inspection':'pending','report_revision':2,'scope':'Public-data execution, design, empirical analysis, reproducibility; no private data prerequisite'}
(root/'evidence/report_metadata.json').write_text(json.dumps(meta,indent=2));print(json.dumps(meta,indent=2))
