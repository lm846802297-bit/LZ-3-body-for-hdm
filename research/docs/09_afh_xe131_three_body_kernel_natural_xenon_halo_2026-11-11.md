# AFH v6.0 氙核响应与三体暗物质散射：对话整理及阶段性研究记录

> 整理日期：2026-11-11  
> 对话来源：[ChatGPT 分享对话](https://chatgpt.com/share/6af4660e-e388-83ea-a86a-2482b065dcea)  
> 对应研究仓库：`lm846802297-bit/LZ-3-body-for-hdm`  
> 当前归档位置：PR #7 的研究分支  
> 研究对象：\(\chi_1+A\rightarrow\chi_1+A+s\) 三体核反冲过程

## 摘要

本次讨论的核心，是把论文 Eq. (6) 中的三体微分散射截面与真实氙靶的核结构和银河系暗物质速度分布连接起来。研究分成三个层次：

1. **单一同位素、固定入射速度：** 计算 \(d\sigma_A/dE_R\)，其中核响应 \(R_A(E_R)\) 与三体相空间积分 \(I_6\) 在给定同位素和运动学条件下因式分解。
2. **核结构输入：** 采用 AFH/DMFormFactor v6.0 内置的 Xe-131 default density matrix，严格使用文献给出的谐振子长度处方，不把 \(b_A\) 当作拟合参数；并处理 AFH 原始 isoscalar response 与物理等质子、等中子耦合之间的因子 4。
3. **真实天然氙靶的理论速率：** 对可用氙同位素按天然丰度求和，并对实验室系暗物质速度分布积分，得到 \(dR/dE_R\)。这一步与固定速度下的 \(d\sigma_A/dE_R\) 是不同的物理量。

目前已经形成 AFH default Xe-131 响应、GCN/JJ55 对照、四组固定速度 benchmark，以及天然氙 selected-point halo-folded rate 的可复现归档。Xe-131 AFH Python 响应已通过 60 位精度 mpmath 对全部 2401 个 q 节点的独立有限和对照；原生 Mathematica 程序仍未在 Wolfram kernel 中实际运行。另已发现天然氙 28 个 AFH 响应样本采用 exact-q，而论文当前核响应定义对应 NR-q；旧速率保留为 legacy 结果，新的七同位素 NR-q 响应尚待重新生成。天然氙结果仍是理论 selected-point rates，尚不是完整的 LZ detector-level likelihood/recast。

---

## 1. 研究问题与物理对象

考虑三体非弹性散射过程

\[
\chi_1+A\longrightarrow \chi_1+A+s,
\]

其中 \(A\) 是氙核，\(s\) 是末态标量。暗物质初态质量为 \(m_{\chi_1}\)，中间态质量写作

\[
m_{\chi_2}=m_{\chi_1}+\Delta m.
\]

论文 Eq. (6) 给出单个核靶的微分散射截面。它描述的是：**指定一个核同位素 \(A\)，并指定一个入射暗物质速度时，每个核发生三体散射的微分截面。**

这还不是 LZ 实验直接测量的事件率。真实探测器使用天然氙靶，入射暗物质也不是单一速度，因此从微分截面到探测器理论速率还需要两次求和/积分：

- 对天然氙中不同同位素的贡献按原子丰度加权；
- 对实验室系暗物质速度分布进行积分。

这两个步骤分别处理靶核组成和入射粒子通量，不能提前混入单一同位素、固定速度的截面公式。

## 2. Eq. (6)：三体积分与核响应的因式分解

采用的微分截面结构为

\[
\frac{d\sigma_A}{dE_R}
=
\frac{
m_A(g_1g_2g_{VN})^2 R_A(E_R)
}{
256\pi^3p_{\chi_1}^2
(m_V^2+2m_AE_R)^2
}
I_6,
\]

其中

\[
I_6 =
\int_{W_{\min}^2}^{W_{\max}^2}
dW^2\,
\sqrt{\lambda(W^2,m_{\chi_1}^2,m_s^2)}
\int_{-1}^{1} dz\,
\left\langle\mathcal L_{00}\right\rangle_{\phi_*}.
\]

这里：

- \(m_A\)：目标核质量；
- \(E_R\)：核反冲能量；
- \(p_{\chi_1}\)：靶核静止系中的入射暗物质动量；
- \(m_V\)：交换矢量粒子质量；
- \(R_A(E_R)\)：核结构响应；
- \(W^2\)：三体子系统积分变量；
- \(z=\cos\theta_*\)：三体子系统中的角变量；
- \(\phi_*\)：相应方位角；
- \(\mathcal L_{00}\)：靶核静止系时间分量对应的粒子侧振幅张量；
- \(\lambda\)：Källén 函数。

### 2.1 为什么核响应可以从三体积分中提出？

在固定同位素、固定 \(E_R\)、固定入射速度和固定粒子物理 benchmark 时，核响应只通过 \(R_A(E_R)\) 乘在截面前面，而 \(I_6\) 包含粒子侧矩阵元和三体相空间积分。因此，对同一组运动学条件：

\[
\left.\frac{d\sigma_A}{dE_R}\right|_{\rm AFH}
:
\left.\frac{d\sigma_A}{dE_R}\right|_{\rm GCN}
:
\left.\frac{d\sigma_A}{dE_R}\right|_{\rm JJ55}
=
R_A^{\rm AFH}
:
R_A^{\rm GCN}
:
R_A^{\rm JJ55}.
\]

所以 AFH、GCN 和 JJ55 的核结构对照可以共用同一个 \(I_6\)，只替换 \(R_A(E_R)\)。这是给定公式的因式分解，不是为不同核模型分别引入新的近似。

但这个结论只适用于**同一个同位素和相同运动学条件**。换成另一个氙同位素后，\(m_A\)、核反冲运动学和三体相空间边界都会变化，必须使用该同位素对应的 \(I_6\) 和阈值，不能把 Xe-131 的积分直接当作所有同位素的积分。

### 2.2 固定速度截面与 halo-folded rate 的区别

\(d\sigma_A/dE_R\) 是单核截面。真实的单位质量靶在单位时间内产生多少事件，还要乘以暗物质数密度和速度通量，并对速度分布积分。因此：

- 固定 \(v\) 的 \(d\sigma_A/dE_R\) 适合复现论文的运动学曲线；
- \(dR/dE_R\) 才是可以继续与探测器曝光、效率和能量响应结合的理论事件率。

两者不能混称为同一条“探测器谱”。

## 3. AFH v6.0 default Xe-131 核响应

### 3.1 数据来源与固定处方

本阶段采用 Anand–Fitzpatrick–Haxton (AFH) 的 DMFormFactor v6.0 内置 Xe-131 default density matrix：

- 内置矩阵名称：`sdgXe131`；
- 同位素选择：`SetIsotope[54,131,"default","default"]`；
- 密度矩阵条目：67 项；
- 核自旋：\(J_A=3/2\)；
- 原子序数：\(Z=54\)。

AFH default 谐振子长度处方固定为

\[
\boxed{
b_A =
\sqrt{
\frac{41.467}
{45A^{-1/3}-25A^{-2/3}}
}\ {\rm fm}
}
\]

Xe-131 对应

\[
b_{131}=2.2923417985218975\ {\rm fm}
\approx 2.292342\ {\rm fm}.
\]

Xe-128 至 Xe-136 这组可用同位素的处方值约为 \(2.284596\)–\(2.304942\) fm。GCN/JJ55 的同核素比较使用相同的 \(b_A\) 处方。

**重要决策：不把 \(b_A\) 当作任意拟合参数，也不通过调节 \(b_A\) 去匹配 Figure 2 的谷值。** 这样可以避免把核模型输入的人为调参误认为独立的物理验证。

来源和数据完整性信息：

- AFH 原始压缩包 SHA-256：`4e0f70e6e780f3f4a40faa14792cae239d1989cf15d1e211b4fd7389b0460727`；
- Mathematica 源文件：`v6/dmformfactor-V6.m`；
- 源文件 SHA-256：`dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372`。

### 3.2 AFH isoscalar response 的因子 4

这是本轮最重要的归一化问题之一。

AFH v6.0 的原始 isoscalar response 并不直接等于以物理单核子耦合 \(g_{VN}\) 定义的等质子、等中子相干响应。AFH 程序中的系数约定使用

\[
c^0=\frac{c^p+c^n}{2},
\qquad
c^1=\frac{c^p-c^n}{2}.
\]

其内置 isoscalar response 在零动量处满足

\[
\frac{4\pi}{2J_A+1}
W_{M,\mathrm{AFH}}^{00}(0)
\simeq \frac{A^2}{4}.
\]

而论文截面中的 \(g_{VN}\) 是物理的等质子、等中子核子耦合：

\[
g_p=g_n=g_{VN}.
\]

因此零动量下的相干核振幅正比于

\[
Zg_p+(A-Z)g_n=A g_{VN},
\]

相应的物理相干响应必须满足

\[
R_A^{\rm phys}(0)=A^2.
\]

在 AFH 接口的系数约定下，物理单核子耦合对应的 isoscalar 输入系数为 \(c_0=2g_{VN}\)，所以振幅平方带来因子 4。若截面前因子仍写成物理的 \(g_{VN}\)，就必须把这一个因子 4 放入核响应定义中。

对于原始 AFH v6.0 输出，物理响应的解析映射写作

\[
R_A^{\rm phys}(E_R)
=
\frac{16\pi}{2J_A+1}
W_{M,\mathrm{AFH}}^{00}(y).
\]

**因子 4 只能计入一次。** 不能既在 \(R_A\) 中乘 4，又在粒子—核子耦合处再乘一次；也不能把 AFH 原始 \(A^2/4\) 归一化响应直接当成物理 \(A^2\) 响应使用。

### 3.3 密度矩阵有限精度与零动量归一化

Xe-131 的源代码数值翻译给出

\[
\frac{4\pi}{2J_A+1}
W_{M,\mathrm{AFH}}^{00}(0)
=
4289.895955714993,
\]

而

\[
\frac{A^2}{4}=\frac{131^2}{4}=4290.25.
\]

相对差异约为 \(8.2523\times10^{-5}\)，与 AFH 内置密度矩阵系数有限小数精度相符。

因此，归档的响应形状使用自身的计算零动量值作归一化：

\[
\boxed{
R_A^{\rm phys}(q)
=
A^2
\frac{R_{A,\mathrm{AFH}}^{00}(q)}
{R_{A,\mathrm{AFH}}^{00}(0)}
}
\]

这样保留完整的 AFH \(q\) 依赖，只消除一个很小的整体有限精度偏移，并保证

\[
R_{131}^{\rm phys}(0)=131^2=17161.
\]

这一数值归一化不是通过移动谷值或调整 \(b_A\) 实现的。

### 3.4 AFH default 的三个主要响应极小值

AFH default Xe-131 响应在 Figure 2 相关范围内得到三个主要极小值：

| 极小值 | \(q_{\min}\) [MeV] | \(E_{R,\min}\) [keV] | \(R_{\min}/R(0)\) |
|---|---:|---:|---:|
| 1 | 157.93578 | 102.20672 | \(1.23638\times10^{-5}\) |
| 2 | 256.27187 | 269.10390 | \(6.34070\times10^{-8}\) |
| 3 | 365.06657 | 546.08690 | \(1.56194\times10^{-7}\) |

此外，在约 \(1021.8\) keV 还有一个更高反冲能量的极小值，不属于 Figure 2 的三个主要谷值范围。

## 4. AFH、GCN 与 JJ55 的对照

三种核结构处方的极小值位置接近，但极小值深度存在模型依赖性：

| 极小值 | 模型 | \(E_{R,\min}\) [keV] | \(R_{\min}/R(0)\) |
|---|---|---:|---:|
| 1 | AFH default | 102.20672 | \(1.23638\times10^{-5}\) |
| 1 | GCN | 101.32097 | \(3.35029\times10^{-6}\) |
| 1 | JJ55 | 100.67637 | \(6.27964\times10^{-8}\) |
| 2 | AFH default | 269.10390 | \(6.34070\times10^{-8}\) |
| 2 | GCN | 269.06059 | \(4.00740\times10^{-8}\) |
| 2 | JJ55 | 270.10365 | \(3.86281\times10^{-9}\) |
| 3 | AFH default | 546.08690 | \(1.56194\times10^{-7}\) |
| 3 | GCN | 551.13818 | \(8.41024\times10^{-8}\) |
| 3 | JJ55 | 554.89265 | \(3.50392\times10^{-9}\) |

这说明：

1. 三种核结构计算都在相近的动量转移区域产生极小值；
2. 极小值的深度对核结构模型较敏感，尤其是 JJ55；
3. 不能为了让三条曲线的谷值重合而调节 \(b_A\)；
4. 在相同粒子物理输入和同一 \(I_6\) 下，截面差异应由 \(R_A(E_R)\) 的差异解释。

一个独立的固定运动学对照点（\(m_s=300\) keV、\(\Delta m=450\) keV、\(v=776\) km/s）给出：

| \(E_R\) [keV] | 核模型 | \(R_A\) | \(d\sigma_A/dE_R\) [cm²/keV] |
|---:|---|---:|---:|
| 267 | AFH | 0.005597764 | \(1.38050\times10^{-35}\) |
| 267 | GCN | 0.004841354 | \(1.19396\times10^{-35}\) |
| 267 | JJ55 | 0.009210023 | \(2.27134\times10^{-35}\) |
| 542 | AFH | 0.003151130 | \(2.34020\times10^{-36}\) |
| 542 | GCN | 0.003843381 | \(2.85431\times10^{-36}\) |
| 542 | JJ55 | 0.005093560 | \(3.78276\times10^{-36}\) |

该表是**同一 \(I_6\) 下的核响应替换对照**，不是天然氙 halo-folded rate。

## 5. 四组 Figure 2 固定速度 benchmark

Xe-131 四组固定速度 benchmark 的输入为：

| 曲线 | \(m_s\) | \(\Delta m\) | 第一个开放的 5 keV 网格点 |
|---|---:|---:|---:|
| Red | 200 keV | 1 MeV | 35 keV |
| Green | 300 keV | 1 MeV | 100 keV |
| Black | 360 keV | 1 MeV | 190 keV |
| Blue | 300 keV | 10 MeV | 100 keV |

公共输入：

\[
m_{\chi_1}=1\ {\rm TeV},\quad
m_V=10\ {\rm GeV},\quad
g_2=1,\quad
(g_1g_2g_{VN})^2=10^{-8}.
\]

- 固定入射速度：\(v=800\) km/s；
- 反冲能量网格：5–800 keV，步长 5 keV；
- Xe-131 核质量：\(m_A=122.02572742\) GeV；
- 核响应：AFH default、GCN、JJ55。

归档表包含 \(4\) 个 benchmark、\(3\) 种核响应和每组 \(160\) 个反冲能量点，共 \(1920\) 行。AFH 使用 2401 点响应表作 PCHIP 插值，不外推。

### 5.1 \(I_6\) 的独立性和收敛检查

在同一同位素和相同运动学条件下，AFH/GCN/JJ55 共用 \(I_6\)。四组 benchmark 的归档计算复用了既有 Eq. (6) 三体积分网格；因此这项工作是对核响应替换的完整对照，不应误称为重新独立计算了全部 640 个三体积分点。

独立数值检查包括：

- 12 个代表点比较 \(24\times24\times12\) 与 \(32\times32\times16\) 求积，最大相对差异 \(5.996\times10^{-6}\)；
- 代表点的 \(16\times16\times8\) 与 \(32\times32\times16\) 对照差异约为 \(3\times10^{-5}\)；
- 截面由表中 \(R_A\) 和 \(I_6\) 重构的最大相对残差为 0；
- AFH/GCN 的截面比逐点等于对应核响应比。

另一个单点诊断为 \(m_s=0.3\) MeV、\(\Delta m=1\) MeV、\(E_R=200\) keV、\(v=776\) km/s，得到

\[
I_6=878078.840766\ {\rm GeV}^2.
\]

该单点与上面的四组 \(v=800\) km/s Figure 2 benchmark 不应混为同一套输入。

### 5.2 固定 \(v=800\) km/s 的适用边界

固定 \(v=800\) km/s 是用于复现固定速度截面曲线的诊断选择，不是标准 halo 中的典型速度，也不是截断 SHM 中允许的速度。后文采用的截断 SHM 实验室系速度上限是 776 km/s。因此，不能把 \(v=800\) km/s 的固定速度截面直接解释为截断 SHM 下的天然氙事件率。

## 6. 为什么要考虑氙同位素和暗物质速度分布？

### 6.1 LZ 是什么探测器？

LZ 指 LUX-ZEPLIN 暗物质实验。其核心靶体是双相液氙时间投影室（dual-phase liquid-xenon TPC），使用约 7 吨 active liquid xenon 搜索暗物质与氙核散射产生的核反冲信号。官方探测器介绍：

- https://lz.lbl.gov/detector/

因此，LZ 的靶不是单一的 Xe-131 核，而是天然氙同位素混合物。Xe-131 单同位素计算是重要的核响应基准，但若要得到天然氙靶的理论速率，就必须对同位素组成进行处理。

### 6.2 天然氙同位素求和

当前 AFH v6.0 内置 default density matrix 可用的天然氙同位素为：

\[
{}^{128}{\rm Xe},\ {}^{129}{\rm Xe},\ {}^{130}{\rm Xe},\
{}^{131}{\rm Xe},\ {}^{132}{\rm Xe},\ {}^{134}{\rm Xe},\
{}^{136}{\rm Xe}.
\]

这七种同位素覆盖 NIST 天然原子丰度的

\[
0.998158.
\]

Xe-124 与 Xe-126 合计约 \(0.001842\)，因为当前提供的 AFH v6.0 响应集合没有相应内置密度矩阵，故本轮没有纳入。**七种可用同位素的丰度没有重新归一化**，不能把缺失的丰度简单重新分配给其余同位素。

每种同位素分别使用：

- 自己的核质量；
- 自己的 AFH response；
- 自己的三体相空间边界和 \(v_{\min,A}\)。

核质量采用

\[
m_A=\left[M_{\rm atom}(A)-54m_e\right]u,
\]

忽略很小的电子结合能。每千克天然氙的靶核数使用 NIST 丰度加权平均原子质量

\[
\overline M_{\rm Xe}=131.2927614479\ {\rm g/mol},
\]

\[
N_T=\frac{N_{\rm Av}\,1000}{\overline M_{\rm Xe}}.
\]

因此，天然氙不能用一个平均核质量和一个平均核响应简单替代逐同位素求和。

### 6.3 暗物质速度分布进入哪个公式？

速度分布不在单一速度的 \(d\sigma_A/dE_R\) 中。它进入从截面到事件率的下一步：

\[
\frac{dR}{dE_R}
=
N_T\frac{\rho_\chi}{m_{\chi_1}}c
\sum_A x_A
\int_{v_{\min,A}}^{v_{\max}}dv\,
f_{\rm lab}(v)\frac{v}{c}
\frac{d\sigma_A}{dE_R}(v).
\]

其中：

- \(x_A\)：天然氙中同位素 \(A\) 的原子丰度；
- \(f_{\rm lab}(v)\)：实验室系暗物质速度分布；
- \(v_{\min,A}\)：该同位素在给定 \(E_R\) 下允许三体过程的最低入射速度；
- \(v_{\max}\)：所采用 halo 模型的实验室系速度上限；
- \(v/c\)：速度通量因子。

这里的 \(v_{\min,A}\) 应从本三体过程的相空间支持条件得到，并且依赖同位素质量；不能不加检查地用普通弹性 \(2\to2\) 散射的 \(v_{\min}\) 公式代替。

### 6.4 采用的 halo benchmark

基准采用截断 Standard Halo Model：

\[
v_0=220\ {\rm km/s},\qquad
v_E=232\ {\rm km/s},\qquad
v_{\rm esc}=544\ {\rm km/s},
\]

对应实验室系最大速度

\[
v_{\max,\rm lab}=v_{\rm esc}+v_E=776\ {\rm km/s}.
\]

另计算一个积分到 1600 km/s 的 untruncated boosted Maxwell–Boltzmann 结果，仅用于检查高速度尾部的敏感性；它不是与截断 SHM 同等地位的首选 halo 假设。两种速度 PDF 均进行了数值归一化检查。

天然氙计算的公共粒子与 halo 输入为

\[
m_{\chi_1}=1\ {\rm TeV},\quad
m_V=10\ {\rm GeV},\quad
g_2=1,\quad
(g_1g_2g_{VN})^2=10^{-8},\quad
\rho_\chi=0.3\ {\rm GeV/cm^3}.
\]

其中 \(\chi_2\) 极点宽度采用条件性的 \(\chi_2\to\chi_1s\) 宽度，假设 Dirac 费米子、实标量、纯 scalar off-diagonal Yukawa 且没有其他开放衰变道；它不是完整的 \(\chi_2\) 自能。

## 7. 天然氙 halo-folded selected-point 结果

在 \(E_R=101\) keV，截断 SHM 下的理论速率为：

| benchmark | \(m_s\) | \(\Delta m\) | \(dR/dE_R\) [events/(kg day keV)] |
|---|---:|---:|---:|
| Red | 200 keV | 1 MeV | \(5.2810\times10^{-11}\) |
| Green | 300 keV | 1 MeV | \(2.5995\times10^{-22}\) |
| Black | 360 keV | 1 MeV | 0（运动学关闭） |
| Blue | 300 keV | 10 MeV | \(2.1675\times10^{-24}\) |

作为高速度尾部诊断，untruncated boosted Maxwell–Boltzmann 的对应数值为：

| benchmark | untruncated MB diagnostic [events/(kg day keV)] |
|---|---:|
| Red | \(8.6009\times10^{-11}\) |
| Green | \(1.3837\times10^{-12}\) |
| Black | \(6.2236\times10^{-14}\) |
| Blue | \(1.1079\times10^{-14}\) |

这些数值差异主要是运动学阈值与 halo 速度端点的共同结果，不应被误判为数值积分不稳定。

在 \(E_R=101\) keV：

- Red 的 \(v_{\min}\) 范围为 588.3–605.0 km/s，七种可用同位素均开放；
- Green/Blue 的 \(v_{\min}\) 范围为 775.8–798.3 km/s，在截断 SHM 下只有 Xe-136 开放；
- Green/Blue 的 Xe-136 阈值为 775.806 km/s，只比 SHM 上限 776 km/s 低 0.194 km/s；
- Black 的 \(v_{\min}\) 范围为 888.3–914.2 km/s，超过截断 SHM 上限，故没有可用同位素开放。

Green benchmark 在其他几个反冲点的截断 SHM 速率为：

| \(E_R\) [keV] | \(dR/dE_R\) [events/(kg day keV)] |
|---:|---:|
| 101 | \(2.5995\times10^{-22}\) |
| 200 | \(1.8136\times10^{-11}\) |
| 267 | \(2.7271\times10^{-13}\) |
| 542 | \(1.4561\times10^{-15}\) |

相同点的 untruncated MB 诊断值依次为 \(1.3837\times10^{-12}\)、\(1.6461\times10^{-10}\)、\(1.7872\times10^{-12}\)、\(8.1709\times10^{-14}\)。

**解释：** Green/Blue 在 101 keV 的截断 SHM 速率极小，是因为只有 Xe-136 的阈值勉强落在 halo 速度端点以内；Black 则完全关闭。把固定 \(v=800\) km/s 的截面曲线与这个 halo-folded 结果比较时，必须记住 800 km/s 已经超过截断 SHM 的 776 km/s 上限。

## 8. 数值验证、归档状态与限制

### 8.1 已完成的检查

- 从官方 AFH v6.0 源文件解析 Xe-131 的 67 项密度矩阵，并与归档 CSV 逐项比较；
- AFH source-to-Python 翻译与源文件数据一致；
- **独立 60 位精度 mpmath 全网格对照已通过：** 对全部 2401 个 q 节点逐点比较，最大振幅绝对差为 \(3.98\times10^{-14}\)，最大相对振幅差（参考振幅绝对值大于 \(10^{-10}\)）为 \(8.83\times10^{-13}\)，最大响应绝对差除以 \(A^2\) 为 \(1.22\times10^{-15}\)；
- Xe-131 AFH 脚本的 Python regression tests 通过；
- 四组 benchmark 的 AFH/GCN/JJ55 响应替换表完成逐点重构检查；
- 天然氙 Eq. (6) kernel 与速度积分完成 selected-point 网格收敛检查；
- 天然氙归档完整性验证 workflow 通过；
- q 约定分离后，显式 legacy_exact 模式重新计算 98 个逐同位素贡献和 14 个总速率，与旧档的最大总速率相对差异为 \\(2.67\\times10^{-12}\\)，CI run 43040078335 通过；
- 核响应 q 与精确三体运动学 q 已完成独立审计，并增加代码防误用检查，详见附录 G。

### 8.2 尚未完成或不能过度声称的事项

1. **AFH 原生 Mathematica 验证仍待执行。** 原生 runner 和比较程序已归档，但当前执行环境没有 Wolfram kernel。mpmath 全网格验证是独立高精度数值交叉检查，不能替代官方 Mathematica 程序的原生执行。
2. **天然氙响应 q 尚未完全统一。** 28 个旧样本采用精确 \(q_{\rm exact}=\sqrt{2m_AE_R+E_R^2}\)，而论文当前 \(y=b_A^2m_AE_R/2\) 对应 \(q_{\rm resp}^{\rm NR}=\sqrt{2m_AE_R}\)。程序已默认要求 manuscript-NR 样本；旧速率保留为 legacy exact-q 结果，没有被改标签或重标度。重新生成七同位素 NR-q 响应仍待取得完整 AFH 输入。
3. **Xe-124/Xe-126 尚未纳入。** 缺少当前 AFH v6.0 内置 density matrix；七种可用同位素的丰度没有重归一化。
4. **天然氙结果是 selected-point rates。** 当前不是连续完整反冲谱。
5. **尚未加入 LZ detector response。** 没有 detector efficiency、能量分辨率、曝光、分析 cuts、背景模型或 likelihood。因此这些理论速率不能直接当作 LZ 预期观测事件数，也不能称为完整的 LZ 数据重铸。
6. **极点宽度是条件性的。** 只包括给定假设下的 \(\chi_2\to\chi_1s\) 标量通道，不等于完整模型的矢量加标量自能。
7. **halo 模型依赖尚未做系统扫描。** untruncated MB 只用于高速度尾部敏感性诊断，不作为默认 halo 结果。

### 8.3 数据修正记录

早期 AFH benchmark CSV 曾出现两类归档问题：

- AFH CSV 中两处缺失换行，导致相邻记录拼接；现已修复，完整 2401 点表可正确解析；
- 早期 benchmark CSV 的 AFH \(R_A\) 列曾误复制 GCN 值，而截面列已经按 AFH/GCN 响应比缩放。现已改为保存真实插值 AFH 响应，并由显示的 \(R_A\) 和 \(I_6\) 直接重构截面。

修正后 AFH 开放点截面相对旧值的最大变化为 \(2.7406\times10^{-4}\)。因此引用结果时应使用 corrected archive，不应使用早期 CSV。

## 9. 当前研究决策与下一步

本轮已经固定的决策：

1. AFH v6.0 default density 作为本阶段 Xe 核响应的标准输入；
2. 固定 AFH 文献默认 \(b_A\)，不拟合谷值；
3. 物理等质子、等中子耦合与 AFH 原始 isoscalar response 之间的因子 4 只计入一次；
4. 对固定同位素和运动学条件，AFH/GCN/JJ55 共用同一个 \(I_6\)，只替换核响应；
5. 天然氙采用逐同位素丰度加权，且不对当前缺失的 Xe-124/Xe-126 丰度重新归一化；
6. 截断 SHM 作为 halo 基准，untruncated MB 仅作为尾部敏感性诊断；
7. 不把固定速度截面、天然氙理论速率和完整 LZ detector-level 预测混为一谈。

建议后续按以下顺序推进：

1. **完成 AFH 原生 Mathematica 对照。** 在有 Wolfram kernel 的环境中执行官方 v6.0 程序，对照 Xe-131 响应曲线和选定点，形成真正独立于 Python 源码翻译的验证。
2. **重新生成七同位素 manuscript-NR 响应。** 取得完整 AFH 七同位素响应表或官方源包，在 \(q_{\rm resp}^{\rm NR}=\sqrt{2m_AE_R}\) 处重新生成 28 个 selected-point 样本，再重算 halo fold；旧 exact-q 结果保留为 legacy 对照。
3. **补全或明确缺失同位素处理。** 在没有可靠 AFH Xe-124/Xe-126 响应之前，保留当前覆盖率和不重归一化的明确限制，不用平均核响应代替。
4. **扩展天然氙连续反冲谱。** 当前 selected points 用于验证阈值和 halo 端点；连续谱需要单独做网格和收敛检查。
5. **最后进行 LZ detector-level 映射。** 在取得并核实效率、分辨率、曝光、cuts 和背景输入后，再计算预期事件数或构建 likelihood；当前 selected-point rate 不应提前解释成 LZ 排除或信号拟合。
---

## 10. 代码、数据和文献入口

### 仓库内的主要研究记录

- AFH default Xe-131 README：`research/afh_default_density_xe131/README.md`
- AFH 因子 4 归一化映射：`research/afh_default_density_xe131/AFH_COUPLING_NORMALIZATION_MAPPING.md`
- AFH Xe-131 源码与归一化审计：`research/afh_default_density_xe131/AFH_DEFAULT_XE131_NORMALIZATION_AUDIT.md`
- AFH/GCN/JJ55 对照：`research/afh_default_density_xe131/output/AFH_DEFAULT_VS_GCN_JJ55_COMPARISON.md`
- 四组 benchmark corrected results：`research/afh_default_density_xe131/output/AFH_FOUR_BENCHMARKS_CORRECTED_RESULTS.md`
- 四组 benchmark 截面审计：`research/afh_default_density_xe131/output/FOUR_BENCHMARK_CROSS_SECTION_AUDIT.md`
- 天然氙 halo fold README：`research/afh_default_density_natural_xenon_halo/README.md`
- 天然氙 halo fold 审计：`research/afh_default_density_natural_xenon_halo/results/NATURAL_XENON_HALO_FOLD_AUDIT.md`
- 响应 q 与精确运动学 q 审计：`research/docs/appendices/09G_recoil_momentum_convention_audit.md`

### 外部参考

- AFH nuclear response：Anand, Fitzpatrick and Haxton, *Weakly interacting massive particle-nucleus elastic scattering response*, Phys. Rev. C 89 (2014) 065501, [arXiv:1308.6288](https://arxiv.org/abs/1308.6288)。
- LZ detector 官方介绍：[The LZ Detector](https://lz.lbl.gov/detector/)。
- AFH v6.0 原始 Mathematica 包及其源文件哈希记录见本研究目录的 README 和 provenance 文件。

---

**归档状态说明：** 本文是对本轮 AFH 核响应、三体积分、天然氙同位素和 halo folding 讨论的研究整理，不代表所有后续验证均已完成。当前 PR #7 仍为 Draft/Open；本文随该研究分支归档，不执行 PR 合并。

---

## 附录导航与独立文件

主报告后文保留 A–G 七份附录的完整正文。为便于检索、单独引用和维护，同一附录还分别保存为独立 Markdown 文件；主报告正文与七份独立副本保持同步：

| 附录 | 内容 | 文件 |
|---|---|---|
| A | 三体运动学、相空间边界与 Dirac 振幅 | [09A_three_body_kinematics_amplitude.md](appendices/09A_three_body_kinematics_amplitude.md) |
| B | AFH v6.0 密度矩阵、谐振子基底与响应实现 | [09B_afh_v6_density_matrix_response.md](appendices/09B_afh_v6_density_matrix_response.md) |
| C | AFH isoscalar 归一化与因子 4 | [09C_afh_isoscalar_factor4_normalization.md](appendices/09C_afh_isoscalar_factor4_normalization.md) |
| D | 天然氙同位素、丰度和核靶归一化 | [09D_natural_xenon_isotope_target.md](appendices/09D_natural_xenon_isotope_target.md) |
| E | 实验室系速度分布、三体最小速度与 halo folding | [09E_halo_velocity_vmin_folding.md](appendices/09E_halo_velocity_vmin_folding.md) |
| F | 计算程序、数据文件、收敛验收和复现命令 | [09F_numerical_validation_reproduction.md](appendices/09F_numerical_validation_reproduction.md) |
| G | 核响应动量与精确三体运动学动量的约定审计 | [09G_recoil_momentum_convention_audit.md](appendices/09G_recoil_momentum_convention_audit.md) |

附录与主报告使用同一研究分支维护。程序、CSV 和机器可读结果仍保存在各自计算目录中；附录负责解释其定义、调用方式和验证边界，不复制大体积数据。

---

# 技术附录（完整内容）

以下 A–G 附录正文与目录 research/docs/appendices/ 中的七份独立文件保持同步。主报告保留完整附录，独立文件用于单独检索和引用。

## 附录 A：三体运动学、相空间边界与 Dirac 振幅

### A.1 研究对象、约定与四动量

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

### A.2 \(W_{\min}^2\) 与 \(W_{\max}^2\) 的推导

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

### A.3 在 \(K\) 静止系构造三体末态

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

### A.4 为什么选取 \((W^2,z,\phi_*)\) 作为积分变量

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

### A.4.1 从不变相空间得到 Eq. (6) 的整体前因子

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

### A.5 两张辐射图、振幅与干涉项

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

### A.6 宽度约定与模型边界

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

### A.7 求积、数值检查与复现入口

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

---

## 附录 B：AFH v6.0 密度矩阵、谐振子基底与响应实现

### B.1 源文件、版本与 Xe-131 输入

本研究使用用户提供的 AFH/DMFormFactor v6.0 压缩包。归档的来源信息为：

- ZIP SHA-256：**4e0f70e6e780f3f4a40faa14792cae239d1989cf15d1e211b4fd7389b0460727**
- Mathematica 源文件：**v6/dmformfactor-V6.m**
- 源文件 SHA-256：**dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372**
- 同位素选择：**SetIsotope[54,131,"default","default"]**
- 内置密度矩阵：**sdgXe131**，共 67 项。

提取后的密度矩阵归档在

**research/afh_default_density_xe131/afh_default_xe131_density_matrix.csv**。

每一行包含：

| 字段 | 含义 |
|---|---|
| index | AFH 内置矩阵条目序号 |
| coefficient | 一体密度矩阵系数 |
| rank | 多极秩 \(J\) |
| isospin | 等标量/等矢量通道标记 \(\tau\) |
| Nprime, two_jprime | 单粒子末态轨道的振子主壳量子数和 \(2j'\) |
| N, two_j | 单粒子初态轨道的振子主壳量子数和 \(2j\) |

这 67 项不是 67 个独立的实验参数，而是壳模型单粒子轨道之间的约化一体密度矩阵元。其系数与轨道标签共同决定多极核矩阵元。

条目分布为：

| rank \(J\) | \(\tau=0\) | \(\tau=1\) | 合计 |
|---:|---:|---:|---:|
| 0 | 16 | 5 | 21 |
| 1 | 9 | 9 | 18 |
| 2 | 8 | 8 | 16 |
| 3 | 6 | 6 | 12 |
| **合计** | **39** | **28** | **67** |

当前使用的是弹性 \(M\) 响应 \(W_M^{00}\)：\(\tau=\tau'=0\)，且宇称选择规则使偶数多极 \(J=0,2\) 贡献进入该响应。因此实际参与本次 \(W_M^{00}\) 有限和的是 16 个 \(J=0,\tau=0\) 条目和 8 个 \(J=2,\tau=0\) 条目；其他条目仍保留在完整提取表中，以保证源矩阵归档完整。

Xe-131 的输入量为

\[
A=131,\qquad Z=54,\qquad J_A=\frac32,
\qquad T_{\rm iso}=|A/2-Z|=11.5.
\]

### B.2 AFH 默认谐振子长度与单位

AFH default 的振子长度处方为

\[
\boxed{
b_A=
\sqrt{\frac{41.467}
{45A^{-1/3}-25A^{-2/3}}}\ {\rm fm}
}.
\]

源程序采用

\[
1\ {\rm fm}=5.0677\ {\rm GeV}^{-1}.
\]

对于 Xe-131，

\[
b_{131}=2.2923417985218975\ {\rm fm}
=11.61690053236942\ {\rm GeV}^{-1}.
\]

核响应的无量纲谐振子变量是

\[
y=\left(\frac{qb_A}{2}\right)^2,
\]

其中 \(q=|\mathbf q|\)。因此 \(b_A\) 是核结构处方的一部分，不是用来拟合 Figure 2 谷值的自由参数。

**为什么不能调节 \(b_A\) 拟合谷值？** 因为 \(b_A\) 决定 \(q\mapsto y\) 的映射，并进入所有径向振子矩阵元。改变它会系统性移动有限动量响应的节点和极小值，相当于改变核模型输入。若为了匹配图中某个谷值而任意调节 \(b_A\)，得到的就不再是 AFH default 处方，也无法再把结果称为对该文献核响应的复现。

### B.3 单粒子轨道、多极角动量与径向矩阵元

AFH 源程序的轨道映射由单粒子振子主壳数 \(N\) 和总角动量 \(j\) 决定。当前 Python 翻译采用：

\[
j_+=j+\frac12.
\]

若 \(N-j_+\) 为偶数，则 \(\ell=j_+\)；否则 \(\ell=j_+-1\)。径向量子数为

\[
n=1+\frac{N-\ell}{2}.
\]

对每一条密度矩阵记录，程序计算一个约化角矩阵元和一个径向 Bessel 矩阵元。角部分用 Wigner \(3j\) 与 \(6j\) 符号：

\[
\begin{aligned}
\mathcal A^{(J)}_{N'j',Nj}
={}&(-1)^{1/2+j+J}
\left[
\frac{(2j+1)(2j'+1)(2\ell+1)(2\ell'+1)(2J+1)}
{4\pi}
\right]^{1/2}\\
&\times
\begin{pmatrix}
\ell'&J&\ell\\
0&0&0
\end{pmatrix}
\left\{
\begin{matrix}
\ell'&j'&1/2\\
j&\ell&J
\end{matrix}
\right\}.
\end{aligned}
\]

径向部分由 AFH 的 BesselElement 有限和实现。其结构为

\[
\begin{aligned}
\mathcal B_{n'\ell',n\ell}^{(J)}(y)
={}&
\frac{2^J}{(2J+1)!!}
y^{J/2}e^{-y}
\sqrt{(n'-1)!(n-1)!}\\
&\times
\sqrt{\Gamma(n'+\ell'+1/2)\Gamma(n+\ell+1/2)}
\sum_{r=0}^{n-1}\sum_{s=0}^{n'-1}
\mathcal C_{rs}\,
{}_1F_1\!\left(
\frac{J-\ell-\ell'-2r-2s}{2};
J+\frac32;y
\right),
\end{aligned}
\]

其中

\[
\begin{aligned}
\mathcal C_{rs}
={}&
\frac{(-1)^{r+s}}
{r!\,s!\,(n-1-r)!\,(n'-1-s)!}\\
&\times
\frac{
\Gamma[(\ell+\ell'+J+2r+2s+3)/2]
}{
\Gamma(\ell+r+3/2)\Gamma(\ell'+s+3/2)
}.
\end{aligned}
\]

这里 \({}_1F_1\) 是合流超几何函数。上式是当前 Python 翻译所实现的 AFH 有限和结构；具体系数和轨道标签仍以归档的 AFH v6.0 源文件及 67 项 CSV 为准。

### B.4 从密度矩阵到 \(W_M^{00}(y)\)

对每个允许的 \(J,\tau=0\)，程序将密度矩阵系数、等标量约化因子、角矩阵元和径向矩阵元求和：

\[
\mathcal A_J(y)
=
\sqrt{\frac{2}{2T_{\rm iso}+1}}
\sum_{\alpha\in D_{J,0}}
\rho_\alpha\,
\mathcal A_{\alpha}^{(J)}
\mathcal B_{\alpha}^{(J)}(y).
\]

对 Xe-131 的弹性 \(M\) 响应，当前程序保留 \(J=0,2\)。AFH v6.0 的 isoscalar 响应归一化在程序翻译中写为

\[
\boxed{
W_{M,\rm AFH}^{00}(y)
=\frac14\left[\mathcal A_0(y)^2+\mathcal A_2(y)^2\right]
}.
\]

这一步返回的是 AFH 包自身的原始 isoscalar response；它还没有自动变成论文中以物理单核子耦合 \(g_{VN}\) 为前因子的等质子、等中子相干响应。两者之间的因子 4 见附录 C。

### B.5 网格、插值、极小值搜索和边界处理

Xe-131 AFH 响应表采用

\[
0\le q\le0.60\ {\rm GeV},
\qquad \Delta q=0.00025\ {\rm GeV}=0.25\ {\rm MeV},
\]

共 2401 个节点。完整结果保存在

**research/afh_default_density_xe131/output/afh_default_xe131_WM00.csv**。

极小值搜索不是简单读取某个粗网格点：

1. 先在离散物理响应数组上用 find_peaks 对 \(-R\) 找局部极小值候选，prominence 取 \(A^2\times10^{-8}\)，distance 取 10 个网格点；
2. 只保留 \(0.08\le q\le0.50\) GeV 的候选；
3. 对每个候选，在相邻网格节点 \([q_{i-1},q_{i+1}]\) 内使用 bounded minimize_scalar；
4. 每次目标函数调用都重新计算 AFH 翻译核，而不是仅对谷值位置作多项式拟合；
5. 数值停止参数为 \(10^{-14}\) GeV。

代码中创建了 PCHIP 插值对象，但**极小值细化实际使用的是直接响应函数**，不是 PCHIP 插值曲线。PCHIP 的实际用途是后续把 AFH 响应插入固定速度的 5 keV 反冲网格：四 benchmark 截面程序使用 shape-preserving PCHIP，并设置 extrapolate=False；网格外不允许外推。超出响应表支持范围时计算应报错，而不是静默生成值。

### B.6 当前核响应结果

AFH default Xe-131 物理等质子、等中子响应的细化极小值为：

| \(q_{\min}\) [MeV] | \(E_{R,\min}\) [keV] | \(R_{\min}/A^2\) |
|---:|---:|---:|
| 157.93578 | 102.20672 | \(1.23638\times10^{-5}\) |
| 256.27187 | 269.10390 | \(6.34070\times10^{-8}\) |
| 365.06657 | 546.08690 | \(1.56194\times10^{-7}\) |
| 499.37189 | 1021.79779 | \(1.67063\times10^{-8}\) |

前三个极小值位于 Figure 2 讨论的反冲能量范围附近。它们是 AFH default 核响应的计算结果，不是通过调整 \(b_A\) 得到的拟合谷值。

### B.7 独立验证的实际范围

已完成的 Python 侧验证：

- 从官方 AFH v6.0 源文件解析 67 项矩阵，并与 CSV 逐项核对；
- 检查 \(q=0\) AFH 原始 isoscalar 归一化；
- 六个 \((q,J)\) 代表点的 60 位精度 mpmath spot checks；
- **全网格独立 mpmath 验证：** 重新组织 BesselElement 有限和，按超几何函数参数分组，使用 60 位精度 mpmath，而不调用 SciPy 的 hyp1f1；对完整 2401 个 q 节点逐点比较；
- 六项 AFH Xe-131 Python 回归测试；
- 保存完整 2401 点响应表、谷值表、Figure 2 参考点表和 metadata。

全网格验收结果：

| 指标 | 结果 |
|---|---:|
| 参考精度 | 60 decimal digits |
| q 网格节点 | 2401 |
| 最大振幅绝对差 | \(3.9782\times10^{-14}\) |
| 最大相对振幅差（参考振幅绝对值大于 \(10^{-10}\)） | \(8.8322\times10^{-13}\) |
| 最大响应绝对差除以 \(A^2\) | \(1.2159\times10^{-15}\) |
| 最大相对响应差（\(R/A^2>10^{-12}\)） | \(1.3376\times10^{-13}\) |
| 状态 | PASS |

完整的 2401 行逐点比较表和 JSON summary 作为 GitHub Actions artifact 保存：

- workflow run：**43038372836**
- artifact：**afh-xe131-mpmath-full-grid-validation**
- [查看完整 CI 运行和 artifact](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43038372836)

此前六个代表点的 mpmath 结果仍保留为早期 spot-check 记录；现在它们已被完整 2401 点验证覆盖。

AFH 原生 Mathematica runner 和 Python/Mathematica 比较程序已经归档：

- run_afh_default_xe131.wls
- verify_afh_xe131_native.wls
- compare_afh_mathematica_python.py

但 Wolfram kernel 尚未在当前计算环境中执行。因此原生 Mathematica 逐点对照仍为待完成项目。全网格 mpmath 是独立高精度数值实现，不应被称为官方 Mathematica 原生复算。

### B.8 核响应动量与精确运动学动量必须分开

论文明确规定

\[
y=\frac{b_A^2m_AE_R}{2},
\]

而 AFH 振子变量为 \(y=(qb_A/2)^2\)。因此，在论文当前写法下，固定反冲能量时的核响应查询动量是

\[
\boxed{q_{\rm resp}^{\rm NR}=\sqrt{2m_AE_R}}.
\]

三体运动学则由核质量壳条件给出精确空间反冲动量

\[
\boxed{q_{\rm kin}^{\rm exact}=\sqrt{2m_AE_R+E_R^2}}.
\]

AFH 响应网格本身以 \(q\) 为自变量；把网格上的 \(q\) 极小值换算成物理反冲能量时，程序使用精确逆映射 \(E_R=\sqrt{m_A^2+q^2}-m_A\)。但在给定 \(E_R\) 查询论文定义的响应 \(y(E_R)\) 时，应使用 \(q_{\rm resp}^{\rm NR}\)。这两个操作应分别命名，不能用同一个未说明约定的 q 代替。

当前代码约定为：

- 固定 Xe-131 benchmark 和 joint Xe-131 响应查询：使用 \(q_{\rm resp}^{\rm NR}\)；
- Eq. (6) 的三体运动学、\(W_{\max}\) 和 \(v_{\min}\)：使用 \(q_{\rm kin}^{\rm exact}\)；
- 旧天然氙 halo 输入的 28 个 AFH response samples：实际使用 \(q_{\rm kin}^{\rm exact}\)，属于 legacy 样本，尚未按论文 \(q_{\rm resp}^{\rm NR}\) 重新生成。

本轮 q 审计显示，28 个天然氙样本的 \(q_{\rm exact}-q_{\rm NR}\) 约为 0.032–0.409 keV（相对 0.20–1.14 ppm）。对 Xe-131 的 2401 点 AFH 响应表直接插值后，四个 selected recoil 点的 \(R_A(q_{\rm exact})/R_A(q_{\rm NR})-1\) 约为 -5.5 至 -212.7 ppm。完整数据和数值见附录 G。

固定 Xe-131 benchmark 仍使用 \(M_A=131u\) 的历史质量约定；天然氙 halo 程序使用 NIST 原子质量减去 54 个电子质量的核质量。质量方案是另一个独立输入维度，不应与上述两个 q 的定义混为一谈。

天然氙脚本现默认要求 manuscript-NR 响应样本；旧的 exact-q 样本只能通过显式的 --response-q-convention legacy_exact 复现。若所选 q 与样本不一致，程序会报错，不会仅修改 q 标签或静默复用旧 \(R_A\)。

---

## 附录 C：AFH isoscalar 归一化与物理核子耦合的因子 4

### C.1 先区分两种不同的 \(c_0\)

标准 isospin 基底中，质子和中子耦合写成

\[
c_{\rm std}^{0}=\frac{c^p+c^n}{2},
\qquad
c_{\rm std}^{1}=\frac{c^p-c^n}{2}.
\]

对物理等质子、等中子耦合

\[
g_p=g_n=g_{VN},
\]

标准 isospin 系数是

\[
\boxed{
c_{\rm std}^{0}=g_{VN},\qquad c_{\rm std}^{1}=0.
}
\]

但 AFH v6.0 分发版 Mathematica 程序的 setter 接口参数不是直接等同于上述标准系数。为避免符号混淆，下面将接口输入记作 \(c_{\rm set}\)。

AFH 的

\[
\texttt{SetCoeffsNonrel[op,c,0]}
\]

在接口内部将质子、中子系数分别设置为

\[
c_p=c_n=\frac{c_{\rm set}}{2}.
\]

因此，要让接口实际产生物理耦合 \(c_p=c_n=g_{VN}\)，必须输入

\[
\boxed{
c_{\rm set}=2g_{VN}.
}
\]

所以“标准 isoscalar 系数 \(c_{\rm std}^{0}=g_{VN}\)”与“AFH setter 输入 \(c_{\rm set}=2g_{VN}\)”并不矛盾；它们是不同层级、不同定义的变量。后续文档不应把这两个量都不加区分地写成同一个 \(c_0\)。

### C.2 从 AFH 原始 \(W_M^{00}\) 到 \(A^2/4\)

AFH 包的调用

\[
\texttt{ResponseNuclear[y,1,0,0]}
\]

返回原始等标量核响应 \(W_{M,\rm AFH}^{00}(y)\)。按 AFH v6.0 包自己的 isoscalar 归一化，定义

\[
R_{\rm AFH,raw}(q)
=
\frac{4\pi}{2J_A+1}
W_{M,\rm AFH}^{00}(y).
\]

在零动量转移处，等标量核算符的单核子电荷带有 \(1/2\)，故相干振幅为 \(A/2\)，对应

\[
\boxed{
R_{\rm AFH,raw}(0)=\left(\frac A2\right)^2=\frac{A^2}{4}.
}
\]

这正是 AFH 原始 isoscalar response 的归一化。它不是已经按物理单核子耦合 \(g_{VN}\) 归一化的 \(A^2\) 响应。

### C.3 物理等质子、等中子耦合为何产生因子 4

对物理相干矢量电荷，

\[
g_p=g_n=g_{VN},
\]

零动量转移时的核振幅为

\[
Zg_p+(A-Z)g_n
=Ag_{VN}.
\]

若截面前因子已经显式提出 \(g_{VN}^2\)，与之相乘的核响应必须满足

\[
R_A^{\rm phys}(0)=A^2.
\]

由上一节 AFH 原始响应的 \(A^2/4\) 归一化，得到

\[
R_A^{\rm phys}(q)=4R_{\rm AFH,raw}(q).
\]

因此

\[
\boxed{
R_A^{\rm phys}(q)
=
\frac{16\pi}{2J_A+1}
W_{M,\rm AFH}^{00}(y)
}
\]

并且在精确的未舍入密度矩阵极限下

\[
R_A^{\rm phys}(0)=A^2.
\]

同一结果也可以在振幅层面理解：AFH setter 要输入 \(c_{\rm set}=2g_{VN}\)，平方后产生 \(c_{\rm set}^2=4g_{VN}^2\)。因此，若把 \(g_{VN}^2\) 留在论文截面前因子中，就必须把这四倍包含在核响应里。

### C.4 三种响应必须分开记录

| 对象 | 定义 | 零动量归一化 |
|---|---|---:|
| AFH 原始 isoscalar response | \(R_{\rm AFH,raw}=4\pi W_M^{00}/(2J_A+1)\) | \(A^2/4\) |
| 物理等 \(p,n\) 相干响应 | \(R_A^{\rm phys}=4R_{\rm AFH,raw}\) | \(A^2\) |
| 论文 Eq. (6) 中的核响应 | 前因子保留 \(g_{VN}^2\)，使用 \(R_A^{\rm phys}\) | \(A^2\) |

等价的另一种记账方式是保留原始 AFH response，但把 \(c_{\rm set}=2g_{VN}\) 的平方显式放在粒子—核子耦合收缩中。两种方式只能选一种，不能既把响应乘 4，又把耦合平方再乘 4。

特别地，夸克到核子的匹配

\[
g_{VN}=3g_{Vq}
\]

是另一条物理关系，与 AFH isoscalar 归一化因子 4 无关；不能通过修改该匹配关系来吸收因子 4。

### C.5 Xe-131 的有限小数精度修正

AFH 内置密度矩阵系数以有限小数位打印。对 Xe-131 的源翻译结果，

\[
R_{\rm AFH,raw}(0)=4289.895955714993,
\]

而理论值为

\[
\frac{A^2}{4}=\frac{131^2}{4}=4290.25.
\]

相对偏差为

\[
8.2522996\times10^{-5}.
\]

先乘因子 4 得到物理等 \(p,n\) 原始响应，其零动量值为

\[
4R_{\rm AFH,raw}(0)=17159.58382285997,
\]

与 \(A^2=17161\) 的差异仍来自密度矩阵的有限打印精度。

为只去除这一整体常数偏差，归档的物理响应采用

\[
\boxed{
R_A^{\rm phys}(q)
=
A^2
\frac{R_{\rm AFH,raw}(q)}
{R_{\rm AFH,raw}(0)}
}.
\]

等价地，它是在 \(16\pi W_M^{00}/(2J_A+1)\) 上乘一个 \(q\) 无关的微小修正因子。这个修正不改变 \(q\) 依赖，也不移动响应极小值；它不是对 \(b_A\)、密度矩阵或谷值的拟合。

### C.6 独立文献和源代码核查

源代码审计记录指出：

1. AFH v6.0 的 Response 表达式对 isoscalar 系数使用 \((a_n+a_p)/2\)；
2. FF 例程对质子/中子系数的二阶导数构造包含 \(1/2\)；
3. ResponseNuclear 的 \(00\) 分支对四个质子/中子矩阵项作 \(1/4\) 的组合；
4. setter 接口将输入 \(c_{\rm set}\) 转换为 \(c_p=c_n=c_{\rm set}/2\)。

这与 \(R_{\rm AFH,raw}(0)=A^2/4\) 的数值归一化一致。

独立文献对照：Oliver C. Gorton, *Shell Model Methods, Statistical Nuclear Reactions, and Beta-delayed Neutron Emission*, UC Irvine PhD dissertation (2024), Sec. 2.2, pp. 29–30。该节讨论标准 isospin 系数与分发版 dmformfactor-prc.m / dmformfactor-V6.m 的接口约定差异，并给出

\[
W_M^{00}(0)=\frac{1}{4\pi}\left(\frac A2\right)^2.
\]

参考：

https://www.escholarship.org/content/qt3ns8f1r8/qt3ns8f1r8.pdf

仓库中的源代码归一化记录：

- research/afh_default_density_xe131/AFH_COUPLING_NORMALIZATION_MAPPING.md
- research/afh_default_density_xe131/AFH_DEFAULT_XE131_NORMALIZATION_AUDIT.md
- research/figure2_full_reproduction/ANAND_WM_RESPONSE_AUDIT.md

最终论文 Eq. (6) 的选择是：前因子保留物理单核子耦合 \(g_{VN}\)，核响应使用 \(16\pi W_{M,\rm AFH}^{00}/(2J_A+1)\)，因子 4 只出现一次。

---

## 附录 D：天然氙同位素、丰度和核靶归一化

### D.1 天然氙同位素输入

天然氙不是单一 Xe-131 核靶，而是九种稳定/长寿命同位素的天然混合物。当前输入采用 NIST 天然原子丰度和原子质量。AFH v6.0 本轮可用 default density matrix 的七种同位素为 Xe-128、129、130、131、132、134、136。

核质量按

\[
m_A=[M_{\rm atom}(A)-54m_e]u
\]

计算，忽略很小的电子结合能，其中

\[
u=0.93149410242\ {\rm GeV},\qquad
m_e=0.000548579909065\,u.
\]

| 同位素 | 原子质量 [u] | 天然原子丰度 \(x_A\) | 核质量 \(m_A\) [GeV] | \(b_A\) [fm] | AFH default |
|---|---:|---:|---:|---:|---|
| Xe-124 | 123.905892 | 0.000952 | 115.390013710 | 2.27403795986 | 缺失 |
| Xe-126 | 125.9042983 | 0.000890 | 117.251517392 | 2.27935034677 | 缺失 |
| Xe-128 | 127.903531 | 0.019102 | 119.113790862 | 2.28459563645 | 可用 |
| Xe-129 | 128.9047808611 | 0.264006 | 120.046449203 | 2.28719370243 | 可用 |
| Xe-130 | 129.903509349 | 0.040710 | 120.976758899 | 2.28977568326 | 可用 |
| Xe-131 | 130.90508406 | 0.212324 | 121.909719835 | 2.29234179852 | 可用 |
| Xe-132 | 131.9041550856 | 0.269086 | 122.840348604 | 2.29489226319 | 可用 |
| Xe-134 | 133.90539466 | 0.104357 | 124.704491465 | 2.29994707834 | 可用 |
| Xe-136 | 135.907214484 | 0.088573 | 126.569174825 | 2.30494176098 | 可用 |

七种有 AFH default response 的同位素覆盖

\[
\boxed{
\sum_{A\in{\rm available}}x_A=0.998158
}
\]

即天然原子丰度覆盖率为 99.8158%。缺失的 Xe-124 与 Xe-126 合计丰度为

\[
x_{124}+x_{126}=0.001842.
\]

当前没有把这两种同位素的核响应设为零以外的任意估计，也没有把其余七种同位素重新归一化到 100%。天然丰度仍按原始 \(x_A\) 使用。

### D.2 缺失同位素造成的误差边界

必须区分“丰度覆盖率”与“事件率覆盖率”。当前输入只能确定缺失同位素占天然氙原子数的 0.1842%，不能仅凭这一数字断言事件率也恰好少了 0.1842%。

令每种同位素在给定反冲能量下、尚未乘天然丰度的速率核为 \(\eta_A(E_R)\)，则缺失同位素的速率为

\[
R_{\rm miss}(E_R)
=
x_{124}\eta_{124}(E_R)+x_{126}\eta_{126}(E_R).
\]

相对速率缺失量为

\[
\epsilon_{\rm miss}(E_R)
=
\frac{R_{\rm miss}(E_R)}
{R_{\rm available}(E_R)+R_{\rm miss}(E_R)}.
\]

由于 \(\eta_{124}\) 和 \(\eta_{126}\) 依赖各自的核响应、核质量和三体阈值，当前没有相应 AFH density matrix 时，无法从丰度单独给出严格的相对事件率误差上界。0.1842% 只是缺失的原子丰度，不是经过证明的速率误差。若未来取得两种同位素的密度矩阵，应补算其响应后再关闭这一误差项。

### D.3 每千克天然氙的靶核数

天然氙完整丰度加权平均原子质量为

\[
\bar M_{\rm Xe}=131.2927614479\ {\rm g/mol}.
\]

每千克天然氙中的靶核总数为

\[
\boxed{
N_T=\frac{N_{\rm Av}\,1000}{\bar M_{\rm Xe}}
}
\]

其中 \(N_{\rm Av}=6.02214076\times10^{23}\ {\rm mol}^{-1}\)，1000 将 kg 转为 g。

这里有两个不同的求和用途：

- \(\bar M_{\rm Xe}\) 使用完整九种天然同位素丰度，确定实际每千克天然氙包含多少个原子；
- 微分速率中的 \(\sum_A x_A\) 当前只包括七种有 AFH default response 的同位素，并保留其原始天然丰度、不重新归一化。

不能把这两个操作混为一谈。

### D.4 为什么不能用平均核质量代替逐同位素求和

对每种同位素，截面和阈值均依赖自己的核质量：

\[
\frac{d\sigma_A}{dE_R}
\propto
\frac{m_A R_A(E_R) I_{6,A}(v,E_R)}
{p_{\chi_1}^2(m_V^2+2m_AE_R)^2}.
\]

同时 \(W_{\max,A}\)、\(v_{\min,A}\) 和 \(R_A(E_R)\) 也都依赖 \(A\)。因此一般有

\[
\sum_A x_A\frac{d\sigma_A}{dE_R}
\ne
\frac{d\sigma_{\bar A}}{dE_R}.
\]

在阈值附近尤其如此：同一个 \(E_R\) 下，一种同位素可能满足 \(v_{\min,A}<v_{\max}\)，另一种同位素则可能完全关闭。平均核质量会抹掉这种离散阈值结构。

因此程序对每种可用同位素分别使用：

1. NIST 原子质量转换得到的 \(m_A\)；
2. 对应质量数的 AFH default \(b_A\)；
3. 对应同位素的 \(R_A(E_R)\)；
4. 对应同位素的 \(W_{\max,A}\) 和 \(v_{\min,A}\)；
5. 最后才乘天然丰度 \(x_A\) 求和。

### D.5 与 Xe-131 固定速度截面表的质量约定区别

固定速度 Xe-131 四 benchmark 截面替换脚本当前使用

\[
M_A=131\times0.93149410242\ {\rm GeV},
\]

并在响应插值时采用 \(q_{\rm resp}=\sqrt{2M_AE_R}\)。天然氙 halo-fold 程序则采用 NIST 原子质量减去电子质量的核质量，并使用 \(q_{\rm resp}=\sqrt{2m_AE_R+E_R^2}\)。

这两种约定在当前反冲范围内数值接近，但不是同一个输入定义。严格比较固定速度 Xe-131 与天然氙结果前，应统一质量和 \(q_{\rm resp}\) 约定，或明确把它们作为不同精度方案报告。

主要输入文件：

- research/afh_default_density_natural_xenon_halo/input/natural_xenon_isotope_weights.csv
- research/afh_default_density_natural_xenon_halo/input/afh_response_samples.csv

---

## 附录 E：实验室系速度分布、三体 \(v_{\min}\) 与 halo folding

### E.1 速度分布与归一化约定

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

### E.2 三体过程的最小入射速度 \(v_{\min,A}\)

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

### E.3 从单同位素截面到天然氙事件率

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

### E.3.1 核响应动量与运动学动量

本节中的 \(v_{\min,A}\)、\(W_{\max,A}\) 和三体 reduced kernel 使用精确的核反冲动量

\[
q_{\rm kin}^{\rm exact}=\sqrt{2m_AE_R+E_R^2}.
\]

但论文当前核响应变量

\[
y=\frac{b_A^2m_AE_R}{2}
\]

对应

\[
q_{\rm resp}^{\rm NR}=\sqrt{2m_AE_R}.
\]

因此 halo fold 的 \(R_A(E_R)\) 应按 \(q_{\rm resp}^{\rm NR}\) 查询 AFH 响应，而不能因为三体运动学使用精确 q，就把同一个 q 直接用于核响应。

**当前已归档的 28 个 AFH 天然氙响应样本仍是在 \(q_{\rm kin}^{\rm exact}\) 处取值。** 本附录后续的数值速率因此应理解为 legacy exact-q-response 结果，而不是已经按论文 \(y(E_R)\) 约定重新生成的最终响应样本。附录 G 给出 28 个样本的动量差异、Xe-131 响应插值影响和重新计算所需输入。

### E.4 101 keV 时逐同位素阈值

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

### E.5 已归档的 selected-point 速率

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

### E.6 速度求积与适用范围

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

### E.7 当前 halo 结果的 q-response 状态

本轮已对旧 exact-q 计算执行完整回归复现：

- 默认 manuscript_nr 模式已被 CI 验证会拒绝当前 exact-q 样本；
- 显式 legacy_exact 模式重新计算 98 个逐同位素贡献和 14 个总速率；
- 与旧归档比较，最大逐同位素贡献相对差异为 \(4.32\times10^{-10}\)，最大总速率相对差异为 \(2.67\times10^{-12}\)；
- [CI run 43040078335](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43040078335) 全部通过。

机器可读比较结果保存在 results/legacy_exact_reproduction_comparison.json。该结果证明 q 约定分离没有破坏旧 exact-q 结果的可复现性；它不等于已经得到 manuscript-NR 的新天然氙速率。

当前归档的天然氙 selected-point 速率没有被本轮 q 审计重标度或覆盖。其输入样本仍采用

\[
q_{\rm response}^{\rm legacy}
=\sqrt{2m_AE_R+E_R^2}.
\]

天然氙计算程序现在将两种 q 明确分开，并默认要求论文定义的 \(q_{\rm resp}^{\rm NR}\) 样本。若要复现旧结果，必须显式传入

~~~bash
python research/afh_default_density_natural_xenon_halo/run_afh_natural_xenon_halo_fold.py \
  --response-q-convention legacy_exact
~~~

不带该选项时，程序选择 manuscript_nr；由于现有 28 个样本仍是 exact-q，程序会在样本一致性检查处报错。这是有意的保护，避免旧 \(R_A\) 数值被错误地标记成 NR-q 响应。

要得到论文约定下的新 halo rate，必须先重新生成七种可用同位素在 \(q_{\rm resp}^{\rm NR}\) 处的 AFH 响应样本，再重新执行逐同位素 \(I_6\) 和速度积分。精确 \(q_{\rm kin}\) 仍然用于 \(v_{\min}\) 和三体运动学。

---

## 附录 F：计算程序、数据文件、收敛验收和复现命令

### F.1 计算链和程序入口

本研究的数值链为

\[
\boxed{
\text{三体振幅}
\longrightarrow I_6
\longrightarrow R_A(E_R)
\longrightarrow \frac{d\sigma_A}{dE_R}
\longrightarrow \sum_A x_A
\longrightarrow \frac{dR}{dE_R}
}.
\]

各环节对应的主要程序如下：

| 任务 | 主要程序/目录 | 作用 |
|---|---|---|
| Eq. (6) 三体 kernel | research/figure2_full_reproduction/eq6_kernel.py | 构造末态四动量、Dirac trace、\(I_6\) |
| AFH Xe-131 响应 | research/afh_default_density_xe131/run_afh_default_xe131.py | 解析密度矩阵并计算 \(W_M^{00}\) |
| AFH Xe-131 Mathematica runner | research/afh_default_density_xe131/run_afh_default_xe131.wls | 调用官方 AFH 包生成原生响应 |
| AFH mpmath full-grid validation | research/afh_default_density_xe131/verify_afh_mpmath_full_grid.py | 独立 60 位精度有限和对照全部 2401 个 q 节点 |
| q convention audit | research/afh_default_density_xe131/audit_response_momentum_conventions.py | 对照论文响应 q、精确运动学 q 和 Xe-131 的响应差异 |
| Mathematica/Python 对照 | research/afh_default_density_xe131/verify_afh_xe131_native.wls | 原生 AFH 与 Python 网格比较 |
| 四 benchmark 响应替换 | research/afh_default_density_xe131/recompute_afh_four_benchmarks.py | AFH/GCN/JJ55 同网格截面对照 |
| 四 benchmark 截面重构 | research/afh_default_density_xe131/compute_four_benchmark_dsigma.py | 从 \(R_A,I_6\) 重构 Eq. (6) 截面 |
| 天然氙 halo fold | research/afh_default_density_natural_xenon_halo/run_afh_natural_xenon_halo_fold.py | 逐同位素速度积分和丰度加权 |

### F.2 关键输入和结果文件

### AFH Xe-131

- afh_default_xe131_density_matrix.csv：67 项官方内置矩阵提取结果；
- output/afh_default_xe131_WM00.csv：2401 点响应网格；
- output/minima.csv：细化极小值；
- output/figure2_dip_check.csv：101、267、542 keV 参考点；
- output/metadata.json：源文件哈希、质量、\(b_A\)、归一化和限制；
- output/mpmath_full_grid_summary.json：2401 点、60 位精度 mpmath 全网格验证汇总；
- CI artifact afh-xe131-mpmath-full-grid-validation：完整逐点比较 CSV 和 JSON summary。
- AFH_DEFAULT_XE131_NORMALIZATION_AUDIT.md：来源和归一化审计；
- AFH_COUPLING_NORMALIZATION_MAPPING.md：接口耦合映射。

### 四 benchmark 截面对照

- output/figure2_four_benchmarks_AFH_GCN_JJ55_corrected.csv；
- output/figure2_four_benchmarks_AFH_GCN_JJ55_wide_audit.csv；
- FOUR_BENCHMARK_CROSS_SECTION_AUDIT.md。

四组 benchmark 各有 160 个反冲能量点；三种核响应模型共形成 1920 行 long table 和 640 行 wide table。该对照固定同一组 \(I_6(E_R)\) 网格，只替换 \(R_A(E_R)\) 并重新计算 Eq. (6) 的截面前因子。因此它是受控的核响应替换比较，**不是重新独立计算 4×160 个三体积分**。该脚本采用固定 \(v=800\) km/s；这一速度高于截断 SHM 的 776 km/s 端点，所以这组结果是固定速度截面诊断，不能直接当作截断 SHM 支持区间内的 halo 事件率。

### 天然氙 halo fold

- input/natural_xenon_isotope_weights.csv；
- input/afh_response_samples.csv；
- results/isotope_halo_contributions_compact.csv；
- results/natural_xenon_halo_rates.csv；
- results/vmin_by_isotope_at_101keV.csv；
- results/kernel_order_crosschecks.csv；
- results/speed_quadrature_crosschecks.csv；
- results/halo_pdf_normalization.csv；
- results/metadata.json；
- results/natural_xenon_q_convention_audit.csv；
- results/xe131_afh_response_shift_NR_vs_exact.csv；
- results/q_convention_audit_summary.json；
- results/legacy_exact_reproduction_comparison.json（98 个同位素贡献和 14 个总速率的回归复现对照）。

当前 response samples 文件包含 7 种可用同位素在 4 个选定反冲能量上的 28 个响应样本。halo fold 对 14 组 benchmark/反冲能量/halo 组合分别输出 7 个同位素贡献，共 98 行逐同位素结果。

### F.3 复现命令

从仓库根目录执行。

AFH Xe-131 Python 响应：

~~~bash
python research/afh_default_density_xe131/run_afh_default_xe131.py \
  --outdir research/afh_default_density_xe131/output
~~~

AFH Xe-131 回归测试：

~~~bash
python -m unittest discover \
  -s research/afh_default_density_xe131 \
  -p 'test_*.py' -v
~~~

若只运行 AFH 响应本身的六项测试，将匹配模式改为 test_afh_default_xe131.py。

AFH mpmath 全网格独立验证：

~~~bash
python research/afh_default_density_xe131/verify_afh_mpmath_full_grid.py \
  --response-csv research/afh_default_density_xe131/output/afh_default_xe131_WM00.csv \
  --outdir research/afh_default_density_xe131/output/mpmath_full_grid
~~~

q 约定审计（需要一份新生成的 AFH Xe-131 响应 CSV）：

~~~bash
python research/afh_default_density_xe131/audit_response_momentum_conventions.py \
  --xe131-response-csv research/afh_default_density_xe131/output/afh_default_xe131_WM00.csv \
  --outdir research/afh_default_density_xe131/output/q_convention_audit
~~~

AFH 原生 Mathematica 运行需要官方 dmformfactor-V6.m 和可用的 Wolfram kernel。设置环境变量 DMFormFactorPath 指向该源文件，再运行：

~~~bash
wolframscript -file research/afh_default_density_xe131/run_afh_default_xe131.wls
~~~

独立原生验证脚本还需要设置 AFHPythonCSV 和 AFHAuditDir：

~~~bash
wolframscript -file research/afh_default_density_xe131/verify_afh_xe131_native.wls
~~~

天然氙 selected-point halo fold：

~~~bash
python research/afh_default_density_natural_xenon_halo/run_afh_natural_xenon_halo_fold.py \
  --response-q-convention legacy_exact
python research/afh_default_density_natural_xenon_halo/validate_archived_results.py
~~~

注意：legacy_exact 只用于复现当前已归档的 28 个 exact-q 响应样本。默认 manuscript_nr 会拒绝这些旧样本，直到七同位素 AFH 响应在 q_response=sqrt(2*m_A*E_R) 处重新生成。

Eq. (6) kernel 测试：

~~~bash
python -m unittest discover \
  -s research/figure2_full_reproduction/tests -v
~~~

四 benchmark 截面对照脚本需要归档的 GCN/JJ55 基础 CSV 和 AFH response CSV。当前归档输入的调用形式为：

~~~bash
python research/afh_default_density_xe131/recompute_afh_four_benchmarks.py \
  --base-csv research/afh_default_density_xe131/input/figure2_recalc_mV10_g2_1_v800_Xe131_full_5keV.csv \
  --afh-response-csv research/afh_default_density_xe131/output/afh_default_xe131_WM00.csv \
  --outdir research/afh_default_density_xe131/output
~~~

调用时必须保存输入文件、输出 CSV 和 metadata，不能只保留最终图像。

### F.4 数值验收矩阵

| 验证项目 | 当前状态 | 已有证据 | 尚未完成的部分 |
|---|---|---|---|
| AFH 67 项密度矩阵解析 | 已完成 | 官方源解析、CSV 逐项核对、67 项计数 | 原生 Mathematica 全网格输出比较 |
| AFH 默认 \(b_A\) | 已完成 | 公式、单位转换、Xe-131 数值回归测试 | 不需要拟合；不得用谷值调参 |
| AFH 零动量归一化 | 已完成（含有限精度修正） | 原始 \(A^2/4\)、物理响应 \(A^2\)、偏差 \(8.2523\times10^{-5}\) | 统一所有计算文件的质量和 \(q_{\rm resp}\) 约定 |
| AFH 谷值 | 已完成 | 离散候选点、直接响应局部极小化、minima.csv | 不需要调整 \(b_A\) |
| mpmath 独立有限和 | 已完成全网格 | 60 位精度、2401 个 q 节点；最大振幅绝对差 \(3.98\times10^{-14}\)，最大响应绝对差除以 \(A^2\) 为 \(1.22\times10^{-15}\) | 原生 Mathematica 逐点对照仍待完成 |
| AFH 原生 Mathematica | 待完成 | WLS runner 和比较脚本已归档；Python/mPMath 全网格交叉验证已通过 | 实际运行 Wolfram kernel 并保存逐点差异 |
| GCN/JJ55 对照 | 已完成归档 | 三种响应、四 benchmark、1920 行 long table | 对照共享既有 \(I_6\)，不是 640 次独立重算 |
| 三体运动学/Dirac trace | 已完成代表性检查 | 壳条件、四动量闭合、显式自旋求和、干涉分解 | 扩展到更宽的参数和质量网格 |
| 三体积分收敛 | 已有 selected-point 验证 | 六个天然氙点 \(8×8×4\) 对 \(16×16×8\)，最大差异 \(2.19×10^{-4}\)；独立 Eq. (6) 测试点 \(16×16×8\) 对 \(32×32×16\)，相对差异小于 \(5×10^{-5}\) | 连续反冲谱全网格收敛 |
| 天然氙速度积分 | 已有 selected-point 验证（legacy q） | 五个点 32 对 64 速度节点，最大差异 \(3.31×10^{-6}\)；98 个逐同位素贡献和 14 个总速率重算后与旧档最大总速率差异 \(2.67×10^{-12}\) | 先生成 manuscript-NR 七同位素响应，再重算速率；连续谱和 halo 参数扫描 |
| q_response / q_kinematic 分离 | 已完成审计与代码保护 | 28 个天然氙样本识别为 exact-q；Xe-131 四点响应差异约 5.5–212.7 ppm | 重新生成七同位素 manuscript-NR 响应样本并重算 halo fold |
| Xe-124/Xe-126 | 输入缺失 | 缺失丰度合计 0.001842 | 取得密度矩阵并补算响应、阈值和速率 |
| LZ detector response | 尚未开展 | 当前仅有理论核反冲率 | 效率、能量分辨、曝光、选择切、背景和统计似然 |

这张表把软件测试、局部数值收敛和物理模型完整性分开。测试通过只说明被测试的代码路径满足相应断言，不等于所有参数点、所有核模型、halo 假设或实验响应都已验证。

### F.5 LZ detector-level 分析还缺少什么

当前输出是理论核反冲能量 \(E_R\) 上的

\[
\frac{dR}{dE_R}
\]

，单位 events/(kg day keV)。它尚不能直接与 LZ 的观测事件分布或似然比较。

至少还需要：

1. 核反冲到观测量的响应模型，例如 S1/S2 或分析采用的重建能量变量；
2. 能量相关的信号接受效率和选择切；
3. 能量分辨函数，将真实 \(E_R\) 卷积到观测变量；
4. 实际有效曝光和数据质量区间；
5. 分析区域内的背景模型及其不确定度；
6. 与指定 LZ 数据集一致的信号/背景 likelihood。

因此当前天然氙结果应称为 **pre-detector theoretical rate**，不能称为完整 LZ recast、实验排除或对某个候选事件的统计解释。

### F.6 历史数据和版本管理原则

1. 保留官方 AFH ZIP 与源文件 SHA-256。
2. 保留原始 67 项密度矩阵，不通过改写系数或 \(b_A\) 修正谷值。
3. 保留 AFH raw response 与物理 equal-\(p,n\) response 两列，因子 4 只应用一次。
4. 早期错误的 AFH response CSV 拼接换行和 benchmark CSV 中 AFH 列误复制 GCN 的版本应标记为 superseded；当前使用 corrected archive。
5. 任何新的 \(q_{\rm resp}\)、核质量、halo 参数、宽度方案或求积阶数都应产生新的输出和 metadata，不覆盖历史结果。
6. 主报告包含完整附录 A–G；本目录中的七份独立附录与主报告对应章节保持同步。
7. 程序、CSV、JSON 和源文件继续保存在各自计算目录，文档只解释其定义、来源、调用方式和验证边界。

---

## 附录 G：核响应动量与精确三体运动学动量的约定审计

### G.1 两个 \(q\) 的物理定义

论文在核响应中采用

\[
y=\frac{b_A^2m_AE_R}{2}.
\]

由于 AFH 的谐振子变量为 \(y=(qb_A/2)^2\)，这对应

\[
\boxed{q_{\rm resp}^{\rm NR}=\sqrt{2m_AE_R}}.
\]

另一方面，核初末态均在质量壳上：

\[
P^\mu=(m_A,\mathbf 0),\qquad
P'^\mu=(m_A+E_R,\mathbf q_{\rm kin}),
\qquad P'^2=P^2=m_A^2.
\]

因此

\[
\boxed{q_{\rm kin}^{\rm exact}
=|\mathbf q_{\rm kin}|
=\sqrt{2m_AE_R+E_R^2}}.
\]

这两个量分别服务于不同的近似层次：

- \(q_{\rm resp}^{\rm NR}\)：论文明确采用的非相对论核响应变量；
- \(q_{\rm kin}^{\rm exact}\)：三体运动学中的精确空间反冲动量。

在 \(E_R\ll m_A\) 时二者很接近，但不应在代码中共用一个没有语义区分的 q 变量。尤其不能把精确的 \(q_{\rm kin}\) 代入 \(y\) 后，仍声称严格使用了论文当前写出的 \(y=b_A^2m_AE_R/2\)。

### G.2 28 个天然氙样本的实际约定

对当前七种有 AFH default density matrix 的氙同位素，以及

\[
E_R=101,\ 200,\ 267,\ 542\ {\rm keV},
\]

逐点读取

**research/afh_default_density_natural_xenon_halo/input/afh_response_samples.csv**

并使用 NIST 核质量

\[
m_A=(M_{\rm atom}-54m_e)u
\]

重新计算两种动量。28 个归档样本的 q_response_GeV 均与 \(q_{\rm kin}^{\rm exact}\) 相符，而不是与论文的 \(q_{\rm resp}^{\rm NR}\) 相符。

| \(E_R\) [keV] | \(\Delta q=q_{\rm exact}-q_{\rm NR}\) [keV] | 相对差异 [ppm] |
|---:|---:|---:|
| 101 | 0.031899–0.032882 | 0.199–0.212 |
| 200 | 0.088887–0.091626 | 0.395–0.420 |
| 267 | 0.137106–0.141332 | 0.527–0.560 |
| 542 | 0.396542–0.408764 | 1.071–1.138 |

因此，原天然氙 halo-fold 的 \(R_A\) 样本采用了精确空间动量；不能把它们直接描述成按论文 \(y(E_R)\) 处方重新生成的 AFH 响应样本。

### G.3 Xe-131 响应曲线上的直接数值影响

为避免只凭 \(\Delta q/q\) 判断响应误差，使用本轮 CI 重新生成的 2401 点 AFH default Xe-131 响应表，对同一 NIST Xe-131 核质量分别在 \(q_{\rm resp}^{\rm NR}\) 和 \(q_{\rm kin}^{\rm exact}\) 处进行 PCHIP 插值。

| \(E_R\) [keV] | \(q_{\rm NR}\) [MeV] | \(q_{\rm exact}\) [MeV] | \(R_A(q_{\rm NR})\) | \(R_A(q_{\rm exact})\) | \(\Delta R/R_{\rm NR}\) [ppm] |
|---:|---:|---:|---:|---:|---:|
| 101 | 156.925981 | 156.926013 | 0.321015586 | 0.321008412 | -22.35 |
| 200 | 220.825469 | 220.825560 | 9.628602910 | 9.628550361 | -5.46 |
| 267 | 255.146606 | 255.146745 | 0.006769034 | 0.006767594 | -212.68 |
| 542 | 363.524602 | 363.525006 | 0.003280695 | 0.003280375 | -97.35 |

这些数值说明：

1. 动量本身的差异只有约 \(0.2\)–\(1.1\) ppm；
2. 在核响应斜率较大的反冲点，响应相对变化可以达到约 \(2.1\times10^{-4}\)；
3. 这组 Xe-131 数值不能作为所有六种其他同位素的响应误差上界；
4. 更不能仅凭小的 \(\Delta q/q\) 就断言天然氙 halo-fold 事件率完全不变。

当前归档的七同位素事件率没有用 \(q_{\rm NR}\) 重新计算，故本附录不把上表解释为已经完成的天然氙速率修正。

### G.4 代码中的明确分离

本轮代码审计和防误用改动为：

- **research/figure2_full_reproduction/rate_kinematics.py**：momentum_transfer 保持精确 \(q_{\rm kin}^{\rm exact}\)，供三体运动学使用；
- **research/figure2_full_reproduction/joint_xe131.py**：固定 Xe-131 响应查询使用论文定义的 \(q_{\rm resp}^{\rm NR}\)；
- **research/afh_default_density_xe131/recompute_afh_four_benchmarks.py**：固定速度 AFH 响应插值使用 \(q_{\rm resp}^{\rm NR}\)；
- **research/afh_default_density_xe131/compute_four_benchmark_dsigma.py**：同样使用 \(q_{\rm resp}^{\rm NR}\)；
- **research/afh_default_density_natural_xenon_halo/run_afh_natural_xenon_halo_fold.py**：现在将响应动量约定与三体运动学动量分开，默认选择 manuscript_nr；只有显式传入 --response-q-convention legacy_exact 才能复现旧的精确-q 样本。

若选择的响应动量与样本文件中的 q 不一致，程序现在会报错，并要求重新生成 \(R_A\)，不会静默地只修改 q 标签。

### G.5 为什么还没有直接更新七同位素 \(R_A\) 样本

旧天然氙响应来源表的归档记录为：

- 文件名：afh_xe_isotope_responses.csv
- 数据行数：16,807（另有一行表头）
- SHA-256：44c88f3aaf2fb212facbe68432d38389374255432eec04ce8a76437c82c1be3a

这份完整七同位素响应表目前没有随 PR #7 提交；仓库只保存了 28 个 selected-point 样本和该文件的哈希。当前可直接复用的 AFH v6.0 源翻译完整响应网格只有 Xe-131。

因此，不能仅把 28 个样本中的 q_response_GeV 改成 \(q_{\rm NR}\)，同时保留旧 \(R_A\) 数值；那样会把“响应在 \(q_{\rm exact}\) 处计算”错误地标记成“响应在 \(q_{\rm NR}\) 处计算”。

要完成严格修正，需要重新取得七同位素的完整 AFH v6.0 响应表（或官方 AFH v6.0 源包和相应 default density matrices），在每个反冲点直接计算

\[
R_A^{\rm new}(E_R)
=
R_A\!\left(\sqrt{2m_AE_R}\right),
\]

随后重新运行逐同位素三体积分和 halo fold。旧的精确-q 结果必须保留为 legacy 对照。

### G.6 机器可读审计结果

本轮 CI 运行 43038372836 已通过，并保存 q-convention audit artifact。相同结果已提交到仓库：

- research/afh_default_density_natural_xenon_halo/results/natural_xenon_q_convention_audit.csv（28 行逐同位素、逐反冲点动量对照）；
- research/afh_default_density_natural_xenon_halo/results/xe131_afh_response_shift_NR_vs_exact.csv（Xe-131 四点 PCHIP 响应对照）；
- research/afh_default_density_natural_xenon_halo/results/q_convention_audit_summary.json（机器可读汇总）。

[查看 CI 运行及其 artifact](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43038372836)。

### G.7 当前状态与验收标准

| 项目 | 状态 | 说明 |
|---|---|---|
| 两种 \(q\) 的解析定义 | 已完成 | \(q_{\rm resp}^{\rm NR}\) 与 \(q_{\rm kin}^{\rm exact}\) 分开 |
| 28 个天然氙样本约定识别 | 已完成 | 归档样本全部匹配 exact-q |
| Xe-131 的 \(R_A(q_{\rm NR})\) 与 \(R_A(q_{\rm exact})\) 对照 | 已完成 | 使用新生成的 2401 点 AFH Xe-131 表 |
| 天然氙 halo 程序防误用与 legacy 回归 | 已完成 | 默认 NR 会拒绝旧样本；legacy_exact 重算 98 个贡献和 14 个总速率，最大总速率差异 \(2.67\times10^{-12}\)，CI 通过 |
| 七同位素 AFH 响应样本重新生成 | 待完成 | 需要完整 AFH 七同位素响应表或源包 |
| 七同位素三体积分与 halo fold 更新 | 待完成 | 必须在新的 \(R_A\) 样本生成后执行 |

本审计不改变三体运动学中的精确 \(q_{\rm kin}\)，也不对已有 halo rate 作经验重标度。它只明确响应函数的输入约定，并阻止今后把两种不同的动量定义混用。
