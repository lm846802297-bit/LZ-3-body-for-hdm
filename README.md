# LZ 3-body dark matter interpretation

本仓库研究暗物质三体辐射过程
\[
\chi_1 + A \longrightarrow \chi_1 + A + s
\]
能否产生与 LZ 高能氙核反冲数据相容的谱形和事件率，并同时满足核结构、粒子物理、宇宙学及探测器约束。研究目标是检验该机制，而不是预设它已经解释候选事件。

## 研究文档入口

- [AFH Xe-131 核响应、三体散射与天然氙反冲率主报告](research/docs/09_afh_xe131_three_body_scattering_natural_xenon.md)：完整正文及正式附录 A–H。
- [研究文档索引](research/docs/README.md)：主报告、独立附录、公式索引和补充记录。
- [公式—符号—正文—程序—结果交叉引用](research/docs/formula_symbol_code_cross_reference.md)：F1–F12 公式、单位、程序入口、输出和适用边界。
- [研究目录索引](research/README.md)：各专题的内容和科学状态。
- [Figure 2 数值结果总索引](research/docs/supplements/three_body_results_master_index_2026-11-16.md)：main 当前的 13 组结果、91 个已提交文件 SHA-256/大小记录及 1 个外部高阶谱归档校验项（共 92 项）；2026-11-13 旧索引保留为历史快照。
- [Phase 1 科学内容审查](research/docs/supplements/scientific_content_audit_2026-11-16.md)：AFH-7 全网格、旧/新相空间积分差异、GCN/JJ55 数值精度边界。
- [Figure 2 科学状态表](research/docs/supplements/three_body_scientific_status_2026-11-13.md)：明确各项验证的适用范围和未完成边界。
- [Eq. (6) kernel 与 Figure 2 数值复现入口](research/three_body_calculation_and_validation/README.md)。
- [LZ detector-response 研究档案](research/lz_detector_response/README.md)，以及 [2026 NR/ER 响应、二维折叠与统计审计索引](research/lz_detector_response/lz_2026_extended_nr/README.md)。

## 论文源码

- paper-source/main_original.tex：用户提供的原始 TeX，逐字节保留；
- paper-source/main.tex：编辑整理后的工作稿；
- paper-source/ref.bib：原始 BibTeX 文献库；
- paper-source/utphys28mod.bst.gz：原始参考文献样式；
- paper-source/build.sh：先进行 SHA-256 校验，再编译整理稿；
- paper-source/figures/：七张原始 figure PDF，未重绘或压缩。

图 2 的标量质量图例存在 MeV/keV 不一致，但原始 ZIP、仓库历史和已检索的文件库中均未找到相应绘图脚本或数值输入，因此暂不修改图例。详见 [paper-source/EDITORIAL_STATUS.md](paper-source/EDITORIAL_STATUS.md)。

## 贡献与研究规范

- 仓库级强制任务规范：[AGENTS.md](AGENTS.md)
- 研究依据优先级与论文草稿边界：[research/RESEARCH_GOVERNANCE_AND_SOURCE_HIERARCHY.md](research/RESEARCH_GOVERNANCE_AND_SOURCE_HIERARCHY.md)
- 贡献入口：[CONTRIBUTING.md](CONTRIBUTING.md)
- 研究分支、目录、复现和合并规范：[research/WORKFLOW.md](research/WORKFLOW.md)
- 新研究目录模板：[research/_template/README.md](research/_template/README.md)

## 仓库结构

- [完整文件分类与研究导航](research/FILE_MAP.md)：说明各目录的科学职责、数据状态和结果使用边界。
- paper-source/：原始论文源码、工作稿和图件；
- research/：研究文档、计算程序、单元测试、审计记录和数值结果；
- v6/：已归档的 AFH DMFormFactor v6.0 Mathematica 源文件；原始 ZIP 仍只保留 SHA-256 provenance。
- .github/workflows/：可选的计算调度与自动化验证。科学研究不以 CI 运行成功为前提。

## 主要研究记录

