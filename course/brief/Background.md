# Document 2 · Background

[原始 DOCX](Assignment_comp3014j_Document_2_Background.docx)。以下为便于 GitHub 阅读和搜索的正文提取；图、公式排版和页码以 DOCX 为准。

Adaptive Handover in Mobile Communication System: Design & Evaluation

COMP3014J- Performance of Computer Systems

2026

Part 2: Handover Background and Scoring Reference

## 1. Introduction:

Mobile networks maintain ongoing phone calls, video streams, and gaming sessions by continuously transferring users to optimal base stations (cell phone towers) as they move. In this assignment, you will develop a rule-based or learning-based decision algorithm for this cell-switching (we call this handover) that outperforms the current industry standard.

## 2. Why this Assignment:

On average, a mobile device is within a few hundred meters of several base stations simultaneously. However, it maintains contact with only one base station at a time, known as the serving cell. As a user moves through a city, whether walking, driving, or operating a drone, the network must continually determine which base station to use, making this decision repeatedly without interrupting the ongoing call. This process is referred to as a handover. If handovers are not optimal, then suboptimal handover decisions can disrupt service.

The baseline method employs the threshold-and-timer measurement event, standardized by 3GPP as Event A3. Although the A3 algorithm is functional and widely used, this approach is limited because it considers only a single user at a time. Also, it does not account for the load on the target cell and treats noise identically to actual motion. For this assignment, you need develop a custom decision rule, evaluate its performance on the provided synthetic multi-user scenarios, and quantify its improvement over the industry A3 baseline.

A network simulator, channel model, and scheduler are provided and remain consistent across all evaluated algorithms, including the baseline. The sole responsibility is to determine, based on the device's current observations, whether it should remain connected to the current cell or request a handover.

## 3. Cellular Network in Five Minutes:

A mobile network consists of multiple cells, each with a fixed base station (called a gNB in 5G NR) that transmits a radio signal over a roughly circular area. Each device (known as a UE, or "user equipment") constantly monitors the signal strength from each surrounding cell and stays connected to the cell currently providing the best service.

*[图见原始 DOCX]*

Source: LinkedIn Post.

Two measurements matter throughout this assignment:

RSRP (dBm)

The reference signal received power (RSRP) measures how loud a particular cell appears to this device. It normally decreases as the distance increases (see in the above gif image). The typical usable range for RSRP in mobile communication system is about from −70 dBm (which is excellent and indicates proximity) to −110 dBm (which is barely audible).

SINR (dB)

Signal-to-Interference-plus-Noise Ratio (SINR) measures how clean that signal is once you account for interference from other cells and background noise. This, not RSRP alone, determines the actual data rate a device can achieve.

We are going to consider two types of cells as well, the following are those:

Serving cell

The one cell a device is currently attached to and receiving/sending data through.

Candidate / neighbour cell

Any other cell the device can currently measure well enough to be considered as a handover target.

Since RSRP decreases with distance and is affected by buildings, weather, and other traffic (a phenomenon known as shadow fading), a device which was nearest to cell A five seconds ago might now be nearer to cell B, or perhaps be able to receive signals from cell B. The role of the network is to detect this kind of shift and move the device before the link deteriorates to the point of the connection being lost. In the practical trace recordings, shadowing changes smoothly as the device moves (its correlation falls to about 37% after 50 m of travel), so that a real crossover is maintained rather than flickering from one sample to the next.

## 4. The handover procedure

You cannot carry out a handover in an instant and it doesn't consist of a single message. Rather, it is a brief protocol involving the UE device, the current serving cell, and the target cell. The steps listed below are a simplified representation of what the simulator in this assignment implements; for the exact 3GPP clauses see README.md in the provided package.

*[图见原始 DOCX]*

Figure 1. A3 handover implemented in the provided simulator.

Figure 1 illustrates the handover procedure implemented by the simulator (simulator/engine.py). For scoring purposes, two phases are relevant. The preparation phase (steps 3–4) ensures that the device remains connected to its previous cell network, which does not constitute an interruption. The execution phase (steps 5–6) is the only period during which the device is disconnected from both cell networks and is therefore unable to receive data.

