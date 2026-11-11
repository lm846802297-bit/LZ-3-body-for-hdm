> 所属主报告：[AFH v6.0 氙核响应与三体暗物质散射](../09_afh_xe131_three_body_kernel_natural_xenon_halo_2026-11-11.md)
> 本文件为该主报告的独立技术附录，保留推导、约定和复现边界。

# 附录 E：实验室系速度分布、三体 \(v_{\min}\) 与 halo folding

### E.1 速度分布约定

本研究采用一维实验室系速度模长分布 \(f_{\rm lab}(v)\)，满足

\[
\int_0^\infty f_{\rm lab}(v)\,dv=1.
\]

速度变量以 km/s 输入，\(f_{\rm lab}\) 的单位相应为 \(({\rm km/s})^{-1}\)。

截断 SHM 的参数为

\[
v_0=220\ {\rm km/s},\quad
v_E=232\ {\rm km/s},\quad
v_{\rm esc}=544\ {\rm km/s}.
\]

定义

\[
z_{\rm esc}=\frac{v_{\rm esc}}{v_0},
\qquad
N_{\rm esc}=
\operatorname{erf}(z_{\rm esc})
-\frac{2z_{\rm esc}}{\sqrt\pi}e^{-z_{\rm esc}^2}.
\]

截断 SHM 的速度模长分布为

\[
f_{\rm SHM}(v)=
\frac{v}{\sqrt\pi v_0v_E N_{\rm esc}}
\begin{cases}
e^{-(v-v_E)^2/v_0^2}-e^{-(v+v_E)^2/v_0^2},
&0\le v<v_{\rm esc}-v_E,\\[2mm]
e^{-(v-v_E)^2/v_0^2}-e^{-v_{\rm esc}^2/v_0^2},
&v_{\rm esc}-v_E\le v\le v_{\rm esc}+v_E,\\[2mm]
0,&v>v_{\rm esc}+v_E.
\end{cases}
\]

因此

\[
v_{\max,\rm lab}=v_{\rm esc}+v_E=776\ {\rm km/s}.
\]

作为高速度尾部诊断，另使用不截断的 boosted Maxwell–Boltzmann 分布

\[
f_{\rm MB}(v)=
\frac{v}{\sqrt\pi v_0v_E}
\left[
e^{-(v-v_E)^2/v_0^2}
-e^{-(v+v_E)^2/v_0^2}
\right],
\]

数值积分上限取 1600 km/s。该分布仅用于尾部敏感性诊断，不作为与截断 SHM 同等地位的默认 halo 假设。两种 PDF 均进行数值归一化检查。

### E.2 三体过程的最小入射速度

在给定 \(E_R\) 下，允许三体过程的阈值由

\[
W_{\max}^2\ge(m_{\chi_1}+m_s)^2
\]

决定。定义核反冲三动量模长

\[
Q=\sqrt{2m_AE_R+E_R^2}
\]

和

\[
a=m_s+\frac{m_AE_R+m_s^2/2}{m_{\chi_1}}.
\]

由 \(W_{\max}^2=(m_{\chi_1}+m_s)^2\) 的阈值方程

\[
\gamma(\beta Q-E_R)=a
\]

可解得

\[
\boxed{
\beta_{\min}=
\frac{
QE_R+a\sqrt{Q^2-E_R^2+a^2}
}{
Q^2+a^2
},
\qquad
v_{\min}=c\beta_{\min}.
}
\]

这个阈值来自当前三体运动学，不是通常弹性或两体非弹性散射的 \(v_{\min}\) 公式。由于 \(m_A\) 不同，每种氙同位素都必须单独计算 \(v_{\min,A}\)。

### E.3 从截面到天然氙事件率

在当前程序单位约定下，

\[
\frac{dR}{dE_R}
=
N_T\frac{\rho_\chi}{m_{\chi_1}}c
\sum_Ax_A
\int_{v_{\min,A}}^{v_{\max}}
dv\,f_{\rm lab}(v)\frac vc
\frac{d\sigma_A}{dE_R}(v).
\]

其中 \(v/c=\beta\) 是无量纲速度通量因子。数值程序在每个速度节点重新计算对应的 \(p_{\chi_1}\)、三体相空间和 \(I_6\)，而不是把某个固定速度的截面直接乘一个平均速度。

采用

\[
\rho_\chi=0.3\ {\rm GeV/cm^3}.
\]

当前未加入年度调制，也未对 \(v_0,v_E,v_{\rm esc}\) 作系统参数扫描。

### E.4 101 keV 阈值诊断

在 \(E_R=101\) keV：

| benchmark | 可用同位素的 \(v_{\min}\) 范围 [km/s] | 截断 SHM 下开放同位素 |
|---|---:|---|
| Red: \(m_s=200\) keV, \(\Delta m=1\) MeV | 588.3–605.0 | 七种均开放 |
| Green: \(m_s=300\) keV, \(\Delta m=1\) MeV | 775.8–798.3 | 仅 Xe-136 |
| Blue: \(m_s=300\) keV, \(\Delta m=10\) MeV | 775.8–798.3 | 仅 Xe-136 |
| Black: \(m_s=360\) keV, \(\Delta m=1\) MeV | 888.3–914.2 | 无 |

Green/Blue 中 Xe-136 的阈值为

\[
v_{\min,136}=775.806\ {\rm km/s},
\]

距离截断 SHM 上限 776 km/s 仅 0.194 km/s。因此其截断 SHM 速率极小是物理速度支持区间很窄的结果，不应首先归因于求积阶数不足。

Black 的所有可用同位素阈值都高于 776 km/s，故截断 SHM 下速率严格为零。untruncated MB 诊断仍可在更高速度提供非零尾部贡献。

### E.5 求积和选定点结果

天然氙基准使用：

- 速度积分：32 点 Gauss–Legendre；
- \(I_6\)：\(8\times8\times4\)；
- 代表性 \(I_6\) 检查：\(8\times8\times4\) 与 \(16\times16\times8\)，最大相对差异 \(2.19\times10^{-4}\)；
- 代表性速度积分检查：32 与 64 节点，最大相对差异 \(3.31\times10^{-6}\)。

这些收敛检查支持当前 selected-point 结果的数值稳定性，但不能替代连续谱的全网格收敛验证。

---
