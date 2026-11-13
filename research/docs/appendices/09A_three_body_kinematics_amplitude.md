> 所属主报告：[AFH v6.0 氙核响应与三体暗物质散射](../09_afh_xe131_three_body_scattering_natural_xenon.md)

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


### A.2.1 固定入射速度下的最大标量质量与最优反冲能量

前面的相空间开放条件给出
\[
m_s\le W_{\max}(E_R)-m_{\chi_1}.
\]
若固定入射速度，寻找该速度下允许的最大 \(m_s\)，等价于对 \(W_{\max}^2(E_R)\) 关于 \(E_R\) 最大化。这里
\[
Q(E_R)=\sqrt{2m_AE_R+E_R^2},
\qquad
W_{\max}^2=m_{\chi_1}^2+2p_{\chi_1}Q-2(E_\chi+m_A)E_R.
\]
因为 \(W_{\max}>0\)，最大化 \(W_{\max}\) 与最大化 \(W_{\max}^2\) 等价。求导得
\[
\frac{dW_{\max}^2}{dE_R}
=2p_{\chi_1}\frac{m_A+E_R}{Q}
-2(E_\chi+m_A).
\]
令导数为零，并定义
\[
B=E_\chi+m_A,\qquad x=m_A+E_R,
\]
则
\[
p_{\chi_1}x=BQ,\qquad Q^2=x^2-m_A^2.
\]
平方后
\[
p_{\chi_1}^2x^2=B^2(x^2-m_A^2),
\]
所以
\[
(B^2-p_{\chi_1}^2)x^2=B^2m_A^2.
\]
靶核静止系中
\[
B^2-p_{\chi_1}^2
=(E_\chi+m_A)^2-p_{\chi_1}^2
=m_{\chi_1}^2+m_A^2+2m_AE_\chi
=s_{\rm tot}.
\]
取物理正根，
\[
x=\frac{Bm_A}{\sqrt{s_{\rm tot}}},
\]
从而
\[
\boxed{
E_R^*=m_A\left(\frac{E_\chi+m_A}{\sqrt{s_{\rm tot}}}-1\right),
\qquad
Q^*=\frac{m_Ap_{\chi_1}}{\sqrt{s_{\rm tot}}}.
}
\]
将其代回 \(W_{\max}^2\)，得到
\[
W_{\max}^2(E_R^*)=(\sqrt{s_{\rm tot}}-m_A)^2.
\]
因此
\[
\boxed{
m_{s,\max}(v)
=\sqrt{s_{\rm tot}}-m_A-m_{\chi_1},
\quad
s_{\rm tot}=m_{\chi_1}^2+m_A^2+2m_AE_\chi.
}
\]
在 \(\beta\ll1\) 时，令
\[
\mu_A=\frac{m_{\chi_1}m_A}{m_{\chi_1}+m_A},
\]
可展开为
\[
m_{s,\max}\simeq\frac12\mu_A\beta^2,
\qquad
E_R^*\simeq
\frac{m_A}{2}
\left(\frac{m_{\chi_1}}{m_{\chi_1}+m_A}\right)^2\beta^2.
\]
这两个近似式展示了暗物质入射动能如何在核反冲与末态标量质量门槛之间分配。\(E_R^*\) 只最大化运动学质量上限；真实谱还乘有核响应、传播子和三体矩阵元，故该点一般不是事件率峰值。

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
### A.3.1 显式 Lorentz boost 与正交基构造

为避免“boost 到 \(K\) 静止系”只停留在操作描述，下面把实际使用的变换写成分量形式。记靶核静止系中的

\[
K^\mu=(K^0,\mathbf K),\qquad K^2=W^2,
\]

并定义

\[
\boldsymbol\beta_K=\frac{\mathbf K}{K^0},
\qquad
\beta_K=|\boldsymbol\beta_K|,
\qquad
\gamma_K=\frac{K^0}{W}=\frac{1}{\sqrt{1-\beta_K^2}}.
\]

对任意靶核静止系四矢量 \(a^\mu=(a^0,\mathbf a)\)，变换到 \(K\) 静止系的分量为