The practice traces use 200 ms steps. The configured preparation time (50 ms) and execution time (40 ms) each occupy one full 200 ms step; service is interrupted during execution.

Three types of failures may occur during this procedure, each of which can be caused or prevented by the algorithm:

Handover failure: This occurs if radio link failure occurs during preparation, if the source link’s T310 timer is running when preparation ends, or if the target is missing or has SINR below −8 dB when execution ends. In such cases, the device searches for any available cell, resulting in a radio link failure (RLF).

Ping-pong: This phenomenon occurs when the device performs a handover and then immediately reverts to the previous cell, or hands over again within a short period. Because each handover incurs an interruption cost, frequent switching between two cells of similar signal strength provides no benefit and results in wasted capacity.

Staying too long: Prolonged connection to a deteriorating cell: If a device remains connected to a cell with declining signal quality, it ceases to receive data once the signal-to-interference-plus-noise ratio (SINR) drops below the out-of-sync threshold (−8 dB), resulting in an outage. If the connection does not recover within approximately 3 seconds, the device registers a radio link failure and requires about 1 second to re-establish a connection with the available cell with the highest SINR above −6 dB; if none is available, recovery continues. Avoiding handovers does not prevent failures; it merely substitutes handovers with radio link failures.

## 5. How the network decides today: Event A3

In real networks, step 2 (the measurement report) is triggered by a rule from the 5G NR standard known as Event A3. A neighbouring cell becomes reportable when it exceeds the serving cell by a fixed margin and maintains this advantage for a specified minimum duration. Formally (3GPP TS 38.331, entering condition):

M_n + Ofn + Ocn − Hys  >  M_p + Ofp + Ocp + Off

| Term | Meaning |
| --- | --- |
| M_n | Neighbour cell's measured RSRP (the supplied A3 baseline uses RSRP) |
| M_p | Serving ("primary") cell's measured RSRP |
| Ofn, Ofp | Per-measurement-object offsets (usually 0; a per-frequency tuning knob) |
| Ocn, Ocp | Cell-individual offsets (CIO) is per-neighbour tuning, e.g. to discourage handover to an already-congested cell |
| Hys | Hysteresis is a dead-zone so noise alone can't flip the decision back and forth |
| Off | The A3 offset is how much stronger the neighbour must be before it even counts |

Fixed for this assignment:

The parameters used in the baseline are published and do not need to be reverse-engineered, as stated in README.md. They are set once and then made final for the entire practice and assessment suite, just as a real operator's radio parameters would be:

| Parameter | Symbol | Value | Config field |
| --- | --- | --- | --- |
| Hysteresis | Hys | 1.0 dB | a3_hysteresis_db |
| A3 offset | Off | 1.0 dB | a3_offset_db |
| Cell-individual offset (CIO) | Ocn = Ocp | 0.0 dB | a3_cell_offset_db |
| Measurement-object offset | Ofn = Ofp | 0.0 dB | a3_object_offset_db |
| Time-to-trigger | TTT | 320 ms | a3_ttt_ms |

With these values, the entering condition (see Figure 2) becomes M_n − 1 > M_p + 1, which starts the 320 ms timer. The neighbour must be strictly more than 2 dB stronger to enter; the hysteresis state described below then controls whether the timer continues. Here, CIO is set to 0 dB for every cell. The baseline setup cannot prefer or avoid any specific neighbour, which is what Section 7 describes as load-blindness. Your policy is not limited by these five numbers, just by the same stay or request_handover actions.

In plain terms, the neighbour must be both clearly and consistently better. "Clearly" means there is a margin of Hys + Off decibels. Once the entering condition is met, Time-to-Trigger (TTT) starts. With the fixed offsets above, the leaving condition is M_n < M_p + Off − Hys; it resets the timer. Between the entering and leaving thresholds, the previous state is retained and an active timer continues. The baseline uses elapsed simulation time: on the 200 ms practice grid, the first decision at or beyond 320 ms is 400 ms after the entering sample.

*[图见原始 DOCX]*

Figure 2. illustrative example of a handover instance.

