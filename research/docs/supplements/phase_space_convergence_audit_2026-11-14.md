# P1-PhaseSpace：三体相空间独立数值收敛审计（2026-11-14）

## 1. 目的与边界

本轮针对正文 Eq. (6) 的 reduced kernel

\[
I_6=\int_{W_{\min}^2}^{W_{\max}^2}dW^2\,
\sqrt{\lambda_{\rm dim}(W^2)}
\int_{-1}^{1}dz\,
\left\langle {\cal L}_{00}\right\rangle_{\phi_*}
\]

开展独立数值审计。目标是区分：

1. \(W^2\) 端点参数化导致的求积误差；
2. \(z\) 和 \(\phi_*\) 的角积分误差；
3. Lorentz-invariant 三体测度与 Eq. (6) 的整体归一化；
4. 接近三体阈值时的浮点消减误差。

**独立性边界：** 本审计独立实现了积分变量映射、积分权重和未归一化 \(d\Phi_3\) 路径，但复用仓库中 `eq6_kernel.py` 的 Dirac 自旋迹和两图振幅。它不是第二套独立的振幅/自旋迹程序，也不是完整 UV 模型验证。

本轮采用 Dirac 外部态、纯标量耦合的条件性 pole-width 处方，\(g_2=1\)。结果只覆盖所列 fixed-speed benchmark 与阈值邻域，不代表完整 halo fold 或 LZ likelihood。

## 2. 阈值变量映射

令

\[
W_{\min}^2=(m_{\chi_1}+m_s)^2,\qquad
W_{\max}^2=W_{\min}^2+\Delta,
\]

并定义

\[
\delta=W^2-W_{\min}^2.
\]

有量纲 Källén 函数可精确因式分解为

\[
\lambda_K
=\left[W^2-(m_{\chi_1}+m_s)^2\right]
 \left[W^2-(m_{\chi_1}-m_s)^2\right]
=\delta(4m_{\chi_1}m_s+\delta).
\]

故

\[
\lambda_{\rm dim}
=\frac{\delta(4m_{\chi_1}m_s+\delta)}
       {(W_{\min}^2+\delta)^2}.
\]

在线性 \(W^2\) 变量下，\(\sqrt{\lambda_{\rm dim}}\sim\sqrt{\delta}\)，在下端点存在平方根型 cusp。采用

\[
\boxed{W^2=W_{\min}^2+\Delta u^2,\quad 0\le u\le1}
\]

则

\[
\boxed{dW^2=2\Delta u\,du}.
\]

阈值附近

\[
\sqrt{\lambda_{\rm dim}}\,dW^2
\propto u^2du,
\]

从而将端点行为平滑化。

### 2.1 阈值处的稳定浮点实现

不能在 \(m_{\chi_1}\sim 10^3\) GeV 时，先计算两个约 \(10^6\ {\rm GeV}^2\) 的数再相减，以恢复很小的 \(\delta\)。代码直接传递 \(\delta=\Delta u^2\)，并使用

\[
\lambda_{\rm dim}
=\frac{\delta(4m_{\chi_1}m_s+\delta)}
       {(W_{\min}^2+\delta)^2},
\]

以及

\[
|\mathbf k_*|
=\frac{\sqrt{\delta(4m_{\chi_1}m_s+\delta)}}{2W},
\]

\[
E_{s,*}
=\frac{2m_s(m_{\chi_1}+m_s)+\delta}{2W},
\qquad
E_{\chi_1,*}
=\frac{2m_{\chi_1}(m_{\chi_1}+m_s)+\delta}{2W}.
\]

该写法避免了阈值附近从 \(W^2-W_{\min}^2\) 和 Källén 函数中重复消减大数。

## 3. 三种积分参数化

实现并比较了：

### A. 线性 \(W^2\)

\[
W^2=W_{\min}^2+\Delta x,\qquad
dW^2=\Delta\,dx.
\]

这是原 `reduced_kernel` 所采用的参数化。

### B. 线性 \(W\)

\[
W=W_{\min}+(W_{\max}-W_{\min})x,
\qquad dW^2=2W\,dW.
\]

该路径单独核验 \(dW^2=2W\,dW\) 的 Jacobian。它与线性 \(W^2\) 在相同阶数下相符，但没有消除 \(\sqrt{\delta}\) 的端点 cusp。

