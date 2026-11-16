> 所属主报告：[AFH v6.0 氙核响应与三体暗物质散射](../09_afh_xe131_three_body_scattering_natural_xenon.md)

# 附录 F：计算程序、数据文件、收敛验收和复现命令

## F.1 计算链和程序入口

本研究的数值链为

\[
\boxed{
\text{三体振幅}
\longrightarrow I_6
\longrightarrow R_A(E_R)
\longrightarrow \frac{d\sigma_A}{dE_R}
\longrightarrow \sum_A x_A
\longrightarrow \frac{dR}{dE_R}
}.
\]

各环节对应的主要程序如下：

| 任务 | 主要程序/目录 | 作用 |
|---|---|---|
| Eq. (6) 三体 kernel | research/figure2_full_reproduction/eq6_kernel.py | 构造末态四动量、Dirac trace、\(I_6\) |
| AFH Xe-131 响应 | research/afh_default_density_xe131/run_afh_default_xe131.py | 解析密度矩阵并计算 \(W_M^{00}\) |
| AFH Xe-131 Mathematica runner | research/afh_default_density_xe131/run_afh_default_xe131.wls | 调用官方 AFH 包生成原生响应 |
| AFH mpmath full-grid validation | research/afh_default_density_xe131/verify_afh_mpmath_full_grid.py | 独立 60 位精度有限和对照全部 2401 个 q 节点 |
| q convention audit | research/afh_default_density_xe131/audit/audit_response_momentum_conventions.py | 对照论文响应 q、精确运动学 q 和 Xe-131 的响应差异 |
| Mathematica/Python 对照 | research/afh_default_density_xe131/verify_afh_xe131_native.wls | 原生 AFH 与 Python 网格比较 |
| 四 benchmark 响应替换 | research/afh_default_density_xe131/recompute_afh_four_benchmarks.py | AFH/GCN/JJ55 同网格截面对照 |
| 四 benchmark 截面重构 | research/afh_default_density_xe131/compute_four_benchmark_dsigma.py | 从 \(R_A,I_6\) 重构 Eq. (6) 截面 |
| 天然氙 halo fold | research/afh_default_density_natural_xenon_halo/run_afh_natural_xenon_halo_fold.py | 逐同位素速度积分和丰度加权 |

## F.2 关键输入和结果文件

### AFH Xe-131

- afh_default_xe131_density_matrix.csv：67 项官方内置矩阵提取结果；
- output/afh_default_xe131_WM00.csv：2401 点响应网格；
- output/minima.csv：细化极小值；
- output/figure2_dip_check.csv：101、267、542 keV 参考点；
- output/metadata.json：源文件哈希、质量、\(b_A\)、归一化和限制；
- output/mpmath_full_grid_summary.json：2401 点、60 位精度 mpmath 全网格验证汇总；
- CI artifact afh-xe131-mpmath-full-grid-validation：完整逐点比较 CSV 和 JSON summary。
- AFH_DEFAULT_XE131_NORMALIZATION_AUDIT.md：来源和归一化审计；
- AFH_COUPLING_NORMALIZATION_MAPPING.md：接口耦合映射。

### 四 benchmark 截面对照

- output/figure2_four_benchmarks_AFH_GCN_JJ55_corrected.csv；
- output/figure2_four_benchmarks_AFH_GCN_JJ55_wide_audit.csv；
- FOUR_BENCHMARK_CROSS_SECTION_AUDIT.md。

四组 benchmark 各有 160 个反冲能量点；三种核响应模型共形成 1920 行 long table 和 640 行 wide table。该对照固定同一组 \(I_6(E_R)\) 网格，只替换 \(R_A(E_R)\) 并重新计算 Eq. (6) 的截面前因子。因此它是受控的核响应替换比较，**不是重新独立计算 4×160 个三体积分**。该脚本采用固定 \(v=800\) km/s；这一速度高于截断 SHM 的 776 km/s 端点，所以这组结果是固定速度截面诊断，不能直接当作截断 SHM 支持区间内的 halo 事件率。

### 天然氙 halo fold

- input/natural_xenon_isotope_weights.csv；
- input/afh_response_samples.csv；
- results/isotope_halo_contributions_compact.csv；
- results/natural_xenon_halo_rates.csv；
- results/vmin_by_isotope_at_101keV.csv；
- results/kernel_order_crosschecks.csv；
- results/speed_quadrature_crosschecks.csv；
- results/halo_pdf_normalization.csv；
- results/metadata.json；
- results/natural_xenon_q_convention_audit.csv；
- results/xe131_afh_response_shift_NR_vs_exact.csv；
- results/q_convention_audit_summary.json；
- results/legacy_exact_reproduction_comparison.json（98 个同位素贡献和 14 个总速率的回归复现对照）。

