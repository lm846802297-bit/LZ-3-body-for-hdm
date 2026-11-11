# 模型、三体振幅与 Breit–Wigner 宽度

## 1. 研究问题与末态结构

本研究考虑

\[
\chi_1(p)+A(P)\to \chi_1(p')+A(P')+s(k),
\]

其中 \(A\) 是氙核，\(s\) 是轻标量。暗物质散射后仍处于 \(\chi_1\) 态；标量辐射使过程成为 \(2\to3\) 过程。它与通常的非弹性散射

\[
\chi_1+A\to\chi_2+A
\]

不同：后者的末态暗物质是重态，而这里的重态 \(\chi_2\) 是内部传播的虚态（在所选参数区间中要求不发生真实 on-shell 产生）。

研究的关键不是仅仅得到一个三体截面，而是判断三体相空间和内部传播子是否能形成足够硬的核反冲谱，同时避免在 LZ 其他能区产生过多事件。

## 2. Vector–vector 模型

用户提供的五页草稿在 II.A 中写出

\[
\mathcal L_{\rm int} =
g_1 V_\mu\bar\chi_2\gamma^\mu\chi_1
+g_2s\bar\chi_2\chi_1+\mathrm{h.c.}
+g_{Vq}V_\mu\sum_q\bar q\gamma^\mu q .
\tag{1}
\]

草稿假设 \(V_\mu\) 对各夸克味道普适，并定义

\[
\Delta m=m_{\chi_2}-m_{\chi_1},\qquad
g_{VN}=3g_{Vq}.
\tag{2}
\]

在等质子、等中子耦合的近似下，草稿采用 \(g_p=g_n=g_{VN}\)，从而使用相干核电荷响应。这里需要明确：\(g_{VN}=3g_{Vq}\) 是普适矢量夸克电荷下的核子价夸克计数结果；若模型含有非普适味道耦合、轴流或额外核子 form factor，关系和响应都需要重算。

**模型定义仍需补全：** 草稿没有明确说明 \(\chi_{1,2}\) 是 Dirac 还是 Majorana 费米子，也没有明确 \(g_1,g_2\) 的手征结构和 CP 约定。后续振幅、衰变宽度及对称因子必须以明确的场定义为基础。

## 3. Scalar–pseudoscalar 候选分支

草稿 II.B 另列出

\[
\mathcal L_{\rm int} =
g_1\phi\bar\chi_2\chi_1
+g_2s\bar\chi_2\chi_1+\mathrm{h.c.}
+i g_{\phi N}\phi\sum_{N=p,n}\bar N\gamma^5N .
\tag{3}
\]

这不是式 (1) 的简单换符号版本。核子端是赝标量流，通常会引入动量抑制、自旋响应及不同的核矩阵元。当前草稿式 (5)–(8) 的 \(\gamma^\mu\) 振幅和 coherent vector response 不能直接用于式 (3)。

**决策点：** 在开展大规模扫描前，先决定文章的主模型究竟是 vector–vector，还是 scalar–pseudoscalar。若两者都保留，应分别给出拉格朗日量、振幅、核响应、参数扫描和宇宙学关联。

## 4. 两张辐射图与式 (5)

草稿将标量 \(s\) 从暗物质线辐射的两种时间排序都保留。相应的费米子流写为

