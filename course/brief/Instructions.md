# Document 1 · Instructions

[原始 DOCX](Assignment_comp3014j_Document_1_Instructions.docx)。以下为便于 GitHub 阅读和搜索的正文提取；图、公式排版和页码以 DOCX 为准。

Adaptive Handover in Mobile Communication System: Design & Evaluation

COMP3014J- Performance of Computer Systems

2026

Part 1: Assignment Instructions

## 1. Your task: algorithm.py

To surpass the 3GPP A3 baseline, submit both algorithm.py and report.pdf. It is not necessary to build a simulator or use a GPU for this assignment. You have to utilize the provided packaged handover-bench v0.1.0.

Your task is to develop and evaluate a practical decision rule. Explain its computational cost and the trade-offs it makes. You do not need to prove that your solution is globally optimal. The supplied always-stay starter demonstrates the policy interface and scores 84.93 against A3’s 100 on the practice suite. Develop your own handover decision rule. See Document 2, Section 9 for its results and guidance.

Submit algorithm.py and report.pdf. Your Python file defines a class with two methods. The simulator creates one instance per device:

class StudentPolicy:    def reset(self, config: dict) -> None:        ...  # called once when this device first appears in a scenario    def decide(self, observation: dict) -> dict:        ...  # called each step this device is idle (not mid-handover)        return {"action": "stay"}        # or:        return {"action": "request_handover", "target_cell_id": cell_id}

The simulator verifies, prepares, and executes user requests, detects radio link failures, manages bandwidth allocation among devices within a cell, delivers packets, and calculates relevant metrics. These processes are implemented identically for both user-defined policies and the A3 baseline. Direct access to the network state, data from other devices, or future observations is not permitted. Information provided is limited to what a real device could plausibly obtain at the current timestamp, subject to a configurable reporting delay. For further details, refer to README.md.

Users are provided with additional information beyond that available to the A3 baseline. This includes RSRP for the serving cell, and RSRP and SINR for candidate cells, the current handover phase, a summary of recent outcomes, and, in this release, a congestion indicator from the previous simulation step for the serving and candidate cells as well as the backlog of undelivered packets. The utilization of this information is at your discretion. You may implement a more sensitive threshold, apply a learned model, or select any method that produces a valid action. Machine learning is not required, but feel free to implement if you want to. Any machine learning model must be trained offline, on your own computer, and then written into algorithm.py itself, because the grader accepts only that single file (at most 1 MiB) and installs only the Python standard library, numpy and pandas. Suitable models are therefore small ones whose parameters can be stored as numbers in the file and evaluated with numpy, for example linear or logistic regression, a small decision tree, or a small neural network (multi-layer perceptron) with a few layers. You may train the model with any tool, such as scikit-learn or PyTorch, including reinforcement learning with the provided simulator, but the submitted file must not import those libraries or load separate model files, and each call to decide() should take no more than a few milliseconds. You may also use learning only to find good parameter values for a rule-based policy. For details, see README.md. The supplied examples/algorithm.py is a minimal always-stay starter.

## 2. What you're given

You are given the handover-bench package as a zip file. It needs Python 3.10 or later; Python 3.11 is recommended because it is used for grading. Its only runtime dependencies are numpy and pandas. Unzip the package and open a terminal in student/handover-bench (the folder containing README.md and pyproject.toml). First, create and activate a virtual environment:

macOS / Linux:python3 -m venv .venvsource .venv/bin/activateWindows (Command Prompt):py -3 -m venv .venv.venv\Scripts\activate.bat

Then install the package (internet access is needed for installation):

python -m pip install -e .

Copy examples/algorithm.py into the handover-bench folder as algorithm.py, using your file manager. Do this once, then edit that copy to develop your policy and fill in your team details. Run it through the evaluator using the command below; running python algorithm.py alone does not run the simulation.

handover-bench evaluate --algorithm algorithm.py --suite data/practice --output results/practice

Each evaluation prints your score and creates results/practice/dashboard.html and results/practice/results.json. Open dashboard.html by double-clicking it or using your browser’s Open File command. The dashboard shows your score against A3 (100), all seven KPI gains and penalties, and per-scenario results. It needs no server or internet connection. After editing algorithm.py, rerun the evaluation command and reload the browser page. In a new terminal, return to the same folder and activate the virtual environment again; do not copy the starter over your work. Full setup and troubleshooting instructions are in README.md.

The practice suite (see Section 6 of Document 2) is already generated. You do not need SUMO, MATLAB, the Vienna 5G simulator or a GPU, and you do not need to regenerate any data to get started. The package includes the A3 baseline, which is a working and tested implementation of everything described in Section 5 of Document 2, one always-stay starter policy (examples/algorithm.py), the evaluator, a local results dashboard that also shows the never hand over comparison reference (equivalent to the starter) next to A3, and the following documents:

| Document | What it contains |
| --- | --- |
| README.md | Installation and running, the observation and action reference, the submission rules and execution limits, the modelling assumptions, and the 3GPP basis of the simulator |
| docs/report_template.md | The structure to follow for your report |

## 3. How You are Scored? (Document 2, Section 8 contains the details)