当前 response samples 文件包含 7 种可用同位素在 4 个选定反冲能量上的 28 个响应样本。halo fold 对 14 组 benchmark/反冲能量/halo 组合分别输出 7 个同位素贡献，共 98 行逐同位素结果。

## F.3 复现命令

从仓库根目录执行。

AFH Xe-131 Python 响应：

~~~bash
python research/afh_default_density_xe131/run_afh_default_xe131.py \
  --outdir research/afh_default_density_xe131/output
~~~

AFH Xe-131 回归测试：

~~~bash
python -m unittest discover \
  -s research/afh_default_density_xe131/tests \
  -p 'test_*.py' -v
~~~

若只运行 AFH 响应本身的测试，将匹配模式改为 test_afh_default_xe131.py。

AFH mpmath 全网格独立验证：

~~~bash
python research/afh_default_density_xe131/verify_afh_mpmath_full_grid.py \
  --response-csv research/afh_default_density_xe131/output/afh_default_xe131_WM00.csv \
  --outdir research/afh_default_density_xe131/output/mpmath_full_grid
~~~

q 约定审计（需要一份新生成的 AFH Xe-131 响应 CSV）：

~~~bash
python research/afh_default_density_xe131/audit/audit_response_momentum_conventions.py \
  --xe131-response-csv research/afh_default_density_xe131/output/afh_default_xe131_WM00.csv \
  --outdir research/afh_default_density_xe131/output/q_convention_audit
~~~

AFH 原生 Mathematica 运行需要官方 dmformfactor-V6.m 和可用的 Wolfram kernel。设置环境变量 DMFormFactorPath 指向该源文件，再运行：

~~~bash
wolframscript -file research/afh_default_density_xe131/run_afh_default_xe131.wls
~~~

独立原生验证脚本还需要设置 AFHPythonCSV 和 AFHAuditDir：

~~~bash
wolframscript -file research/afh_default_density_xe131/verify_afh_xe131_native.wls
~~~

天然氙 selected-point halo fold：

~~~bash
python research/afh_default_density_natural_xenon_halo/run_afh_natural_xenon_halo_fold.py
python research/afh_default_density_natural_xenon_halo/validate_archived_results.py
~~~

默认 exact_spatial 使用 AFH 定义的空间动量转移 (q=\sqrt{2m_AE_R+E_R^2})，与精确核质量壳关系一致。nr_approx 是 (q=\sqrt{2m_AE_R}) 的小反冲近似；当前 28 个响应样本不采用该近似，因此程序会拒绝将其与 exact-q 样本混用。legacy_exact 仍是 exact_spatial 的向后兼容别名。

Eq. (6) kernel 测试：

~~~bash
python -m unittest discover \
  -s research/figure2_full_reproduction/tests -v
~~~

四 benchmark 截面对照脚本需要归档的 GCN/JJ55 基础 CSV 和 AFH response CSV。当前归档输入的调用形式为：

~~~bash
python research/afh_default_density_xe131/recompute_afh_four_benchmarks.py \
  --base-csv research/afh_default_density_xe131/input/figure2_recalc_mV10_g2_1_v800_Xe131_full_5keV.csv \
  --afh-response-csv research/afh_default_density_xe131/output/afh_default_xe131_WM00.csv \
  --outdir research/afh_default_density_xe131/output
~~~

调用时必须保存输入文件、输出 CSV 和 metadata，不能只保留最终图像。

## F.4 数值验收矩阵

