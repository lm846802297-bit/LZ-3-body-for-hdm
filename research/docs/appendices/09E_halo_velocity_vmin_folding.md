> 所属主报告：[AFH v6.0 氙核响应与三体暗物质散射](../09_afh_xe131_three_body_scattering_natural_xenon.md)

# 附录 E：实验室系速度分布、三体 \(v_{\min}\) 与 halo folding

## E.1 速度分布与归一化约定

采用一维实验室系速度模长分布 \(f_{\rm lab}(v)\)，而不是三维速度矢量分布：

\[
\int_0^\infty f_{\rm lab}(v)\,dv=1.
\]

速度 \(v\) 以 km/s 输入，因此 \(f_{\rm lab}\) 的单位是 \(({\rm km/s})^{-1}\)。程序中的 \(v/c\) 使用 km/s 单位下的 \(c=299792.458\) km/s 计算。

截断标准晕模型（truncated Standard Halo Model, SHM）采用

\[
v_0=220\ {\rm km/s},\qquad
v_E=232\ {\rm km/s},\qquad
v_{\rm esc}=544\ {\rm km/s}.
\]

定义

\[
z_{\rm esc}=\frac{v_{\rm esc}}{v_0},
\]

\[
N_{\rm esc}
=
\operatorname{erf}(z_{\rm esc})
-\frac{2z_{\rm esc}}{\sqrt\pi}e^{-z_{\rm esc}^2}.
\]

实验室系速度模长 PDF 为

\[
f_{\rm SHM}(v)=
\frac{v}{\sqrt\pi v_0v_EN_{\rm esc}}
\begin{cases}
e^{-(v-v_E)^2/v_0^2}
-e^{-(v+v_E)^2/v_0^2},
&0\le v<v_{\rm esc}-v_E,\\[1mm]
e^{-(v-v_E)^2/v_0^2}
-e^{-v_{\rm esc}^2/v_0^2},
&v_{\rm esc}-v_E\le v\le v_{\rm esc}+v_E,\\[1mm]
0,&v>v_{\rm esc}+v_E.
\end{cases}
\]

因此

\[
\boxed{v_{\max,\rm lab}=v_{\rm esc}+v_E=776\ {\rm km/s}}.
\]

该 PDF 在 \(v=v_{\max,\rm lab}\) 处连续趋于零。若某同位素的 \(v_{\min,A}\) 只比 776 km/s 低很小一段距离，虽然运动学上仍开放，速度积分也会因为支持区间很窄且 PDF 在端点消失而极度抑制。

作为高速度尾部诊断，程序另使用不截断的 boosted Maxwell–Boltzmann 速度模长分布：

\[
f_{\rm MB}(v)=
\frac{v}{\sqrt\pi v_0v_E}
\left[
e^{-(v-v_E)^2/v_0^2}
-e^{-(v+v_E)^2/v_0^2}
\right].
\]

数值积分上限取 1600 km/s。该分布只用于检查截断 SHM 高速度尾部对结果的影响，不作为与截断 SHM 同等地位的默认 halo 假设。两种 PDF 均进行数值归一化检查。

## E.2 三体过程的最小入射速度 \(v_{\min,A}\)

固定同位素 \(A\) 和反冲能量 \(E_R\) 时，三体过程开放的条件为

\[
W_{\max,A}^2(v,E_R)\ge(m_{\chi_1}+m_s)^2.
\]

阈值速度由等号确定。定义

\[
Q=\sqrt{2m_AE_R+E_R^2},
\]

以及

\[
a=m_s+\frac{m_AE_R+m_s^2/2}{m_{\chi_1}}.
\]

将

\[
W_{\max}^2=
m_{\chi_1}^2+
2m_{\chi_1}\gamma\beta Q
-2(m_{\chi_1}\gamma+m_A)E_R
\]

代入阈值方程，整理得

\[
\boxed{\gamma(\beta Q-E_R)=a}.
\]

使用 \(\gamma=(1-\beta^2)^{-1/2}\)，平方后得到关于 \(\beta\) 的二次方程：

\[
(Q^2+a^2)\beta^2-2QE_R\beta+(E_R^2-a^2)=0.
\]

取物理的正根：

\[
\boxed{
\beta_{\min}=
\frac{
QE_R+a\sqrt{Q^2-E_R^2+a^2}
}{
Q^2+a^2
},
\qquad
v_{\min,A}=c\beta_{\min}.
}
\]

这个阈值来自当前 \(\chi_1+A\to\chi_1+A+s\) 三体运动学，不是弹性散射或普通两体非弹性散射的标准 \(v_{\min}\) 公式。由于 \(m_A\) 不同，每种氙同位素都必须单独计算 \(v_{\min,A}\)。

## E.3 从单同位素截面到天然氙事件率

对单一同位素、固定入射速度，正文 Eq. (6) 给出

\[
\frac{d\sigma_A}{dE_R}
=
\frac{
m_A(g_1g_2g_{VN})^2R_A(E_R)
}{
256\pi^3p_{\chi_1}^2(m_V^2+2m_AE_R)^2
}
I_{6,A}(v,E_R).
\]