### C. 阈值映射 \(u^2\)

\[
W^2=W_{\min}^2+\Delta u^2,\qquad
dW^2=2\Delta u\,du.
\]

此参数化同时使用显式 \(\delta\) 计算 Källén 函数和末态三动量。

## 4. 四组固定速度 benchmark

统一参数：

- \(m_{\chi_1}=1000\) GeV；
- \(m_A=122\) GeV；
- \(v=776\) km/s；
- \(\Delta m=1\) MeV；
- pole-width 处方，\(g_2=1\)。

绿色 benchmark 取 \(m_s=300\) keV，红色 benchmark 取 \(m_s=200\) keV。反冲点分别为 200、267、542、101 keV。

参考值采用 threshold-\(u^2\) 的 \(48\times24\times16\) 求积，顺序为 \((n_u,n_z,n_\phi)\)。

| \(m_s\) | \(E_R\) | 线性 \(W^2\), 8×8×4 相对差异 | 线性 \(W^2\), 16×16×8 相对差异 | threshold-\(u^2\), 6×6×4 相对差异 |
|---:|---:|---:|---:|---:|
| 300 keV | 200 keV | \(2.37742\times10^{-4}\) | \(3.23494\times10^{-5}\) | \(4.02\times10^{-11}\) |
| 300 keV | 267 keV | \(2.33199\times10^{-4}\) | \(3.17397\times10^{-5}\) | \(1.45\times10^{-11}\) |
| 300 keV | 542 keV | \(2.42444\times10^{-4}\) | \(3.29824\times10^{-5}\) | \(9.03\times10^{-12}\) |
| 200 keV | 101 keV | \(2.24319\times10^{-4}\) | \(3.05467\times10^{-5}\) | \(1.62\times10^{-10}\) |

表中差异均相对于 \(48\times24\times16\) threshold-\(u^2\) 参考值。四组点上，线性 \(W^2\) 的 \(8\times8\times4\) 最大相对差异为 \(2.42445\times10^{-4}\)；新映射的 \(6\times6\times4\) 最大差异为 \(1.616\times10^{-10}\)。

线性 \(W\) 的 \(8\times8\times4\) 与线性 \(W^2\) 的结果在四组点上相差约 \(10^{-9}\) 相对量级，确认显式 \(2W\) Jacobian 的实现一致；但它仍保留阈值端点的慢收敛。

## 5. 真正接近运动学阈值的检查

对 \(m_s=300\) keV、\(E_R=542\) keV，先由三体阈值方程求 \(v_{\min}\)，再取

\[
v=v_{\min}+\{0.1,0.5,1,2,5\}\ {\rm km/s}.
\]

在最接近阈值的 \(v-v_{\min}=0.1\) km/s 点，

\[
W_{\max}^2-W_{\min}^2
=2.42608832\times10^{-4}\ {\rm GeV}^2.
\]

对这五个速度点，线性 \(W^2\) 的 \(8\times8\times4\) 最大相对差异为 \(2.53370\times10^{-4}\)，而稳定 threshold-\(u^2\) 的 \(4\times4\times4\) 最大相对差异为 \(1.64\times10^{-10}\)。这说明新变量映射不仅改善普通 benchmark，也改善了非常靠近相空间开启边界的积分。

这里的参考是相同角阶数下 \(24\times4\times4\) threshold-\(u^2\) 结果；这项检查针对 W 方向收敛，不是对完整 halo 速度积分的误差估计。

## 6. 分别检查 \(z\) 和 \(\phi_*\)

在绿色 \(E_R=200\) keV benchmark 上，固定 \(n_u=8\)：

- \(z\) 阶数从 2 到 24，最大相对差异为 \(2.81\times10^{-12}\)；
- \(\phi_*\) 阶数从 2 到 20，最大相对差异为 \(3.58\times10^{-12}\)。

这些数值说明该代表点的角积分非常平滑。不能据此断言所有参数点，尤其是极点附近，都有同样的角阶数要求；后续需要在近极点参数下重复角向收敛检查。

## 7. 直接 Lorentz-invariant 相空间归一化复核

不先将方位角写成平均，而是保留未归一化 \(d\phi_*\)：

