> 所属主报告：[AFH v6.0 氙核响应与三体暗物质散射](../09_afh_xe131_three_body_kernel_natural_xenon_halo_2026-11-11.md)

# 附录 A：三体运动学、相空间边界与 Dirac 振幅

## A.1 研究对象、约定与四动量

考虑正文 Eq. (6) 对应的过程

\[
\chi_1(p)+A(P)\longrightarrow \chi_1(p')+A(P')+s(k),
\]

其中 \(A\) 是质量为 \(m_A\) 的初态静止核，\(s\) 是质量为 \(m_s\) 的末态标量，暗物质初态质量为 \(m_{\chi_1}\)，中间态质量为

\[
m_{\chi_2}=m_{\chi_1}+\Delta m.
\]

采用自然单位制 \(\hbar=c=1\)、度规 \(g_{\mu\nu}=\mathrm{diag}(+,-,-,-)\)。程序输入的质量、能量和动量均以 GeV 表示；速度先以 km/s 输入，再转换为 \(\beta=v/c\)。

在靶核静止系取

\[
P^\mu=(m_A,\mathbf 0),\qquad
p^\mu=(E_\chi,0,0,p_\chi),
\]

\[
E_\chi=m_{\chi_1}\gamma,\qquad
p_\chi=m_{\chi_1}\gamma\beta,\qquad
\gamma=(1-\beta^2)^{-1/2}.
\]

定义核反冲四动量

\[
q^\mu=P'^\mu-P^\mu=(E_R,\mathbf q).
\]

由于初末核均在质量壳上，

\[
P'^2=P^2=m_A^2
\]

给出

