# Figure 2 三体暗物质计算：科学结果状态表

## 0. Current status update — 2026-11-18

本次更新修正了完整 VV 核子流与 AFH 非 \(M\) 响应的数值状态。AFH-7 的 \(M\) 响应仍是唯一已归档的七同位素 AFH 核响应基线；PR #53 的 \(L^{\mu\nu}\) 只与核质心点电荷流收缩。先前 Python source-translated 的 \(\Sigma'\) selected-\(q\) 表已撤回；AFH \(\Delta J\) 已纠正为同阶 \(MJLDivQ\) 映射，旧 parity-conflict 判断已撤回。PR #51 现已归档 Xe-131 的 2,401 点 native \(M,\Phi'',M\Phi''\) 响应，专用 Python validator 为 PASS；该结果仍仅限核响应层。当前 flavor-universal 三味 benchmark 暂采用 2017 年显式 flavor-separated \(F_2^V(0)=-0.552\)，HKS 2015 紧凑记号差异保留待核.

This update supersedes the 2026-11-14 snapshot rows below for the AFH-7 full-grid milestone and the 2026-11-16 Python-only full Eq. (6) / factor-four validation and native Mathematica/Python 652-row full-cross-section comparison. Historical tables remain below for provenance; they are not the current status where this update gives a newer result.