\[
\frac{d\Phi_3}
{dE_R\,dW^2\,dz\,d\phi_*}
=
\frac{\sqrt{\lambda_{\rm dim}}}
{512\pi^4p_{\chi_1}}.
\]

使用

\[
F=4m_Ap_{\chi_1},
\qquad
|\mathcal M|^2
=\frac{4m_A^2 C^2R_A}{D^2}\mathcal L_{00},
\qquad
D=m_V^2+2m_AE_R,
\]

直接积分未归一化 \(d\phi_*\)，得到

\[
\frac{d\sigma}{dE_R}
=
\frac{m_A C^2R_A}
{512\pi^4p_{\chi_1}^2D^2}
\int dW^2\,dz\,d\phi_*\,
\sqrt{\lambda_{\rm dim}}\mathcal L_{00}.
\]

与 Eq. (6) 的 \(1/(2\pi)\) 方位角平均形式比较，二者应满足

\[
\int dW^2\,dz\,d\phi_*\,
\sqrt{\lambda_{\rm dim}}\mathcal L_{00}
=2\pi I_6.
\]

数值对照（\(m_V=10\) GeV、\(C^2=1\)、\(R_A=1\)，8×8×4）：

| 数值量 | 结果 |
|---|---:|
| \(I_6\) | \(868218.71218827\ {\rm GeV}^2\) |
| 未归一化方位角积分 | \(5455179.0558397\ {\rm GeV}^2\) |
| raw integral / \((2\pi I_6)\) | 1 |
| Eq. (6) 的 \(d\sigma/dE_R\) | \(0.19897140857689\ {\rm GeV}^{-3}\) |
| 直接 \(d\Phi_3\) 的 \(d\sigma/dE_R\) | \(0.19897140857689\ {\rm GeV}^{-3}\) |
| 两条路径之比 | 1 |

因此，在本次采用的相空间和核电荷流约定下，\(256\pi^3\) 前因子与未归一化 Lorentz-invariant 测度数值一致。这个检查没有引入 AFH factor 4；AFH 核响应归一化仍然是独立的一层。

## 8. 质量壳与数值实现检查

稳定阈值点构造后，代表点的最大四动量闭合残差约为 \(2.5\times10^{-13}\) GeV；外腿质量壳和 \(K^2-W^2\) 的绝对残差在 \(4\times10^{-10}\ {\rm GeV}^2\) 量级。

新增 6 个回归测试，覆盖：

1. threshold-\(u^2\) 与高阶参考值；
2. 线性 \(W\) 和线性 \(W^2\) Jacobian 对照；
3. \(v_{\min}+0.1\) km/s 的阈值邻域；
4. \(z\) 和 \(\phi_*\) 独立收敛；
5. raw \(d\phi_*\) 与 normalized azimuthal average；
6. 稳定末态构造的质量壳和四动量闭合。

本地测试：**6/6 PASS**。GitHub Actions 的独立 CI 结果需以新 PR 实际运行记录为准。

## 9. 当前结论与尚未完成事项

### 已完成

- 三种 \(W\) 变量参数化的比较；
- 阈值稳定 Källén 函数和末态动量构造；
- 四组 benchmark 的 \(I_6\) 收敛对照；
- 五个 \(v_{\min}\) 邻域速度点；
- \(z,\phi_*\) 分别求积阶数对照；
- raw Lorentz-invariant \(d\Phi_3\) 与 Eq. (6) 前因子复核。

### 尚未完成

- 当 \(m_{\chi_2}^2\) 从上方逼近 \(W_{\max}^2\) 时的窄峰/近极点积分；
- 在零宽、pole-width、running-width 方案下系统比较收敛性；
- 对更广泛的 \((m_s,\Delta m,E_R,v)\) 区域建立自动误差估计；
- 将收敛后的 \(I_6\) 接入完整天然氙 halo fold。

因此，本轮支持的结论是：**在所测的非近极点 benchmark 和阈值邻域，threshold-\(u^2\) 映射显著改善了 \(I_6\) 的数值收敛，并且 \(256\pi^3\) 归一化通过 raw-\(d\Phi_3\) 数值对照。** 不能把这一结论扩大为全参数空间已完成误差控制。