Figure 2 presents an illustrative example rather than a live trace. As the device moves, the neighbour cell's Reference Signal Received Power (RSRP) surpasses that of the serving cell. The entering condition is satisfied at approximately 1048 ms; however, the report is transmitted only after the margin persists for the entire 320 ms Time-to-Trigger (TTT) window, which is indicated by the shaded band.

The times in Figure 2 illustrate the nominal 320 ms timer; the supplied practice traces can trigger only on the 200 ms decision grid described above.

The margin-plus-timer design adopts a deliberately conservative approach, prioritizing a relatively late handover to minimize false triggers. Alternative algorithms may implement this trade-off differently, such as by responding more rapidly, considering cell load, or disregarding neighbouring cells that are already occupied, provided they adhere to the same execution model described in Section 1 of Document 1.

## 6. The network you'll optimise on

The ten fixed and independently seeded scenarios provided in the data/practice/ directory utilize a single 9-cell layout. Figure 3 presents the actual layout, rather than a schematic, and is drawn directly from cells.csv. The coverage boundaries are depicted in an idealized form, specifically as a Voronoi division, which represents the boundary line that would occur if two cells were equally strong under uniform transmit power and in the absence of shadowing. In practice, the real association boundaries are more uncertain because Reference Signal Received Power (RSRP) also accounts for shadow fading and, for aerial UAV routes, altitude. Nevertheless, the diagram accurately reflects the overall shape of the network.

*[图见原始 DOCX]*

Figure 3. The nine cells shared by all ten practice scenarios, 1200 m × 1200 m. Each of the ten scenarios re-samples mobility, traffic and radio conditions on this same network (see README.md).

## 6.1. Scenario statistics (10 scenarios, seeds 1–10)

The simulation setup consists of nine cells, each with a bandwidth of 20 MHz. Each scenario includes between 53 and 69 user equipments (UEs), with a total of 607 UE tracks across all scenarios. Six mobility modes are evaluated. Scenarios are generated over a nominal 30-second window, with measurements recorded at 200 ms intervals while devices are present; the latest timestamp in the suite is 29.8 seconds. Across the entire suite, 138,303 packet arrivals are offered, not necessarily all delivered.

Each cell has no fixed limit on the number of devices, and there is no admission limit based on cell load; handover requests must still name a measurable candidate other than the serving cell. Instead, its capacity is its 20 MHz of bandwidth, which is shared equally every 200 ms among the devices attached to it that have data waiting. Each device then transmits at a rate given by the Shannon formula at its own SINR: rate = (20 MHz / n) × log2(1 + SINR), where n is the number of devices sharing the cell and SINR in the formula is a linear ratio (10^(SINR_dB/10)). For example, at an SINR of 10 dB a device alone in a cell receives about 69 Mb/s, while five devices sharing the same cell receive about 14 Mb/s each. A device attached to a cell whose SINR is below −8 dB receives no data. The congestion indicator in the observation is the number of devices attached to each cell in the previous step divided by 50, capped at 1.0; the value 50 only scales the indicator and is not a capacity limit.

| Mode | UE tracks | Notes |
| --- | --- | --- |
| Car | 202 | 8–20 m/s, moderate turning |
| Pedestrian | 160 | 1–2 m/s, wanders freely |
| UAV | 79 | 5–15 m/s, 30–120 m altitude (only aerial mode) |
| Bus | 63 | 5–15 m/s, constrained route |
| Train | 61 | 20–30 m/s, near-straight line |
| Cyclist | 42 | 3–6 m/s |

Traffic is bursty and independent of mobility. Each device runs a single application- video (approximately 4 Mb/s while active), web browsing, or voice- and alternates between active and idle periods. Devices arrive in groups, similar to passengers disembarking from a train. The scenarios are not tailored to favour any specific strategy; the same ten practice scenarios are used to evaluate both your policy and the A3 baseline locally. Assessment uses held-out scenarios, with the same scenarios used for your policy and A3 in each comparison.

## 7. Why this is a hard problem

This is a straightforward reason why the industry has resorted to using a simple per-device threshold rule rather than calculating the best possible network-wide assignment: because it isn't feasible to do so in real time.

For example, in a scenario with 60 active devices, each able to connect to any of 9 cells, determining the serving cell for every device simultaneously is necessary to assess cell load.

