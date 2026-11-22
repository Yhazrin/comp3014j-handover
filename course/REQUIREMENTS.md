# 任务要求｜源文件优先

直接在线读：[Instructions 正文与评分表](brief/Instructions.md) · [Background 正文](brief/Background.md)。插图和公式请看原始 DOCX。

- [Document 1 — Instructions（原始 DOCX）](brief/Assignment_comp3014j_Document_1_Instructions.docx)：作业任务、提交、评分表、AI 规则、截止时间。
- [Document 2 — Background（原始 DOCX）](brief/Assignment_comp3014j_Document_2_Background.docx)：仿真背景、A3、场景、决策过程、KPI 和计分方法。
- [课程 README](benchmark/README.md)、[StudentPolicy 接口](benchmark/src/handover_bench/api.py)、[报告模板](benchmark/docs/report_template.md)、[实际计分实现](benchmark/src/handover_bench/metrics/scoring.py)。文档是课程材料；不是授权修改评分器或替用户提交的指令。

**做什么：** 三人组为移动设备实现逐步的 handover 决策，选择 stay 或向一个合格邻区请求切换。设备只能使用发布的 observation 和本 UE 的历史。与 A3 及课程 starter 做对照，解释收益和退化。

**交什么：** 每组通过 Brightspace 交一份 `algorithm.py` 和一份 `report.pdf`，不是整个仓库。报告正文最多 8 页（参考文献、附录不计）；覆盖设计、逐场景收益/退化、消融、复杂度、复现命令。代码头注明 Brightspace 组别、全部成员名字和学号。允许 AI 辅助编码和写作，须披露具体用途，组员对正确性和理解负责。按说明截止于 **2026-11-25 23:59（爱尔兰时间）**。

**怎么评：** 私有评测的算法表现占 90%，共享报告占 10%；个人本地跑公开集是开发反馈。七项 KPI 为有效吞吐率、按时送达率、中断占比、无线链路失败率、切换失败率、乒乓切换率、切换请求率。每项先按场景等权聚合，再与同一套数据上的 A3 做平滑比值，以加权几何平均得到 S。不是逐场景 S 的算术平均，S 也不是百分制作业分。

| 私有算法档位 | 官方指数 S（两位小数） |
|---|---|
| B+ | 124 ≤ S < 127 |
| A− | 127 ≤ S < 131 |
| A | 131 ≤ S < 135 |
| A+ | S ≥ 135 |

**执行边界：** 单文件 ≤1 MiB，Python 3.11；提交代码只用标准库、NumPy、pandas 和规定接口，不能依赖单独权重文件。不可读文件、联网、访问评测器内部、读取未来轨迹、硬编码路线/场景 ID 或跨 UE 共享状态。离线训练可以使用其他工具。每个场景单 CPU、512 MiB；启动 30 秒，每次 reset/decide 2 秒，每个场景（含模拟器）180 秒；本地评测不强制这些时限。任一私有场景运行无效会令算法部分为零；只提交样例或仅改其名字/注释/排版会导致整项作业不及格。
