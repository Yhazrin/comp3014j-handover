# COMP3014J · VASH Handover

三人小组协作仓库：切换算法、英文报告、报告源码与公开实验结果。

## 当前版本

- 策略：VASH 1.0 / V10，`StudentPolicy.reset` 与 `StudentPolicy.decide`。
- 公开十场景：**126.13**，A3 基准为 **100**。
- 开发集 seeds 1–6：131.97；复用留出集 seeds 7–10：115.13。
- 报告：第 2 版，共 8 页，正文 6 页。

## 文件入口

| 文件 | 用途 |
|---|---|
| [algorithm.py](submission/algorithm.py) | 算法提交文件 |
| [report.pdf](submission/report.pdf) | 英文报告 |
| [报告源码](tools/build_reference_report.py) | 编辑正文、表格和图表，重新导出 PDF |
| [中文讲解](LEARNING_GUIDE.md) | 算法推导、实验解释和建议分工 |
| [公开结果](experiments/v10_full/results.json) | 指标与逐场景结果 |
| [上界研究笔记](SCORE_BOUND_NOTE.md) | 单独保留的离线分析 |

报告及代码中的 `GROUP_ID`、`MEMBER_1/2/3` 待填写真实信息。课程允许 AI 辅助编码和写作，报告中保留了实际使用范围声明。

## 用公开数据运行

老师的原始课程包和数据保留在各自电脑上，不放入本仓库。先准备 Python 3.11，再执行：

```sh
git clone https://github.com/Yhazrin/comp3014j-handover.git
cd comp3014j-handover
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements-evaluation.txt
export BENCH_ROOT='/你的路径/handover-bench'
./reproduce.sh
```

`BENCH_ROOT` 指向同时包含 `src/` 和 `data/practice/` 的课程目录。脚本自动创建结果目录；冻结版本的已有实测指数为 126.13。

需要复现开发/留出划分时：

```sh
.venv/bin/python tools/prepare_splits.py --bench "$BENCH_ROOT"
```

## 编辑与生成报告

```sh
.venv/bin/python -m pip install -r requirements-report.txt
.venv/bin/python tools/build_reference_report.py
```

正文与布局在 `tools/build_reference_report.py`，生成文件是 `submission/report.pdf`。构建器使用仓库中保存的实验结果，不会自动运行模拟器。它将结果绑定到当前冻结算法的 SHA-256；修改算法后，应先更新对应实验结果、代码哈希和报告中的说明，再生成报告。

## 三人协作

建议分别负责算法、实验、报告；具体贡献按实际完成的工作记录。

```sh
git switch -c report/member-details
# 修改文件
git add submission/algorithm.py tools/build_reference_report.py submission/report.pdf
git commit -m "docs: fill group details"
git push -u origin report/member-details
```

在 GitHub 发起 Pull Request，再合并到 `main`。公开仓库可以直接浏览或 fork；需要直接推送分支的同学由仓库拥有者添加为 collaborator。

正式交作业时只提交 `submission/algorithm.py` 与 `submission/report.pdf`。不要上传整个协作仓库。

## 结果与材料范围

本仓库没有老师提供的原始数据、课程压缩包、本机虚拟环境或完整执行日志。发布的 JSON 来源于已有公开实验：本机绝对路径已改为相对路径，逐 UE 明细已省略；聚合指标和逐场景结果保留。报告中的部分历史归档引用指向原本的完整本地研究目录。

开发集、复用留出集和最终私有评测各有不同用途。最终私有评测由老师运行；小组使用公开数据完成开发、复现和报告。