Your score S is a composite performance index relative to A3, which scores 100 on the same scenario suite. S above 100 indicates a better weighted combination of the seven KPIs; S below 100 indicates a worse combination. S is not a percentage assignment mark. There is no imposed score cap, but each fixed suite has a finite mathematical upper bound (see Document 2, Section 8).

For each of the seven metrics, we calculate an epsilon-smoothed ratio r: yours divided by A3 for higher-is-better metrics, and A3 divided by yours for lower-is-better metrics. A ratio above 1 improves the score; a ratio below 1 penalises a regression. Metrics are averaged equally across scenarios before the score is calculated. We then combine these ratios using a weighted geometric mean and multiply the result by 100.

## 4. Deliverables and grading

Each group submits the following two files on Brightspace:

algorithm.py: your handover policy. It is run against the practice suite for your own development and against held-out scenarios for assessment. The file must be self-contained: at most 1 MiB, compatible with Python 3.11, using only the Python standard library, numpy and pandas, and without any separate model or data files. Parameters found by offline tuning, or a small learned model, may be written into the file itself (see README.md). Fill in the team details comment at the top of the file with your Brightspace group and the name and student number of every member.

report.pdf: one shared report per group, at most 8 pages excluding references and appendices, based on docs/report_template.md. Explain your design, comparisons with A3 and the supplied sample, per-scenario KPI gains and regressions, an ablation study, computational cost, and commands to reproduce your results. This group report contributes 10% of the assignment grade; the algorithm-performance component contributes 90% (see Marking below).

Submission deadline: 23:59 (Irish time) on Wednesday, 25 November 2026, on Brightspace.

Groups: The assignment is completed in groups of up to three students. Groups will be created based on random selection of three students. Submissions are made as that Brightspace group, so each group submits one algorithm.py and one report.pdf.

Late submissions: The UCD late submission policy applies. Work submitted up to five days after the deadline has its grade reduced by one grade points. Work submitted between one and two weeks after the deadline (6-10 working days) has its grade reduced by two grade points. Work submitted more than two weeks after the deadline is not accepted. Approved extensions are handled in according with UCD policy.

Marking: 90% of your group’s assignment grade comes from algorithm performance on a fixed, private assessment suite, using the score intervals below. The remaining 10% comes from your group’s single shared report. Every group is assessed against the same criteria. Your grade does not depend on class rank, and there is no limit on the number of groups receiving any grade. The two component grades are combined using the applicable UCD component-grade calculation procedure. The sample-submission rule above and the late-submission rules still apply.

Read the table using S, the evaluator’s aggregate score rounded to two decimal places. Composite-index improvement over A3 is 100 × (S / 100 − 1)% = (S − 100)%. For example, S = 135 means a 35% increase in the composite index; it does not mean that throughput or every KPI improved by 35%.

Your algorithm-performance component is graded as follows:

| Performance grade | Aggregate score S | Composite-index improvement over A3 |
| --- | --- | --- |
| A+ | S ≥ 135 | ≥ 35% |
| A | 131 ≤ S < 135 | 31% to < 35% |
| A− | 127 ≤ S < 131 | 27% to < 31% |
| B+ | 124 ≤ S < 127 | 24% to < 27% |
| B | 121 ≤ S < 124 | 21% to < 24% |
| B− | 118 ≤ S < 121 | 18% to < 21% |
| C+ | 115 ≤ S < 118 | 15% to < 18% |
| C | 112 ≤ S < 115 | 12% to < 15% |
| C− | 109 ≤ S < 112 | 9% to < 12% |
| D+ | 106 ≤ S < 109 | 6% to < 9% |
| D | 103 ≤ S < 106 | 3% to < 6% |
| D− | 100 ≤ S < 103 | 0% to < 3% |
| Fail | Valid S < 100, or invalid run | Below baseline, or invalid |
| No submission | No algorithm submitted | Not evaluated |

For assessment, your unmodified algorithm.py is evaluated on the same fixed, private suite as A3, using the published simulator, configuration and scoring rules. These unseen scenarios follow the published assumptions. Your practice score is feedback and does not determine your assessment grade. Failure on any assessment scenario, for example an exception, timeout or unavailable import, invalidates the whole performance run: its score is 0 and its performance component fails. A valid score below 100 also fails the performance component; the group report is assessed separately. Submitting the supplied sample remains an assignment-level fail under the rule above.

## 5. Help and academic integrity

Post questions about the assignment brief, the behaviour of the simulator, or anything that looks like a bug on the module's Brightspace discussion forum rather than in a private message. If something in the package is unclear to you, it is very likely unclear to other students as well, and answers on the forum are visible to everyone.

Use of generative AI: You may use generative AI tools, such as ChatGPT, Claude or Copilot, to help with coding and writing, provided that you declare in your report how you used them. Your group remains fully responsible for everything you submit, including its correctness and your understanding of it.

Submit only what Section 4 asks for: algorithm.py and report.pdf. Everything your policy does must go through the observation and action interface described in Section 1. There is no other channel to the simulator, and your work is graded with the evaluator you were given, not with a modified copy of it.
