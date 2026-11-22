# COMP3014J · Group 25 / VASH-Q

**评审入口：** [老师的任务要求](course/REQUIREMENTS.md) · [现状、尝试与证据](review/STATUS.md) · [给 Pro / Agent 的任务单](review/AGENT_PROMPT.md)

此仓库包含两份原始作业说明、原版评测器及十个公开场景。克隆后可以直接评测，不需要作者电脑上的文件。当前保留的版本是 **VASH-Q（完整公开集 126.45）**，不是较早的 V10（126.13），也不是单次公开得分更高的 timing（126.53）。**127 / 131 / 135 是私有算法评测的 A− / A / A+ 门槛。**

| 文件 | 用途 |
|---|---|
| [submission/algorithm.py](submission/algorithm.py) · [submission/report.pdf](submission/report.pdf) | 当前保留的两份提交候选，一一配套 |
| [report/report.tex](report/report.tex) | 当前五页英文黑白报告的可编辑源，不是旧版 PDF 构建器 |
| [两份官方 DOCX](course/brief/) · [官方 README](course/benchmark/README.md) · [报告模板](course/benchmark/docs/report_template.md) | 评分、约束、接口和报告要求；若摘要有出入，以课程原文为准 |
| [公开结果](review/evidence/summary.json) · [逐场景 JSON](review/evidence/public-queue.json) · [受控消融](review/evidence/table3.csv) | 真实评测和版本比较；公开数据与合成数据分开 |
| [review/variants/](review/variants/) · [合成对照工具](tools/compare_transfer.py) | 历史对照和新想法的同场测试，不是提交文件 |

## 复现（在仓库根目录）

需要 Python 3.11。先创建环境，安装仓库里的官方包：

```sh
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install ./course/benchmark
PYTHON=python ./reproduce.sh runs/public-q
python -B tools/ablation.py course/benchmark runs/table3.csv
```

第一条评测运行提交候选和**老师发的真实 starter**；A3 由官方评测器在同一组场景运行。预期：starter **84.93**，A3 **100.00**，VASH-Q **126.45**；162 次请求，中断占比 **0.6801%**。输出目录包括原始 JSON、HTML、摘要和表 2；消融命令生成表 3。重复运行换一个新的输出路径。历史复现环境的精确依赖见 [requirements-evaluation.txt](requirements-evaluation.txt)。

测试新代码时，从当前候选复制一份到独立分支，不要一开始就覆盖基线：

```sh
git switch -c review/next-policy
mkdir -p candidates
cp submission/algorithm.py candidates/next.py
# 编辑 candidates/next.py 后：
python -m handover_bench.cli evaluate --algorithm candidates/next.py \
  --suite course/benchmark/data/practice --output runs/candidate-public
python -B tools/compare_transfer.py --candidate candidates/next.py \
  --start 120301 --count 20 --output runs/paired-transfer.json
```

120301 起这一段是**建议预留**的新种子，不是已取得的结果。第一次揭晓后应记录为已用，不能再称为盲测。要复现已发表的十个合成场景对照，使用 `--candidate review/variants/timing.py --start 47301 --count 10`，预期 Q **122.34**，timing **122.31**。生成器与课程私有数据无关。

## 报告与提交

如需编译报告，使用 `pdflatex -interaction=nonstopmode -halt-on-error -output-directory=report report/report.tex`。只有确认数据和哈希一致后才替换提交 PDF。实际交 Brightspace 前，组员须在本地补上三人的真实学号、确认各自实际贡献；修改代码头注释也会改变哈希，应重跑评测并更新报告。公开仓库不放学号。

旧 `experiments/v10_*`、`LEARNING_GUIDE.md`、旧 ReportLab 构建器及旧版证据是历史资料，不能替代上述 VASH-Q 文件。官方包保留原版 [LICENSE](course/benchmark/LICENSE) 和 [第三方声明](course/benchmark/THIRD_PARTY_NOTICES.md)。本仓库不是课程发布渠道，也没有私有评测结果。
