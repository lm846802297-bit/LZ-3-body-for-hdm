# LZ 3-body dark matter interpretation

本仓库研究通过暗物质三体辐射过程
\[
\chi_1 + A \longrightarrow \chi_1 + A + s
\]
解释 LZ 高能氙核反冲候选事件的可能性。研究目标是检验这一机制能否同时满足高能候选事件、低能/高能侧带、探测器响应、遗迹丰度及额外暗辐射约束，而不是预设其解释成功。

## 论文源码

原始论文的核心文本源文件和编译脚本已加入 [paper-source/](paper-source/README.md)：
- \`main.tex\`：原始 PRD/RevTeX 主文件，保持原样；
- \`ref.bib\`：原始 BibTeX 文献库；
- \`utphys28mod.bst.gz\`：压缩保存的原始参考文献样式；
- \`build.sh\`：在临时副本中修正 BibTeX 数据库 basename 后编译。

原始 ZIP 中的七个 figure PDF 已登记在 [源码资产清单](paper-source/ASSET_MANIFEST.md)，但尚未加入 GitHub 分支。需要从原始 ZIP 恢复 \`paper-source/figures/\` 后，才能从 checkout 独立编译。编译和视觉审计记录见 [docs/07_source_build_and_figure_audit.md](docs/07_source_build_and_figure_audit.md)。

原稿仍是研究草稿，具体 TODO 和源码审计见 [docs/06_original_source_audit.md](docs/06_original_source_audit.md)。

## 研究记录

- [模型、三体振幅与 Breit–Wigner 宽度](docs/01_model_and_amplitude.md)
- [LZ 数据、事件率与统计重铸路线](docs/02_lz_recast.md)
- [冻结出后演化与 \(\Delta N_{\rm eff}\)](docs/03_cosmology.md)
- [草稿审计、未解决问题与执行路线](docs/04_audit_and_roadmap.md)
- [参考文献与数据来源](docs/05_references.md)
- [与原始 LaTeX 源码逐项对照](docs/06_original_source_audit.md)
- [源码编译与图像审计](docs/07_source_build_and_figure_audit.md)

## 实验动机

LZ Collaboration 在 2.84 tonne-year 曝光的扩展核反冲分析中报告一个与核反冲相符的候选事件：
\[
E_R = 248 \pm 23_{\rm stat} \pm 23_{\rm sys}\ {\rm keV}.
\]
背景假设下全局显著性为 \(2.6\sigma\)，最大局部显著性为 \(3.4\sigma\)。这不是暗物质发现。实验原文：arXiv:2609.02823；公开数据 DOI: 10.17182/hepdata.182472.v1。

## 研究纪律

1. 将该事件称为 candidate/event of interest，不称为 discovery。
2. 区分真实反冲谱 \(dR/dE_R\)、探测器卷积后的重建谱和最终事件似然。
3. 当前三体截面和直接探测谱属于 vector–vector 分支；scalar–pseudoscalar 分支目前只有相互作用拉格朗日量。
4. 宇宙学计算只保留原稿实际写出的碰撞项；被忽略的重态相关源项需作为独立扩展验证。
5. 只有在输入、数值测试、统计构造和独立复现归档后，才能把结果标记为 validated。