\[
\Gamma^\mu =
\gamma^\mu
\frac{\slashed p-\slashed k+m_{\chi_2}}
{(p-k)^2-m_{\chi_2}^2}
+
\frac{(\slashed p'+\slashed k+m_{\chi_2})\gamma^\mu}
{W^2-m_{\chi_2}^2+i m_{\chi_2}\Gamma_{\chi_2}},
\tag{4}
\]

其中

\[
W^2=(p'+k)^2,\qquad
\Gamma_{\chi_2}=\Gamma(\chi_2\to\chi_1s)
\]

是草稿采用的 pole width。两项必须在振幅层面相加，再平方；不能把两张图的截面简单相加，因为它们存在干涉。

### 4.1 为什么只有第二个传播子带宽度？

两个内部线的四动量不同：

- 第一项内部动量为 \(r_1=p-k\)；
- 第二项内部动量为 \(r_2=p'+k\)，其不变量就是 \(W^2\)。

对第一项，若 \(p\) 和 \(k\) 是未来指向的壳上四动量，则

\[
p\cdot k\ge m_{\chi_1}m_s,
\]

所以

\[
(p-k)^2
=m_{\chi_1}^2+m_s^2-2p\cdot k
\le (m_{\chi_1}-m_s)^2
<m_{\chi_1}^2
<m_{\chi_2}^2 .
\tag{5}
\]

因此第一条内部 \(\chi_2\) 线不可能到达其质量壳，分母不会出现 \((p-k)^2=m_{\chi_2}^2\) 的共振点。对这条线加入 Breit–Wigner 宽度没有必要。

第二项则不同。它的内部动量是两个未来指向末态粒子的和 \(p'+k\)，其不变量 \(W^2\) 可以在运动学允许的范围内接近 \(m_{\chi_2}^2\)。因此第二个传播子可能出现近共振增强，需要考虑不稳定粒子的自能/宽度效应。

这就是式 (4) 中第二个传播子有宽度、第一项没有宽度的物理原因，而不是人为地只给某一张图加修正。

### 4.2 近共振与“排除 on-shell 产生”并不矛盾

草稿要求

\[
W_{\max}<m_{\chi_2}
\tag{6}
\]

以排除可达 halo 相空间内的 on-shell \(\chi_2\) 产生。但这只说明极点没有真正进入积分区间，并不自动意味着 Breit–Wigner 项可以删掉。

当

\[
m_{\chi_2}^2-W^2
\lesssim m_{\chi_2}\Gamma_{\chi_2}
\tag{7}
\]

时，即使 \(W<m_{\chi_2}\)，宽度项仍可能影响传播子大小和谱形。反之，若整个积分区间满足

\[
m_{\chi_2}^2-W^2\gg m_{\chi_2}\Gamma_{\chi_2},
\]

则宽度修正应当很小。

因此每个参数点都应记录

\[
\delta_{\rm pole}^{\min}
=m_{\chi_2}^2-W_{\max}^2,
\qquad
\eta_\Gamma=
\frac{m_{\chi_2}\Gamma_{\chi_2}}
{\delta_{\rm pole}^{\min}},
\]

并直接比较有宽度和无宽度的积分结果。不能只凭 \(W_{\max}<m_{\chi_2}\) 就判断宽度无关紧要。

### 4.3 宽度方案需要进一步审计

草稿使用常数 pole-width 形式 \(i m_{\chi_2}\Gamma_{\chi_2}\)。这是一种近极点 Breit–Wigner 近似。若结果依赖近共振区，应检查：

1. \(\Gamma_{\chi_2}\) 是否随扫描中的 \(g_2,m_s,\Delta m\) 一起更新；
2. 常数 pole width 与能量依赖的 absorptive self-energy 是否给出一致结果；
3. 是否需要使用完整的 Dyson-resummed propagator；
4. 是否存在其他开放衰变道；
5. 近共振区是否需要处理 \(\chi_2\) 的级联产生、传播和衰变，而不能继续把它视为单纯虚态。

若 \(\chi_{1,2}\) 是 Dirac 费米子，且相互作用确实为纯标量 Yukawa 项 \(g_2s\bar\chi_1\chi_2+\mathrm{h.c.}\)，并且 \(\chi_2\to\chi_1s\) 是唯一开放道，则可用下式作独立宽度核查：

\[
\Gamma_{\chi_2\to\chi_1s}
=
\frac{|g_2|^2}{16\pi m_{\chi_2}^3}
\lambda^{1/2}(m_{\chi_2}^2,m_{\chi_1}^2,m_s^2)
\left[(m_{\chi_2}+m_{\chi_1})^2-m_s^2\right],
\tag{8}
\]

其中这里的 \(\lambda\) 是有质量量纲的 Källén 函数
\(\lambda(x,y,z)=x^2+y^2+z^2-2xy-2xz-2yz\)。该式是**带有上述 Dirac/纯标量/单一衰变道假设的核查式**，不能在场内容未明确前直接当作最终模型结果。

完整推导、数值基准、稳定的因式分解实现和单元测试见 `docs/08_chi2_decay_width.md`。

## 5. 三体运动学与积分范围

草稿定义

\[
q=P'-P,\qquad t=q^2=-2m_AE_R,
\qquad W^2=(p'+k)^2 .
\tag{9}
\]

三体不变量的积分下限为

\[
W_{\min}^2=(m_{\chi_1}+m_s)^2,
\tag{10}
\]

上限为

\[
W_{\max}^2 =
m_{\chi_1}^2
+2p_{\chi_1}\sqrt{2m_AE_R+E_R^2}
-2(E_{\chi_1}+m_A)E_R,
\tag{11}
\]

其中

\[
E_{\chi_1}=\frac{m_{\chi_1}}{\sqrt{1-v^2}},
\qquad p_{\chi_1}=E_{\chi_1}v .
\tag{12}
\]

式 (11) 是在给定入射速度和核反冲能量下，对末态 \(\chi_1+s\) 系统不变量取允许角度极值所得。实现时必须检查 \(W_{\max}^2\ge W_{\min}^2\)，否则该 \((v,E_R)\) 点没有相空间。

草稿中的无量纲函数为

\[
\lambda(w,m_1^2,m_2^2)=
\left[1-\frac{(m_1+m_2)^2}{w}\right]
\left[1-\frac{(m_1-m_2)^2}{w}\right].
\tag{13}
\]

这里 \(w\) 的量纲是质量平方。不要将其与式 (8) 的有量纲 Källén 函数混用。

## 6. 微分截面与核响应

草稿的 vector–vector 分支给出

\[
\begin{aligned}
\frac{d\sigma_A}{dE_R}
={}&
\frac{m_A(g_1g_2g_{VN})^2R_A(E_R)}
{256\pi^3p_{\chi_1}^2(m_V^2+2m_AE_R)^2}\\
&\times
\int_{W_{\min}^2}^{W_{\max}^2}dW^2\,
\sqrt{\lambda(W^2,m_{\chi_1}^2,m_s^2)}
\int_{-1}^{1}dz\,
\langle L^{00}\rangle_{\phi^*}.
\end{aligned}
\tag{14}
\]

其中

\[
L^{00}=\frac12\sum_{\rm spins}
|\bar u(p')\Gamma^0u(p)|^2
\]

是草稿所用的自旋平均/求和约定；\(z=\cos\theta^*\)，\(\phi^*\) 是 \(\chi_1s\) 系中的标量发射角，\(\langle\cdots\rangle_{\phi^*}\) 表示方位角平均。代码实现必须明确初态自旋平均和末态自旋求和，避免与式 (14) 中的 \(1/2\) 重复或遗漏。

在等质子和中子矢量耦合下，草稿采用

\[
R_A(E_R)=
\frac{4\pi W_M^{00}(y)}{2J_A+1},
\qquad
y=\frac{b_A^2m_AE_R}{2},
\qquad R_A(0)=A^2 .
\tag{15}
\]

这描述的是相干矢量电荷响应；高动量转移下不能简单用 \(A^2\) 替代完整核 form factor。

**数值验收要求：** 对式 (14) 独立检查量纲、相空间边界、Dirac trace、方位角积分、核响应归一化、初末态自旋因子及 \(m_V^2+2m_AE_R\) 的传播子因子。图上的谱线不是这些检查的替代品。

## 7. Halo 速度积分

式 (14) 是单核子/单核截面，不是探测器事件率。每单位探测器质量的理论反冲率应由 halo 分布积分，例如

\[
\frac{dR}{dE_R}
=
\frac{\rho_\chi}{m_{\chi_1}m_A}
\int d^3v\,f_{\rm lab}(\mathbf v)\,
v\,\frac{d\sigma_A(v,E_R)}{dE_R},
\tag{16}
\]

其中 \(f_{\rm lab}\) 归一化为 1。需要显式给出局域暗物质密度、银河系速度分布、逃逸速度、地球速度及其采用的时间平均/年度调制约定。原草稿尚未完整列出这些输入。

## 8. 规范理论完备性

如果 \(V_\mu\) 真正是自发破缺 \(U(1)_X\) 的规范玻色子，而不是一般 Proca 有效矢量场，那么非对角矢量流

\[
\bar\chi_2\gamma^\mu\chi_1
\]

在 \(m_{\chi_2}\ne m_{\chi_1}\) 时一般不守恒。需要说明暗部门质量矩阵、\(U(1)_X\) 破缺来源、Goldstone/暗 Higgs 的耦合，并检查纵向传播子及相关 Ward identity。若只采用 Proca EFT，也应明确其适用能标和纵向模式处理。

## 9. Loop-induced \(2\to2\) 散射

草稿 III.B 仅写出“2→2 from loop diagram”，尚无拓扑、振幅或结果。该过程可能产生普通弹性核反冲，尤其会影响 LZ 低能侧带。必须先明确允许的环图和 counterterms，再完成匹配、核响应及其与树级 \(2\to3\) 信号的联合事件率；不能把它留作一句占位文字。