- [模型、三体振幅与 Breit–Wigner 宽度](research/docs/01_model_and_amplitude.md)
- [LZ 数据、事件率与统计重铸路线](research/docs/02_lz_recast.md)
- [冻结出后演化与 \(\Delta N_{\rm eff}\)](research/docs/03_cosmology.md)
- [审计与研究路线](research/docs/04_audit_and_roadmap.md)
- [参考文献](research/docs/05_references.md)
- [原始源码审计](research/docs/06_original_source_audit.md)
- [构建与图像审计](research/docs/07_source_build_and_figure_audit.md)
- [\(\chi_2\to\chi_1s\) pole width 推导与验证](research/docs/08_chi2_decay_width.md)
- [AFH v6.0、Eq. (6)、天然氙与 LZ rate-level 主报告](research/docs/09_afh_xe131_three_body_scattering_natural_xenon.md)
- [VV 核子流匹配与 Xe-131 \(W_{\Phi''}\) 响应审计](research/afh_vv_phi_xe131/README.md)：AFH 自旋—轨道响应、质量—轨道干涉、2401 点数值结果及三体振幅匹配边界。

## 当前科学状态（2026-11-16）

- **Eq. (6) kernel：** 已有 Dirac-spinor 实现、运动学/自旋迹检查和数值积分测试；模型的 Dirac/Majorana、完整矢量扇区等输入仍须按具体 benchmark 明确。
- **核响应与天然氙：** AFH Xe-131 的 2401 点响应已通过 60 位 mpmath 检查和 Wolfram 14.0.0 原生 Mathematica/Python 逐点比较（最大相对差异 $3.59\times10^{-9}$）。七种官方 AFH default 同位素的 16,807 行响应网格及 AFH-7/Hybrid-9 的 84 点全范围反冲谱已归档；高阶摘要的最大基准—最终谱差异为 $6.47\times10^{-6}$。这仍是七同位素 AFH-7，不是 AFH-9；最终 1,344 行高阶谱 ZIP 目前仅有外部 checksum，未提交完整内容。Xe-124/Xe-126 仍无官方 AFH default density matrix，不伪造输入。
- **LZ 探测器响应：** 已归档公开 NEST `541b643` 的 EFT2024 配置候选、NR/ER 响应审计、三体二维响应折叠、Fig. S2 rate-level folds，以及十独立种子的 paired S1 响应和 100,000 次 seed-cluster bootstrap。1-keV 仍是全范围数值参考；独立全范围 1/5-keV 比较未通过 1% 二维 TV 门槛。黑色 360-keV benchmark 的点估计低于 1%，但 bootstrap 和 leave-one-out 不支持稳健等价性声明。以上均为中间 NEST 响应诊断，不是官方 waveform-level selected PDF、profile likelihood 或 90% CL exclusion。
- **450 keV benchmark：** 已归档一个条件性 pointwise \(\mathcal L_{00}\)/\(I_6\) 验证，以及一个独立的 Xe-131 固定速度、零宽度、\(A u\) 质量近似曲线。后者只覆盖 130–650 keV 的内部网格，不能当作天然氙 halo rate。
- **高能尾部核模型敏感性：** 225–269.9 keV 效率加权尾部已比较 AFH-7、Hybrid-9、GCN、JJ55 和 Helm-9。GCN/JJ55 的 8×8×4 linear-W² kernel 与 16×16×8 spot-check 最大差异为 $2.19\times10^{-4}$；AFH-7/Hybrid-9 使用 threshold-u²，二者尚未匹配数值积分方案。GCN/JJ55 的 12–19% 尾部变化远大于该差异，但 0.66–1.16% 的 Hybrid-9 变化应在统一积分后再作为精密结果。所有结果仍是 rate-level 诊断，不是 likelihood。
- **完整 Eq. (6) 截面：** AFH Xe-131 response-level 原生 Mathematica/Python 验证已有 PASS；现已完成原生 Wolfram 14.2.0 与独立 Python 的 652 行 full Eq. (6) 逐点比较（500 open、152 closed）。最大相对差异：I6 = 1.33872e-12、dσ = 1.33872e-12、已转换 dσ = 1.33857e-12；AFH physical/package response 分别为 3.36051e-16 / 3.76685e-16，factor-four mapping residual = 4.30300e-16。Mathematica/Python 各自的单位转换恒等式残差分别为 3.34766e-16 和 0。交叉代码的 dσ 比较按 2e-7 观测量容差验收；q、C0、响应归一化映射、动量和各自单位转换恒等式分别按其独立容差验收。**固定速度 Xe-131 full-cross-section cross-code gate 已 PASS_WITH_NOTES**；仍不是天然氙 halo fold 或 detector-level LZ likelihood，且 pole width 仅在条件性 Dirac / real-scalar / pure-scalar / single-channel 假设下成立。
- **总体解释：** 代码、文档和归档完成不等于所有物理假设均已验证，更不代表模型已经解释 LZ 候选事件。
