# AFH 核响应方法背景与本文阅读导言

> **文档说明**
>
> 本节是新增的 AFH 方法背景，放在原有讨论之前，帮助读者先理解 AFH 核响应的理论逻辑和计算流程。**本节之后的原有讨论全文保留**；不删减原有段落、表格、物理判断、数值结果或研究计划。为保证 GitHub Markdown 的数学显示，原文中已有的数学内容只统一公式定界符，不改写公式本身。

## A. AFH 方法的目标：把粒子物理与核结构分开处理

AFH（Anand–Fitzpatrick–Haxton）方法是暗物质直接探测中一套系统处理低能暗物质—核子相互作用及原子核响应的框架。它解决的核心问题是：给定一种暗物质与单个核子的低能相互作用，如何把它可靠地嵌入由许多质子和中子组成的原子核，并计算整个核的散射响应。

传统的 SI/SD 描述对部分相互作用很有用，但一般低能相互作用还可能依赖核子自旋、动量转移、相对速度、轨道运动以及自旋—轨道结构。不同结构在原子核中的矩阵元不同，不能全部由一个统一的核形状因子代表。

AFH 方法将问题拆成两个层次：

1. **粒子物理层：** 从暗物质—核子相互作用出发，得到单核子非相对论算符及其系数。
2. **核结构层：** 将单核子算符嵌入原子核，利用核波函数和单体密度矩阵计算相应多极矩阵元，并构造核响应函数。

因此，其基本逻辑是

$$
\boxed{
\text{暗物质—核子相互作用}
\longrightarrow
\text{单核子非相对论算符}
\longrightarrow
\text{原子核多极算符}
\longrightarrow
\text{AFH 核响应}
}
$$

AFH 核响应本身不是某个具体 UV 模型的截面。它提供的是核结构部分；具体模型仍需提供相应的单核子相互作用系数，才能形成物理响应组合。

## B. 单核子层：低能非相对论有效算符

直接探测中的暗物质速度通常远小于光速，核反冲动量也处于低能区间。因此，可以在暗物质和核子作为低能自由度的层面，对相对论振幅进行非相对论展开。

这一展开不意味着核子内部的夸克、胶子 QCD 动力学是非相对论的。核子内部结构已经被吸收到核子矩阵元、形状因子或有效耦合中；AFH 的非相对论展开针对的是低能暗物质与核子自由度。

对于标准弹性两体运动学，常用的构件包括动量转移、相对速度以及暗物质和核子的自旋：

$$
\mathbf q,\qquad
\mathbf v^\perp,\qquad
\mathbf S_\chi,\qquad
\mathbf S_N.
$$

在常用约定下，

$$
\mathbf v^\perp
=
\mathbf v+\frac{\mathbf q}{2\mu_N},
\qquad
\mathbf v^\perp\cdot\mathbf q=0,
$$

其中 $\mu_N$ 是暗物质—核子的约化质量。这里的 $\mathbf v^\perp$ 关系属于弹性 $2\to2$ 单核子运动学；它用于说明 AFH 标准非相对论 EFT 的构造背景，不应未经推导就当作额外辐射过程的完整运动学关系。

对于自旋为 $1/2$ 的暗物质和核子，常用非相对论算符包括

$$
\mathcal O_1=1_\chi 1_N,
$$

$$
\mathcal O_4=\mathbf S_\chi\cdot\mathbf S_N,
$$

$$
\mathcal O_5
=
i\mathbf S_\chi\cdot
\left(
\frac{\mathbf q}{m_N}\times\mathbf v^\perp
\right),
$$

$$
\mathcal O_6
=
\left(
\mathbf S_\chi\cdot\frac{\mathbf q}{m_N}
\right)
\left(
\mathbf S_N\cdot\frac{\mathbf q}{m_N}
\right).
$$

一般单核子相互作用可以组织为

$$
\mathcal M_{\chi N}
=
\sum_i c_i^N(q^2)
\langle\mathcal O_i\rangle,
$$

其中 $c_i^N$ 是单核子层面的有效系数。它们可以依赖动量转移；是否可以近似为常数取决于具体模型和所研究的动量范围。

## C. 从单核子算符到原子核多体算符

实际靶标是原子核，而不是自由核子。在单体核流近似下，单核子算符需要对原子核中的所有核子求和。对最简单的核子密度算符，

$$
\boxed{
\hat\rho_A(\mathbf q_A)
=
\sum_{a=1}^{A}
e^{i\mathbf q_A\cdot\mathbf r_a}
}
$$

其中 $\mathbf r_a$ 是第 $a$ 个核子相对于原子核质心的坐标，$\mathbf q_A$ 是原子核整体获得的空间动量转移。

在零动量极限，

$$
\hat\rho_A(\mathbf 0)=A.
$$

因此，等质子、等中子耦合时，领先阶相干振幅正比于 $A$，其平方正比于 $A^2$。在有限动量转移下，各核子的空间相位不同，必须计算原子核的有限动量多体矩阵元；这正是核响应函数所描述的内容。

更一般地，单体核流可以写成

$$
\hat J_A^\mu(\mathbf q_A)
=
\sum_{a=1}^{A}
e^{i\mathbf q_A\cdot\mathbf r_a}
\hat j_a^\mu,
$$

其中 $\hat j_a^\mu$ 是作用在第 $a$ 个核子上的单核子流算符。不同的时间分量、空间分量、自旋结构和动量结构，会投影到不同的核多极算符。

## D. 多极展开：AFH 核算符从哪里来？

原子核态具有确定的总角动量和宇称。为了利用这些对称性计算核矩阵元，AFH 将平面波因子及其伴随的自旋、轨道和空间流结构展开为球对称多极算符。

平面波的标准展开为

$$
\boxed{
e^{i\mathbf q\cdot\mathbf r}
=
4\pi
\sum_{JM}
i^J
j_J(qr)
Y_{JM}^{*}(\widehat{\mathbf q})
Y_{JM}(\widehat{\mathbf r})
}
$$

其中 $j_J$ 是球贝塞尔函数，$Y_{JM}$ 是球谐函数，$J,M$ 是多极角动量指标。

质量/核子密度型多极算符具有

$$
M_{JM}(q\mathbf r)
\sim
j_J(qr)Y_{JM}(\widehat{\mathbf r})
$$

的基本结构。对流电流、核子自旋和自旋—轨道结构则需要构造相应的纵向、横向矢量球谐多极算符。

AFH 的标准核响应基底由六类基本响应组成：

| 核响应 | 主要核结构 | 物理来源概述 |
| --- | --- | --- |
| $M$ | 质量/核子密度响应 | 相干核子密度或矢量电荷 |
| $\Sigma''$ | 纵向自旋响应 | 核子自旋沿动量方向的分量 |
| $\Sigma'$ | 横向自旋响应 | 核子自旋的横向分量 |
| $\Delta$ | 轨道角动量响应 | 核子对流和轨道运动结构 |
| $\Phi''$ | 自旋—轨道响应 | 核子自旋与轨道运动的耦合 |
| $\widetilde\Phi'$ | 另一种自旋—轨道相关响应 | 相应的横向自旋—动量多极结构 |

此外，还有重要的干涉响应，例如

$$
M-\Phi'',
\qquad
\Sigma'-\Delta.
$$

干涉响应不是新的独立对角响应，也不能通过把两个对角响应简单相加来代替。其数值取决于对应核多极矩阵元之间的相对符号、相位和归一化。

## E. 核结构输入：壳模型与单体密度矩阵

AFH DMFormFactor 并不是在每次调用核响应时从头求解原子核多体薛定谔方程。核结构信息通过单体密度矩阵（one-body density matrix elements, OBDME）提供。核结构模型给出单粒子轨道及其占据、关联信息，AFH 程序据此计算单体多极算符在核态之间的矩阵元。

示意地，核多极算符的约化矩阵元可以写为

$$
\boxed{
\begin{aligned}
\langle J_A\|
\hat O_{J;\tau}(q)
\|J_A\rangle
=
\sum_{\alpha,\beta}
\rho_{J;\tau}(\alpha,\beta)
\langle\alpha\|
\hat O_{J;\tau}(q)
\|\beta\rangle .
\end{aligned}
}
$$

其中 $\alpha,\beta$ 标记单粒子轨道，$\rho_{J;\tau}$ 是相应的单体约化密度矩阵元，右侧的单粒子约化矩阵元由具体多极算符计算得到。

DMFormFactor v6.0 使用谐振子（harmonic oscillator, HO）单粒子基底。单粒子轨道可用 $|nljm\rangle$ 标记。有限动量矩阵元包含球贝塞尔函数与 HO 径向波函数的积分，例如

$$
I_{n'l',nl}^{(J)}(q)
=
\int_0^\infty dr\,r^2
R_{n'l'}(r)
j_J(qr)
R_{nl}(r).
$$

角动量耦合由相应的 Wigner $3j$、$6j$ 和 $9j$ 符号处理。由此，AFH 响应包含所采用核结构输入所决定的有限动量多体信息，而不是简单地给点核结果乘上一个通用经验函数。

## F. AFH 核响应函数的含义

对某一类核多极算符 $X_{J;\tau}$，核响应函数的结构可以概括为

