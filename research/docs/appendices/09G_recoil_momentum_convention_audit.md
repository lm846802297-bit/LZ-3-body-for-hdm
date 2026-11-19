> 所属主报告：[AFH v6.0 氙核响应与三体暗物质散射](../09_afh_xe131_three_body_scattering_natural_xenon.md)

# 附录 G：AFH 空间动量转移与非相对论反冲近似

## G.1 AFH 响应函数中的 \(q\) 是什么？

AFH 原始文献定义谐振子变量

\[
y=\left(\frac{qb_A}{2}\right)^2,
\]

其中 \(q=|\mathbf q|\) 是**空间动量转移的大小**。AFH 的核响应 \(W_M(y)\) 是这个空间动量变量的函数，而不是直接以洛伦兹不变量 \(t\) 为自变量。

参考：Fitzpatrick et al., *Model-independent WIMP Scattering Responses and Event Rates*, JCAP 02 (2013) 004, arXiv:1203.3542, Secs. 4 and 7.

## G.2 精确质量壳关系与常见 NR 近似

靶核初态静止：

\[
P^\mu=(m_A,\mathbf 0).
\]

反冲后的核满足

\[
P'^\mu=(m_A+E_R,\mathbf q),\qquad P'^2=P^2=m_A^2.
\]

因此

\[
(m_A+E_R)^2-|\mathbf q|^2=m_A^2,
\]

从而得到精确的空间反冲动量

\[
\boxed{q_{\rm exact}=\sqrt{2m_AE_R+E_R^2}}.
\]

代入 AFH 变量：

\[
\boxed{
y_{\rm exact}
=\frac{b_A^2}{4}(2m_AE_R+E_R^2)
}.
\]

在 \(E_R\ll m_A\) 时，忽略 \(E_R^2\) 项，才得到常用近似

\[
q_{\rm NR}=\sqrt{2m_AE_R},\qquad
y_{\rm NR}=\frac{b_A^2m_AE_R}{2}.
\]

所以两种表达的关系是：

| 量 | 精确三体计算 | 非相对论反冲近似 |
|---|---|---|
| 空间动量 | \(\sqrt{2m_AE_R+E_R^2}\) | \(\sqrt{2m_AE_R}\) |
| AFH 变量 | \(b_A^2(2m_AE_R+E_R^2)/4\) | \(b_A^2m_AE_R/2\) |
| 物理定位 | 质量壳精确关系 | \(E_R/m_A\) 展开最低阶 |

本项目的三体运动学保留精确质量壳关系，因此采用 \(q_{\rm exact}\) 作为 AFH 响应输入。\(q_{\rm NR}\) 只作为误差对照，不应被称为唯一正确的响应动量。

## G.3 28 个天然氙响应样本的约定核查

对七种有 AFH default density matrix 的氙同位素

\[
A=128,129,130,131,132,134,136
\]

及

\[
E_R=101,\ 200,\ 267,\ 542\ {\rm keV},
\]

逐点读取

research/afh_default_density_natural_xenon_halo/input/afh_response_samples.csv

并使用 NIST 原子质量减去 54 个电子质量得到核质量。28 个样本的 q_response_GeV 全部与 \(q_{\rm exact}\) 相符。

| \(E_R\) [keV] | \(q_{\rm exact}-q_{\rm NR}\) [keV] | \((q_{\rm exact}/q_{\rm NR}-1)\) [ppm] |
|---:|---:|---:|
| 101 | 0.031899–0.032882 | 0.199–0.212 |
| 200 | 0.088887–0.091626 | 0.395–0.420 |
| 267 | 0.137106–0.141332 | 0.527–0.560 |
| 542 | 0.396542–0.408764 | 1.071–1.138 |

结论：旧 28 点样本采用的是精确空间动量；这与 AFH 的 \(q\) 定义以及精确三体质量壳关系一致，不需要重新生成才能用于当前选定反冲点。

## G.4 响应曲线斜率会放大微小的动量差

虽然 \(q_{\rm exact}-q_{\rm NR}\) 只有亚 keV 量级，但 Xe-131 AFH 响应在衍射谷附近变化很快。使用新生成的 2401 点 AFH default Xe-131 响应网格做 PCHIP 插值，得到：

### NIST Xe-131 核质量