天然氙的微分事件率为

\[
\boxed{
\frac{dR}{dE_R}
=
N_T\frac{\rho_\chi}{m_{\chi_1}}c
\sum_{A\in{\rm available}}x_A
\int_{v_{\min,A}}^{v_{\max}}
dv\,f_{\rm lab}(v)\frac vc
\frac{d\sigma_A}{dE_R}(v)
}.
\]

其中：

- \(N_T=N_{\rm Av}1000/\bar M_{\rm Xe}\) 是每 kg 天然氙的靶核总数；
- \(\rho_\chi/m_{\chi_1}\) 是暗物质数密度；
- \(c\) 是以 cm/s 表示的光速；
- \(v/c\) 是无量纲速度通量因子；
- \(x_A\) 是天然原子丰度；
- 每个同位素使用自己的 \(m_A,R_A(E_R),v_{\min,A}\) 和 \(I_{6,A}\)。

程序在每个速度节点重新计算

\[
p_{\chi_1}=\frac{m_{\chi_1}\beta}{\sqrt{1-\beta^2}}
\]

以及三体 reduced kernel \(I_6\)，而不是把某一个固定速度的截面乘以平均速度。

采用的基准输入为

\[
m_{\chi_1}=1\ {\rm TeV},\qquad m_V=10\ {\rm GeV},
\]
\[
(g_1g_2g_{VN})^2=10^{-8},\qquad g_2=1,
\qquad \rho_\chi=0.3\ {\rm GeV/cm^3}.
\]

这里单独给出 (g_2=1)，是因为 ((g_1g_2g_{VN})^2) 这个耦合乘积并不能单独确定 (chi_2	o\chi_1s) 的 pole width；当前宽度还采用 Dirac 费米子、实标量、纯 scalar Yukawa、单一开放衰变道的条件性假设。

程序内部先以自然单位计算截面，再转换单位。对于微分截面，

\[
1\ {\rm GeV}^{-3}
\longrightarrow
0.389379\times10^{-33}\ {\rm cm^2/keV}.
\]

最终 halo-folded rate 的单位为 events/(kg day keV)。速率计算包括秒到天的 \(86400\) 转换，但尚未乘探测器效率或能量分辨函数。

### E.3.1 AFH 响应动量与三体运动学

AFH 响应函数使用空间动量转移 \(q\)，满足 \(y=(qb_A/2)^2\)。本节的精确三体质量壳关系给出

\[
q_{\rm exact}=\sqrt{2m_AE_R+E_R^2}.
\]

因此 halo fold 中 \(R_A(E_R)\)、\(W_{\max,A}\)、\(v_{\min,A}\) 和三体 reduced kernel 均使用同一个精确空间动量。常见的

\[
q_{\rm NR}=\sqrt{2m_AE_R}
\]

只是 \(E_R\ll m_A\) 的非相对论反冲近似，保留为独立的响应敏感性对照。

当前归档的 28 个 AFH 天然氙响应样本全部是在 \(q_{\rm exact}\) 处取值，与精确三体运动学一致，不属于需要修正的 legacy 错误样本。独立补充技术说明给出精确质量壳推导、28 个样本核查及 Xe-131 NR 近似的响应影响。

## E.4 101 keV 时逐同位素阈值

对四组 benchmark，101 keV 处的 \(v_{\min,A}\) 如下。Green 与 Blue 的 \(m_s\) 相同，因此其运动学阈值相同；\(\Delta m\) 会改变传播子和 \(I_6\)，但不改变这个由 \(m_s,m_{\chi_1},m_A,E_R\) 决定的三体阈值。

| 同位素 | 天然丰度 \(x_A\) | \(m_A\) [GeV] | Red \(m_s=200\) keV | Green/Blue \(m_s=300\) keV | Black \(m_s=360\) keV |
|---|---:|---:|---:|---:|---:|
| Xe-128 | 0.019102 | 119.1137909 | 604.992 | 798.261 | 914.222 |
| Xe-129 | 0.264006 | 120.0464492 | 602.819 | 795.335 | 910.845 |
| Xe-130 | 0.040710 | 120.9767589 | 600.677 | 792.452 | 907.516 |
| Xe-131 | 0.212324 | 121.9097198 | 598.554 | 789.594 | 904.217 |
| Xe-132 | 0.269086 | 122.8403486 | 596.461 | 786.776 | 900.964 |
| Xe-134 | 0.104357 | 124.7044915 | 592.342 | 781.229 | 894.560 |
| Xe-136 | 0.088573 | 126.5691748 | 588.316 | 775.806 | 888.300 |

速度单位均为 km/s。截断 SHM 的最大速度为 776 km/s，因此：

- Red：七种可用同位素全部开放；
- Green/Blue：只有 Xe-136 开放，且 \(v_{\min,136}=775.8059\) km/s，仅比截断端点低约 0.1941 km/s；
- Black：七种可用同位素全部关闭。