| Topic | Current status | Evidence | Remaining boundary |
|---|---|---|---|
| AFH v6.0 seven-isotope response grid | **Archived / validated within scope** | Seven matrices, seven 2,401-node tables and combined 16,807-row grid are on main with SHA-256 manifest | Xe-124/Xe-126 still lack AFH default matrices |
| AFH-7 / Hybrid-9 natural-xenon spectrum | **PASS_WITH_NOTES** | 84 recoil points, four benchmarks, 1,344 baseline rows; threshold-\(u^2\); high-order summary max baseline-to-final difference \(6.47\times10^{-6}\) | Full high-order 1,344-row ZIP is external/checksum-only; output is a sampled grid, not an analytic continuum |
| Historical AFH selected-point rates | **HISTORICAL** | Reproducible legacy output retained | Old low-order linear-\(W^2\) values differ from new threshold-\(u^2\) grid by about 230–255 ppm at common points; do not mix |
| GCN/JJ55 natural-xenon spectra | **PASS_WITH_NOTES** | Four 84-point spectra and metadata are archived | Legacy linear-\(W^2\) (\(8\times8\times4\)) production; max \(16\times16\times8\) kernel difference \(2.18895\times10^{-4}\); matched threshold-\(u^2\) rerun pending |
| Cross-model high-energy tail comparison | **PROVISIONAL** | Broad GCN/JJ55 shifts exceed the reported kernel error | Hybrid-9 0.66–1.16% shifts should be re-evaluated after matched quadrature |
| Python-only full Xe-131 Eq. (6) and factor-four ledger | **PASS_WITH_NOTES (within Python)** | v=800 km/s fixed-speed, conditional Dirac / real-scalar / pure-scalar / single-channel pole-width assumptions; 652 rows (500 open, 152 closed), 16 high-order anchors; max I6 relative difference 1.66367e-11, factor-four mapping residual 3.55679e-16, physical/no-factor-four ratio residual 0; artifact 14112736343 | This is not a natural-xenon halo fold or an independent Mathematica/Python comparison |
| Full Mathematica–Python \(d\sigma_A/dE_R\) | **PASS** | Native Wolfram 14.2.0 and independent Python compare 652 rows (500 open, 152 closed); max I6 1.34e-12, dσ 1.34e-12, AFH response 3.36e-16, factor-four mapping residual 4.30e-16 | Fixed-speed Xe-131 only; per-code unit-conversion identities pass at 2e-12; converted cross-code dσ uses 2e-7 observable tolerance; conditional Dirac / real-scalar / pure-scalar / single-channel pole-width; not halo fold or LZ likelihood |
| F13 full three-body VV current and AFH contraction | **NOT COMPLETE** | Appendix I fixes the Dirac–Pauli convention and AFH response map; PR #53 has the exact-source four-component DM tensor / point-current diagnostic; PR #51 archives native Xe-131 indices 1,4,7 (M, Phi'', M-Phi'') with response-level validator PASS | No internal-nucleon (F_1/F_2) coefficient contraction, no spatial-response native comparison, and no full (L_{mu\nu}W_A^{mu\nu}) or natural-xenon VV spectrum |
| Nucleon \(F_1/F_2\) matching | **ANALYTIC MAP DOCUMENTED; FINITE-\(t\) INPUT OPEN** | Explicit flavor-separated benchmark uses \(F_2^{V,p/n}(0)=-0.552\) under isospin symmetry; \(F_1^V(0)=3\) | HKS 2015 compact \(\kappa_N,\kappa_N^s\) expression differs when naively summed; reconcile definitions and propagate strange-moment covariance; finite-\(t\) form factors open |
| Xe-129/Xe-131 \(\Sigma'\) | **PREVIOUS TABLE WITHDRAWN; NATIVE PENDING** | Earlier Python source-translated selected-\(q\) table withdrawn after AFH source-call-chain review | Native Wolfram export, pointwise comparison, normalization and multipole convergence remain pending |
| AFH \(\Delta\), \(W_{\Sigma'\Delta}\) | **MAPPING CORRECTED; NATIVE PENDING** | DeltaJ now maps to same-rank MJLDivQ; earlier parity-conflict claim withdrawn | Native Wolfram outputs and Python pointwise comparison not yet completed |
| Xe-131 \(M,\Phi'',M\Phi''\) | **NATIVE RESPONSE ARCHIVED; VALIDATOR PASS** | PR #51 commits 2,401-node Wolfram 14.2.0 CSV, source/input metadata, Python validation JSON and SHA-256 manifest | Response-level only; no three-body Wilson-coefficient contraction or rate-level correction is established |
| Xe-129 \(\Phi''\), \(M\Phi''\) | **NOT STARTED** | Xe-131 native export is the first target | No AFH response grid or three-body coefficient contraction |
| Official LZ likelihood | **OPEN** | NEST proxy response and rate-level studies exist | No official waveform-level selected PDF, background/profile likelihood or 90% CL exclusion |

The Python-only full fixed-speed result and the native Mathematica/Python 652-row cross-code result are separate calculation layers. The latter now verifies pointwise agreement of the complete fixed-speed Xe-131 Eq. (6) implementation after the per-code unit-conversion identities were separated from the converted-rate cross-code comparison. Neither result is a natural-xenon halo fold or an official LZ detector likelihood. The historical Section 2–5 tables below retain their original dates and should be read as snapshots where they differ from this current-status table.

The 2026-11-16 source-of-truth index is [13 groups / 98 files](three_body_results_master_index_2026-11-16.md), including the native full Eq. (6) Mathematica/Python cross-code archive. The full audit is [scientific_content_audit_2026-11-16.md](scientific_content_audit_2026-11-16.md).

日期：2026-11-16（以下原始表保留 2026-11-14 状态快照；本页以新增 2026-11-16 更新为当前状态）
本表按“当前可证明的范围”给状态，不把某个局部 benchmark 的通过推广成整个模型或整条连续谱均已验证。

## 1. 状态定义

| 状态 | 判定标准 |
|---|---|
| **已验证** | 公式、代码和输入约定在明确范围内一致，并有独立解析推导、数值对照或可复现检查支撑 |
| **部分验证** | 主要链路已有结果和检查，但仍缺输入覆盖、独立实现、模型定义或更高层物理环节 |
| **待补输入** | 计算方法可以继续，但缺少必要的原始物理输入或模型定义 |
| **尚未完成** | 研究任务尚未执行到可判断正确性的阶段，不能给出完成性结论 |

## 2. 粒子物理与三体运动学

| 子任务 | 当前状态 | 已有证据 | 尚存边界 |
|---|---|---|---|
| vector–vector 分支的两张辐射图 | **部分验证** | 主报告 §1.1–1.2、附录 A.5；`eq6_kernel.py` 的 before/after propagator 和完整振幅相加 | 当前按 Dirac、实耦合实现；原模型未完全固定 Dirac/Majorana 与复耦合相位 |
| Dirac \(L_{00}\) trace 的程序实现 | **已验证（限定 Dirac 基准）** | 显式自旋求和与 Dirac trace 对照；before、after、interference 三项恢复完整迹；450 keV pointwise benchmark 与回归测试 | 不能自动外推为 Majorana 外部态 |
| \(\chi_2\) 条件性 pole width | **部分验证** | 附录 A.6 的 Dirac–scalar 两体衰变推导；代码宽度函数 | 依赖纯 scalar Yukawa、实标量、单一开放衰变道；不是完整自能 |
| \(q^\mu,t,Q\) 运动学关系 | **已验证** | 核质量壳解析推导；`rate_kinematics.py` 与 `joint_xe131.py` 使用 exact spatial \(Q\) | fixed-speed Xe-131 与 natural-xenon 使用不同且已记录的核质量输入方案 |
| \(W_{\min},W_{\max}\) 与三体相空间开放条件 | **已验证** | 主报告 §2.4、附录 A.2；`eq6_kernel.limits` 与 `rate_kinematics.wmax_squared` 一致 | 不是对任意 UV 模型和任意传播子方案的验证 |
| \(W^2,z,\phi_*\) 相空间 Jacobian 与 \(256\pi^3\) | **已验证（解析层）** | 正文 §2.5.1–2.5.8、附录 A.4.1–A.4.2；独立分解 \(d\Phi_3\)、flux、azimuthal average；\([I_6]={\rm GeV}^2\) 维度检查 | 解析结论限定于未极化相干靶和 leading \(J_A^0\) 近似；数值收敛另列如下 |
| \(I_6\) 数值求积收敛（P1-PhaseSpace） | **部分验证（按计算链分层）** | AFH-7/Hybrid-9 已有 84 点全范围 threshold-\(u^2\) 谱；基准到最终 \(24\times8\times8\times4\) 谱差异最大 \(6.47\times10^{-6}\)。GCN/JJ55 仍使用 linear-\(W^2\) \(8\times8\times4\)，\(16\times16\times8\) 检查最大 kernel 差异 \(2.18895\times10^{-4}\) | Native Mathematica/Python 完整 Eq. (6) 截面对照已在固定速度 Xe-131 范围内单独通过；GCN/JJ55 匹配求积和近传播子极点宽度处方系统比较仍开放 |
| 三体 \(v_{\min}\) 闭式公式 | **已验证** | 从 \(W_{\max}=m_{\chi_1}+m_s\) 独立推导；64 组输入与独立求根最大 \(|\Delta\beta|=3.89\times10^{-13}\) | 仍需对新增质量区间和完整连续谱网格做专门数值检查 |
| 450 keV pointwise \(L_{00}\) benchmark | **已验证（单点数值范围）** | \(48\times40\times24\) 求积、run manifest、局部验证记录、SHA-256 manifest | 单点 kernel 结果，不代表整条 \(d\sigma/dE_R\)、halo-fold 或 LZ 事件数 |
| 固定速度 Xe-131 \(d\sigma/dE_R\) 曲线 | **部分验证** | 105 个内部能量点、GCN/JJ55、metadata 与 SHA-256 校验 | 与 450 keV pointwise \(L_{00}\) 不同；端点外推/积分和 halo-fold 不包含在该曲线内 |
| 完整 (d\sigma_A/dE_R) Mathematica/Python 端到端对照 | **PASS（数值比较器）；PASS_WITH_NOTES（科学范围）** | Native Wolfram 14.2.0 与独立 Python：652 行（500 open、152 closed）、4 组 benchmark、16×16×8；max I6/dσ = 1.33872e-12，converted dσ = 1.33857e-12，AFH response = 3.36e-16，factor-four mapping residual = 4.303e-16；comparison JSON PASS | 固定速度 Xe-131；两端使用同一份原生 AFH 响应表；条件性 Dirac / real-scalar / pure-scalar / single-channel pole-width；不代表天然氙 halo fold 或官方 LZ likelihood |

## 3. AFH 核响应与核靶输入

| 子任务 | 当前状态 | 已有证据 | 尚存边界 |
|---|---|---|---|
| AFH v6.0 Xe-131 67 项密度矩阵提取 | **已验证（source + translation）** | 官方 v6.0 来源哈希、67 项逐项解析、CSV 与 source translation 对照；`v6/dmformfactor-V6.m` 已提交；七同位素矩阵和 16,807 行响应网格另已归档 | 原始 AFH package ZIP 仍为 checksum-only provenance；Xe-124/Xe-126 仍无 AFH default matrix |
| AFH Xe-131 2401 点响应 | **已验证（限定 response-level）** | 0–0.6 GeV、2401 节点；60 位 mpmath 与 Wolfram 14.0.0 原生 Mathematica/Python 逐点比较；四种响应量全部通过，最大相对差异 \(3.59087\times10^{-9}\) | 仅验证 Xe-131 AFH response-level，不代表三体 kernel、天然氙连续谱或 LZ likelihood |
| AFH factor-of-four 物理归一化 | **历史快照：response-level PASS** | raw (A^2/4)；setter (c_{\rm set}=2g_{VN})；physical (R_A(0)=A^2)；原生 2401 点响应表与 Python 对照通过 | 当前状态已在顶部 2026-11-16 更新：Python-only fixed-speed full Eq. (6) factor-four ledger 与原生 Mathematica/Python 652 行完整截面对照均已 PASS；适用范围仍限固定速度 Xe-131 和条件性宽度假设 |
| AFH Xe-131 响应极小值 | **部分验证** | 固定文献 \(b_A\)、精确空间 \(q\)、AFH default 67 项矩阵，三个 Figure 2 范围内的主要极小值已提取 | 这些是核响应极小值，不自动等于完整截面或 halo 事件率极小值 |
| AFH 七同位素响应 | **已验证（响应网格归档，限七同位素）** | 七种可用同位素；7×2401=16,807 个 direct finite-sum 响应节点及 source matrices 已提交；另保留 56 个 NIST/AME2020 selected-q mpmath 检查 | Xe-124/Xe-126 缺少官方 AFH default density matrix；AFH-7 不等于 AFH-9 |
| Xe-124、Xe-126 AFH default 密度矩阵 | **AFH v6.0 default dispatch 未提供** | 官方源文件第 1555–1597 行只列出 128、129、130、131、132、134、136；124/126 进入通用回退；新增静态 dispatch 回归测试 | 需独立、可追溯的核结构密度矩阵；0.1842% 原子丰度不是事件率误差上界 |
| 原始 Figure 2 的靶核定义 | **待补输入** | 已区分 Xe-131 固定靶诊断和 LZ 天然氙扩展 | 原稿未充分说明单一 Xe-131 还是天然氙混合物 |

## 4. 天然氙、halo 与探测器

| 子任务 | 当前状态 | 已有证据 | 尚存边界 |
|---|---|---|---|
| 天然氙靶核数与同位素丰度 | **已验证** | NIST 同位素输入；完整平均原子质量用于 \(N_T\)；原始丰度求和不重新归一化 | AFH 速率求和仅包括七种有响应的同位素 |
| AFH 天然氙 halo-fold | **已验证（AFH-7/Hybrid-9 84 点网格，限七同位素）** | 四组 benchmark、84 个 recoil 点、1,344 行谱；direct exact-q AFH finite sum；threshold-\(u^2\) 积分；高阶基准—最终谱差异最大 \(6.47\times10^{-6}\) | 高阶 1,344 行 ZIP 仅外部 checksum；Xe-124/Xe-126 仍缺 AFH；旧 selected-point 表是历史 linear-\(W^2\) 低阶结果，不可与新网格混用 |
| AME2020 direct exact-\(q\) selected-point 对照 | **部分验证** | 七同位素选定点输出、metadata 和独立 SHA-256 manifest | Xe-131-only hybrid 不等于完整 AME2020 七同位素重算 |
| GCN/JJ55 天然氙连续谱 | **部分验证（谱层完成，求积未匹配）** | 四组 benchmark 的 84 点谱、逐 benchmark metadata 和 quadrature crosschecks 已归档 | 生产为 linear-\(W^2\) \(8\times8\times4\)，高阶检查最大差异 \(2.18895\times10^{-4}\)；需用 threshold-\(u^2\) 与 AFH-7 统一后重算 |
| halo 模型系统扫描与年度调制 | **尚未完成** | 当前有截断 SHM 基准和 untruncated MB 尾部诊断 | 尚未进行完整 \(v_0,v_E,v_{\rm esc}\) 系统扫描或年度调制 |
| LZ 2026 一维效率折叠 | **部分验证** | 2.84 tonne-year、5.4–269.9 keV ROI；分段线性乘积解析积分；稠密梯形交叉检查 | 仅 rate-level yield；没有二维信号 PDF、NEST nuisance、背景 likelihood |
| LZ 二维 detector likelihood / profile likelihood | **尚未完成** | 已有一维 efficiency 输入和 rate-level output | 尚无完整 \(S1_c\)–\(\log_{10}S2_c\) response、背景 PDF 与 nuisance covariance |

## 5. 数据完整性与文档一致性

| 子任务 | 当前状态 | 已有证据 | 尚存边界 |
|---|---|---|---|
| Figure 2 结果总索引 | **已验证（PR #46 分支；待合并 main）** | [当前机器可读总清单](three_body_results_master_index_2026-11-16.json)：13 组、98 个顶层文件条目，含 SHA-256、大小、参数和用途 | 97 个组内引用对应 96 个唯一文件路径；另有 2 个未归组 manuscript 文件；外部高阶 ZIP 仍为 checksum-only |
| AFH response sample SHA-256 | **已验证（当前 main 归档）** | 历史 28 点 sample digest 与 exact-q 归档仍可复现；完整 16,807 行七同位素 response grid 已提交并有 SHA-256 manifest；84 点 AFH-7/Hybrid-9 谱已归档 | 外部高阶 ZIP 未提交完整内容；不把 AFH-7 描述为 AFH-9 |
| 原始论文 AFH response 公式 | **已修正** | `paper-source/main.tex` 改为 factor 4 physical mapping 和 exact spatial \(q\)；`paper-source/SHA256SUMS` 同步 | 合并后仍需在正式 Overleaf / PDF 构建中检查排版 |
| 主报告—附录 A–H—代码公式索引 | **部分验证** | F1–F12 公式索引、主报告、附录 A–H、代码入口和结果路径已交叉检查 | 仍需按最终固定的 Dirac/Majorana 模型约定做一轮完整 UV 层复核 |
| 完整 Eq. (6) 截面对照程序 | **已提交，尚未运行** | 新增 run_afh_eq6_full_dsigma.wls、compare_full_dsigma_mathematica.py、主报告附录 H 与附录 A.8 | 没有 Wolfram 运行产物和逐点 comparison CSV；不把脚本存在或 CI 通过等同于物理结果验证 |

## 6. 不得混淆的四组结果

1. **AFH Xe-131 核响应**：只描述核结构 \(R_A(Q)\)，不是散射截面。
2. **四组 \(v=800\) km/s 固定速度曲线**：用于 Figure 2 核响应替换诊断；该速度高于截断 SHM 的 \(776\) km/s。
3. **450 keV pointwise \(L_{00}\)** 与 **450 keV fixed-speed \(d\sigma/dE_R\)**：前者是单点 Dirac trace / \(I_6\) 检查，后者是整条固定速度曲线，求积、核模型和宽度约定并不相同。
4. **GCN/JJ55 连续天然氙谱与 LZ 一维效率折叠**：GCN/JJ55 84 点谱仍使用 legacy linear-\(W^2\) 积分；rate-level yields 不能标记为 AFH 预测。AFH-7/Hybrid-9 的 84 点谱另有独立归档，但两条链的相空间积分尚未统一。

## 7. 下一阶段的关闭条件

- **P0 关闭条件：** 总索引中的每个已提交输入/输出都有 64 位 SHA-256；外部输入和缺失文件明确标注 checksum-only / missing；每个 benchmark 都能追溯到参数和结果。
- **P1 关闭条件：** 原始拉格朗日量、主报告、附录 A–G、代码和单位约定无未解释的符号冲突；Dirac/Majorana 与宽度模型的边界由物理输入明确固定。
- **P2 关闭条件：** 每个科学结论都有状态、证据、输入缺口和适用范围；任何 selected-point、fixed-speed 或 rate-level 结果都不被表述为更高层的完整验证。

当前 PR #46 分支的 Figure 2 总索引为 13 组、98 个顶层文件条目；97 个组内引用对应 96 个唯一文件路径，另有 2 个未归组 manuscript 文件。AFH-7 七同位素 response grid 和 84 点谱已归档；原生 Mathematica/Python 完整 Xe-131 fixed-speed Eq. (6) 对照已 PASS。剩余开放项为 GCN/JJ55 threshold-\(u^2\) 匹配重算、近极点宽度处方系统比较、AFH-9 缺失同位素输入，以及官方 LZ detector likelihood。


## 8. 2026-11-14 comparator correction and final CI confirmation

The first archive comparison failed only for the derived residual `relative_to_archived = I_6/I_6^{\\rm archive}-1`. Since this residual is close to zero, applying a relative tolerance to it was ill-conditioned: small upstream differences in `I_6` were magnified in the residual comparison even though the physical integral column satisfied its original tolerance. PR #34 changed only this comparator branch to `rel_tol=0, abs_tol=5e-8`; all other numerical columns retain `rel_tol=5e-8, abs_tol=1e-12`. No physical calculation, historical input, or archived output was changed.

The corrected workflow passed in [run 43581233498](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43581233498): 13/13 Eq. (6) kernel tests, 9/9 phase-space tests, benchmark/threshold/historical-800/off-shell near-pole scans, artifact preservation, and row-by-row comparison with committed phase-space CSV archives. The AFH-7/Hybrid-9 84-point threshold-\(u^2\) grid and its high-order summary were added later; GCN/JJ55 still use the legacy linear-\(W^2\) kernel. Neither this CI run nor the AFH grid closes near-pole width-prescription systematics or the full Mathematica–Python (d\sigma_A/dE_R) comparison.


## 6. 2026-11-18 addendum — full VV nucleon current and AFH non-\(M\) responses

| Work item | Status | Evidence / interpretation | Required next check |
|---|---|---|---|
| AFH \(M\) charge response | **ARCHIVED / VALIDATED WITHIN SCOPE** | Seven-isotope 16,807-row grid, zero-momentum normalization and factor-four mapping remain unchanged | Preserve as leading-charge baseline; do not relabel rank-2 \(M\) multipoles as \(\Phi''\) |
| Full DM-side \(L^{\mu\nu}\) | **REPRODUCIBLE DIAGNOSTIC IN PR #53** | Exact-source workflow: 8/8 tests, 12-row reproduction, archived/regenerated maximum relative difference 0 | This is not an internal nuclear-current calculation; merge status of PR #53 remains separate |
| Coherent point-charge-current contraction | **REPRODUCIBLE DIAGNOSTIC IN PR #53** | About 4.3–5.1 ppm relative to charge-only in the scanned fixed-speed Xe-131 points | It constrains nuclear centre-of-mass convection only; it does not bound internal \(\Delta,\Sigma'\), or \(\Phi''\) |
| Nucleon Dirac–Pauli \(F_1/F_2\) | **ANALYTIC STRUCTURE DOCUMENTED** | Appendix I.3–I.4 fixes \(q_A=p_N'-p_N\), the Pauli sign, and \(F_1+2F_2\)/\(F_1+F_2\) combinations; adopted \(F_2^V(0)=-0.552\) | Reconcile HKS 2015 compact notation with explicit 2017 flavor-separated input; provide finite-\(t_A\) form factors and covariance |
| \(\Sigma'\) AFH response | **PREVIOUS SELECTED-\(q\) TABLE WITHDRAWN** | Earlier Python source translation used an unvalidated operator mapping | Native AFH index-3 export and pointwise comparison required |
| \(\Delta\), \(W_{\Sigma'\Delta}\) | **MAPPING CORRECTED; NATIVE PENDING** | DeltaJ uses same-rank MJLDivQ; the former parity-conflict diagnosis is withdrawn | Native AFH index-6/index-8 export and pointwise comparison required |
| Xe-131 \(M,\Phi'',M\Phi''\) | **NATIVE RESPONSE ARCHIVED; VALIDATOR PASS** | PR #51 commits 2,401-node Wolfram 14.2.0 CSV, source/input metadata, Python validation JSON and SHA-256 manifest | Response-level only; no three-body Wilson-coefficient contraction or rate-level correction is established |
| Full \(L^{\mu\nu}W_A^{\alpha\beta}\) and natural-xenon VV spectrum | **NOT COMPLETE** | No current implementation combines the full DM tensor with matched internal nucleon currents and AFH multipoles | Complete one-body matching, phase-space-dependent contraction, separate convergence audits, then isotope/halo fold |

The status distinction is deliberate: a small dark-matter spatial-current norm or a ppm-level point-nucleus correction is not a bound on internal nuclear responses. The withdrawn \(\Sigma'\) ratios are not evidence and must not be used as cross-section percentages. The \(F_2^V(0)=-0.552\) value is a selected central-value input, not a finite-\(t_A\) prediction; its common strange-moment uncertainty and the HKS 2015 notation discrepancy remain explicit matching tasks. The current three-body result must continue to be labelled a leading-\(M\) benchmark until the complete one-body current contraction has been carried out.
