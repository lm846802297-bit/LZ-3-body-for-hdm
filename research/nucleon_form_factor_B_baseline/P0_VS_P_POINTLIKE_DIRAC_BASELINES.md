# P0 与 P：点状 Dirac 核子的领先阶基准和有限动量基准

**用途：** 固定三体 VV 暗物质散射中 P0 与 P 两组点状核子基准的物理定义、匹配阶数、变量约定、数值关系和代码实现。本文是四级 P0/P/A0/B 比较的补充规范；完整四级结果见 [POINTLIKE_NUCLEON_P_A_B_COMPARISON.md](POINTLIKE_NUCLEON_P_A_B_COMPARISON.md)。

## 1. 结论先行

P0 与 P **不是两种不同的核子内部结构模型**。两者均采用点状 Dirac 核子：

\[
\widehat F_1=1,\qquad \widehat F_2=0.
\]

两者的区别是对同一个点状 Dirac 核子电荷流采用不同的匹配精度：

- **P0：领先阶点核子电荷基准。** 只保留领先阶电荷项，令归一化系数 \(\widehat c_M^{P0}=F_M^{P0}=1\)（原始未归一化系数 \(c_M^{\rm raw,P0}=3\)，舍去有限动量的 \(1/m_N^2\) 匹配修正。
- **P：有限动量点状 Dirac 电荷基准。** 仍取 \(\widehat F_1=1,\widehat F_2=0\)，但保留当前 M-only 匹配方案中的有限转移动力学修正。

在本仓库采用的匹配约定下，

\[
\boxed{
\widehat c_M^{P0}=1,
\qquad
\widehat c_M^P=1+\frac{t_N}{8m_N^2}
=1-\frac{Q_N^2}{8m_N^2},
}
\qquad Q_N^2\equiv -t_N.
\]

所以

\[
\boxed{
P0=\lim_{Q_N^2/m_N^2\to0}P.
}
\]

仅写出 \(\widehat F_1=1,\widehat F_2=0\) 不能区分 P0 和 P；必须同时说明是否保留 \(\widehat c_M\) 中的有限转移项。


### 2.0 Raw and normalized coefficient: why the reference value is one

The repository's flavor-summed current is normalized for universal unit \(u,d,s\) vector couplings:
\[
F_i^{uds,N}=3\left(F_i^{\mathrm{EM},p}+F_i^{\mathrm{EM},n}+F_i^{s,N,\mathrm{unit}}\right).
\]
At zero transfer, \(F_1^{\mathrm{EM},p}(0)=1\), \(F_1^{\mathrm{EM},n}(0)=0\), and the net strange vector charge is zero. Hence \(F_1^{uds,N}(0)=3\) for either nucleon. The raw coefficient therefore obeys \(c_M^{\rm raw}(0)=3\).

The rate postprocessor factors out this common charge normalization and defines
\[
F_M(t_N)=\frac{c_M^{\rm raw}(t_N)}{3}
\equiv \widehat c_M(t_N).
\]
Thus the pointlike leading-order reference is
\[
c_M^{\rm raw,P0}=3,\qquad
\widehat c_M^{P0}=F_M^{P0}=1.
\]
The value one is the normalized unit vector charge of a nucleon, not an arbitrary fit parameter and not a statement that the nuclear response \(W_M\) equals one.

## 2. 从核子矢量流定义两组基准

核子级矢量流采用 Dirac–Pauli 形式：

