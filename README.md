# LZ 3-body dark matter interpretation

本仓库研究通过暗物质三体辐射过程
\[
\chi_1 + A \longrightarrow \chi_1 + A + s
\]
解释 LZ 高能氙核反冲候选事件的可能性。研究目标是检验这一机制能否同时满足候选事件、探测器响应、遗迹丰度及额外暗辐射约束，而不是预设其解释成功。

## 论文源码

- paper-source/main_original.tex：用户提供的原始 TeX，逐字节保留；
- paper-source/main.tex：编辑整理后的工作稿；
- paper-source/ref.bib：原始 BibTeX 文献库；
- paper-source/utphys28mod.bst.gz：原始参考文献样式；
- paper-source/build.sh：先进行 SHA-256 校验，再编译整理稿；
- paper-source/figures/：七张原始 figure PDF，未重绘或压缩。

图 2 的标量质量图例存在 MeV/keV 不一致，但原始 ZIP、仓库历史和已检索的文件库中均未找到相应绘图脚本或数值输入，因此暂不修改图例。详见 paper-source/EDITORIAL_STATUS.md。

## 仓库结构

- `paper-source/`：原始论文源码、工作稿和图件。
- `research/`：集中保存全部研究文档、计算程序、单元测试、审计记录和数值结果；目录索引见 `research/README.md`。
- `.github/workflows/`：可复现计算与自动化验证。

## 研究记录

- 模型、三体振幅与 Breit–Wigner 宽度：research/docs/01_model_and_amplitude.md
- χ₂ → χ₁s pole width 的解析推导、数值结果与验证：research/docs/08_chi2_decay_width.md
- 对应数值实现与单元测试：research/figure2_full_reproduction/chi2_decay_width.py、research/figure2_full_reproduction/tests/test_chi2_decay_width.py
- LZ 数据、事件率与统计重铸路线：research/docs/02_lz_recast.md
- 冻结出后演化与 ΔN_eff：research/docs/03_cosmology.md
- 审计与研究路线：research/docs/04_audit_and_roadmap.md
- 参考文献：research/docs/05_references.md
- 原始源码审计：research/docs/06_original_source_audit.md
- 构建与图像审计：research/docs/07_source_build_and_figure_audit.md

## 科学状态

当前内容仍是研究草稿。源码整理不等于物理结果验证，也不代表模型已经解释 LZ 候选事件。
