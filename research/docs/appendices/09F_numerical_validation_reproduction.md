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
| q convention audit | research/afh_default_density_xe131/audit_response_momentum_conventions.py | 对照论文响应 q、精确运动学 q 和 Xe-131 的响应差异 |
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
  -s research/afh_default_density_xe131 \
  -p 'test_*.py' -v
~~~

若只运行 AFH 响应本身的六项测试，将匹配模式改为 test_afh_default_xe131.py。

AFH mpmath 全网格独立验证：

~~~bash
python research/afh_default_density_xe131/verify_afh_mpmath_full_grid.py \
  --response-csv research/afh_default_density_xe131/output/afh_default_xe131_WM00.csv \
  --outdir research/afh_default_density_xe131/output/mpmath_full_grid
~~~

q 约定审计（需要一份新生成的 AFH Xe-131 响应 CSV）：

~~~bash
python research/afh_default_density_xe131/audit_response_momentum_conventions.py \
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
| AFH 67 项密度矩阵解析 | 已完成 | 官方源解析、CSV 逐项核对、67 项计数 | 原生 Mathematica 全网格输出比较 |
| AFH 默认 \(b_A\) | 已完成 | 公式、单位转换、Xe-131 数值回归测试 | 不需要拟合；不得用谷值调参 |
| AFH 零动量归一化 | 已完成（含有限精度修正） | 原始 \(A^2/4\)、物理响应 \(A^2\)、偏差 \(8.2523\times10^{-5}\) | 记录 AFH 空间 q 的精确质量壳关系，并区分 NR 近似 |
| AFH 谷值 | 已完成 | 离散候选点、直接响应局部极小化、minima.csv | 不需要调整 \(b_A\) |
| mpmath 独立有限和 | 已完成全网格 | 60 位精度、2401 个 q 节点；最大振幅绝对差 \(3.98\times10^{-14}\)，最大响应绝对差除以 \(A^2\) 为 \(1.22\times10^{-15}\) | 原生 Mathematica 逐点对照仍待完成 |
| AFH 原生 Mathematica | 待完成 | WLS runner 和比较脚本已归档；Python/mPMath 全网格交叉验证已通过 | 实际运行 Wolfram kernel 并保存逐点差异 |
| GCN/JJ55 对照 | 已完成归档 | 三种响应、四 benchmark、1920 行 long table | 对照共享既有 \(I_6\)，不是 640 次独立重算 |
| 三体运动学/Dirac trace | 已完成代表性检查 | 壳条件、四动量闭合、显式自旋求和、干涉分解 | 扩展到更宽的参数和质量网格 |
| 三体积分收敛 | 已有 selected-point 验证 | 六个天然氙点 \(8×8×4\) 对 \(16×16×8\)，最大差异 \(2.19×10^{-4}\)；独立 Eq. (6) 测试点 \(16×16×8\) 对 \(32×32×16\)，相对差异小于 \(5×10^{-5}\) | 连续反冲谱全网格收敛 |
| 天然氙速度积分 | 已有 selected-point 验证（exact spatial q） | 五个点 32 对 64 速度节点，最大差异 \(3.31×10^{-6}\)；98 个逐同位素贡献和 14 个总速率在 exact_spatial 默认模式下复现，最大总速率差异 \(2.67×10^{-12}\)，CI run 43044583357 | 连续谱和 halo 参数扫描 |
| AFH 空间 q 与 NR 近似 | 已完成审计与代码保护 | 28 个天然氙样本匹配 exact spatial q；Xe-131 四点 NR 近似响应差异约 5.5–225 ppm；halo fold CI run 43044583357 通过 | 连续反冲谱需要完整七同位素 AFH 响应网格 |
| Xe-124/Xe-126 | 输入缺失 | 缺失丰度合计 0.001842 | 取得密度矩阵并补算响应、阈值和速率 |
| LZ detector response | 尚未开展 | 当前仅有理论核反冲率 | 效率、能量分辨、曝光、选择切、背景和统计似然 |

这张表把软件测试、局部数值收敛和物理模型完整性分开。测试通过只说明被测试的代码路径满足相应断言，不等于所有参数点、所有核模型、halo 假设或实验响应都已验证。

## F.5 LZ detector-level 分析还缺少什么

当前输出是理论核反冲能量 \(E_R\) 上的

\[
\frac{dR}{dE_R}
\]

，单位 events/(kg day keV)。它尚不能直接与 LZ 的观测事件分布或似然比较。

至少还需要：

1. 核反冲到观测量的响应模型，例如 S1/S2 或分析采用的重建能量变量；
2. 能量相关的信号接受效率和选择切；
3. 能量分辨函数，将真实 \(E_R\) 卷积到观测变量；
4. 实际有效曝光和数据质量区间；
5. 分析区域内的背景模型及其不确定度；
6. 与指定 LZ 数据集一致的信号/背景 likelihood。

因此当前天然氙结果应称为 **pre-detector theoretical rate**，不能称为完整 LZ recast、实验排除或对某个候选事件的统计解释。

## F.6 历史数据和版本管理原则

1. 保留官方 AFH ZIP 与源文件 SHA-256。
2. 保留原始 67 项密度矩阵，不通过改写系数或 \(b_A\) 修正谷值。
3. 保留 AFH raw response 与物理 equal-\(p,n\) response 两列，因子 4 只应用一次。
4. 早期错误的 AFH response CSV 拼接换行和 benchmark CSV 中 AFH 列误复制 GCN 的版本应标记为 superseded；当前使用 corrected archive。
5. 任何新的 \(q_{\rm resp}\)、核质量、halo 参数、宽度方案或求积阶数都应产生新的输出和 metadata，不覆盖历史结果。
6. 主报告包含完整附录 A–F；本目录中的六份独立附录与主报告对应章节保持同步。
7. 程序、CSV、JSON 和源文件继续保存在各自计算目录，文档只解释其定义、来源、调用方式和验证边界。