960 ≈ 1.8 × 1057

At each moment, there are many possible assignments. The network makes these decisions roughly every 200 milliseconds and continues this process as long as the scenario runs. It can only use current measurements, not future information.

*[图见原始 DOCX]*

Figure 4. Every device that can hear cell A could attach to it. But if A is already near capacity, the network-optimal choice routes some of them to B or C instead. A3 never sees this. It compares one device's own RSRP readings, one device at a time.

Users compete for shared cell bandwidth, and a handover affects both current service and future choices. This motivates heuristic optimization with incomplete information. The implemented scheduler shares bandwidth and does not enforce the hard admission-capacity constraints of a generalized-assignment model. No NP-hardness proof exists for this exact benchmark. A formal complexity claim requires a specified decision problem and a reduction.

## 8. How You are Scored?

| KPI | Better | Definition |
| --- | --- | --- |
| Goodput ratio | more | Bytes delivered divided by bytes offered, over all packets that arrived for present devices. Late packets still count; packets still queued at the end count only for the bytes already sent. |
| Deadline delivery ratio | more | This metric is calculated by dividing the total bytes of packets delivered in full by their deadline, which is the arrival time plus 50 to 300 ms depending on the application, by the number of bytes offered. |
| Outage fraction | less | The proportion of time a device has no service is measured when it is not connected to any cell, such as during handover execution, RLF recovery, or initial search, or when it is connected but the serving SINR is below −8 dB and no data is delivered. |
| RLF per UE-minute | less | Radio link failures per UE-minute happen when out-of-sync timers expire because of a fading link or a failed handover. Each time this occurs, re-establishment takes about 1 second. |
| HO failures per UE-minute | less | A failure is counted if RLF occurs during preparation, T310 is running when preparation ends, or the target is missing or has SINR below −8 dB when execution ends. A handover still in progress at the end is reported separately, not counted as failed. |
| Ping-pong per UE-minute | less | A handover whose execution starts less than 1 second after the previous handover’s execution started. Returning to the original cell is not required. |
| HO attempts per UE-minute | less | The simulator accepts handover requests as long as the device is idle, the target can be measured, and it is not the serving cell, regardless of the outcome. |

Some KPIs are the higher the better, some are the vice-versa. The calculation happens in the following way:

For each policy, each KPI is calculated per scenario and then averaged equally across the suite. The score uses those aggregate KPIs; it is not the average of the per-scenario scores. A3 always scores 100 on the same suite, and lower performance on any scored KPI reduces its factor.

More is better (goodput, deadline delivery):    r = (yours + ε) / (A3 + ε)Less is better (outage, RLF, HO failures, ping-pong, HO attempts):    r = (A3 + ε) / (yours + ε)ε = 0.02 for goodput, deadline delivery and outage (fractions from 0 to 1)ε = 0.05 for the four rates per UE-minutescore = 100 × r_goodput^0.30 × r_deadline^0.20 × r_outage^0.20            × r_RLF^0.15 × r_HO_failures^0.05 × r_ping_pong^0.05            × r_HO_attempts^0.05

ε keeps a KPI of exactly zero, such as zero ping-pongs, from dividing by zero; it is not a cap. Each term rw is that metric's score factor: above 1 it raises your score, below 1 it lowers it. Your dashboard lists all seven factors, and multiplying them by 100 gives your score. The code is compute_score in src/handover_bench/metrics/scoring.py.

The score is not mathematically unbounded on a fixed suite. To obtain an optimistic upper bound, substitute goodput = 1, deadline delivery = 1 and all five lower-is-better KPIs = 0 into the same formula. For the supplied practice suite this gives approximately 159.96. These ideal KPI values may not be achievable together, so this is a bound, not a demonstrated attainable score. A different suite has a different bound. Do not divide your score by this bound to calculate an assignment mark.

For grading, use the fixed intervals in Document 1. An index improvement of x% means S = 100 + x: for example, S = 135 is a 35% increase in this weighted composite index, not a 35% increase in throughput. Your performance component contributes 90% of the assignment grade and your group’s single shared report contributes 10%. Practice results support development; the assessment score comes from the fixed private suite.