| \(E_R\) [keV] | \(q_{\rm exact}-q_{\rm NR}\) [keV] | \(R_A(q_{\rm NR})/R_A(q_{\rm exact})-1\) [ppm] |
|---:|---:|---:|
| 101 | 0.032503 | +22.346 |
| 200 | 0.090569 | +5.458 |
| 267 | 0.139702 | +212.729 |
| 542 | 0.404049 | +97.363 |

### Figure-2 固定 benchmark 质量 \(M_A=131u\)

| \(E_R\) [keV] | \(q_{\rm exact}-q_{\rm NR}\) [keV] | \(R_A(q_{\rm NR})/R_A(q_{\rm exact})-1\) [ppm] |
|---:|---:|---:|
| 101 | 0.032487 | +21.191 |
| 200 | 0.090526 | +5.478 |
| 267 | 0.139636 | +224.967 |
| 542 | 0.403857 | +89.607 |

这些差异是 NR 近似相对于精确空间动量的响应变化，不是对现有事件率施加的经验修正。固定 \(E_R\) 下，如果 \(I_6\) 和其他因子不变，微分截面的相对变化与 \(R_A\) 的相对变化相同。

## G.5 不要混淆空间 \(q^2\) 与不变量 \(-t\)

虽然 AFH 响应使用空间动量 \(q=|\mathbf q|\)，媒介子传播子使用的是四动量转移不变量：

