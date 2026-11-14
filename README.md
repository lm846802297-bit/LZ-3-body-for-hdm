# LZ 3-body dark matter interpretation

本仓库研究暗物质三体辐射过程
\[
\chi_1 + A \longrightarrow \chi_1 + A + s
\]
能否产生与 LZ 高能氙核反冲数据相容的谱形和事件率，并同时满足核结构、粒子物理、宇宙学及探测器约束。研究目标是检验该机制，而不是预设它已经解释候选事件。

## 研究文档入口

- [AFH Xe-131 核响应、三体散射与天然氙反冲率主报告](research/docs/09_afh_xe131_three_body_scattering_natural_xenon.md)：完整正文及正式附录 A–G。
- [研究文档索引](research/docs/README.md)：主报告、独立附录、公式索引和补充记录。
- [公式—符号—正文—程序—结果交叉引用](research/docs/formula_symbol_code_cross_reference.md)：F1–F12 公式、单位、程序入口、输出和适用边界。
- [研究目录索引](research/README.md)：各专题的内容和科学状态。
- [Figure 2 数值结果总索引](research/docs/supplements/figure2_results_master_index_2026-11-13.md)：benchmark、输入、参数、输出和 SHA-256 provenance。
- [Figure 2 科学状态表](research/docs/supplements/figure2_scientific_status_2026-11-13.md)：明确各项验证的适用范围和未完成边界。
- [Eq. (6) kernel 与 Figure 2 数值复现入口](research/figure2_full_reproduction/README.md)。
- [LZ detector-response 输入与 rate-level 归档说明](research/lz_detector_response/README.md)。

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
- 贡献入口：[CONTRIBUTING.md](CONTRIBUTING.md)
- 研究分支、目录、复现和合并规范：[research/WORKFLOW.md](research/WORKFLOW.md)
- 新研究目录模板：[research/_template/README.md](research/_template/README.md)

## 仓库结构

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

## 当前科学状态（2026-11-14）

- **Eq. (6) kernel：** 已有 Dirac-spinor 实现、运动学/自旋迹检查和数值积分测试；模型的 Dirac/Majorana、完整矢量扇区等输入仍须按具体 benchmark 明确。
- **核响应与天然氙：** AFH Xe-131 的 2401 点响应已通过 60 位 mpmath 检查和 Wolfram 14.0.0 原生 Mathematica/Python 逐点比较（最大相对差异 $3.59\times10^{-9}$）；七种官方 AFH default 同位素的 AFH-7 连续谱及 AFH-7 + Helm-2 的 Hybrid-9 连续谱现已归档。Xe-124/Xe-126 仍无官方 AFH default density matrix，不伪造输入。
- **LZ 接口：** 已完成一维 final-ROI efficiency 加权的 GCN/JJ55 rate-level event-yield estimates；尚不是二维 NEST + background + profile-likelihood 的完整 LZ recast，也不是 90% CL exclusion。
- **450 keV benchmark：** 已归档一个条件性 pointwise \(\mathcal L_{00}\)/\(I_6\) 验证，以及一个独立的 Xe-131 固定速度、零宽度、\(A u\) 质量近似曲线。后者只覆盖 130–650 keV 的内部网格，不能当作天然氙 halo rate。
- **高能尾部核模型敏感性：** 225–269.9 keV 效率加权尾部已比较 AFH-7、Hybrid-9、GCN、JJ55 和 Helm-9；Hybrid-9 相对 AFH-7 的变化约 0.7–1.2%，GCN/JJ55 约 12–19%，Helm-9 约 4.5–4.7 倍。结果是 rate-level 诊断，不是 likelihood。
- **完整 Eq. (6) 截面：** response-level AFH 原生 Mathematica 验证已有 PASS 归档；完整 \(I_6\) 与 \(d\sigma_A/dE_R\) 的 Mathematica–Python 逐点验证仍待执行，安排在其他研究工作完成之后。
- **总体解释：** 代码、文档和归档完成不等于所有物理假设均已验证，更不代表模型已经解释 LZ 候选事件。