| 验证项目 | 当前状态 | 已有证据 | 尚未完成的部分 |
|---|---|---|---|
| AFH 67 项密度矩阵解析 | 已完成 | 官方源解析、CSV 逐项核对、67 项计数；对应七同位素 source matrices 已归档 | 无；Xe-124/Xe-126 不属于官方 default dispatch |
| AFH 默认 \(b_A\) | 已完成 | 公式、单位转换、Xe-131 数值回归测试 | 不需要拟合；不得用谷值调参 |
| AFH 零动量归一化 | 已完成（含有限精度修正） | 原始 \(A^2/4\)、物理响应 \(A^2\)、偏差 \(8.2523\times10^{-5}\) | 记录 AFH 空间 q 的精确质量壳关系，并区分 NR 近似 |
| AFH 谷值 | 已完成 | 离散候选点、直接响应局部极小化、minima.csv | 不需要调整 \(b_A\) |
| mpmath 独立有限和 | 已完成全网格 | 60 位精度、2401 个 q 节点；最大振幅绝对差 \\(3.98\\times10^{-14}\\)，最大响应绝对差除以 \\(A^2\\) 为 \\(1.22\\times10^{-15}\\) | 无；原生 Mathematica 对照另有独立 PASS 记录 |
| AFH 原生 Mathematica | 已完成（限定 Xe-131 response-level） | Wolfram 14.0.0 原生执行；2401 个 q 节点；四种响应量与 Python 逐点比较通过，最大相对差异 \\(3.59\\times10^{-9}\\)；SHA-256 manifest 已归档 | 不验证完整 Eq. (6) pole-width \\(I_6\\) 或 \\(d\\sigma_A/dE_R\\)；后者的端到端 Mathematica/Python 对照仍待完成 |
| GCN/JJ55 对照 | 已完成归档 | 三种响应、四 benchmark、1920 行 long table | 对照共享既有 \(I_6\)，不是 640 次独立重算 |
| 三体运动学/Dirac trace | 已完成代表性检查 | 壳条件、四动量闭合、显式自旋求和、干涉分解 | 扩展到更宽的参数和质量网格 |
| 450 keV pointwise \(\mathcal L_{00}\)/\(I_6\) benchmark | 已完成本地验收 | 六项 regression tests、显式自旋求和、四动量闭合、三阶求积对照；见 local validation record | 仅覆盖指定诊断运动学点；pole width 依赖 Dirac / pure-scalar / single-channel 假设 |
| 450 keV Xe-131 fixed-speed curve | 已归档的内部网格诊断 | 105 点 130–650 keV、独立 PCHIP 重构、Eq. (6) anchor convergence、运动学端点 bracket | 109.150–654.956 keV 两端尚未完成高阶积分；固定速度、A×u 质量近似、zero width，不是 halo rate |
| 三体积分收敛 | 部分验证（按计算路径分层） | AFH-7/Hybrid-9 84 点 grid：baseline \\(24\\times6\\times6\\times3\\) 到 high-order \\(24\\times8\\times8\\times4\\) 的最大谱差异 \\(6.46772\\times10^{-6}\\)；12-speed-node kernel 到 24-speed-node high-order kernel 的最大差异 \\(6.63746\\times10^{-6}\\)；24-speed-node 内部阶数增量 \\(5.96430\\times10^{-10}\\) | GCN/JJ55 仍为 legacy linear-\\(W^2\\)、\\(8\\times8\\times4\\)；\\(16\\times16\\times8\\) spot-check 最大差异 \\(2.18895\\times10^{-4}\\)；需统一 threshold-\\(u^2\\) 重算；近极点宽度处方系统比较仍开放 |
| 天然氙速度积分 | 部分验证（按计算路径分层） | 历史 selected-point fold 的 32/64 节点检查最大差异 \\(3.31\\times10^{-6}\\)，98 个逐同位素贡献和 14 个总速率复现最大总速率差异 \\(2.67\\times10^{-12}\\)；AFH-7 grid 的速度 12→24 节点最大差异 \\(6.63735\\times10^{-6}\\)，最差 32 点 24→48 节点最大差异 \\(2.21749\\times10^{-7}\\) | GCN/JJ55 匹配 threshold-\\(u^2\\) 后需重新执行全网格速度收敛；halo 参数扫描和年度调制未完成 |
| AFH 空间 q 与 NR 近似 | 已完成（输入/响应层） | 28 个历史天然氙样本匹配 exact spatial q；七同位素 AFH response grid 16,807 行已提交并逐同位素 direct finite-sum at exact q；Xe-131 四点 NR 近似响应差异约 5.5–225 ppm | Xe-124/Xe-126 仍缺 AFH matrices；不得把 AFH-7 或 Hybrid-9 称为 AFH-9 |
| Xe-124/Xe-126 | 输入缺失 | 缺失丰度合计 0.001842 | 取得密度矩阵并补算响应、阈值和速率 |
| 天然氙全范围反冲谱 | 部分完成（按核模型区分） | AFH-7/Hybrid-9：四 benchmark、84 点、1,344 baseline rows、5–800 keV、threshold-\\(u^2\\)；高阶摘要最大 baseline-to-final 谱差异 \\(6.46772\\times10^{-6}\\)。GCN/JJ55 也有四组 84 点谱 | GCN/JJ55 仍为 legacy linear-\\(W^2\\)、\\(8\\times8\\times4\\)，尚未匹配 AFH-7 求积；AFH-9 缺 Xe-124/Xe-126 matrices；高阶 AFH ZIP 仅外部 checksum |
| LZ efficiency-weighted rate-level fold | 部分完成（仅 GCN/JJ55 rate-level） | Fig. S2 一维效率曲线及灰色包络；2.84 tonne-year；四组 benchmark 事件数；解析分段积分与稠密梯形对照 | 现有事件数只对应 GCN/JJ55；AFH-7/Hybrid-9 84 点谱尚未折叠到本表；NEST 二维响应、能量分辨/重建、nuisance covariance、背景样本和 profile likelihood 未完成 |