这解释了为什么 Green 在 101 keV 处只剩 Xe-136 有贡献：Xe-136 是当前七种可用同位素中质量最大的核，因而在该点具有最低的三体阈值速度。其他六种同位素的阈值均高于 SHM 支持区间。Xe-136 虽然开放，但只剩极窄的速度积分区间，且 PDF 在 776 km/s 处趋于零，因此速率仍然极小。

## E.5 已归档的 selected-point 速率

在 \(E_R=101\) keV，结果为：

| Benchmark | 截断 SHM [events/(kg day keV)] | 不截断 MB 尾部诊断 |
|---|---:|---:|
| Red: \(m_s=200\) keV, \(\Delta m=1\) MeV | \(5.2810\times10^{-11}\) | \(8.6009\times10^{-11}\) |
| Green: \(m_s=300\) keV, \(\Delta m=1\) MeV | \(2.5995\times10^{-22}\) | \(1.3837\times10^{-12}\) |
| Black: \(m_s=360\) keV, \(\Delta m=1\) MeV | 0（关闭） | \(6.2236\times10^{-14}\) |
| Blue: \(m_s=300\) keV, \(\Delta m=10\) MeV | \(2.1675\times10^{-24}\) | \(1.1079\times10^{-14}\) |

Green benchmark 在其他三个选定反冲能量的结果为：

| \(E_R\) [keV] | 截断 SHM | 不截断 MB 尾部诊断 |
|---:|---:|---:|
| 101 | \(2.5995\times10^{-22}\) | \(1.3837\times10^{-12}\) |
| 200 | \(1.8136\times10^{-11}\) | \(1.6461\times10^{-10}\) |
| 267 | \(2.7271\times10^{-13}\) | \(1.7872\times10^{-12}\) |
| 542 | \(1.4561\times10^{-15}\) | \(8.1709\times10^{-14}\) |

这些是 selected-point 理论速率，不是连续反冲谱，也不是 LZ 探测器层面的事件预测。

## E.6 速度求积与适用范围

当前天然氙计算采用：

- 速度积分：32 点 Gauss–Legendre；
- 三体 kernel：\(8\times8\times4\) 个 \(W^2,z,\phi_*\) 求积节点；
- 六个代表性点的 kernel 阶数对照：\(8\times8\times4\) 与 \(16\times16\times8\)，最大相对差异 \(2.19\times10^{-4}\)；
- 五个代表性点的速度阶数对照：32 与 64 节点，最大相对差异 \(3.31\times10^{-6}\)。

当前所有 selected-point 的 \(v_{\min}\) 都高于 \(v_{\rm esc}-v_E=312\) km/s，因此这些积分点均落在截断 SHM PDF 的第二个解析分支。若未来计算完整连续反冲谱，使某些 \(v_{\min}\) 低于 312 km/s，应在该分段点处分割速度积分区间，以避免 Gauss–Legendre 求积跨越 PDF 的解析分支切换点。

当前尚未加入：

- 年度调制；
- \(v_0,v_E,v_{\rm esc}\) 的系统参数扫描；
- Xe-124、Xe-126 的 AFH 响应；
- 连续反冲谱的全网格收敛；
- 探测器效率、分辨率、曝光、选择切和背景似然。

主要程序和结果：

- research/afh_default_density_natural_xenon_halo/run_afh_natural_xenon_halo_fold.py
- research/afh_default_density_natural_xenon_halo/results/vmin_by_isotope_at_101keV.csv
- research/afh_default_density_natural_xenon_halo/results/isotope_halo_contributions_compact.csv
- research/afh_default_density_natural_xenon_halo/results/natural_xenon_halo_rates.csv
- research/afh_default_density_natural_xenon_halo/results/kernel_order_crosschecks.csv
- research/afh_default_density_natural_xenon_halo/results/speed_quadrature_crosschecks.csv

## E.7 exact-spatial-q 归档与 NR 近似对照

当前天然氙 selected-point halo fold 使用 AFH exact spatial q：

\[
q_{\rm response}=q_{\rm kin}
=\sqrt{2m_AE_R+E_R^2}.
\]

当前 exact_spatial 默认模式已完成完整回归复现。CI 对照了 98 个逐同位素贡献和 14 个总速率，最大逐同位素贡献相对差异为 \(4.32\times10^{-10}\)，最大总速率相对差异为 \(2.67\times10^{-12}\)。

- [exact-spatial CI run 43044583357](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43044583357)
- 机器可读比较：results/exact_spatial_reproduction_comparison.json
- 旧的 legacy_exact 别名回归记录仍保留在 results/legacy_exact_reproduction_comparison.json。

当前代码默认 exact_spatial，可直接运行：

~~~bash
python research/afh_default_density_natural_xenon_halo/run_afh_natural_xenon_halo_fold.py
~~~

若显式选择 nr_approx，程序会因输入样本仍采用 exact spatial q 而报错，除非同时提供在 NR q 处重新计算的匹配响应值。该检查用于防止把一个 q 点的 \(R_A\) 错误地标记成另一个 q 点的响应。

本节的 selected-point 速率保留 exact spatial q，不进行经验重标度。NR 近似的响应变化见独立补充技术说明；连续反冲谱仍需恢复完整七同位素 AFH 响应网格后再开展。
