# 三体 VV 核子流与 AFH 核响应——完整物理讨论记录

**研究对象：** \(\chi_1+A\to\chi_1+A+s\) 的 vector–vector（VV）基准模型  
**记录日期：** 2026-11-18  
**关联仓库：** `lm846802297-bit/LZ-3-body-for-hdm`  
**关联研究分支：** `research/afh-isotope-response-equivalence-20261118`  
**关联 PR：** #51（AFH 七同位素核响应等价性审计）  
**状态：** 理论讨论已系统整理；AFH 七同位素电荷（\(M\)）响应审计已归档；完整三体 VV 核子流与所有相关核响应的数值匹配尚未完成。

**2026-11-18 文档更新说明：** 在保留此前全部讨论正文的基础上，新增 AFH v6.0 作为唯一核结构输入的正式约定、核子 Dirac–Pauli form factor 与 AFH 核响应的层级区分、\(t_A\)/\(t_N\)/空间动量的记号审计、因子 4 记账规则，以及当前 PR #58 的证据边界。另修正原文中一处 Dirac–Pauli 顶点符号与动量转移方向不一致的问题，并撤回一处仍残留的“三味 \(F_2^V(0)\) 可能相消为零”的旧判断。除这两处物理校订外，原有讨论和历史数值均保留；没有把尚未完成的 AFH 多体投影写成已完成结果。

**2026-11-18 全响应数据库专题更新：** 新增第四部分 §§36–37，明确 AFH 核响应与单核子 (F_1,F_2) 的层级关系、(t_A/t_N) 的处方边界、八种 AFH 响应的独立数据库策略、禁止直接相加的原因、完整三体响应收缩、结果精度层级，以及数据库和收缩引擎的并行实施方案。该专题只更新理论组织和计算计划，不声称全响应数据库或新的核响应数值已经完成。

---

## 0. 先给出结论

本文区分两个彼此关联、但不能混为一谈的问题：第一，是否可以独立计算并保存 AFH v6.0 的全部标准核响应——可以，这构成可复用的核结构数据库；第二，哪些响应以及哪些干涉项真正进入当前三体 VV 截面——这必须由完整三体暗物质流和单核子 Dirac–Pauli 流匹配决定。**全响应数据库可以先于模型匹配建立，但不能把数据库中的全部响应直接相加作为物理截面。**

当前可以确定的结论如下。

1. **AFH 的 \(W_M^{00}\) 是当前 VV 模型的领先阶核电荷响应，但不是完整矢量核流的同义词。** 它描述单体矢量电荷密度及其有限核尺寸、多极结构。只在核电荷分量主导、质子和中子耦合等标量、且单体流近似成立时，点状核振幅乘以归一化的 \(M\) 响应才等价于逐核子 NR 算符嵌入原子核的结果。
2. **三体末态标量 \(s\) 不会自动产生新的核子相互作用。** 当前模型中 \(s\) 从暗物质线上辐射，没有直接的 \(s\bar NN\) 顶点。因此，三体结构主要进入暗物质侧的 \(\mathcal T_3^\mu\) 和三体相空间；核侧仍由媒介子所耦合的矢量流决定。
3. **不能把标准弹性 AFH 的完整 \(2\to2\) 截面公式直接套到三体过程。** 标准 \(\mathbf v^\perp\) 的正交关系来自弹性二体能量守恒；三体过程中还存在 \(k_s\)，必须从完整 \(\mathcal T_3^\mu\) 出发匹配。
4. **不能任意添加轴矢量、赝标量、张量等 Wilson 系数；但必须保留 UV 矢量流实际诱导的次领先项。** 对当前 VV 模型，除 \(M\) 外，优先审计的是可能的自旋—轨道 \(\Phi''\) 及其与 \(M\) 的干涉，以及暗物质空间流与核子空间流收缩后可能出现的 \(\Delta\)、\(\Sigma'\) 等响应。
5. **三味 Pauli form factor 的零动量基准存在一个必须公开记录的文献表示差异。** HKS 1503.04811 Eq. (23) 将低动量 flavor form factors 写为 \(F_2^{u,N}=\kappa_N+\mathcal O(t)\)、\(F_2^{d,N}=-\kappa_N-\kappa_N^s+\mathcal O(t)\)、\(F_2^{s,N}=\kappa_N^s+\mathcal O(t)\)；若按同一 \(\kappa_N\) 定义逐项相加，字面上得到零和。另一方面，HKS Eq. (21) 的显式 flavor 重构关系与物理质子/中子磁矩、strange Pauli 输入结合后，以及 Bishara et al. (2017) Appendix A.1 Eqs. (80)–(82)，给出
   \[
   F_2^{u/p}(0)=1.609,\quad F_2^{d/p}(0)=-2.097,\quad F_2^{s/p}(0)=-0.064,
   \]
   因而 \(F_2^{uds,p}(0)=F_2^{uds,n}(0)=-0.552\)（同位旋对称近似）。这两种写法在不进一步澄清 \(\kappa_N\) 的定义、近似和适用条件时不能同时按字面使用。本项目当前 benchmark 采用显式 flavor-separated 数值 \(-0.552\)，但将 HKS Eq. (23) 与 Eq. (21) 的表示差异保留为待进一步追溯的文献一致性问题，而不把零和式静默删除或当成已解决。有限 \(t\) 形状及误差协方差仍需进一步匹配。
6. **AFH v6.0 的因子 4 必须且只能计入一次。** 原始 package 的等标量量 \(4\pi W_M^{00}/(2J_A+1)\) 在零动量转移趋近 \(A^2/4\)；物理等质子、等中子耦合响应趋近 \(A^2\)。
7. **Xe-131 的 \(M\) 响应深极小值使次领先响应值得检查，但不能据此断言其一定填平谱谷。** 需要实际计算 \(W_{\Phi''}\)、\(W_{M\Phi''}\) 及相关完整张量收缩。

8. **完整 AFH 响应数据库与物理三体截面是两个不同的交付物。** 可以先独立计算 AFH v6.0 的全部八种标准响应；但只有完成 (F_1/F_2) 与 (mathcal T_3^mu) 的匹配、允许交叉项和完整相空间收缩后，才能确定哪些响应实际贡献于截面。

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
F_1^{V,N}(t_N)\gamma^\mu
+\frac{iF_2^{V,N}(t_N)}{2m_N}
\sigma^{\mu\nu}q_{N\nu}
\right]u_N(p_N),
\]

本文从这里开始统一采用 \(q_N=p_N'-p_N\)、\(\sigma^{\mu\nu}=\frac{i}{2}[\gamma^\mu,\gamma^\nu]\) 和度规 \((+,-,-,-)\)。若改用相反的动量转移 \(q_N=p_N-p_N'\)，Pauli 项前的显式符号必须同时反转；不能只改变 \(q_N\) 而保留同一个顶点符号。\(t_N=q_N^2\le0\)，并定义 \(Q_N^2=-t_N\ge0\)。

对 flavor-universal 的三味 \(u,d,s\) 矢量流，在零动量转移下

\[
F_1^{u,N}(0)+F_1^{d,N}(0)+F_1^{s,N}(0)=3.
\]

Bishara、Brod、Grinstein 和 Zupan，arXiv:1707.06998，Appendix A.1 给出的质子 flavor-separated 中心值为

\[
F_2^{u/p}(0)=1.609,\qquad
F_2^{d/p}(0)=-2.097,\qquad
F_2^{s/p}(0)=-0.064.
\]

这些输入由电磁质子/中子反常磁矩和 strange Pauli form factor 构造。写成

\[
\kappa_p=1.793,\qquad \kappa_n=-1.913,\qquad \kappa_s=-0.064,
\]

则显式 flavor 重构为

\[
F_2^{u/p}(0)=2\kappa_p+\kappa_n+\kappa_s=1.609,
\]
\[
F_2^{d/p}(0)=\kappa_p+2\kappa_n+\kappa_s=-2.097,
\qquad F_2^{s/p}(0)=\kappa_s=-0.064.
\]

因此，对当前 UV benchmark 的等权重三味流 \(J_{uds}^\mu=\bar u\gamma^\mu u+\bar d\gamma^\mu d+\bar s\gamma^\mu s\)，应当求和为

\[
\boxed{F_2^{uds/p}(0)=1.609-2.097-0.064=-0.552.}
\]

在同位旋对称近似下，\(u\leftrightarrow d\) 将质子与中子分量交换，而三味总和不变，因此

\[
\boxed{F_2^{uds/n}(0)\simeq F_2^{uds/p}(0)=-0.552.}
\]

与 \(F_1^{uds,p/n}(0)=3\) 比较，

\[
\frac{F_2^{uds}(0)}{F_1^{uds}(0)}=-0.184,
\qquad
F_1^{uds}+2F_2^{uds}=1.896,
\qquad
F_1^{uds}+F_2^{uds}=2.448.
\]

这里的 \(-0.552\) 是该 benchmark 的零动量中心值，不是有限 \(t\) 的常数近似。Bishara et al. 对三个 flavor 分量给出的误差有共同输入来源；在没有完整协方差矩阵时，不应把三个误差当作独立量简单平方相加，也不在此处虚构总和误差。

**关于 HKS 2015 的公式编号与文献一致性：** HKS 1503.04811 §4.2 的 Eq. (19) 定义夸克矢量流的 Dirac–Pauli 分解，Eq. (20) 给出同位旋关系，Eq. (21) 给出由电磁 form factors 和 strange form factor 重构 flavor 分量的关系，Eq. (22) 给出零动量矢量电荷。Eq. (23) 确实同时列出 \(F_2^{u,N}\)、\(F_2^{d,N}\)、\(F_2^{s,N}\) 的低动量表达；若逐字按同一 \(\kappa_N\) 记号求和，它给出零和。不能把 Eq. (23) 描述成“只给 strange Pauli form factor”，也不能声称它不包含零和结构。需要审计的是：Eq. (23) 的 \(\kappa_N\) 及其近似条件，是否能与 Eq. (21) 的显式 flavor 重构、Eq. (24) 的物理 Sachs 磁矩定义同时采用同一解释。按 Eq. (21) 并代入物理 \(\kappa_p,\kappa_n,\kappa_s\)，得到的显式 flavor 数值与 Eq. (23) 的字面零和形式不一致；目前没有在本文中擅自消除这一文献表示差异。当前数值 benchmark 仍直接采用 Bishara et al. 1707.06998 Appendix A.1 Eqs. (80)–(82)，而 HKS Eq. (23) 的零和形式保留为需要进一步追溯的交叉检查。

有限 \(t_N\) 时仍需使用 \(F_1^{uds,N}(t_N)\)、\(F_2^{uds,N}(t_N)\) 的实际形状、误差和协方差；不能把零动量中心值直接外推到整个 Xe 反冲区间。

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

此前对话中曾使用 \(|F_2/F_1|\sim0.1\) 和核子内部速度 \(0.1\)–\(0.3\) 做过 O3-like 项的百分比估算。**该百分比不是已验证的 Xe-131 响应结果，不应进入论文或数值结论。** 原因包括：早期曾根据 HKS 紧凑记号误判 flavor-universal 三味流的 \(F_2^V(0)\) 常数项可能相消；该判断已由本档案第 7.3 节所列 Bishara et al. 的显式 flavor-separated 输入撤回，当前零动量基准为 \(F_2^{uds}(0)=-0.552\)，不能再把“相消为零”作为模型结论。仍未完成的是有限 \(t_N\) 的 flavor form factors 及其协方差、AFH 核响应矩阵元和干涉；三体暗物质张量也不能用弹性 \(\mathbf v^\perp\) 替代。

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
2. flavor-universal 三味流在 \(t=0\) 恢复 \(F_1^V(0)=3\)，并恢复显式 flavor-separated 基准 \(F_2^V(0)=-0.552\)，不得假设三味常数项相消；
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
| 三体暗物质侧 \(\Gamma^\mu,L^{\mu\nu}\) 代表性诊断 | 有历史数值报告；原始脚本和完整收敛证据未找回 | 仅说明所报 benchmark 的空间流较小，不构成全参数或核响应验收 |\n| 三体 VV 完整核子流张量收缩 | 未完成 | 尚不能宣称完整 VV 核流已验证 |
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
3. **对 universal \(u,d,s\) 矢量流，当前零动量 Pauli 基准为 \(F_2^V(0)=-0.552\)，不是零。** 早期由 HKS 紧凑记号直接推出三味相消的判断已撤回；应采用 Bishara et al. (2017) Appendix A.1 的显式 flavor-separated 输入，并将有限 \(t\) 形状留作待匹配项。
4. **弹性 VV 公式中的 \(\mathcal O_3\) 匹配不能直接搬到三体过程。** 三体暗物质流含 \(k_s\)，其空间/时间分量比例和干涉必须从完整 \(\Gamma_3^\mu\) 重新计算。


---

# 补充专题：三体流数值诊断、点核极限与 AFH 自旋–轨道响应

> 本补充把此前关于完整三体流、点状核流、Xe-131 质量响应深极小值及核子自旋–轨道结构的讨论并入主记录。数值按证据等级区分：AFH 电荷响应网格和归一化审计属于已有归档结果；三体空间流比值、点核 ppm 修正及深极小值附近的单核子估算属于此前报告的代表性结果或启发式估算，尚未在本次文档更新中重新运行原始程序。不能将后者表述为已经独立复现的最终物理结论。

## 18. 为什么必须把三个物理问题分开

当前基准仍然是质量（电荷）响应
\[
R_M(q_A)\propto W_M^{00}(y_A),
\]
但“\(W_M^{00}\) 是领先阶”不等于“所有非 \(M\) 响应都已被证明可以忽略”。需要分别判断三个问题：