这张表把软件测试、局部数值收敛和物理模型完整性分开。测试通过只说明被测试的代码路径满足相应断言，不等于所有参数点、所有核模型、halo 假设或实验响应都已验证。

## F.5 LZ detector-response interface：已完成部分与剩余工作

当前已经超出单纯的 pre-detector theoretical rate，但仍未达到完整 detector-level recast。已完成的第一层接口包括：

1. 从 LZ 2026 Fig. S2 的官方 PDF 矢量路径提取 final-ROI 一维 central efficiency 曲线及灰色上下包络，并保存 CSV、SVG 和提取 metadata；
2. 在 248 keV 处与独立数字化结果对照；灰色包络作为 detector-systematic range 使用，不赋予置信水平；
3. 使用公开的名义曝光 \(2.84\ {\rm tonne\,year}=1.03731\times10^6\ {\rm kg\,day}\)；
4. 将该效率曲线与 GCN/JJ55 连续天然氙谱在 \(5.4\le E_R\le269.9\) keV 内折叠，得到四组 benchmark 的 preliminary rate-level expected event yields；
5. 对分段线性谱与分段线性效率的乘积执行区间解析积分，并以稠密梯形积分交叉检查。

这组事件数**只对应 GCN/JJ55 连续核响应谱**。AFH-7/Hybrid-9 的 84 点全范围 pre-detector spectra 已归档，但尚未折叠到本节的效率加权事件数表；因此不能把现有 GCN/JJ55 的连续谱折叠结果标记为 AFH 预测。效率曲线的机器可读 HEPData 端点当前受到 HTTP 403 challenge；归档数据来自官方 PDF 的可复现矢量提取，而不是声称下载到了 HEPData 原始 YAML/JSON 表。

完整 detector-level recast 仍至少需要：

1. tuned NEST v2.4.5 的联合 \(S1_c\)–\(\log_{10}S2_c\) 响应分布、相关性和能量重建/分辨模型；
2. 效率与探测器响应的校准 nuisance parameters 及其 covariance；当前 Fig. S2 灰色包络不是完整协方差矩阵，也不是置信区间；
3. 与该 LZ 数据集对应的 science、prompt-veto、delayed-veto 数据样本及背景约束；
4. 由所选核模型自己的 recoil spectrum 构造二维信号 PDF；AFH-7/Hybrid-9 已可提供 pre-detector 84 点 grid-sampled spectrum，但 AFH-9 仍缺 Xe-124/Xe-126 输入，且二维 NEST/likelihood 尚未建立；
5. LZ profile likelihood、系统误差参数化及信号/背景联合统计处理。

因此，当前结果应称为 **efficiency-weighted rate-level event-yield estimate**，而不是完整 LZ recast、90% CL 排除或对 248 keV 候选事件的统计解释。LZ 论文中的两体 \(\chi_1+A\to\chi_2+A\) 限制也不能直接移植到本研究的三体 \(\chi_1+A\to\chi_1+A+s\) 过程。

## F.6 历史数据和版本管理原则

1. 保留官方 AFH ZIP 与源文件 SHA-256。
2. 保留原始 67 项密度矩阵，不通过改写系数或 \(b_A\) 修正谷值。
3. 保留 AFH raw response 与物理 equal-\(p,n\) response 两列，因子 4 只应用一次。
4. 早期错误的 AFH response CSV 拼接换行和 benchmark CSV 中 AFH 列误复制 GCN 的版本应标记为 superseded；当前使用 corrected archive。
5. 任何新的 \(q_{\rm resp}\)、核质量、halo 参数、宽度方案或求积阶数都应产生新的输出和 metadata，不覆盖历史结果。
6. 主报告包含正式附录 A–H；独立附录文档和补充说明应与主报告对应章节保持同步。
7. 程序、CSV、JSON 和源文件继续保存在各自计算目录，文档只解释其定义、来源、调用方式和验证边界。
## F.7 450 keV supplied benchmark：复现与适用边界

本节记录两个独立的 450 keV benchmark。它们共享粒子质量点，但并不共享全部运动学、核响应或传播子处方。

本节所列 native outputs 与 validation records 均已归档在 main。这里的 main-branch 状态只说明文件归档位置，不扩大各 benchmark 的物理适用范围。