\[
q^2=(P'-P)^2=-2m_AE_R.
\]

因此，核反冲三动量模长为

\[
\boxed{Q\equiv|\mathbf q|=\sqrt{2m_AE_R+E_R^2}},
\]

而不是在所有精度约定下都可以直接写成 \(\sqrt{2m_AE_R}\)。后者是 \(E_R\ll m_A\) 时的非相对论近似。

定义暗物质与标量组成的末态子系统总动量

\[
K^\mu=p^\mu-q^\mu=p'^\mu+k^\mu,
\qquad W^2\equiv K^2=(p'+k)^2.
\]

这里 \(W\) 是子系统的不变质量，\(W^2\) 是正文和数值积分中实际使用的积分变量。

## A.2 \(W_{\min}^2\) 与 \(W_{\max}^2\) 的推导

由 \(K=p-q\)，

\[
\begin{aligned}
W^2
&=(p-q)^2\\
&=p^2-2p\cdot q+q^2\\
&=m_{\chi_1}^2-2E_\chi E_R
  +2p_\chi Q\cos\theta_q-2m_AE_R\\
&=m_{\chi_1}^2+2p_\chi Q\cos\theta_q
  -2(E_\chi+m_A)E_R,
\end{aligned}
\]

其中 \(\theta_q\) 是入射暗物质三动量与核反冲三动量之间的夹角。

固定 \(v\) 和 \(E_R\) 后，\(\cos\theta_q\in[-1,1]\)。因此允许的最大 \(W^2\) 在 \(\cos\theta_q=1\) 处取得：

\[
\boxed{
W_{\max}^2=
m_{\chi_1}^2+
2p_{\chi_1}\sqrt{2m_AE_R+E_R^2}
-2(E_{\chi_1}+m_A)E_R
}.
\]

另一方面，末态子系统必须能够产生一对壳上粒子 \(\chi_1+s\)。由两体阈值，

\[
W\ge m_{\chi_1}+m_s,
\]

故

\[
\boxed{W_{\min}^2=(m_{\chi_1}+m_s)^2}.
\]

在给定 \((v,E_R)\) 下，积分区间开放的必要条件为

\[
W_{\max}^2\ge W_{\min}^2.
\]

若 \(W_{\max}^2\le W_{\min}^2\)，当前点的三体相空间关闭，程序返回零，不对负宽度积分区间作数值求积。

对给定的 \(W^2\)，核反冲方向由

\[
\boxed{
\cos\theta_q=
\frac{W^2-m_{\chi_1}^2+
2(E_\chi+m_A)E_R}
{2p_{\chi_1}Q}
}
\]

唯一确定。数值构造还检查 \(|\cos\theta_q|\le1\)，以排除不物理点。

## A.3 在 \(K\) 静止系构造三体末态

给定 \(W^2\) 后，子过程

\[
K\longrightarrow\chi_1(p')+s(k)
\]

在 \(K\) 静止系中是普通两体运动学。定义有量纲 Källén 函数

\[
\lambda_K(x,y,z)=x^2+y^2+z^2-2xy-2xz-2yz
\]

以及本文使用的无量纲函数

\[
\lambda_{\rm dim}(W^2,m_{\chi_1}^2,m_s^2)
=
\frac{\lambda_K(W^2,m_{\chi_1}^2,m_s^2)}{W^4}.
\]

于是

\[
|\mathbf k_*|
=\frac{\sqrt{\lambda_K(W^2,m_{\chi_1}^2,m_s^2)}}{2W}
=\frac W2\sqrt{\lambda_{\rm dim}},
\]

\[
E_{s,*}=\frac{W^2-m_{\chi_1}^2+m_s^2}{2W},
\qquad
E_{\chi_1,*}=\frac{W^2+m_{\chi_1}^2-m_s^2}{2W}.
\]

星号表示 \(K\) 静止系。程序先在靶核静止系构造 \(p,q,K\)，再以

\[
\boldsymbol\beta_K=\frac{\mathbf K}{K^0}
\]

将入射 \(p\) boost 到 \(K\) 静止系。其空间方向定义为极轴：

\[
\hat{\mathbf e}_3=
\frac{\mathbf p_*}{|\mathbf p_*|}.
\]

再选择与 \(\hat{\mathbf e}_3\) 正交的 \(\hat{\mathbf e}_1,\hat{\mathbf e}_2\)，构造标量方向

\[
\hat{\mathbf k}_*
=
z\hat{\mathbf e}_3+
\sqrt{1-z^2}
\left(\cos\phi_*\hat{\mathbf e}_1+
\sin\phi_*\hat{\mathbf e}_2\right),
\]

其中

\[
\boxed{z=\cos\theta_*=
\hat{\mathbf k}_*\cdot\hat{\mathbf p}_*},
\qquad -1\le z\le1,\qquad 0\le\phi_*<2\pi.
\]

因此 \(z\) 是标量在 \(\chi_1s\) 子系统静止系中的极角余弦；它不是靶核静止系中 \(\mathbf q\) 与 \(\mathbf p\) 的夹角余弦 \(\cos\theta_q\)。

末态四动量在 \(K\) 静止系中取为

\[
k_*^\mu=(E_{s,*},|\mathbf k_*|\hat{\mathbf k}_*),
\]

\[
p_*'{}^\mu=(E_{\chi_1,*},-|\mathbf k_*|\hat{\mathbf k}_*).
\]

将二者 boost 回靶核静止系后，逐点满足

\[
p^2=p'^2=m_{\chi_1}^2,\qquad
k^2=m_s^2,\qquad
P'^2=m_A^2,
\]

\[
p+P=p'+P'+k,\qquad K^2=W^2.
\]

这就是程序中末态四动量构造函数的逻辑。

## A.4 为什么选取 \((W^2,z,\phi_*)\) 作为积分变量

三体相空间可以按中间子系统的不变质量分解：

\[
d\Phi_3(p+P;P',p',k)
=
\frac{dW^2}{2\pi}\,
d\Phi_2(p+P;P',K)\,
d\Phi_2(K;p',k).
\]

在固定核反冲能量 \(E_R\) 时，\(Q=|\mathbf q|\) 已确定；第一段两体运动学的极角由 \(W^2\) 唯一决定，因为

\[
\frac{dW^2}{d\cos\theta_q}=2p_{\chi_1}Q.
\]

第二段两体衰变的两个方向自由度正好由 \(z=\cos\theta_*\) 和 \(\phi_*\) 参数化。对未极化靶核和本文采用的相干核电荷近似，核反冲方位角可通过旋转对称性积分掉。因此固定 \(E_R\) 后，\((W^2,z,\phi_*)\) 是一组自然且无冗余的三体积分变量。

正文把方位角写成平均：

\[
\langle\mathcal L_{00}\rangle_{\phi_*}
=
\frac{1}{2\pi}\int_0^{2\pi}
d\phi_*\,\mathcal L_{00}.
\]

程序的 reduced kernel 为

\[
\boxed{
I_6=
\int_{W_{\min}^2}^{W_{\max}^2}dW^2
\sqrt{\lambda_{\rm dim}}
\int_{-1}^{1}dz\,
\langle\mathcal L_{00}\rangle_{\phi_*}
}.
\]

\(dW^2\) 的单位是 GeV\(^2\)，\(\lambda_{\rm dim}\) 与自旋迹无量纲，因此 \(I_6\) 的单位是 GeV\(^2\)。相空间分解中的常数、Jacobian 与正文定义共同决定 Eq. (6) 的整体 \(256\pi^3\) 系数；不能在 reduced kernel 外再次重复加入已经包含在正文 prefactor 中的相空间常数。

## A.5 两张辐射图、振幅与干涉项

正文矢量流的两个图分别对应标量在矢量交换前、后从暗物质费米子线上辐射：

\[
\Gamma^\mu=\Gamma^\mu_{\rm before}+\Gamma^\mu_{\rm after},
\]

\[
\Gamma^\mu_{\rm before}
=
\frac{\gamma^\mu(\slashed p-\slashed k+m_{\chi_2})}
{(p-k)^2-m_{\chi_2}^2},
\]

\[
\Gamma^\mu_{\rm after}
=
\frac{(\slashed p'+\slashed k+m_{\chi_2})\gamma^\mu}
{W^2-m_{\chi_2}^2+i m_{\chi_2}\Gamma_{\chi_2}}.
\]

靶核静止系中核电荷流取时间分量 \(\Gamma^0\)。对于 Dirac 初末态，初态自旋平均、末态自旋求和为

\[
\mathcal L_{00}
=
\frac12\sum_{s,s'}
\left|\bar u_{s'}(p')\Gamma^0u_s(p)\right|^2.
\]

利用完备关系

\[
\sum_s u_s(p)\bar u_s(p)=\slashed p+m_{\chi_1},
\]

可写成

\[
\boxed{
\mathcal L_{00}
=
\frac12\operatorname{Tr}
\left[
(\slashed p'+m_{\chi_1})
\Gamma^0
(\slashed p+m_{\chi_1})
\overline{\Gamma}^{\,0}
\right]
},
\]

\[
\overline{\Gamma}^{\,0}
=\gamma^0(\Gamma^0)^\dagger\gamma^0.
\]

程序使用 Dirac 表象：

\[
\gamma^0=
\begin{pmatrix}I&0\\0&-I\end{pmatrix},
\qquad
\gamma^i=
\begin{pmatrix}0&\sigma_i\\-\sigma_i&0\end{pmatrix},
\]

并定义

\[
\slashed p=\gamma^0p^0-\gamma^1p^1-\gamma^2p^2-\gamma^3p^3.
\]

令

\[
\mathcal L_b=\mathcal L(\Gamma_{\rm before}^0),\qquad
\mathcal L_a=\mathcal L(\Gamma_{\rm after}^0),
\]

则完整结果为

\[
\mathcal L_{00}
=\mathcal L_b+\mathcal L_a+\mathcal L_{\rm int},
\]

\[
\mathcal L_{\rm int}
=
\frac12\operatorname{Tr}
\left[
(\slashed p'+m)
\left(
\Gamma_b^0(\slashed p+m)\bar\Gamma_a^0+
\Gamma_a^0(\slashed p+m)\bar\Gamma_b^0
\right)
\right].
\]

代码通过完整振幅的迹减去两个单图迹得到干涉项。两张图必须先在振幅层面相加；把两张图的平方非相干相加会丢失干涉贡献。

只有第二个传播子可能接近 \(\chi_2\) 极点，因为它的内部动量为 \(p'+k=K\)，不变量为 \(W^2\)。第一个内部动量是 \(p-k\)，对未来指向的壳上 \(p,k\) 有

\[
(p-k)^2
=m_{\chi_1}^2+m_s^2-2p\cdot k
\le(m_{\chi_1}-m_s)^2<m_{\chi_2}^2.
\]

因此当前实现只在 after 图的传播子中放入 pole width。

## A.6 宽度约定与模型边界

若额外明确采用 Dirac 费米子、实标量、纯 scalar off-diagonal Yukawa 耦合，并假设唯一开放衰变道为 \(\chi_2\to\chi_1s\)，则

\[
\Gamma_{\chi_2\to\chi_1s}
=
\frac{|g_2|^2}{16\pi m_{\chi_2}^3}
\sqrt{\lambda_K(m_{\chi_2}^2,m_{\chi_1}^2,m_s^2)}
\left[(m_{\chi_2}+m_{\chi_1})^2-m_s^2\right].
\]

这是一条带有明确场论假设的条件性宽度，不是未指定 Dirac/Majorana 性质时的通用结果。程序的 pole 选项在极点质量处使用该宽度；running 选项采用 \(W\Gamma(W)\) 的诊断性 Breit–Wigner 虚部。后者不能替代包含完整 \(\Sigma_V,\Sigma_S\) 的 Dyson-resummed 传播子。

论文参数空间还要求可达 halo 速度下 \(W_{\max}<m_{\chi_2}\)，以排除真实 \(\chi_2\) 产生。这个全局参数筛选是独立的运动学审计；不能把它误认为 reduced kernel 对所有输入自动执行的通用保护。

当前实现明确采用 Dirac 外部自旋子。原始模型文本尚未把 \(\chi_{1,2}\) 的 Dirac/Majorana 性质和完整 CP/手征约定全部固定，因此 Majorana 版本不在当前结果的自动适用范围内。

## A.7 求积、数值检查与复现入口

程序使用 Gauss–Legendre 求积：

- \(W^2\)：把节点从 \([-1,1]\) 线性映射到 \([W_{\min}^2,W_{\max}^2]\)；
- \(z\)：直接在 \([-1,1]\) 积分；
- \(\phi_*\)：令 \(\phi_*=\pi(x+1)\)，权重为原 Gauss–Legendre 权重的一半，从而实现 \(1/(2\pi)\) 方位角平均。

天然氙 selected-point 基准采用 \(8\times8\times4\)；六个代表性点与 \(16\times16\times8\) 对照，最大相对差异为 \(2.19\times10^{-4}\)。独立 Eq. (6) kernel 的代表性检查还包括：

1. 四动量守恒和所有外腿质量壳条件；
2. 在一个测试点，Dirac trace 与显式初末自旋态求和的相对差异小于 \(5\times10^{-15}\)；
3. before、after、interference 三项之和恢复完整迹；
4. 一个关闭相空间的测试返回严格零；
5. 提高 \(W^2,z,\phi_*\) 求积阶数后，reduced kernel 收敛。

主要代码：**research/figure2_full_reproduction/eq6_kernel.py**。

复现入口：

~~~bash
python -m unittest discover -s research/figure2_full_reproduction/tests -v
~~~

上述检查验证的是当前 Dirac 基准实现和被测试点，不自动证明所有参数点、所有传播子方案或未定义的 Majorana 模型都已验证。