\[
J_N^\mu=
\bar u_N(p_N')
\left[
F_1^V(t_N)\gamma^\mu
+\frac{iF_2^V(t_N)}{2m_N}
\sigma^{\mu\nu}q_{N,\nu}
\right]u_N(p_N),
\]

其中

\[
q_N^\mu=p_N'^\mu-p_N^\mu,\qquad t_N=q_N^2.
\]

为与项目采用的普适单位 \(u,d,s\) 夸克矢量流耦合规范一致，定义

\[
\widehat F_i^N(t_N)=\frac{F_i^{uds,N}(t_N)}{3}.
\]

### 2.1 P0：领先阶点核子电荷基准

\[
\widehat F_1^{P0}=1,\qquad \widehat F_2^{P0}=0,
\]

并且在领先阶近似中直接取

\[
\boxed{\widehat c_M^{P0}=F_M^{P0}=1,\qquad c_M^{\rm raw,P0}=3.}
\]

P0 的含义是：在核子电荷响应中只保留零阶电荷耦合。它不保留当前匹配系数中的有限转移项

\[
\frac{t_N}{8m_N^2}
\left(\widehat F_1+2\widehat F_2\right).
\]

因此 P0 是项目早期三体反冲率的 leading-order charge-only 基准。历史输入谱的通用列名 **rate_events_kg_day_keV** 对应 P0；旧记录中称为 A 的这组谱，在当前四级规范中统一解释为 P0，而不是 A0。

### 2.2 P：有限动量点状 Dirac 电荷基准

P 仍然采用点状 Dirac 形状因子：

\[
\widehat F_1^P(t_N)=1,\qquad
\widehat F_2^P(t_N)=0.
\]

但 P 保留当前项目采用的电荷型匹配系数：

\[
\widehat c_M(t_N)\equiv F_M(t_N)=\frac{c_M^{\rm raw}(t_N)}{3}=
\widehat F_1(t_N)
+\frac{t_N}{8m_N^2}
\left[\widehat F_1(t_N)+2\widehat F_2(t_N)\right].
\]

代入点状 Dirac 形状因子：

\[
\boxed{
\widehat c_M^P(t_N)=1+\frac{t_N}{8m_N^2}
=1-\frac{Q_N^2}{8m_N^2},\qquad c_M^{\rm raw,P}=3\widehat c_M^P.
}
\]

P 因而检验有限动量转移下、当前 M-only 匹配处方中的 Dirac 电荷项修正。它没有引入核子的有限尺寸形状因子，也没有引入 Pauli 磁矩。

### 2.3 为什么完整顶点相同，计算结果仍然不同？

对 P0 和 P，核子顶点都可写为

\[
\Gamma_N^\mu=\gamma^\mu,
\]

因为两者都令 \(F_1=1,F_2=0\)。

如果对两者都保留完全相同的完整相对论自旋量矩阵元，并且不作不同的展开或匹配截断，那么两者当然给出相同结果。

当前 P0/P 的区别出现在后续的核子流约化和 M-only rate-level 匹配中：

- P0 将归一化电荷匹配系数截断为 \(\widehat c_M=F_M=1\)（原始系数 \(c_M^{\rm raw}=3\)）；
- P 保留项目当前匹配公式中的有限 \(t_N/m_N^2\) 项，即 \(\widehat c_M=1+t_N/(8m_N^2)\)。

因此，不能仅凭两组的 \(F_1,F_2\) 数值判断其计算精度；还必须检查 \(c_M\) 的定义和保留阶数。

## 3. 动量转移约定：不能混淆 \(t_N\)、\(Q_N^2\) 和 \(Q_A^2\)

本项目采用的形式冲量匹配约定为

\[
q_N^\mu=q_A^\mu,\qquad
t_N=t_A=-2m_AE_R.
\]

定义核子形状因子的正类空间变量

\[
Q_N^2\equiv -t_N=2m_AE_R.
\]

AFH 核响应使用的是精确空间动量平方：

\[
Q_A^2\equiv |\mathbf q_A|^2
=2m_AE_R+E_R^2.
\]

三者在计算中承担不同角色：

| 变量 | 定义 | 用途 |
|---|---|---|
| \(t_N\) | \(-2m_AE_R\) | 核子流匹配中的不变转移 |
| \(Q_N^2\) | \(-t_N=2m_AE_R\) | P 的有限转移修正；B 的形状因子自变量 |
| \(Q_A^2\) | \(2m_AE_R+E_R^2\) | AFH 空间傅里叶变量 |

AFH 的振子变量为

\[
y_A=\frac{b_A^2Q_A^2}{4},
\]

而 P 的匹配系数为

\[
\widehat c_M^P=1-\frac{Q_N^2}{8m_N^2}.
\]

在当前形式冲量约定下，\(Q_N^2\) 与 \(Q_A^2\) 相差 \(E_R^2\)。不能把 AFH 空间动量平方直接替换进 P 的 \(c_M\)，也不能把 P 的核子有限转移修正误称为 AFH 核有限尺寸修正。

## 4. P0 与 P 的振幅、微分率关系

在当前只保留 \(W_M\) 的 rate-level 实现中，P0 与 P 共用相同的三体暗物质动力学核、三体相空间积分、媒介子传播子、halo 速度积分、同位素丰度和 AFH 有限尺寸 \(W_M(y_A)\)。

对单个同位素、固定 \(E_R\)，P 相对 P0 的核子电荷振幅乘子为

\[
\frac{\mathcal M_P}{\mathcal M_{P0}}
=\frac{\widehat c_M^P}{\widehat c_M^{P0}}
=1-\frac{Q_N^2}{8m_N^2}.
\]

因此

\[
\boxed{
\frac{d\sigma_P/dE_R}
     {d\sigma_{P0}/dE_R}
=
\left(1-\frac{Q_N^2}{8m_N^2}\right)^2.
}
\]

令

\[
\epsilon_N=\frac{Q_N^2}{8m_N^2},
\]

则

\[
\frac{d\sigma_P/dE_R}
     {d\sigma_{P0}/dE_R}
=(1-\epsilon_N)^2
=1-2\epsilon_N+\epsilon_N^2.
\]

在 \(\epsilon_N\ll1\) 时，

\[
\boxed{
\frac{d\sigma_P}{d\sigma_{P0}}
\simeq 1-\frac{Q_N^2}{4m_N^2}.
}
\]

所以振幅相对修正为 \(-Q_N^2/(8m_N^2)\)，而微分率的领先相对修正为 \(-Q_N^2/(4m_N^2)\)。

### 4.1 天然氙同位素求和

上面的简单比值是单个同位素、固定反冲能量下的关系。天然氙总谱需要先逐同位素乘上各自的 \(\widehat c_M^2=|F_M|^2，再求和：

\[
\frac{dR_P}{dE_R}
=
\sum_A \eta_A
\frac{dR_{P0,A}}{dE_R}
\left(1-\frac{2m_AE_R}{8m_N^2}\right)^2,
\]

\[
\frac{dR_{P0}}{dE_R}
=
\sum_A\eta_A\frac{dR_{P0,A}}{dE_R}.
\]

因此天然氙总谱的比值是以各同位素 P0 贡献为权重的比值，不应直接使用某一个同位素的 \(\widehat c_M^2 代替。

探测器级事例数还要继续乘以能量依赖的探测效率并在 ROI 内积分：

\[
N_X=
\mathcal E\int_{\mathrm{ROI}}dE_R\,
\epsilon_{\mathrm{LZ}}(E_R)
\frac{dR_X}{dE_R},
\qquad X=P0,P.
\]

所以探测器级 \(N_P/N_{P0}\) 是经过同位素求和、反冲能量积分和探测效率加权后的结果。

## 5. 定量大小：Xe-131 示例

使用

\[
m_A(^{131}\mathrm{Xe})=121.933\ \mathrm{GeV},
\qquad m_N=0.938919\ \mathrm{GeV},
\]

以及 \(Q_N^2=2m_AE_R\)，得到：

| \(E_R\) (keV) | \(Q_N\) (MeV) | \(\widehat c_M^P=F_M^P\) | \((d\sigma_P/dE_R)/(d\sigma_{P0}/dE_R)\) |
|---:|---:|---:|---:|
| 5.4 | 36.29 | 0.9998133 | 0.9996266 |
| 50 | 110.42 | 0.9982711 | 0.9965451 |
| 100 | 156.16 | 0.9965422 | 0.9930963 |
| 200 | 220.85 | 0.9930843 | 0.9862165 |
| 269.9 | 256.55 | 0.9906673 | 0.9814217 |

在 Xe-131 的 269.9 keV 处，P 的微分率比 P0 低约 \(1.86\%\)。低反冲端两者几乎重合，差异随反冲能量增加而增大。

## 6. 已有 LZ 探测器级比较

以下为当前四级比较记录中的 AFH-7、Sufian 2017 strange-current 场景结果。所有结果采用相同的三体/halo 输入、天然氙 AFH 同位素、LZ 2026 Fig. S2 中央 NR 效率、5.4–269.9 keV ROI 和 2.84 tonne-year 曝光：

| Benchmark | P0 事例数 | P 事例数 | \(N_P/N_{P0}\) | P 相对 P0 变化 |
|---|---:|---:|---:|---:|
| \(m_s=200\) keV, \(\Delta m=1\) MeV | 0.3172783 | 0.3142066 | 0.990319 | \(-0.9681\%\) |
| \(m_s=300\) keV, \(\Delta m=1\) MeV | \(1.397899\times10^{-3}\) | \(1.379657\times10^{-3}\) | 0.986950 | \(-1.3050\%\) |
| \(m_s=360\) keV, \(\Delta m=1\) MeV | \(2.858492\times10^{-9}\) | \(2.807575\times10^{-9}\) | 0.982188 | \(-1.7812\%\) |
| \(m_s=300\) keV, \(\Delta m=10\) MeV | \(1.144298\times10^{-5}\) | \(1.129372\times10^{-5}\) | 0.986957 | \(-1.3043\%\) |

这些是探测效率折叠后的事例数，不是未折叠的总散射截面。它们说明在当前 benchmark 和 ROI 下，P0 对 P 的领先阶近似产生约 \(0.97\%\)–\(1.78\%\) 的探测器级差异。

## 7. P0、P、A0、B 四级基准中的位置

四组基准必须按以下顺序区分：

| 基准 | \(\widehat F_1\) | \(\widehat F_2\) | 归一化系数 \(\widehat c_M=F_M\) 的处理 | 所隔离的效应 |
|---|---:|---:|---|---|
| P0 | 1 | 0 | \(\widehat c_M=1\)（原始 \(c_M^{\rm raw}=3\)） | 领先阶点核子电荷基准 |
| P | 1 | 0 | \(\widehat c_M=1+t_N/(8m_N^2)\) | 点状 Dirac 电荷流的有限转移匹配修正 |
| A0 | 1 | \(\widehat F_2(0)\) | 保留 \(t_N\) 项 | 静态 Pauli 磁矩贡献 |
| B | \(\widehat F_1(t_N)\) | \(\widehat F_2(t_N)\) | 完整使用有限转移形状因子 | 核子有限动量内部结构 |

对应的逐级比较是：

1. P0 \(\to\) P：有限转移 Dirac 电荷匹配修正；
2. P \(\to\) A0：静态 Pauli 磁矩修正；
3. A0 \(\to\) B：有限动量核子形状因子修正。

P0/P 的比较不能与 A0/B 的核子内部结构比较混为一谈。

## 8. P 的适用范围与命名边界

本文中的 P 是**当前 M-only 核响应计算中的有限转移点状 Dirac 电荷基准**。它不是完整精确的相对论核子流计算。

P 的定义没有自动包含：

- 完整相对论核子流的全部空间分量；
- 全部自旋相关非相对论核算符；
- \(W_{\Phi''}\)、\(W_{\Sigma'}\)、\(W_\Delta\) 等其他 AFH 核响应；
- 完整三体暗物质张量与全部核流张量的协变收缩。

因此代码、图例和论文中采用以下名称：

- P0 — Leading-order point-nucleon charge；
- P — Finite-transfer pointlike Dirac charge (M-only)；
- A0 — Zero-transfer Dirac–Pauli form-factor approximation；
- B — Finite-transfer Dirac–Pauli form factors.

## 9. 代码实现和回归要求

实现位于：

- compare_pointlike_A_B_nucleon_baselines.py
- borah2020_lowq2.py
- test_compare_pointlike_A_B_nucleon_baselines.py

代码中 P0 是历史领先阶源谱的直接重建；P 使用 pointlike_dirac_cM_hat 计算有限转移系数。两者都在相同的三体/halo kernel 和 AFH \(W_M\) 上计算。

回归测试至少检查：

1. \(\widehat c_M^{P0}=1\)（原始 \(c_M^{\rm raw,P0}=3\)）；
2. \(\widehat c_M^P(Q_N^2=0)=1\)，即零转移极限下 P 与 P0 闭合；
3. 对正的类空间转移，当前约定下 \(\widehat c_M^P<1\)；
4. 单同位素固定反冲能量的 P/P0 微分率比等于 \((\widehat c_M^P)^2\)；
5. 完整天然氙谱和探测器折叠中，P0 重建与历史源谱闭合；
6. P、A0、B 的输出使用同一三体/halo 输入和相同的 AFH 响应。

运行回归测试：

~~~bash
python -m unittest research.nucleon_form_factor_B_baseline.test_compare_pointlike_A_B_nucleon_baselines -v
~~~

运行四级比较：

~~~bash
python research/nucleon_form_factor_B_baseline/compare_pointlike_A_B_nucleon_baselines.py \
  --source-dir research/afh_default_density_natural_xenon_halo/results/afh7_hybrid9_continuous_2026-11-14 \
  --efficiency-csv research/lz_detector_response/lz_2026_extended_nr/lz_2026_nr_efficiency_digitized.csv \
  --out-dir results/nucleon-P0-P-A0-B \
  --roi-min-keV 5.4 --roi-max-keV 269.9 --exposure-tonne-year 2.84
~~~

输出包括天然氙谱、逐同位素贡献、LZ 探测器级事例数、metadata 和 SHA-256 校验文件。

---

## 10. 项目固定规范

后续项目中凡使用 P0 或 P，必须同时报告：

- 点状形状因子条件：\(\widehat F_1=1,\widehat F_2=0\)；
- 归一化电荷匹配系数：P0 为 \(\widehat c_M=F_M=1\)，P 为 \(\widehat c_M=1+t_N/(8m_N^2)\)；原始系数在零转移时为 \(c_M^{\rm raw}=3\)。
- 采用的 \(t_N\) 约定；
- AFH 核响应是否保留；
- 是否仅为 M-only rate-level 结果。

**最终固定结论：P0 是 P 的领先阶近似；P 是保留当前有限转移电荷匹配项的点状 Dirac 核子基准。两者的差别来自匹配阶数，不来自核子内部形状因子。**