1. **核自旋 / 磁化结构：** 核子 Dirac–Pauli 流中的磁化项是否产生 \(\Sigma'\)、\(\Sigma''\) 或自旋–轨道响应？这里尤其要区分普通总核自旋响应与 \(\Phi''\) 自旋–轨道响应。
2. **核内轨道运动：** 核子对流电流和内部动量是否产生 \(\Delta\) 等响应？核子内部速度 \(v_N^{\rm int}\sim0.1\text{--}0.3\) 大于暗物质晕速度 \(v_\chi\sim10^{-3}\)，本身既不能证明轨道响应大，也不能证明其小；必须计算实际流收缩、Wilson 系数和核矩阵元。
3. **三体共振 / 传播子效应：** 两张标量辐射图中的虚 \(\chi_2\) 传播子及其宽度，是否改变 \(\mathcal T_3^0\) 与 \(\mathcal T_3^i\) 的相对大小？这一点必须在本项目的三体运动学中直接计算，不能套用普通弹性散射的速度阶数。

这三个问题相关但不等价。特别是，暗物质侧空间流很小，只约束 \(\mathcal T_3^i\) 的一部分；它不能排除核子时间流中的次领先自旋–轨道电荷项。

## 19. 完整三体暗物质流：已有的代表性数值诊断

三体暗物质侧有效流写作
\[
\mathcal T_3^\mu=\bar u_1(p')\,\Gamma^\mu(p,p',k_s)\,u_1(p),
\qquad
L^{\mu\nu}=\frac12\sum_{\rm spins}
\mathcal T_3^\mu\mathcal T_3^{\nu *}.
\]
\(\Gamma^\mu\) 必须由两张标量辐射图相加得到。其结构可写成
\[
\begin{aligned}
\Gamma^\mu_{(a)}&\sim
\gamma^\mu\frac{\slashed p-\slashed k_s+m_2}
{(p-k_s)^2-m_2^2+i m_2\Gamma_2},\\
\Gamma^\mu_{(b)}&\sim
\frac{\slashed p'+\slashed k_s+m_2}
{(p'+k_s)^2-m_2^2+i m_2\Gamma_2}\gamma^\mu,
\end{aligned}
\qquad
\Gamma^\mu=\Gamma^\mu_{(a)}+\Gamma^\mu_{(b)}.
\]
因此 \(L^{\mu\nu}\) 中包含两张辐射图各自的平方项和两图之间的干涉项。若只计算某一张图或把两图平方后直接相加，就不是完整的三体流结果。

此前讨论中曾报告如下代表性诊断：

| 项目 | 此前报告的设置 / 结果 | 证据状态 |
|---|---|---|
| 暗物质质量 | \(m_\chi=1\,{\rm TeV}\) | 代表性 benchmark |
| 入射速度 | \(v=800\,{\rm km/s}\) | 代表性 benchmark |
| 质量劈裂 | \(\Delta m=1\,{\rm MeV}\) | 代表性 benchmark |
| 标量质量 | \(m_s=200\text{--}360\,{\rm keV}\)；另有 \(m_s=300\,{\rm keV}\) 的单点报告 | 代表性扫描范围 / 单点 |
| \(\chi_2\) 宽度 | 条件性的 on-shell / pole-width 处理 | 宽度方案尚需与正式主线输入逐项核对 |
| 空间—时间张量比 | \(\displaystyle\frac{\sum_i L^{ii}}{L^{00}}\simeq(6.1\text{--}6.9)\times10^{-6}\) | 历史报告；未找到可独立重跑的原始脚本与完整输入清单 |
| 分量振幅尺度 | \(\displaystyle\sqrt{\frac{\sum_iL^{ii}}{L^{00}}}\simeq(2.5\text{--}2.6)\times10^{-3}\) | 由上述历史报告给出的量级 |
| 一个具体报告值 | \(m_s=300\,{\rm keV}\) 时，曾报告 \((L_{LL}+L_{TT})/L_{00}=6.276\text{--}6.571\times10^{-6}\)，空间流振幅约 \(2.5\times10^{-3}\) | 曾报告采用 \(8^3\) 有限求积；求积节点定义、积分边界及收敛记录未完整找回 |

这些结果支持的有限结论是：在所报告的代表性运动学点，暗物质侧空间流相对时间流较小，因而 \(\mathcal T_3^0\) 主导是合理的工作假设。

它们**不能**证明整个参数空间都具有同样的抑制，不能证明 \(L^{0i}\) 干涉项可以忽略，也不能证明完整核子流的空间分量或时间分量中的自旋–轨道项可以忽略。尤其要区分“暗物质侧 \(\Gamma^i\) 小”与“核子流中的所有非电荷算符小”。两图干涉据此前报告已保留在完整流构造中，但目前没有找回两张图各自贡献、交叉干涉项单独数值及对应的逐点收敛日志；因此本表应标为历史诊断，不应标成新的独立验收 PASS。

## 20. 点状、无自旋原子核：ppm 级修正的意义与边界

此前还报告过一个点核 sanity check。将靶核近似为点状、无自旋的复合粒子，使用完整弹性矢量流
\[
J_A^\mu=(P+P')^\mu,
\]
并将完整暗物质流与之收缩；以只保留时间分量的 \(L^{00}\) 结果为基准，得到：

| 核反冲能量 \(E_R\) | 完整点核流相对纯 \(L^{00}\) 基准的截面变化 |
|---:|---:|
| \(101\,{\rm keV}\) | \(-3.0\,{\rm ppm}\) |
| \(200\,{\rm keV}\) | \(-4.1\,{\rm ppm}\) |
| \(267\,{\rm keV}\) | \(-4.8\,{\rm ppm}\) |
| \(360\,{\rm keV}\) | \(-5.6\,{\rm ppm}\) |
| \(542\,{\rm keV}\) | \(-6.9\,{\rm ppm}\) |

这里的相对修正定义为
\[
\delta_{\rm pt}=10^6\left[
\frac{\sigma(J_A^\mu=(P+P')^\mu)}
{\sigma(\text{仅保留核电荷 / }L^{00}\text{ 基准})}-1
\right]\,{\rm ppm}.
\]
这组 ppm 数值是此前报告的点核诊断结果；当前没有找到与之配套的原始输出表、精确暗物质参数、逐点相空间求积和脚本，因此必须保留为“历史报告、待复现”，不能作为已完成的可复现核结构计算。

其物理意义是：它只检验整个原子核质心的平动电流。对重核，
\[
\frac{|\mathbf J_A|}{J_A^0}\sim\frac{|\mathbf q_A|}{2m_A}
\]
很小，故 ppm 级修正并不意外。

但点核流不包含核子内部坐标、内部动量、单核子自旋、磁化电流及自旋–轨道结构。它没有计算
\[
\sum_a e^{i\mathbf q_A\cdot\mathbf r_a}\mathbf p_a,\qquad
\sum_a e^{i\mathbf q_A\cdot\mathbf r_a}\boldsymbol\sigma_a,\qquad
\sum_a e^{i\mathbf q_A\cdot\mathbf r_a}
\boldsymbol\sigma_a\cdot\mathbf L_a
\]
等核内算符。因此，ppm 级点核修正只能说明核质心对流电流很小，**不能**排除核内部的 \(\Delta\)、磁化、自旋–轨道或 \(\Phi''\) 响应。

## 21. 从完整 Dirac–Pauli 核子流看时间分量的自旋–轨道项

核子矢量流应从
\[
J_N^\mu=\bar u_N(p_N')\left[
F_1^{V,N}(t_N)\gamma^\mu
+\frac{iF_2^{V,N}(t_N)}{2m_N}
\sigma^{\mu\nu}q_{N,\nu}
\right]u_N(p_N)
\]
出发，其中本节统一取 \(q_N=p_N'-p_N\)。在单体冲量近似中，核子流插入携带的外部转移与核整体转移 \(q_A=P_A'-P_A\) 对应；但束缚核子的能量分量和静态自由核子诊断的处理必须另行说明，不能在符号上直接把 \(q_N\) 与 \(q_A\) 混写。\(F_1\) 是 Dirac 电荷形状因子，\(F_2\) 是 Pauli / 磁化形状因子。

在非相对论展开中，除领先阶电荷项外，时间分量还含有自旋–轨道型修正。以协变归一化旋量、\(\mathbf K_N=(\mathbf p_N'+\mathbf p_N)/2\) 及上述动量方向为例，其结构可示意写为
\[
J_N^0=2m_NF_1^{V,N}(t_N)+\cdots
+i\,\frac{F_1^{V,N}(t)+2F_2^{V,N}(t)}{2m_N}
\boldsymbol\sigma_N\cdot(\mathbf q_N\times\mathbf K_N)
+\cdots.
\]
整体符号会随 \(q_N\)、\(\sigma^{\mu\nu}\) 和旋量归一化约定变化；上式用于指出结构及其 \(F_1+2F_2\) 组合，正式代码必须从固定约定重新推导并做自由核子对照。

这项结构的关键在于，它位于**核子流的时间分量**。因此完整振幅中存在
\[
\mathcal T_3^0\,\delta J_{N,\rm SO}^0,
\]
即使暗物质侧 \(\mathcal T_3^i\) 很小，暗物质侧领先阶时间流仍可与核子侧次领先自旋–轨道电荷项收缩。经 AFH 多极展开后，这类核子自旋–轨道结构需要检查 \(\Phi''\) 及其与质量响应的干涉 \(M\Phi''\)。

所以，不能采用以下推理：
\[
\Gamma^i\text{ 很小}\quad\Longrightarrow\quad W_{\Phi''}\text{ 很小}.
\]
正确的审计必须同时展开 \(J_N^0\) 和 \(\mathbf J_N\)，并将所有相关项与 \(\mathcal T_3^0,\mathcal T_3^i\) 收缩。

对当前 flavor-universal \(u,d,s\) 矢量流，零动量转移处 \(F_1^V(0)=3\) 给出 \(g_{VN}=3g_{Vq}\)，而采用 Bishara et al. (2017) Appendix A.1 的显式 flavor-separated 输入得到 \(F_2^V(0)=-0.552\)，不是零。相应的时间分量自旋—轨道组合为 \(F_1^V+2F_2^V=1.896\)，空间磁化组合为 \(F_1^V+F_2^V=2.448\)。因此暗物质时间流与核子时间流的自旋—轨道项收缩时不能把系数仍取为 3；但这些 form-factor 组合本身也不等于已经计算出的 AFH 核响应。有限 \(t_N\) 的剩余形状仍必须由实际 flavor form factors 加权求和得到。

## 22. 为什么优先检查 \(\mathcal O_3\)、\(W_{\Phi''}\) 和 \(W_{M\Phi''}\)

标准弹性 NR EFT 中
\[
\mathcal O_3=i\mathbf S_N\cdot
\left(\frac{\mathbf q_A}{m_N}\times\mathbf v^\perp\right)
\]
是一个含核子自旋与动量叉乘的算符。其核结构与 AFH 的自旋–轨道响应 \(W_{\Phi''}\) 相关，并会与质量响应产生 \(W_{M\Phi''}\) 干涉。这里的对应关系用于识别需要计算的核算符；三体过程含末态 \(k_s\) 和虚 \(\chi_2\) 传播子，不能直接把弹性过程的 \(\mathbf v^\perp\) 或二体 Wilson 系数搬过来，必须由完整 \(\mathcal T_3^\mu J_{N,\mu}\) 重新匹配。

\(\Phi''\) 不是普通意义上只测量总核自旋的 SD 响应。它编码核子自旋与轨道角动量耦合，可能具有准相干结构。因此，不能因为 Xe-129 / Xe-131 的总核自旋不大，就先验断言 \(\Phi''\) 很小；也不能因为总核自旋非零，就不加匹配地把全部 SD 响应加入模型。

当前排序应为：

| 响应 / 项目 | 物理来源 | 优先级与理由 |
|---|---|---|
| \(M\) | 领先阶核子矢量电荷 | 必须保留，现有基准 |
| \(\Phi''\) | 核子自旋–轨道结构；特别是时间分量的次领先电荷项 | 第一优先级 |
| \(M\Phi''\) | 质量响应与自旋–轨道响应干涉 | 第一优先级，必须与 \(\Phi''\) 同时计算 |
| \(\Sigma'\)、\(\Sigma''\) | 核子自旋 / 磁化流 | 第二层；先看完整匹配中的实际系数，不能预先设零 |
| \(\Delta\) | 对流 / 轨道运动相关核响应 | 由空间流匹配结果决定是否纳入 |
| 两核子流 | 核子间相互作用修正 | 第一轮暂不优先；单核子流完成后按手征计数与精度要求评估 |

暂不优先计算全部 \(\Sigma\)、\(\Delta\) 和两核子流，不等于宣称它们严格为零。理由是目前最有针对性的未知量是 \(\mathcal T_3^0\) 与核子时间流自旋–轨道项的收缩，以及 \(W_M\) 深极小值附近 \(W_{\Phi''}\) 和 \(W_{M\Phi''}\) 对谱形的影响。先完成这一主线，再根据匹配系数扩展响应集合，能避免无差别地增加核响应而引入未经证明的算符。

## 23. Xe-131 的三个 \(W_M\) 深极小值与单核子量级估算

此前 Xe-131 AFH 质量响应审计报告的三个重点极小值为：

| \(q_A\) (MeV) | 对应 \(E_R\) (keV) | \(q_A/m_N\) | \(R_M(q_A)/R_M(0)\) | \(\sqrt{R_M(q_A)/R_M(0)}\) |
|---:|---:|---:|---:|---:|
| 157.94 | 102.21 | 0.168 | \(1.2364\times10^{-5}\) | \(3.52\times10^{-3}\) |
| 256.27 | 269.10 | 0.273 | \(6.3407\times10^{-8}\) | \(2.52\times10^{-4}\) |
| 365.07 | 546.09 | 0.389 | \(1.5619\times10^{-7}\) | \(3.95\times10^{-4}\) |

这里 \(R_M\) 指按相同 AFH 归一化约定定义的质量响应。三个点都处在明显受抑制的质量响应区域，尤其第二、第三点的归一化振幅尺度已降至 \(10^{-4}\) 量级。若某个次领先核响应在相同 \(q_A\) 处没有相同的极小值，它可能改变局部谱形；但这并不意味着它一定填平极小值，必须计算对应核矩阵元及干涉项。

此前还给出过单核子层面的启发式 \(\mathcal O_3/\mathcal O_1\) 振幅量级：

| \(q_A\) (MeV) | 此前报告的单核子量级估算 |
|---:|---:|
| 157.94 | \(0.2\text{--}0.6\%\) |
| 256.27 | \(0.3\text{--}1.0\%\) |
| 365.07 | \(0.5\text{--}1.4\%\) |

旧表中的百分比保留为历史记录，但不再作为当前 benchmark 的输入。它们曾采用 \(|F_2/F_1|\sim0.1\)，而这个比例并非当前显式 flavor-separated 零动量基准。采用当前 \(F_1^V(0)=3\)、\(F_2^V(0)=-0.552\) 后，时间分量自旋—轨道项相对领先电荷项的单核子量级应按

\[
\epsilon_{\rm SO}^{(1N)}\sim
\frac{|F_1^V+2F_2^V|}{4|F_1^V|}
\frac{|\mathbf q_A|}{m_N}v_N^{\rm int}
=0.158\frac{|\mathbf q_A|}{m_N}v_N^{\rm int}
\]

重新估算。取 \(v_N^{\rm int}\sim0.1\text{--}0.3\)，在三个重点动量处得到约：

| \(|\mathbf q_A|\) [MeV] | 当前 benchmark 的单核子自旋—轨道振幅量级 |
|---:|---:|
| 158 | \(0.27\%\text{--}0.80\%\) |
| 256 | \(0.43\%\text{--}1.29\%\) |
| 365 | \(0.62\%\text{--}1.84\%\) |

这些仍然只是单核子算符的量级估算，不是 Xe-131 的 \(W_{\Phi''}/W_M\)，也不是三体截面修正；正式结果必须由完整三体系数和 AFH 核矩阵元计算得到。空间磁化项使用不同的 form-factor 组合 \(F_1^V+F_2^V=2.448\)，不能与时间分量的 \(1.896\) 混用。

还需区分 AFH 网格上的第一局部极小值与后续插值/精化位置：已有 AFH-7 归档曾报告 \(q\) 网格范围 \(0\text{--}0.6\,{\rm GeV}\)、步长 \(0.25\,{\rm MeV}\)，网格局部第一极小值约在 \(158.00\,{\rm MeV}\)，对应 \(F^2\simeq1.24\times10^{-5}\)；上表的 \(157.94\,{\rm MeV}\) 是此前报告的精化位置。两者相差约 \(0.06\,{\rm MeV}\)，不应误读为不同的物理极小值。第二、第三个位置也应在正式代码中用更细的局部网格和插值稳定性测试重新确认。

## 24. 从核子流到天然氙反冲谱：计算实施路线

建议按以下顺序实施，且每一步都保留独立输入、输出和 provenance：

1. **固定 UV 流与味道结构。** 明确 active flavors、各夸克耦合和重夸克是否积分掉；锁定 \(F_1^{V,p/n}(t)\)、\(F_2^{V,p/n}(t)\) 的定义、来源、误差和适用 \(q_A\) 区间。零动量检查 \(g_{Vp}=g_{Vn}=3g_{Vq}\)，同时验证显式 flavor-separated 输入给出的 \(F_2^V(0)=-0.552\)；不得把 HKS 紧凑式的字面零和当作当前 benchmark 输入。
2. **构造完整三体暗物质流。** 分别实现两张标量辐射图，保留两图干涉和 \(\chi_2\) 宽度；计算 \(\Gamma^0,\Gamma^i\) 及 \(L^{00},L^{0i},L^{ij}\)。在极点附近和相空间边界做求积收敛。
3. **完成 Dirac–Pauli 单核子匹配。** 对 \(\mathcal T_3^\mu J_{N,\mu}\) 作一致 NR 展开，明确 \(J_N^0\) 的自旋–轨道项、对流电流和磁化电流；从三体运动学重新定义速度组合，不直接套用弹性 \(\mathbf v^\perp\)。与自由核子直接 Dirac 自旋求和对照。
4. **优先实现 Xe-131 的 \(M+\Phi''+M\Phi''\)。** 先验证 AFH factor-four、零动量归一化和现有 \(M\) 结果，再生成 \(W_{\Phi''}\)、\(W_{M\Phi''}\)，特别在 \(q_A\simeq158,256,365\,{\rm MeV}\) 附近做高分辨率局部扫描。
5. **按匹配结果扩展。** 若 Wilson 系数显示横向磁化或对流项不可忽略，再加入 \(\Sigma'\)、\(\Sigma''\)、\(\Delta\)；两核子流在单核子结果和精度预算明确后再按手征计数评估。
6. **回到三体相空间与天然氙。** 保持已定义的 \(q_A,q_\chi,k_s,E_R\) 区分及原三体相空间；逐同位素计算完整响应，之后按天然丰度加权，再比较仅 \(M\) 与完整一体流的 \(dR/dE_R\)。探测器响应和似然仍是更后面的独立层级。

最低限度的验收应包括：点核极限恢复、自由核子极限、\(q_A\to0\) 的电荷归一化、Ward identity / 流守恒适用性、两图干涉、\(L^{0i}\) 项、\(M\Phi''\) 干涉、极小值附近的网格收敛，以及三体相空间和核响应插值的分别收敛。

## 25. 本补充中各项数值的证据等级

| 内容 | 本次记录的状态 | 后续要求 |
|---|---|---|
| AFH 七同位素 \(M\) 响应网格、因子 4、零动量归一化、多极闭合 | 已归档并有脚本 / 测试记录；见主文第 16 节及 PR #51 | 保持为当前可复现基线 |
| 三体暗物质侧 \(\sum_iL^{ii}/L^{00}\sim6.1\text{--}6.9\times10^{-6}\) | 此前报告的代表性诊断；原始脚本、逐点输入和完整收敛证据未找回 | 重新运行并归档 \(\Gamma^\mu,L^{\mu\nu}\)、求积和宽度设置 |
| 两张辐射图及其干涉 | 结构上必须保留；此前报告称已包含，但未找回分图 / 干涉独立数值 | 单独输出 \(|\mathcal M_a|^2\)、\(|\mathcal M_b|^2\)、\(2\mathrm{Re}(\mathcal M_a\mathcal M_b^*)\) |
| 点核完整流 ppm 修正 | 历史报告值；没有找到原始表格和脚本 | 用固定 benchmark 重算，检查与纯 \(L^{00}\) 的定义 |
| Xe-131 三个 \(W_M\) 深极小值 | 历史结果与 AFH 输出记录相符；需要重新核对精化位置、插值和归一化 | 局部高分辨率重算并记录 \(R_M/R_M(0)\) |
| 单核子 \(\mathcal O_3/\mathcal O_1\) 百分比 | 启发式估算，且旧估算区间存在轻微不一致；不适用于替代当前 universal-flavor 有限 \(t\) 匹配 | 由实际 \(F_1/F_2\) 及三体系数重新推导 |
| Xe-131 \(W_{\Phi''}\)、\(W_{M\Phi''}\) 与完整核流收缩 | 尚未完成 | 第一优先级数值工作 |
| \(\Sigma'\)、\(\Sigma''\)、\(\Delta\)、两核子流 | 尚未完成 / 暂不优先 | 由匹配系数和误差预算决定是否扩展 |

**补充结论：** 现有结果支持继续以 \(W_M^{00}\) 作为领先阶主线，但不能据此宣称完整 VV 核流已经由 \(W_M^{00}\) 穷尽。特别是，暗物质侧空间流很小和点状核质心电流只有 ppm 级修正，都不能排除核子时间流中的自旋–轨道电荷项。下一步最有判别力的计算仍然是：在完整三体 \(\mathcal T_3^\mu\) 下完成 flavor-universal Dirac–Pauli 核子流匹配，并定量计算 Xe-131 的 \(W_{\Phi''}\) 与 \(W_{M\Phi''}\)。

## 26. AFH v6.0 核结构响应与核子 Dirac–Pauli form factor：必须分开的两层物理

本节把项目后续计算中最容易混淆的两个“form factor”层级正式分开。我们决定采用 AFH DMFormFactor v6.0 作为氙核有限动量核结构响应的统一来源；但这不意味着 AFH 同时替我们完成了夸克到单核子的有限动量 Dirac、Pauli form-factor 匹配。

### 26.1 AFH 计算的是什么

AFH 的 \(W_M\)、\(W_{\Phi''}\)、\(W_{\Sigma'}\) 等对象是**原子核层面的响应函数**。它们由给定核子算符在具体核态上的矩阵元构造，包含：

- 核子在原子核中的空间分布和有限核尺寸；
- 壳模型轨道、角动量耦合及单体密度矩阵（OBDME）；
- 球贝塞尔函数与球谐函数的多极展开；
- 不同核算符在核态上的响应，以及 AFH 定义的交叉响应。

以质量/矢量电荷响应为例，AFH 使用

\[
y_A=\left(\frac{Q_A b_A}{2}\right)^2,
\qquad Q_A=|\mathbf q_A|,
\]

并通过核多极矩阵元计算 \(W_M^{\tau\tau'}(y_A)\)。它不是一个额外的相互作用，也不是单一均匀球体的 Helm 近似。

### 26.2 核子 \(F_1^N,F_2^N\) 计算的是什么

夸克矢量流到单核子的匹配则由

\[
\langle N'|J_V^\mu|N\rangle
=\bar u_N'\left[
F_1^{V,N}(t_N)\gamma^\mu
+\frac{iF_2^{V,N}(t_N)}{2m_N}
\sigma^{\mu\nu}q_{N,\nu}
\right]u_N
\]

描述。这里 \(F_1\) 是单核子 Dirac 形状因子，\(F_2\) 是单核子 Pauli/磁化形状因子。它们编码夸克、胶子在单个质子或中子内部的结构；它们不是 AFH 的核波函数或核密度矩阵。

因此必须明确：

\[
\boxed{\text{单核子 }F_1,F_2\quad\neq\quad\text{AFH 原子核响应 }W_X.}
\]

AFH v6.0 的核响应程序不会因为用户调用了 \(W_M\) 就自动把本模型的 flavor-universal \(F_1^{uds,N}(t_N)\)、\(F_2^{uds,N}(t_N)\) 作为有限动量输入乘进去。单核子 form factor 必须在核子流匹配层明确给出，再将其产生的核子算符投影到 AFH 响应上。

### 26.3 AFH v6.0 程序接口的实际含义

本项目采用的源文件是仓库中的 v6.0 Mathematica 程序。其接口将核响应组织为有限集合。源代码中 `ResponseNuclear` 的响应编号对应关系为：

| 程序编号 | AFH 核算符 / 响应 | 本项目的解释 |
|---:|---|---|
| 1 | \(M\) | 质量/矢量电荷响应，当前领先阶基准 |
| 2 | \(\Sigma''\) | 纵向自旋响应 |
| 3 | \(\Sigma'\) | 横向自旋响应 |
| 4 | \(\Phi''\) | 自旋—轨道响应，当前优先检查 |
| 5 | \(\widetilde\Phi'\) | AFH 另一种自旋—轨道相关响应；记号是 \(\widetilde\Phi'\)，不是 \(\widetilde\Phi''\) |
| 6 | \(\Delta\) | 轨道角动量响应 |
| 7 | \(M\)-\(\Phi''\) | 质量与自旋—轨道干涉响应 |
| 8 | \(\Sigma'\)-\(\Delta\) | 横向自旋与轨道响应的干涉 |

---

# 第三部分：从粒子物理到 AFH 核响应的逐步推导

本部分把前 26 节的物理结论改写成可以逐式检查的推导链。统一采用度规 \(g^{\mu\nu}=\mathrm{diag}(1,-1,-1,-1)\)，
\[
\sigma^{\mu\nu}=\frac{i}{2}[\gamma^\mu,\gamma^\nu],
\qquad
q_A=P_A'-P_A,\qquad
q_N=p_N'-p_N.
\]
除非特别说明，外部 \(\chi_1\) 与核子旋量采用协变归一化
\[
\bar u(p)u(p)=2m,\qquad \sum_s u(p,s)\bar u(p,s)=\slashed p+m.
\]
所有三维动量平方均写成 \(\mathbf q^2\ge0\)，Minkowski 不变量写成 \(t=q^2\le0\)。这样可以避免把 \(Q^2\) 与 \(t\) 混成同一个符号。

## 27. 从 UV 拉格朗日量到完整三体振幅

### 27.1 相互作用、质量本征态和过程

本项目的粒子物理输入为
\[
\begin{aligned}
\mathcal L_{\mathrm{int}}={}&
g_1 A'_\mu\bar\chi_2\gamma^\mu\chi_1
+g_2s\bar\chi_2\chi_1+\mathrm{h.c.}\\
&+g_q A'_\mu\sum_{q=u,d,s}\bar q\gamma^\mu q ,
\end{aligned}
\]
其中
\[
m_{\chi_1}=m_\chi,\qquad m_{\chi_2}=m_\chi+\Delta.
\]
这里 \(A'\) 是矢量媒介子，\(s\) 是末态实标量。两个相互作用顶点都改变暗物质的质量本征态：
\[
\chi_1\leftrightarrow\chi_2+A',
\qquad
\chi_1\leftrightarrow\chi_2+s.
\]
因此，外部态虽然是 \(\chi_1\) 入射、\(\chi_1\) 出射，但树级振幅的暗物质线上必须经过一次虚 \(\chi_2\) 传播。

过程为
\[
\chi_1(p)+A(P)\longrightarrow
\chi_1(p')+A(P')+s(k).
\]
四动量守恒给出
\[
p+P=p'+P'+k.
\]
定义媒介子传给核的动量
\[
q_A=P'-P,
\]
便有
\[
\boxed{q_A=p-p'-k.}
\]
这条等式是后续全部运动学的起点：媒介子传播子和 AFH 核响应使用 \(q_A\)，而不能把 \(p'-p\) 直接当作核动量转移。

### 27.2 两张辐射图的内部动量

沿暗物质费米子线从入射态走向出射态，标量可以在矢量散射之前或之后发射。

**图 a：先发射标量，再发生矢量散射。**

虚 \(\chi_2\) 的四动量为
\[
r_1=p-k.
\]
在矢量顶点处，
\[
r_1-q_A=p-k-(p-p'-k)=p',
\]
所以内部动量流与外部四动量守恒一致。传播子分母为
\[
D_1=r_1^2-m_{\chi_2}^2
=(p-k)^2-m_{\chi_2}^2.
\]

**图 b：先发生矢量散射，再发射标量。**

虚 \(\chi_2\) 的四动量为
\[
r_2=p'+k.
\]
在矢量顶点处，
\[
p-r_2=p-p'-k=q_A.
\]
对应分母为
\[
D_2=r_2^2-m_{\chi_2}^2
=(p'+k)^2-m_{\chi_2}^2.
\]

两图的费米子链顺序不同，因而不能把两张图简单视为同一个标量因子的重复。去掉整体耦合后，完整顶点矩阵为
\[
\boxed{
\widehat\Gamma_3^\mu=
\gamma^\mu
\frac{\slashed r_1+m_{\chi_2}}{D_1+i m_{\chi_2}\Gamma_{\chi_2}}
+
\frac{\slashed r_2+m_{\chi_2}}{D_2+i m_{\chi_2}\Gamma_{\chi_2}}
\gamma^\mu .
}
\]
这里写的是固定宽度形式；远离极点时可令 \(\Gamma_{\chi_2}\to0\)。整体振幅为
\[
\mathcal T_3^\mu
=g_1g_2\,\bar u_{\chi_1}(p')\widehat\Gamma_3^\mu
u_{\chi_1}(p).
\]
相对正号对应本项目拉格朗日量中两个实耦合及所选费米子线方向。程序实现时必须使用同一套 Feynman 规则，不能在其中一张图上人为改变相位。

### 27.3 媒介子传播子与核流因子化

在 Proca/幺正规范下，质量为 \(m_{A'}\) 的矢量传播子可写成
\[
D_{\mu\nu}^{A'}(q_A)=
\frac{-i}{t_A-m_{A'}^2}
\left(g_{\mu\nu}-\frac{q_{A\mu}q_{A\nu}}{m_{A'}^2}\right),
\qquad t_A=q_A^2.
\]
令
\[
J_A^\nu(q_A)=
\langle A(P')|J_V^\nu(q_A)|A(P)\rangle
\]
表示包含夸克—核子耦合后的核矢量流，则完整振幅是
\[
\boxed{
\mathcal M_3=
\mathcal T_3^\mu D_{\mu\nu}^{A'}(q_A)J_A^\nu(q_A).
}
\]
若把 \(g_q\) 放在 \(J_A^\nu\) 中，就不能再在振幅前额外乘一次 \(g_q\)；若把 \(g_q\) 从核流中提出，则应在整体系数中显式保留。两种记账方式等价，但只能选一种。

对弹性、守恒的核矢量流，
\[
q_{A\nu}J_A^\nu=0.
\]
因此传播子的纵向项满足
\[
\frac{q_{A\mu}q_{A\nu}}{m_{A'}^2}
\mathcal T_3^\mu J_A^\nu=0,
\]
完整振幅在该条件下简化为
\[
\mathcal M_3=
\frac{-i}{t_A-m_{A'}^2}\,
\mathcal T_{3\mu}J_A^\mu.
\]
注意：这个简化使用的是**核侧**流守恒，并不要求暗物质三体流本身守恒。事实上，\(\chi_1\) 与 \(\chi_2\) 质量不同，三体暗物质流一般不守恒，见 §27.5。

当 \(m_{A'}^2\gg |t_A|\) 时，
\[
\frac{1}{t_A-m_{A'}^2}
=-\frac{1}{m_{A'}^2}
\left[1+\frac{t_A}{m_{A'}^2}+\cdots\right].
\]
只有在该条件成立时才可将媒介子交换近似成局域接触相互作用；若 \(m_{A'}\) 与 \(|\mathbf q_A|\) 同量级，必须保留完整传播子。

### 27.4 重质量、离壳极限下的两图相干因子

为了理解论文中出现的因子 2，取
\[
m_{\chi_2}=m_\chi+\Delta,\qquad
\Delta\gg E_s,\ |\mathbf q_A|v,\ \frac{\mathbf q_A^2}{2m_\chi}.
\]
在暗物质重粒子近似下，令 \(v^\mu\) 为暗物质四速度，
\[
P_+=\frac{1+\slashed v}{2}.
\]
内部传播子的分子在领先阶满足
\[
\slashed r_{1,2}+m_{\chi_2}
\simeq 2m_\chi P_++\mathcal O(\Delta,k,\mathbf q_A),
\]
分母满足
\[
D_{1,2}\simeq -2m_\chi\Delta
+\mathcal O(m_\chi E_s,m_\chi v|\mathbf q_A|).
\]
再利用
\[
P_+\gamma^\mu P_+=v^\mu P_+,
\]
两张图在领先阶都约化到同一暗物质矢量流结构：
\[
\mathcal T_3^\mu
\simeq
-\frac{2g_1g_2}{\Delta}\,
\bar u_{\chi_1}(p')v^\mu u_{\chi_1}(p)
+\mathcal O\!\left(\frac{E_s}{\Delta},
\frac{|\mathbf q_A|}{m_\chi}\right).
\]
这里的整体符号取决于传播子和振幅约定；可观测的关键是两图在所选 benchmark 下相干相加，领先阶振幅出现因子 2。

因此，与只含一条相应跃迁矢量流的二体参考振幅比较时，
\[
\frac{\overline{|\mathcal M_{2\to3}|^2}}
{\overline{|\mathcal M_{2\to2}|^2}}
\simeq \frac{4g_2^2}{\Delta^2},
\]
但这个量具有能量负二次量纲，**不是截面比**。真正的截面比还必须乘三体相空间因子，见 §28.4。

该近似不能用于接近 \(\chi_2\) 极点的区域。靠近极点时，\(D_1,D_2\) 对 \(k\) 和角变量的依赖不同，两图的相对大小和干涉都可能改变，必须使用完整的 Breit–Wigner 分母逐点积分。

### 27.5 \(\chi_2\) 宽度与三体流的 Ward 收缩

若衰变通道 \(\chi_2\to\chi_1+s\) 开放，即
\[
m_{\chi_2}>m_{\chi_1}+m_s,
\]
且拉格朗日量中的标量顶点为 \(g_2s\bar\chi_2\chi_1+\mathrm{h.c.}\)，则仅考虑该衰变道时
\[
\boxed{
\Gamma(\chi_2\to\chi_1s)=
\frac{g_2^2}{16\pi m_{\chi_2}^3}
\lambda^{1/2}(m_{\chi_2}^2,m_{\chi_1}^2,m_s^2)
\left[(m_{\chi_2}+m_{\chi_1})^2-m_s^2\right],
}
\]
其中
\[
\lambda(x,y,z)=x^2+y^2+z^2-2xy-2xz-2yz.
\]
若还存在其他衰变道，传播子中使用的总宽度应为所有开放道的部分宽度之和，而不是只使用上式。

现在推导三体暗物质流的 Ward 收缩。定义
\[
q_A=p-p'-k=r_1-p'=p-r_2,
\]
并先取零宽度。利用外部 \(\chi_1\) 的 Dirac 方程
\[
(\slashed p-m_\chi)u(p)=0,\qquad
\bar u(p')(\slashed p'-m_\chi)=0,
\]
第一张图有
\[
\begin{aligned}
&\bar u(p')\slashed q_A
(\slashed r_1+m_{\chi_2})u(p)\\
&=\bar u(p')(\slashed r_1-m_\chi)
(\slashed r_1+m_{\chi_2})u(p)\\
&=\bar u(p')
\left[D_1+(m_{\chi_2}-m_\chi)
(\slashed r_1+m_{\chi_2})\right]u(p).
\end{aligned}
\]
第二张图则为
\[
\begin{aligned}
&\bar u(p')(\slashed r_2+m_{\chi_2})
\slashed q_Au(p)\\
&=\bar u(p')(\slashed r_2+m_{\chi_2})
(m_\chi-\slashed r_2)u(p)\\
&=\bar u(p')
\left[-D_2-(m_{\chi_2}-m_\chi)
(\slashed r_2+m_{\chi_2})\right]u(p).
\end{aligned}
\]
两式除以各自的 \(D_i\) 后，常数项 \(+1\) 与 \(-1\) 抵消，得到
\[
\boxed{
q_{A\mu}\mathcal T_3^\mu
=(m_{\chi_2}-m_\chi)g_1g_2\,
\bar u(p')
\left[
\frac{\slashed r_1+m_{\chi_2}}{D_1}
-\frac{\slashed r_2+m_{\chi_2}}{D_2}
\right]u(p).
}
\]
因此：
- 若 \(m_{\chi_2}=m_\chi\)，零宽度下两张图的 Ward 收缩相消；
- 若 \(m_{\chi_2}\ne m_\chi\)，三体暗物质流一般不守恒；
- 不能把弹性守恒矢量流的简化恒等式直接套到本模型。

还要注意有限宽度的实现。令 \(a=m_{\chi_2}\Gamma_{\chi_2}\)、\(\mathcal D_i=D_i+ia\)。若只把两个实分母替换成 \(\mathcal D_i\)，而分子仍保留实质量，则直接重复上面的代数得到
\[
q_{A\mu}\mathcal T_{3,\Gamma}^\mu
=(m_{\chi_2}-m_\chi)g_1g_2\bar u'
\left[
\frac{\slashed r_1+m_{\chi_2}}{\mathcal D_1}
-\frac{\slashed r_2+m_{\chi_2}}{\mathcal D_2}
\right]u
+iag_1g_2\bar u'u
\left(\frac{1}{\mathcal D_2}-\frac{1}{\mathcal D_1}\right).
\]
最后一项正是两个常数项不再严格抵消留下的固定宽度残项。它不是新的物理顶点，而是固定宽度插入对 Ward 恒等式的影响。数值实现必须明确使用固定宽度、能量依赖自能还是复极点方案，并将方案差异纳入极点附近的误差审计。不能在一张图中加宽度、另一张图中不加，也不能把有限宽度下的零宽度 Ward 公式当成严格恒等式。

## 28. 三体运动学、相空间和 \(I(D)\) 的推导

### 28.1 核反冲的精确动量关系

初始核静止：
\[
P^\mu=(m_A,\mathbf 0),\qquad
P'^\mu=(m_A+E_R,\mathbf q_A).
\]
由 \(P'^2=P^2=m_A^2\)，
\[
(m_A+E_R)^2-\mathbf q_A^2=m_A^2,
\]
因此
\[
\boxed{
Q_A^2\equiv|\mathbf q_A|^2=E_R(E_R+2m_A),
\qquad t_A=q_A^2=-2m_AE_R.
}
\]
非相对论近似为
\[
Q_A\simeq\sqrt{2m_AE_R}.
\]
论文中的 \(q=\sqrt{2m_AE_R}\) 正是这一近似；AFH 的 \(y_A\) 应优先使用精确的 \(Q_A\)，传播子则使用 \(t_A\)。

### 28.2 \(\chi_1s\) 不变质量与内部动能

定义末态暗物质—标量系统总四动量
\[
K^\mu=p'^\mu+k^\mu,\qquad W^2=K^2.
\]
将其不变质量参数化为
\[
W=m_\chi+m_s+\epsilon,\qquad \epsilon\ge0.
\]
这里 \(\epsilon\) 是 \(\chi_1s\) 在自身质心系中的内部运动能量，不是核反冲能量，也不是标量的总能量。

初始暗物质动量记为 \(\mathbf p=m_\chi\mathbf v\)。在 \(m_\chi\gg m_s\)、\(E_R\ll m_A\) 的重粒子非相对论近似下，末态 \(\chi_1s\) 系统质心动量为
\[
\mathbf K=\mathbf p-\mathbf q_A.
\]
能量守恒写成
\[
m_\chi+\frac{\mathbf p^2}{2m_\chi}+m_A
=
m_\chi+m_s+\epsilon
+\frac{|\mathbf p-\mathbf q_A|^2}{2m_\chi}
+m_A+E_R.
\]
展开平方并使用
\[
E_R\simeq\frac{Q_A^2}{2m_A},
\]
得到
\[
\epsilon=
\mathbf v\cdot\mathbf q_A
-\frac{Q_A^2}{2m_\chi}
-\frac{Q_A^2}{2m_A}
-m_s.
\]
定义约化质量
\[
\mu=\frac{m_\chi m_A}{m_\chi+m_A},
\]
并令 \(\theta\) 为入射速度与核反冲动量之间的夹角，则
\[
\boxed{
\epsilon=vQ_A\cos\theta-\frac{Q_A^2}{2\mu}-m_s.
}
\]
在固定 \(E_R\) 和 \(v\) 下，最大内部能量出现在 \(\cos\theta=1\)：
\[
\boxed{
D(E_R,v)=vQ_A-\frac{Q_A^2}{2\mu}-m_s
=Q_A[v-v_{\min}(E_R)],
}
\]
其中
\[
\boxed{
v_{\min}(E_R)=\frac{Q_A}{2\mu}+\frac{m_s}{Q_A}.
}
\]
因此允许的内部能量区间为
\[
0\le\epsilon\le D,
\]
且只有 \(D\ge0\) 时才存在物理相空间。

这里的 \(m_s\) 来自末态必须产生一个真实标量的静质量；\(\epsilon\) 则描述在此阈值之上的额外内部运动能量。把两者混成一个“有效质量劈裂”会丢失三体末态的连续不变质量自由度。

### 28.3 阈值、反冲端点和谱峰位置

由
\[
D(Q_A,v)=vQ_A-\frac{Q_A^2}{2\mu}-m_s\ge0
\]
可知 \(D\) 是关于 \(Q_A\) 的开口向下二次函数。其最大值出现在
\[
\frac{\partial D}{\partial Q_A}
=v-\frac{Q_A}{\mu}=0,
\qquad Q_A^{\rm peak}=\mu v.
\]
最大内部能量为
\[
D_{\max}=\frac{\mu v^2}{2}-m_s.
\]
故存在可行反冲的阈值速度为
\[
\boxed{v_{\rm thr}=\sqrt{\frac{2m_s}{\mu}}.}
\]
在 \(D=0\) 处解出两根：
\[
Q_A^\pm=\mu\left(v\pm\sqrt{v^2-\frac{2m_s}{\mu}}\right).
\]
再用 \(E_R\simeq Q_A^2/(2m_A)\)，得到
\[
\boxed{
E_R^\pm(v)=\frac{\mu^2}{2m_A}
\left(v\pm\sqrt{v^2-\frac{2m_s}{\mu}}\right)^2.
}
\]
二体非弹性散射若取质量劈裂 \(\delta=m_s\)，有相同的 \(v_{\min}\) 和相同的两个反冲端点；差别在于二体末态的不变质量固定，而三体末态还要积分 \(0\le\epsilon\le D\)。

谱峰位置由 \(Q_A^{\rm peak}=\mu v\) 给出：
\[
\boxed{
E_R^{\rm peak}(v)=\frac{\mu^2v^2}{2m_A}.
}
\]
这是固定入射速度、常振幅近似下三体相空间核的峰位置，不应直接解释为 halo 平均后的实验谱峰；后者还要积分速度分布、乘核响应并进行同位素求和。

### 28.4 三体相空间如何产生 \(I(D)\)

三体相空间的关键是把末态 \(\chi_1s\) 看成一个总不变质量为 \(W\) 的复合系统。令 \(K=p'+k\)，有标准相空间恒等式
\[
d\Phi_3(P_i;P',p',k)
=
\frac{dW^2}{2\pi}\,
d\Phi_2(P_i;P',K)\,
d\Phi_2(K;p',k).
\]
右侧第一项描述初态到核加 \(\chi_1s\) 系统的外层二体运动学；第二项描述 \(\chi_1s\) 系统内部的二体衰变相空间。

在 \(K\) 的质心系，内部相对动量大小为
\[
p_*=
\frac{\lambda^{1/2}(W^2,m_\chi^2,m_s^2)}{2W}.
\]
积分内部两体角度后，
\[
\int d\Phi_2(K;p',k)=\frac{p_*}{4\pi W}.
\]
又因为
\[
W=m_\chi+m_s+\epsilon,\qquad dW^2=2W\,d\epsilon,
\]
故
\[
\frac{dW^2}{2\pi}\int d\Phi_2(K;p',k)
=
\frac{p_*}{4\pi^2}\,d\epsilon.
\]
这一步直接说明：在外层核反冲运动学固定后，剩余内部相空间自然带有 \(p_*d\epsilon/(4\pi^2)\)，而不是简单的 \(d\epsilon\)。

对 \(m_\chi\gg m_s,\epsilon\)，Källén 函数可展开为
\[
p_*=
\sqrt{\epsilon(\epsilon+2m_s)}
\left[1+\mathcal O\!\left(\frac{m_s+\epsilon}{m_\chi}\right)\right].
\]
若进一步假设矩阵元在允许的内部不变质量和内部角度范围内变化缓慢，外层运动学因子也可在该区间近似提出积分，则内部相空间核为
\[
\boxed{
I(D)=\int_0^D d\epsilon\,
\sqrt{\epsilon(\epsilon+2m_s)},\qquad D>0,
}
\]
而 \(D\le0\) 时 \(I(D)=0\)。

这个积分可以解析完成。令 \(x=\epsilon+m_s\)，则
\[
I(D)=\int_{m_s}^{m_s+D}dx\,\sqrt{x^2-m_s^2}.
\]
使用
\[
\int dx\,\sqrt{x^2-a^2}
=\frac12\left[x\sqrt{x^2-a^2}
-a^2\ln\left(x+\sqrt{x^2-a^2}\right)\right],
\]
得到
\[
\boxed{
I(D)=\frac12\left[
(D+m_s)\sqrt{D(D+2m_s)}
-m_s^2\ln\frac{D+m_s+\sqrt{D(D+2m_s)}}{m_s}
\right].
}
\]
因此 \(I(D)\) 的量纲是能量平方，恰好补偿振幅平方比 \(4g_2^2/\Delta^2\) 的能量负二次量纲。

当 \(D\ll m_s\) 时，
\[
\sqrt{\epsilon(\epsilon+2m_s)}
=\sqrt{2m_s\epsilon}
\left[1+\frac{\epsilon}{4m_s}
+\mathcal O\!\left(\frac{\epsilon^2}{m_s^2}\right)\right],
\]
逐项积分可得
\[
\boxed{
I(D)=\frac23\sqrt{2m_s}\,D^{3/2}
\left[1+\frac{3D}{20m_s}
+\mathcal O\!\left(\frac{D^2}{m_s^2}\right)\right].
}
\]
这说明三体微分谱在两个反冲端点附近按 \(D^{3/2}\) 关闭，而二体非弹性谱在相同运动学端点并没有这一个内部相空间幂次。

**适用边界非常重要：** 如果 \(D_1,D_2\) 接近 \(\chi_2\) 极点，或者矩阵元明显依赖 \(k\) 的能量和角度，就不能把 \(\mathcal M_3\) 从内部积分中提出。此时必须使用
\[
\int_0^D d\epsilon\int d\Omega_*\,
p_*(\epsilon)\,
\overline{|\mathcal M_3(\epsilon,\Omega_*)|^2}
\]
及完整外层 Jacobian 做数值积分。\(I(D)\) 是常振幅、重粒子极限下的解析相空间核，不是对所有 Breit–Wigner 参数点都精确的完整三体截面。

### 28.5 与二体非弹性散射的对照

在 \(m_{A'}^2\gg Q_A^2\)、\(\Delta\gg E_s\) 且两张辐射图可用同一领先阶系数近似时，振幅平方比约为
\[
\frac{\overline{|\mathcal M_{2\to3}|^2}}
{\overline{|\mathcal M_{2\to2}|^2}}
\simeq\frac{4g_2^2}{\Delta^2}.
\]
再乘上 §28.4 得到的内部相空间，固定速度、固定反冲能量下有
\[
\boxed{
\frac{d\sigma_{2\to3}/dE_R}
{d\sigma_{2\to2}/dE_R}
\simeq
\frac{4g_2^2}{\Delta^2}\frac{I(D)}{4\pi^2},
}
\]
这里两种过程采用相同核响应、相同矢量耦合归一化和相同外层运动学近似。若核响应或振幅具有显著 \(W\) 依赖，必须回到完整积分，不能使用该简式。

等 \(v_{\min}\) 的两支反冲能量也可直接从运动学推导。由
\[
v_{\min}(Q_A)=\frac{Q_A}{2\mu}+\frac{m_s}{Q_A}
\]
可知在给定 \(v_{\min}\) 下，两根 \(Q_L,Q_H\) 满足
\[
Q_LQ_H=2\mu m_s.
\]
使用 \(E_R\simeq Q_A^2/(2m_A)\)，
\[
E_LE_H=\left(\frac{\mu m_s}{m_A}\right)^2.
\]
定义
\[
E_c=\frac{\mu m_s}{m_A},
\]
便有
\[
\boxed{E_LE_H=E_c^2,\qquad
v_{\min}(E_L)=v_{\min}(E_H).}
\]
常振幅二体谱在这两个反冲点采样相同的 halo 积分；三体谱还乘 \(I[D]\)，而较高反冲支具有较大的 \(Q_A\)，在相同 \(v-v_{\min}>0\) 下有较大的 \(D=Q_A(v-v_{\min})\)，所以 \(I(D)\) 更大。

若两个分支贡献速度都满足 \(D\ll m_s\)，则 \(I(D)\propto D^{3/2}\)。在相同 \(v_{\min}\) 的近阈值近似下，
\[
\frac{\widetilde R_{2\to3}(E_H)}
{\widetilde R_{2\to3}(E_L)}
\simeq
\left(\frac{Q_H}{Q_L}\right)^{3/2}
=
\left(\frac{E_H}{E_L}\right)^{3/4}.
\]
这不是完整天然氙实验谱的普适恒等式；它只适用于单同位素、常振幅、相同 halo 输入且 \(D/m_s\) 足够小的近似情形。

## 29. 从夸克矢量流到单核子 Dirac–Pauli form factors

### 29.1 Lorentz 分解为什么只需要 \(F_1\) 和 \(F_2\)

对同种、等质量的外部核子，矢量流矩阵元在 Lorentz 协变性、宇称和时间反演约束下可写成
\[
\boxed{
\langle N(p_N')|J_V^\mu|N(p_N)\rangle
=
\bar u_N(p_N')
\left[
F_1^{V,N}(t_N)\gamma^\mu+
\frac{iF_2^{V,N}(t_N)}{2m_N}
\sigma^{\mu\nu}q_{N\nu}
\right]
u_N(p_N).
}
\]
这里
\[
q_N=p_N'-p_N,\qquad t_N=q_N^2.
\]
\(F_1\) 是 Dirac form factor，控制矢量电荷；\(F_2\) 是 Pauli form factor，控制反常磁化结构。对本项目的 flavor-universal 低能流，
\[
J_{uds}^\mu=\bar u\gamma^\mu u+\bar d\gamma^\mu d+\bar s\gamma^\mu s,
\]
总 form factor 是各味道矩阵元的线性组合：
\[
F_i^{uds,N}(t_N)=
F_i^{u,N}(t_N)+F_i^{d,N}(t_N)+F_i^{s,N}(t_N).
\]
如果 UV 耦合不是等权重，则必须保留
\[
F_i^{V,N}(t_N)=\sum_q c_q F_i^{q,N}(t_N),
\]
其中 \(c_q\) 由 UV 电荷赋值和重味阈值匹配决定。

### 29.2 \(F_1(0)\) 从价夸克数得到

在零动量转移下，矢量流积分就是对应味道的守恒净夸克数。因此对质子
\[
F_1^{u/p}(0)=2,\qquad
F_1^{d/p}(0)=1,\qquad
F_1^{s/p}(0)=0.
\]
同位旋对称下中子交换 \(u\leftrightarrow d\)：
\[
F_1^{u/n}(0)=1,\qquad
F_1^{d/n}(0)=2,\qquad
F_1^{s/n}(0)=0.
\]
所以
\[
\boxed{
F_1^{uds,p}(0)=F_1^{uds,n}(0)=3.
}
\]
若每个夸克味道的媒介子耦合为 \(g_q\)，则
\[
\boxed{g_{Vp}=g_{Vn}=3g_q.}
\]
这是当前 benchmark 的零动量等标量电荷匹配，不代表有限动量下完整核子流只是常数 \(3\gamma^\mu\)。

### 29.3 \(F_2(0)\) 的显式 flavor 重构

Pauli form factor 在零动量处给出各味道对核子反常磁矩的贡献。Bishara et al.，arXiv:1707.06998，Appendix A.1 的输入为
\[
a_p=1.793,\qquad a_n=-1.913,\qquad
F_2^{s/p}(0)=-0.064(17).
\]
由电磁流的 flavor 分解和同位旋对称关系，
\[
\begin{aligned}
F_2^{u/p}(0)&=2a_p+a_n+F_2^{s/p}(0)
=1.609(17),\\
F_2^{d/p}(0)&=a_p+2a_n+F_2^{s/p}(0)
=-2.097(17).
\end{aligned}
\]
于是
\[
\boxed{
F_2^{uds,p}(0)
=1.609-2.097-0.064=-0.552.
}
\]
中子由 \(u\leftrightarrow d\) 得到相同的三味总和：
\[
\boxed{F_2^{uds,n}(0)\simeq-0.552.}
\]
所以当前零动量 benchmark 有
\[
\frac{F_2^{uds}}{F_1^{uds}}=-0.184,\qquad
F_1^{uds}+2F_2^{uds}=1.896,\qquad
F_1^{uds}+F_2^{uds}=2.448.
\]
这里不能把 \(F_2^{uds}(0)\) 设为零，也不能把质子和中子各自的电磁反常磁矩直接当成三味等权重流的 Pauli form factor。

**文献表示差异必须保留：** HKS 1503.04811 Eq. (23) 确实写出
\[
F_2^{u,N}=\kappa_N+\mathcal O(t),\qquad
F_2^{d,N}=-\kappa_N-\kappa_N^s+\mathcal O(t),\qquad
F_2^{s,N}=\kappa_N^s+\mathcal O(t),
\]
其字面三味和为零。另一方面，HKS Eq. (21) 的显式 flavor 重构式结合物理 \(\kappa_p,\kappa_n,\kappa_s\)，以及 Bishara et al. 1707.06998 Appendix A.1 Eqs. (80)–(82)，给出 \(1.609,-2.097,-0.064\)，其和为 \(-0.552\)。因此这里不是简单的“Eq. (23) 不含零和”，而是两个表示在同一组 \(\kappa\) 定义下存在需要追溯的差异。本文当前 benchmark 使用可直接由显式质子/中子磁矩关系重构的 Bishara 数值；在完成 HKS Eq. (23) 的符号、近似和 \(\kappa_N\) 定义审计前，不将其字面零和式作为当前模型的输入，也不宣称这项文献差异已经解决。

### 29.4 Sachs form factors 与有限 \(t_N\)

定义
\[
\tau_N=-\frac{t_N}{4m_N^2}
=\frac{Q_N^2}{4m_N^2},
\qquad Q_N^2=-t_N,
\]
则 Sachs 电、磁 form factors 为
\[
\boxed{
G_E^N(t_N)=F_1^N(t_N)-\tau_NF_2^N(t_N),
\qquad
G_M^N(t_N)=F_1^N(t_N)+F_2^N(t_N).
}
\]
因此
\[
F_1^N=\frac{G_E^N+\tau_NG_M^N}{1+\tau_N},
\qquad
F_2^N=\frac{G_M^N-G_E^N}{1+\tau_N}.
\]
这些关系可以用于把实验或格点给出的 Sachs 形状转成 Dirac–Pauli 输入。

Bishara et al. Appendix A.1 还给出零动量处 \(F_1\) 的斜率中心值：
\[
F_1^{u/p\,\prime}(0)=5.57(9)\ {\rm GeV}^{-2},\quad
F_1^{d/p\,\prime}(0)=2.84(5)\ {\rm GeV}^{-2},\quad
F_1^{s/p\,\prime}(0)=-0.018(9)\ {\rm GeV}^{-2}.
\]
等权重三味和的中心斜率为
\[
F_1^{uds,p\,\prime}(0)\simeq8.392\ {\rm GeV}^{-2},
\]
中子在同位旋对称近似下相同。它只允许写出局部展开
\[
F_1^{uds,N}(t_N)
=3+8.392\,t_N+\mathcal O(t_N^2),
\]
不能把这条线性展开无条件外推到本项目全部 \(Q_A\) 区间。尤其 \(Q_A\sim0.3\)–\(0.4\) GeV 时，高阶曲率和 flavor 相关形状可能重要；Bishara 的 \(F_2(0)\) 中心值也不等于已经给出了完整 \(F_2(t_N)\)。有限 \(t_N\) 的 \(F_1,F_2\) 及协方差仍需独立输入。

### 29.5 \(t_A\) 与 \(t_N\) 的关系

AFH 使用核整体三维动量 \(Q_A=|\mathbf q_A|\)，媒介子传播子使用 \(t_A=q_A^2\)，而单核子 form factor 使用 \(t_N=q_N^2\)。在严格的一体冲量近似中，若核子顶点携带完整外部四动量转移 \(q_N=q_A\)，则
\[
t_N=t_A=-2m_AE_R.
\]
若只做静态自由核子诊断并人为令 \(q_N^0=0\)，则
\[
t_N=-Q_A^2=t_A-E_R^2.
\]
这两个处方的差别不是符号问题，而是不同的核子能量转移近似。正式计算必须在 metadata 中记录所用处方；不能把 \(Q_A^2\)、\(t_A\)、\(t_N\) 混为一个 q2。


## 30. Dirac–Pauli 核子流的非相对论展开：逐项推导

本节是从单核子流进入 AFH 核结构的关键。不能只引用一个 \(F_1+2F_2\) 的结果；必须同时说明旋量归一化、动量方向、Pauli 项符号以及时间、空间分量分别来自哪里。

### 30.1 运动学变量和外部旋量

定义单核子平均动量
\[
\mathbf K_N=\frac{\mathbf p_N'+\mathbf p_N}{2},
\qquad
\mathbf q_N=\mathbf p_N'-\mathbf p_N.
\]
于是
\[
\mathbf p_N'=\mathbf K_N+\frac{\mathbf q_N}{2},
\qquad
\mathbf p_N=\mathbf K_N-\frac{\mathbf q_N}{2}.
\]
非相对论展开参数为
\[
\frac{|\mathbf K_N|}{m_N}\ll1,\qquad
\frac{Q_N}{m_N}\ll1,\qquad
Q_N=|\mathbf q_N|.
\]
采用 \(\bar u u=2m_N\) 的 Dirac 旋量：
\[
u(\mathbf p)=
\sqrt{E_{\mathbf p}+m_N}
\begin{pmatrix}
\xi\\[2pt]
\dfrac{\boldsymbol\sigma\cdot\mathbf p}
{E_{\mathbf p}+m_N}\xi
\end{pmatrix},
\qquad
E_{\mathbf p}=\sqrt{m_N^2+\mathbf p^2}.
\]
展开到所需阶：
\[
E_{\mathbf p}=m_N+\frac{\mathbf p^2}{2m_N}
+\mathcal O\!\left(\frac{p^4}{m_N^3}\right),
\]
\[
\frac{1}{E_{\mathbf p}+m_N}
=\frac{1}{2m_N}
+\mathcal O\!\left(\frac{p^2}{m_N^3}\right).
\]
整个计算只需要 Pauli 矩阵恒等式
\[
(\boldsymbol\sigma\cdot\mathbf a)
(\boldsymbol\sigma\cdot\mathbf b)
=\mathbf a\cdot\mathbf b
+i\boldsymbol\sigma\cdot(\mathbf a\times\mathbf b).
\]

### 30.2 时间分量的 Dirac 项

先计算不含 Pauli form factor 的时间分量：
\[
J_{D}^{0}
=F_1\bar u(\mathbf p_N')\gamma^0u(\mathbf p_N).
\]
代入旋量，并保留到二阶动量：
\[
\begin{aligned}
\bar u'\gamma^0u
={}&2m_N\,\xi'^\dagger
\left[
1+\frac{\mathbf p_N'^2+\mathbf p_N^2}{8m_N^2}
+\frac{(\boldsymbol\sigma\cdot\mathbf p_N')
(\boldsymbol\sigma\cdot\mathbf p_N)}
{4m_N^2}
\right]\xi+\cdots\\
={}&2m_N\,\xi'^\dagger
\left[
1+\frac{\mathbf p_N'^2+\mathbf p_N^2
+2\mathbf p_N'\cdot\mathbf p_N}{8m_N^2}
+\frac{i\boldsymbol\sigma\cdot
(\mathbf p_N'\times\mathbf p_N)}{4m_N^2}
\right]\xi+\cdots .
\end{aligned}
\]
由平均动量定义，
\[
\mathbf p_N'^2+\mathbf p_N^2
+2\mathbf p_N'\cdot\mathbf p_N
=(\mathbf p_N'+\mathbf p_N)^2
=4\mathbf K_N^2,
\]
而
\[
\mathbf p_N'\times\mathbf p_N
=\mathbf q_N\times\mathbf K_N.
\]
因此
\[
\boxed{
\bar u'\gamma^0u
=
2m_N\,\xi'^\dagger
\left[
1+\frac{\mathbf K_N^2}{2m_N^2}
+\frac{i\boldsymbol\sigma_N\cdot
(\mathbf q_N\times\mathbf K_N)}{4m_N^2}
\right]\xi+\cdots .
}
\]
这一步已经显示出一个重要事实：即使从纯矢量 Dirac 项开始，时间分量也不只有一个常数电荷项；它还包含核子平均动量与自旋的耦合。

### 30.3 时间分量的 Pauli 项

按本文统一的约定
\[
\Gamma_N^\mu=
F_1(t_N)\gamma^\mu+
\frac{iF_2(t_N)}{2m_N}
\sigma^{\mu\nu}q_{N,\nu},
\]
有
\[
J_P^0=
\frac{iF_2}{2m_N}
\bar u'\sigma^{0\nu}q_{N,\nu}u.
\]
因为 \(\sigma^{00}=0\)，只剩空间转移。用
\[
\sigma^{0i}=i\gamma^0\gamma^i
\]
以及 \(q_{N,i}=-q_N^i\)，可得
\[
\bar u'i\sigma^{0\nu}q_{N,\nu}u
=
\bar u'\boldsymbol\alpha\cdot\mathbf q_Nu.
\]
代入非相对论旋量：
\[
\begin{aligned}
\bar u'\boldsymbol\alpha\cdot\mathbf q_Nu
={}&
\xi'^\dagger\left[
(\boldsymbol\sigma\cdot\mathbf q_N)
(\boldsymbol\sigma\cdot\mathbf p_N)
-
(\boldsymbol\sigma\cdot\mathbf p_N')
(\boldsymbol\sigma\cdot\mathbf q_N)
\right]\xi+\cdots\\
={}&
\xi'^\dagger\left[
-Q_N^2
+2i\boldsymbol\sigma_N\cdot
(\mathbf q_N\times\mathbf K_N)
\right]\xi+\cdots .
\end{aligned}
\]
于是
\[
\boxed{
J_P^0=
-\frac{F_2Q_N^2}{2m_N}
+i\frac{F_2}{m_N}
\boldsymbol\sigma_N\cdot
(\mathbf q_N\times\mathbf K_N)+\cdots .
}
\]
将 Dirac 和 Pauli 两部分相加，得到
\[
\boxed{
\begin{aligned}
J_N^0={}&
2m_NF_1
+\frac{F_1}{m_N}\mathbf K_N^2
-\frac{F_2}{2m_N}Q_N^2\\
&+
i\frac{F_1+2F_2}{2m_N}
\boldsymbol\sigma_N\cdot
(\mathbf q_N\times\mathbf K_N)
+\cdots .
\end{aligned}
}
\]
这里的 \(F_i\) 均指 \(F_i^{V,N}(t_N)\)。省略项包含更高阶动量修正及相应 form factor 的更高阶展开。

**为什么出现 \(F_1+2F_2\)？**

Dirac 部分的自旋—轨道系数是 \(F_1/(2m_N)\)，Pauli 部分的系数是 \(F_2/m_N\)。两者相加：
\[
\frac{F_1}{2m_N}+\frac{F_2}{m_N}
=\frac{F_1+2F_2}{2m_N}.
\]
所以这个组合不是人为定义出来的，而是 Dirac 和 Pauli 两种相对论结构在时间分量中共同产生的。

### 30.4 空间分量：对流电流和磁化电流

空间 Dirac 项为
\[
J_D^i=F_1\bar u'\gamma^iu.
\]
利用 Pauli 矩阵恒等式可得
\[
\boxed{
\bar u'\boldsymbol\gamma u
=
2\mathbf K_N+i\boldsymbol\sigma_N\times\mathbf q_N
+\cdots .
}
\]
空间 Pauli 项在领先非相对论阶给出
\[
\frac{iF_2}{2m_N}
\bar u'\sigma^{i\nu}q_{N,\nu}u
=
iF_2(\boldsymbol\sigma_N\times\mathbf q_N)^i+\cdots .
\]
因此
\[
\boxed{
\mathbf J_N=
2F_1\mathbf K_N+
i(F_1+F_2)\boldsymbol\sigma_N\times\mathbf q_N
+\cdots .
}
\]
空间流出现的不是 \(F_1+2F_2\)，而是
\[
\boxed{G_M=F_1+F_2.}
\]
这正是 Sachs 磁 form factor。时间分量的自旋—轨道修正和空间分量的磁化流必须分别保留，不能把二者统一乘同一个 \(F_1+2F_2\)。

### 30.5 用 Sachs form factor 做独立检查

在 Breit 系中 \(\mathbf K_N=0\)、\(q_N^0=0\)。于是
\[
J_N^0=2m_NF_1-\frac{F_2Q_N^2}{2m_N}
=2m_N\left(F_1-\frac{Q_N^2}{4m_N^2}F_2\right),
\]
\[
\mathbf J_N=i(F_1+F_2)\boldsymbol\sigma_N\times\mathbf q_N.
\]
定义
\[
G_E=F_1-\frac{Q_N^2}{4m_N^2}F_2,\qquad
G_M=F_1+F_2,
\]
则
\[
J_N^0=2m_NG_E,\qquad
\mathbf J_N=iG_M\boldsymbol\sigma_N\times\mathbf q_N.
\]
这与标准电、磁 Sachs 分解一致，是检查 Pauli 项符号和动量方向的一个非常有效的单核子测试。

### 30.6 归一化成非相对论核子流

若将协变核子矩阵元整体除以 \(2m_N\)，得到便于嵌入非相对论核算符的形式：
\[
\boxed{
\begin{aligned}
\frac{J_N^0}{2m_N}
={}&F_1
+\frac{F_1\mathbf K_N^2}{2m_N^2}
-\frac{F_2Q_N^2}{4m_N^2}\\
&+
i\frac{F_1+2F_2}{4m_N^2}
\boldsymbol\sigma_N\cdot
(\mathbf q_N\times\mathbf K_N)+\cdots ,
\\[4pt]
\frac{\mathbf J_N}{2m_N}
={}&
\frac{F_1}{m_N}\mathbf K_N
+i\frac{F_1+F_2}{2m_N}
\boldsymbol\sigma_N\times\mathbf q_N+\cdots .
\end{aligned}
}
\]
四类结构现在可以清楚区分：
1. \(F_1\)：领先阶矢量电荷；
2. \(F_1\mathbf K_N^2\) 和 \(F_2Q_N^2\)：时间分量的自旋无关次领先修正；
3. \(F_1+2F_2\)：时间分量自旋—轨道电荷；
4. \(F_1\) 与 \(F_1+F_2\)：空间对流和磁化电流。

对当前 \(u+d+s\) 零动量 benchmark，
\[
F_1=3,\qquad F_2=-0.552,
\]
因此
\[
F_1+2F_2=1.896,\qquad F_1+F_2=2.448.
\]
这两个组合分别进入时间自旋—轨道项和空间磁化项。

### 30.7 Gordon identity 与流守恒检查

在相同质量、外部核子均在壳时，Gordon identity 为
\[
\bar u(p')\gamma^\mu u(p)
=
\bar u(p')
\left[
\frac{(p'+p)^\mu}{2m_N}
+\frac{i\sigma^{\mu\nu}q_{N,\nu}}{2m_N}
\right]u(p).
\]
同时
\[
q_{N\mu}\sigma^{\mu\nu}q_{N,\nu}=0
\]
来自 \(\sigma^{\mu\nu}\) 的反对称性，而
\[
\bar u(p')\slashed q_Nu(p)
=\bar u(p')(\slashed p'-\slashed p)u(p)
=(m_N-m_N)\bar u(p')u(p)=0.
\]
因此
\[
\boxed{q_{N\mu}J_N^\mu=0.}
\]
这应当作为自由核子数值实现的单元测试。若代码在相同质量、在壳旋量和统一 \(q_N\) 约定下不能满足该关系，通常意味着 Pauli 项符号、指标升降或 gamma 矩阵约定有误。

束缚核子不是严格自由在壳粒子，不能把上述自由核子 Ward 恒等式机械地当作每个单粒子近似的精确恒等式。核整体的连续性方程应与所用核 Hamiltonian 和核流近似保持一致；若采用与核 Hamiltonian 不一致的一体流截断，剩余差异需要作为截断误差检查。

## 31. 从单核子流到核内算符：为什么出现 \(M\)、\(\Phi''\)、\(\Delta\) 和 \(\Sigma'\)

### 31.1 把平均核子动量变成核内动量算符

在一体冲量近似中，核子流嵌入原子核时，对第 \(i\) 个核子的平面波因子为
\[
e^{i\mathbf q_A\cdot\mathbf r_i}.
\]
单核子矩阵元中的平均动量 \(\mathbf K_i\) 在坐标空间不能简单替换成一个数；它应作为作用在束缚核波函数上的动量算符。对任意初末单粒子态，
\[
\left\langle p_i'\left|
\frac12\left\{e^{i\mathbf q_A\cdot\mathbf r_i},\mathbf p_i\right\}
\right|p_i\right\rangle
=
\frac{\mathbf p_i'+\mathbf p_i}{2}
\langle p_i'|e^{i\mathbf q_A\cdot\mathbf r_i}|p_i\rangle.
\]
因此用反对易子可以同时保证：
- 平均初末动量的正确矩阵元；
- 对有限动量转移算符的厄米性关系；
- 导数作用在核波函数上的正确位置。

在 \(F_i\) 暂时取同位素内常数时，归一化的一体核电荷密度可以写成
\[
\begin{aligned}
\widehat\rho_A(\mathbf q_A)
=\sum_{i=1}^{A}e^{i\mathbf q_A\cdot\mathbf r_i}
\bigg[
&F_1^{N_i}
+\frac{F_1^{N_i}}{2m_{N_i}^2}\mathbf K_i^2
-\frac{F_2^{N_i}}{4m_{N_i}^2}Q_A^2\\
&+
i\frac{F_1^{N_i}+2F_2^{N_i}}{4m_{N_i}^2}
\boldsymbol\sigma_i\cdot(\mathbf q_A\times\mathbf K_i)
\bigg]+\cdots ,
\end{aligned}
\]
其中最后一项的 \(\mathbf K_i\) 应理解为上面的对称化算符，而不是经典数值。若 \(F_i^{p}\ne F_i^{n}\)，必须分别对质子和中子求和。

### 31.2 四个最直接的一体核算符

把不同项单独写出，可以看到它们在核结构上的差别。

**矢量电荷密度：**
\[
\widehat\rho_M(\mathbf q_A)
=
\sum_i F_1^{N_i}
e^{i\mathbf q_A\cdot\mathbf r_i}.
\]
这是 AFH 的 \(M\) 响应来源。

**自旋—轨道电荷密度：**
\[
\widehat\rho_{\rm SO}(\mathbf q_A)
=
\sum_i
i\frac{F_1^{N_i}+2F_2^{N_i}}{4m_{N_i}^2}
\boldsymbol\sigma_i\cdot
\left[
\mathbf q_A\times
\frac12\left\{
e^{i\mathbf q_A\cdot\mathbf r_i},\mathbf p_i
\right\}
\right].
\]
它包含核子自旋、核内轨道动量和外部动量转移，是 AFH \(\Phi''\) 响应的核心候选来源。

**对流电流：**
\[
\widehat{\mathbf j}_{\rm conv}(\mathbf q_A)
=
\sum_i\frac{F_1^{N_i}}{m_{N_i}}
\frac12\left\{
e^{i\mathbf q_A\cdot\mathbf r_i},\mathbf p_i
\right\}.
\]
它含有核子内部轨道运动；多极展开后，其横向磁投影与 AFH \(\Delta\) 响应相关。

**磁化电流：**
\[
\widehat{\mathbf j}_{\rm mag}(\mathbf q_A)
=
\sum_i i\frac{F_1^{N_i}+F_2^{N_i}}{2m_{N_i}}
e^{i\mathbf q_A\cdot\mathbf r_i}
\boldsymbol\sigma_i\times\mathbf q_A.
\]
由于
\[
\mathbf q_A\cdot(\boldsymbol\sigma_i\times\mathbf q_A)=0,
\]
该领先磁化项是横向电流，直接提示需要检查横向自旋响应。其他纵向自旋结构是否出现，必须由完整相对论流及其高阶展开决定，不能只凭这个领先磁化项推断。

### 31.3 为什么自旋—轨道项对应 \(\Phi''\)，而不是普通 SD

AFH 的矢量电荷多极定义为
\[
M_{JM}(\mathbf q_A\mathbf r)
=j_J(Q_Ar)Y_{JM}(\widehat{\mathbf r}).
\]
平面波展开为
\[
e^{i\mathbf q_A\cdot\mathbf r}
=
4\pi\sum_{JM}i^J
j_J(Q_Ar)
Y_{JM}^{*}(\widehat{\mathbf q}_A)
Y_{JM}(\widehat{\mathbf r}).
\]
因此核子密度算符在核态上的矩阵元自然被组织成 \(M_{JM}\) 多极。

AFH 的自旋—轨道多极可以写为
\[
\boxed{
\Phi''_{JM;\tau}
=
i\sum_{i=1}^{A}
\left(\frac{1}{Q_A}\boldsymbol\nabla_i
M_{JM}(Q_A r_i)\right)
\cdot
\left(
\boldsymbol\sigma_i\times
\frac{1}{Q_A}\boldsymbol\nabla_i
\right)t^\tau(i).
}
\]
其中右侧第二个梯度作用在第 \(i\) 个单粒子核波函数上，\(t^\tau(i)\) 为 AFH 的 isospin 插入。它正是“外部动量转移 × 核内平均动量，再与核子自旋点乘”的多极化表达。长波极限下，AFH 给出
\[
\sqrt{4\pi}\,\Phi''_{00}(0)
=
\frac13\sum_i
\boldsymbol\sigma_i\cdot\mathbf l_i\,t^\tau(i),
\]
其中 \(\mathbf l_i=\mathbf r_i\times\mathbf p_i\)，\(t^\tau\) 是同位旋算符。这个极限直接显示它测量的是核子自旋与轨道角动量的相关，而不是单纯的未成对核子总自旋。

因此 \(\Phi''\) 可以产生旋转标量响应，甚至在总核自旋为零的核中也不必严格为零。它与常规 SD 的 \(\Sigma'\)、\(\Sigma''\) 物理含义不同。AFH 对六类基本核算符及其多极结构的系统定义见 Anand–Fitzpatrick–Haxton, arXiv:1308.6288。

### 31.4 \(M\)-\(\Phi''\) 干涉为什么必须保留

如果核电荷密度写成
\[
\widehat\rho_A=
c_M\widehat M+c_\Phi\widehat\Phi''+\cdots ,
\]
则核矩阵元为
\[
\mathcal A_A=c_M\langle A'|\widehat M|A\rangle
+c_\Phi\langle A'|\widehat\Phi''|A\rangle+\cdots .
\]
平方后必然出现
\[
\begin{aligned}
|\mathcal A_A|^2={}&
|c_M|^2|\langle M\rangle|^2
+|c_\Phi|^2|\langle\Phi''\rangle|^2\\
&+2\operatorname{Re}
\left[
c_Mc_\Phi^*
\langle M\rangle\langle\Phi''\rangle^*
\right]+\cdots .
\end{aligned}
\]
在 AFH 语言中，这三项分别对应
\[
R_MW_M,\qquad
R_{\Phi''}W_{\Phi''},\qquad
R_{M\Phi''}W_{M\Phi''}.
\]
因此只计算 \(W_{\Phi''}\) 的对角项而遗漏 \(W_{M\Phi''}\)，并不是完整的一体核流结果。

对于 Xe-131 的 \(W_M\) 深极小值，如果 \(\langle M\rangle\) 接近零，干涉项也可能因相对振幅变化而影响局部谱形。但这不意味着它必然填平极小值：实际大小和符号由 \(\langle\Phi''\rangle\)、两项 Wilson 系数以及相位共同决定。

### 31.5 AFH v6.0 八种响应与当前核流的关系

仓库 v6.0 源程序的 ResponseNuclear 接口按如下顺序输出响应：
| 编号 | AFH 响应 | 核算符解释 |
|---:|---|---|
| 1 | \(M\) | 矢量电荷 |
| 2 | \(\Sigma''\) | 纵向自旋 |
| 3 | \(\Sigma'\) | 横向自旋 |
| 4 | \(\Phi''\) | 自旋—轨道/纵向矢量相关响应 |
| 5 | \(\widetilde\Phi'\) | 横向电、自旋—速度张量响应 |
| 6 | \(\Delta\) | 轨道角动量/对流电流相关响应 |
| 7 | \(M\Phi''\) | 质量与自旋—轨道干涉 |
| 8 | \(\Sigma'\Delta\) | 横向自旋与轨道干涉 |

对于当前 VV 一体流，第一轮的物理排序是：
1. \(M\)：领先阶，必须保留；
2. \(\Phi''\) 与 \(M\Phi''\)：时间分量自旋—轨道项的第一优先级；
3. \(\Delta\)、\(\Sigma'\)：由完整空间流收缩决定；
4. \(\Sigma''\)、\(\widetilde\Phi'\)：由完整多极投影决定，不能仅因为程序有接口就自动加入；
5. 两核子流：在一体流和误差预算明确后，再按手征 EFT 评估。

这个顺序是模型匹配优先级，不是对所有响应大小的预先断言。

## 32. 完整三体张量与 AFH 核响应如何收缩

### 32.1 暗物质张量

定义暗物质侧自旋平均张量
\[
L^{\mu\nu}(p,p',k)
=
\frac12\sum_{s,s'}
\mathcal T_3^\mu(s',s)
\mathcal T_3^{\nu *}(s',s).
\]
它可以直接写成 Dirac trace：
\[
\boxed{
L^{\mu\nu}
=
\frac12\operatorname{Tr}
\left[
(\slashed p'+m_\chi)
\Gamma_3^\mu
(\slashed p+m_\chi)
\overline\Gamma_3^\nu
\right],
}
\]
其中
\[
\overline\Gamma_3^\nu
=\gamma^0(\Gamma_3^\nu)^\dagger\gamma^0.
\]
由于 \(\Gamma_3^\mu\) 包含两张辐射图，\(L^{\mu\nu}\) 自动包含
\[
|{\cal M}_a|^2,\qquad |{\cal M}_b|^2,\qquad
2\operatorname{Re}({\cal M}_a{\cal M}_b^*).
\]
程序可以将三项分别输出作诊断，但物理总张量必须由两图先相加后平方得到。

### 32.2 核张量

对初始核自旋 \(J_A\) 平均、对末态核自旋求和，定义
\[
W_A^{\mu\nu}(q_A)
=
\frac{1}{2J_A+1}
\sum_{M_A,M_A'}
J_A^\mu(M_A',M_A)
J_A^{\nu *}(M_A',M_A).
\]
忽略已由核流守恒消去的传播子纵向部分后，
\[
\boxed{
\overline{|\mathcal M_3|^2}
=
\frac{1}{|t_A-m_{A'}^2|^2}
L_{\mu\nu}W_A^{\mu\nu}
}
\]
其中 \(g_1,g_2,g_q\) 等耦合可以包含在 \(L\) 或 \(W_A\) 中，但必须保持统一记账。若媒介子传播子不在重媒介子极限，分母应保留其完整 \(t_A\) 依赖。

AFH 核响应不是任意替代 \(W_A^{00}\) 的一条曲线，而是将核张量按旋转、宇称和 CP 允许的多极算符分解后的独立结构函数。三体过程的暗物质张量依赖 \(k_s\)，所以 AFH 提供核结构矩阵元，但不能替代三体粒子物理张量和相空间积分。

### 32.3 只保留 \(M\) 时的简化条件

若核子矢量电荷项主导，且核侧其他分量的贡献低于目标精度，则
\[
L_{\mu\nu}W_A^{\mu\nu}
\simeq L_{00}W_A^{00}
\simeq R_M W_M.
\]
这就是当前以 \(W_M^{00}\) 为领先阶基准的依据。

但当核子时间流包含自旋—轨道项时，
\[
J_A^0=J_{A,M}^0+J_{A,\Phi''}^0+\cdots,
\]
即使暗物质空间流很小，仍然存在
\[
L_{00}\left[
W_M+W_{\Phi''}+W_{M\Phi''}
\right].
\]
因此
\[
\frac{\sum_i L^{ii}}{L^{00}}\ll1
\]
不能推出 \(W_{\Phi''}\) 可以忽略。这个逻辑区别是本项目必须保留 \(M\Phi''\) 审计的核心原因。

### 32.4 AFH factor-four 在张量收缩中的唯一位置

当前 AFH v6.0 package 的等标量 raw 响应零动量归一化为
\[
R_{M,\mathrm{raw}}(0)=\frac{A^2}{4},
\]
而物理等质子、等中子耦合响应应为
\[
R_M^{\mathrm{phys}}(0)=A^2.
\]
所以
\[
R_M^{\mathrm{phys}}(Q_A)=4R_{M,\mathrm{raw}}(Q_A)
\]
仅在 raw-to-physical 映射时执行一次。若已经使用物理归一化 \(W_M^{\mathrm{phys}}\)，截面前因子不能再乘 4；若点核振幅已经带有 \(Ag_{VN}\)，只乘 \(R_M(Q_A)/R_M(0)\)，不能再乘完整 \(A^2\)。

这一因子与夸克—核子匹配 \(g_{VN}=3g_q\) 无关。前者是 AFH package 响应的归一化约定，后者是 UV 流的核子电荷匹配。

## 33. 从不变振幅到 \(d\sigma/dE_R\) 和天然氙事件率

### 33.1 三体微分截面的不变表达式

初态为暗物质和静止核，三体末态为暗物质、反冲核和标量。定义
\[
d\Phi_3=(2\pi)^4\delta^{(4)}
(p+P-p'-P'-k)
\prod_{f=p',P',k}\frac{d^3p_f}{(2\pi)^3\,2E_f}.
\]
则不变截面为
\[
\boxed{
d\sigma_3=
\frac{\overline{|\mathcal M_3|^2}}
{4\sqrt{(p\cdot P)^2-m_\chi^2m_A^2}}
\,d\Phi_3.
}
\]
在靶核静止系，
\[
4\sqrt{(p\cdot P)^2-m_\chi^2m_A^2}
=4m_A|\mathbf p|
=4m_AE_\chi v.
\]
非相对论暗物质下 \(E_\chi\simeq m_\chi\)，所以通量因子约为 \(4m_Am_\chi v\)。

若要得到 \(d\sigma/dE_R\)，需要在 \(d\Phi_3\) 中用
\[
E_R=E_A'-m_A
\]
插入 \(\delta(E_R-(E_A'-m_A))\)，对末态核方向、末态暗物质和标量动量积分。若矩阵元依赖标量能量或角度，不能只保留 \(I(D)\)，而要对完整 \(\mathcal M_3\) 积分。

### 33.2 \(L^{00}\) 近似与完整结果的对照

建议每个数值点至少同时输出：
\[
\begin{aligned}
\mathcal R_{00}&=L^{00}W_A^{00},\\
\mathcal R_{0i}&=2\operatorname{Re}(L^{0i}W_A^{0i}),\\
\mathcal R_{ij}&=L^{ij}W_A^{ij}.
\end{aligned}
\]
这里 \(\mathcal R_{00}\) 还应进一步分解成 \(M\)、\(\Phi''\)、\(M\Phi''\) 等核响应项。只报告 \(\sum_iL^{ii}/L^{00}\) 并不足以验收完整核流，因为它没有包含核张量本身的结构，也没有给出 \(L^{0i}\) 干涉。

推荐同时给出两种截面：
\[
\left.\frac{d\sigma_3}{dE_R}\right|_{M\text{-only}},
\qquad
\left.\frac{d\sigma_3}{dE_R}\right|_{\rm full\ one-body}.
\]
并分别报告绝对差
\[
\Delta_{\rm abs}
=\frac{d\sigma_{\rm full}}{dE_R}
-\frac{d\sigma_{M}}{dE_R}
\]
和相对差
\[
\Delta_{\rm rel}
=\frac{d\sigma_{\rm full}/dE_R}
{d\sigma_M/dE_R}-1.
\]
当 \(W_M\) 位于深极小值时，相对差可能非常大，但绝对事件率仍可能很小；两者必须一起报告。

### 33.3 天然氙同位素求和

对同位素 \(A\)，定义天然丰度数分数 \(x_A\)，并满足
\[
\sum_A x_A=1.
\]
若按探测器总质量归一化，则同位素质量分数为
\[
\xi_A=\frac{x_A m_A}{\sum_Bx_Bm_B}.
\]
每单位探测器质量的微分事件率为
\[
\boxed{
\frac{dR}{dE_R}
=
\frac{\rho_\chi}{m_\chi}
\sum_A\frac{\xi_A}{m_A}
\int d^3v\,f_{\rm lab}(\mathbf v)\,
v\,\frac{d\sigma_A(v)}{dE_R}.
}
\]
若直接使用数丰度，则可等价写成
\[
\frac{dR}{dE_R}
=
\frac{\rho_\chi}{m_\chi}
\frac{1}{\sum_Bx_Bm_B}
\sum_Ax_A
\int d^3v\,f_{\rm lab}(\mathbf v)\,
v\,\frac{d\sigma_A(v)}{dE_R}.
\]
两种写法等价，不能一边使用质量分数 \(\xi_A\)，另一边又重复乘 \(m_A\)。

天然氙求和必须在同位素级截面计算完成后进行，因为不同同位素的 \(J_A\)、OBDME、AFH 响应曲线和 \(Q_A(E_R)\) 均不同。一个 Xe-131 的 \(W_M\) 深极小值不能直接等同于天然氙总谱中的同样深度的极小值。

### 33.4 探测器折叠是独立的一层

若实验测量变量为 \(E_{\rm obs}\)，则需要再对核反冲率做探测器响应卷积：
\[
\frac{dN}{dE_{\rm obs}}
=
\mathcal E
\int dE_R\,
\epsilon(E_R)\,
G(E_{\rm obs}|E_R)\,
\frac{dR}{dE_R},
\]
其中 \(\mathcal E\) 为曝光量，\(\epsilon\) 为效率，\(G\) 为能量响应核。该层不属于 AFH 核响应，也不属于三体相空间。核响应、halo fold、同位素求和和探测器卷积必须分别保存输入和输出。

## 34. 从理论公式到程序实现的最小验收闭环

为避免不同层级的数值误差互相掩盖，建议按下面顺序做单元测试。

| 层级 | 必须验证的关系 | 通过条件 |
|---|---|---|
| 四动量 | \(q_A=p-p'-k\) | 每个相空间点四动量守恒残差满足设定精度 |
| 核反冲 | \(Q_A^2=E_R(E_R+2m_A)\)、\(t_A=-2m_AE_R\) | 精确关系与非相对论近似差异被分别记录 |
| 三体顶点 | 两张图的 \(r_1,r_2,D_1,D_2\) | 与独立费米子线动量流检查一致 |
| 极点宽度 | \(\Gamma_{\chi_2}\) | 部分宽度、总宽度和极点位置可追溯 |
| Ward 收缩 | 零宽度 \(q_A\cdot\mathcal T_3\) 公式 | 与解析式逐点一致；有限宽度方案另行测试 |
| 核子流 | \(F_1,F_2\) Dirac–Pauli 顶点 | 自由核子直接旋量计算与 NR 展开在共同适用区间一致 |
| 核子守恒流 | \(q_N\cdot J_N=0\) | 同质量、在壳自由核子测试通过 |
| flavor 匹配 | \(F_1^{uds}(0)=3\)、\(F_2^{uds}(0)=-0.552\) | 零动量锚点恢复 |
| AFH \(M\) | raw \(A^2/4\) 到 physical \(A^2\) | factor 4 只出现一次 |
| AFH \(\Phi''\) | 多极和 OBDME | 选择定则、长波极限及独立矩阵元检查通过 |
| 干涉 | \(M\Phi''\) | 实部、符号、同位旋通道均可追溯 |
| 三体相空间 | \(d\Phi_3\) 与 \(I(D)\) | 常振幅极限恢复解析 \(I(D)/(4\pi^2)\) |
| 数值积分 | \(\epsilon,\Omega_*\)、核反冲和 halo 速度 | 各积分层独立收敛 |
| 天然氙 | 同位素丰度与质量归一化 | 数丰度和质量分数两种写法一致 |

### 34.1 自由核子直接计算与 NR 展开的对照

对给定 \(p_N,p_N'\)，先直接用 Dirac 矩阵计算
\[
J_{\rm exact}^\mu=
\bar u(p_N')
\left[
F_1\gamma^\mu+
\frac{iF_2}{2m_N}\sigma^{\mu\nu}q_{N,\nu}
\right]u(p_N).
\]
再用 §30 的 NR 公式计算 \(J_{\rm NR}^\mu\)。定义
\[
\delta_{\rm NR}
=
\frac{\sqrt{\sum_\mu|J_{\rm exact}^\mu-J_{\rm NR}^\mu|^2}}
{\sqrt{\sum_\mu|J_{\rm exact}^\mu|^2}}.
\]
随着 \(|\mathbf p|/m_N\)、\(Q_N/m_N\) 下降，\(\delta_{\rm NR}\) 应按被省略阶数下降。若不下降，优先检查 Pauli 项的指标和符号，而不是调整 AFH 响应。

### 34.2 常振幅三体相空间对照

构造一个人为与 \(\epsilon,\Omega_*\) 无关的常数振幅，分别计算：
1. 直接三体不变相空间积分；
2. 先做外层运动学，再使用解析 \(I(D)/(4\pi^2)\)。

两者在相同的重粒子近似和相同 Jacobian 下应一致。然后逐步恢复 \(D_1,D_2\) 的能量和角度依赖，检查常振幅近似何时开始失效。这样可以把相空间算法错误与真实 Breit–Wigner 动力学区别开。

### 34.3 AFH 长波极限和多极检查

对每个同位素分别验证：
\[
R_M^{\rm phys}(Q_A\to0)=A^2.
\]
对 \(\Phi''\)，检查 \(J=0\) 长波矩阵元与
\[
\sqrt{4\pi}\Phi''_{00}(0)
=\frac13\sum_i\boldsymbol\sigma_i\cdot\mathbf l_i
\]
的对应关系；同时检查 \(J=2\) 的张量长波分量
\[
\sqrt{4\pi}\Phi''_{2M}(0)
=-\frac{1}{\sqrt5}\sum_i
\left[
\mathbf r_i\otimes
\left(\boldsymbol\sigma_i\times\frac{1}{i}\boldsymbol\nabla_i\right)_1
\right]_{2M}t^\tau(i).
\]
Xe-131 的 \(M\) rank-2 多极仍然属于 \(M\) 响应，不能因为 \(J=2\) 就把它记成 \(\Phi''\) 或 SD 响应。

### 34.4 必须保持的物理状态边界

本次新增的解析推导不等于完成了下列数值任务：
- 没有得到完整有限 \(t_N\) 的 \(F_1^{uds,N}(t_N)\)、\(F_2^{uds,N}(t_N)\) 数据及协方差；
- 没有得到三体完整张量在全部相空间上的独立收敛结果；
- 没有完成 Xe-131 的 AFH \(W_{\Phi''}\) 与 \(W_{M\Phi''}\) 数值投影；
- 没有得到完整一体流修正后的天然氙 halo-folded 反冲谱；
- 没有计算 VV 两核子流对当前高动量区间的数值修正。

因此，现阶段可以说：三体振幅、相空间、单核子流和 AFH 核响应之间的解析联系已经明确；但不能说完整 VV 三体核响应或最终反冲谱已经通过数值验收。



### 30.8 为什么不能把这一项直接标成弹性散射的 \(\mathcal O_3\)

将时间分量自旋—轨道项写成核子自旋 \(\mathbf S_N=\boldsymbol\sigma_N/2\) 和平均核子速度 \(\mathbf v_N=\mathbf K_N/m_N\)：
\[
\frac{J_{N,\mathrm{SO}}^0}{2m_N}
=
i\frac{F_1+2F_2}{2m_N^2}
\mathbf S_N\cdot(\mathbf q_N\times\mathbf K_N)
=
i\frac{F_1+2F_2}{2m_N}
\mathbf S_N\cdot(\mathbf q_N\times\mathbf v_N).
\]
这与弹性 NREFT 中常见的自旋—速度结构有相似的张量形式，但不能仅凭这一项就把系数直接认作标准弹性 \(\mathcal O_3\)。原因是标准弹性定义使用相对速度
\[
\mathbf v^\perp=
\frac{\mathbf p+\mathbf p'}{2m_\chi}
-\frac{\mathbf k+\mathbf k'}{2m_N},
\]
并依赖弹性二体能量守恒得到
\[
\mathbf q\cdot\mathbf v^\perp=0.
\]
在当前三体过程中，暗物质还发射了标量，动量守恒变成
\[
\mathbf q_A=\mathbf p-\mathbf p'-\mathbf k_s.
\]
若仍用弹性定义的平均速度，则在非相对论近似下
\[
\mathbf q_A\cdot\mathbf v^\perp
=
E_s-\frac{\mathbf k_s\cdot(\mathbf p+\mathbf p')}{2m_\chi},
\]
一般不为零。这里 \(E_s\) 是标量总能量，包含其静质量。

因此，弹性散射中用于消去时间导数、改写算符或建立标准 \(\mathbf v^\perp\) 基底的步骤，在三体过程中必须重新推导。正确顺序是：
1. 保留完整 \(\mathcal T_3^\mu(p,p',k_s)\)；
2. 与完整 Dirac–Pauli 核子流 \(J_N^\nu\) 收缩；
3. 在明确的三体能量守恒关系下做非相对论展开；
4. 再把所得核子算符投影到 AFH 多极响应。

这也是不能直接调用标准弹性 AFH FFfinal 作为三体截面公式的运动学原因。


### 31.6 OBDME 如何把单粒子算符变成核响应

AFH 的输入不是一个经验 Helm 半径，而是核态的一体密度矩阵。把核算符写成单粒子算符之和后，其约化矩阵元可组织为
\[
\langle J_A\Vert\widehat{\mathcal O}_{X,J}^{\,\tau}(Q_A)
\Vert J_A\rangle
=
\sum_{ab}
\rho_{ab}^{(\tau)}
\langle a\Vert
\widehat o_{X,J}(Q_A)
\Vert b\rangle.
\]
这里 \(a,b\) 表示单粒子轨道，\(\rho_{ab}^{(\tau)}\) 是相应同位旋通道的一体密度矩阵（OBDME），而单粒子约化矩阵元包含球贝塞尔函数、球谐函数、轨道角动量和自旋耦合。

核响应是这些约化矩阵元的双线性组合。其标准结构为
\[
W_{XY}^{\tau\tau'}(Q_A)
=
\frac{4\pi}{2J_A+1}
\sum_J
\langle J_A\Vert\widehat{\mathcal O}_{X,J}^{\,\tau}
\Vert J_A\rangle
\langle J_A\Vert\widehat{\mathcal O}_{Y,J}^{\,\tau'}
\Vert J_A\rangle^*,
\]
其中 \(X,Y\) 取 AFH 的允许核算符，具体允许的 \(J\) 奇偶性由算符的宇称决定。实际使用时还必须遵循 AFH v6.0 的 isospin 和 package 输出归一化约定；当前 raw \(A^2/4\) 到 physical \(A^2\) 的 factor-four 映射另按 §32.4 处理。不能在外部代码中既使用已经归一化的 AFH 输出，又手动重复乘相同的多极归一化因子。

对 \(X=Y=M\)，得到 \(W_M\)；对 \(X=Y=\Phi''\)，得到 \(W_{\Phi''}\)；对 \(X=M,Y=\Phi''\)，得到 \(W_{M\Phi''}\)。最后一个是两个不同核算符的交叉双线性项，不是 \(W_M\) 和 \(W_{\Phi''}\) 的几何平均，也不能由两个对角响应单独恢复其符号。

这解释了为什么核子流匹配必须先于 AFH 响应计算：只有先确定 \(\widehat o_{X,J}\) 的 Wilson 系数和同位旋权重，才能知道需要调用哪些 OBDME 投影以及如何构造响应之间的干涉。


## 35. 推导所依据的文献和代码来源

本档案中的推导分为三类：本模型从 UV 拉格朗日量直接得到的解析结果；采用标准 QFT、相空间和非相对论展开得到的通用关系；由 AFH v6.0 和核子 form factor 文献提供的核结构输入。三者不能混作同一种证据。

1. **本模型的三体振幅与运动学：** 以本项目的相互作用拉格朗日量和论文源文件为准，尤其是仓库的 paper-source/main.tex。两张 \(\chi_2\) 辐射图、传播子分母、三体相空间和 \(I(D)\) 的重粒子近似均应与该源文件及后续完整数值实现交叉检查。
2. **AFH 核响应：** N. Anand, A. L. Fitzpatrick, W. C. Haxton, *Model-independent WIMP Scattering Responses and Event Rates: A Mathematica Package for Experimental Analysis*, arXiv:1308.6288。该文给出 \(M,\Sigma',\Sigma'',\Delta,\widetilde\Phi',\Phi''\) 多极算符、\(M\leftrightarrow\Phi''\) 和 \(\Delta\leftrightarrow\Sigma'\) 干涉，以及 OBDME 到核响应的构造。链接：https://arxiv.org/abs/1308.6288。
3. **夸克—核子矢量 form factors：** F. Bishara, J. Brod, B. Grinstein, J. Zupan, *From quarks to nucleons in dark matter direct detection*, arXiv:1707.06998，特别是 Eq. (22)、Appendix A.1 Eqs. (78)–(85)。它给出 flavor-separated \(F_1,F_2\) 的零动量值和 \(F_1\) 斜率。链接：https://arxiv.org/abs/1707.06998。
4. **矢量流与手征 EFT：** M. Hoferichter, P. Klos, A. Schwenk, *Chiral power counting of one- and two-body currents in direct detection of dark matter*, arXiv:1503.04811。本文用于检查矢量流分解、同位旋关系、单体与两体流的手征计数，以及弹性二体 NREFT 的适用条件。链接：https://arxiv.org/abs/1503.04811。
5. **AFH v6.0 实现：** 仓库 v6/dmformfactor-V6.m。ResponseNuclear 的编号 1–8、各算符的单粒子矩阵元、OBDME 折叠、等标量 raw 响应归一化以及 \(M\Phi''\) 交叉响应，均以当前仓库版本为准。
6. **本项目三体流诊断：** PR #58 是静态单核子 Dirac–Pauli 收缩诊断；它不是 AFH 多体 \(\Phi''\) 或 \(M\Phi''\) 数值结果，也不是完整三体截面验收。



---

# 第四部分：完整 AFH 核响应数据库与三体收缩引擎

## 36. AFH 核响应与单核子 Dirac–Pauli 形状因子：两个层次、一个物理振幅

前文已经分别推导了单核子 Dirac–Pauli 流和 AFH 多极响应。本节进一步回答一个实际研究问题：**既然项目已经采用 AFH v6.0，是否还需要单核子 \(F_1,F_2\)？能否先把 AFH 的全部响应算出来，再决定它们在三体截面中的贡献？**

答案分为两部分：

1. **需要 \(F_1,F_2\)。** AFH 核响应和单核子 Dirac–Pauli form factors 描述不同层次的物理结构，不能互相替代。
2. **可以先计算全部 AFH 响应。** 建立完整 AFH 核响应数据库不要求先完成三体模型匹配；但把这些响应用于物理截面时，仍必须完成核子流投影、动力学权重和允许的干涉收缩。

因此，本项目采用的原则是：

\[
\boxed{\text{AFH 负责核结构；}\quad F_1,F_2
\text{ 负责单核子流；}\quad
\mathcal T_3^\mu\text{ 负责三体暗物质动力学。}}
\]

这不是三套互相竞争的 form factor，而是从单核子流到核矩阵元再到散射振幅的连续计算链。

### 36.1 两层 form factor 描述的物理对象不同

单个质子或中子是夸克、胶子构成的复合粒子。矢量流作用于核子时，其在壳矩阵元一般写为 Dirac–Pauli 分解：

\[
J_N^\mu=
\bar u_N(p_N')
\left[
F_1^{V,N}(t_N)\gamma^\mu+
\frac{iF_2^{V,N}(t_N)}{2m_N}
\sigma^{\mu\nu}q_{N,\nu}
\right]
u_N(p_N),
\qquad q_N=p_N'-p_N.
\]

其中：

- \(F_1^{V,N}\) 描述核子的 Dirac 电荷结构；
- \(F_2^{V,N}\) 描述核子的 Pauli/磁化结构；
- \(t_N=q_N^2\) 是单核子流所使用的四动量转移不变量。

对于 flavor-dependent 的矢量流，若将 UV 耦合显式写出，则可定义

\[
F_i^{V,N}(t_N)
\equiv
\sum_{q=u,d,s}g_{Vq}F_i^{q,N}(t_N),
\qquad i=1,2.
\]

如果采用“把共同耦合从 form factor 中提出”的约定，则应相应定义不含该共同耦合的 flavor 加权和。两种记账方式均可使用，但不能既在 \(F_i^{V,N}\) 中包含 \(g_{Vq}\)，又在振幅外重复乘同一个耦合。

AFH v6.0 则处在原子核层面。它通过核态、单粒子轨道、角动量耦合和一体密度矩阵（OBDME）计算核算符的多体矩阵元，输出例如

\[
W_M,\quad W_{\Sigma''},\quad W_{\Sigma'},\quad
W_{\Phi''},\quad \widetilde W_{\Phi'},\quad
W_\Delta,\quad W_{M\Phi''},\quad W_{\Sigma'\Delta}.
\]

这些响应描述的是整个核对指定核算符的响应，不是单个核子的夸克结构。

| 比较项目 | 单核子 \(F_1,F_2\) | AFH 核响应 |
|---|---|---|
| 研究对象 | 单个质子或中子 | 整个原子核 |
| 物理来源 | 夸克、胶子及核子电流矩阵元 | 核波函数、轨道、自旋、OBDME 和多极展开 |
| 自变量 | \(t_N\)，需明确单核子转移处方 | \(Q_A=|\mathbf q_A|\)，通常通过 \(y_A=(Q_A b_A/2)^2\) 输入 |
| 输出含义 | 给出单核子流各结构的系数 | 给出核算符矩阵元的平方和允许的交叉项 |
| 能否互相替代 | 不能 | 不能 |

因此，调用 AFH 的 \(W_M\) 并不意味着已经自动包含 flavor-universal \(u+d+s\) 矢量流的有限 \(t_N\) 核子形状因子；反过来，单核子 \(F_1,F_2\) 也不能替代 AFH 对氙核多体结构的计算。

### 36.2 从单核子流到整个核流：冲量近似下的连接

在一体冲量近似（impulse approximation）下，核矢量流可以示意写成

\[
J_A^\mu(q_A)=
\sum_{a=1}^{A}
e^{i\mathbf q_A\cdot\mathbf r_a}
J_{N,a}^\mu(q_{N,a}),
\]

其中 \(a\) 对应核内各个质子或中子，\(J_{N,a}^\mu\) 由该核子的 Dirac–Pauli 流构造。将其放入当前三体 VV 振幅，结构为

\[
\boxed{
\mathcal M_3=
\mathcal T_{3,\mu}\,
D^{\mu}{}_{\nu}(q_A)\,
\langle A'|J_A^\nu(q_A)|A\rangle .
}
\]

这里：

- \(\mathcal T_3^\mu\) 包含暗物质线上两张 \(\chi_2\) 辐射图及其干涉；
- \(D_{\mu\nu}(q_A)\) 是媒介子传播子，动量由核整体转移 \(q_A\) 决定；
- \(J_A^\nu\) 是由单核子流嵌入核态后得到的核矢量流；
- AFH 提供该核流所含核算符的多体矩阵元和响应函数。

上式是冲量近似下的核流组织方式。核内核子是束缚态，不能把自由在壳旋量公式不加说明地当作完整核波函数；实际计算需要先将单核子流约化为核内非相对论算符，再由 AFH 的 OBDME 和多极矩阵元完成核结构折叠。

这一步解释了 AFH 与 \(F_1,F_2\) 的正确串联关系：先确定单核子流，再计算其在核内的矩阵元，而不是把两套 form factor 作为两个独立核尺寸修正相乘。

### 36.3 必须区分 \(t_A\) 与 \(t_N\)：不能把附件中的 \(F_i(t_A)\) 直接作为无条件定义

核整体转移定义为

\[
q_A^\mu=P_A'^\mu-P_A^\mu,\qquad
Q_A=|\mathbf q_A|,\qquad t_A=q_A^2.
\]

单核子流的形式变量则是

\[
q_N^\mu=p_N'^\mu-p_N^\mu,\qquad t_N=q_N^2.
\]

在一体冲量近似中，空间转移通常取

\[
\mathbf q_N\simeq\mathbf q_A,
\]

但核内束缚核子的能量转移并不由这条空间关系唯一决定。因此不能在所有计算方案中不加说明地令 \(t_N=t_A\)。

例如：

- 若采用 \(q_N^0=q_A^0=E_R\)，则 \(t_N=t_A=-2m_AE_R\)；
- 若采用静态自由核子诊断 \(q_N^0=0\)，则 \(t_N=-Q_A^2=t_A-E_R^2\)。

二者是不同的运动学处方。对于束缚核子，所采用的单核子 form-factor 变量属于冲量近似的实现选择，必须在输入 metadata 和误差分析中明确记录。

因此，本项目统一使用：

\[
\boxed{
\text{AFH 使用 }Q_A;\qquad
\text{媒介子传播子使用 }t_A;\qquad
\text{单核子 form factor 使用明确处方下的 }t_N.
}
\]

附件中将核子形状因子直接写成 \(F_i(t_A)\) 的表达，只能理解为某一种特定的转移处方（例如令单核子四动量转移等于核整体转移）的简写，不能替代本项目已经采用的 \(t_A/t_N\) 分离约定。

### 36.4 \(F_1,F_2\) 如何决定 AFH 算符的激发系数

按照 §30 的 Dirac–Pauli 非相对论展开，时间分量含有

\[
\begin{aligned}
\frac{J_N^0}{2m_N}
={}&F_1
+\frac{F_1}{2m_N^2}\mathbf K_N^2
-\frac{F_2}{4m_N^2}Q_N^2\\
&+
i\frac{F_1+2F_2}{4m_N^2}
\boldsymbol\sigma_N\cdot
(\mathbf q_N\times\mathbf K_N)
+\cdots ,
\end{aligned}
\]

而空间分量含有

\[
\frac{\mathbf J_N}{2m_N}
=
\frac{F_1}{m_N}\mathbf K_N
+
i\frac{F_1+F_2}{2m_N}
\boldsymbol\sigma_N\times\mathbf q_N
+\cdots .
\]

由此可以看出两个 Pauli 组合具有不同的物理来源：

- \(F_1+2F_2\)：进入时间分量的自旋—轨道电荷结构；
- \(F_1+F_2\)：进入空间分量的磁化电流；
- \(F_1\mathbf K_N\)：进入空间对流电流。

将这些单核子算符推广到整个核并进行 AFH 多极投影，主要的候选对应关系为：

| 单核子流结构 | AFH 核算符/响应候选 | 物理含义 |
|---|---|---|
| 领先电荷 \(F_1\) | \(M\)、\(W_M\) | 相干质量/矢量电荷响应 |
| 时间分量自旋—轨道 \(F_1+2F_2\) | \(\Phi''\)、\(W_{\Phi''}\) | 自旋—轨道电荷响应 |
| 领先电荷与自旋—轨道电荷的交叉项 | \(M\Phi''\)、\(W_{M\Phi''}\) | 两种电荷结构的干涉 |
| 对流电流 \(F_1\mathbf K_N\) | \(\Delta\)、\(W_\Delta\) 等相关投影 | 轨道/对流响应 |
| 磁化电流 \((F_1+F_2)\boldsymbol\sigma_N\times\mathbf q_N\) | \(\Sigma'\)、\(\Sigma''\) 等相关投影 | 横向或纵向自旋响应 |
| 对流与磁化流交叉 | 例如 \(\Sigma'\Delta\) | 空间流干涉 |

这张表是算符结构的导航，不是可以直接用于截面的最终系数表。严格的系数、相位、同位旋组合、\(J\) 多极求和和归一化必须按 AFH v6.0 的定义逐项投影。特别是三体过程不能直接把普通弹性散射的 \(\mathcal O_i\) 系数照搬进来；最终投影必须从完整 \(\mathcal T_3^\mu\) 与核子流的收缩开始。

对当前 flavor-universal \(u+d+s\) 零动量 benchmark，已有锚点为

\[
F_1^{uds,p/n}(0)=3,\qquad
F_2^{uds,p/n}(0)=-0.552
\]

（中子采用同位旋对称近似），因此

\[
F_1+2F_2=1.896,\qquad
F_1+F_2=2.448.
\]

这些数值只用于 \(t_N=0\) 的校验，不能当作整个 Xe 反冲动量范围内的精确常数。若零动量核子电荷 \(g_{VN}=3g_{Vq}\) 已经吸收了 \(F_1^{uds}(0)=3\)，有限动量 Dirac 项应使用归一化形状

\[
f_1^{V,N}(t_N)=
\frac{F_1^{V,N}(t_N)}{F_1^{V,N}(0)}
\]

乘在该零动量耦合上，不能再重复乘一次 3。Pauli 项则按照同一流定义单独计入 \(F_2^{V,N}(t_N)\)。

### 36.5 可以先计算 AFH 的全部响应：建立独立、可复用的核结构数据库

计算 AFH 响应函数本身，并不要求先知道当前三体模型对每个算符的 Wilson 系数。AFH 的核响应是核结构计算结果；在给定核态、密度矩阵、算符定义、同位旋约定和动量网格后，可以独立预计算和归档。

因此，建议把 AFH v6.0 的八个标准响应接口全部纳入统一数据库：

| 编号 | AFH 响应 | 类型 |
|---:|---|---|
| 1 | \(M\) | 对角响应 |
| 2 | \(\Sigma''\) | 对角响应 |
| 3 | \(\Sigma'\) | 对角响应 |
| 4 | \(\Phi''\) | 对角响应 |
| 5 | \(\widetilde\Phi'\) | 对角响应 |
| 6 | \(\Delta\) | 对角响应 |
| 7 | \(M\Phi''\) | 交叉/干涉响应 |
| 8 | \(\Sigma'\Delta\) | 交叉/干涉响应 |

数据库目标写成

\[
\boxed{
\mathcal D_{\rm AFH}
=
\left\{
W_M,W_{\Sigma''},W_{\Sigma'},W_{\Phi''},
\widetilde W_{\Phi'},W_\Delta,
W_{M\Phi''},W_{\Sigma'\Delta}
\right\}_{A,Q_A}.
}
\]

对每个具有 AFH v6.0 default density matrix 的同位素，建议保存：

1. AFH 原生 Mathematica 输出和程序版本；
2. 原始响应与物理归一化响应，明确区分 package convention；
3. \(Q_A\)、\(y_A=(Q_Ab_A/2)^2\) 网格及插值方案；
4. 核自旋、宇称、同位旋通道、谐振子长度 \(b_A\) 和密度矩阵来源；
5. 对角响应与交叉响应的符号、相位及归一化；
6. 长波极限、选择定则、数值精度、求积/插值收敛结果；
7. 每个输出文件的 SHA-256、输入指纹和 provenance manifest；
8. 与独立 Python 实现或解析极限的交叉验证结果。

**因子 4 不能被机械地施加到全部八个响应。** 当前已经审计清楚的 \(A^2/4\to A^2\) 是 AFH 等标量 \(M\) 响应 raw-to-physical 映射规则。其他对角响应和交叉响应必须分别按照 AFH v6.0 的 isospin 与归一化定义审计，不能因为 \(M\) 通道有因子 4，就假设所有通道都使用同一个外部乘数。

同样，当前可追溯的 AFH default-density 主线覆盖七种天然氙同位素。Xe-124 和 Xe-126 缺少当前可用的 AFH v6.0 default matrices。因此，完整数据库的第一阶段应明确称为 **AFH-7**；不能把 Hybrid-9 中的 Helm fallback 称为 AFH-9，也不能通过丰度重归一化掩盖缺失的核结构输入。

预计算全部 AFH 响应的意义在于：以后改变暗物质模型、三体耦合、传播子宽度或核子 form-factor 模型时，可以复用核结构数据库，不必每次重新运行同一套核多体计算。

### 36.6 为什么不能把所有 \(W_X\) 直接相加

“计算所有响应”与“将所有响应都加进某个散射截面”是两个不同的问题。

AFH 的 \(W_M,W_{\Phi''},W_{\Sigma'}\) 等对应不同核算符。它们不是同一物理量的不同数值近似，也不是一组具有相同动力学权重的独立截面。若直接写

\[
W_{\rm total}
\stackrel{\rm wrong}{=}
W_M+W_{\Phi''}+W_{\Sigma'}+W_\Delta+\cdots,
\]

就等于擅自假设所有算符具有相同的动力学系数，并且遗漏了不同核算符之间的干涉。

正确的组织方式是先将核流投影到 AFH 算符基底：

\[
J_A^\mu
=
\sum_\alpha C_\alpha^\mu
\widehat{\mathcal O}_\alpha.
\]

这里 \(C_\alpha^\mu\) 由三体暗物质流、媒介子传播子、单核子 \(F_1/F_2\)、同位旋系数和多极投影共同决定；它一般依赖三体相空间变量，而不是统一常数。

对核矩阵元平方求和后，结构为

\[
\sum_{\alpha,\beta}
C_\alpha C_\beta^*
W_{\alpha\beta}^{A}(Q_A),
\]

其中 \(W_{\alpha\beta}\) 是 AFH 所允许的对角或交叉响应。对当前 AFH v6.0 接口，必须特别保留 \(M\Phi''\) 和 \(\Sigma'\Delta\) 这类交叉结构；不能仅凭两个对角响应的大小推断交叉项，也不能从两个对角响应单独恢复交叉项的符号。

以电荷通道为例：

\[
\mathcal M_{\rm charge}
=
C_M\mathcal A_M+
C_{\Phi''}\mathcal A_{\Phi''}.
\]

平方后为

\[
\begin{aligned}
|\mathcal M_{\rm charge}|^2
={}&|C_M|^2W_M
+|C_{\Phi''}|^2W_{\Phi''}\\
&+2\operatorname{Re}
\left(C_MC_{\Phi''}^*\right)
W_{M\Phi''},
\end{aligned}
\]

其中具体的 AFH 归一化和多极求和应由程序接口负责。干涉项可以为正，也可以为负；在 \(W_M\) 深极小值附近，相对修正可能很大，但这不意味着绝对反冲率必然很大。

因此，数据库可以包含全部响应，但实际截面只能使用模型真正产生、且通过对称性和多极选择定则允许的响应组合。

### 36.7 完整三体收缩：响应数据库怎样进入反冲截面

当前过程为

\[
\chi_1+A\longrightarrow\chi_1+A+s.
\]

暗物质张量

\[
L^{\mu\nu}
=
\frac12\sum_{\rm spins}
\mathcal T_3^\mu\mathcal T_3^{\nu *}
\]

依赖三体末态变量，例如不变质量 \(W^2\)、角变量 \(z\)、方位角 \(\phi_*\) 以及标量动量 \(k_s\)。对固定同位素和固定反冲能量，AFH 核响应的空间动量输入 \(Q_A\) 已确定；但三体动力学系数仍会在相空间内变化。

因此一般应计算

\[
\boxed{
\frac{d\sigma_A}{dE_R}
=
\frac{1}{\mathcal F}
\int d\Phi_3\,
\delta\!\left(E_R-(E_A'-m_A)\right)
\,
D_{\mu\nu}D_{\rho\sigma}^*
L^{\mu\rho}
W_A^{\nu\sigma},
}
\]

其中 \(\mathcal F\) 为相应初态通量因子，\(W_A^{\nu\sigma}\) 再按 AFH 核算符和允许的响应矩阵展开。耦合常数可以统一放在暗物质张量、核流系数或传播子前因子中，但必须有唯一、可追溯的记账位置。

将核流投影到 AFH 基底后，程序实现可组织为

\[
\boxed{
\frac{d\sigma_A}{dE_R}
\propto
\int d\Phi_3
\sum_{\alpha,\beta}
C_\alpha(W^2,z,\phi_*,Q_A,t_N)
C_\beta^*(W^2,z,\phi_*,Q_A,t_N)
W_{\alpha\beta}^{A}(Q_A).
}
\]

这里明确区分：

- \(W_{\alpha\beta}^{A}(Q_A)\)：固定同位素、固定 \(Q_A\) 的核结构输入，可预计算并缓存；
- \(C_\alpha\)：由三体动力学、单核子流和多极投影决定的系数，通常随三体相空间变化；
- \(d\Phi_3\)：完整三体相空间，必须保留两张辐射图、传播子和有限宽度对矩阵元的影响。

只有在振幅系数对相应积分变量的依赖确实可以忽略时，才可以进一步提出解析相空间因子 \(I(D)\)。靠近 Breit–Wigner 极点或 form factor 随 \(t_N\) 显著变化时，不能把 \(I(D)\) 当作完整三体积分的替代。

完整计算至少应同时输出

\[
\left.\frac{d\sigma_A}{dE_R}\right|_{M\text{-only}},
\qquad
\left.\frac{d\sigma_A}{dE_R}\right|_{\rm full\ matched\ one-body},
\]

并逐项保存对角响应、交叉项、总收缩、绝对差和相对差。特别在 \(W_M\) 深极小值附近，不能只报告可能发散的相对比值而不报告绝对截面或事件率。

### 36.8 “全部响应都计算了”是否意味着结果精确？

不能。应区分三个逐级增强的结果层次。

| 层次 | 完成内容 | 可以作出的结论 |
|---|---|---|
| I. AFH 全响应数据库 | 对 AFH v6.0 可用核态计算其八个标准响应，并完成各自归一化和收敛审计 | AFH 核结构输入在所覆盖同位素和算符基底内完整 |
| II. 完整匹配的一体流三体截面 | 完整 \(\mathcal T_3^\mu\)、有限 \(F_1/F_2\)、所有相关 AFH 响应和允许干涉均进入三体相空间积分 | 在指定 UV 模型、冲量近似、AFH v6.0 核结构和 form-factor 处方下，得到完整的一体核流结果 |
| III. 完整物理核散射预测 | 进一步评估两核子流、核结构模型误差、核子 form factor、halo、同位素覆盖和探测器响应 | 得到带有明确理论和实验系统误差的物理预测，而不是数学意义上的无误差“精确值” |

即使第二层全部通过，也不能声称已经包含所有真实核物理效应。至少还需要分别评估：

1. AFH 壳模型空间、核态和 OBDME 的模型依赖；
2. 一体冲量近似之外的两核子交换流和相关修正；
3. 有限 \(t_N\) flavor form factors 的输入、误差和协方差；
4. 束缚核子转移处方及可能的离壳效应；
5. 高阶相对论项和更高阶核算符；
6. 三体相空间、传播子宽度及极点方案的系统误差；
7. 天然氙同位素覆盖、halo 模型和探测器响应。

所以，**完整 AFH 响应库是完整一体流三体计算的必要核结构输入，但它本身不是精确的三体散射截面。**

### 36.9 建议的软件架构：全响应数据库与通用三体收缩引擎

建议将研究代码拆成五个可独立测试、可复用的模块。

| 模块 | 输入 | 输出 | 是否依赖当前三体模型 |
|---|---|---|---|
| A. AFH 核响应数据库 | AFH v6.0、核态/OBDME、同位素和 \(Q_A\) 网格 | 全部可用 AFH 响应及 provenance | 否 |
| B. 三体动力学 | UV 拉格朗日量、质量、耦合、宽度和相空间点 | \(\mathcal T_3^\mu,L^{\mu\nu}\) | 是 |
| C. 单核子流匹配 | flavor 系数、\(F_1^{q,N}(t_N)\)、\(F_2^{q,N}(t_N)\)、\(t_N\) 处方 | 核子流及 NR/多极系数 \(C_\alpha\) | 是 |
| D. 自动投影与响应收缩 | 模块 A 的响应、模块 B/C 的系数 | \(\sum_{\alpha\beta}C_\alpha C_\beta^*W_{\alpha\beta}\) | 是 |
| E. 截面与事件率 | 完整收缩、三体相空间、同位素丰度和 halo | \(d\sigma_A/dE_R\)、\(dR_{\rm Xe}/dE_R\) | 是 |

模块 A 应作为可复用核结构数据层。改变暗物质质量、三体耦合、传播子宽度或核子 form-factor 模型时，只要核态和 AFH 处方不变，就不需要重新计算相同的 AFH 核响应。

模块 C 和 D 则负责把具体模型与 AFH 接起来。这样既避免每次改模型都重跑核结构，也避免把没有匹配依据的响应错误加入物理截面。

### 36.10 推荐的实施顺序与验收标准

建议将原先只围绕 \(M+\Phi''+M\Phi''\) 的工作顺序扩展为“完整 AFH 数据库”和“模型匹配收缩”两条并行工作线。

**工作线 A：先完成 AFH 全响应数据库**

1. 固定 AFH v6.0 源文件版本、default density matrix、同位素、\(b_A\) 和 isospin convention；
2. 对八个接口逐一输出原生 Mathematica 响应，不能只保存 \(M\)；
3. 对角响应与交叉响应分别保存，不将交叉项转换为对角量；
4. 为每个响应建立 \(Q_A\) 网格、插值器、单位、归一化和 SHA-256 manifest；
5. 对每个响应检查长波极限、选择定则、核自旋/宇称、数值精度和插值收敛；
6. 对 \(M\) 通道复现现有已验证 CSV，确保新增数据库不修改旧基准；
7. 对其他通道独立审计 package normalization；不把 \(M\) 的 factor-four 规则直接套用到所有响应；
8. 第一阶段只覆盖具有可追溯 AFH default density matrix 的七种同位素，并明确缺少 Xe-124/Xe-126。

**工作线 B：建立三体核子流匹配和收缩引擎**

1. 固定 flavor-resolved \(F_1^{q,N}(t_N)\)、\(F_2^{q,N}(t_N)\) 输入、误差和 \(t_N\) 处方；
2. 恢复 \(F_1^{uds}(0)=3\)、\(F_2^{uds}(0)=-0.552\) 的零动量锚点；
3. 从完整两图 \(\mathcal T_3^\mu\) 与 Dirac–Pauli 核子流出发，计算三体版核算符系数；
4. 先完成 \(M\)、\(\Phi''\)、\(M\Phi''\) 的完整电荷通道投影；
5. 再根据实际系数、对称性和多极选择定则扩展 \(\Delta,\Sigma',\Sigma''\)、\(\widetilde\Phi'\) 及允许的交叉响应；
6. 实现统一的 \(\sum_{\alpha\beta}C_\alpha C_\beta^*W_{\alpha\beta}\) 收缩接口；
7. 验证 \(M\)-only 模式逐点恢复现有基准，然后逐项打开其他响应；
8. 最后完成完整三体相空间、halo、同位素求和和探测器折叠。

**最低数值验收闭环**

| 验收层 | 必须通过的检查 |
|---|---|
| AFH 源与输入 | 源版本、OBDME、\(b_A\)、同位素和响应编号可追溯 |
| 核响应归一化 | \(M\) 通道恢复已验证的 \(A^2/4\to A^2\) 映射；其他通道各自独立归一化 |
| 核响应矩阵 | 对角响应、交叉响应、复共轭关系、符号和允许多极均有独立检查 |
| 单核子流 | \(F_1,F_2\) 零动量锚点、有限 \(t_N\) 输入及误差协方差可追溯 |
| 三体动力学 | 两张辐射图、传播子宽度、Ward 收缩和四动量守恒逐点通过 |
| 匹配系数 | \(M\)、\(\Phi''\)、\(\Delta\)、\(\Sigma\) 等系数与 AFH 算符定义一致 |
| 干涉 | \(M\Phi''\)、\(\Sigma'\Delta\) 等允许交叉项的符号和归一化可追溯 |
| 回归基准 | 关闭次领先通道时，\(M\)-only 结果恢复当前已验证基线 |
| 相空间 | 完整 \(d\Phi_3\) 求积、极点区域和能量/角度网格分别收敛 |
| 事件率 | 同位素丰度、halo fold 和 detector fold 分层验收 |

本节的核心研究决策是：**先把 AFH v6.0 能提供的全部标准核响应计算并保存为通用数据库，同时并行完成模型特定的三体核子流匹配。最终截面由自动收缩引擎决定实际使用哪些响应及其权重，而不是把数据库中的所有数值直接相加。**

---

## 37. 本专题的最终结论与当前状态边界

1. 使用 AFH v6.0 后仍然需要核子 \(F_1,F_2\)，因为两者分别描述单核子内部结构和整个原子核的多体响应。
2. 可以不等待三体匹配完成，就先计算 AFH v6.0 的全部八种标准响应，建立独立核结构数据库。
3. 全响应数据库不等于完整散射结果；物理截面必须使用完整三体暗物质流、单核子流匹配系数、AFH 对角响应和允许的交叉响应。
4. 不允许把所有 \(W_X\) 以单位权重直接相加；应计算 \(\sum_{\alpha\beta}C_\alpha C_\beta^*W_{\alpha\beta}\)。
5. \(F_1(0)=3\) 若已吸收到零动量核子耦合中，不得再次重复乘 3；有限 \(t_N\) 的形状另行输入。
6. AFH \(M\) 通道的 factor-four 映射只按已经审计的 raw-to-physical 规则执行一次，不能自动套到所有其他响应。
7. AFH-7 的同位素覆盖边界仍然存在；缺失的 Xe-124/Xe-126 不能由 Helm fallback 冒充 AFH default response。
8. 即使完成全部 AFH 响应和完整一体流收缩，结果仍属于指定核结构模型和冲量近似下的预测，必须单独评估两体核流、有限核子形状因子、核结构、halo 和探测器系统误差。

**当前状态：** 本节记录的是新的理论组织方式、软件架构和数值验收计划，不代表八种响应的全同位素数据库已经生成，也不代表新的 \(\Phi''\)、\(\Sigma\)、\(\Delta\) 数值结果已经通过验收。

# 第五部分：完整三体反冲率、响应矩阵与数值验收规范

本部分把前述 UV 三体振幅、Dirac–Pauli 核子流和 AFH 核响应进一步组织成可直接实现的反冲率公式。这里不再把 AFH 响应写成一个没有动力学权重的列表，而是明确区分三体动力学、媒介子传播子、核子流匹配、AFH 核结构、相空间、halo 和探测器响应。

本部分的核心原则是：

\[
\boxed{
\text{完整反冲率}
=
\text{三体动力学}
\times
\text{媒介子传播子}
\times
\text{匹配后的 AFH 核响应矩阵}
\times
\text{完整三体相空间}
\times
\text{halo 与靶核归一化}.
}
\]

文中所有 \(R_i^{(3)}\) 都是三体过程投影到 AFH 算符基底后得到的动力学响应系数；它们不是 AFH 核响应本身，也不是普通弹性 \(2\to2\) NREFT 的响应系数。

## 38. 从 \(M\)-only 基准到完整三体反冲率

### 38.1 \(M\)-only 反冲率的准确含义

当前已验证的主基准只保留 AFH 领先阶矢量电荷/质量响应。将三体暗物质流、矢量媒介子传播子和核子电荷系数统一收进三体动力学系数后，可以示意写成

\[
\frac{dR_M}{dE_R}
=
\mathcal N
\int d^3v\,f_{\rm lab}(\mathbf v)\,v
\int d\Phi_3\,
\delta_E\,
R_M^{(3)}(\xi)\,
W_M^A(Q_A).
\]

这里 \(\xi\) 表示三体相空间点，例如 \((W^2,z,\phi_*)\)；\(\delta_E\) 是固定核反冲能量的约束；\(W_M^A\) 是指定同位素 \(A\) 的 AFH \(M\) 响应。该式是一个结构表达式，公共归一化因子 \(\mathcal N\) 仍须按 §38.3 展开，不能在数值代码中作为未定义的自由常数。

### 38.2 完整 AFH 响应的反冲率

将核子流投影到 AFH 核算符后，完整的一体核流结果应写成响应矩阵收缩：

\[
\boxed{
\frac{dR}{dE_R}
=
\mathcal N
\int d^3v\,f_{\rm lab}(\mathbf v)\,v
\int d\Phi_3\,\delta_E
\sum_{\alpha,\beta}
\sum_{\tau,\tau'}
\mathcal R_{\alpha\beta}^{(3),\tau\tau'}(\xi)\,
W_{\alpha\beta}^{A,\tau\tau'}(Q_A).
}
\]

其中：

- \(\alpha,\beta\) 标记 AFH 核算符或相应多极结构；
- \(\tau,\tau'=0,1\) 标记等标量、等矢量同位旋通道；
- \(\mathcal R_{\alpha\beta}^{(3),\tau\tau'}\) 是由完整三体振幅、媒介子传播子、核子 form factors 和多极投影产生的动力学系数；
- \(W_{\alpha\beta}^{A,\tau\tau'}\) 是同位素 \(A\) 的 AFH 对角或干涉核响应；
- \(d\Phi_3\) 是包含末态暗物质、反冲核和辐射标量的完整不变相空间。

本文件采用的系数记账约定是：\(\mathcal R_{\alpha\beta}^{(3)}\) 包含暗物质三体张量、矢量媒介子传播子、UV 耦合和从核子流到 AFH 多极算符的动力学系数；\(W_{\alpha\beta}^{A,\tau\tau'}\) 只包含相应核矩阵元及 AFH 自身约定。若程序选择把某个耦合或传播子移入 \(W\) 一侧，必须同步修改另一侧定义，并保证每个因子只出现一次。

若在给定近似下响应矩阵已经对角化，或某些交叉项由对称性严格禁止，上式才可缩写成

\[
\frac{dR}{dE_R}
=
\mathcal N
\int d^3v\,f_{\rm lab}v
\int d\Phi_3\,\delta_E
\left[
R_M^{(3)}W_M
+R_{\Phi''}^{(3)}W_{\Phi''}
+R_{M\Phi''}^{(3)}W_{M\Phi''}
+R_{\Sigma'}^{(3)}W_{\Sigma'}
+R_{\Sigma''}^{(3)}W_{\Sigma''}
+R_\Delta^{(3)}W_\Delta
+\cdots
\right].
\]

这个逐项写法是便于展示的简写，不代表 AFH 的全部响应可以单位权重相加，也不代表每一项都一定由当前 UV 模型产生。尤其是交叉响应的系数、复共轭和因子 2，必须与 AFH v6.0 输出定义保持一致。

### 38.3 将公共归一化因子 \(\mathcal N\) 展开

采用相对论外线归一化，初始核处于静止系：

\[
P_A^\mu=(m_A,\mathbf 0),\qquad
p_\chi^\mu=(E_\chi,\mathbf p_\chi).
\]

不变初态通量为

\[
\mathcal F_A
=
4\sqrt{(p_\chi\cdot P_A)^2-m_\chi^2m_A^2}
=
4m_A|\mathbf p_\chi|
=
4m_AE_\chi v,
\]

其中 \(v=|\mathbf p_\chi|/E_\chi\) 是靶核静止系中的相对速度。定义完整三体振幅的自旋平均平方后，

\[
\boxed{
\frac{d\sigma_A}{dE_R}
=
\frac{1}{\mathcal F_A}
\int d\Phi_3\,
\overline{|\mathcal M_A|^2}\,
\delta\!\left(E_R-(E_A'-m_A)\right).
}
\]

这里

\[
d\Phi_3
=
(2\pi)^4
\delta^{(4)}(p_\chi+P_A-p_\chi'-P_A'-k_s)
\prod_{f=\chi',A',s}
\frac{d^3p_f}{(2\pi)^3\,2E_f}.
\]

固定反冲能量的 delta 函数优先使用精确核质量壳关系。由

\[
E_A'=\sqrt{m_A^2+Q_A^2}
\]

可得

\[
E_R=\sqrt{m_A^2+Q_A^2}-m_A,
\qquad
Q_A^2=E_R(E_R+2m_A),
\qquad
t_A=-2m_AE_R.
\]

因此精确约束为

\[
\delta_E
=
\delta\!\left(
E_R-\sqrt{m_A^2+Q_A^2}+m_A
\right).
\]

只有在 \(E_R\ll m_A\) 时，才可采用

\[
E_R\simeq \frac{Q_A^2}{2m_A},
\qquad
\delta_E\simeq
\delta\!\left(E_R-\frac{Q_A^2}{2m_A}\right).
\]

若数值程序从 \(Q_A\) 而不是从三动量分量积分，变量替换还必须包含相应 Jacobian；不能在使用精确质量壳关系后又重复采用非相对论 delta 函数。

每单位探测器质量的天然氙核反冲率为

\[
\boxed{
\frac{dR_{\rm Xe}}{dE_R}
=
\frac{\rho_\chi}{m_\chi}
\sum_A\frac{X_A}{m_A}
\int d^3v\,
f_{\rm lab}(\mathbf v)\,
v\,
\frac{d\sigma_A(v)}{dE_R}.
}
\]

这里 \(X_A\) 是同位素质量分数，满足 \(\sum_A X_A=1\)；\(f_{\rm lab}\) 归一化为 \(\int d^3v f_{\rm lab}=1\)。因而在质量分数约定下，每单位探测器质量中的同位素靶核数为 \(X_A/m_A\)。

若输入采用天然氙原子数丰度 \(x_A\)，则应先转换为

\[
\overline m_{\rm Xe}=\sum_A x_A m_A,
\qquad
X_A=\frac{x_A m_A}{\overline m_{\rm Xe}},
\]

从而

\[
\frac{X_A}{m_A}=\frac{x_A}{\overline m_{\rm Xe}}.
\]

这两种写法等价，但不能把质量分数和原子数丰度混用或重复乘丰度。

因此，原先的 \(\mathcal N\) 不是一个新的物理参数；它由 \(\rho_\chi/m_\chi\)、靶核数归一化、初态通量、自旋平均约定以及耦合常数的唯一记账位置组成。代码必须明确这些因子分别放在哪一层。

自旋平均也必须只有一次：本文的 \(W_A^{\mu\nu}\) 定义已经包含初始核自旋 \(1/(2J_A+1)\) 的平均；因此在使用该核张量时，\(\overline{|\mathcal M_A|^2}\) 中只再对初始暗物质自旋平均、并对末态自旋求和，不能在总振幅平方外额外再除一次 \(2J_A+1\)。若程序改用未平均的核张量，则必须把核自旋平均移到总振幅平方的统一位置。

## 39. AFH 响应矩阵、干涉结构与同位旋分解

### 39.1 从完整核张量到响应矩阵

在固定同位素和核动量转移下，定义核流矩阵元

\[
J_A^\mu(M_A',M_A)
=
\langle A(P_A',M_A')|J_A^\mu|A(P_A,M_A)\rangle.
\]

核张量为

\[
W_A^{\mu\nu}
=
\frac{1}{2J_A+1}
\sum_{M_A,M_A'}
J_A^\mu(M_A',M_A)
J_A^{\nu *}(M_A',M_A).
\]

将核流按 AFH 多极算符展开：

\[
J_A^\mu
=
\sum_{\alpha,\tau}
C_\alpha^{\mu,\tau}(\xi,t_N)
\mathcal A_\alpha^\tau(Q_A).
\]

于是

\[
W_A^{\mu\nu}
=
\sum_{\alpha,\beta}
\sum_{\tau,\tau'}
C_\alpha^{\mu,\tau}
C_\beta^{\nu,\tau' *}
W_{\alpha\beta}^{A,\tau\tau'}(Q_A),
\]

其中

\[
W_{\alpha\beta}^{A,\tau\tau'}
=
\frac{1}{2J_A+1}
\sum_{M_A,M_A'}
\mathcal A_\alpha^\tau
\mathcal A_\beta^{\tau' *}
\]

表示相应约定下的核矩阵元乘积及多极求和。AFH v6.0 对具体响应的归一化、约化矩阵元和交叉项定义必须以源程序接口为准。

### 39.2 对角项与干涉项不能混为一谈

对角响应例如

\[
W_{MM}^{A,\tau\tau'},\qquad
W_{\Phi''\Phi''}^{A,\tau\tau'},\qquad
W_{\Sigma'\Sigma'}^{A,\tau\tau'}
\]

与交叉响应例如

\[
W_{M\Phi''}^{A,\tau\tau'},\qquad
W_{\Sigma'\Delta}^{A,\tau\tau'}
\]

具有不同的数学含义。核响应矩阵满足 Hermiticity：

\[
W_{\beta\alpha}^{A,\tau'\tau}
=
\left(W_{\alpha\beta}^{A,\tau\tau'}\right)^*.
\]

如果代码对所有有序的 \((\alpha,\beta)\) 都求和，则一对非对角项已经同时出现；如果数据库只保存一个无序交叉项，则必须按 AFH v6.0 的定义加入相应的 \(2\operatorname{Re}\) 组合。两种记账方式只能选一种，不能既保存双向矩阵元又额外乘 2。

以电荷通道为例，若采用只保存一次交叉响应的约定，

\[
\begin{aligned}
\mathcal S_{\rm charge}
={}&
|C_M|^2W_{MM}
+
|C_{\Phi''}|^2W_{\Phi''\Phi''}
\\
&+
2\operatorname{Re}
\left(C_MC_{\Phi''}^*W_{M\Phi''}\right).
\end{aligned}
\]

干涉项可以为正也可以为负。仅凭 \(W_M\) 和 \(W_{\Phi''}\) 两个对角响应，不能恢复 \(W_{M\Phi''}\) 的符号或相位。

AFH v6.0 的标准算符/响应接口应严格区分

\[
M,\quad \Sigma',\quad \Sigma'',\quad
\Delta,\quad \Phi'',\quad \widetilde\Phi',
\]

以及程序实际提供的交叉响应，例如

\[
M\Phi'',\qquad \Sigma'\Delta.
\]

这里使用的是 \(\widetilde\Phi'\)，不能误写成 \(\widetilde\Phi''\)。也不能把“六类基本核算符”“八个程序响应接口”和“所有数学上可能的 \(\alpha\beta\) 交叉矩阵元”视为同一集合。当前程序没有输出或没有定义的交叉响应，不能仅靠两个对角响应推算出来。

### 39.3 质子、中子与等标量、等矢量通道

先对给定 UV 夸克流完成 flavor 加权：

\[
F_i^{V,p}(t_N)=\sum_q c_qF_i^{q,p}(t_N),
\qquad
F_i^{V,n}(t_N)=\sum_q c_qF_i^{q,n}(t_N),
\qquad i=1,2.
\]

再定义同位旋分解

\[
F_i^{(0)}(t_N)
=
\frac{F_i^{V,p}(t_N)+F_i^{V,n}(t_N)}{2},
\]

\[
F_i^{(1)}(t_N)
=
\frac{F_i^{V,p}(t_N)-F_i^{V,n}(t_N)}{2}.
\]

因此

\[
F_i^{V,p}=F_i^{(0)}+F_i^{(1)},
\qquad
F_i^{V,n}=F_i^{(0)}-F_i^{(1)}.
\]

相应的核响应收缩包含

\[
W_{\alpha\beta}^{00},\qquad
W_{\alpha\beta}^{01},\qquad
W_{\alpha\beta}^{10},\qquad
W_{\alpha\beta}^{11}
\]

及其动力学系数。由于 Hermiticity，\(01\) 与 \(10\) 不是两个可以任意独立赋值的实数。

当前 flavor-universal \(u+d+s\) 零动量 benchmark 有

\[
F_1^{V,p}(0)=F_1^{V,n}(0)=3.
\]

但这只说明该点的等矢量 Dirac 电荷分量为零；它不能证明有限 \(t_N\) 下 \(F_1^p=F_1^n\)，也不能证明 Pauli 形状因子在有限动量处仍完全相等。实际计算必须先进行 flavor-separated 输入，再按上式形成同位旋系数。

AFH v6.0 的 \(\tau=0,1\) 归一化可能包含程序自身的 isospin convention。实现时必须把这里的 \(1/2\) 定义与 AFH 源程序的质子/中子算符约定对齐；不能仅凭符号相同就假定数值归一化相同。

### 39.4 \(R_i^{(3)}\) 与 \(W_i\) 的分工

二者的职责应严格区分：

| 量 | 由什么决定 | 主要变量 | 是否可预计算 |
|---|---|---|---|
| \(R_i^{(3)}\) 或 \(\mathcal R_{\alpha\beta}^{(3)}\) | 三体振幅、传播子、\(F_1/F_2\)、同位旋系数和多极投影 | \(W^2,z,\phi_*,q_A,q_\chi,k_s,t_N\) 等 | 可对给定模型和网格缓存 |
| \(W_{\alpha\beta}^{A,\tau\tau'}\) | AFH 核态、OBDME、核算符和同位旋约定 | 同位素 \(A\)、\(Q_A\) | 可独立预计算并复用 |
| \(d\Phi_3\) | 三体末态运动学 | 初态速度、\(E_R,W^2,z,\phi_*\) 等 | 不能被核响应替代 |
| \(f_{\rm lab}\) | halo 与实验室运动学 | 速度向量和时间/halo benchmark | 可独立缓存 |

所以，AFH 响应库可以先于三体匹配完成；但 \(R_i^{(3)}\) 必须由当前三体 UV 模型推导，不能直接复制普通弹性散射的响应系数。

## 40. 矢量媒介子传播子、Ward 收缩与 \(\chi_2\) 有限宽度

### 40.1 完整振幅中的媒介子张量

将核整体转移定义为

\[
q_A^\mu=P_A'^\mu-P_A^\mu.
\]

在 Proca/单位规范的常见约定下，质量为 \(m_V\) 的矢量媒介子传播子可写成

\[
D_{\mu\nu}^{V}(q_A)
=
\frac{-i}{t_A-m_V^2+i\epsilon}
\left(
g_{\mu\nu}
-\frac{q_{A,\mu}q_{A,\nu}}{m_V^2}
\right).
\]

具体整体符号随度规和 Feynman 规则约定变化，但横向与纵向张量结构必须保持一致。完整振幅为

\[
\boxed{
\mathcal M_A
=
\mathcal T_3^\mu
D_{\mu\nu}^{V}(q_A)
J_A^\nu.
}
\]

这里 \(\mathcal T_3^\mu\) 是暗物质三体流，\(J_A^\nu\) 是核矢量流。若把媒介子传播子吸收到 \(\mathcal T_3^\mu\) 的定义中，后续张量中就不能再次乘 \(D_{\mu\nu}^{V}\)。

### 40.2 Proca 纵向项何时可以忽略

传播子中的纵向项与

\[
(q_{A,\mu}\mathcal T_3^\mu)
(q_{A,\nu}J_A^\nu)
\]

成正比。因此，只有在相应一侧的流守恒、使该乘积严格为零时，才可以删去纵向部分。

对于相同质量、在壳的自由核子 Dirac–Pauli 矢量流，

\[
q_{N,\mu}J_N^\mu=0
\]

可由 Dirac 方程和反对称的 Pauli 张量项得到。但这不自动证明任意束缚核子近似、截断的一体核流或不一致的两体流都严格满足核流连续性方程。若 impulse approximation 或数值截断破坏了守恒关系，必须把残差作为诊断，而不是静默丢掉纵向项。

另一方面，本项目暗物质侧是不同质量态之间的跃迁，并伴随标量辐射。§27.5 已经得到零宽度下

\[
q_{A,\mu}\mathcal T_3^\mu
\propto
(m_{\chi_2}-m_{\chi_1})
\]

乘以两张内部传播子结构；一般不为零。因此，不能把普通弹性暗物质矢量流的 Ward identity 直接套到 \(\mathcal T_3^\mu\)。

若 UV 理论是自发破缺的规范理论，还应从完整规范模型检查相应 Goldstone 模式和 Ward–Slavnov–Taylor 关系。不能只保留 Proca 纵向项、同时忽略 UV 完备化要求的相关 Goldstone 贡献。是否需要该贡献取决于具体规范完成和相互作用顶点，不能在没有模型推导时预设为零。

### 40.3 两张标量辐射图必须先相加再平方

沿用 §27 的动量约定：

\[
r_1=p_\chi-k_s,\qquad
r_2=p_\chi'+k_s,
\]

\[
D_1=r_1^2-m_{\chi_2}^2,\qquad
D_2=r_2^2-m_{\chi_2}^2.
\]

有限宽度下定义

\[
\mathcal D_i
=
D_i+i\,m_{\chi_2}\Gamma_{\chi_2}(r_i^2),
\]

其中固定宽度近似对应 \(\Gamma_{\chi_2}(r_i^2)=\Gamma_{\chi_2}\)。三体顶角结构为

\[
\widehat\Gamma_3^\mu
=
\gamma^\mu
\frac{\slashed r_1+m_{\chi_2}}{\mathcal D_1}
+
\frac{\slashed r_2+m_{\chi_2}}{\mathcal D_2}
\gamma^\mu.
\]

令两图振幅为 \(\mathcal M_1,\mathcal M_2\)，则

\[
\boxed{
|\mathcal M_1+\mathcal M_2|^2
=
|\mathcal M_1|^2
+
|\mathcal M_2|^2
+
2\operatorname{Re}(\mathcal M_1\mathcal M_2^*).
}
\]

交叉项不是可选的数值修正，而是完整振幅平方的一部分。离壳重质量极限下两图可以相干产生振幅因子 2，但这不能替代极点附近的逐点计算。

### 40.4 \(\chi_2\) 的 Breit–Wigner 宽度与 Ward 审计

\(\chi_2\) 的有限宽度来自其自能或物理开放衰变道；它不是矢量媒介子的宽度。若只开放 \(\chi_2\to\chi_1s\)，可使用 §27.5 的部分宽度；若有其他开放道，传播子中必须使用总宽度。

固定宽度插入

\[
D_i\longrightarrow D_i+i m_{\chi_2}\Gamma_{\chi_2}
\]

会产生 §27.5 已明确推导的 Ward 收缩残项。故数值计算必须：

1. 对两张图使用同一套宽度方案；
2. 明确区分常数宽度、能量依赖自能和复极点方案；
3. 对每张图保存 \(D_i\)、\(\mathcal D_i\)、分子和相位；
4. 在远离极点处检查零宽度极限；
5. 在极点附近比较不同自能/宽度方案；
6. 不把固定宽度下的零宽度 Ward 结果当作严格恒等式。

## 41. 三体独立动量、运动学边界与积分 Jacobian

### 41.1 三个动量变量必须独立保存

定义

\[
q_A^\mu=P_A'^\mu-P_A^\mu,
\qquad
q_\chi^\mu=p_\chi'^\mu-p_\chi^\mu,
\qquad
k_s^\mu=\text{末态辐射标量四动量}.
\]

由总四动量守恒

\[
p_\chi+P_A=p_\chi'+P_A'+k_s
\]

得到

\[
\boxed{
q_A^\mu+q_\chi^\mu+k_s^\mu=0,
\qquad
q_A^\mu=-q_\chi^\mu-k_s^\mu.
}
\]

这三个变量承担不同职责：

- \(q_A\)：AFH 核响应的外部转移；空间模长 \(Q_A=|\mathbf q_A|\) 进入 \(y_A=(Q_Ab_A/2)^2\)，不变量 \(t_A=q_A^2\) 进入矢量媒介子传播子；
- \(q_\chi\)：暗物质初末态动量差，进入暗物质外线运动学和三体顶角；
- \(k_s\)：真实末态标量的独立四动量，进入两个 \(\chi_2\) 内部动量、传播子和三体相空间。

三体过程不能使用弹性散射中的 \(q_A=-q_\chi\)。只有在 \(k_s=0\) 的退化极限才会恢复该关系，而本项目研究的正是 \(k_s\neq0\) 的辐射过程。

### 41.2 不变质量变量与递归相空间

定义末态暗物质—标量系统

\[
K^\mu=p_\chi'^\mu+k_s^\mu,\qquad W^2=K^2.
\]

三体相空间严格分解为

\[
d\Phi_3
=
\frac{dW^2}{2\pi}
d\Phi_2(p_\chi+P_A;P_A',K)
d\Phi_2(K;p_\chi',k_s).
\]

在 \(K\) 静止系，内部动量为

\[
p_*=
\frac{\lambda^{1/2}(W^2,m_\chi^2,m_s^2)}{2W},
\]

并且

\[
W\ge m_\chi+m_s.
\]

采用 \((W^2,z,\phi_*)\) 作为积分变量时，必须把精确两体相空间、外层散射角、内部角度和变量变换 Jacobian 一并保留。可写成

\[
d\Phi_3
=
\mathcal J_\Phi(E_R,v;W^2,z,\phi_*)\,
dW^2\,dz\,d\phi_*,
\]

其中 \(\mathcal J_\Phi\) 必须由上述不变相空间分解推导，不能通过拟合旧数值反推，也不能在更换积分变量后继续沿用旧 Jacobian。

在固定 \(E_R\) 时，\(Q_A\) 由核质量壳关系确定；三体动力学仍随 \(W^2,z,\phi_*\) 变化。尤其 \(D_1,D_2\) 分别依赖两张图的内部四动量，所以不能仅因 \(Q_A\) 固定就把整个振幅从三体积分中提出。

### 41.3 三体最小速度与适用近似

在 §28.2 的重粒子、非相对论近似下，令

\[
\mu_A=\frac{m_\chi m_A}{m_\chi+m_A},
\]

则

\[
D(E_R,v)
=
vQ_A-\frac{Q_A^2}{2\mu_A}-m_s.
\]

允许相空间要求 \(D\ge0\)，从而

\[
\boxed{
v_{\min}^{(3)}(E_R)
=
\frac{Q_A}{2\mu_A}+\frac{m_s}{Q_A}.
}
\]

这里 \(Q_A\) 应优先由精确反冲关系确定；上述 \(v_{\min}^{(3)}\) 仍属于 §28.2 所述的非相对论重粒子近似，不能标记为包含所有相对论修正和完整传播子效应的精确公式。

对每个 halo 速度点，数值程序应检查：

\[
D\ge0,\qquad
W\ge m_\chi+m_s,
\]

以及外层和内部 Källén 函数的非负性。对 \(D<0\) 的点，积分必须严格关闭，而不是通过数值截断留下小的非物理贡献。

### 41.4 解析 \(I(D)\) 与完整三体积分的边界

当矩阵元在内部不变质量和角变量上近似常数时，§28.4 的

\[
I(D)=
\int_0^D d\epsilon\,
\sqrt{\epsilon(\epsilon+2m_s)}
\]

可以提出并解析积分。接近 \(\chi_2\) Breit–Wigner 极点时，两个传播子和两图干涉会随 \(W^2,z,\phi_*\) 明显变化，此时必须计算

\[
\int dW^2\,dz\,d\phi_*\,
\mathcal J_\Phi\,
\overline{|\mathcal M_1+\mathcal M_2|^2}
\]

而不能只用 \(I(D)\) 代替。解析 \(I(D)\) 是受控近似基准，不是所有参数点的完整三体截面。

## 42. AFH 因子 4、同位素归一化与天然氙组装

### 42.1 \(M\) 通道 factor-four 的唯一位置

当前已审计的 AFH v6.0 等标量 \(M\) 响应满足

\[
R_{M,\rm AFH}^{\rm raw}(0)=\frac{A^2}{4},
\qquad
R_M^{\rm phys}(0)=A^2,
\]

因此

\[
R_M^{\rm phys}(Q_A)=4R_{M,\rm AFH}^{\rm raw}(Q_A)
\]

（若有有限打印精度修正 \(C_0\)，必须独立记录）。

这个因子 4 是特定 \(M\) 通道 raw-to-physical 映射的一部分，不是三体相空间因子、不是 \(g_{VN}=3g_{Vq}\)，也不是可以自动施加到 \(\Phi''\)、\(\Sigma'\)、\(\Delta\) 或交叉响应上的统一规则。每个 AFH 通道必须按 v6.0 源程序和自身 isospin convention 独立审计。

### 42.2 同位素响应必须先分别计算

对每个同位素 \(A\)，单独构造

\[
W_{\alpha\beta}^{A,\tau\tau'}(Q_A),
\qquad
m_A,\quad J_A,\quad b_A,\quad
\text{OBDME}_A.
\]

然后计算对应的

\[
\frac{d\sigma_A}{dE_R}
\]

并在事件率层面进行同位素求和。不能先对不同同位素的 AFH 响应作简单平均，因为它们的核自旋、核波函数、响应极小值位置和反冲运动学都不同。

当前主线是具有可追溯 AFH v6.0 default density matrices 的 AFH-7。Xe-124/Xe-126 缺失输入仍必须显式记录；Hybrid-9 的 fallback 只能作为单独核模型敏感性方案，不能冒充纯 AFH-9。

### 42.3 天然氙丰度的两种等价记账方式

若 \(x_A\) 是原子数丰度，

\[
\overline m_{\rm Xe}=\sum_A x_A m_A,
\qquad
X_A=\frac{x_A m_A}{\overline m_{\rm Xe}}.
\]

每单位探测器质量的靶核数权重为

\[
\frac{X_A}{m_A}
=
\frac{x_A}{\overline m_{\rm Xe}}.
\]

因此天然氙反冲率可以使用

\[
\sum_A\frac{X_A}{m_A}
\]

或等价的

\[
\frac{1}{\overline m_{\rm Xe}}\sum_Ax_A
\]

但不能混合两套定义重复乘质量或丰度。数据文件必须注明 abundance 是 number fraction 还是 mass fraction。

## 43. 理论误差预算与 LZ 探测器接口

### 43.1 完整计算的理论误差预算

即使全部 AFH 一体响应都计算完成，最终结果仍然有模型和数值误差。至少应建立以下误差账本：

| 误差来源 | 需要评估的内容 | 优先级 |
|---|---|---|
| AFH 核结构 | 壳模型空间、核态、OBDME、谐振子长度和多极截断 | 高 |
| 核子流匹配 | flavor-resolved \(F_1,F_2\)、有限 \(t_N\)、输入协方差 | 高 |
| 一体流近似 | 两核子交换流、相关修正和连续性方程一致性 | 中—高 |
| 三体相空间 | 积分区域、Jacobian、阈值处理和求积收敛 | 高 |
| \(\chi_2\) 传播子 | 总宽度、自能方案、极点位置和两图干涉 | 高 |
| 矢量媒介子 | 完整 \(t_A\) 依赖、纵向结构及规范完成 | 由模型决定 |
| Halo | 速度分布、银河逃逸速度、实验室运动和参数变化 | 中 |
| 天然氙组装 | 丰度、同位素覆盖和核质量 | 高 |
| 探测器响应 | 效率、能量分辨率、接受度、S1/S2 响应 | 高 |

误差必须区分统计数值误差、输入参数误差和理论模型误差。不能把不同来源的误差在没有相关性依据时简单合成一个百分比。

### 43.2 理论核反冲谱与探测器可观测量

理论层首先得到

\[
\frac{dR}{dE_R},
\]

它包含三体动力学、AFH 核结构、halo 和天然氙同位素求和，但还不是实验重建能量谱。

若只采用一维效率近似，预期事例数可写为

\[
N_{\rm pred}
=
MT\int dE_R\,
\frac{dR}{dE_R}\,
\epsilon(E_R),
\]

其中 \(M T\) 是曝光量，\(\epsilon(E_R)\) 是相应核反冲能量下的总效率。

若需要处理重建变量 \(E_{\rm obs}\)、S1/S2 和能量分辨率，则必须引入条件响应分布，例如

\[
\frac{dN}{dE_{\rm obs}}
=
MT\int dE_R\,
\frac{dR}{dE_R}\,
P(E_{\rm obs}\mid E_R)\,
\epsilon(E_R).
\]

更完整的 LZ 分析还需要相应的二维信号响应、校准和 nuisance 参数、背景模型及似然函数。一维效率折叠不能被称为完整 detector-level likelihood，也不能把理论核反冲能量直接等同于实验重建能量。

## 44. 从 \(M\)-only 到完整响应的数值验收标准

本节把理论公式转成可执行的分层验收要求。任何一层的 PASS 都只对该层负责，不能替代后续层的物理验收。

### 44.1 基准回归：完整程序必须恢复 \(M\)-only

在关闭所有非 \(M\) 核算符系数后，完整响应引擎必须逐点恢复现有 \(M\)-only 结果：

\[
C_{\alpha\ne M}=0
\quad\Longrightarrow\quad
\left.\frac{d\sigma_A}{dE_R}\right|_{\rm full}
=
\left.\frac{d\sigma_A}{dE_R}\right|_{M\text{-only}}.
\]

必须使用相同的核质量、AFH 网格、插值、三体积分变量、宽度方案、耦合归一化和 factor-four 记账。若不能恢复，不能继续解释新增响应的物理贡献。

### 44.2 振幅和张量级检查

1. 直接使用两张完整 Dirac 振幅相加平方，与 trace 形式 \(L^{\mu\nu}\) 对照；
2. 验证 \(|\mathcal M_1+\mathcal M_2|^2\) 与两张对角图加交叉项的分解逐点一致；
3. 检查 \(q_A+q_\chi+k_s=0\) 的四分量残差；
4. 零宽度下复现 §27.5 的 Ward 收缩；
5. 固定宽度下复现其显式残项，并比较自能/复极点方案；
6. 分别检查 \(L^{00}\)、\(L^{0i}\)、\(L^{ij}\) 和媒介子传播子的纵向贡献；
7. 在相同约定下，用自由核子 Dirac–Pauli 流和 NR 展开交叉验证系数、符号与归一化。

### 44.3 AFH 响应矩阵检查

1. 每个对角响应与原生 AFH v6.0 输出逐点一致；
2. 每个交叉响应单独检查符号、相位和程序归一化；
3. 检查 Hermiticity 关系及最终收缩的实数性；
4. 分别验证 \(\tau\tau'=00,01,10,11\) 的同位旋记账；
5. 不把未由 AFH 接口提供的交叉响应从两个对角响应推算出来；
6. \(M\) 通道 factor 4 只出现一次，其他通道分别审计；
7. Xe-131 在 \(Q_A\simeq158,256,365\ {\rm MeV}\) 的响应极小值附近提高网格分辨率，并同时报告绝对响应和插值误差。

### 44.4 相空间和积分收敛检查

1. 逐点验证能量、动量守恒和所有末态质量壳条件；
2. 检查 \(W\)、\(z\)、\(\phi_*\) 的边界及 Jacobian；
3. 对 \(D<0\) 的运动学关闭点严格得到零相空间；
4. 在常振幅极限下复现递归相空间和解析 \(I(D)\)；
5. 在远离极点处检查有限宽度结果向零宽度结果的连续极限；
6. 在极点附近分别提高 \(W^2,z,\phi_*\) 求积阶数；
7. 对求积收敛和 Mathematica/Python 代码间一致性分别验收，不能用代码间一致性代替积分收敛。

### 44.5 反冲率和实验组装检查

1. \(M\)-only 与 full matched one-body 结果在同一参数点并列输出；
2. 分别保存 \(M\)、\(\Phi''\)、\(M\Phi''\)、空间流对角项和允许的交叉项；
3. 同时报告绝对差、相对差和绝对事件率，尤其关注 \(W_M\) 深极小值；
4. 对每个同位素单独完成 \(d\sigma_A/dE_R\)，再进行天然氙丰度组装；
5. 检查 number fraction 与 mass fraction 两种组装方式数值等价；
6. 分开验收 halo fold、效率折叠、能量分辨率和 detector-level likelihood；
7. 为每个结果保存输入参数、程序版本、核响应 SHA-256、求积阶数、宽度方案和 provenance。

本项目不应在没有统一验收前人为指定一个“完整结果百分比精度”。每一层应先依据独立基准、求积阶数变化和跨代码比较建立容差，再冻结验收阈值。已有 \(M\)-only 基准的历史容差继续保留，不因新增响应而放宽。

### 44.6 当前状态边界

本部分建立的是完整三体反冲率的公式组织、归一化定义、响应矩阵结构和数值验收规范。它不意味着下列工作已经完成：

- 全部 AFH 八种响应的七同位素数值数据库；
- 所有有限 \(t_N\) flavor form factors 及其协方差；
- 完整三体 \(R_i^{(3)}\) 系数和全部允许的同位旋干涉；
- \(\chi_2\) 完整 UV 自能和极点方案比较；
- 全参数空间完整三体张量收缩；
- AFH-9 同位素覆盖；
- 完整 LZ detector-level likelihood。

因此，当前可以准确称为：**AFH v6.0 核结构框架下的完整三体一体核流反冲率计算规范已经建立；对应的全响应数值实现和最终天然氙预测仍需逐层验收。**
