> 所属主报告：[AFH v6.0 氙核响应与三体暗物质散射](../09_afh_xe131_three_body_kernel_natural_xenon_halo_2026-11-11.md)
> 本文件为该主报告的独立技术附录，保留推导、约定和复现边界。

# 附录 A：三体运动学、相空间边界与 Dirac 振幅

### A.1 四动量约定

采用自然单位制 \(\hbar=c=1\) 和度规 \(g_{\mu\nu}=\mathrm{diag}(+,-,-,-)\)。所有输入质量、能量和动量在核积分程序中均以 GeV 表示。

考虑

\[
\chi_1(p)+A(P)\longrightarrow
\chi_1(p')+A(P')+s(k).
\]

在靶核静止系，

\[
P^\mu=(m_A,\mathbf 0),\qquad
p^\mu=(E_\chi,0,0,p_\chi),
\]

其中

\[
E_\chi=m_{\chi_1}\gamma,\qquad
p_\chi=m_{\chi_1}\gamma\beta,\qquad
\beta=v/c.
\]

定义核反冲四动量

\[
q^\mu=P'^\mu-P^\mu=(E_R,\mathbf q).
\]

由 \(P'^2=P^2=m_A^2\) 得

\[
|\mathbf q|^2=2m_AE_R+E_R^2.
\]

因此

\[
P'^\mu=(m_A+E_R,\mathbf q).
\]

暗物质与标量组成的末态子系统总动量为

\[
K^\mu=p^\mu-q^\mu=p'^\mu+k^\mu,
\qquad W^2=K^2.
\]

### A.2 \(W^2\) 积分上下限

直接展开

\[
\begin{aligned}
W^2
&=(p-q)^2\\
&=m_{\chi_1}^2-2p\cdot q+q^2\\
&=m_{\chi_1}^2
+2p_\chi|\mathbf q|\cos\theta_q
-2(E_\chi+m_A)E_R,
\end{aligned}
\]

其中使用了

\[
q^2=-2m_AE_R.
\]

在给定 \(v,E_R\) 时，\(\cos\theta_q\in[-1,1]\)。最大值取 \(\cos\theta_q=1\)，故

\[
\boxed{
W_{\max}^2=
m_{\chi_1}^2+
2p_\chi\sqrt{2m_AE_R+E_R^2}
-2(E_\chi+m_A)E_R
}.
\]

末态 \(\chi_1+s\) 的不变量质量必须不小于两粒子静质量之和，因此

\[
\boxed{W_{\min}^2=(m_{\chi_1}+m_s)^2}.
\]

开放相空间的必要条件是

\[
W_{\max}^2\ge W_{\min}^2.
\]

若不满足，程序将该 \((v,E_R)\) 点的积分设为零，而不是对负区间进行数值积分。

对给定 \(W^2\)，核反冲方向与入射暗物质方向的夹角由

\[
\cos\theta_q=
\frac{W^2-m_{\chi_1}^2+
2(E_\chi+m_A)E_R}
{2p_\chi|\mathbf q|}
\]

确定。数值实现还检查 \(|\cos\theta_q|\le1\)，超出允许范围的点不能被当作物理相空间点。

### A.3 \(\chi_1s\) 子系统静止系中的角变量

在 \(K\) 静止系中，末态是一个两体运动学问题：

\[
K\rightarrow\chi_1(p')+s(k).
\]

定义无量纲 Källén 函数

\[
\lambda_{\rm dim}(W^2,m_{\chi_1}^2,m_s^2)
=
\left[1-\frac{(m_{\chi_1}+m_s)^2}{W^2}\right]
\left[1-\frac{(m_{\chi_1}-m_s)^2}{W^2}\right].
\]

则

\[
|\mathbf k_*|
=\frac{W}{2}\sqrt{\lambda_{\rm dim}},
\]

\[
E_{s,*}=
\frac{W^2-m_{\chi_1}^2+m_s^2}{2W},
\qquad
E_{\chi_1,*}=
\frac{W^2+m_{\chi_1}^2-m_s^2}{2W}.
\]

这里的星号表示 \(K\) 静止系。角变量定义为

\[
z=\cos\theta_* \in[-1,1],\qquad
\phi_*\in[0,2\pi).
\]

\(\theta_*\) 是标量三动量与入射暗物质四动量 boost 到 \(K\) 静止系后空间方向之间的夹角。方位角 \(\phi_*\) 定义绕该轴的角位置。

程序先构造 \(K\) 静止系中的 \(p'_*,k_*\)，再 boost 回靶核静止系。这样可以逐点检查：

\[
p^2=p'^2=m_{\chi_1}^2,\qquad
k^2=m_s^2,\qquad
P'^2=m_A^2,
\]

以及四动量守恒

\[
p+P=p'+P'+k.
\]

### A.4 两张辐射图与自旋迹

在正文所采用的 vector–vector 流约定下，

\[
\Gamma^\mu=
\gamma^\mu
\frac{\slashed p-\slashed k+m_{\chi_2}}
{(p-k)^2-m_{\chi_2}^2}
+
\frac{\slashed p'+\slashed k+m_{\chi_2}}
{W^2-m_{\chi_2}^2+i m_{\chi_2}\Gamma_{\chi_2}}
\gamma^\mu.
\]

靶核静止系的时间分量为 \(\Gamma^0\)。对 Dirac 外部费米子，程序计算

\[
\boxed{
L^{00}=
\frac12
\operatorname{Tr}
\left[
(\slashed p'+m_{\chi_1})
\Gamma^0
(\slashed p+m_{\chi_1})
\overline{\Gamma}^{\,0}
\right]
}
\]

其中

\[
\overline{\Gamma}^{\,0}
=\gamma^0(\Gamma^0)^\dagger\gamma^0.
\]

前面的 \(1/2\) 是初态暗物质自旋平均；末态自旋求和已经包含在迹中。实现时不能再额外重复平均，也不能遗漏这一因子。

令两张图分别为 \(\Gamma^0_{\rm before}\) 和 \(\Gamma^0_{\rm after}\)，则

\[
L^{00}=L_{\rm before}+L_{\rm after}+L_{\rm interference}.
\]

干涉项通过完整迹减去两个单图迹得到。两张图必须先在振幅层面相加，再平方；不能把两个单图截面作非相干求和。

只有第二个传播子带 pole width。第一条内部动量是 \(p-k\)。对于未来指向的壳上 \(p,k\)，

\[
(p-k)^2
=m_{\chi_1}^2+m_s^2-2p\cdot k
\le(m_{\chi_1}-m_s)^2
<m_{\chi_2}^2,
\]

因而它不可能到达 \(\chi_2\) 质量壳。第二条内部动量为 \(p'+k=K\)，其不变量为 \(W^2\)，可以接近 \(m_{\chi_2}^2\)，所以近极点处理出现在第二项。

### A.5 \(I_6\) 的数值积分

程序计算的 reduced kernel 为

\[
I_6=
\int_{W_{\min}^2}^{W_{\max}^2}dW^2
\sqrt{\lambda_{\rm dim}}
\int_{-1}^{1}dz
\left[
\frac{1}{2\pi}\int_0^{2\pi}d\phi_*
L^{00}
\right].
\]

采用 Gauss–Legendre 求积：

- \(W^2\)：映射到 \([W_{\min}^2,W_{\max}^2]\)；
- \(z\)：直接在 \([-1,1]\) 积分；
- \(\phi_*\)：将 Gauss–Legendre 节点映射到 \([0,2\pi]\)，并包含 \(1/(2\pi)\) 方位角平均。

当前天然氙基准使用 \(8\times8\times4\) 的 \(W^2,z,\phi_*\) 求积阶数；代表点与 \(16\times16\times8\) 比较。四组 Xe-131 固定速度 benchmark 另有更高阶 spot checks，具体见正文和对应 CSV。

### A.6 \(\chi_2\) pole width 的条件性

若明确采用 Dirac 费米子、实标量、纯 scalar off-diagonal Yukawa 耦合，并且唯一开放衰变道为

\[
\chi_2\rightarrow\chi_1s,
\]

则

\[
\Gamma_{\chi_2\to\chi_1s}
=
\frac{|g_2|^2}{16\pi m_{\chi_2}^3}
\sqrt{\lambda_K(m_{\chi_2}^2,m_{\chi_1}^2,m_s^2)}
\left[(m_{\chi_2}+m_{\chi_1})^2-m_s^2\right],
\]

其中有量纲 Källén 函数为

\[
\lambda_K(x,y,z)=x^2+y^2+z^2-2xy-2xz-2yz.
\]

这一宽度不是在未明确粒子场性质时自动成立的通用公式。当前程序的 pole-width 选项是上述条件下的计算；running-width 选项使用 \(\sqrt{W^2}\Gamma(\sqrt{W^2})\) 作为诊断性 Breit–Wigner 形式，不能替代包含完整 \(\Sigma_V,\Sigma_S\) 的 Dyson-resummed 传播子。

---
