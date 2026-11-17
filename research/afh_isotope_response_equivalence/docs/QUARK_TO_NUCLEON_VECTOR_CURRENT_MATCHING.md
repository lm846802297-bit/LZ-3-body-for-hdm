# 三体 VV 核子流与 AFH 核响应——完整物理讨论记录

**研究对象：** \(\chi_1+A\to\chi_1+A+s\) 的 vector–vector（VV）基准模型  
**记录日期：** 2026-11-18  
**关联仓库：** `lm846802297-bit/LZ-3-body-for-hdm`  
**关联研究分支：** `research/afh-isotope-response-equivalence-20261118`  
**关联 PR：** #51（AFH 七同位素核响应等价性审计）  
**状态：** 理论讨论已系统整理；AFH 七同位素电荷（\(M\)）响应审计已归档；完整三体 VV 核子流与所有相关核响应的数值匹配尚未完成。

---

## 0. 先给出结论

本文要解决的不是“AFH 的六种核响应是否都要计算”，而是：**从当前 UV 矢量耦合出发，经过夸克—核子匹配和三体暗物质流收缩后，究竟会产生哪些核算符；这些核算符分别需要哪些 AFH 响应？**

当前可以确定的结论如下。

1. **AFH 的 \(W_M^{00}\) 是当前 VV 模型的领先阶核电荷响应，但不是完整矢量核流的同义词。** 它描述单体矢量电荷密度及其有限核尺寸、多极结构。只在核电荷分量主导、质子和中子耦合等标量、且单体流近似成立时，点状核振幅乘以归一化的 \(M\) 响应才等价于逐核子 NR 算符嵌入原子核的结果。
2. **三体末态标量 \(s\) 不会自动产生新的核子相互作用。** 当前模型中 \(s\) 从暗物质线上辐射，没有直接的 \(s\bar NN\) 顶点。因此，三体结构主要进入暗物质侧的 \(\mathcal T_3^\mu\) 和三体相空间；核侧仍由媒介子所耦合的矢量流决定。
3. **不能把标准弹性 AFH 的完整 \(2\to2\) 截面公式直接套到三体过程。** 标准 \(\mathbf v^\perp\) 的正交关系来自弹性二体能量守恒；三体过程中还存在 \(k_s\)，必须从完整 \(\mathcal T_3^\mu\) 出发匹配。
4. **不能任意添加轴矢量、赝标量、张量等 Wilson 系数；但必须保留 UV 矢量流实际诱导的次领先项。** 对当前 VV 模型，除 \(M\) 外，优先审计的是可能的自旋—轨道 \(\Phi''\) 及其与 \(M\) 的干涉，以及暗物质空间流与核子空间流收缩后可能出现的 \(\Delta\)、\(\Sigma'\) 等响应。
5. **此前“\(F_2^V\) 一定非零且约为 \(0.1F_1^V\)”的说法不能作为当前模型的输入。** 对 flavor-universal 的 \(u,d,s\) 矢量流，Hoferichter–Klos–Schwenk 的三味分解给出 \(F_2^{u,N}(0)+F_2^{d,N}(0)+F_2^{s,N}(0)=0\)。有限 \(t\) 的斜率和更高阶项仍需匹配，但不能未经证明就采用一个常数比例。
6. **AFH v6.0 的因子 4 必须且只能计入一次。** 原始 package 的等标量量 \(4\pi W_M^{00}/(2J_A+1)\) 在零动量转移趋近 \(A^2/4\)；物理等质子、等中子耦合响应趋近 \(A^2\)。
7. **Xe-131 的 \(M\) 响应深极小值使次领先响应值得检查，但不能据此断言其一定填平谱谷。** 需要实际计算 \(W_{\Phi''}\)、\(W_{M\Phi''}\) 及相关完整张量收缩。

本文将“已完成的数值结果”“已有文献给出的解析结构”“尚待本模型计算的量”分开标注，避免把估算写成验证结论。

## 1. 变量、动量约定与三体运动学

采用度规 \((+,-,-,-)\)。定义：

- \(P_A^\mu\)、\(P_A'^\mu\)：初末态原子核四动量；
- \(p_\chi^\mu\)、\(p_\chi'^\mu\)：初末态 \(\chi_1\) 四动量；
- \(k_s^\mu\)：末态标量四动量；
- \(q_A^\mu\equiv P_A'^\mu-P_A^\mu\)：媒介子传递给原子核的四动量；
- \(q_\chi^\mu\equiv p_\chi'^\mu-p_\chi^\mu\)：暗物质外线初末态动量差；
- \(E_R\)：靶核反冲能量。

由四动量守恒

\[
p_\chi+P_A=p_\chi'+P_A'+k_s
\]

得到

\[
\boxed{q_A^\mu=-q_\chi^\mu-k_s^\mu.}
\]

因此三体过程中一般有 \(q_A\ne -q_\chi\)。AFH 核响应的自变量必须是原子核实际获得的空间动量

\[
\boxed{\mathbf q_A=\mathbf P_A'-\mathbf P_A
=\mathbf p_\chi-\mathbf p_\chi'-\mathbf k_s.}
\]

若初始原子核静止，则

\[
q_A^0=E_R,\qquad
|\mathbf q_A|^2=E_R(E_R+2m_A),
\]

故

\[
|\mathbf q_A|\simeq\sqrt{2m_AE_R}
\]

是核反冲区间内极精确的非相对论近似。这里的 \(|\mathbf q_A|^2\) 是正的三维动量平方；四动量不变量则为

\[
t_A=q_A^2=(q_A^0)^2-|\mathbf q_A|^2=-2m_AE_R.
\]

建议代码和文档始终区分 `qA_vec2`、`tA` 或 `Q2=-tA`，不要让同一个 `q2` 同时表示三维正值和 Minkowski 不变量。

| 变量 | 物理意义 | 用途 |
|---|---|---|
| \(\mathbf q_A\) | 原子核实际动量转移 | AFH 核响应、多极展开、核子流匹配 |
| \(\mathbf q_\chi\) | 暗物质外线动量差 | 暗物质运动学、外线自旋量 |
| \(\mathbf k_s\) | 末态标量动量 | 三体相空间、\(\chi_2\) 传播子 |
| \(E_R\) | 核反冲能量 | 实验可观测量及微分谱 |

## 2. 当前 UV 模型与振幅因子化

当前研究的 VV benchmark 可概括为

\[
\begin{aligned}
\mathcal L_{\rm int}={}&
 g_1 V_\mu\bar\chi_2\gamma^\mu\chi_1
 +g_2s\bar\chi_2\chi_1+\mathrm{h.c.}\\
&+g_{Vq}V_\mu\sum_q\bar q\gamma^\mu q.
\end{aligned}
\]

其物理结构是：

- \(V\) 通过矢量流与夸克、进而与核子耦合；
- \(s\) 通过 \(\chi_2\to\chi_1+s\) 在暗物质线上辐射；
- 当前 benchmark 没有直接的 \(s\bar NN\) 或 \(s\)–核子标量密度耦合；
- \(\chi_2\) 的两个内部传播子及其干涉必须保留，尤其在接近 pole 时不能先做局域常数近似。

把暗物质侧的完整三体流写成

\[
\mathcal T_3^\mu
=\bar u_{\chi_1}(p_\chi')\Gamma_3^\mu
 u_{\chi_1}(p_\chi),
\]

其中 \(\Gamma_3^\mu\) 由两张标量辐射图组成。按当前模型的动量流向，其结构可写为

\[
\Gamma_3^\mu\sim
\gamma^\mu\frac{\slashed p_\chi-\slashed k_s+m_2}
{(p_\chi-k_s)^2-m_2^2}
+
\frac{\slashed p_\chi'+\slashed k_s+m_2}
{(p_\chi'+k_s)^2-m_2^2+i m_2\Gamma_2}
\gamma^\mu,
\]

整体耦合、传播子符号和宽度方案以仓库的振幅定义为准。完整振幅为

\[
\boxed{
\mathcal M_3=\mathcal T_3^\mu D_{\mu\nu}(q_A)J_A^\nu(q_A),
}
\]

其中

\[
J_A^\nu(q_A)=\langle A'|J_V^\nu(q_A)|A\rangle
\]

是原子核的矢量流矩阵元。

**因子化的准确含义：** 在单次媒介子交换、核流线性耦合和单体流近似下，暗物质三体张量与核流矩阵元可以分开计算。但一般平方振幅是

\[
\overline{|\mathcal M_3|^2}
\propto
\overline{\mathcal T_3^\mu\mathcal T_3^{\nu *}}
D_{\mu\alpha}D^*_{\nu\beta}
W_A^{\alpha\beta},
\]

而不是无条件地等于一个标量 \(|\mathcal K_3|^2\) 乘 \(W_M\)。只有在核电荷分量主导、其余核流项可忽略时，才可简化为

\[
\overline{|\mathcal M_3|^2}
\simeq |\mathcal K_3|^2 R_M^{\rm phys}(q_A).
\]

标量发射改变 \(\mathcal T_3^\mu\) 和相空间，并不自动把核子矢量流变成标量流或轴矢量流。

## 3. 点状原子核振幅与 AFH \(M\) 响应为什么等价

先只保留核子矢量电荷的领先阶。单体流近似下，核电荷算符为

\[
\rho_A(\mathbf q_A)
=\sum_{i=1}^{A}g_{N_i}
 e^{i\mathbf q_A\cdot\mathbf r_i},
\]

其中 \(\mathbf r_i\) 是第 \(i\) 个核子相对核质心的坐标。

如果 \(g_p=g_n=g_N\)，则

\[
\rho_A(\mathbf q_A)
=g_N\sum_{i=1}^{A}e^{i\mathbf q_A\cdot\mathbf r_i}.
\]

原子核矩阵元是

\[
\mathcal A_M(q_A)=
\left\langle A'\left|
\sum_{i=1}^{A}e^{i\mathbf q_A\cdot\mathbf r_i}
\right|A\right\rangle.
\]

在 \(q_A\to0\) 时，指数趋于 1，振幅为 \(A\)，平方为 \(A^2\)。这就是等质子、等中子耦合下的相干增强。

有限 \(q_A\) 时，各核子位置带来不同相位；AFH 将指数算符作球谐函数—球贝塞尔函数多极展开，并用核波函数计算各多极的约化矩阵元。对弹性质量（vector-charge）响应，AFH 的 \(M\) 多极给出

\[
W_M^{\tau\tau'}(y_A)
=\sum_{J=0,2,\ldots}
\langle J_A\|M_{J;\tau}(q_A)\|J_A\rangle
\langle J_A\|M_{J;\tau'}(q_A)\|J_A\rangle^*,
\]

其中

\[
y_A=\left(\frac{q_Ab_A}{2}\right)^2
=\frac{b_A^2m_AE_R}{2}
\]

使用反冲近似时成立。这里的 \(W_M\) 不是额外相互作用，而是同一个单体核子密度算符在复合核态上的矩阵元平方、自旋平均及多极组织。

因此，在纯 \(M\) 响应近似下，以下两条路线计算的是同一个矩阵元：

**路线 A：点状核振幅乘有限核尺寸响应**

\[
\mathcal M_{3,\rm pt}\propto A g_N\mathcal K_3,
\qquad
\overline{|\mathcal M_3(q_A)|^2}
=\overline{|\mathcal M_{3,\rm pt}|^2}
\frac{R_M^{\rm phys}(q_A)}{R_M^{\rm phys}(0)}.
\]

**路线 B：先构造单核子算符，再嵌入原子核**

\[
1_\chi1_N\longrightarrow
\sum_{i=1}^{A}e^{i\mathbf q_A\cdot\mathbf r_i},
\qquad
\overline{|\mathcal M_A|^2}
\propto R_M^{\rm phys}(q_A).
\]

两者等价的条件是：相同的单核子耦合、相同的 \(q_A\)、相同的核态和单体流近似、相同的同位旋约定、相同的归一化，并且实际振幅只选取同一个核电荷算符。

**重要区别：** 如果点状核振幅只把核子耦合替换成 \(Ag_N\)，却没有乘有限核尺寸因子，它只在 \(q_A\to0\) 的长波极限成立。有限动量下必须恢复 AFH 核结构；不能把 \(F_A(q)=1\) 当成真实氙核的响应。

## 4. AFH v6.0 的因子 4 与响应归一化

本仓库当前 AFH v6.0 package 的等标量归一化约定为

\[
R_{M,\rm raw}(q_A)
=\frac{4\pi}{2J_A+1}W_{M,\rm AFH}^{00}(y_A),
\]

其零动量极限为

\[
R_{M,\rm raw}(0)\simeq\frac{A^2}{4}.
\]

物理上每个质子和中子都具有相同核子耦合 \(g_N\) 时，乘在 \(g_N^2\) 前面的物理响应必须满足

\[
\boxed{R_M^{\rm phys}(0)=A^2.}
\]

所以在该 package 约定下

\[
\boxed{R_M^{\rm phys}(q_A)=4R_{M,\rm raw}(q_A)}
\]

或等价地用归一化形状

\[
R_M^{\rm phys}(q_A)
=A^2\frac{R_{M,\rm raw}(q_A)}{R_{M,\rm raw}(0)}.
\]

这两种写法只能选一种实现；**因子 4 不能在振幅、响应和耦合定义中重复乘入。** 如果点状核振幅已经含有 \(Ag_N\)，只能再乘归一化形状 \(R_M(q_A)/R_M(0)\)，不能再乘完整的 \(A^2\) 响应。

当前 PR #51 的七同位素审计已经将这一约定明确写入计算和测试：原始响应零动量值与 \(A^2/4\) 对应，物理响应按一次 factor-four 映射后为 \(A^2\)。

## 5. \(W_M^{00}\) 究竟包含什么、不包含什么

| 内容 | \(W_M^{00}\) 是否包含 | 说明 |
|---|---|---|
| 核子相干求和 | 是 | 在长波极限产生 \(A^2\) |
| 有限核尺寸 | 是 | 核子坐标相位及径向密度分布 |
| 核多极结构 | 是 | 对弹性电荷响应求和 \(J=0,2,\ldots\) |
| 核波函数/单体密度矩阵 | 是 | 取决于采用的壳模型与 OBDMEs |
| 质子—中子耦合结构 | 通过 \(\tau,\tau'\) 响应矩阵处理 | 若非等标量，不能只取 00 |
| 核子有限尺寸形状因子 \(F_1^N(t)\) | 不自动包含 | 属于夸克—核子匹配，需要另行乘入或匹配 |
| 核子 Pauli 形状因子 \(F_2^N(t)\) | 不自动包含 | 可能生成自旋—轨道及磁化流项 |
| \(\chi_2\) Breit–Wigner 共振 | 否 | 属于暗物质粒子物理振幅 |
| 标量 \(s\) 的三体相空间 | 否 | 属于三体运动学积分 |
| 暗物质速度分布 | 否 | 属于 halo fold |
| 探测器效率与 LZ likelihood | 否 | 属于探测器和统计层 |
| 两核子交换流 | 不自动包含 | AFH 默认单体密度矩阵不是完整多体流计算 |

AFH 的有限核尺寸响应已经取代简单点核近似；因此若再对整个核响应额外乘一个 Helm 形状因子，会重复计入核尺寸效应。核子自身的有限尺寸 form factor 与核整体的 AFH 响应是不同层次，不能混为一谈。

## 6. 什么时候两种方法不再等价

“点状核振幅 × 一个 \(W_M^{00}\)”只在特定核算符下成立。以下情形会使这个简单等价关系失效或需要推广。

| 情形 | 失效原因 | 应采用的处理 |
|---|---|---|
| \(g_p\ne g_n\) | 核电荷不再是纯等标量密度 | 使用 \(W_M^{00},W_M^{01},W_M^{11}\) 的完整同位旋组合 |
| 核子自旋算符出现 | 探测自旋密度而非单纯核子数密度 | 匹配 \(\Sigma'\)、\(\Sigma''\) 等响应 |
| 核子内部轨道/自旋—轨道算符出现 | 点核只保留质心自由度，会丢失束缚核子结构 | 匹配 \(\Delta\)、\(\Phi''\)、\(\tilde\Phi'\) 等 |
| 暗物质空间流与核子空间流不可忽略 | 振幅是多个 Lorentz 分量的张量收缩 | 计算完整 \(\mathcal T_3^\mu J_{A\mu}\) 和干涉项 |
| 有限 \(Q^2\) 核子 form factor 不可忽略 | 核子不是点状 Dirac 粒子 | 使用正确 flavor 组合的 \(F_1^N(t),F_2^N(t)\) |
| 非弹性核跃迁 | 初末核态不同，弹性响应不足 | 使用相应跃迁密度矩阵与非弹性核响应 |
| 两核子交换流、多体流 | 相互作用不再只是 \(\sum_i J_i\) | 用手征 EFT/多体核流重新计算 |
| 多次媒介子交换或非线性核耦合 | 振幅不再线性因子化为单个核流 | 直接计算相应多体振幅 |
| \(q_A/m_N\) 不够小 | 低阶 NR 截断和 form factor 展开可能不可靠 | 保留完整 form factor，做相对论修正/截断误差审计 |
| 响应归一化不一致 | 因子 4 或 \(A^2\) 被漏乘/重复乘 | 用 \(q=0\) 归一化测试锁定约定 |

特别强调：**“原子核有非零自旋”本身并不意味着任何模型都必须有 SD 响应。** 是否需要 \(\Sigma'\)、\(\Sigma''\)，取决于 UV 相互作用经过匹配后是否真正产生核子自旋算符。

## 7. 从夸克矢量流到质子、中子：等耦合是否合理

### 7.1 一般夸克耦合

若低能矢量流只写出 \(u,d\) 两个轻味，

\[
J_q^\mu=g_u\bar u\gamma^\mu u+g_d\bar d\gamma^\mu d,
\]

则在零动量转移下，按净价夸克数

\[
g_{Vp}=2g_u+g_d,\qquad
g_{Vn}=g_u+2g_d.
\]

定义等标量、等矢量组合

\[
g_0=\frac{g_{Vp}+g_{Vn}}{2},\qquad
g_1=\frac{g_{Vp}-g_{Vn}}{2},
\]

则

\[
g_0=\frac32(g_u+g_d),\qquad
g_1=\frac12(g_u-g_d).
\]

### 7.2 flavor-universal benchmark

若所有相关轻夸克具有相同矢量耦合

\[
g_u=g_d=g_s=\cdots=g_{Vq},
\]

则零动量矢量电荷给出

\[
\boxed{g_{Vp}=g_{Vn}=3g_{Vq}.}
\]

这对应重子数型（整体归一化可吸收到耦合常数中）的等标量矢量流。因此，当前模型采用 \(g_{Vp}=g_{Vn}\) 并非毫无物理依据的任意拟合：它是 flavor-universal quark-vector benchmark 的自然低能电荷匹配。

但这不是所有 \(U(1)'\) 的普遍结论。不同 UV 电荷赋值会产生不同 \(g_u,g_d\)，例如电磁型暗光子耦合并不等于当前重子数型 benchmark，不能把两个模型混用。

### 7.3 有限动量转移时不能把 \(3g_{Vq}\) 当作完整核子流

一般核子矢量矩阵元应写成

\[
\langle N(p_N')|J_V^\mu|N(p_N)\rangle
=\bar u_N(p_N')\left[
F_1^{V,N}(t)\gamma^\mu
-\frac{iF_2^{V,N}(t)}{2m_N}
\sigma^{\mu\nu}q_{N\nu}
\right]u_N(p_N),
\]

这里的 Pauli 项符号对应 \(q_N=p_N-p_N'\) 的约定；若改用 \(q_N=p_N'-p_N\)，Pauli 项符号随之改变。\(t=q_N^2\le0\)，并定义 \(Q^2=-t\ge0\)。

对 flavor-universal 的三味 \(u,d,s\) 矢量流，在零动量转移下

\[
F_1^{u,N}(0)+F_1^{d,N}(0)+F_1^{s,N}(0)=3.
\]

在 Hoferichter–Klos–Schwenk 的三味分解中，Pauli 常数项满足

\[
F_2^{u,N}(0)=\kappa_N,\qquad
F_2^{d,N}(0)=-\kappa_N-\kappa_N^s,\qquad
F_2^{s,N}(0)=\kappa_N^s,
\]

从而

\[
\boxed{F_2^{u,N}(0)+F_2^{d,N}(0)+F_2^{s,N}(0)=0.}
\]

因此，对当前 flavor-universal 三味 benchmark，**不能笼统宣称 \(F_2^V(0)\ne0\)**。有限 \(t\) 的 form-factor 斜率、更高阶项、实际求和的 active flavors 和 UV 权重仍需明确；若模型的 \(\sum_q\) 包含不同阈值下的重味，必须先完成相应低能匹配。也不能把电磁 Pauli form factor 直接当成重子数型流的 \(F_2^V\)。

在精确同位旋对称极限下，纯等标量矢量流的质子和中子 form factors 相同；实际计算仍应记录所用的 isospin-breaking、strangeness 和重味近似。

## 8. VV 相互作用的 NR 匹配：已知的二体基准与三体限制

Hoferichter–Klos–Schwenk 对弹性 \(\chi N\to\chi N\) 的 VV 单体流给出完整的非相对论约化。按其自旋量归一化和动量约定，结构为

\[
\begin{aligned}
\mathcal M_{1,\mathrm{NR}}^{VV}={}&
\chi_{r'}^\dagger\chi_r\,
\chi_{s'}^\dagger\left[
 f_1^{V,N}(t)
 -\frac{\mathbf q}{4m_N^2}\cdot
 (\mathbf q-i\boldsymbol\sigma_N\times\mathbf P)
 f_2^{V,N}(t)
\right]\chi_s\\
&+\frac{1}{2m_\chi}
\chi_{r'}^\dagger[\mathbf K+i\boldsymbol\sigma_\chi\times\mathbf q]\chi_r
\cdot\frac{1}{2m_N}
\chi_{s'}^\dagger i\boldsymbol\sigma_N\times\mathbf q
 f_2^{V,N}(t)\chi_s.
\end{aligned}
\]

其中该文定义 \(\mathbf q=\mathbf k_\chi'-\mathbf k_\chi
=\mathbf p_N-\mathbf p_N'\)、\(\mathbf P=\mathbf p_N+\mathbf p_N'\)、\(\mathbf K=\mathbf k_\chi+\mathbf k_\chi'\)，且

\[
f_i^{V,N}(t)=\frac{1}{\Lambda^2}
\sum_{q=u,d,s}c_q^{VV}F_i^{q,N}(t).
\]

这个公式表明：

- \(f_1^{V,N}\) 给出领先的核子密度耦合，对应 \(M\) 响应；
- \(f_2^{V,N}\) 进入含核子动量 \(\mathbf P\) 的自旋—动量项，其 NR 结构与 \(\mathcal O_3\) 相关；
- \(f_2^{V,N}\) 还进入磁化流项；其中显式的暗物质空间流部分带有 \(1/m_\chi\) 抑制；
- 这些项在完整振幅中可能与领先电荷项发生干涉，不能只比较某一个单独的平方项。

AFH 的标准弹性算符

\[
\mathcal O_3=i\mathbf S_N\cdot
\left(\frac{\mathbf q}{m_N}\times\mathbf v^\perp\right)
\]

在核结构层面主要关联 \(\Phi''\) 及其与 \(M\) 的干涉，而不应简单地当作普通 SD 自旋响应。AFH 明确指出，\(\mathcal O_3\) 可通过 \(\Phi''_0\propto\sum_i\boldsymbol\sigma_i\cdot\mathbf l_i\) 产生标量、准相干的核响应。

**但是上面的 \(\mathcal M_{1,\mathrm{NR}}^{VV}\) 是弹性二体公式，不是本项目三体振幅的结果。** 本项目有额外的 \(k_s\)，暗物质侧是 \(\mathcal T_3^\mu\) 而不是简单的 \(\bar u_\chi'\gamma^\mu u_\chi\)。标准 \(\mathbf v^\perp\cdot\mathbf q=0\) 依赖弹性二体能量守恒，不能不加推导地用于三体过程。

正确做法是先使用完整核子矢量流顶点，再与 \(\mathcal T_3^\mu\) 收缩；完成这一步之后，才能确定三体过程中 \(\Phi''\)、\(\Delta\)、\(\Sigma'\) 等响应的实际系数。

## 9. AFH 六种主要核响应及其在本模型中的候选角色

AFH 的六种主要核多极响应为

\[
\boxed{M,\quad \Sigma',\quad\Sigma'',\quad\Delta,
\quad\Phi'',\quad\widetilde\Phi'.}
\]

这里必须纠正一个常见记号错误：标准 AFH 响应是 \(\widetilde\Phi'\)（tilde-Phi-prime），不是 \(\widetilde\Phi''\)。另外，AFH 的平方振幅还包含允许的干涉响应，例如 \(W_{M\Phi''}\) 和 \(W_{\Delta\Sigma'}\)。

| 响应 | AFH 核算符性质 | 对当前 VV 模型的地位 |
|---|---|---|
| \(M\) | 矢量电荷/核子密度 | **领先阶，必须保留** |
| \(\Phi''\) | 矢量纵向、自旋—轨道结构 | **优先审计**；若完整匹配产生 O3-like 核算符，则需计算 |
| \(W_{M\Phi''}\) | \(M\) 与 \(\Phi''\) 干涉 | 与 \(\Phi''\) 同步计算，不能只算对角项 |
| \(\Delta\) | 与轨道角动量相关的矢量横向磁响应 | 暗物质空间流与核对流电流收缩后可能出现 |
| \(\Sigma'\) | 横向自旋响应 | 磁化流与暗物质空间流收缩后可能出现 |
| \(\Sigma''\) | 纵向自旋响应 | 需由完整纵向投影判断，不应仅因核自旋非零而加入 |
| \(\widetilde\Phi'\) | 矢量横向电、自旋—速度张量响应 | 当前不是领先候选；只有匹配产生相应结构才计算 |

注意，\(\Phi''\) 不是传统意义上只测量未成对核子总自旋的 SD 响应。它含有 \(\boldsymbol\sigma\cdot\mathbf l\) 型核子自旋—轨道结构，可具有准相干增强；因此不能因为 VV 模型没有轴矢量顶点，就先验排除 \(\Phi''\)。

同时，Xe-131 的 AFH \(M\) 响应中出现的 rank-2（\(J=2\)）多极仍属于**矢量电荷 \(M\) 响应**，不是 \(\Sigma'\)、\(\Delta\) 或 \(\Phi''\)。这两个“高阶结构”必须分开命名。

## 10. 为什么当前首先要审计 \(\Phi''\)，但不能预先断言它重要

现有 Xe-131 \(M\) 响应记录的若干深极小值为：

| \(q_A\) (MeV) | \(E_R\) (keV) | \(q_A/m_N\) | \(\sqrt{R_M/A^2}\) |
|---:|---:|---:|---:|
| 157.94 | 102.21 | 0.168 | \(3.52\times10^{-3}\) |
| 256.27 | 269.10 | 0.273 | \(2.52\times10^{-4}\) |
| 365.07 | 546.09 | 0.389 | \(3.95\times10^{-4}\) |
| 499.37 | 1021.80 | 0.532 | \(1.29\times10^{-4}\) |

这里 \(R_M/A^2\) 是归一化的核响应强度；表中的平方根是相对振幅尺度。它们显示在这些位置，单独的 \(M\) 核矩阵元受到很强的抵消。

因此，即使某个次领先核响应在一般动量处较小，也不能仅靠其单核子幂次估计就排除它在 \(M\) 极小值附近改变相对谱形的可能性。但必须区分：

- **相对修正可能变大**，因为领先项接近零；
- **绝对事件率不一定变大**，因为相空间、三体阈值、halo fold 和其他同位素都仍然起作用；
- 天然氙是逐同位素求和，单个 Xe-131 的 \(M\) 极小值不等于天然氙总谱必然出现同样深的谷。

此前对话中曾使用 \(|F_2/F_1|\sim0.1\) 和核子内部速度 \(0.1\)–\(0.3\) 做过 O3-like 项的百分比估算。**该百分比不是已验证的 Xe-131 响应结果，不应进入论文或数值结论。** 原因包括：当前 flavor-universal 流的 \(F_2(0)\) 常数项可能抵消；有限 \(t\) 的 flavor form factors 尚未匹配；核响应矩阵元和干涉尚未计算；三体暗物质张量也不能用弹性 \(\mathbf v^\perp\) 替代。

## 11. 暗物质空间流小，不等于 \(\Phi''\) 小

之前的三体 Dirac 张量诊断给出一个代表性 benchmark 的估计：

\[
\frac{\sum_i L^{ii}}{L^{00}}\sim(6.1\text{--}6.9)\times10^{-6},
\qquad
\frac{\sqrt{\sum_iL^{ii}}}{\sqrt{L^{00}}}
\sim(2.5\text{--}2.6)\times10^{-3}.
\]

该数值只能说明所检查参数点的暗物质空间流相对暗物质时间流较小；它不是完整氙核截面修正，也不能单独排除 \(\Phi''\)。

原因是：若核子矢量流的次领先自旋—轨道结构出现在 \(J_A^0\) 中，它仍然与领先的 \(\mathcal T_3^0\) 收缩，而不需要暗物质空间分量 \(\mathcal T_3^i\)。因此

\[
\mathcal T_3^0 J_A^0
=\mathcal T_3^0(J_{A,M}^0+J_{A,\Phi''}^0+\cdots)
\]

可能包含 \(M\)–\(\Phi''\) 干涉，即使 \(\mathcal T_3^i\) 很小也一样。

此前的点状无自旋核质心电流检查只测试了整体质心对流项，不能代表核子在核内的内部轨道运动或磁化流。反过来，核子内部速度较大也不自动意味着其贡献大；最终仍要计算完整张量收缩及核矩阵元。

对守恒矢量流，连续性方程会约束纵向电流，但不能据此消去所有横向电流。因此仅由 \(q_{A\mu}J_A^\mu=0\) 不能推出 \(\Delta\) 或 \(\Sigma'\) 为零。

## 12. 质子—中子耦合不等时如何使用 AFH

在物理等标量/等矢量约定下，若

\[
g_0=\frac{g_p+g_n}{2},\qquad
g_1=\frac{g_p-g_n}{2},
\]

则纯密度响应的组合具有结构

\[
R_M^{\rm phys}
=g_0^2W_M^{00}
+2g_0g_1W_M^{01}
+g_1^2W_M^{11},
\]

具体数值因子必须与 AFH package 的 \(t^\tau\)、coupling setter 和 factor-four 约定统一。

- 当前 flavor-universal benchmark：\(g_p=g_n\)，故 \(g_1=0\)，领先阶只需等标量电荷通道。
- 一般 \(U(1)'\)：必须由 UV 电荷赋值计算 \(g_u,g_d,g_s,\ldots\)，再匹配 \(g_p,g_n\)，不能任意调 \(g_p/g_n\)。
- 若 \(g_p\ne g_n\)，即使仍然只有 \(\mathcal O_1\) 型密度算符，也不能只用 \(W_M^{00}\)；必须保留 isoscalar–isovector 干涉。

AFH 七同位素响应必须按同位素分别使用。不同同位素可以都使用同一类 \(W_M\) 响应定义，但不能共用一条数值响应曲线；核自旋、壳结构、质量和 \(q_A(E_R)\) 都不同。当前官方 AFH default-density 档案覆盖 Xe-128、129、130、131、132、134、136；Xe-124 和 Xe-126 没有本档案所用的官方 default density matrix，不能把它们伪装成已计算的 AFH 响应。

## 13. 两核子流：不是当前第一优先级，但也不能宣称永远为零

Hoferichter、Klos、Schwenk 的手征 EFT 计数对矢量/轴矢量 WIMP—核子流作了系统分类。其 Table 1 中，VV 通道的一体矢量电荷是最低阶；VV 两体矢量流在该计数下进入更高阶（时间分量 \(\mathcal O(p^4)\)，空间分量表中记作 \(\mathcal O(p^2+2)\)，其中额外的 2 来自 WIMP 非相对论自旋量抑制）。该文只计算到 \(\mathcal O(p^3)\)，因此没有把这些 VV 两体项作为其该阶结果的一部分。

这支持如下执行顺序：

1. 先完成一体流 \(F_1/F_2\) 匹配和 \(M,\Phi'',\Delta,\Sigma'\) 的相关投影；
2. 量化一体流完整结果相对 \(L_{00}W_M\) 的变化；
3. 再按相同 chiral EFT 约定评估 VV 两体流的高阶误差。

但不能把“形式上是 \(p^4\)”直接等同于“在本项目所有动量点数值上必然可忽略”。本项目关注的 \(q_A\) 可达到约 0.36–0.50 GeV，已高于 \(m_\pi\) 的典型尺度；手征展开的收敛性和 form-factor 形状必须单独评估。两体流不是 P0，但应作为更高精度核结构误差项保留在研究路线中。

## 14. 对当前代码与 AFH v6.0 的使用边界

仓库 `v6/dmformfactor-V6.m` 定义的相对论算符中：

- `OpRel[5]` 是 \((\bar\chi\gamma^\mu\chi)(\bar N\gamma_\mu N)\)；
- `OpRel[6]` 是暗物质矢量流与核子张量/Pauli 型 \(i\sigma_{\mu\alpha}q^\alpha\) 结构的组合。

这有助于组织普通弹性 VV 的核子流匹配，但**不能据此直接宣称标准 AFH v6.0 的二体散射入口已经实现了本项目三体流**。本项目的暗物质侧是 \(\mathcal T_3^\mu(p,p',k_s)\)，需要把它与核子流的各个 Lorentz 分量重新收缩；标准 AFH \(2\to2\) 的 \(\mathbf v^\perp\) 和截面前因子不能直接复用。

建议保持模块边界：

1. 粒子物理模块：精确计算 \(\Gamma_3^\mu\)、\(\chi_2\) propagator、宽度和完整三体相空间；
2. 核子匹配模块：输入明确的 flavor coefficients、\(F_1^{q,N}(t)\)、\(F_2^{q,N}(t)\)，输出核子流分量/NR 算符系数；
3. 核结构模块：用 AFH 密度矩阵计算相应 \(M,\Phi'',\Delta,\Sigma'\) 等响应及干涉；
4. 总振幅模块：逐相空间点完成 \(\mathcal T_3^\mu D_{\mu\nu}J_A^\nu\) 的自旋求和；
5. 率模块：再做三体相空间、halo、同位素丰度及探测器折叠。

## 15. 建议的数值审计顺序与验收条件

### P0：锁定 UV 流与归一化

- 明确 \(\sum_q\) 的 active flavors、每个 flavor 的 \(g_q\)、阈值匹配和重味处理；
- 验证 \(g_p=g_n=3g_{Vq}\) 是所选 benchmark 的零动量电荷，而非有限 \(t\) 完整 form factor；
- 记录 \(F_1^{V,N}(t),F_2^{V,N}(t)\) 的来源、参数化、误差和符号约定；
- 锁定 \(q_A\)、\(q_\chi\)、\(k_s\)、\(t_A\) 定义；
- 锁定 AFH v6.0 factor-four 映射，验证每个同位素 \(R_M^{\rm phys}(0)=A^2\)。

### P1：完整一体 VV 流匹配

- 从完整 \(\mathcal T_3^\mu\) 开始，而不是把 \(\mathcal T_3^\mu\) 替换成普通弹性 \(\bar u'\gamma^\mu u\)；
- 保留两个 \(\chi_2\) 辐射图、干涉、有限宽度及其对不同分量的影响；
- 将核子 Dirac/Pauli form factors 与暗物质流完整收缩，推导三体版的核子算符；
- 优先计算 \(\Phi''\) 与 \(M\Phi''\)，同时检查空间核流可能引入的 \(\Delta\)、\(\Sigma'\) 及允许的干涉；
- 对守恒矢量流检查核侧 Ward identity，并区分纵向与横向投影。

### P2：完整三体截面对照

逐点比较

\[
\frac{d\sigma_3}{dE_R}\bigg|_{M\text{-only}}
\quad\text{与}\quad
\frac{d\sigma_3}{dE_R}\bigg|_{\rm full\ one\mbox{-}body\ current}.
\]

同时输出：各响应对角项、干涉项、总响应、相对修正和绝对截面。不能只在 \(M\) 极小值处报告巨大相对比值而不报告绝对率。

### P3：高阶核结构

在一体流结果稳定后，再估算 VV 两体流、核子 form-factor 高阶项、核结构模型差异。若要进入论文定量结论，需要给出手征阶数、适用动量区间、误差估计和独立核结构输入。

### 最低验收条件

1. \(q_A\to0\) 时恢复等标量电荷归一化 \(A^2\)，factor 4 只出现一次；
2. flavor-universal 三味流在 \(t=0\) 恢复 \(F_1^V(0)=3\)，并正确处理 \(F_2^V(0)\) 的 flavor cancellation；
3. 完整振幅满足与模型相应的 Ward identity；
4. 两张三体辐射图及其干涉均保留；
5. 三体能量守恒与 \(q_A=-q_\chi-k_s\) 在数值点逐点满足；
6. \(M\)、\(\Phi''\)、\(\Delta\)、\(\Sigma'\) 的多极选择定则与核自旋/宇称一致；
7. 响应插值、动量网格、相空间积分分别做收敛检查；
8. 物理截面、天然氙速率和探测器结果作为不同层级报告。

## 16. 当前研究状态表

| 任务 | 状态 | 可作出的结论 |
|---|---|---|
| 七同位素 AFH v6.0 \(M\) 响应网格 | 已归档 | 7 种同位素、每种 2401 点，共 16807 个响应节点 |
| AFH factor-four 与零动量归一化 | 已归档 | 物理等核子响应满足 \(R_M(0)=A^2\) |
| AFH 多极重构闭合 | 已归档 | 最大相对残差约 \(2.22\times10^{-16}\) |
| Xe-131 的 \(M\) rank-0/rank-2 结构 | 已归档 | rank-2 是电荷 \(M\) 响应的一部分，不是 SD 响应 |
| flavor-universal 零动量核子电荷 | 解析匹配 | \(g_p=g_n=3g_{Vq}\) |
| flavor-universal 有限 \(t\) 的 \(F_1,F_2\) | 未完成 | 需定义 active flavors 并提供 form-factor 输入 |
| 三体 VV 完整核子流张量收缩 | 未完成 | 尚不能宣称完整 VV 核流已验证 |
| Xe-129/Xe-131 的 \(\Phi''\)、\(M\Phi''\) | 未完成 | P1 优先项 |
| \(\Delta\)、\(\Sigma'\) 空间核流响应 | 未完成 | 取决于完整 \(\mathcal T_3^i\) 收缩 |
| VV 两核子流 | 未完成/高阶 | P2/P3，需手征计数与误差评估 |
| 完整天然氙 halo-folded rate | 未完成 | 需先完成完整一体流核响应 |

**当前允许的结论：** \(W_M^{00}\) 是当前 VV benchmark 的合理领先阶核响应，且七同位素 AFH 电荷响应已通过所归档的内部数值审计。  
**当前不允许的结论：** 不能宣称完整矢量核流已由 \(W_M^{00}\) 完全描述；不能宣称 \(\Phi''\)、\(\Delta\)、\(\Sigma'\) 已经数值证明可忽略；也不能把此前单核子量级估算写成 Xe-131 截面修正。

## 17. 相关文献与仓库材料

1. N. Anand, A. L. Fitzpatrick, W. C. Haxton, “Model-independent WIMP Scattering Responses and Event Rates: A Mathematica Package for Experimental Analysis,” *Phys. Rev. C* **89**, 065501 (2014), [arXiv:1308.6288](https://arxiv.org/abs/1308.6288)。AFH 六种核响应、multipole 展开、\(\Phi''\) 与 \(M\Phi''\) 干涉，以及点核近似的局限。
2. A. L. Fitzpatrick, W. Haxton, E. Katz, N. Lubbers, Y. Xu, “The Effective Field Theory of Dark Matter Direct Detection,” *JCAP* **02** (2013) 004, [arXiv:1203.3542](https://arxiv.org/abs/1203.3542)。标准弹性 NR 算符基底。
3. M. Hoferichter, P. Klos, A. Schwenk, “Chiral power counting of one- and two-body currents in direct detection of dark matter,” *Phys. Lett. B* **746** (2015) 410–416, [arXiv:1503.04811](https://arxiv.org/abs/1503.04811), [DOI:10.1016/j.physletb.2015.05.041](https://doi.org/10.1016/j.physletb.2015.05.041)。矢量流的 \(F_1/F_2\) flavor 分解、VV 弹性 NR 匹配和一体/两体流手征计数。
4. M. Hoferichter, P. Klos, J. Menéndez, A. Schwenk, “Analysis strategies for general spin-independent WIMP-nucleus scattering,” *Phys. Rev. D* **94**, 063505 (2016), [arXiv:1605.08043](https://arxiv.org/abs/1605.08043)。一般相干响应、同位旋修正和两体流。
5. M. Hoferichter, P. Klos, J. Menéndez, A. Schwenk, “Nuclear structure factors for general spin-independent WIMP-nucleus scattering,” *Phys. Rev. D* **99**, 055031 (2019), [arXiv:1812.05617](https://arxiv.org/abs/1812.05617)。一般 SI 核结构因子与两体流扩展。

**仓库内对应材料：**

- `research/afh_isotope_response_equivalence/README.md`
- `research/afh_isotope_response_equivalence/docs/AFH_ISOTOPE_RESPONSE_EQUIVALENCE.md`
- `research/afh_isotope_response_equivalence/results/`
- `research/afh_default_density_xe131/output/minima.csv`
- `research/docs/01_model_and_amplitude.md`
- `research/docs/appendices/09A_three_body_kinematics_amplitude.md`
- `v6/dmformfactor-V6.m`（特别是 `OpRel[5]` 与 `OpRel[6]` 的定义）

---

## 附：需要从原讨论中明确修正的四点

1. **不是所有有限核尺寸修正都能用一个普通球形形状因子代替。** 对纯 \(M\) 响应，AFH \(W_M\) 是系统核结构结果；对 \(\Phi''\)、\(\Delta\) 等复合核算符，必须计算各自的矩阵元。
2. **标准 AFH 的 \(\widetilde\Phi\) 记号是 \(\widetilde\Phi'\)。** 不应写成 \(\widetilde\Phi''\)。
3. **对 universal \(u,d,s\) 矢量流，不能把 \(F_2^V(0)\ne0\) 当作默认。** 该文的 flavor 分解显示零动量常数项相消；有限动量的剩余项需要实际输入。
4. **弹性 VV 公式中的 \(\mathcal O_3\) 匹配不能直接搬到三体过程。** 三体暗物质流含 \(k_s\)，其空间/时间分量比例和干涉必须从完整 \(\Gamma_3^\mu\) 重新计算。