Example of A3 versus No-handover score calculation:

“Never hand over” always returns {"action": "stay"}. The simulator still performs initial attachment and reconnects after radio link failure, so a device can change cell during recovery. This is a comparison reference, not a lower bound on scores or an additional grading baseline. The values below refer to the supplied practice suite with the default configuration; displayed values are rounded.

| KPI | Better | Weight w | ε | A3 | Never hand over | Ratio r | Factor r^w |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Goodput ratio | more | 0.30 | 0.02 | 0.9978 | 0.9747 | 0.9774 | 0.9932 |
| Deadline delivery ratio | more | 0.20 | 0.02 | 0.9357 | 0.8623 | 0.9233 | 0.9842 |
| Outage fraction | less | 0.20 | 0.02 | 0.0109 | 0.0428 | 0.4920 | 0.8678 |
| RLF per UE-minute | less | 0.15 | 0.05 | 0.0262 | 0.5302 | 0.1314 | 0.7375 |
| HO failures per UE-minute | less | 0.05 | 0.05 | 0.0262 | 0.0000 | 1.5248 | 1.0213 |
| Ping-pong per UE-minute | less | 0.05 | 0.05 | 0.2321 | 0.0000 | 5.6424 | 1.0904 |
| HO attempts per UE-minute | less | 0.05 | 0.05 | 2.5826 | 0.0000 | 52.6526 | 1.2192 |
| Score = 100 × product of the factors | 84.93 |  |  |  |  |  |  |

***Note:

A weight sets how strongly a ratio counts, but a factor also depends on how far the ratio is from 1. Goodput has the largest weight (30%), yet goodput ratios stay close to 1 because almost all traffic is eventually delivered: a ratio of 0.9774 gives 0.97740.30 = 0.9932, less than 1% off the score. RLF has half that weight (15%), but a ratio of 0.1314 gives 0.13140.15 = 0.7375, a 26% cut. To see what drives your score, read the score factors, not only the weights.

9. Developing your own policy from the always-stay starter

Purpose and decision rule. The supplied examples/algorithm.py is an always-stay starter that demonstrates the required interface. Its reset() method does nothing and its decide() method always returns {"action": "stay"}. It never requests a handover. The simulator still performs initial attachment and reconnection after radio link failure, so a device can change cell during recovery. Always staying is different from always requesting handover.

Measured result. On the supplied ten practice scenarios with the default configuration, the starter scores 84.93 against A3’s 100. Its composite index is therefore 15.07% below A3: (84.93 − 100)% = −15.07%. This is below the performance pass threshold of 100. Practice results are feedback; assessment uses the private suite. The score is not a percentage assignment mark. It produces the same decisions and results as the dashboard’s never hand over reference. Section 8 shows the worked KPI comparison and score calculation.

Why it performs worse than A3. Avoiding handover requests eliminates handover attempts, handover failures and ping-pongs, but it can leave a moving device on a deteriorating link until radio link failure triggers recovery. On the practice suite, worse goodput, deadline delivery, outage and RLF metrics outweigh those handover-related gains. A3 can transfer a device before the serving link fails. Minimising the number of handovers alone does not solve this assignment.

Develop your own policy. Use the observation fields documented in README.md to decide when staying is harmful and which candidate could improve service. You can consider radio measurements, congestion, backlog and per-device history. Form a testable hypothesis about the trade-off your rule addresses. Explain when your policy requests handover and when it stays; do not assume that more or fewer handovers always improve the score.

Evaluate your changes. Compare your policy with A3 and the always-stay starter on identical scenarios. Inspect all seven KPI gains and penalties and the weakest scenarios, not only the aggregate score. Change one idea at a time and use an ablation to identify its effect. Validate on additional seeds that you did not use for tuning. In your group report, explain your design, measured improvements and regressions, computational cost, and the commands needed to reproduce the results.

Submitting the supplied sample solution (examples/algorithm.py) as your solution will receive a fail grade for the assignment, regardless of its performance score or report mark. Changing only names, comments or formatting does not count as developing your own algorithm. You may use the sample as a starting point, but must develop, explain and evaluate your own changes.