$$
W_X^{\tau\tau'}(q_A)
\sim
\sum_J
\langle J_A\|X_{J;\tau}(q_A)\|J_A\rangle
\langle J_A\|X_{J;\tau'}(q_A)\|J_A\rangle^*.
$$

不同响应之间的干涉项则具有

$$
W_{XY}^{\tau\tau'}(q_A)
\sim
\sum_J
\langle J_A\|X_{J;\tau}(q_A)\|J_A\rangle
\langle J_A\|Y_{J;\tau'}(q_A)\|J_A\rangle^*.
$$

上式只展示响应函数的结构；具体角动量求和、初态自旋平均、归一化和相位约定，应以 AFH 论文及所使用的 DMFormFactor v6.0 程序定义为准。

因此，$W_X$ 是核结构量，不是截面。物理截面需要由单核子相互作用系数形成相应的粒子物理响应，再与核响应及允许的干涉项组合。**不能把 AFH 输出的全部 $W_X$ 不带权重地直接相加。**

## G. 同位旋分解与质子、中子响应

AFH 可以分别处理质子和中子耦合，也可以使用等标量、等矢量基底。采用

$$
t^0=1,\qquad t^1=\tau_3
$$

的约定时，质子/中子系数与同位旋系数之间的关系为

$$
\boxed{
c^0=\frac{c^p+c^n}{2},
\qquad
c^1=\frac{c^p-c^n}{2}.
}
$$

因此：

- 当 $c^p=c^n$ 时，等矢量系数为零，领先阶密度响应为纯等标量；
- 当 $c^p\ne c^n$ 时，需要保留等标量、等矢量及相应的混合响应；
- 对一般相互作用，不能未经核子流匹配就假设质子和中子的耦合相同。

同位旋分量是核响应计算的重要索引。对每个响应，程序可以分别给出不同 $\tau,\tau'$ 组合；具体模型再决定这些分量如何加权。

## H. DMFormFactor v6.0 与氙核响应输入

本项目使用的 AFH Mathematica 程序为 `dmformfactor-V6.m`。程序的核响应接口为

```Mathematica
ResponseNuclear[y, i, tau1, tau2]
```

其中：

- `y` 是无量纲动量变量；
- `i` 是核响应通道编号；
- `tau1`、`tau2` 是同位旋指标。

本项目采用的 v6.0 响应通道对应关系为：

| 程序编号 | 核响应 |
| ---: | --- |
| 1 | $M$ |
| 2 | $\Sigma''$ |
| 3 | $\Sigma'$ |
| 4 | $\Phi''$ |
| 5 | $\widetilde\Phi'$ |
| 6 | $\Delta$ |
| 7 | $M-\Phi''$ |
| 8 | $\Sigma'-\Delta$ |

AFH 使用的无量纲动量变量为

$$
\boxed{
y_A=\left(\frac{Q_A b_A}{2}\right)^2,
\qquad Q_A=|\mathbf q_A|.
}
$$

在自然单位下可直接使用上式。如果 $Q_A$ 以 GeV 表示而 $b_A$ 以 fm 表示，则应写为

$$
y_A=
\left(
\frac{Q_A[\mathrm{GeV}]\,b_A[\mathrm{fm}]}
{2\,\hbar c[\mathrm{GeV\,fm}]}
\right)^2.
$$

本项目使用的 v6.0 默认谐振子长度约定为

$$
b_A[\mathrm{fm}]
=
\sqrt{
\frac{41.467}
{45A^{-1/3}-25A^{-2/3}}
}.
$$

谐振子长度、默认密度矩阵、响应编号和程序版本应随每一份核响应数据一并记录，确保结果可追溯。

## I. AFH 方法的适用范围与边界

AFH 核响应计算的完整性必须相对于明确的核流近似来定义。使用 v6.0 默认单体密度矩阵和标准核算符基底，得到的是该核结构输入和单体核流框架下的核响应。

因此需要区分：

1. **AFH 核响应数据库完整：** 所需的标准核响应通道、同位旋分量和同位素输入均已计算并通过数值验收。
2. **给定模型的核流匹配完整：** 已将模型的单核子流投影到 AFH 核算符，并确定所有相关响应和干涉项的系数。
3. **更完整的核物理描述：** 还需另外评估两体交换流、超出当前核结构模型的效应及相应理论不确定度；这些不会因为调用 AFH 程序而自动包含。

AFH 标准非相对论算符基底的构造背景主要针对低能弹性暗物质—核子散射。对于本文所讨论的额外辐射过程，AFH 可以提供核结构侧的多极响应，但不能因此把完整辐射过程的运动学无条件等同于弹性两体散射。必须先确定实际核子流，再完成核算符投影。

## J. 本文后续讨论的阅读路线

理解 AFH 后，后续内容应按以下逻辑阅读：

1. 先明确当前模型在单核子层面产生什么样的矢量流；
2. 再将该核子流约化为非相对论核算符；
3. 判断这些核算符对应哪些 AFH 多极响应；
4. 检查对角响应、干涉响应、同位旋系数和归一化；
5. 最后使用 AFH v6.0 的氙核结构输入计算相应响应。

这条路线的关键是区分**核结构响应**与**具体模型的响应系数**：前者由 AFH 核结构计算提供，后者由当前相互作用模型和核子流匹配决定。

---

# 原有讨论正文（完整保留）

以下正文承接原始完整文档。除将原有数学公式的定界符统一为 GitHub Markdown 支持的 `$...$` 和 `$$...$$` 外，原有文字、公式内容、表格、数值、结论、章节顺序和研究记录均予以保留。

AFH（Anand–Fitzpatrick–Haxton）文章之所以能够把暗物质与核子的相互作用展开成一组**非相对论有效算符（Non-relativistic EFT operators）**，核心原因是：


**在直接探测实验所涉及的低能、低动量转移条件下，暗物质和原子核内部核子的运动都可以近似看作非相对论运动。因此，完整的相对论散射振幅可以按照低能运动学变量进行系统展开，并用一组满足对称性要求的非相对论算符表示。**

$$
R_A(E_R)=\frac{4\pi}{2J_A+1}W_M^{00}(y_A),
$$

**到底包含了什么效应，为什么我们使用点状原子核得到的散射振幅乘上核响应函数得到的结果和把暗物质与核子展开为有效非相对论性相互作用得到的结果是一致的？我看不出来这之间是如何联系的**


这不是一种额外的相互作用假设，而是一种有效场论展开方法。


不过，这里有一个对我们目前的 LZ 三体散射计算特别重要的问题：

> AFH 的非相对论算符基底主要针对暗物质与核子的 $2\to2$ 弹性散射。我们的过程是
>
> $$
> \chi_1+A\longrightarrow\chi_1+A+s,
> $$
>
> 不能不加区分地把整个三体振幅直接写成 AFH 的 15 个算符。

需要区分两个层次：

1. **核子相互作用顶点的非相对论展开**：可以借鉴 AFH。
2. **完整的三体散射振幅的非相对论展开**：必须额外保留末态标量的动量和三体运动学。

下面从理论基础开始解释。

## **一、为什么可以进行非相对论展开？**

直接探测实验中，银河系晕暗物质的典型速度约为

$$
v_\chi\sim 10^{-3}c.
$$

原子核反冲能量通常在 keV 量级，而暗物质质量通常远大于其动能。


因此：

$$
\frac{|\mathbf p_\chi|}{m_\chi}\sim 10^{-3},
$$

暗物质处于非相对论区域。


对于核子，虽然核子内部存在强相互作用和相对论性的夸克、胶子动力学，但在核子自由度层面，低能核子之间的相互作用也可以采用非相对论有效理论描述。


这里要特别注意：


**非相对论展开并不意味着核子内部的 QCD 动力学是非相对论的。** 我们是把核子作为低能有效自由度，而不是直接对夸克和胶子做速度展开。


因此，暗物质与核子的散射振幅可以写成

$$
\begin{aligned}
\mathcal M_{\chi N}
&=
\mathcal M_{\chi N}
\left(
\mathbf q,\mathbf v,\mathbf S_\chi,\mathbf S_N
\right),
\end{aligned}
$$

其中：

- $\mathbf q$：核子的三维动量转移；
- $\mathbf v$：相对速度；
- $\mathbf S_\chi$：暗物质自旋；
- $\mathbf S_N$：核子自旋。

然后按照动量和速度的阶数展开。

## **二、为什么最后只需要有限个算符？**

关键在于：并不是任意函数都可以出现在散射振幅中。振幅必须满足一系列对称性条件。

### **1. Galilean 不变性**

在非相对论极限下，低能散射过程应当满足 Galilean 变换不变性。


因此，不能随意使用绝对速度，而应该使用暗物质与核子的相对速度：

$$
\mathbf v=\mathbf v_\chi-\mathbf v_N.
$$

同时引入动量转移：

$$
\mathbf q.
$$

对于弹性 $2\to2$ 散射，能量守恒给出

$$
\mathbf v\cdot\mathbf q + \frac{q^2}{2\mu_N}=0,
$$

其中

$$
\mu_N=\frac{m_\chi m_N}{m_\chi+m_N}
$$

是暗物质与核子的约化质量。


于是定义垂直速度：

$$
\boxed{ \mathbf v^\perp = \mathbf v+\frac{\mathbf q}{2\mu_N} }
$$

这里采用的动量转移约定是 $\mathbf q=\mathbf p_\chi'-\mathbf p_\chi$。如果采用相反的动量转移约定，公式中的正负号也相应改变。


它满足：

$$
\boxed{ \mathbf v^\perp\cdot\mathbf q=0 }
$$

这非常重要：$\mathbf v^\perp$ 和 $\mathbf q$ 是两个独立的运动学方向。

### **2. 旋转不变性**

散射振幅必须是旋转标量。


对于自旋为 $1/2$ 的暗物质和核子，可以使用：

$$
\mathbf S_\chi,\qquad \mathbf S_N,\qquad \mathbf q,\qquad \mathbf v^\perp.
$$

通过这些量构造点乘、叉乘和张量组合，就可以得到旋转不变的算符。

### **3. 宇称、时间反演与厄米性**

还必须要求算符满足相应的宇称、时间反演和厄米性条件。


例如，单独的 $\mathbf q$ 在交换初末态时改变符号，因此常常需要引入 $i\mathbf q$，使相应的动量空间算符具有正确的厄米性质。


这些条件共同限制了允许出现的算符。

### **4. 按动量和速度阶数截断**

最后，按照

$$
\frac{|\mathbf q|}{m_N}\ll1, \qquad v\ll1
$$

进行展开，保留指定阶数的项。


在通常的自旋 $1/2$ 暗物质框架下，就得到大家熟悉的非相对论算符基底。

## **三、AFH 的非相对论算符具体是什么？**

常用的算符基底由以下结构组成。

| 算符 | 数学表达式 | 主要物理含义 |
| --- | --- | --- |
| $\mathcal O_1$ | $1_\chi 1_N$ | 自旋无关相互作用 |
| $\mathcal O_4$ | $\mathbf S_\chi\cdot\mathbf S_N$ | 自旋－自旋相互作用 |
| $\mathcal O_5$ | $i\mathbf S_\chi\cdot(\frac{\mathbf q}{m_N}\times\mathbf v^\perp)$ | 动量与速度耦合 |
| $\mathcal O_6$ | $(\mathbf S_\chi\cdot\frac{\mathbf q}{m_N})(\mathbf S_N\cdot\frac{\mathbf q}{m_N})$ | 双自旋动量耦合 |
| $\mathcal O_7$ | $\mathbf S_N\cdot\mathbf v^\perp$ | 核子自旋－速度耦合 |
| $\mathcal O_8$ | $\mathbf S_\chi\cdot\mathbf v^\perp$ | 暗物质自旋－速度耦合 |
| $\mathcal O_9$ | $i\mathbf S_\chi\cdot(\mathbf S_N\times\frac{\mathbf q}{m_N})$ | 自旋与动量耦合 |
| $\mathcal O_{10}$ | $i\mathbf S_N\cdot\frac{\mathbf q}{m_N}$ | 核子自旋－动量耦合 |
| $\mathcal O_{11}$ | $i\mathbf S_\chi\cdot\frac{\mathbf q}{m_N}$ | 暗物质自旋－动量耦合 |

这只是列出一些有代表性的算符，并不是完整列表。


完整的常用基底还包含其他自旋、动量和速度的组合。


因此，暗物质与核子的相互作用可以写成

$$
\boxed{ \mathcal M_{\chi N} = \sum_i c_i^N(q^2)\, \langle\mathcal O_i\rangle }
$$

这里：

- $\mathcal O_i$ 是非相对论算符；
- $c_i^N$ 是对应的 Wilson 系数；
- $q^2$ 表示动量转移依赖。

注意，系数不一定是常数。例如轻媒介子的传播子可以保留在 $c_i^N(q^2)$ 中。


也就是说，非相对论展开不等于一定要把媒介子传播子近似为常数。

## **四、AFH 是如何从核子算符走到原子核响应的？**

这是 AFH 工作最重要的部分之一。


暗物质实际上并不是与一个自由核子散射，而是与一个包含 $A$ 个核子的原子核散射。


AFH 采用单体流近似，将暗物质－原子核相互作用写成对所有核子的求和：

$$
\boxed{
\begin{aligned}
\hat H_{\chi A}
&=
\sum_{i=1}^{A}
\sum_{\tau=0,1}
\sum_j
c_j^\tau \mathcal O_j^{(i)}t_i^\tau
\end{aligned}
}
$$

其中：

- $i$ 表示第 $i$ 个核子；
- $j$ 表示不同的非相对论算符；
- $\tau=0,1$ 表示同位旋的等标量和等矢量分量；
- $t_i^\tau$ 是对应的同位旋算符。

然后计算核矩阵元：

$$
\langle J_A'| \hat H_{\chi A} |J_A\rangle.
$$

通过多极展开和核结构计算，可以把核子层面的算符组织成有限种核响应函数。


AFH 得到的主要核响应包括：

$$
\boxed{
\begin{gathered}
M,\quad \Sigma',\quad \Sigma'',\\
\Delta,\quad \Phi'',\quad \widetilde\Phi''
\end{gathered}
}
$$

它们分别反映不同的核结构：

| 核响应 | 主要物理内容 |
| --- | --- |
| $M$ | 核子的相干质量或电荷密度响应 |
| $\Sigma'$ | 横向自旋响应 |
| $\Sigma''$ | 纵向自旋响应 |
| $\Delta$ | 核子的轨道角动量响应 |
| $\Phi''$ | 自旋－轨道相关响应 |
| $\widetilde\Phi''$ | 与自旋－轨道结构相关的另一种响应 |

因此，AFH 实际上完成了两个步骤：

$$
\boxed{
\begin{gathered}
\text{暗物质－核子相互作用}\\
\longrightarrow \text{非相对论算符}\\
\longrightarrow \text{原子核响应函数}
\end{gathered}
}
$$

这使得粒子物理部分和核结构部分能够相对独立地处理。


AFH 2014 年的文章正是通过这种方式，把一般的弹性 WIMP－核子相互作用嵌入原子核，并构造因子化的 WIMP 和核响应函数。

APS Journals+1


## **五、这和我们目前研究的三体散射有什么关系？**

现在回到我们的过程：

$$
\boxed{ \chi_1+A\longrightarrow\chi_1+A+s }
$$

这里必须区分两件事。

### **1. 核子顶点仍然可以使用非相对论展开**

假设媒介子 $V$ 与原子核之间通过矢量流相互作用。


那么振幅可以示意性地写成

$$
\boxed{
\begin{aligned}
\mathcal M_3
&=
J_A^\mu(q_A)D_{\mu\nu}(q_A)
\\
&\quad
\mathcal T_{\chi,s}^{\nu}(p_\chi,p_\chi',k_s)
\end{aligned}
}
$$

其中：

- $J_A^\mu(q_A)$：原子核的矢量流；
- $D_{\mu\nu}(q_A)$：媒介子传播子；
- $\mathcal T_{\chi,s}^{\nu}$：暗物质发射标量后的有效流；
- $k_s$：末态标量的四动量。

注意，虽然暗物质发射了一个标量，但是原子核仍然只通过媒介子与暗物质发生相互作用。


因此，原子核一侧的流仍然可以进行非相对论展开。


例如矢量流的时间分量在非相对论极限下主要对应核子密度：

$$
J_N^0 \simeq 2m_N\,\xi_N'^\dagger\xi_N.
$$

把它嵌入原子核之后，就得到相干的核子密度响应。


这正是 AFH 中 $M$ 型核响应的主要来源。


所以，对于我们的矢量相互作用，如果领先阶由核子矢量电荷主导，那么可以使用 AFH 的质量响应：

$$
W_M^{\tau\tau'}(q_A^2).
$$

这里需要强调：使用的是核子的非相对论流及其对应的核响应，而不是直接假定整个三体振幅就是某个 AFH 算符。

### **2. 但是，完整的三体振幅不能直接使用标准 AFH 算符基底**

这是最重要的区别。


对于普通弹性散射：

$$
\chi+N\longrightarrow\chi+N,
$$

动量守恒为

$$
p_\chi+p_N=p_\chi'+p_N'.
$$

只有一个独立的动量转移。


但是我们的三体过程满足：

$$
p_\chi+P_A = p_\chi'+P_A'+k_s.
$$

因此定义原子核动量转移：

$$
\boxed{
\begin{aligned}
\mathbf q_A
&=
\mathbf P_A'-\mathbf P_A
\\
&=
\mathbf p_\chi-\mathbf p_\chi'-\mathbf k_s
\end{aligned}
}
$$

这意味着：

$$
\boxed{ \mathbf q_A\neq \mathbf p_\chi-\mathbf p_\chi' }
$$

一般情况下，两者相差末态标量的动量。


这就是为什么我们之前专门区分：

| 变量 | 物理意义 | 主要用途 |
| --- | --- | --- |
| $\mathbf q_A$ | 原子核初末态动量差 | AFH 核响应 |
| $\mathbf q_\chi$ | 暗物质初末态动量差 | 暗物质运动学 |
| $\mathbf k_s$ | 末态标量动量 | 三体相空间、传播子 |
| $E_R$ | 原子核反冲能量 | 实验可观测量 |

对于初始静止的原子核：

$$
\boxed{ q_A=\sqrt{2m_AE_R} }
$$

这个关系在三体散射中依然成立，因为它来自原子核自身的非相对论反冲运动。


但是不能因此把 $q_A$ 替换成暗物质的初末态动量差。

### **3. 三体过程中的 $\mathbf v^\perp$ 也需要重新处理**

AFH 标准定义：

$$
\mathbf v^\perp = \mathbf v+\frac{\mathbf q}{2\mu_N}
$$

依赖于弹性 $2\to2$ 散射的能量守恒。


现在有一个额外的末态标量：

$$
E_\chi+E_A = E_\chi'+E_A'+\omega_s.
$$

因此，原来用于推导

$$
\mathbf v^\perp\cdot\mathbf q=0
$$

的两体运动学关系不再直接成立。


如果仍然使用标准的 AFH $\mathbf v^\perp$，就可能遗漏标量发射带来的运动学贡献。


正确的做法是：

- 保留 $k_s$；
- 从完整三体振幅出发；
- 对暗物质外线自旋结构进行非相对论约化；
- 根据三体能量、动量守恒构造相应的运动学变量；
- 不预先假设标准 AFH 算符基底已经完备。

此外，我们的中间态 $\chi_2$ 存在接近共振的可能性，因此内部传播子也必须保留相应的 Breit–Wigner 结构，不能简单地用低阶多项式替代。

## **六、对我们 LZ 计算，究竟应该如何使用 AFH？**

我建议采用下面的理论路线。

## **我们的三体散射计算框架**

**第一步：完整相对论三体振幅**


$$
\mathcal M_3(\chi_1,A\to\chi_1,A,s)
$$


保留 χ₂ 内部传播子、标量发射顶点和媒介子传播子

**第二步：分离暗物质流与核子流**


$$
\mathcal M_3=J_A^\mu D_{\mu\nu}\mathcal T_{\chi,s}^\nu
$$


明确区分 qA、qχ 和 ks

**第三步：核子流非相对论约化**


$$
J_N^\mu\longrightarrow\text{核子非相对论算符}
$$


利用 AFH 的核子流与核结构框架

**第四步：AFH 核响应**


$$
W_M(q_A^2),\ W_{\Sigma'}(q_A^2),\ldots
$$


根据实际耦合结构选取所需核响应

**第五步：完整三体相空间积分**


$$
\displaystyle \frac{d\sigma_3}{dE_R}
$$


保留标量的三体相空间和能量守恒条件

这里还有一个重要的技术区别：


**AFH 的核响应函数可以继续作为核结构模块使用，但 AFH 原来的完整弹性散射截面公式不能不经推导就直接套到三体过程。**


特别是我们的 $W_M$ 响应：

$$
R_A(E_R) = \frac{4\pi}{2J_A+1} W_M^{00}(y_A),
$$

其中

$$
y_A=\frac{b_A^2m_AE_R}{2} =\frac{b_A^2q_A^2}{4},
$$

仍然可以用于描述相应的核子密度响应，但三体振幅中的粒子物理部分必须重新计算。


另外，AFH 的 $W_M(y_A)$ 是有限动量转移下的核结构结果，不能再随意对整个核响应做 $q_A\to0$ 的展开。对于氙核，这一点尤其重要。

arXiv+2

## **七、最终结论：二体和三体应该怎么区分？**

| 比较项目 | AFH 标准二体散射 | 我们的三体散射 |
| --- | --- | --- |
| 散射过程 | $\chi+N\to\chi+N$ | $\chi_1+A\to\chi_1+A+s$ |
| 动量转移 | 一个独立的两体转移量 | 核反冲与暗物质动量差不同 |
| 末态粒子 | 暗物质、核子 | 暗物质、原子核、标量 |
| $\mathbf v^\perp$ | 标准弹性定义 | 需要重新推导 |
| 非相对论算符 | 标准 AFH 基底 | 可能需要包含 $k_s$ 的扩展结构 |
| 核响应 | AFH 核响应 | 满足相同核流条件时可以沿用 |
| 相空间 | 二体相空间 | 三体相空间 |

**我认为我们目前最合理的选择是：保留完整的三体粒子物理振幅，只把 AFH 用于原子核结构部分。**


这样既不会丢失标量发射和 $\chi_2$ 共振带来的物理信息，也能充分利用 AFH 已经计算好的氙核响应函数。


这也是我们需要坚持区分 $q_A$、$q_\chi$ 和 $k_s$ 的根本原因。你这个问题实际上问到了 AFH 方法最核心的地方：**为什么一个在原子核层面直接写出的散射振幅，可以和先在单个核子层面构造非相对论有效相互作用、再把它嵌入原子核的计算方法得到相同结果？**


关键不是两种方法碰巧给出了相同数值，而是：


**在相同的单核子相互作用、相同的单体流近似和相同的核态下，它们计算的是同一个矩阵元，只是把计算分成了不同的步骤。**


我先给出最重要的对应关系：

$$
\boxed{
\begin{aligned}
&\underbrace{\text{点状原子核的粒子物理振幅}}_{\text{粒子物理}}
\\
&\quad\times
\underbrace{\text{核密度响应}}_{\text{核结构}}
\\
&=
\underbrace{\text{单核子相互作用嵌入原子核后的矩阵元}}_{\text{AFH方法}}
\end{aligned}
}
$$

这个等式有适用条件，特别是对于我们目前考虑的矢量电荷主导的相互作用，它成立得非常直接。但它不是对任意非相对论算符都成立的普遍等式。


下面我从最简单的一个核子开始，一直推导到 AFH 的 $W_M^{00}$，再解释它和我们的三体振幅如何对应。

## **一、先不考虑 AFH：假设暗物质只与一个核子发生散射**

考虑一个简单的自旋无关相互作用：

$$
\mathcal L_{\rm int} = C\,\bar\chi\gamma^\mu\chi\, \bar N\gamma_\mu N.
$$

这里 $C$ 可以包含耦合常数和媒介子传播子的相关因子。


在非相对论极限下，矢量流的时间分量占主导：

$$
\bar u_\chi'\gamma^0u_\chi \simeq 2m_\chi,
$$

$$
\bar u_N'\gamma^0u_N \simeq 2m_N.
$$

因此振幅的领先阶是

$$
\mathcal M_{\chi N} \simeq 4C m_\chi m_N.
$$

如果采用非相对论归一化，去掉相应的外线归一化因子，就得到

$$
\boxed{ \mathcal O_1=1_\chi 1_N }
$$

这就是 AFH 非相对论算符中的自旋无关算符。


现在问题来了：


如果靶标不是一个核子，而是一个包含 $A$ 个核子的原子核，该怎么办？


答案就是：把单核子算符作用到原子核的每一个核子上，然后求和。

$$
\boxed{ \hat{\mathcal O}_A = c_1\sum_{i=1}^{A} e^{i\mathbf q_A\cdot\mathbf r_i} }
$$

这里：

- $c_1$ 是单核子的有效耦合；
- $\mathbf r_i$ 是第 $i$ 个核子相对于原子核质心的坐标；
- $\mathbf q_A$ 是原子核获得的动量转移。

注意这个指数因子是非常关键的。


它表示暗物质把动量 $\mathbf q_A$ 传递给原子核时，究竟是由哪个位置的核子参与相互作用。


因此，原子核的散射矩阵元是

$$
\boxed{
\begin{aligned}
\mathcal M_A
&=
c_1\left\langle A_f\left|
\\
&\quad
\sum_{i=1}^{A}e^{i\mathbf q_A\cdot\mathbf r_i}
\right|A_i\right\rangle
\end{aligned}
}
$$

这就是从单核子相互作用走到原子核相互作用的最基本公式。


它还没有使用 AFH 的任何特殊技巧。

## **二、先把原子核看成一个点：为什么会得到 $A^2$？**

假设原子核有 $A$ 个核子，并且暗物质对质子和中子的耦合完全相同。


如果动量转移足够小，使得

$$
|\mathbf q_A\cdot\mathbf r_i|\ll1,
$$

那么可以展开：

$$
e^{i\mathbf q_A\cdot\mathbf r_i} \simeq 1.
$$

因此：

$$
\hat{\mathcal O}_A \simeq c_1\sum_{i=1}^{A}1 =Ac_1.
$$

原子核散射振幅：

$$
\boxed{ \mathcal M_A= A\mathcal M_{\chi N} }
$$

散射概率正比于振幅平方：

$$
\boxed{ |\mathcal M_A|^2 =A^2|\mathcal M_{\chi N}|^2 }
$$

这就是自旋无关散射中的相干增强（coherent enhancement）。


注意，这里不是把 $A$ 个核子的散射截面直接相加：

$$
\sigma_A\neq A\sigma_N.
$$

而是先将所有核子的散射振幅相加，再平方：

$$
\left|\sum_{i=1}^A\mathcal M_i\right|^2.
$$

这两者的区别非常重要。

**两种不同的求和方式**

相干散射

$$
\left|\sum_i\mathcal M_i\right|^2
$$

# $A^2$

振幅相加后平方

非相干散射

$$
\sum_i|\mathcal M_i|^2
$$

# $A$

概率直接相加

对于长波长、相同耦合的核子密度相互作用，前者是正确的领先阶描述。

因此，当我们把原子核近似成一个点状粒子时，实际上已经把所有核子的相干贡献包含进了原子核的有效耦合：

$$
g_A=Ag_N.
$$

这就是点状原子核振幅中出现 $A$ 的原因。


但是，这个近似有一个问题：它假设所有核子都处于同一个相位。


实际并非如此。

## **三、如果动量转移不够小，怎么办？**

现在恢复之前忽略的指数因子：

$$
\begin{aligned}
\mathcal M_A
&=
c_1
\left\langle A\left|
\\
&\quad
\sum_{i=1}^{A}e^{i\mathbf q_A\cdot\mathbf r_i}
\right|A\right\rangle.
\end{aligned}
$$

把指数展开：

$$
\begin{aligned}
e^{i\mathbf q_A\cdot\mathbf r_i}
&=
1
\\
&\quad
+i\mathbf q_A\cdot\mathbf r_i
\\
&\quad
-\frac{1}{2}(\mathbf q_A\cdot\mathbf r_i)^2
\\
&\quad
+\cdots.
\end{aligned}
$$

你可以看到：

- 不同核子的位置 $\mathbf r_i$ 不一样；
- 不同位置对应不同的散射相位；
- 核子之间的振幅不再完全同相；
- 相干增强会随着动量转移增大而受到抑制。

因此，我们定义一个原子核形状因子：

$$
\boxed{
\begin{aligned}
F_A(\mathbf q_A)
&=
\frac{1}{A}
\left\langle A\left|
\\
&\quad
\sum_{i=1}^{A}e^{i\mathbf q_A\cdot\mathbf r_i}
\right|A\right\rangle
\end{aligned}
}
$$

这里假设所有核子的耦合相同。


显然：

$$
F_A(0)=1.
$$

于是：

$$
\boxed{ \mathcal M_A = Ac_1F_A(q_A) }
$$

平方后：

$$
\boxed{ |\mathcal M_A|^2 = A^2|c_1|^2|F_A(q_A)|^2 }
$$

这就是通常所说的有限核尺寸修正。

[PPT - ###  Understanding Nuclear Sizes and Scattering: A Comprehensive Analysis  ### PowerPoint Presentation - ID:6629766](https://images.openai.com/static-rsc-4/g0LLS-_Ya7-Vhl06gYT4-D6-1NfozIQ9Xta0boiyTyS8dgTaTuTliOG25CK2eQvBMmUkQCqTOlTuzxQ3xvT5xKuRXQR92azWjhIn1KtJz7hJZ2T_AZdoEJVPimtLXDQORkWdekBE6097tyqjofnaUpK6gwAxSR0VkTic2MR8r6E?purpose=inline)

[slideserve.com](https://www.slideserve.com/savannah-gomez/sizes?utm_source=chatgpt.com)

这里需要注意：


$F_A(q)$ 不是额外引入的一种新相互作用，而是原子核内部核子空间分布造成的结果。


换句话说：


**点状原子核近似忽略了核子的空间分布，而核响应函数恰好把这个空间分布重新放回计算中。**


但是，AFH 的 $W_M$ 比通常简单使用的一个球形核密度形状因子更一般。

## **四、AFH 是怎样把这个形状因子变成 $W_M^{00}$ 的？**

这一步是整个问题的关键。


我们刚才得到：

$$
\hat{\mathcal O}_A(\mathbf q_A) = \sum_{i=1}^{A} e^{i\mathbf q_A\cdot\mathbf r_i}.
$$

直接计算这个指数算符的原子核矩阵元并不方便。


AFH 使用球谐函数和球贝塞尔函数进行多极展开：

$$
\begin{aligned}
e^{i\mathbf q\cdot\mathbf r}
&=
4\pi\sum_{JM}i^Jj_J(qr)
\\
&\quad
Y_{JM}^{*}(\hat{\mathbf q})Y_{JM}(\hat{\mathbf r}).
\end{aligned}
$$

于是定义原子核的质量密度多极算符：

$$
\boxed{
\begin{aligned}
M_{JM;\tau}(q)
&=
\sum_{i=1}^{A}j_J(qr_i)
\\
&\quad
Y_{JM}(\hat{\mathbf r}_i)t^\tau(i)
\end{aligned}
}
$$

其中：

- $j_J(qr_i)$：球贝塞尔函数；
- $Y_{JM}$：球谐函数；
- $t^\tau$：核子的同位旋算符；
- $\tau=0$：等标量通道；
- $\tau=1$：等矢量通道。

在 AFH 常用约定下：

$$
t^0=1,\qquad t^1=\tau_3.
$$

现在就可以定义核响应：

$$
\boxed{
\begin{aligned}
W_M^{\tau\tau'}(y_A)
&=
\sum_{J=0,2,\ldots}
\langle J_A\|M_{J;\tau}(q_A)\|J_A\rangle
\\
&\quad
\langle J_A\|M_{J;\tau'}(q_A)\|J_A\rangle^*
\end{aligned}
}
$$

这里的多极求和是针对弹性核态、具有相应宇称的质量密度响应。


这就是 AFH 的 $W_M$ 的物理来源。


因此，你给出的：

$$
\boxed{ R_A(E_R) = \frac{4\pi}{2J_A+1} W_M^{00}(y_A) }
$$

实际上就是把原子核的等标量质量密度矩阵元平方，并进行初始核自旋平均、末态自旋求和之后得到的响应。


其中：

$$
y_A=\left(\frac{q_Ab_A}{2}\right)^2 =\frac{b_A^2m_AE_R}{2}.
$$

### **这个公式到底包含什么？**

我们可以逐项拆开：

| 物理效应 | 是否包含在 $R_A$ 中 | 具体表现 |
| --- | --- | --- |
| 核子相干增强 | 包含 | 长波极限下 $A^2$ |
| 有限核尺寸 | 包含 | 不同核子位置导致相位差 |
| 核子空间分布 | 包含 | 核子密度及其径向分布 |
| 核多极结构 | 包含 | $J=0,2,\ldots$ 的贡献 |
| 核自旋平均 | 包含 | $2J_A+1$ 的归一化 |
| 壳模型核结构 | 包含 | 取决于所采用的核波函数和单体密度矩阵 |
| 暗物质传播子 | 不包含 | 需要在粒子物理振幅中计算 |
| $\chi_2$ 共振 | 不包含 | 需要单独计算 Breit–Wigner 传播子 |
| 标量发射相空间 | 不包含 | 属于三体运动学 |
| 暗物质速度分布 | 不包含 | 属于晕模型积分 |

这里还有一个重要的细节：


$W_M^{00}$ 是核子单体质量密度算符对应的响应。在 AFH 默认的单体流处理下，它不会自动包含所有可能的双核子流、介子交换流等多体电流修正。

### **一个非常有用的极限检查**

在零动量转移时：

$$
q_A\rightarrow0.
$$

因为：

$$
j_0(0)=1,\qquad j_{J>0}(0)=0,
$$

只剩下 $J=0$ 项。


在 $t^0=1$ 的等标量约定下：

$$
M_{00;0}(0) = \frac{A}{\sqrt{4\pi}}.
$$

经过约化矩阵元和自旋平均，可以得到：

$$
\boxed{ R_A(0)=A^2 }
$$

所以：

$$
\boxed{ R_A(q_A) = A^2 F_M^2(q_A) }
$$

这里定义了一个归一化的有效质量响应形状因子：

$$
F_M^2(q_A) \equiv\frac{R_A(q_A)}{A^2}.
$$

对于自旋为零的原子核，这可以直接理解为普通的质量密度形状因子平方。对于具有非零自旋的核，AFH 的多极求和还可能包含高阶偶数多极贡献，因此不一定等于简单的单一球形形状因子。

## **五、现在看到了吗？两种计算方法实际上是同一个矩阵元**

我们把刚才的两种方法放在一起。

**方法 A：点状原子核振幅乘有限尺寸修正**

$$
\mathcal M_{\rm pt}=A\mathcal M_{\chi N}^{(1)}
$$

$$
\overline{|\mathcal M_A|^2} = \overline{|\mathcal M_{\rm pt}|^2} F_M^2(q_A)
$$

**方法 B：AFH 单核子非相对论算符嵌入原子核**

$$
\hat{\mathcal O}_1 \longrightarrow \sum_{i=1}^{A} e^{i\mathbf q_A\cdot\mathbf r_i}
$$

$$
\overline{|\mathcal M_A|^2} \propto \frac{4\pi}{2J_A+1}W_M^{00}(y_A)
$$

相同物理结果

$$
\boxed{
\begin{aligned}
\overline{|\mathcal M_A|^2}
&=
\overline{|\mathcal M_{\rm pt}|^2}
\\
&\quad
\frac{R_A(q_A)}{R_A(0)}
\end{aligned}
}
$$

这里假设点状振幅已经包含了零动量转移时的完整相干核子耦合。

所以：

- 方法 A：先把核子相干求和近似为一个整体，再恢复有限核尺寸。
- 方法 B：先保留每一个核子的算符，再通过核波函数计算整个原子核的矩阵元。

数学上：

$$
\boxed{
\left|
\left\langle A\left|
\sum_i e^{i\mathbf q_A\cdot\mathbf r_i}
\right|A\right\rangle
\right|^2
}
$$

无论你采用哪一种方法，最终计算的都是同一个量。


AFH 做的是把这个量组织成适合一般相互作用使用的核响应函数。


这也是 AFH 文章强调的粒子物理响应和核结构响应因子化的来源。

arXiv+1


## **六、但是，为什么 AFH 还需要那么多其他核响应？**

你可能会继续问：


既然一个核响应函数就可以处理有限核尺寸，为什么 AFH 还要引入

$$
\Sigma',\quad \Sigma'',\quad \Delta,\quad \Phi'',\quad \widetilde\Phi''?
$$

原因是刚才我们选择的相互作用非常特殊：

$$
\mathcal O_1=1_\chi1_N.
$$

它只探测核子的密度。


但考虑另一个相互作用：

$$
\mathcal O_4 = \mathbf S_\chi\cdot\mathbf S_N.
$$

此时核子算符变成：

$$
\begin{aligned}
\hat{\mathcal O}_{4,A}
&=
\sum_i
\mathbf S_\chi\cdot\mathbf S_N^{(i)}
\\
&\quad
e^{i\mathbf q_A\cdot\mathbf r_i}.
\end{aligned}
$$

它探测的就不是核子密度，而是核子自旋分布。


因此需要：

$$
W_{\Sigma'}(q_A),\qquad W_{\Sigma''}(q_A).
$$

再例如：

$$
\begin{aligned}
\mathcal O_3
&=
i\mathbf S_N\cdot
\left(
\frac{\mathbf q}{m_N}\times\mathbf v^\perp
\right).
\end{aligned}
$$

把这个算符嵌入原子核时，核子内部的速度和轨道角动量也会参与相互作用，因此会出现与 $\Phi''$、$\Delta$ 等有关的核结构。


这就是为什么：


**一个普通的有限尺寸形状因子不能替代 AFH 的全部核响应。**


AFH 的真正贡献不仅仅是给传统的自旋无关和自旋相关散射增加形状因子，而是系统地考虑了不同非相对论相互作用在复合原子核内部产生的不同核算符。


原文也明确指出，直接采用点状核近似可能丢失这些复合核算符的贡献。

arXiv+1


## **七、回到我们的 LZ 三体散射：为什么依然可以使用 $W_M^{00}$？**

现在最重要的是把以上推导放回我们的模型。


我们研究的过程：

$$
\chi_1+A\rightarrow\chi_1+A+s.
$$

假设媒介子 $V$ 与核子通过矢量流耦合，暗物质在散射过程中辐射标量 $s$。


完整振幅可以写成：

$$
\boxed{ \mathcal M_3 = \mathcal T_{\chi,s}^{\mu} D_{\mu\nu}(q_A) J_A^\nu(q_A) }
$$

这里：

$$
J_A^\nu(q_A) = \langle A'|J_A^\nu(q_A)|A\rangle.
$$

注意，这里我们可以把整个三体振幅分成两部分：

$$
\begin{gathered}
\underbrace{
\mathcal T_{\chi,s}^{\mu}D_{\mu\nu}(q_A)
}_{\text{暗物质与标量的粒子物理部分}}
\\
\qquad
\underbrace{J_A^\nu(q_A)}_{\text{原子核部分}}.
\end{gathered}
$$

对于领先阶的矢量电荷相互作用：

$$
\begin{aligned}
J_A^0(q_A)
&\simeq
2m_N
\left\langle A'\left|
\\
&\quad
\sum_{i=1}^{A}g_{N_i}e^{i\mathbf q_A\cdot\mathbf r_i}
\right|A\right\rangle.
\end{aligned}
$$

于是：

$$
\begin{aligned}
\mathcal M_3
&\simeq
\mathcal K_3
\left\langle A'\left|
\\
&\quad
\sum_{i=1}^{A}g_{N_i}e^{i\mathbf q_A\cdot\mathbf r_i}
\right|A\right\rangle,
\end{aligned}
$$

其中 $\mathcal K_3$ 收集暗物质流、标量发射顶点、媒介子传播子及相关运动学因子。


这时候就和前面的 AFH 推导完全接上了！


因此：

$$
\boxed{ \overline{|\mathcal M_3|^2} \propto |\mathcal K_3|^2 R_A(E_R) }
$$

这里暂时假设纯等标量耦合，并省略了与振幅归一化有关的常数。


而三体散射的特殊信息仍然全部留在：

$$
\mathcal K_3 = \mathcal K_3(q_A,q_\chi,k_s).
$$

这意味着：

- $\chi_2$ 传播子的 Breit–Wigner 共振结构仍然保留；
- 标量 $s$ 的动量和质量仍然保留；
- 三体相空间仍然需要完整积分；
- 原子核只通过 $q_A$ 对应的核响应进入。

这正是我们目前计算框架能够成立的理论基础。

### **特别注意： $R_A$ 不能重复乘上相干增强**

如果你的点状原子核振幅已经使用了：

$$
g_A=Ag_N,
$$

那么它已经包含了零动量转移时的 $A$ 倍振幅。


这时正确的有限尺寸修正是：

$$
\boxed{ |\mathcal M_3|^2 = |\mathcal M_{3,\rm pt}|^2 \frac{R_A(q_A)}{R_A(0)} }
$$

而不是直接再乘一个未经归一化的 $R_A(q_A)$。


否则会重复计算 $A^2$。


反过来，如果你的粒子物理振幅只使用了单核子的耦合 $g_N$，还没有包含核子相干求和，那么就应该使用完整的 $R_A(q_A)$，并保持 AFH 的归一化约定一致。


这两种计算方法的数值比较，必须先确认这一点。

## **八、对我们目前的计算，我建议做一个严格的等价性验证**

我们可以直接做一个不涉及暗物质速度积分、不涉及标量相空间的测试。


只验证原子核部分。

## **AFH 核响应与点状核振幅等价性测试**

1. **构造单核子振幅**

   取纯矢量电荷相互作用，求出单核子领先阶非相对论振幅。
2. **点状原子核计算**

   将单核子耦合替换为等标量核耦合：

$$
g_A=Ag_N.
$$
3. **AFH 核响应计算**

   使用 Xe-131 的核结构输入计算：

$$
R_A(q_A)= \frac{4\pi}{2J_A+1}W_M^{00}(y_A).
$$
4. **逐点比较**

   比较：

$$
\begin{gathered}
\frac{|\mathcal M_A(q_A)|^2}{|\mathcal M_A(0)|^2}
\\
\text{与}
\\
\frac{R_A(q_A)}{R_A(0)}.
\end{gathered}
$$
5. **零动量极限检查**

   验证：

$$
R_A(0)=A^2
$$

   （纯等标量、$t^0=1$ 的约定）。

如果两者一致，就证明了我们对 $M$ 响应的使用是正确的。


然后再把同一个核响应嵌入完整的三体振幅中。

## **九、最值得记住的三个公式**

我把整个理论逻辑压缩成三个公式：


**第一：微观核子相互作用。**

$$
\boxed{
\mathcal O_1
\longrightarrow
\sum_{i=1}^{A}e^{i\mathbf q_A\cdot\mathbf r_i}
}
$$

这一步是从单核子到复合原子核。


**第二：核响应函数。**

$$
\boxed{ R_A(q_A) = \frac{4\pi}{2J_A+1}W_M^{00}(y_A) }
$$

这一步是把原子核矩阵元平方、自旋平均并组织成 AFH 的核响应。


**第三：我们的三体振幅。**

$$
\boxed{
\overline{|\mathcal M_3|^2}
\propto
|\mathcal K_3(q_A,q_\chi,k_s)|^2R_A(q_A)
}
$$

这一步是把三体粒子物理与核结构分离。


**我的判断是：我们目前采用的 AFH $W_M^{00}$ 核响应路线，在矢量电荷主导、单体流近似下是有明确理论依据的。** 但要证明当前代码实现也完全正确，还需要检查相干因子、响应函数归一化和三体动量转移是否一致。


参考原文：

- [Anand, Fitzpatrick & Haxton, arXiv:1308.6288](https://arxiv.org/abs/1308.6288?utm_source=chatgpt.com)：第 2 节讲单核子非相对论展开，第 3 节讲如何嵌入原子核。
- [Anand, Fitzpatrick & Haxton, arXiv:1405.6690](https://arxiv.org/abs/1405.6690?utm_source=chatgpt.com)：进一步讨论一般相互作用与六种独立核响应。

这两个部分值得结合起来阅读，因为它们恰好解释了我们从粒子物理振幅走到氙核响应的全过程。什么情况下不能等价，另外我们的模型不需要考虑其他有效相互作用吗这个问题非常关键，因为它决定了我们是否可以放心地使用 AFH 的 $W_M^{00}$，还是必须重新构造一套适用于我们三体过程的核响应。


我先给出结论：

1. **点状原子核振幅乘以 $W_M^{00}$，并不总是等价于完整的非相对论有效理论计算。** 它只在一定的相互作用结构和近似条件下成立。
2. 如果暗物质与核子的相互作用包含自旋、速度、动量等不同结构，那么一般需要 AFH 的其他核响应，而不能只使用 $W_M^{00}$。
3. 对于我们目前的模型，不能因为存在三体末态标量 $s$，就认为必须引入全部 AFH 算符。是否需要其他算符，取决于**媒介子 $V$ 与核子的耦合结构，以及非相对论约化后哪些核子流分量实际出现**。

这里尤其要区分两个问题：

- 三体过程是否需要新的暗物质运动学结构？
- 原子核是否需要新的核响应？

这两件事不是一回事。即使三体振幅非常复杂，原子核一侧仍然可能只需要 $M$ 响应；反过来，即使暗物质散射过程是简单的二体过程，也可能同时需要多个核响应。

## **一、什么情况下两种方法不再等价？**

先明确我们讨论的两种方法。


**方法 A：点状核近似加核响应**

$$
|\mathcal M_A|^2 = |\mathcal M_{\mathrm{pt}}|^2 \frac{R_M(q_A)}{A^2}.
$$

这里假设点状振幅已经包含 $A$ 个核子的相干耦合。


**方法 B：先做单核子非相对论展开，再计算核矩阵元**

$$
\begin{aligned}
\mathcal M_A
&=
\left\langle A'\left|
\\
&\quad
\sum_{i=1}^{A}\sum_jc_j^N\mathcal O_j^{(i)}
\right|A\right\rangle.
\end{aligned}
$$

两者等价的实质条件是：方法 A 的点状振幅和核响应，必须能够完整重构方法 B 中实际出现的核子算符矩阵元。


以下几种情况会破坏这种简单的等价关系。

## **情况 1：核子相互作用不再只是密度耦合**

这是最重要的一种情况。


我们之前讨论的是：

$$
\mathcal O_1=1_\chi 1_N.
$$

它对应核子数密度。


在原子核中：

$$
\hat{\mathcal O}_1 = \sum_i e^{i\mathbf q_A\cdot\mathbf r_i}.
$$

所以对应 $M$ 型核响应：

$$
W_M^{\tau\tau'}.
$$

但是，如果微观相互作用是：

$$
\mathcal O_4 = \mathbf S_\chi\cdot\mathbf S_N,
$$

那么嵌入原子核后得到：

$$
\begin{aligned}
\hat{\mathcal O}_4
&=
\sum_i e^{i\mathbf q_A\cdot\mathbf r_i}
\\
&\quad
\mathbf S_\chi\cdot\mathbf S_N^{(i)}.
\end{aligned}
$$

这时候，探测的已经不是核子密度，而是核子自旋分布。


需要使用：

$$
W_{\Sigma'},\qquad W_{\Sigma''}.
$$

如果仍然使用 $W_M$，就会遗漏自旋相关贡献。


类似地：

| 核子层面的 NR 算符 | 对应的主要核响应 |
| --- | --- |
| $\mathcal O_1$ | $M$ |
| $\mathcal O_4$ | $\Sigma',\Sigma''$ |
| $\mathcal O_3$ | $\Phi'',\widetilde\Phi''$ 等 |
| $\mathcal O_5,\mathcal O_8$ | $M,\Delta$ 等 |
| $\mathcal O_6$ | $\Sigma''$ |
| $\mathcal O_9$ | $\Sigma',\Sigma''$ |

这里列的是主要响应对应关系，完整的响应矩阵还包含不同算符之间的干涉项，不能简单地理解成每个算符只对应一个响应。


这里需要结合我们模型的实际拉格朗日量来判断，而不能只根据 AFH 的一般理论来决定。


我重新对照了我们 LZ 三体模型的相互作用结构。我们目前的主计算采用的是 **vector–vector benchmark**：

$$
\begin{aligned}
\mathcal L_{\rm int}
={}&
g_1V^\mu\bar\chi_2\gamma_\mu\chi_1
\\
&+
g_2s\bar\chi_2\chi_1+\mathrm{h.c.}
\\
&+
g_{Vq}V^\mu\sum_q\bar q\gamma_\mu q.
\end{aligned}
$$

在核子层面，我们采用：

$$
\boxed{ \mathcal L_{VN} = g_{VN}V_\mu\bar N\gamma^\mu N, \qquad N=p,n }
$$

其中当前 benchmark 采用：

$$
g_{Vp}=g_{Vn}=g_{VN}=3g_{Vq}.
$$

这几个结构非常重要：

- $V$ 与核子通过矢量流相互作用；
- $\chi_1,\chi_2$ 通过矢量顶点与 $V$ 相互作用；
- 标量 $s$ 通过暗物质内部的 $\chi_2\to\chi_1+s$ 过程产生；
- $s$ 并没有直接耦合到核子的标量密度或核子自旋。

因此，我们的三体过程虽然有一个标量末态，但核子侧并不是标量相互作用。


**这是判断我们需不需要其他 AFH 核响应的第一条依据。**

## **一、先看哪些情况会使 $W_M$ 不够用**

### **1. 出现核子自旋相互作用**

假设核子侧不是矢量流，而是轴矢量流：

$$
J_N^\mu=\bar N\gamma^\mu\gamma^5N.
$$

它的非相对论约化与矢量流不同。


轴矢量流的空间分量在领先阶包含：

$$
\mathbf J_N^A \simeq 2m_N\boldsymbol\sigma_N.
$$

于是原子核上的相互作用变成：

$$
\hat{\mathbf J}_A^A
\sim
\sum_i\boldsymbol\sigma_i
e^{i\mathbf q_A\cdot\mathbf r_i}.
$$

这时探测的是核子的自旋分布，而不是核子数密度。


必须考虑：

$$
W_{\Sigma'}^{\tau\tau'}, \qquad W_{\Sigma''}^{\tau\tau'}.
$$

尤其对氙而言，这一点有实际意义。

[4. Nuclear Spin & Moments — PHY303 Nuclear Physics](https://images.openai.com/static-rsc-4/PPwkmRdkSVgnHecvNXv8XgMUtWycvdzIuaAGRKpM9ia5PQGWRiDzhkUABPUupvlWu_UxFWyQUlP7SbUqMpMsR7pFNC-jMsaSMzqZKrm4sRoHFKWHiXEJJ23NDwgQfuyBUropzqi3NywXk7LeGw0bnT0_u2IzHCq4yQrsiHzxJH0?purpose=inline)

[patrickstowell.github.io](https://patrickstowell.github.io/PHY303-Lectures-2024/unit4/phy303-unit4-parity-moments.html?utm_source=chatgpt.com)

氙的主要天然同位素中：

- $^{129}\mathrm{Xe}$：核自旋 $J=1/2$；
- $^{131}\mathrm{Xe}$：核自旋 $J=3/2$。

它们具有非零核自旋，因此可以产生自旋响应。


但这不意味着我们的模型就必须使用自旋响应。是否使用取决于相互作用是否真的耦合到了核子自旋。

### **2. 出现核子内部速度或轨道角动量相互作用**

这是 AFH 相对于传统 SI/SD 处理特别重要的贡献。


例如考虑：

$$
\mathcal O_8 = \mathbf S_\chi\cdot\mathbf v^\perp.
$$

在单个自由核子层面，它看起来只是暗物质自旋与相对速度的耦合。


但把它嵌入原子核时，核子的速度不再只是原子核质心的速度。


可以分解为：

$$
\mathbf v_N(i) = \mathbf V_A+\mathbf v_N^{\rm int}(i),
$$

其中：

- $\mathbf V_A$：原子核质心速度；
- $\mathbf v_N^{\rm int}$：核子在原子核内部的运动速度。

对于束缚核子：

$$
v_N^{\rm int}\sim 0.1-0.3
$$

是合理的典型量级。


它远大于银河系暗物质的速度：

$$
v_\chi\sim10^{-3}.
$$

如果直接把整个原子核看成点粒子，就会把内部速度信息丢掉。


AFH 证明，这类速度相关相互作用可以产生与核子轨道角动量有关的新响应，例如：

$$
W_\Delta,\qquad W_{\Phi''}.
$$

因此，不能简单地认为所有相互作用都只需要一个 SI 形状因子。AFH 专门指出，点核近似对于一部分速度相关算符甚至会严重低估响应。

arXiv+1


### **3. 质子和中子的耦合不相同**

假设：

$$
g_p\neq g_n.
$$

这时即使相互作用仍然是最简单的核子数密度耦合，也不能只使用等标量响应 $W_M^{00}$。


因为原子核的密度算符变成：

$$
\begin{aligned}
\hat J_A^0
&=
g_p\sum_{i\in p}e^{i\mathbf q_A\cdot\mathbf r_i}
\\
&\quad
+g_n\sum_{i\in n}e^{i\mathbf q_A\cdot\mathbf r_i}.
\end{aligned}
$$

定义：

$$
g_0=\frac{g_p+g_n}{2}, \qquad g_1=\frac{g_p-g_n}{2},
$$

则：

$$
\hat J_A^0 = g_0\hat M_0+g_1\hat M_1.
$$

平方之后：

$$
\boxed{ R_M = g_0^2W_M^{00} + 2g_0g_1W_M^{01} + g_1^2W_M^{11} }
$$

这里采用 AFH 的等标量、等矢量归一化约定。


所以，甚至同一个 $\mathcal O_1$，也可能需要多个核响应分量。

### **4. 出现不同的核子 Lorentz 结构**

不同的相对论相互作用，在非相对论极限下会生成不同的核子算符。


例如：

| 相对论核子流 | 非相对论领先结构 | 主要核响应 |
| --- | --- | --- |
| $\bar N N$ | 核子密度 | $M$ |
| $\bar N\gamma^\mu N$ | 矢量电荷密度 | $M$ |
| $\bar N\gamma^\mu\gamma^5N$ | 核子自旋 | $\Sigma',\Sigma''$ |
| $\bar N i\gamma^5N$ | $\mathbf S_N\cdot\mathbf q_A/m_N$ | 自旋－动量响应 |
| 含核子导数的流 | 核子内部速度、轨道结构 | $\Delta,\Phi''$ 等 |

这张表描述的是主要领先结构，不是说每一种相对论流严格只产生一个 AFH 响应。

## **二、现在具体判断我们的 vector–vector 模型**

这里需要真正做一次非相对论约化。


我们的完整振幅可以示意性地写成：

$$
\mathcal M_3 = \frac{g_1g_2g_{VN}}{t-m_V^2} \mathcal T_3^\mu J_{A,\mu}.
$$

其中：

$$
\mathcal T_3^\mu
$$

包含两张标量辐射图、两个 $\chi_2$ 内部传播子以及它们的干涉；

$$
J_A^\mu = \langle A'| J_A^\mu |A\rangle
$$

是原子核的矢量流。


这里先把注意力放在核子流上。


对于单个核子：

$$
J_N^\mu=\bar u_N(p_N')\gamma^\mu u_N(p_N).
$$

非相对论展开后：


**时间分量：**

$$
\boxed{ J_N^0 = 2m_N\,\xi_N'^\dagger\xi_N +\mathcal O(v_N^2,q_A^2/m_N^2) }
$$

它是核子数密度。


**空间分量：**

$$
\boxed{
\begin{aligned}
\mathbf J_N
&=
\xi_N'^\dagger
\\
&\quad
\left[
(\mathbf p_N'+\mathbf p_N)
+i\boldsymbol\sigma_N\times\mathbf q_A
\right]\xi_N+\cdots
\end{aligned}
}
$$

这里的符号取决于动量转移约定；关键是空间流包含两种结构：

1. 核子的对流电流（convection current）；
2. 核子的自旋磁化电流（magnetization current）。

所以，完整的矢量流并不只有 $J_N^0$。


代入原子核后：

$$
\begin{aligned}
\mathcal M_3
&=
\frac{g_1g_2g_{VN}}{t-m_V^2}
\\
&\quad
\left(
\mathcal T_3^0J_A^0
-\boldsymbol{\mathcal T}_3\cdot\mathbf J_A
\right).
\end{aligned}
$$

现在就可以清楚地看到两种贡献。

## **我们模型中的核响应分解**

领先阶

**时间分量 × 时间分量**

$$
\mathcal M_3^{(0)} \propto \mathcal T_3^0J_A^0
$$

核子矢量电荷密度，产生 $M$ 响应。

$$
W_M^{00}
$$

等标量、相干核响应

需要检查的次领先项

**空间分量 × 空间分量**

$$
\mathcal M_3^{(1)} \propto -\boldsymbol{\mathcal T}_3\cdot\mathbf J_A
$$

核子对流电流、磁化电流。


需要对完整振幅进行匹配，可能引入轨道及相关核响应。

这意味着：


**我们的 vector–vector 模型在领先阶只需要 $W_M^{00}$，但完整的矢量流原则上并不只包含 $W_M^{00}$。**


这一点比简单地说“矢量相互作用只对应 SI”更加准确。

## **三、我们的模型究竟需要哪些 AFH 响应？**

现在可以给出一个比较明确的判断。

| 相互作用结构 | 我们当前模型是否存在 | 是否需要考虑 |
| --- | --- | --- |
| 核子矢量电荷 $J_N^0$ | 存在 | 必须，$W_M^{00}$ |
| 核子轴矢量流 | 不存在 | 不需要引入独立的轴矢量自旋耦合 |
| 核子赝标量流 | 不存在 | 不需要 |
| 核子张量流 | 不存在 | 不需要 |
| 质子－中子非普适耦合 | 当前不存在 | 当前只需等标量通道 |
| 核子矢量空间流 | 存在 | 需要评估次领先阶贡献 |
| 核子两体交换流 | 当前未纳入 | 基准计算不需要自动加入 |

所以，我的建议不是把 AFH 的六种响应全部计算一遍，而是按照我们实际的相互作用逐阶匹配。

### **1. 领先阶：只保留 $W_M^{00}$**

我们的模型中：

$$
g_{Vp}=g_{Vn}.
$$

所以矢量电荷是等标量的：

$$
J_A^0 \propto \sum_{i=1}^{A} e^{i\mathbf q_A\cdot\mathbf r_i}.
$$

它对应：

$$
\mathcal O_1=1_\chi1_N.
$$

因此：

$$
\boxed{ R_A(E_R) = \frac{4\pi}{2J_A+1} W_M^{00}(y_A) }
$$

在这一阶，我们没有理由额外引入：

$$
W_{\Sigma'},\quad W_{\Sigma''},\quad W_\Delta,\quad W_{\Phi''}.
$$

因为当前领先阶的核子相互作用没有对应的自旋、轨道或自旋－轨道耦合。

### **2. 次领先阶：检查空间矢量流**

这里我认为应该做一个额外的理论验证。


定义：

$$
\begin{aligned}
\epsilon_{\rm spatial}
&=
\frac{
|\boldsymbol{\mathcal T}_3\cdot\mathbf J_A|
}{
|\mathcal T_3^0J_A^0|
}.
\end{aligned}
$$

它直接衡量空间流相对于领先阶电荷响应的贡献。


如果：

$$
\epsilon_{\rm spatial}\ll1,
$$

那么只使用 $W_M^{00}$ 就是受控的领先阶近似。


如果空间流贡献不可忽略，则必须将其进行多极展开，并根据实际匹配结果加入相应的 AFH 核响应。


这里不能仅仅因为 $\mathbf J_N$ 中有一个 $\boldsymbol\sigma_N$，就直接添加 $\Sigma'$ 和 $\Sigma''$。必须先计算暗物质空间流与核子磁化流的收缩，再判断最终产生什么核算符。


尤其是我们的暗物质流不是简单的弹性顶点：

$$
\bar u_{\chi_1}'\gamma^\mu u_{\chi_1},
$$

而是包含两个 $\chi_2$ 传播子和标量辐射的完整结构：

$$
\mathcal T_3^\mu = \bar u_{\chi_1}(p') \Gamma_3^\mu(p,p',k_s) u_{\chi_1}(p).
$$

因此，必须对完整的 $\Gamma_3^\mu$ 做非相对论展开，而不是直接套用普通弹性散射的结果。


还要注意：$\chi_2$ 接近共振时，两个传播图及其干涉必须保留。不能只根据一个裸顶点的速度阶数判断整个振幅的修正大小。

## **四、为什么三体过程不意味着需要更多核响应？**

这是另外一个容易混淆的地方。


AFH 的标准非相对论 EFT 是针对弹性：

$$
\chi+N\longrightarrow\chi+N
$$

构造的。


它使用：

$$
\mathbf v^\perp\cdot\mathbf q=0.
$$

但是我们的过程是：

$$
\chi_1+A\longrightarrow\chi_1+A+s.
$$

能量守恒多出了：

$$
\omega_s.
$$

因此，不能直接使用标准二体运动学推导出来的全部 $\mathcal O_i$，尤其不能直接把标准的 $\mathbf v^\perp$ 定义套入完整三体振幅。


但是，这不意味着核响应也必须改变。


原因是：

$$
\boxed{ \text{三体结构主要发生在暗物质流一侧，而不是自动改变核子流的 Lorentz 结构。} }
$$

我们可以将振幅写成：

$$
\begin{aligned}
\mathcal M_3
&=
\underbrace{
\mathcal T_3^\mu(q_A,q_\chi,k_s)D_{\mu\nu}(q_A)
}_{\text{三体粒子物理}}
\\
&\quad
\underbrace{J_A^\nu(q_A)}_{\text{核结构}}.
\end{aligned}
$$

只要核子流仍然由矢量电荷密度主导，核响应就仍然是：

$$
W_M^{00}(q_A).
$$

因此：

- 三体相空间需要重新计算；
- $\chi_2$ 的 Breit–Wigner 结构需要保留；
- 标量的动量 $k_s$ 需要保留；
- 核子密度响应仍然可以使用 AFH 的 $W_M^{00}$。

AFH 的因子化思想正是把粒子物理响应和核结构响应分开处理。

arXiv+1


## **五、还有一个需要特别区分的模型**

我们之前的研究中还讨论过另一种 scalar–pseudoscalar 结构：

$$
\mathcal L_{\phi N} = ig_{\phi N}\phi \bar N\gamma^5N.
$$

这个模型和目前的 vector–vector benchmark 不一样。


因为：

$$
\bar u_N'\gamma^5u_N \propto \boldsymbol\sigma_N\cdot\mathbf q_A
$$

（忽略整体归一化和相位约定）。


它在领先阶就具有动量抑制的自旋结构。


因此，这种模型不能继续简单使用：

$$
W_M^{00}
$$

来描述全部核响应，而应该重新构造自旋－动量相关的核矩阵元。


**尤其不能因为两个模型都存在标量粒子，就把它们的核响应混在一起。**


这里的区别是：

- 当前模型：$V$ 与核子矢量流耦合，$s$ 在暗物质线上辐射。
- 另一种模型：交换媒介子 $\phi$ 直接通过赝标量流与核子耦合。

它们是两种不同的核子相互作用。

## **六、我建议我们对当前模型采用什么计算标准？**

我建议明确分成三个层次。

**Level 0：当前主线计算**

必须完成

$$
\mathcal M_3^{(0)} = \mathcal K_3^{(0)} \times \sqrt{R_A(E_R)}
$$

- 完整保留两张标量辐射图及干涉。
- 保留 $\chi_2$ 的共振传播子。
- 使用 $q_A$ 计算 AFH $W_M^{00}$。

**保留三体相空间。**

**Level 1：矢量流次领先阶审计**

建议完成

$$
\mathcal M_3^{(1)}-\mathcal K_3^i J_A^i
$$

1. 展开完整暗物质流的空间分量。
2. 计算核子的对流电流与磁化电流。
3. 判断是否需要 $\Delta$ 或其他响应。
4. 给出相对于 Level 0 的数值修正。

**Level 2：更高精度核结构修正**

有需要再做
5. 核子有限尺寸形状因子。
6. 两核子交换流。
7. 更高阶核子算符。
8. 检查壳模型核结构的不确定性。

这里还需要强调：AFH 的单体流近似本身并不是完整的 QCD 核结构理论。更高精度计算可能需要手征 EFT 中的两体流等修正，但这不是当前领先阶计算必须自动加入的内容。

## **七、最终判断**

我认为我们目前不需要把所有 AFH 有效相互作用都加入模型。


原因是有效算符不是自由添加的参数，而是由我们的 UV 拉格朗日量匹配出来的。

$$
\boxed{
\begin{gathered}
\text{UV 模型}
\\
\longrightarrow\text{核子流}
\\
\longrightarrow\text{非相对论核子算符}
\\
\longrightarrow\text{AFH 核响应}
\end{gathered}
}
$$

对我们当前的 vector–vector 模型：

- 领先阶：$\mathcal O_1$，使用 $W_M^{00}$。
- 次领先阶：检查完整矢量流的空间分量，不能先验宣称为零。
- 轴矢量、赝标量、张量等其他相互作用：没有相应的 UV 顶点，就不应该人为加入。

**我认为下一步最值得做的不是计算另外五种 AFH 响应，而是对我们已有的三体振幅 $\mathcal T_3^\mu$ 做完整的非相对论展开，定量证明 $W_M^{00}$ 单独使用的精度。**


这样才能把目前的处理从一个合理的领先阶假设，提升为经过理论和数值检验的近似。

我认为需要检查，但目前不能直接断定我们需要加入自旋响应和轨道响应。更准确的判断是：


**我们的模型很可能仍然由 $W_M^{00}$ 主导，但必须检查完整三体振幅的空间分量，才能证明其他核响应可以忽略。**


这里有一个容易产生误判的地方：氙核内部核子的速度可以达到 $0.1\sim0.3$，远大于暗物质晕速度 $10^{-3}$，但这并不意味着轨道响应一定重要。


因为核子内部速度大，并不等于它对散射振幅的贡献大。还必须看它如何与暗物质流收缩，以及相应核矩阵元是否受到其他运动学因子的抑制。


我建议把这个问题分成三个独立的检查：

1. **核自旋响应：** 矢量流的磁化电流是否产生不可忽略的自旋相关贡献？
2. **轨道响应：** 矢量流的对流电流是否产生不可忽略的轨道角动量贡献？
3. **三体共振效应：** $\chi_2$ 传播子和标量发射是否改变了暗物质空间流与时间流的相对大小？

第三项尤其重要。不能只使用普通弹性散射的速度阶数来判断我们的三体过程。

## **一、先给出一个定量判断标准**

我们的核子矢量流可以写成：

$$
J_N^\mu=\bar u_N(p_N')\gamma^\mu u_N(p_N).
$$

非相对论展开后：

$$
J_N^0 \simeq 2m_N,
$$

$$
\begin{aligned}
\mathbf J_N
&\simeq
(\mathbf p_N'+\mathbf p_N)
\\
&\quad
+i\boldsymbol\sigma_N\times\mathbf q_A.
\end{aligned}
$$

因此原子核矢量流包含：

$$
\boxed{ \mathbf J_A = \mathbf J_{\rm conv} + \mathbf J_{\rm mag} }
$$

其中：

- $\mathbf J_{\rm conv}$：对流电流，与核子内部运动及轨道结构有关；
- $\mathbf J_{\rm mag}$：磁化电流，与核子自旋有关。

三体振幅为：

$$
\begin{aligned}
\mathcal M_3
&=
\mathcal K_3
\left(
\mathcal T_3^0J_A^0
-\boldsymbol{\mathcal T}_3\cdot\mathbf J_A
\right).
\end{aligned}
$$

因此定义两个比值：

$$
\boxed{
\begin{aligned}
\epsilon_{\rm conv}
&=
\frac{
|\boldsymbol{\mathcal T}_3\cdot\mathbf J_{\rm conv}|
}{
|\mathcal T_3^0J_A^0|
}
\end{aligned}
}
$$

$$
\boxed{
\begin{aligned}
\epsilon_{\rm mag}
&=
\frac{
|\boldsymbol{\mathcal T}_3\cdot\mathbf J_{\rm mag}|
}{
|\mathcal T_3^0J_A^0|
}
\end{aligned}
}
$$

它们分别衡量轨道电流和自旋电流相对于领先阶密度响应的大小。


如果两者都足够小，我们就可以有依据地只使用 $W_M^{00}$。


注意，这里最好最终比较的是自旋求和、初态平均后的振幅平方及其干涉项，而不只是振幅模长的比值。

## **二、我检查了仓库中的实际三体振幅和数值实现**

这里不再使用普通弹性散射的估计，而是直接检查了我们项目的真实模型。


检查对象：

- `research/docs/01_model_and_amplitude.md`
- `research/docs/appendices/09A_three_body_kinematics_amplitude.md`
- `research/figure2_full_reproduction/eq6_kernel.py`
- `paper-source/main.tex`

对应的拉格朗日量是：

$$
\begin{aligned}
\mathcal L_{\rm int}
={}&
g_1V_\mu\bar\chi_2\gamma^\mu\chi_1
\\
&+
g_2s\bar\chi_2\chi_1+\mathrm{h.c.}
\\
&+
g_{Vq}V_\mu\sum_q\bar q\gamma^\mu q.
\end{aligned}
$$

这里有一个重要事实：


**我们的暗物质不是直接通过一个普通的弹性矢量流与原子核散射，而是通过两个包含虚 $\chi_2$ 传播子的辐射图形成有效三体流。**


数值程序目前计算的是：

$$
\mathcal L_{00} = \frac12\sum_{\rm spins} \left|\bar u(p')\Gamma^0u(p)\right|^2.
$$

也就是说，程序完整保留了两张标量辐射图及其干涉，但只取了暗物质流的时间分量。


这和附录 A.4 中采用的核电荷领先阶近似是一致的，但**目前还没有通过完整的 $\Gamma^i$ 计算证明空间分量可以忽略**。

### **1. 我对完整三体暗物质流做了数值检查**

我使用仓库中的四动量构造方法和 Dirac 矩阵实现，将顶点从

$$
\Gamma^0
$$

推广到

$$
\Gamma^\mu,\qquad \mu=0,1,2,3,
$$

然后计算：

$$
\begin{aligned}
L^{\mu\nu}
&=
\frac12\operatorname{Tr}
\left[
(\slashed p'+m_\chi)\Gamma^\mu
\\
&\quad
(\slashed p+m_\chi)\overline{\Gamma}^{\,\nu}
\right].
\end{aligned}
$$

对于仓库中代表性的参数：

$$
m_\chi=1\ {\rm TeV},\qquad v=800\ {\rm km/s},
$$

$$
m_s=200\text{--}360\ {\rm keV}, \qquad \Delta m=1\ {\rm MeV},
$$

并使用条件性的 $\chi_2$ pole width，我得到：

$$
\boxed{ \frac{\sum_{i=1}^3 L^{ii}}{L^{00}} \simeq (6.1\text{--}6.9)\times10^{-6} }
$$

也就是：

$$
\frac{\sqrt{\sum_iL^{ii}}}{\sqrt{L^{00}}} \simeq 2.5\text{--}2.6\times10^{-3}.
$$

这是对三体暗物质流的数值诊断，不是完整氙核截面修正。积分采用代表性参数点和有限阶求积，尚不是全参数空间的收敛审计。


这说明在目前的 benchmark 下，暗物质流的空间分量确实受到约 $10^{-3}$ 量级的振幅抑制。

### **2. 点状原子核的完整矢量流检查**

进一步，我将靶核近似为一个点状、无自旋的复合粒子，使用其完整弹性矢量流：

$$
J_A^\mu=(P+P')^\mu.
$$

此时：

$$
\frac{|\mathbf J_A|}{J_A^0} \simeq \frac{q_A}{2m_A}.
$$

用完整 $\Gamma^\mu$ 与这个核流收缩，而不是只取 $J_A^0$，得到：

| $E_R$ | 完整点状核流相对于纯 $L^{00}$ 的截面变化 |
| --- | --- |
| 101 keV | $-3.0\times10^{-6}$ |
| 200 keV | $-4.1\times10^{-6}$ |
| 267 keV | $-4.8\times10^{-6}$ |
| 360 keV | $-5.6\times10^{-6}$ |
| 542 keV | $-6.9\times10^{-6}$ |

点状核质心电流修正很小

但是，这个结果只验证了原子核质心的对流电流。


它没有验证 AFH 中与核子内部轨道、自旋结构相关的响应。


因此，不能直接据此宣布 $W_\Delta$ 和自旋响应都不重要。

## **三、真正需要注意的是：我们的夸克矢量流并不等于点状核子的 Dirac 矢量流**

这是我进一步检查后认为最重要的地方。


我们的 UV 拉格朗日量实际上写的是：

$$
\mathcal L\supset g_{Vq}V_\mu\sum_q\bar q\gamma^\mu q.
$$

但从夸克层面到核子层面，不能在所有动量转移下都简单地写成：

$$
J_N^\mu=3\bar N\gamma^\mu N.
$$

更完整的核子矩阵元应该是：

$$
\boxed{
\begin{aligned}
\langle N'|J_V^\mu|N\rangle
&=
\bar u_N'
\left[
F_1^{V,N}(t)\gamma^\mu
\\
&\quad
-\frac{iF_2^{V,N}(t)}{2m_N}
\sigma^{\mu\nu}q_{A\nu}
\right]u_N
\end{aligned}
}
$$

这里：

- $F_1^{V,N}$：Dirac 形状因子；
- $F_2^{V,N}$：Pauli 形状因子；
- $t=q_A^2$，这里的 $q_A$ 是四动量转移，满足 $t\simeq-|\mathbf q_A|^2$。

在零动量转移下：

$$
F_1^{V,p}(0)=F_1^{V,n}(0)=3.
$$

这正是我们目前使用

$$
g_{VN}=3g_{Vq}
$$

的来源。


但是：

$$
\boxed{F_2^{V,N}(t)\neq0}
$$

而且 $F_1$、$F_2$ 都有动量转移依赖。


Hoferichter、Klos 和 Schwenk 对矢量流的夸克－核子匹配正是采用了这两个形状因子，并进一步进行了非相对论展开。

arxiv.org+1


### **1. Pauli 形状因子会产生什么？**

非相对论匹配后，矢量－矢量相互作用不再只有最简单的：

$$
\mathcal O_1=1_\chi1_N.
$$

还会出现与 Pauli 形状因子有关的结构：

$$
\boxed{
\begin{aligned}
\mathcal M_{VV}^{NR}
&=
c_1(t)\mathcal O_1
\\
&\quad
+c_3(t)\mathcal O_3
\\
&\quad
+c_4(t)\mathcal O_4
\\
&\quad
+c_6(t)\mathcal O_6+\cdots
\end{aligned}
}
$$

其中主要有：

$$
\begin{aligned}
\mathcal O_3
&=
i\mathbf S_N\cdot
\left(
\frac{\mathbf q_A}{m_N}
\times\mathbf v^\perp
\right),
\end{aligned}
$$

$$
\mathcal O_4 = \mathbf S_\chi\cdot\mathbf S_N,
$$

$$
\begin{aligned}
\mathcal O_6
&=
\left(
\mathbf S_\chi\cdot\frac{\mathbf q_A}{m_N}
\right)
\\
&\quad
\left(
\mathbf S_N\cdot\frac{\mathbf q_A}{m_N}
\right).
\end{aligned}
$$

这里采用 AFH 的标准弹性算符定义来说明核子流匹配；在我们的三体过程中，$\mathbf v^\perp$ 必须根据三体运动学重新定义，不能直接使用弹性散射的运动学关系。


这三个算符的系数并不一样：

- $c_1$：由 $F_1$ 主导；
- $c_3$：由 $F_2$ 产生，主要包含核子内部速度；
- $c_4,c_6$：也与 $F_2$ 有关，但含有额外的 $1/m_\chi$ 抑制。

这也是为什么不能简单地认为矢量相互作用一定只有 SI 响应。

indico.global+1


## **四、对我们来说，最值得检查的是 $\mathcal O_3$，而不是之前举例的 $\mathcal O_8$**

这里需要修正前面讨论中的一个重点。


之前举例：

$$
\mathcal O_8 = \mathbf S_\chi\cdot\mathbf v^\perp.
$$

这是一个能够探测核子内部速度的算符，但它不是我们当前 vector–vector 模型在领先阶自然产生的算符。


对于我们的模型，应该优先检查的是：

$$
\boxed{
\begin{aligned}
\mathcal O_3
&=
i\mathbf S_N\cdot
\left(
\frac{\mathbf q_A}{m_N}
\times\mathbf v^\perp
\right)
\end{aligned}
}
$$

它对应的核响应是：

$$
\boxed{ \mathcal O_3 \longrightarrow W_{\Phi''} }
$$

并且与标准质量响应存在干涉：

$$
\boxed{ W_{M\Phi''} }
$$

这两个响应非常值得注意。


AFH 的核结构分析表明，$\Phi''$ 是与核子自旋－轨道结构有关的准相干响应（quasi-coherent response），而不是普通的 SD 响应。对氙而言，它可以涉及相当数量的核子。

archive.int.washington.edu+1


这意味着：


**即使我们没有轴矢量耦合，也可能存在与核子内部轨道运动有关的次领先贡献。**


它不应该和 $^{129}\mathrm{Xe}$、$^{131}\mathrm{Xe}$ 的总核自旋简单等同起来。

## **五、为什么我认为这个修正对我们尤其值得检查？**

这里有一个非常重要的数值原因。


我们之前计算的 Xe-131 的 $W_M^{00}$ 存在三个非常深的极小值。


数据来自仓库 `research/afh_default_density_xe131/output/minima.csv`。

| $q_A$ (MeV) | $E_R$ (keV) | $q_A/m_N$ | $\sqrt{R_M(q_A)/A^2}$ |
| --- | --- | --- | --- |
| 157.94 | 102.21 | 0.168 | $3.52\times10^{-3}$ |
| 256.27 | 269.10 | 0.273 | $2.52\times10^{-4}$ |
| 365.07 | 546.09 | 0.389 | $3.95\times10^{-4}$ |

这几个极小值意味着：

$$
\mathcal M_M \propto AF_M(q_A)
$$

在这些位置受到非常强的抑制。


而 $\Phi''$ 响应不一定在相同位置发生相同的抵消。


因此，即使 $\mathcal O_3$ 的 Wilson 系数比较小，也有可能在这些位置改变总振幅：

$$
\begin{aligned}
|\mathcal M_A|^2
\sim{}&
|c_1|^2W_M
\\
&+
2\operatorname{Re}(c_1c_3^*)W_{M\Phi''}
\\
&+
|c_3|^2W_{\Phi''}+\cdots.
\end{aligned}
$$

这里省略了 AFH 的具体归一化系数，重点是展示干涉结构。

### **一个量级估算**

用一个仅供判断的低动量估计：

$$
\left|\frac{F_2^V}{F_1^V}\right|\sim0.1,
$$

并取：

$$
v_N^{\rm int}\sim0.1-0.3.
$$

那么：

$$
\begin{aligned}
\frac{|c_3\mathcal O_3|}{|c_1\mathcal O_1|}
&\sim
\frac{F_2^V}{F_1^V}
\frac{q_A}{m_N}v_N^{\rm int}.
\end{aligned}
$$

三个极小值附近对应的单核子算符量级大致为：

| $q_A$ | $\mathcal O_3/\mathcal O_1$ 量级 |
| --- | --- |
| 158 MeV | $0.2\%-0.6\%$ |
| 256 MeV | $0.3\%-1.0\%$ |
| 365 MeV | $0.5\%-1.4\%$ |

这还不是完整的原子核响应比值。


真正的原子核振幅还要乘以 $W_{\Phi''}$ 对应的核矩阵元，并考虑与 $W_M$ 的干涉。


但是，比较一下前面表格中的 $F_M$，就能看出为什么值得认真检查：


在第二、第三个极小值附近，$M$ 响应本身已经被压低到 $10^{-4}$ 量级的振幅。


所以我不认为可以仅凭一般的速度幂次估算，就把 $\Phi''$ 排除。

需要进行核响应数值审计

注意：上面的百分比是单核子层面的量级估算，不是我们已经算出的 Xe-131 截面修正。不能将其直接作为论文结果。

## **六、哪些其他响应可以暂时不考虑？**

现在可以更有针对性地筛选。

| AFH 核响应 | 对应结构 | 我们当前的判断 |
| --- | --- | --- |
| $M$ | $\mathcal O_1$ | 必须保留 |
| $\Phi''$ | $\mathcal O_3$ | 优先检查 |
| $\Sigma'$ | $\mathcal O_4,\mathcal O_6$ 等 | 次要，检查系数抑制 |
| $\Sigma''$ | $\mathcal O_4,\mathcal O_6$ 等 | 次要，检查系数抑制 |
| $\Delta$ | 与 $\mathcal O_8$ 等有关 | 当前领先阶不需要 |
| $\widetilde\Phi''$ | 其他速度、自旋结构 | 当前领先阶不需要 |

对于自旋响应，最重要的是暗物质质量很大：

$$
m_\chi=1\ {\rm TeV}.
$$

相应的次领先系数含有：

$$
\frac{q_A^2}{m_Nm_\chi}.
$$

在三个极小值附近：

$$
\frac{q_A^2}{m_Nm_\chi}
\simeq
\begin{cases}
2.7\times10^{-5},\\
7.0\times10^{-5},\\
1.4\times10^{-4}.
\end{cases}
$$

因此，相比 $\mathcal O_3$，$\mathcal O_4,\mathcal O_6$ 的系数受到更强的质量抑制。


我的判断是：不需要在主线中优先展开完整的自旋响应计算，但应该在匹配阶段检查它们的实际系数。


另外，Hoferichter 等人的手征 EFT 计算表明，在他们考虑的 $p^3$ 阶，矢量两体流首先出现在暗物质轴矢量－核子矢量（AV）通道，而不是我们目前的 VV 通道。因此，两核子矢量流不需要成为我们当前第一轮审计的内容。

arxiv.org+1


## **七、我建议如何修改我们目前的计算框架？**

不需要推翻已经完成的三体计算。


只需要在现有框架中增加一个核子流匹配层。

## **建议的计算路线**

**第一层：完整三体暗物质流**

$$
\mathcal T_3^\mu(p,p',k_s)
$$

保留两张辐射图、干涉和 $\chi_2$ 传播子。

**第二层：夸克－核子矢量流匹配**

$$
J_N^\mu = F_1^V(t)\gamma^\mu -\frac{iF_2^V(t)}{2m_N}\sigma^{\mu\nu}q_{A\nu}
$$

不再把核子当作完全点状的 Dirac 粒子。

**第三层：AFH 核响应**

$$
W_M,\quad W_{\Phi''},\quad W_{M\Phi''}
$$

再根据匹配系数检查 $\Sigma'$、$\Sigma''$。

**第四层：三体相空间积分**

$$
\frac{d\sigma_3}{dE_R}
$$

保留原有的 $W^2,z,\phi_*$ 积分。

### **在现有 DMFormFactor-v6 中如何实现？**

我检查了仓库里的：


[dmformfactor-V6.m](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/blob/main/v6/dmformfactor-V6.m?utm_source=chatgpt.com)


其中已经定义了相应的相对论算符：

- `OpRel[5]`：矢量－矢量流；
- `OpRel[6]`：暗物质矢量流－核子张量流。

这恰好可以用来组织：

$$
F_1^V(t)\times\mathrm{OpRel}[5] + F_2^V(t)\times\mathrm{OpRel}[6],
$$

其中必须按照相同的动量转移、符号和归一化约定完成匹配。


这样可以继续使用现有 Xe-131 的单体密度矩阵，而不必重新开发一套核结构程序。

## **八、最终检查结论**

我把目前的判断分成三个层次：

| 问题 | 结论 |
| --- | --- |
| 氙核非零自旋是否迫使我们使用 SD 响应？ | 否 |
| 是否需要加入 $\mathcal O_8$、$W_\Delta$？ | 当前 VV 模型领先阶不需要 |
| 是否需要检查核子内部速度和轨道结构？ | **需要，优先检查 $\mathcal O_3$ 与 $W_{\Phi''}$** |
| 是否需要检查 $\Sigma'$、$\Sigma''$？ | 需要匹配，但预计受到较强质量抑制 |
| 是否需要马上计算两核子矢量流？ | 暂时不需要 |

还有一个特别重要的区别：


我刚才计算的暗物质空间流约 $2.5\times10^{-3}$，以及点状核质心电流的 ppm 级修正，**不能用来排除 $\Phi''$。** 因为 $\mathcal O_3$ 还可以通过核子 Pauli 形状因子进入核子时间流，并耦合到暗物质的领先阶时间分量。


因此，之前的数值检查只完成了一部分。


**我的最终建议是：保留目前 $W_M^{00}$ 作为主基准，但在正式定稿之前，增加一次 Xe-131 的 $W_{\Phi''}$ 和 $W_{M\Phi''}$ 计算。** 特别检查 $q_A\simeq256$ MeV 和 $365$ MeV 附近的两个深极小值。


如果这些响应确实很小，我们就可以有依据地继续使用目前的简化公式；如果它们填平了原来的谱形极小值，就必须修正天然氙的三体反冲谱。


这项工作比现在就把 AFH 的六种响应全部计算一遍更有针对性。


我建议下一步直接在 `LZ-3-body-for-hdm` 中建立 **VV 核子流的 $F_1/F_2$ 匹配与 Xe-131 $\Phi''$ 响应审计**，先计算干涉项，再决定是否需要扩展完整三体截面。


参考文献：

1. [Anand, Fitzpatrick & Haxton, arXiv:1308.6288](https://arxiv.org/abs/1308.6288?utm_source=chatgpt.com)。
2. [Hoferichter, Klos & Schwenk, arXiv:1503.04811](https://arxiv.org/abs/1503.04811?utm_source=chatgpt.com)。
3. [Hoferichter, Chiral EFT matching to nonrelativistic operators](https://indico.global/event/6060/contributions/49525/attachments/24815/42475/Hoferichter.pdf?utm_source=chatgpt.com)。讨论的物理对话我已经复制给你了，你可以自行完善并扩充，写入到文档中

---

# 补充章节：完整 AFH 核响应数据库与三体散射的统一收缩

> 本章补充讨论：既然已经使用 AFH DMFormFactor v6.0，是否还需要核子 Dirac–Pauli 形状因子？为什么要做核子流与 AFH 核响应的匹配？能否直接计算全部 AFH 核响应并将它们都纳入三体截面？全部响应都算出来是否就意味着结果精确？
>
> 本章作为前文的补充，不替代前面关于 AFH、核子流和三体运动学的推导。核心思路是：**可以先完整建立 AFH 核响应数据库，但物理截面必须由模型给出的核子流系数、AFH 响应及其允许的干涉项共同确定。**

## 一、先区分三个不同层次的物理结构

我们的过程为

$$
\chi_1+A\longrightarrow \chi_1+A+s.
$$

在单体核流近似下，三体振幅可以组织为

$$
\boxed{
\mathcal M_3=
\mathcal T_{3,\mu}(p,p',k_s)\,
D^{\mu\nu}(q_A)\,
\langle A'|J_{A,\nu}(q_A)|A\rangle
}
$$

其中：

- $\mathcal T_3^\mu$：暗物质辐射标量后的三体有效流，包含两张标量辐射图、两个 $\chi_2$ 传播子及其干涉；
- $D^{\mu\nu}(q_A)$：媒介子传播子；
- $J_A^\nu$：原子核的矢量流；
- $q_A$：原子核获得的四动量转移；
- $k_s$：末态标量四动量。

核子流与 AFH 核响应处在不同的理论层次，不能互相替代。

| 层次 | 描述对象 | 主要输入 | 回答的问题 |
| --- | --- | --- | --- |
| 核子内部结构 | 单个质子或中子 | $F_1^V(t_A),F_2^V(t_A)$ | 外部矢量流怎样作用于单个核子？ |
| 原子核结构 | 整个氙核 | AFH 核响应 $W_X(y_A)$ | 给定核算符在氙核中有多大的矩阵元？ |
| 三体粒子动力学 | $\chi_1,A,s$ 的散射过程 | $\mathcal T_3^\mu$、传播子、三体相空间 | 模型以多大权重激发各核响应？ |

因此，AFH 的核响应不能替代核子形状因子；核子形状因子也不能替代 AFH 的多体核结构计算。

## 二、已经使用 AFH，为什么仍然要考虑核子 $F_1,F_2$？

对于矢量流，单个核子的 Dirac–Pauli 矩阵元可写为

$$
\boxed{
\langle N(p_N')|J_V^\mu|N(p_N)\rangle
=
\bar u_N(p_N')
\left[
F_1^V(t_A)\gamma^\mu
+\frac{iF_2^V(t_A)}{2m_N}
\sigma^{\mu\nu}q_{A,\nu}
\right]
 u_N(p_N)
}
$$

这里采用 $q_A=p_N'-p_N$ 的动量转移约定。若采用相反的 $q_A$ 定义，Pauli 项及后续非相对论表达式中的符号需要一致地改变。不同文献可能采用不同的度规、$\sigma^{\mu\nu}$ 和动量转移约定，实际程序必须固定一套约定，不能混用公式。

- $F_1^V(t_A)$ 是 Dirac 形状因子，描述核子矢量电荷分布；
- $F_2^V(t_A)$ 是 Pauli 形状因子，描述核子磁化结构；
- $t_A=q_A^2$，在非相对论散射中通常有 $t_A\simeq-|\mathbf q_A|^2$。

AFH v6.0 的核响应是对指定核算符在核态之间的矩阵元进行组织。它不会仅仅因为程序已经输出 $W_M$、$W_{\Phi''}$ 等函数，就自动替用户的 UV 模型决定有限动量下的 $F_1^V,F_2^V$。这些单核子流信息必须在核子流匹配层中提供，或者已经由所用的相对论算符输入明确包含。

在单核子冲量近似下，原子核流具有示意形式

$$
J_A^\mu(q_A)
=
\sum_{a=1}^{A}
 e^{i\mathbf q_A\cdot\mathbf r_a}
 J_{N,a}^\mu(q_A),
$$

其中 $J_{N,a}^\mu$ 是第 $a$ 个核子的 Dirac–Pauli 流。随后才将这个核子算符求和并投影到 AFH 的多极核算符基底。

### 2.1 非相对论约化后出现哪些结构？

为说明物理结构，核子流的非相对论展开可示意写成

$$
\frac{J_N^0}{2m_N}
=
F_1^V(t_A)
+
\frac{i\,[F_1^V(t_A)+2F_2^V(t_A)]}{4m_N^2}
\boldsymbol\sigma_N\cdot
(\mathbf q_A\times\mathbf K_N)
+\cdots,
$$

以及

$$
\frac{\mathbf J_N}{2m_N}
=
\frac{F_1^V(t_A)}{m_N}\mathbf K_N
+
\frac{i\,[F_1^V(t_A)+F_2^V(t_A)]}{2m_N}
\boldsymbol\sigma_N\times\mathbf q_A
+\cdots,
$$

其中

$$
\mathbf K_N=\frac{\mathbf p_N'+\mathbf p_N}{2}.
$$

以上表达式用于展示主要算符结构；精确的整体符号、归一化和高阶项必须以项目最终采用的自旋器归一化、动量转移约定及 AFH 算符定义为准。

从结构上看，核子矢量流包含：

1. 电荷密度项，主要由 $F_1^V$ 控制；
2. 电荷中的自旋—轨道项，涉及 $F_1^V+2F_2^V$；
3. 对流电流，涉及 $F_1^V\mathbf K_N$；
4. 磁化电流，涉及 $(F_1^V+F_2^V)\boldsymbol\sigma_N\times\mathbf q_A$。

因此，$F_2$ 不只是空间磁化电流中的修正；在完整的 Dirac–Pauli 电流约化中，它也会进入时间分量的自旋—轨道结构。后者正是需要检查 $\Phi''$ 及其与 $M$ 干涉的原因之一。

### 2.2 核子形状因子与 AFH 响应的主要对应

| 核子流结构 | 主要 AFH 核算符 | 相关核响应 | 说明 |
| --- | --- | --- | --- |
| 领先电荷密度 $F_1^V$ | $M$ | $W_M$ | 质量/电荷密度相干响应 |
| 电荷自旋—轨道结构 $F_1^V+2F_2^V$ | $\Phi''$ | $W_{\Phi''}$ | 还需考虑与 $M$ 的干涉 |
| 电荷通道干涉 | $M-\Phi''$ | $W_{M\Phi''}$ | 不能只计算两个对角响应 |
| 对流电流 $F_1^V\mathbf K_N$ | $\Delta$ | $W_\Delta$ | 与核子轨道运动相关 |
| 磁化电流 $(F_1^V+F_2^V)\boldsymbol\sigma_N\times\mathbf q_A$ | 主要涉及横向自旋结构 | $W_{\Sigma'}$ | 需按实际多极定义投影 |
| 对流—磁化干涉 | 相关的混合核算符 | 如 $W_{\Sigma'\Delta}$ | 是否出现及其系数由完整投影决定 |

这张表是结构层面的导航，不是可直接代入截面的最终系数表。严格计算必须从实际核子流出发，按照 AFH v6.0 的算符、相位、归一化和多极约定完成投影。

## 三、AFH 核响应数据库可以先全部计算出来

**可以先计算并保存 AFH 程序支持的全部标准核响应。** 这一步不要求先决定当前三体模型最终会显著使用哪些响应。

建议建立统一的 AFH 核响应数据库：

$$
\boxed{
\mathcal D_{\rm AFH}
=
\left\{
W_M,W_{\Sigma'},W_{\Sigma''},W_\Delta,
W_{\Phi''},W_{\widetilde\Phi'},
W_{M\Phi''},W_{\Sigma'\Delta},\ldots
\right\}
}
$$

上式表示常见 AFH 响应及其允许的干涉响应的示意集合。实际数据库应以 AFH v6.0 源程序中真实定义和输出的响应名称为准；不能仅凭文献符号推测接口，也不能假设所有响应之间都存在非零干涉项。

对每个同位素，建议保存：

- AFH 原始响应输出及其原生 Mathematica 数据；
- 对应的物理归一化响应；
- 动量转移 $Q_A=|\mathbf q_A|$ 或 $y_A$ 网格；
- 响应之间的允许干涉项；
- 核态、自旋、壳模型输入和程序版本；
- 数值精度、插值误差、网格收敛与校验结果；
- 文件哈希、计算脚本和 provenance manifest。

这样做的优点是：以后改变三体模型、核子流匹配或 Wilson 系数时，可以复用核结构数据，不必每次重新运行 AFH 核结构计算。

但需要明确：**完整 AFH 响应库只意味着在所选 AFH 核模型、算符基底和数值精度内，核响应数据准备得更完整；它不等于所有真实核物理效应都已经包含。** 例如，标准单体流响应不会自动包含任意两核子交换流或所有手征 EFT 多体流修正。

## 四、为什么不能把所有 AFH 响应直接相加？

不同 AFH 响应对应不同核算符。它们不是同一个物理量的不同数值近似，也不是可以不加权地相加的截面。

例如，假设某个动量点上有

$$
W_M=100,\qquad W_{\Phi''}=20,\qquad W_{\Sigma'}=50.
$$

直接定义

$$
W_{\rm total}=W_M+W_{\Phi''}+W_{\Sigma'}=170
$$

没有一般的物理依据。这样的相加等价于擅自假设不同核算符具有相同的动力学系数，并且忽略了响应之间可能存在的干涉。

正确的逻辑是先写出模型产生的振幅结构：

$$
\mathcal M_3
=
C_M\mathcal A_M
+C_{\Phi''}\mathcal A_{\Phi''}
+C_\Delta\mathcal A_\Delta
+C_{\Sigma'}\mathcal A_{\Sigma'}
+\cdots.
$$

平方后得到对角项和允许的干涉项：

$$
\begin{aligned}
\overline{|\mathcal M_3|^2}
={}&
|C_M|^2W_M
+|C_{\Phi''}|^2W_{\Phi''}
+|C_\Delta|^2W_\Delta
+|C_{\Sigma'}|^2W_{\Sigma'}
\\
&+2\operatorname{Re}(C_MC_{\Phi''}^*)W_{M\Phi''}
+2\operatorname{Re}(C_\Delta C_{\Sigma'}^*)W_{\Sigma'\Delta}
+\cdots.
\end{aligned}
$$

这里的式子是响应分解的示意形式；实际表达式中的运动学张量、响应归一化、同位旋指标和允许的干涉组合，必须严格使用 AFH v6.0 的定义。

更一般地，可以写成矩阵形式：

$$
\boxed{
\overline{|\mathcal M_3|^2}
\propto
\sum_{\alpha,\beta}
C_\alpha C_\beta^*
W_{\alpha\beta}^{A}(Q_A)
}
$$

其中：

- $\alpha,\beta$ 标记投影后的核算符通道；
- $C_\alpha$ 是由三体暗物质流、媒介子传播子和核子流匹配共同决定的系数；
- $W_{\alpha\beta}^{A}$ 是 AFH 核响应矩阵中的对角响应或允许的干涉响应。

并非任意 $(\alpha,\beta)$ 都对应非零响应。哪些干涉项存在，必须由角动量、宇称以及 AFH 的多极结构决定。

**因此，计算全部响应是可以的；把全部响应无权重地相加则不可以。**

## 五、核子流匹配究竟解决什么问题？

匹配的目的不是为了人为增加核响应，而是把 UV 模型给出的相互作用转换成 AFH 能识别的核算符，并确定各核响应前面的系数。

其逻辑链条为

$$
\boxed{
\text{UV 拉格朗日量}
\longrightarrow
\text{三体暗物质流 }\mathcal T_3^\mu
\longrightarrow
\text{核子流 }J_N^\mu(F_1,F_2)
\longrightarrow
\text{AFH 核算符}
\longrightarrow
\text{核响应收缩}
}
$$

对于当前 VV benchmark，核子侧通过矢量流耦合。没有相应 UV 顶点的轴矢量、赝标量或张量相互作用，不能仅因为 AFH 程序提供了相应响应，就自动加入当前模型的截面。

反过来，如果 Dirac–Pauli 流的非相对论约化确实产生了某个 AFH 核算符，那么即使该算符不是最简单的 SI 电荷项，也应在匹配后判断其贡献，而不能仅凭“模型是 vector–vector”就先验排除。

因此，匹配可以作为程序中的一个独立模块实现，不一定需要先开展一个与数值计算分离的大型理论项目。程序应自动完成：

1. 读取 UV 模型和耦合常数；
2. 构造完整三体流 $\mathcal T_3^\mu$；
3. 读取核子 $F_1^V(t_A),F_2^V(t_A)$；
4. 对核子流进行非相对论约化；
5. 将所得核算符投影到 AFH v6.0 的多极算符基底；
6. 生成各响应通道的系数及允许的干涉系数；
7. 与 AFH 核响应数据库进行收缩。

## 六、核子形状因子与相干归一化不能重复计算

当前夸克层面的矢量流为

$$
\mathcal L\supset
g_{Vq}V_\mu\sum_q\bar q\gamma^\mu q.
$$

在所采用的零动量转移归一化下，若

$$
F_1^{V,p}(0)=F_1^{V,n}(0)=3,
$$

并且已经定义

$$
g_{Vp}=g_{Vn}=g_{VN}=3g_{Vq},
$$

那么零动量核子电荷因子 3 已经包含在 $g_{VN}$ 中，不能再额外乘一次 $F_1^V(0)=3$。

有限动量下可以定义归一化 Dirac 形状

$$
f_1^V(t_A)=\frac{F_1^V(t_A)}{F_1^V(0)},
$$

并将电荷耦合写为

$$
g_{VN}(t_A)=g_{VN}(0)f_1^V(t_A).
$$

Pauli 项则应按照同一流定义单独纳入，不能把 $F_2^V(t_A)$ 当作已经包含在 $g_{VN}(0)$ 中的电荷归一化因子。

同样，AFH 核响应的归一化也必须独立核对。例如在纯等标量、$t^0=1$ 的约定下，若采用

$$
R_A(Q_A)=\frac{4\pi}{2J_A+1}W_M^{00}(y_A),
$$

并且零动量极限为

$$
R_A(0)=A^2,
$$

则：

- 若点状原子核振幅已经使用 $g_A=A g_N$，它已经包含零动量相干振幅，有限尺寸修正应使用 $R_A(Q_A)/R_A(0)$；
- 若粒子物理振幅仍然只使用单核子耦合 $g_N$，尚未进行核子相干求和，则应使用与该归一化相匹配的完整核响应。

**核子电荷因子 3 与原子核相干因子 $A^2$ 属于两个不同层次，二者都必须各自只计入一次。**

## 七、三体运动学为什么必须保留在收缩系数中？

我们的三体过程满足

$$
p_\chi+P_A=p_\chi'+P_A'+k_s.
$$

若定义

$$
q_A=P_A'-P_A,
\qquad
q_\chi=p_\chi'-p_\chi,
$$

则四动量守恒给出

$$
\boxed{q_A=-q_\chi-k_s.}
$$

因此，原子核动量转移、暗物质初末态动量差和末态标量动量不能混为一个变量。

AFH 核响应使用核子/原子核获得的动量转移 $q_A$。固定同位素和反冲能量时，非相对论核反冲给出

$$
Q_A=|\mathbf q_A|=\sqrt{2m_AE_R}.
$$

而三体暗物质流仍然依赖三体相空间点：

$$
\mathcal T_3^\mu=\mathcal T_3^\mu(q_A,q_\chi,k_s).
$$

所以对固定 $E_R$，AFH 响应的动量参数可以固定在对应的 $Q_A$，但三体动力学系数仍需在剩余相空间变量上积分。最终结构为

$$
\boxed{
\frac{d\sigma_A}{dE_R}
\propto
\int d\Phi_3\,
\sum_{\alpha,\beta}
C_\alpha(\Phi_3,Q_A)
C_\beta^*(\Phi_3,Q_A)
W_{\alpha\beta}^{A}(Q_A)
}
$$

其中 $d\Phi_3$ 表示满足三体能量、动量守恒和阈值条件的相空间测度。具体通量因子、外线归一化、传播子和相空间雅可比必须由实际三体截面公式给出，不能仅凭上式的比例符号替代。

这也说明：AFH 的核响应可以预先计算和缓存；但完整三体反冲谱不能只由 AFH 响应表直接读出。

## 八、全部 AFH 响应算出来，结果是不是精确的？

需要区分三个层次。

| 层次 | 完成内容 | 可以得出的结论 | 仍然缺少什么 |
| --- | --- | --- | --- |
| I. AFH 核响应数据库 | 计算并验证所选 AFH 模型支持的全部标准对角响应和允许的干涉响应 | 在指定核结构模型内，核响应数据较完整 | 尚未确定当前三体模型的权重，不能直接得到截面 |
| II. 三体模型与 AFH 完整收缩 | 完成三体流、核子流匹配、AFH 算符投影、干涉和三体相空间积分 | 得到 AFH v6.0 标准算符基底及所采用单体核流近似下的完整三体结果 | 仍有核结构、核流和高阶近似的不确定度 |
| III. 更完整的物理预测 | 进一步评估多体核流、核子有限尺寸、高阶修正、核模型误差、Halo 和探测器效应 | 得到带有明确误差预算的物理预测 | 仍不能称为数学意义上的绝对精确结果 |

因此，**全部 AFH 响应计算完成，不等于完整三体截面完成；完成 AFH 响应与三体流的正确收缩，也不等于自然界中所有核物理效应都已精确纳入。**

需要单独评估的误差来源包括：

1. 核壳模型空间、核波函数和单体密度矩阵的不确定性；
2. AFH 标准算符基底和多极截断；
3. 单体流近似遗漏的两核子交换流及其他多体核流；
4. 核子 $F_1,F_2$ 的输入、有限 $t_A$ 依赖及其不确定性；
5. 核子流非相对论展开中未保留的高阶项；
6. $\chi_2$ 传播子、有限宽度和两张辐射图干涉的处理；
7. 三体相空间积分的网格、求积和数值收敛；
8. 天然氙同位素丰度、Halo 速度分布和探测器响应。

同位素覆盖也必须明确检查。若当前使用的 AFH 数据集未包含 Xe-124、Xe-126，则天然氙谱不能在没有说明的情况下称为完整同位素求和；应补充相应核结构输入，或明确报告缺失同位素的处理及其影响。

## 九、建议采用的统一计算架构

建议把研究拆成相互独立、可单独验收的五个模块。

### 模块 A：AFH 完整核响应数据库

$$
\mathcal D_{\rm AFH}^{(A)}(Q_A)
=\{W_{\alpha\beta}^{(A)}(Q_A)\}.
$$

任务：

- 计算 AFH v6.0 支持的全部标准核响应；
- 保存所有程序实际输出的允许干涉响应；
- 对每个同位素统一动量网格、归一化和元数据；
- 验证零动量极限、响应矩阵性质和数值收敛。

### 模块 B：核子 Dirac–Pauli 流输入

$$
J_N^\mu=J_N^\mu(F_1^V(t_A),F_2^V(t_A)).
$$

任务：

- 固定夸克流到质子、中子的匹配约定；
- 提供 $F_1^V(t_A),F_2^V(t_A)$ 及其不确定度；
- 分别处理零动量归一化与有限动量形状；
- 防止重复计入 $F_1^V(0)$ 和 $g_{VN}$ 中的因子 3。

### 模块 C：完整三体暗物质流

$$
\mathcal T_3^\mu(p,p',k_s).
$$

任务：

- 保留两张标量辐射图；
- 保留两个 $\chi_2$ 内部传播子及其干涉；
- 使用一致的 Breit–Wigner 宽度方案；
- 计算完整的 $L^{\mu\nu}$，而不预先只保留 $L^{00}$。

### 模块 D：自动核子流投影与 AFH 收缩

$$
J_N^\mu
\longrightarrow
\{C_\alpha\}
\longrightarrow
\sum_{\alpha,\beta}C_\alpha C_\beta^*W_{\alpha\beta}^{A}.
$$

任务：

- 将核子流非相对论约化；
- 投影到 AFH v6.0 的实际多极算符定义；
- 自动生成对角项和允许的干涉项；
- 对符号、归一化、同位旋和动量转移进行一致性检查。

### 模块 E：三体反冲谱、Halo 与天然氙

$$
\frac{d\sigma_A}{dE_R}
\longrightarrow
\frac{dR_A}{dE_R}
\longrightarrow
\frac{dR_{\rm Xe}}{dE_R}.
$$

任务：

- 对三体相空间进行收敛积分；
- 逐同位素计算截面和反冲谱；
- 按天然丰度求和；
- 再进行 Halo 速度积分和探测器层面的比较。

## 十、建议设置的数值验收测试

为了保证新模块不会破坏现有已经验证的 $M$-only 基准，建议至少设置以下测试。

| 测试 | 操作 | 预期检查 |
| --- | --- | --- |
| 零动量核电荷归一化 | 令 $Q_A\to0$ | 在指定等标量约定下恢复对应的 $A^2$ 归一化 |
| 核子电荷归一化 | 检查 $F_1^V(0)$ 与 $g_{VN}$ 的定义 | 因子 3 只计入一次 |
| 点核极限 | 将有限尺寸响应归一化到零动量 | 与已有点状核基准一致 |
| $M$-only 回归 | 关闭所有非 $M$ 投影系数 | 恢复原有 $M$-only 三体结果 |
| Pauli 项开关 | 依次令 $F_2=0$ 和恢复物理 $F_2$ | 隔离 Pauli 结构对各响应的影响 |
| 干涉项检查 | 分别关闭和开启允许的干涉项 | 确认符号、相位和归一化正确 |
| 响应矩阵检查 | 检查完整收缩的实数性及平方振幅非负性 | 排除响应拼接或插值导致的非物理结果 |
| 三体运动学检查 | 独立核对 $q_A=-q_\chi-k_s$ | AFH 只使用核反冲动量转移 |
| 相空间收敛 | 提高积分阶数和网格密度 | 给出稳定的三体截面及数值误差 |
| 同位素覆盖检查 | 对照天然氙丰度表和 AFH 输入清单 | 不遗漏同位素或明确量化缺失贡献 |

## 十一、最终研究判断

对于当前 LZ 三体 VV 模型，最合理的目标不是在 $W_M$ 与其他响应之间二选一，而是把核结构计算和粒子物理匹配分层处理：

1. **核结构层面：** 尽可能完整地计算 AFH v6.0 支持的全部核响应，并建立可复用数据库；
2. **核子流层面：** 使用 $F_1^V(t_A),F_2^V(t_A)$ 完成 Dirac–Pauli 核子流匹配；
3. **三体动力学层面：** 保留 $\mathcal T_3^\mu$、两张辐射图、$\chi_2$ 传播子和三体相空间；
4. **收缩层面：** 通过 AFH 核算符投影和允许的干涉响应，构造实际的 $L_{\mu\nu}W_A^{\mu\nu}$；
5. **误差层面：** 明确 AFH 单体流近似、核结构模型、有限核子形状因子、多体核流、Halo 和探测器响应带来的不确定性。

最终计算目标可概括为

$$
\boxed{
\mathcal T_3^\mu
+J_N^\mu(F_1,F_2)
\longrightarrow
\text{AFH 全部相关核算符与响应}
\longrightarrow
\int d\Phi_3\,L_{\mu\nu}W_A^{\mu\nu}
}
$$

**最终结论：可以先把 AFH 的全部标准核响应计算出来，但不能把它们不加权地直接相加。完整的三体反冲谱必须由当前 UV 模型决定核子流与三体流，再将它们投影到 AFH 核算符，并连同允许的干涉项一起完成相空间收缩。**

这一路线既能最大限度复用已经完成的 AFH 核结构工作，也能避免把与当前模型无关的响应人为加入截面。它得到的将是 AFH v6.0 标准核算符基底及所采用核流近似下的完整三体计算，而不是不带理论误差的绝对精确结果。


---

## 十二、从 $M$-only 基准推广到完整三体反冲率

前面的讨论已经说明：AFH 核响应描述原子核对不同核算符的响应，而三体暗物质振幅和核子流匹配决定这些核算符在当前模型中的权重。现在可以把这两部分统一写进反冲率公式。

### 12.1 从原有 $M$-only 基准出发

原先采用的主基准可以写成

$$
\frac{dR_M}{dE_R}
\propto
\int d^3v\,f(\mathbf v)
\int d\Phi_3\,
R_M^{(3)}\,W_M.
$$

这里仅保留质量密度响应 $W_M$，对应当前计算中的 $M$-only 核结构近似。它是一个有用的基准，但不能预先代表完整的矢量核流结果。

### 12.2 完整三体反冲率的响应分解

完整计算应推广为

$$
\boxed{
\begin{aligned}
\frac{dR}{dE_R}
={}&
\mathcal N
\int d^3v\,f(\mathbf v)
\int d\Phi_3
\Big[
R_M^{(3)}W_M
+R_{\Phi''}^{(3)}W_{\Phi''}
+R_{M\Phi''}^{(3)}W_{M\Phi''}
\\
&\qquad\qquad
+R_{\Sigma'}^{(3)}W_{\Sigma'}
+R_{\Sigma''}^{(3)}W_{\Sigma''}
+R_{\Delta}^{(3)}W_{\Delta}
+\cdots
\Big].
\end{aligned}
}
$$

其中：

- $R_i^{(3)}$：由完整三体暗物质振幅、核子流匹配及三体运动学决定的运动学响应系数；
- $W_i$：由 AFH 核结构计算得到的核响应；
- $d\Phi_3$：包含末态暗物质、核反冲和辐射标量的完整三体相空间；
- $f(\mathbf v)$：实验室参考系下的暗物质速度分布；
- $\mathcal N$：通量、归一化、靶核数及其他公共因子。

这里的公式是将完整收缩组织成 AFH 响应形式的结构性表达。实际计算时，各项的系数、归一化、同位旋指标和允许的干涉项，必须采用 AFH v6.0 的具体定义，并由当前模型的核子流匹配确定。省略号表示其他经实际投影后确实出现的响应项，而不是要求把所有 AFH 响应无条件加入。

### 12.3 $R_i^{(3)}$ 不能照搬弹性二体散射的响应系数

这一点是从二体公式推广到三体公式时必须遵守的原则。

标准弹性 $2\to2$ 非相对论响应系数，是在弹性能量守恒关系和相应的运动学变量下推导出来的。我们的过程则是

$$
\chi_1+A\longrightarrow\chi_1+A+s.
$$

末态多出辐射标量 $s$，能量守恒中包含其能量 $\omega_s$。因此，标准弹性散射中用于构造 $\mathbf v^\perp$ 及其响应系数的两体运动学关系，不能未经推导就直接用于完整三体振幅。

正确的 $R_i^{(3)}$ 必须从完整三体振幅出发构造，并保留三体相空间变量。它们一般依赖于三体相空间点，而不只是 $E_R$ 或 $q_A^2$。

### 12.4 必须区分的三个动量变量

三体计算必须始终区分

$$
\boxed{
q_A,\qquad q_\chi,\qquad k_s
}
$$

其定义为

$$
q_A^\mu=P_A'^\mu-P_A^\mu,
$$

$$
q_\chi^\mu=p_\chi'^\mu-p_\chi^\mu,
$$

以及末态标量四动量 $k_s^\mu$。

由四动量守恒，

$$
p_\chi^\mu+P_A^\mu
=
p_\chi'^\mu+P_A'^\mu+k_s^\mu,
$$

在上述动量转移约定下有

$$
\boxed{
q_A^\mu+q_\chi^\mu+k_s^\mu=0.
}
$$

因此，$q_A$、$q_\chi$ 和 $k_s$ 是具有不同物理含义的变量，不能相互替代：

| 变量 | 物理意义 | 在计算中的用途 |
| --- | --- | --- |
| $q_A$ | 原子核初末态四动量之差 | AFH 核响应及核反冲能量 |
| $q_\chi$ | 暗物质初末态四动量之差 | 暗物质三体运动学及内部传播子 |
| $k_s$ | 末态辐射标量四动量 | 标量发射、三体相空间及传播子 |

对于初始静止、非相对论反冲的原子核，

$$
\boxed{
|\mathbf q_A|=\sqrt{2m_AE_R}.
}
$$

AFH 核响应应使用由核反冲确定的 $q_A$，而不是将其替换成暗物质初末态动量差。

### 12.5 两张标量辐射图、干涉和有限宽度必须保留

完整的三体暗物质流应写成

$$
\mathcal T_3^\mu
=
\mathcal T_{3,a}^\mu+\mathcal T_{3,b}^\mu,
$$

其中 $\mathcal T_{3,a}^\mu$ 和 $\mathcal T_{3,b}^\mu$ 分别表示两张标量辐射图。平方后必须保留

$$
\begin{aligned}
|\mathcal T_3|^2
={}&|\mathcal T_{3,a}|^2
+|\mathcal T_{3,b}|^2
\\
&+2\operatorname{Re}
\left(
\mathcal T_{3,a}\mathcal T_{3,b}^{*}
\right).
\end{aligned}
$$

两个 $\chi_2$ 内部传播子应保留模型所采用的有限宽度 Breit–Wigner 结构。不能先分别对两张图取平方，再丢弃它们之间的干涉；也不能在可能接近共振的区域把有限宽度传播子随意替换为低阶多项式。

这些效应属于三体粒子物理部分，最终进入 $R_i^{(3)}$ 及其可能的相互干涉系数，而不是由 AFH 核响应 $W_i$ 提供。

### 12.6 与完整张量收缩的关系

响应分解应当是完整三体张量收缩的组织方式，而不是替代它的独立假设。概念上，

$$
\boxed{
\frac{dR}{dE_R}
\propto
\int d^3v\,f(\mathbf v)
\int d\Phi_3\,
L_{\mu\nu}^{(3)}W_A^{\mu\nu}
}
$$

其中 $L_{\mu\nu}^{(3)}$ 由完整三体暗物质流构造，$W_A^{\mu\nu}$ 表示核流的相应响应结构。将核子流投影到 AFH 多极算符后，才可以把张量收缩整理成上一节所示的 $R_i^{(3)}W_i$ 及干涉响应之和。

因此，实际程序应遵循以下顺序：

1. 从完整三体振幅计算 $L_{\mu\nu}^{(3)}$，保留两张辐射图及其干涉；
2. 用 Dirac–Pauli 核子流 $J_N^\mu(F_1^V,F_2^V)$ 完成核子流匹配；
3. 将核子流投影到 AFH v6.0 的核算符和多极响应；
4. 根据投影结果构造 $R_i^{(3)}$ 及所有允许的干涉项；
5. 在固定 $E_R$ 下完成三体相空间积分；
6. 再进行暗物质速度积分、同位素加权及天然氙反冲率计算。

### 12.7 与原有 $M$-only 结果的关系及验收要求

完整公式应当能够退化回已经采用的 $M$-only 基准。具体而言，当关闭所有非 $M$ 的投影系数及相应干涉项时，应恢复

$$
\frac{dR}{dE_R}
\longrightarrow
\frac{dR_M}{dE_R}.
$$

建议至少完成以下逐项验收：

| 验收项目 | 检查内容 |
| --- | --- |
| $M$-only 回归 | 关闭其他响应后恢复现有基准结果 |
| 三体动量守恒 | 逐点检查 $q_A+q_\chi+k_s=0$ |
| 核响应动量输入 | 确认 AFH 只使用 $q_A$ 对应的核反冲动量 |
| 辐射图干涉 | 保留两张标量辐射图之间的交叉项 |
| 共振传播子 | 检查两个 $\chi_2$ 传播子的有限宽度处理 |
| 响应干涉 | 按 AFH 定义检查 $M$-$\Phi''$ 等允许的交叉响应 |
| 相空间收敛 | 提高三体积分精度并给出数值误差 |
| 归一化一致性 | 检查核子电荷因子、AFH 响应归一化和公共因子没有重复计入 |

**本节最终结论：** 完整三体反冲率不是把 AFH 的全部核响应直接相加，而是将完整三体暗物质动力学形成的 $R_i^{(3)}$，与核子流匹配后对应的 AFH 核响应 $W_i$ 及干涉项相乘，并在完整三体相空间和 Halo 速度分布上积分。三体运动学必须保留 $q_A$、$q_\chi$、$k_s$ 三个不同变量，同时保留两张标量辐射图的干涉和有限宽度传播子。



---

# 第十三章：AFH 核响应在三体散射中的应用及本模型的理论推广

> **本章定位**
>
> 本章补充 AFH 核响应理论在三体散射中的适用方式、相关文献先例，以及将 AFH 用于本项目暗物质标量辐射模型时必须重新推导的内容。本章是对前文的补充，不替换前面的 AFH 理论背景、核响应推导、数值结果或研究记录。
>
> **核心结论：** AFH 核响应可以用于本项目三体散射的核结构部分；但 AFH 原始弹性二体散射的粒子物理响应系数和微分截面公式不能直接照搬。需要保留 AFH 的核多极结构，并从本项目完整三体振幅重新构造三体响应系数。

## 13.1 先给出结论：AFH 可以用于三体散射，但使用层次必须正确

AFH 指 Anand–Fitzpatrick–Haxton 核响应理论。它最初解决的是：如何将暗物质与单个核子的低能相互作用嵌入具有复杂内部结构的原子核，并将核矩阵元组织成有限组核响应函数。

对单个核子的矢量流，可以采用 Dirac–Pauli 形式：

$$
\boxed{
J_N^\mu
=
\bar u_N(p_N')
\left[
F_1^V(t_N)\gamma^\mu
+
\frac{iF_2^V(t_N)}{2m_N}
\sigma^{\mu\nu}q_{N,\nu}
\right]
u_N(p_N)
}
$$

其中 $F_1^V$ 和 $F_2^V$ 描述单核子的 Dirac 电荷结构和 Pauli 磁化结构。将该单核子流嵌入氙原子核后，需要计算相应的核矩阵元：

$$
\langle A(P_A')|J_A^\mu(q_A)|A(P_A)\rangle.
$$

AFH 的作用，是把这个核矩阵元按核多极算符分解，并用核结构输入计算相应的核响应。

标准 AFH 基本响应包括：

| 核响应 | 主要物理含义 |
| --- | --- |
| $M$ | 核质量/核子密度及矢量电荷响应 |
| $\Sigma'$ | 横向自旋响应 |
| $\Sigma''$ | 纵向自旋响应 |
| $\Delta$ | 核子轨道角动量和对流结构 |
| $\Phi''$ | 自旋—轨道响应 |
| $\widetilde{\Phi}'$ | 另一类自旋—轨道相关响应 |

此外，还存在由不同核多极算符产生的干涉响应，例如

$$
W_{M\Phi''},
\qquad
W_{\Delta\Sigma'}.
$$

DMFormFactor v6.0 的具体输出通道、归一化及同位旋约定，仍应以本文前面关于 v6.0 接口的说明为准。

**关键区别：** AFH 的核结构响应可以用于三体过程；但 AFH 原本为弹性二体散射推导的 $R_i^{(2)}$、标准两体运动学关系以及二体微分截面，不能直接当作本项目三体过程的结果。

## 13.2 AFH 原始理论与三体辐射文献分别做了什么？

### 13.2.1 AFH 原始工作：弹性二体核响应

Anand、Fitzpatrick 和 Haxton 的核响应工作研究

$$
\chi+A\longrightarrow\chi+A.
$$

其核心结果是将弹性暗物质—原子核散射的振幅平方因子化为粒子物理响应与核结构响应的组合：

$$
\boxed{
\overline{|\mathcal M_{2\to2}|^2}
\sim
\sum_i R_i^{(2)}W_i
}
$$

其中：

- $R_i^{(2)}$ 是由暗物质—核子相互作用系数及弹性两体运动学决定的粒子物理响应；
- $W_i$ 是由原子核多体结构决定的核响应。

该工作建立了 AFH 核响应框架，但研究对象是弹性二体散射。它没有给出本项目中暗物质内部态跃迁并辐射标量的通用三体响应系数。

参考：

- Fitzpatrick et al., *The Effective Field Theory of Dark Matter Direct Detection*, [arXiv:1203.3542](https://arxiv.org/abs/1203.3542)。
- Anand, Fitzpatrick and Haxton, *Weakly interacting massive particle-nucleus elastic scattering response*, [arXiv:1308.6288](https://arxiv.org/abs/1308.6288), Phys. Rev. C **89**, 065501 (2014)。
- Anand, Fitzpatrick and Haxton, *Model-independent Analyses of Dark-Matter Particle Interactions*, [arXiv:1405.6690](https://arxiv.org/abs/1405.6690)。

### 13.2.2 Kouvaris–Pradler：核反冲伴随光子辐射

Kouvaris 和 Pradler 研究了核反冲伴随光子辐射的非弹性过程：

$$
\chi+A\longrightarrow\chi+A+\gamma.
$$

这是真正的 $2\to3$ 辐射过程。其关键处理是在软光子近似下，将光子 bremsstrahlung 截面与对应的弹性二体核散射截面联系起来：

$$
\boxed{
\frac{d^2\sigma}{dE_R\,d\omega}
=
\frac{4\alpha Z^2}{3\pi}
\frac{E_R}{m_A\omega}
\left(
\frac{d\sigma}{dE_R}
\right)_{2\to2}
}
$$

这里 $\omega$ 是光子能量，$m_A$ 是靶核质量。该关系依赖软光子近似及相应的辐射机制，不是任意三体过程都成立的恒等式。

这篇工作说明：核反冲伴随额外辐射粒子时，可以在特定近似下把三体过程与弹性核散射联系起来。但它研究的是核反冲相关的光子辐射，不是本项目由暗物质内部态跃迁产生的标量辐射。

参考：

- C. Kouvaris and J. Pradler, *Probing Sub-GeV Dark Matter with Conventional Detectors*, [arXiv:1607.01789](https://arxiv.org/abs/1607.01789), Phys. Rev. Lett. **118**, 031803 (2017)。

### 13.2.3 Bell et al.：核子 EFT、AFH 型核响应与光子 bremsstrahlung

Bell、Dent、Newstead、Sabharwal 和 Weiler 研究了暗物质直接探测中的 Migdal 效应与光子 bremsstrahlung，并将相关过程置于核子非相对论 EFT 框架中。

其光子辐射过程为

$$
\chi+A\longrightarrow\chi+A+\gamma.
$$

该工作在核子 EFT 部分使用核算符多极展开，并计算 $M$、$\Sigma'$、$\Sigma''$ 等核响应；文中说明其核响应由 DMFormFactor 程序计算。对光子 bremsstrahlung 部分，论文采用软光子近似下的因子化关系，将辐射率联系到弹性 $2\to2$ 截面：

$$
\frac{d^2\sigma}{dE_R\,d\omega}
=
\frac{4\alpha Z^2}{3\pi}
\frac{E_R}{m_A\omega}
\left(
\frac{d\sigma}{dE_R}
\right)_{2\to2}.
$$

因此，这篇论文提供了非常有价值的方法先例：

1. 使用核子 EFT 描述不同的暗物质—核子相互作用；
2. 将单核子算符嵌入靶核；
3. 使用 AFH/Fitzpatrick 型核多极响应描述核结构；
4. 将额外辐射过程纳入相应的相空间和事件率计算。

但需要准确理解它的适用范围：论文中的光子 bremsstrahlung 结果采用软光子因子化处理，并不是从任意完整三体振幅出发，推导适用于任意辐射粒子、任意辐射位置和任意内部传播子的通用 $R_i^{(3)}$。特别是，它没有替本项目推导暗物质内部 $\chi_1$–$\chi_2$ 跃迁并辐射标量 $s$ 时的完整三体响应系数。

参考：

- N. F. Bell, J. B. Dent, J. L. Newstead, S. Sabharwal and T. J. Weiler, *The Migdal Effect and Photon Bremsstrahlung in effective field theories of dark matter direct detection and coherent elastic neutrino-nucleus scattering*, [arXiv:1905.00046](https://arxiv.org/abs/1905.00046), Phys. Rev. D **101**, 015012 (2020)。

## 13.3 三类过程与本项目模型的区别

本项目研究的过程是

$$
\boxed{
\chi_1+A\longrightarrow\chi_1+A+s
}
$$

其中标量 $s$ 从暗物质内部线辐射出来，暗物质通过 $\chi_1$–$\chi_2$ 非对角相互作用与矢量媒介子交换发生散射。

三类研究的关键区别如下：

| 比较项目 | AFH 原始工作 | Kouvaris–Pradler / Bell et al. | 本项目 |
| --- | --- | --- | --- |
| 基本过程 | $\chi+A\to\chi+A$ | $\chi+A\to\chi+A+\gamma$ | $\chi_1+A\to\chi_1+A+s$ |
| 额外末态粒子 | 无 | 光子 $\gamma$ | 标量 $s$ |
| 辐射位置/机制 | 无辐射 | 核反冲相关的光子 bremsstrahlung | 暗物质内部线辐射 |
| 核结构处理 | AFH 核响应 | 核子 EFT 与 AFH/Fitzpatrick 型响应 | 需要使用 AFH 核响应并完成本模型匹配 |
| 三体动力学 | 不涉及 | 软光子近似及相应辐射相空间 | 完整三体振幅、内部态传播子及两图干涉 |
| 可直接复用的内容 | 核响应理论和核结构输入 | 核子 EFT、核响应及特定软光子方法 | AFH 核结构部分可复用；三体响应系数必须重新推导 |

由此可以得到一个准确判断：

**已有文献证明了额外辐射过程与 AFH 型核响应可以放在同一个计算框架中，但这些文献并没有直接给出本项目暗物质内部标量辐射模型所需的完整三体 AFH 响应系数。**

## 13.4 为什么本项目仍然可以复用 AFH 核结构部分？

本项目的标量 $s$ 从暗物质内部线辐射。若满足以下条件：

1. 原子核通过一个矢量流与暗物质相互作用；
2. 标量只从暗物质内部线辐射，不直接从核子或核子间相互作用顶点辐射；
3. 原子核保持弹性，初末态属于同一个核能级；
4. 核侧仍采用与 AFH 数据相一致的单体核流近似；
5. 矢量媒介子与核流之间的耦合可以按单一核流顶点因子化；

那么，额外标量辐射改变的是暗物质侧的动力学流，而不是自动改变原子核的内部波函数或 AFH 多极算符定义。

在把媒介子传播子和耦合吸收到暗物质侧流的约定下，振幅可写成

$$
\boxed{
\mathcal M_3
=
\mathcal T_3^\mu J^A_\mu(q_A)
}
$$

如果不把媒介子传播子吸收到 $\mathcal T_3^\mu$，则应显式写成

$$
\mathcal M_3
=
\mathcal T_3^\mu
D_{\mu\nu}(q_A)
J_A^\nu(q_A).
$$

其中：

- $\mathcal T_3^\mu$ 是完整三体暗物质侧流；
- $D_{\mu\nu}(q_A)$ 是矢量媒介子的传播子；
- $J_A^\nu(q_A)$ 是原子核矢量流。

因此，核结构部分仍然由

$$
J_A^\mu(q_A)
=
\langle A(P_A')|\hat J_A^\mu(q_A)|A(P_A)\rangle
$$

描述。对该核流进行非相对论约化和多极投影后，可以使用与当前核流相匹配的 AFH 核响应。

**这里的“复用 AFH”是复用核结构矩阵元和核响应定义，不是复用 AFH 原始弹性二体散射的全部粒子物理响应系数。**

以下情况则不能简单沿用现有弹性 AFH 核响应而不作扩展：

- 标量 $s$ 直接耦合到核子或核内自由度；
- 辐射发生在核子流或核子间相互作用部分；
- 原子核发生内部激发或非弹性跃迁；
- 两体交换流、核介质修正或其他核多体流达到所需精度而不能忽略。

这些情形会改变核侧算符或核态矩阵元，需要相应扩展核流和核响应。

## 13.5 本项目必须重新推导的三体粒子物理部分

### 13.5.1 完整三体暗物质流

本项目的完整三体振幅包含两张标量辐射图：

$$
\boxed{
\mathcal T_3^\mu
=
\mathcal T_{3,a}^\mu
+
\mathcal T_{3,b}^\mu
}
$$

两张图分别对应标量辐射发生在矢量相互作用的不同一侧。必须保留：

- $\chi_1$ 与 $\chi_2$ 的非对角相互作用；
- 中间态虚 $\chi_2$ 的完整传播子；
- 标量辐射顶点；
- 矢量媒介子传播子；
- 两张辐射图之间的干涉；
- 共振附近有限宽度的处理。

因此，不能把完整三体振幅替换成一个弹性二体振幅乘以与光子软辐射相同的通用因子。光子软辐射近似的适用条件不能自动转移到暗物质内部线的标量辐射。

### 13.5.2 三体粒子物理张量

由完整三体流构造粒子物理张量：

$$
\boxed{
L_{\mu\nu}^{(3)}
=
\frac{1}{2s_\chi+1}
\sum_{\text{DM spins}}
\mathcal T_{3,\mu}
\mathcal T_{3,\nu}^{*}
}
$$

其中 $s_\chi$ 是初态暗物质自旋。具体的初态平均、末态求和以及公共耦合因子，应与实际振幅归一化保持一致。

核侧张量可定义为

$$
\boxed{
W_A^{\mu\nu}
=
\frac{1}{2J_A+1}
\sum_{M_A,M_A'}
J_A^\mu(M_A',M_A)
J_A^{\nu *}(M_A',M_A)
}
$$

其中 $J_A$ 是靶核基态自旋，$M_A,M_A'$ 是初末态磁量子数。

在流因子化成立且公共传播子、耦合已按约定放入相应张量时，有

$$
\boxed{
\overline{|\mathcal M_3|^2}
=
L_{\mu\nu}^{(3)}W_A^{\mu\nu}
}
$$

这一表达式是从完整三体振幅出发的起点。下一步才是将核侧张量投影到 AFH 多极响应。

### 13.5.3 从完整张量到三体 AFH 响应系数

经过核子流匹配和 AFH 多极投影后，完整张量收缩可以按 AFH 核响应组织为

$$
\boxed{
L_{\mu\nu}^{(3)}W_A^{\mu\nu}
\ \longrightarrow\
\sum_X R_X^{(3)}W_X
+
\sum_{X<Y}R_{XY}^{(3)}W_{XY}
}
$$

其中：

- $W_X$ 是 AFH 对角核响应；
- $W_{XY}$ 是 AFH 允许的核响应干涉项；
- $R_X^{(3)}$ 和 $R_{XY}^{(3)}$ 是由本项目完整三体振幅、核子流匹配及三体运动学决定的系数。

这些三体响应系数一般依赖三体相空间点，不能直接照搬 AFH 弹性二体散射中的 $R_X^{(2)}$。

在实际计算中，应从本项目的 $J_N^\mu(F_1^V,F_2^V)$ 出发，完成非相对论约化和多极投影，再确定哪些 AFH 响应确实出现。不能因为 AFH 程序能够输出某个 $W_X$，就将它无条件加入三体截面。

## 13.6 三体运动学：必须统一动量定义与符号约定

本项目必须区分三个四动量：

$$
q_A^\mu=P_A'^\mu-P_A^\mu,
$$

$$
q_\chi^\mu=p_\chi'^\mu-p_\chi^\mu,
$$

$$
k_s^\mu=p_s^\mu.
$$

由四动量守恒，

$$
p_\chi^\mu+P_A^\mu
=
p_\chi'^\mu+P_A'^\mu+k_s^\mu,
$$

因此，在本文统一采用的约定下，

$$
\boxed{
q_A^\mu+q_\chi^\mu+k_s^\mu=0.
}
$$

若另一本笔记将暗物质动量转移定义为相反方向，

$$
q_{\chi,\mathrm{in-out}}^\mu
=
p_\chi^\mu-p_\chi'^\mu
=
-q_\chi^\mu,
$$

则同一守恒关系写成

$$
\boxed{
q_A^\mu
=
q_{\chi,\mathrm{in-out}}^\mu-k_s^\mu.
}
$$

这两种写法只是暗物质动量转移的符号约定不同，物理内容相同。后续代码和文档必须固定使用其中一种，不能混用。

AFH 核响应使用原子核实际接受的空间动量转移：

$$
\boxed{
Q_A^2=|\mathbf q_A|^2.
}
$$

对于初始静止、非相对论反冲的原子核，

$$
\boxed{
Q_A^2\simeq 2m_AE_R,
\qquad
t_A=q_A^2\simeq-2m_AE_R.
}
$$

其中 $Q_A^2$ 是空间动量平方，而 $t_A$ 是四动量转移不变量。AFH 的无量纲变量由 $Q_A$ 构造：

$$
y_A=\left(\frac{Q_A b_A}{2}\right)^2.
$$

因此，不能把 $q_\chi$ 或 $k_s$ 直接作为 AFH 核响应的动量输入。三体相空间会改变给定反冲能量下的暗物质侧运动学，但 AFH 核结构响应仍以核子流所传递的 $q_A$ 为自变量。

## 13.7 本项目完整三体 AFH 反冲率的结构

原有 $M$-only 基准为

$$
\frac{dR_M}{dE_R}
\propto
\int d^3v\,f(\mathbf v)
\int d\Phi_3\,
R_M^{(3)}W_M.
$$

推广到完整核流后，结构上应写为

$$
\boxed{
\begin{aligned}
\frac{dR}{dE_R}
={}&
\mathcal N
\int d^3v\,f(\mathbf v)
\int d\Phi_3\,
\delta\!\left(E_R-E_R^{\mathrm{kin}}\right)
\\
&\times
\left[
\sum_X R_X^{(3)}W_X
+
\sum_{X<Y}R_{XY}^{(3)}W_{XY}
\right].
\end{aligned}
}
$$

这里：

- $R_X^{(3)}$：三体暗物质流与核子流匹配后得到的对角响应系数；
- $R_{XY}^{(3)}$：不同 AFH 多极算符之间的三体干涉系数；
- $W_X$：AFH 核结构对角响应；
- $W_{XY}$：AFH 核结构干涉响应；
- $d\Phi_3$：末态暗物质、原子核和标量的完整三体相空间；
- $f(\mathbf v)$：暗物质速度分布；
- $\mathcal N$：通量、归一化、靶核数及其他公共因子；
- $\delta(E_R-E_R^{\mathrm{kin}})$：固定核反冲能量的运动学约束。

上式是完整收缩的结构性表达。实际实现时，必须按 AFH v6.0 的具体归一化、同位旋指标和干涉响应定义逐项展开，不能把所有 AFH 响应无权重地相加。

当关闭所有非 $M$ 响应系数及其干涉项时，完整结果必须退化回已经验证的 $M$-only 基准：

$$
\boxed{
\left.
\frac{dR}{dE_R}
\right|_{\text{$M$ only}}
=
\frac{dR_M}{dE_R}.
}
$$

## 13.8 哪些内容可以复用，哪些必须重新推导？

| 理论或计算内容 | 是否需要重新推导 | 处理原则 |
| --- | --- | --- |
| AFH 核多极算符定义 | 不需要从头推导 | 采用 AFH 原始定义及 v6.0 约定 |
| 已验证的 Xe 同位素 OBDME | 不需要重新计算 | 核流和核结构近似相同时复用 |
| AFH $W_X(Q_A)$ 核响应 | 不因增加暗物质侧标量辐射而自动重算 | 确认核子流投影与现有响应定义一致 |
| 两张标量辐射费曼图 | 必须重新计算 | 使用本项目完整三体振幅 |
| $\chi_2$ 传播子及有限宽度 | 必须重新处理 | 保留两图干涉和共振行为 |
| 三体张量 $L_{\mu\nu}^{(3)}$ | 必须重新推导 | 从完整 $\mathcal T_3^\mu$ 构造 |
| Dirac–Pauli 核子流到 AFH 算符的投影 | 必须完成模型匹配 | 明确 $F_1^V,F_2^V$ 对各核多极的系数 |
| 三体响应系数 $R_X^{(3)}$ | 必须重新推导 | 不使用弹性二体 $R_X^{(2)}$ 替代 |
| 完整三体相空间积分 | 必须重新计算 | 对固定 $E_R$ 积分并检查收敛 |
| 天然氙同位素组合 | 使用已验证核响应后重新组合 | 每个同位素使用自己的 AFH 响应 |

## 13.9 对本项目的具体推导路线

建议按照以下顺序完成：

1. **完整三体振幅：** 从两张标量辐射费曼图出发，保留完整 $\chi_2$ 传播子、有限宽度和图间干涉。
2. **核子矢量流：** 使用 Dirac–Pauli 流 $J_N^\mu(F_1^V,F_2^V)$，固定核子动量转移和 form factor 约定。
3. **非相对论约化：** 对核子流逐分量展开，区分时间分量、纵向空间流和横向空间流。
4. **AFH 多极投影：** 将得到的核子算符投影到 $M,\Phi'',\Delta,\Sigma',\Sigma''$、$\widetilde\Phi'$ 等 AFH 多极算符，判断哪些通道实际出现。
5. **干涉项：** 对投影后允许的通道计算相应干涉，例如 $M-\Phi''$ 和 $\Sigma'-\Delta$；是否存在以及系数大小必须由实际流结构决定。
6. **三体响应系数：** 从完整三体张量计算 $R_X^{(3)}$ 和 $R_{XY}^{(3)}$，不直接使用弹性二体响应系数。
7. **张量收缩验证：** 对若干运动学点，直接计算 $L_{\mu\nu}^{(3)}W_A^{\mu\nu}$，并与 AFH 响应分解结果逐点对照。
8. **基准回归：** 关闭非 $M$ 投影后恢复已有 $M$-only 结果。
9. **完整反冲率：** 完成三体相空间积分，并在后续计算中进行速度分布和同位素加权。

## 13.10 必须完成的理论和数值验收

| 验收项目 | 具体要求 |
| --- | --- |
| 文献适用范围 | 区分 AFH 弹性二体框架、软光子 bremsstrahlung 先例和本项目暗物质线标量辐射 |
| 核流因子化 | 验证媒介子传播子及耦合放置方式，避免重复计入 |
| 动量守恒 | 按本文固定约定逐点验证 $q_A+q_\chi+k_s=0$ |
| AFH 动量输入 | 确认核响应只使用 $Q_A=|\mathbf q_A|$ |
| 两张辐射图 | 分别验证两张图及其交叉干涉 |
| 有限宽度 | 检查 $\chi_2$ 传播子的宽度约定和共振附近稳定性 |
| 核子流匹配 | 检查 $F_1^V,F_2^V$、符号、动量幂次及同位旋分解 |
| 多极投影 | 检查 AFH 算符的角动量、宇称和多极选择规则 |
| 响应干涉 | 检查交叉响应的相位、归一化及数值一致性 |
| $M$-only 回归 | 关闭非 $M$ 项后恢复原有基准 |
| 直接张量对照 | 比较直接 $L_{\mu\nu}^{(3)}W_A^{\mu\nu}$ 与响应分解 |
| 相空间收敛 | 提高积分精度并记录数值误差 |

## 13.11 本章最终结论

本项目不需要重新发明 AFH 核响应理论，也不需要因为暗物质末态多出一个标量，就自动重新计算相同核结构输入下的全部氙核 OBDME 和 AFH 核响应。

需要做的是：

- **复用 AFH 核结构理论：** 使用已有的核多极算符、密度矩阵、核响应函数和经过验证的同位素输入；
- **重新推导三体粒子物理：** 从完整的 $\chi_1$–$\chi_2$ 标量辐射振幅构造 $L_{\mu\nu}^{(3)}$；
- **完成模型特定的核子流匹配：** 将 Dirac–Pauli 核子流投影到 AFH 核算符，确定实际出现的响应和干涉项；
- **完成三体收缩：** 从 $L_{\mu\nu}^{(3)}W_A^{\mu\nu}$ 得到本模型的 $R_X^{(3)}W_X$ 组合，再进行三体相空间积分。

因此，文献中已有 AFH 核响应和三体光子辐射相结合的相关先例，但这些先例不等同于本项目所需的暗物质内部标量辐射三体公式。**本项目需要完成的是 AFH 核响应在特定三体标量辐射模型中的模型依赖推广，而不是从零重做 AFH 核结构理论。**

---

## 本章参考文献

1. A. L. Fitzpatrick et al., *The Effective Field Theory of Dark Matter Direct Detection*, [arXiv:1203.3542](https://arxiv.org/abs/1203.3542)。
2. N. Anand, A. L. Fitzpatrick and W. C. Haxton, *Weakly interacting massive particle-nucleus elastic scattering response*, [arXiv:1308.6288](https://arxiv.org/abs/1308.6288), Phys. Rev. C **89**, 065501 (2014)。
3. N. Anand, A. L. Fitzpatrick and W. C. Haxton, *Model-independent Analyses of Dark-Matter Particle Interactions*, [arXiv:1405.6690](https://arxiv.org/abs/1405.6690)。
4. C. Kouvaris and J. Pradler, *Probing Sub-GeV Dark Matter with Conventional Detectors*, [arXiv:1607.01789](https://arxiv.org/abs/1607.01789), Phys. Rev. Lett. **118**, 031803 (2017)。
5. N. F. Bell, J. B. Dent, J. L. Newstead, S. Sabharwal and T. J. Weiler, *The Migdal Effect and Photon Bremsstrahlung in effective field theories of dark matter direct detection and coherent elastic neutrino-nucleus scattering*, [arXiv:1905.00046](https://arxiv.org/abs/1905.00046), Phys. Rev. D **101**, 015012 (2020)。