### F.7.1 Pointwise \(\mathcal L_{00}\) 与 reduced \(I_6\)

输入为 \(g_1=g_2=g_{VN}=1\)、\(m_{\chi_1}=1\) TeV、\(\Delta m=450\) keV、\(m_s=300\) keV、\(m_V=10\) GeV。点态运动学为显式指定的诊断点：\(m_A=122\) GeV、\(E_R=200\) keV、\(v=776\) km/s、\(W^2\) midpoint、\(z=0.2\)、\(\phi_*=1.1\)。这不是由 supplied particle benchmark 唯一确定的运动学点。

从仓库根目录复现：

~~~bash
python research/figure2_full_reproduction/run_user_l00_benchmark.py \
  --nw 48 --nz 40 --nphi 24 \
  --output /tmp/USER_L00_BENCHMARK_450KEV_48x40x24.json
python -m unittest discover \
  -s research/figure2_full_reproduction/tests \
  -p test_user_l00_benchmark.py -v
~~~

本地验收记录位于：

- research/figure2_full_reproduction/research/figure2_full_reproduction/results/USER_L00_BENCHMARK_450KEV_LOCAL_2026-11-13/LOCAL_VALIDATION_2026-11-13.md；
- 同目录的 JSON、quadrature convergence CSV、run manifest、validation log 和 SHA256SUMS。

该结果比较 zero-width 与条件性 pole-width；后者只在 Dirac 费米子、实标量、纯 scalar off-diagonal Yukawa 且仅 \(\chi_2\to\chi_1s\) 通道开放的假设下成立。它不是完整 vector-plus-scalar self-energy，也不是 halo-folded 或 detector-level prediction。该本地验收没有使用 GitHub Actions；不能将未运行的 CI 描述为通过。

### F.7.2 Fixed-speed Xe-131 \(d\sigma/dE_R\) 曲线

该曲线采用 \(v=776\) km/s、\(m_A=131u\)、GCN/JJ55 response tables 和 zero-width prescription，扫描 130–650 keV 共 105 个内部点。它与 F.7.1 的 \(m_A=122\) GeV 点态 trace benchmark 不是同一核质量或传播子宽度方案。

从仓库根目录复现：

~~~bash
python research/figure2_full_reproduction/run_user_dsigma_curve.py \
  --step-keV 5 --nw 20 --nz 16 --nphi 12 \
  --output /tmp/xe131_dsigma_450kev.csv
python research/figure2_full_reproduction/plot_user_dsigma_curve.py
python -m unittest discover \
  -s research/figure2_full_reproduction/tests \
  -p test_user_dsigma_curve.py -v
~~~

结果与 provenance：

- research/figure2_full_reproduction/results/fixed_speed_xe131_dsigma_450kev.csv；
- research/figure2_full_reproduction/results/local_minima_refinement_1keV.csv；
- research/figure2_full_reproduction/results/kernel_quadrature_convergence_450kev.csv；
- research/figure2_full_reproduction/results/metadata_user_dsigma_450kev.json；
- research/figure2_full_reproduction/results/USER_DSIGMA_CURVE_450KEV_LOCAL_2026-11-13.md；
- research/figure2_full_reproduction/results/SHA256SUMS_user_dsigma_450kev.txt；
- research/figure2_full_reproduction/results/plots/fixed_speed_xe131_dsigma_450kev.svg；
- research/figure2_full_reproduction/results/plots/xe131_gcn_jj55_response_ratio_450kev.svg。

开放反冲区间约为 109.150286–654.955583 keV；当前曲线只覆盖 130–650 keV。两端的 kinematic bracket tests 不等于端点附近的高阶积分收敛，故当前归档只能称为内部网格 fixed-speed diagnostic。它不是天然氙 halo-folded spectrum、事件率、LZ detector-level prediction 或 exclusion。

### F.7.3 两项 benchmark 的不可互换性

| 项目 | Pointwise L00 benchmark | Fixed-speed Xe-131 curve |
|---|---|---|
| 核质量 | 122 GeV 诊断近似 | 131 u 质量近似 |
| 运动学 | 单一点：200 keV、776 km/s、指定角变量 | 105 个反冲能量点、固定 776 km/s |
| 核响应 | 点态 \(\mathcal L_{00}\)/\(I_6\)，不构成完整核响应谱 | GCN/JJ55 响应表 |
| 宽度 | zero-width 与条件性 scalar pole-width 对照 | zero width |
| 输出层级 | pointwise trace 与 reduced integral | 单同位素固定速度 \(d\sigma/dE_R\) |
| 不能声称 | 完整自能、halo rate、LZ 预测 | 完整开放区间、halo rate、detector likelihood |