\[
t=(P'-P)^2=E_R^2-q_{\rm exact}^2=-2m_AE_R.
\]

因此传播子分母

\[
m_V^2-t=m_V^2+2m_AE_R
\]

本身是精确的，并不意味着空间动量也必须满足 \(q^2=2m_AE_R\)。

这是本次审计最重要的区分：

- AFH 核响应：使用空间动量 \(q_{\rm exact}\)；
- 三体相空间、\(W_{\max}\)、\(v_{\min}\)：使用 \(q_{\rm exact}\)；
- 媒介子传播子：使用不变量 \(t=-2m_AE_R\)；
- \(q_{\rm NR}\)：仅是核反冲能量关系的非相对论近似。

## G.6 代码约定

当前统一约定：

- research/three_body_calculation_and_validation/rate_kinematics.py：精确 \(q_{\rm exact}\)，用于三体运动学；
- research/three_body_calculation_and_validation/eq6_kernel.py：精确 \(q_{\rm exact}\)，用于三体末态构造；
- research/three_body_calculation_and_validation/joint_xe131.py：AFH 响应插值使用精确空间 \(q_{\rm exact}\)；
- research/afh_default_density_xe131/recompute_afh_four_benchmarks.py：固定速度四组 benchmark 使用精确空间 \(q_{\rm exact}\)；
- research/afh_default_density_xe131/compute_four_benchmark_dsigma.py：同样使用精确空间 \(q_{\rm exact}\)；
- research/afh_default_density_natural_xenon_halo/run_afh_natural_xenon_halo_fold.py：默认 exact_spatial；nr_approx 仅用于近似对照；legacy_exact 保留为向后兼容别名。

若输入样本的 q 与所选约定不一致，程序会报错，不会静默复用不匹配的 \(R_A\)。

## G.7 机器可读结果

q 审计程序保存以下文件：

- research/afh_default_density_natural_xenon_halo/results/natural_xenon_q_convention_audit.csv：28 个天然氙样本；
- research/afh_default_density_natural_xenon_halo/results/xe131_afh_response_shift_NR_vs_exact.csv：NIST Xe-131 质量下的响应对照；
- research/afh_default_density_natural_xenon_halo/results/xe131_fixed_benchmark_q_comparison.csv：\(M_A=131u\) 下的固定 benchmark 对照；
- research/afh_default_density_natural_xenon_halo/results/q_convention_audit_summary.json：机器可读汇总。

当前 16,807 行的七同位素 AFH v6.0 default-density response grid 已提交，包含七个 2,401 点 direct finite-sum exact-q 响应表、七种 source density matrices、metadata 和 SHA-256 manifest。早期 28 个 selected-point exact-q 样本仍作为历史输入与交叉检查保留，但不再是连续谱的唯一 AFH 响应输入。基于完整七同位素网格，AFH-7/Hybrid-9 的 84 点、5–800 keV grid-sampled spectra 已归档；Xe-124/Xe-126 仍无 AFH default matrices，完整高阶 1,344 行 ZIP 仍为外部 checksum-only。

## G.8 验收标准

| 项目 | 状态 | 说明 |
|---|---|---|
| AFH 的 \(q\) 定义 | 已核实 | \(q\) 是空间动量转移 |
| 精确质量壳关系 | 已推导 | \(q^2=2m_AE_R+E_R^2\) |
| 28 个天然氙样本 | 已核实 | 全部匹配 exact spatial q |
| Xe-131 NR 近似影响 | 已计算 | NIST 与 \(M_A=131u\) 两种质量约定均有对照 |
| 天然氙 halo fold | exact-q 基线 | 98 个同位素贡献、14 个总速率复现；最大总速率差异 \(2.67\\times10^{-12}\)，CI run 43044583357 通过 |
| AFH-7/Hybrid-9 全范围反冲谱 | PASS_WITH_NOTES | 四 benchmark、84 点、1,344 baseline rows；AFH direct exact-q + threshold-\(u^2\)；高阶 baseline-to-final spectrum difference 最大 \(6.46772\times10^{-6}\) | 这是 grid-sampled pre-detector spectrum；高阶 ZIP 仅外部 checksum；Xe-124/Xe-126 缺 AFH matrices；GCN/JJ55 求积尚未匹配 |
| 原生 Mathematica 复算 | 已完成 PASS（Xe-131 response-level） | Wolfram 14.0.0；2401 个 q 节点；与 Python 最大相对差异 (3.59\times10^{-9})；SHA-256 manifest 已归档 | 不代表完整 AFH 天然氙连续谱或 LZ likelihood |


## G.9 2026-11-19：B 基准中的核子形状因子与 AFH 核形状因子

本项目现在正式采用 B 作为三体 VV 的主基准。必须区分两个不同尺度的形状效应：

1. 单核子内部的夸克流结构由
   \(\widehat F_1^N(t_N)\)、\(\widehat F_2^N(t_N)\) 描述；
2. 核子在整个氙核中的空间分布由 AFH 的
   \(W_M^{\rm phys}(y_A)\) 描述。

它们不是同一个 form factor，也不能互相替代。B 的 M-only 基准为
\[
\frac{d\sigma_B}{dE_R}\propto
\mathcal P_3L_C^{(3)}
\widehat c_M(t_N)^2W_M^{\rm phys}(y_A),
\]
其中
\[
\widehat c_M(t_N)=
\widehat F_1(t_N)+
\frac{t_N}{8m_N^2}
\left[\widehat F_1(t_N)+2\widehat F_2(t_N)\right].
\]
B 不包含其他 AFH 响应；\(\Phi''\)、\(\Delta\)、\(\Sigma'\) 及干涉项属于后续 C/D 扩展。

采用 Bishara et al. Appendix A.1 的低动量 flavor-separated 输入：
\[
F_1^{uds,N}(t_N)=3+8.392t_N+\mathcal O(t_N^2),\qquad
F_2^{uds,N}(t_N)=-0.552+\mathcal O(t_N).
\]
外部截面前因子使用 \(g_{VN}=3g_{Vq}\)，所以
\[
\widehat F_i=F_i^{uds}/3,\qquad
\widehat F_1(0)=1,\quad \widehat F_2(0)=-0.184.
\]
\(F_2\) 仅取已给定的领先阶常数，不假设未提供的 Pauli 斜率。

严格单体 impulse 处方取
\[
q_N^\mu=q_A^\mu,\qquad t_N=t_A=-2m_AE_R.
\]
AFH 核响应仍然使用
\[
Q_A^2=2m_AE_R+E_R^2,\qquad y_A=b_A^2Q_A^2/4.
\]
静态核子处方 \(q_N^0=0\Rightarrow t_N=-Q_A^2\) 是独立诊断，不得混入正式 B 结果。

AFH raw-to-physical factor four 与 \(g_{VN}=3g_{Vq}\) 的 quark-current factor three 是独立归一化。native physical equal-\(p=n\) AFH response 已经包含 factor four；外部 \(g_{VN}\) 基准使用 \(\widehat F_i=F_i^{uds}/3\)。二者各自只计入一次。

历史 Mathematica notebook 的 AFH \(W_M(y_A)\) 有限核尺寸效应必须保留；其已归档常数 \(g_{VN}\) 路径作为 A 历史参考，不自动等同于 B。所有 B 绝对截面和 Halo 率必须使用上述有限-\(t_N\) 核子流重新计算。