\[
\boxed{
a_*^0=\gamma_K(a^0-\boldsymbol\beta_K\cdot\mathbf a)
}
\]

以及

\[
\boxed{
\mathbf a_*=
\mathbf a+
\left[
\frac{\gamma_K-1}{\beta_K^2}
(\boldsymbol\beta_K\cdot\mathbf a)
-\gamma_K a^0
\right]\boldsymbol\beta_K
}.
\]

这里的符号对应于进入以速度 \(+\boldsymbol\beta_K\) 运动的 \(K\) 系；因此能量变换中出现负号。逆变换为

\[
\boxed{
a^0=\gamma_K(a_*^0+\boldsymbol\beta_K\cdot\mathbf a_*)
}
\]

和

\[
\boxed{
\mathbf a=
\mathbf a_*+
\left[
\frac{\gamma_K-1}{\beta_K^2}
(\boldsymbol\beta_K\cdot\mathbf a_*)
+\gamma_K a_*^0
\right]\boldsymbol\beta_K
}.
\]

这两组公式分别用于将入射动量 \(p^\mu\) 变换到 \(K\) 静止系，以及将构造出的 \(p_*'{}^\mu,k_*^\mu\) 变换回靶核静止系。变换后应有

\[
K_*^\mu=(W,\mathbf 0),\qquad
p_*'{}^\mu+k_*^\mu=K_*^\mu.
\]

当 \(\beta_K=0\) 时，上述含 \(\beta_K^{-2}\) 的表达按连续极限理解为恒等变换。

**正交基的一个明确构造方式**如下。先定义

\[
\hat{\mathbf e}_3=\frac{\mathbf p_*}{|\mathbf p_*|}.
\]

选取一个不与 \(\hat{\mathbf e}_3\) 平行的参考单位向量 \(\hat{\mathbf r}\)，例如优先取靶核静止系的固定 \(z\) 轴方向；若两者近乎平行，则改用固定 \(x\) 轴方向。随后作 Gram–Schmidt 正交化：

\[
\hat{\mathbf e}_1=
\frac{
\hat{\mathbf r}
-(\hat{\mathbf r}\cdot\hat{\mathbf e}_3)\hat{\mathbf e}_3
}{
\sqrt{1-(\hat{\mathbf r}\cdot\hat{\mathbf e}_3)^2}
},
\]

\[
\hat{\mathbf e}_2=\hat{\mathbf e}_3\times\hat{\mathbf e}_1.
\]

于是

\[
\hat{\mathbf e}_i\cdot\hat{\mathbf e}_j=\delta_{ij},
\qquad
\hat{\mathbf e}_1\times\hat{\mathbf e}_2=\hat{\mathbf e}_3.
\]

在这个基底下，标量方向为

\[
\hat{\mathbf k}_*
=z\hat{\mathbf e}_3+
\sqrt{1-z^2}
(\cos\phi_*\hat{\mathbf e}_1+\sin\phi_*\hat{\mathbf e}_2).
\]

参考向量的选择只决定横向坐标轴的零方位角。由于对完整的 \(0\le\phi_*<2\pi\) 区间积分，物理积分不依赖这一任意坐标选择；改变横向基底只会重新定义 \(\phi_*\) 的原点。

因此，完整的四动量构造可以按以下顺序理解：

1. 在靶核静止系给定 \(p,P,q\)，并由 \(K=p-q\) 得到子系统总动量；
2. 使用上述正向 boost 得到 \(p_*\)，并由其方向定义 \(\hat{\mathbf e}_3\)；
3. 根据 \(W,m_{\chi_1},m_s\) 得到两体衰变的 \(E_{s,*}\)、\(E_{\chi_1,*}\) 和 \(|\mathbf k_*|\)；
4. 使用 \(z,\phi_*\) 构造 \(\hat{\mathbf k}_*\)，从而得到 \(k_*^\mu\) 和 \(p_*'{}^\mu\)；
5. 使用逆 boost 得到靶核静止系中的 \(k^\mu,p'^\mu\)，并取 \(P'=P+q\)。

这样构造后，子系统关系 \(p'+k=K\) 与总四动量守恒 \(p+P=p'+P'+k\) 在解析上相互一致。数值程序中的质量壳和四动量闭合检查属于对这一构造的实现检查，不改变上述运动学定义。


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

## A.4.1 从不变相空间得到 Eq. (6) 的整体前因子

这一节把正文中 \(256\pi^3\) 的系数与相空间归一化联系起来。记初态总不变量为

\[
s_{\rm tot}=(p+P)^2,\qquad
\Lambda_{\rm in}\equiv
\sqrt{\lambda_K(s_{\rm tot},m_{\chi_1}^2,m_A^2)}.
\]

靶核静止系中

\[
\Lambda_{\rm in}=2m_Ap_{\chi_1}.
\]

不变通量因子为

\[
4\sqrt{(p\cdot P)^2-m_{\chi_1}^2m_A^2}
=2\Lambda_{\rm in}
=4m_Ap_{\chi_1}.
\]

所以

\[
d\sigma=
\frac{|\mathcal M|^2}{2\Lambda_{\rm in}}d\Phi_3.
\]

利用 A.4 的相空间分解，第一段两体相空间在固定 \(t=q^2\) 下满足

\[
\frac{d\Phi_2(p+P;P',K)}{dt}
=\frac{1}{8\pi\Lambda_{\rm in}}.
\]

由于

\[
t=-2m_AE_R,\qquad
\left|\frac{dt}{dE_R}\right|=2m_A,
\]

得到

\[
\frac{d\Phi_2(p+P;P',K)}{dE_R}
=
\frac{m_A}{4\pi\Lambda_{\rm in}}
=\frac{1}{8\pi p_{\chi_1}}.
\]

第二段两体相空间为

\[
d\Phi_2(K;p',k)
=
\frac{|\mathbf k_*|}{16\pi^2W}d\Omega_*
=
\frac{\sqrt{\lambda_{\rm dim}}}{32\pi^2}
\,dz\,d\phi_*.
\]

因此

\[
\frac{d\Phi_3}
{dE_R\,dW^2\,dz\,d\phi_*}
=
\frac{1}{2\pi}
\frac{1}{8\pi p_{\chi_1}}
\frac{\sqrt{\lambda_{\rm dim}}}{32\pi^2}
=
\frac{\sqrt{\lambda_{\rm dim}}}
{512\pi^4p_{\chi_1}}.
\]

将方位角积分写成平均，

\[
\int_0^{2\pi}d\phi_*\,\mathcal L_{00}
=
2\pi\langle\mathcal L_{00}\rangle_{\phi_*},
\]

便得到

\[
\frac{d\Phi_3}{dE_R\,dW^2\,dz}
\mathcal L_{00}
\longrightarrow
\frac{\sqrt{\lambda_{\rm dim}}}
{256\pi^3p_{\chi_1}}
\langle\mathcal L_{00}\rangle_{\phi_*}.
\]

在靶核非相对论极限，矢量核电荷流的时间分量为

\[
J_A^0\simeq 2m_A.
\]

将物理核响应 \(R_A(E_R)\)、粒子耦合和矢量传播子放入振幅平方，可写为

\[
|\mathcal M|^2
=
\frac{
4m_A^2(g_1g_2g_{VN})^2R_A(E_R)
}{
(m_V^2+2m_AE_R)^2
}
\mathcal L_{00}.
\]

再乘不变通量因子 \(1/(2\Lambda_{\rm in})=1/(4m_Ap_{\chi_1})\)，得到

\[
\frac{4m_A^2}{4m_Ap_{\chi_1}}
\frac{1}{256\pi^3p_{\chi_1}}
=
\frac{m_A}{256\pi^3p_{\chi_1}^2}.
\]

最终即为正文 Eq. (6)：

\[
\boxed{
\frac{d\sigma_A}{dE_R}
=
\frac{
m_A(g_1g_2g_{VN})^2R_A(E_R)
}{
256\pi^3p_{\chi_1}^2(m_V^2+2m_AE_R)^2
}
I_6
}.
\]

这个推导采用的条件是：靶核矢量电荷流保留 leading non-relativistic 时间分量 \(2m_A\)，核结构和核自旋平均已经包含在物理响应 \(R_A\) 中，且 \(\phi_*\) 使用平均而非未归一化积分。若改变这些定义，不能继续原样沿用 \(256\pi^3\) 前因子。

### A.4.2 独立审计：从单粒子不变测度逐项重建 \(256\pi^3\)

本节不把 A.4.1 的中间结果作为输入，而从单粒子 Lorentz-invariant 测度重新计算两体相空间、两个角变量的处理方式、通量因子及核电荷流归一化。所有 \(2\pi\) 因子均显式保留。

#### (i) 从单粒子测度得到两体相空间

采用
\[
d\Pi_i=\frac{d^3\mathbf p_i}{(2\pi)^3\,2E_i},
\qquad
d\Phi_2(Q;a,b)
=(2\pi)^4\delta^{(4)}(Q-p_a-p_b)d\Pi_a d\Pi_b .
\]
在 \(Q\) 静止系，令 \(M=\sqrt{Q^2}\)。积分掉三维动量 delta 函数后，
\[
d\Phi_2
=\frac{p^2dp\,d\Omega}{16\pi^2 E_aE_b}
\delta(M-E_a-E_b).
\]
又有
\[
\frac{d(E_a+E_b)}{dp}
=p\left(\frac1{E_a}+\frac1{E_b}\right)
=\frac{pM}{E_aE_b}.
\]
完成径向动量积分得到
\[
\boxed{
d\Phi_2(Q;a,b)
=\frac{p_*}{16\pi^2M}d\Omega
=\frac{\sqrt{\lambda_K(M^2,m_a^2,m_b^2)}}{32\pi^2M^2}d\Omega .
}
\]
因此全立体角积分为
\[
\int d\Phi_2
=\frac{\sqrt{\lambda_K(M^2,m_a^2,m_b^2)}}{8\pi M^2},
\]
与标准两体不变相空间归一化一致。

#### (ii) 第一段两体过程：显式计算 \(t\) 的 Jacobian

令
\[
s_{\rm tot}=(p+P)^2,\qquad
\Lambda_{\rm in}
=\sqrt{\lambda_K(s_{\rm tot},m_{\chi_1}^2,m_A^2)}.
\]
在初态质心系中，
\[
p_i^*=\frac{\Lambda_{\rm in}}{2\sqrt{s_{\rm tot}}},
\qquad
p_f^*=\frac{\sqrt{\lambda_K(s_{\rm tot},m_A^2,W^2)}}{2\sqrt{s_{\rm tot}}}.
\]
对 \(p+P\to P'+K\)，两体相空间为
\[
d\Phi_2
=\frac{p_f^*}{16\pi^2\sqrt{s_{\rm tot}}}
\,d\cos\theta\,d\phi_q.
\]
这里 \(\theta\) 是初态轴与末态核动量之间的质心系散射角。由
\[
t=(P'-P)^2,\qquad
\left|\frac{dt}{d\cos\theta}\right|=2p_i^*p_f^*
\]
可得
\[
\frac{d\Phi_2}{dt\,d\phi_q}
=\frac{1}{32\pi^2\sqrt{s_{\rm tot}}p_i^*}
=\frac{1}{16\pi^2\Lambda_{\rm in}}.
\]
对 \(\phi_q\) 积分给出
\[
\boxed{
\frac{d\Phi_2}{dt}
=\frac{1}{8\pi\Lambda_{\rm in}}.
}
\]
这一步已经消耗了第一段两体过程的 \(2\pi\) 方位角因子。它只在未极化靶核、相干且仅保留 \(J_A^0\) 的旋转对称近似下成立；若保留靶极化或横向核流，必须保留 \(\phi_q\)，不能直接使用这一已积分表达式。

核质量壳条件 \(P'^2=P^2=m_A^2\) 给出
\[
t=q^2=-2m_AE_R,\qquad
\left|\frac{dt}{dE_R}\right|=2m_A.
\]
靶核静止系还满足
\[
\Lambda_{\rm in}=2m_Ap_{\chi_1}.
\]
所以
\[
\boxed{
\frac{d\Phi_2(p+P;P',K)}{dE_R}
=\frac{2m_A}{8\pi\Lambda_{\rm in}}
=\frac{1}{8\pi p_{\chi_1}}.
}
\]

#### (iii) 第二段两体过程：\((z,\phi_*)\) 的 Jacobian

在 \(K\) 静止系，令 \(W=\sqrt{W^2}\)，则
\[
|\mathbf k_*|
=\frac{\sqrt{\lambda_K(W^2,m_{\chi_1}^2,m_s^2)}}{2W}.
\]
取
\[
z=\cos\theta_*,\qquad d\Omega_*=dz\,d\phi_*,
\]
并定义
\[
\lambda_{\rm dim}(W^2,m_{\chi_1}^2,m_s^2)
=\frac{\lambda_K(W^2,m_{\chi_1}^2,m_s^2)}{W^4}.
\]
正文 main.tex 与 Python 的 lambda_dimensionless 使用的函数正是
\[
\lambda_{\rm paper}(W^2,m_{\chi_1}^2,m_s^2)
=
\left[1-\frac{(m_{\chi_1}+m_s)^2}{W^2}\right]
\left[1-\frac{(m_{\chi_1}-m_s)^2}{W^2}\right]
=\lambda_{\rm dim}.
\]
因此正文的 \(\sqrt{\lambda}\)、附录中的 \(\sqrt{\lambda_{\rm dim}}\) 与程序的 \texttt{lambda_dimensionless} 是同一个无量纲量；这里没有遗漏 \(W^{-2}\) 或额外的 \(W^2\) 因子。
由 (i) 得
\[
\boxed{
d\Phi_2(K;p',k)
=\frac{\sqrt{\lambda_{\rm dim}}}{32\pi^2}
\,dz\,d\phi_*.
}
\]
这里没有额外的 \(\sin\theta_*\)：它已通过 \(z=\cos\theta_*\) 的变量变换吸收，因为 \(d\cos\theta_*=-\sin\theta_*d\theta_*\)。

#### (iv) 合并三体相空间：保留未积分的 \(\phi_*\)

插入中间态不变质量的标准分解
\[
d\Phi_3
=\frac{dW^2}{2\pi}
d\Phi_2(p+P;P',K)d\Phi_2(K;p',k).
\]
这里的积分变量就是 \(W^2\)，所以分解式不产生额外的 \(2W\)；只有将积分变量另行改成 \(W\) 时，才需要使用 \(dW^2=2W\,dW\)。末态 \(p'\) 与 \(k\) 是不同粒子，因此没有相同末态的 \(1/2!\) 对称因子。
结合 (ii)、(iii)，得到
\[
\boxed{
\frac{d\Phi_3}
{dE_R\,dW^2\,dz\,d\phi_*}
=
\frac{1}{2\pi}
\frac{1}{8\pi p_{\chi_1}}
\frac{\sqrt{\lambda_{\rm dim}}}{32\pi^2}
=
\frac{\sqrt{\lambda_{\rm dim}}}
{512\pi^4p_{\chi_1}}.
}
\]
至此，所有未积分的相空间因子已经确定；尚未对 \(\phi_*\) 作任何平均。

#### (v) 将 \(\phi_*\) 积分改写为平均

论文定义
\[
\left\langle\mathcal L_{00}\right\rangle_{\phi_*}
=\frac{1}{2\pi}\int_0^{2\pi}d\phi_*\,
\mathcal L_{00}.
\]
故
\[
\int_0^{2\pi}d\phi_*\,\mathcal L_{00}
=2\pi\left\langle\mathcal L_{00}\right\rangle_{\phi_*}.
\]
将其乘到 (iv) 的相空间测度上：
\[
\boxed{
\frac{\sqrt{\lambda_{\rm dim}}}{512\pi^4p_{\chi_1}}
\int_0^{2\pi}d\phi_*\,\mathcal L_{00}
=
\frac{\sqrt{\lambda_{\rm dim}}}{256\pi^3p_{\chi_1}}
\left\langle\mathcal L_{00}\right\rangle_{\phi_*}.
}
\]
因此，从 \(512\pi^4\) 到 \(256\pi^3\) 的唯一变化，是把未归一化的方位角积分替换成 \(1/(2\pi)\) 平均；不能再额外乘 \(2\pi\)。

#### (vi) 通量因子与核电荷流

不变通量为
\[
F=4\sqrt{(p\cdot P)^2-m_{\chi_1}^2m_A^2}
=4m_Ap_{\chi_1}.
\]
所以
\[
d\sigma=\frac{|\mathcal M|^2}{4m_Ap_{\chi_1}}d\Phi_3.
\]
在本文的 leading non-relativistic 核电荷近似下，
\[
J_A^0\simeq 2m_A,
\]
而 \(\mathcal L_{00}\) 已按
\[
\mathcal L_{00}
=\frac12\sum_{s_i,s_f}
|\bar u(p')\Gamma^0u(p)|^2
\]
对初态暗物质自旋平均、对末态自旋求和。核初态自旋平均及求和包含在 \(R_A\) 中。因此振幅平方写为
\[
|\mathcal M|^2
=
\frac{4m_A^2(g_1g_2g_{VN})^2R_A(E_R)}
{(m_V^2-t)^2}\mathcal L_{00},
\qquad
m_V^2-t=m_V^2+2m_AE_R.
\]
结合 (v) 与通量因子，整体质量和动量因子为
\[
\frac{4m_A^2}{4m_Ap_{\chi_1}}
\frac{1}{256\pi^3p_{\chi_1}}
=
\boxed{\frac{m_A}{256\pi^3p_{\chi_1}^2}}.
\]
故
\[
\boxed{
\frac{d\sigma_A}{dE_R}
=
\frac{m_A(g_1g_2g_{VN})^2R_A(E_R)}
{256\pi^3p_{\chi_1}^2(m_V^2+2m_AE_R)^2}
I_6,
}
\]
其中
\[
I_6=
\int_{W_{\min}^2}^{W_{\max}^2}dW^2
\sqrt{\lambda_{\rm dim}}
\int_{-1}^{1}dz\,
\left\langle\mathcal L_{00}\right\rangle_{\phi_*}.
\]

#### (vii) 与正文及 Python 实现逐项对应

| 理论量 | 解析表达式 | 程序对应 |
|---|---|---|
| 中间态质量测度 | \(dW^2/(2\pi)\) | \texttt{wvals}, \texttt{wweights} |
| 第一段反冲相空间 | \(1/(8\pi p_{\chi_1})\) | 已进入 Eq. (6) 外部系数 |
| 第二段极角测度 | \(dz\) | \texttt{xz}, \texttt{wz} |
| 第二段方位角平均 | \((2\pi)^{-1}\int d\phi_*\) | \texttt{phis}, \texttt{phiweights=0.5*wp} |
| 两体末态动量 | \(\sqrt{\lambda_{\rm dim}}\) | \texttt{lambda_dimensionless} |
| 自旋平均 | \(\frac12\sum_{\rm spins}\) | \texttt{spin_trace} 中的 \texttt{/2.} |
| 相空间积分 | \(I_6\) | \texttt{reduced_kernel} |

特别地，Gauss–Legendre 变量变换
\[
\phi_i=\pi(x_i+1),\qquad d\phi=\pi dx
\]
给出
\[
\frac{1}{2\pi}\int_0^{2\pi}f(\phi)d\phi
=\frac12\int_{-1}^{1}f(\pi(x+1))dx
\simeq\sum_i\frac{w_i}{2}f(\phi_i).
\]
因此程序中的 \texttt{phiweights=0.5*wp} 正是方位角平均权重，且其权重和为 1；\texttt{z} 方向仍使用未平均的积分权重，其权重和为 2。

#### (viii) 维度与适用条件

\[
[d\Phi_3]=\mathrm{GeV}^2,\qquad
\left[
\frac{d\Phi_3}{dE_R\,dW^2\,dz\,d\phi_*}
\right]=\mathrm{GeV}^{-1},
\]
与 (iv) 的 \(1/p_{\chi_1}\) 一致。又有
\[
[I_6]=\mathrm{GeV}^2,\qquad
\left[\frac{d\sigma}{dE_R}\right]=\mathrm{GeV}^{-3}.
\]

**独立推导结论：** 在未极化靶核、相干且仅保留 \(J_A^0\) 的近似、初态暗物质自旋平均已经包含于 \(\mathcal L_{00}\)、核自旋处理已经包含于 \(R_A\)，以及 \(\phi_*\) 采用平均定义的条件下，整体系数确为 \(256\pi^3\)。这一系数来自 Lorentz-invariant 三体相空间、反冲能量 Jacobian、通量和核电荷流；它与 AFH 响应的因子 4 是完全不同的归一化来源。


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


### A.6.1 从 Dirac 标量 Yukawa 振幅推导条件性二体宽度

明确采用
\[
\mathcal L_{\chi\chi s}
=-g_2s\,\bar\chi_1\chi_2
-g_2^*s\,\bar\chi_2\chi_1
\]
的纯标量、非对角 Yukawa 相互作用，并考虑
\[
\chi_2(P)\longrightarrow\chi_1(p)+s(k),
\qquad
P^2=m_{\chi_2}^2,\quad
p^2=m_{\chi_1}^2,\quad
k^2=m_s^2.
\]
树级振幅为
\[
\mathcal M=g_2\,\bar u_1(p)u_2(P).
\]
对初态 \(\chi_2\) 自旋平均、末态 \(\chi_1\) 自旋求和，使用
\[
\sum_su_s(p)\bar u_s(p)=\slashed p+m
\]
得到
\[
\begin{aligned}
\overline{|\mathcal M|^2}
&=\frac{|g_2|^2}{2}
\operatorname{Tr}\!\left[
(\slashed p+m_{\chi_1})(\slashed P+m_{\chi_2})
\right]\\
&=2|g_2|^2(p\cdot P+m_{\chi_1}m_{\chi_2})\\
&=|g_2|^2
\left[(m_{\chi_2}+m_{\chi_1})^2-m_s^2\right],
\end{aligned}
\]
其中最后一步使用
\[
2p\cdot P=m_{\chi_2}^2+m_{\chi_1}^2-m_s^2.
\]
在 \(\chi_2\) 静止系，二体末态动量大小为
\[
|\mathbf p_*|
=\frac{\sqrt{\lambda_K(m_{\chi_2}^2,m_{\chi_1}^2,m_s^2)}}
{2m_{\chi_2}},
\]
且角积分后的二体衰变宽度为
\[
\Gamma=\frac{|\mathbf p_*|}{8\pi m_{\chi_2}^2}
\overline{|\mathcal M|^2}.
\]
代入即得
\[
\boxed{
\Gamma_{\chi_2\to\chi_1s}
=\frac{|g_2|^2}{16\pi m_{\chi_2}^3}
\sqrt{\lambda_K(m_{\chi_2}^2,m_{\chi_1}^2,m_s^2)}
\left[(m_{\chi_2}+m_{\chi_1})^2-m_s^2\right].
}
\]
该式仅在 \(m_{\chi_2}\ge m_{\chi_1}+m_s\) 时对应开放衰变道。末态 \(\chi_1\) 与 \(s\) 是不同粒子，不存在额外的 \(1/2!\) 因子；若有其他开放衰变道，总宽度应将它们的部分宽度相加。

这不是任意 Dirac/Majorana、标量/赝标量或完整 UV 模型的通用宽度。本文当前 pole prescription 采用 Dirac 外部态、实标量、纯标量耦合和单一开放衰变道。该宽度只进入可能接近极点的 after 传播子；它不改变 \(W_{\min}\) 或三体相空间边界，也不能替代完整的 Dyson 自能计算。对应代码入口为 \(\texttt{chi2\_width\_dirac\_scalar}\)，详见索引 F12。

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

