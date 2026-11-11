# AFH v6.0 氙核响应与三体暗物质散射：对话整理及阶段性研究记录

> 整理日期：2026-11-11  
> 对话来源：[ChatGPT 分享对话](https://chatgpt.com/share/6af4660e-e388-83ea-a86a-2482b065dcea)  
> 对应研究仓库：\`lm846802297-bit/LZ-3-body-for-hdm\`  
> 当前归档位置：PR #7 的研究分支  
> 研究对象：\(\chi_1+A\rightarrow\chi_1+A+s\) 三体核反冲过程

## 摘要

本次讨论的核心，是把论文 Eq. (6) 中的三体微分散射截面与真实氙靶的核结构和银河系暗物质速度分布连接起来。研究分成三个层次：

1. **单一同位素、固定入射速度：** 计算 \(d\sigma_A/dE_R\)，其中核响应 \(R_A(E_R)\) 与三体相空间积分 \(I_6\) 在给定同位素和运动学条件下因式分解。
2. **核结构输入：** 采用 AFH/DMFormFactor v6.0 内置的 Xe-131 default density matrix，严格使用文献给出的谐振子长度处方，不把 \(b_A\) 当作拟合参数；并处理 AFH 原始 isoscalar response 与物理等质子、等中子耦合之间的因子 4。
3. **真实天然氙靶的理论速率：** 对可用氙同位素按天然丰度求和，并对实验室系暗物质速度分布积分，得到 \(dR/dE_R\)。这一步与固定速度下的 \(d\sigma_A/dE_R\) 是不同的物理量。

目前已经形成 AFH default Xe-131 响应、GCN/JJ55 对照、四组固定速度 benchmark，以及天然氙 selected-point halo-folded rate 的可复现归档。需要继续明确的边界是：AFH 原生 Mathematica 程序尚未在 Wolfram kernel 中实际运行；天然氙结果仍是理论 selected-point rates，尚不是完整的 LZ detector-level likelihood/recast。

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

- 内置矩阵名称：\`sdgXe131\`；
- 同位素选择：\`SetIsotope[54,131,"default","default"]\`；
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

- AFH 原始压缩包 SHA-256：\`4e0f70e6e780f3f4a40faa14792cae239d1989cf15d1e211b4fd7389b0460727\`；
- Mathematica 源文件：\`v6/dmformfactor-V6.m\`；
- 源文件 SHA-256：\`dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372\`。

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
- 独立 60 位精度 mpmath 有限和计算，在代表性振幅点与 Python 结果相符，精度优于 \(2\times10^{-11}\)；
- Xe-131 AFH 脚本的六项 Python regression tests 通过；
- 四组 benchmark 的 AFH/GCN/JJ55 响应替换表完成逐点重构检查；
- 天然氙 Eq. (6) kernel 与速度积分完成网格收敛 spot checks；
- 天然氙归档完整性验证 workflow 通过。

### 8.2 尚未完成或不能过度声称的事项

1. **AFH 原生 Mathematica 验证仍待执行。** 原生 runner 和比较程序已归档，但当前执行环境没有 Wolfram kernel。现阶段结果应称为“基于 AFH v6.0 源码翻译的 Python 计算，并通过独立高精度数值检查”，不能称为已经完成 Mathematica 原生复算。
2. **Xe-124/Xe-126 尚未纳入。** 缺少当前 AFH v6.0 内置 density matrix；七种可用同位素的丰度没有重归一化。
3. **天然氙结果是 selected-point rates。** 当前不是连续完整反冲谱。
4. **尚未加入 LZ detector response。** 没有 detector efficiency、能量分辨率、曝光、分析 cuts、背景模型或 likelihood。因此这些理论速率不能直接当作 LZ 预期观测事件数，也不能称为完整的 LZ 数据重铸。
5. **极点宽度是条件性的。** 只包括给定假设下的 \(\chi_2\to\chi_1s\) 标量通道，不等于完整模型的矢量加标量自能。
6. **halo 模型依赖尚未做系统扫描。** untruncated MB 只用于高速度尾部敏感性诊断，不作为默认 halo 结果。

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
2. **锁定 AFH 归一化实现。** 对照原始 \(W_M^{00}\)、因子 4 映射和零动量归一化，确保论文公式、Python 程序、Mathematica 程序和归档 CSV 使用同一约定。
3. **补全或明确缺失同位素处理。** 在没有可靠 AFH Xe-124/Xe-126 响应之前，保留当前覆盖率和不重归一化的明确限制，不用平均核响应代替。
4. **扩展天然氙连续反冲谱。** 当前 selected points 用于验证阈值和 halo 端点；连续谱需要单独做网格和收敛检查。
5. **最后进行 LZ detector-level 映射。** 在取得并核实效率、分辨率、曝光、cuts 和背景输入后，再计算预期事件数或构建 likelihood；当前 selected-point rate 不应提前解释成 LZ 排除或信号拟合。

---

## 10. 代码、数据和文献入口

### 仓库内的主要研究记录

- AFH default Xe-131 README：\`research/afh_default_density_xe131/README.md\`
- AFH 因子 4 归一化映射：\`research/afh_default_density_xe131/AFH_COUPLING_NORMALIZATION_MAPPING.md\`
- AFH Xe-131 源码与归一化审计：\`research/afh_default_density_xe131/AFH_DEFAULT_XE131_NORMALIZATION_AUDIT.md\`
- AFH/GCN/JJ55 对照：\`research/afh_default_density_xe131/output/AFH_DEFAULT_VS_GCN_JJ55_COMPARISON.md\`
- 四组 benchmark corrected results：\`research/afh_default_density_xe131/output/AFH_FOUR_BENCHMARKS_CORRECTED_RESULTS.md\`
- 四组 benchmark 截面审计：\`research/afh_default_density_xe131/output/FOUR_BENCHMARK_CROSS_SECTION_AUDIT.md\`
- 天然氙 halo fold README：\`research/afh_default_density_natural_xenon_halo/README.md\`
- 天然氙 halo fold 审计：\`research/afh_default_density_natural_xenon_halo/results/NATURAL_XENON_HALO_FOLD_AUDIT.md\`

### 外部参考

- AFH nuclear response：Anand, Fitzpatrick and Haxton, *Weakly interacting massive particle-nucleus elastic scattering response*, Phys. Rev. C 89 (2014) 065501, [arXiv:1308.6288](https://arxiv.org/abs/1308.6288)。
- LZ detector 官方介绍：[The LZ Detector](https://lz.lbl.gov/detector/)。
- AFH v6.0 原始 Mathematica 包及其源文件哈希记录见本研究目录的 README 和 provenance 文件。

---

**归档状态说明：** 本文是对本轮 AFH 核响应、三体积分、天然氙同位素和 halo folding 讨论的研究整理，不代表所有后续验证均已完成。当前 PR #7 仍为 Draft/Open；本文随该研究分支归档，不执行 PR 合并。

---

# 技术附录

本组附录与正文属于**同一份研究文档**。附录给出正文所引用公式的运动学来源、核响应约定、数值积分方法和复现边界。凡是现有代码或归档尚未确定的内容，均明确标为待核实，不以推测补齐。

## 附录 A：三体运动学、相空间边界与 Dirac 振幅

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

## 附录 B：AFH v6.0 密度矩阵、谐振子基底与响应实现

### B.1 源文件与同位素选择

本研究采用 DMFormFactor v6.0 的官方 Mathematica 源文件 \`v6/dmformfactor-V6.m\)，Xe-131 选择为

\[
\texttt{SetIsotope[54,131,"default","default"]}.
\]

内置密度矩阵为 \`sdgXe131\`，共 67 项。官方源文件及压缩包 SHA-256 已记录在正文第 3 节。提取出的 67 项矩阵保存在

\[
\texttt{research/afh\_default\_density\_xe131/afh\_default\_xe131\_density\_matrix.csv}.
\]

程序可重新解析官方 \`.m\` 文件，并将解析出的条目与 CSV 逐项核对。这里的 Python 结果来自对官方源函数的翻译，而不是把 GCN 或 JJ55 响应重新命名为 AFH。

### B.2 谐振子长度与无量纲变量

AFH default 的振子长度为

\[
b_A=
\sqrt{\frac{41.467}
{45A^{-1/3}-25A^{-2/3}}}\ {\rm fm}.
\]

长度单位转换采用

\[
1\ {\rm fm}=5.0677\ {\rm GeV}^{-1}.
\]

Xe-131 的数值为

\[
b_{131}=2.2923417985218975\ {\rm fm}
=11.61690053236942\ {\rm GeV}^{-1}.
\]

AFH 谐振子响应通常用无量纲变量

\[
y=\frac{b_A^2|\mathbf q|^2}{4}
\]

表示。在非相对论反冲近似 \(|\mathbf q|^2=2m_AE_R\) 下，

\[
y=\frac{b_A^2m_AE_R}{2}.
\]

**动量转移约定需要与具体计算文件一起读取。** 当前 Xe-131 四 benchmark response-substitution 脚本使用

\[
q_{\rm resp}^{(131)}=\sqrt{2m_AE_R},
\]

而天然氙 halo-fold 程序对各同位素响应样本使用

\[
q_{\rm resp}^{(\rm nat)}
=\sqrt{2m_AE_R+E_R^2}.
\]

两者分别对应非相对论近似与精确核反冲三动量。由于 \(E_R\ll m_A\)，数值差异很小，但二者不是逐字相同的约定。跨文件比较时必须注明使用哪一种；若未来要求逐点 bit-level 对照，应先统一响应动量定义并重新生成相应样本，不能把两种表混用后宣称完全相同。

### B.3 \(W_M^{00}\) 的实现

AFH 源代码的相关函数包括 \`Lnumber\`、\`Nodal\`、\`mjelement\`、\`BesselElement\`、\`FF\` 和 \`ResponseNuclear\`。本研究将这些源函数翻译为 Python 有限和实现，并计算弹性 \(M\) 响应。对于 Xe-131 当前使用的密度矩阵，响应中保留偶数多极 \(J=0,2\) 的贡献。

原始 AFH 输出记为 \(W_{M,\rm AFH}^{00}(y)\)。在正文所采用的物理等质子、等中子耦合约定下，不能把该原始 isoscalar 输出未经映射就直接放入截面。

### B.4 极小值的数值定位

Xe-131 响应表覆盖

\[
0\le q\le0.6\ {\rm GeV}
\]

，网格步长为 \(0.25\) MeV，共 2401 点。极小值定位先由离散网格识别局部候选区，再对局部响应函数作数值细化。应同时保存：

- 原始离散网格的最小点；
- 细化后的 \(q_{\min}\)；
- 由该 \(q_{\min}\) 换算的 \(E_{R,\min}\)；
- \(R_{\min}/R(0)\)；
- 局部网格步长和细化算法。

不能只保存谷值位置而丢失原始响应网格，也不能把插值产生的细化精度误认为原始核结构输入具有同等精度。

### B.5 当前独立验证边界

已经完成：

1. 官方 AFH 源文件的 67 项 Xe-131 矩阵解析；
2. 解析矩阵与归档 CSV 逐项比较；
3. Python 源码翻译的回归测试；
4. 代表性有限和与独立 60 位精度 mpmath 计算比较。

仍待完成：

- 在安装 Wolfram kernel 的环境中运行官方 Mathematica 包；
- 将 Mathematica 原生输出与 Python 表逐点比较；
- 统一 Xe-131 固定速度表和天然氙响应样本的 \(q_{\rm resp}\) 约定，或在输出元数据中永久保留二者差别。

---

## 附录 C：AFH isoscalar 归一化与物理核子耦合的因子 4

### C.1 物理相干核电荷

对于等质子、等中子矢量耦合，

\[
g_p=g_n=g_{VN}.
\]

零动量转移时，核子的相干振幅正比于

\[
Zg_p+(A-Z)g_n=A g_{VN}.
\]

因此，若截面前因子已经显式提出 \(g_{VN}^2\)，核响应必须满足

\[
R_A^{\rm phys}(0)=A^2.
\]

### C.2 AFH 系数定义

AFH 标准 isospin 分解写作

\[
c^0=\frac{c^p+c^n}{2},
\qquad
c^1=\frac{c^p-c^n}{2}.
\]

对 \(c^p=c^n=g_{VN}\)，得到

\[
c^0=g_{VN},\qquad c^1=0
\]

是标准数学定义下的分解结果。但分布的 DMFormFactor v6.0 Mathematica 接口在其系数设置和响应构造中采用了不同的内部归一化：其 \`SetCoeffsNonrel[op,c,0]\` 接口对应的等质子、等中子输入为 \(c_p=c_n=c/2\)，而 \`ResponseNuclear[y,1,0,0]\` 返回的单个 isoscalar response 在零动量处按 \(A^2/4\) 归一化。

因此，不能仅凭“标准 isospin 分解”这几个字就把接口输入 \(c\) 与论文中定义的物理单核子耦合 \(g_{VN}\) 直接等同。必须按实际包接口的定义进行映射。

### C.3 因子 4 的物理响应映射

对 AFH v6.0 的原始输出，

\[
R_{\rm AFH,raw}(q)
=\frac{4\pi}{2J_A+1}W_{M,\rm AFH}^{00}(q),
\]

其零动量值为

\[
R_{\rm AFH,raw}(0)\simeq\frac{A^2}{4}.
\]

而论文截面前因子使用的是物理的 \(g_{VN}^2\)，故必须使用

\[
\boxed{
R_A^{\rm phys}(q)=4R_{\rm AFH,raw}(q)
=\frac{16\pi}{2J_A+1}W_{M,\rm AFH}^{00}(q)
}
\]

使得

\[
R_A^{\rm phys}(0)=A^2.
\]

这与 \(g_{VN}=3g_{Vq}\) 的夸克到核子匹配是不同问题。因子 4 不改变 \(g_{VN}=3g_{Vq}\)，也不应通过修改 \(b_A\) 或密度矩阵来补偿。

### C.4 有限小数精度修正

Xe-131 的源翻译结果为

\[
R_{\rm AFH,raw}(0)=4289.895955714993,
\qquad
A^2/4=4290.25.
\]

相对偏差

\[
8.2522996\times10^{-5}.
\]

归档物理响应使用

\[
R_A^{\rm phys}(q)
=A^2\frac{R_{\rm AFH,raw}(q)}
{R_{\rm AFH,raw}(0)}.
\]

这是整体零动量归一化修正，不改变响应的 \(q\) 依赖，也不移动响应极小值。其目的在于避免有限小数密度矩阵使零动量相干归一化略微偏离理论值。

### C.5 独立文献对照

Oliver C. Gorton, *Shell Model Methods, Statistical Nuclear Reactions, and Beta-delayed Neutron Emission*, UC Irvine PhD dissertation (2024), Sec. 2.2, pp. 29–30，讨论了标准 isospin 约定与分发的 \`dmformfactor-prc.m\`、\`dmformfactor-V6.m\` 脚本之间的系数约定，并给出

\[
W_M^{00}(0)=\frac{1}{4\pi}\left(\frac A2\right)^2.
\]

参考链接：

https://www.escholarship.org/content/qt3ns8f1r8/qt3ns8f1r8.pdf

该文献是对 AFH v6.0 原始 isoscalar 零动量归一化的独立交叉检查；它不能替代对实际包版本和接口调用的源代码核查。

---

## 附录 D：天然氙同位素、丰度和核靶归一化

### D.1 天然丰度与 AFH 响应可用性

采用的天然氙原子丰度与本研究 AFH v6.0 内置响应可用性如下。核质量列为当前程序采用的 \((M_{\rm atom}-54m_e)u\)。

| 同位素 | 原子质量 [u] | 天然原子丰度 | AFH default 响应 |
|---|---:|---:|---|
| Xe-124 | 123.905892 | 0.000952 | 不可用 |
| Xe-126 | 125.9042983 | 0.000890 | 不可用 |
| Xe-128 | 127.903531 | 0.019102 | 可用 |
| Xe-129 | 128.9047808611 | 0.264006 | 可用 |
| Xe-130 | 129.903509349 | 0.040710 | 可用 |
| Xe-131 | 130.90508406 | 0.212324 | 可用 |
| Xe-132 | 131.9041550856 | 0.269086 | 可用 |
| Xe-134 | 133.90539466 | 0.104357 | 可用 |
| Xe-136 | 135.907214484 | 0.088573 | 可用 |

七种有 AFH default 响应的同位素覆盖

\[
\sum_{A\in\mathrm{available}}x_A=0.998158.
\]

Xe-124 与 Xe-126 的合计丰度为 \(0.001842\)。本阶段没有这两种同位素的相应 AFH default density matrix，因此没有纳入其响应贡献。

**丰度不重新归一化。** 也就是说，不把七种可用同位素的 \(x_A\) 除以 0.998158。这样保留了“当前计算只覆盖天然氙 99.8158% 的原子丰度”这一事实。缺失同位素的速率不能简单假定为总速率的 0.1842%，因为它们的核质量、响应函数和运动学阈值都可能不同。

### D.2 核质量和每千克靶核数

同位素核质量按

\[
m_A=[M_{\rm atom}(A)-54m_e]u
\]

计算，忽略很小的电子结合能。这里 \(u=0.93149410242\) GeV，\(m_e=0.000548579909065u\)。

每千克天然氙的靶核数采用完整天然丰度的平均原子质量

\[
\overline M_{\rm Xe}=131.2927614479\ {\rm g/mol},
\]

\[
\boxed{
N_T=\frac{N_{\rm Av}\,1000}{\overline M_{\rm Xe}}
}.
\]

这里的 \(\overline M_{\rm Xe}\) 使用完整天然氙丰度，而同位素速率求和只包括当前 AFH 响应可用的七种同位素。两者的处理目的不同：前者确定每千克实际天然氙含有多少个原子，后者确定当前能计算哪些同位素贡献。

### D.3 为什么不能用平均核质量替代同位素求和？

每个同位素的微分截面为

\[
\frac{d\sigma_A}{dE_R}(v)
\propto
m_A R_A(E_R) I_{6,A}(v,E_R)
\]

并且 \(W_{\max,A}\)、\(v_{\min,A}\) 也依赖 \(m_A\)。因此一般有

\[
\sum_A x_A\,\frac{d\sigma_A}{dE_R}
\ne
\frac{d\sigma_{\overline A}}{dE_R}.
\]

尤其在阈值附近，不同同位素可能分别处于开放或关闭状态。对每种同位素都必须使用自己的核质量、AFH 响应、相空间边界和最小速度。

---

## 附录 E：实验室系速度分布、三体 \(v_{\min}\) 与 halo folding

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

## 附录 F：计算程序、数据文件、收敛验收和复现命令

### F.1 主要程序入口

| 任务 | 程序或目录 |
|---|---|
| Eq. (6) 三体 kernel | \`research/figure2_full_reproduction/eq6_kernel.py\` |
| AFH Xe-131 response | \`research/afh_default_density_xe131/run_afh_default_xe131.py\` |
| AFH Xe-131 benchmark 截面替换 | \`research/afh_default_density_xe131/compute_four_benchmark_dsigma.py\` |
| AFH 天然氙 halo fold | \`research/afh_default_density_natural_xenon_halo/run_afh_natural_xenon_halo_fold.py\` |
| AFH Xe-131 源矩阵 | \`research/afh_default_density_xe131/afh_default_xe131_density_matrix.csv\` |
| 天然氙同位素权重 | \`research/afh_default_density_natural_xenon_halo/input/natural_xenon_isotope_weights.csv\` |
| 天然氙响应样本 | \`research/afh_default_density_natural_xenon_halo/input/afh_response_samples.csv\` |

### F.2 主要复现命令

从仓库根目录运行。

AFH Xe-131：

\`\`\`bash
python research/afh_default_density_xe131/run_afh_default_xe131.py --outdir research/afh_default_density_xe131/output
python -m unittest research.afh_default_density_xe131.test_afh_default_xe131
\`\`\`

四 benchmark 的 AFH/GCN/JJ55 截面对照需要提供归档的 GCN/JJ55 基础表和 AFH 响应表：

\`\`\`bash
python research/afh_default_density_xe131/compute_four_benchmark_dsigma.py \\
  --base-csv <archived-gcn-jj55-base.csv> \\
  --afh-response-csv research/afh_default_density_xe131/output/afh_default_xe131_WM00.csv \\
  --out-csv <output.csv> \\
  --metadata <metadata.json>
\`\`\`

天然氙 selected-point halo fold：

\`\`\`bash
python research/afh_default_density_natural_xenon_halo/run_afh_natural_xenon_halo_fold.py
\`\`\`

天然氙程序默认采用 \(m_{\chi_1}=1\) TeV、\(m_V=10\) GeV、耦合乘积平方 \(10^{-8}\)、\(g_2=1\)、\(\rho_\chi=0.3\) GeV/cm³、32 个速度节点和 \(8\times8\times4\) 的三体求积。修改输入时必须同步保存新的 metadata，不应覆盖历史输出。

### F.3 输出和审计文件

主要结果文件包括：

- \`output/afh_default_xe131_WM00.csv\`：Xe-131 AFH response 网格；
- \`output/minima.csv\`：响应极小值；
- \`output/figure2_four_benchmarks_AFH_GCN_JJ55_corrected.csv\`：修正后的四 benchmark 长表；
- \`output/FOUR_BENCHMARK_CROSS_SECTION_AUDIT.md\`：四 benchmark 截面审计；
- \`results/natural_xenon_halo_rates.csv\`：天然氙 selected-point halo-folded rates；
- \`results/isotope_halo_contributions_compact.csv\`：同位素贡献；
- \`results/kernel_order_crosschecks.csv\`：三体求积阶数对照；
- \`results/speed_quadrature_crosschecks.csv\`：速度积分阶数对照；
- \`results/halo_pdf_normalization.csv\`：速度 PDF 归一化；
- \`results/vmin_by_isotope_at_101keV.csv\`：101 keV 的逐同位素阈值；
- \`results/metadata.json\`：输入和计算约定。

### F.4 关键验收检查

**运动学与矩阵元**

- 四动量守恒；
- 所有外腿质量壳条件；
- \(K^2=W^2\)；
- Dirac trace 与显式自旋态求和对照；
- before、after、interference 三项之和等于完整迹；
- 关闭相空间时积分为零。

**核响应**

- 67 项 AFH density matrix 与官方源文件一致；
- \(R_A(0)=A^2\)；
- 不拟合 \(b_A\)；
- AFH、GCN、JJ55 的核响应替换保持相同 \(I_6\)；
- 插值不外推，且记录 \(q_{\rm resp}\) 约定。

**数值积分**

- 增加 \(W^2,z,\phi_*\) 求积阶数；
- 增加 halo 速度求积阶数；
- 检查速度 PDF 归一化；
- 检查逐同位素开放/关闭条件；
- 由 \(R_A\)、\(I_6\) 和总前因子重构 \(d\sigma_A/dE_R\)。

### F.5 结果状态的严格表述

当前应采用以下状态描述：

| 项目 | 状态 |
|---|---|
| AFH v6.0 源码翻译和 Xe-131 矩阵提取 | 已完成 |
| AFH 零动量物理归一化映射 | 已完成，含有限精度修正 |
| Xe-131 AFH/GCN/JJ55 对照 | 已归档 |
| 四 benchmark 固定速度截面替换 | 已归档；共用既有 \(I_6\) 网格 |
| 天然氙七同位素 selected-point halo fold | 已归档 |
| AFH 原生 Mathematica/Wolfram 执行 | 待完成 |
| Xe-124/Xe-126 AFH 响应 | 当前输入集中缺失 |
| 天然氙连续反冲谱全网格验证 | 待完成 |
| LZ detector response 与 likelihood | 尚未开展 |

通过软件测试只能说明程序满足相应的代码检查，不能自动证明未指定的粒子场性质、核模型选择、halo 假设或探测器模型已经得到验证。

### F.6 历史数据修正原则

旧结果不应被静默覆盖。特别是：

1. 早期 AFH response CSV 的拼接换行错误已经修复；
2. 早期 benchmark CSV 的 AFH \(R_A\) 列曾误复制 GCN 值，现已由真实 AFH response 插值重新生成；
3. corrected archive 是当前引用版本；
4. 旧版文件若保留，应标记为 superseded，并说明错误来源；
5. 任何新的动量转移约定、halo 参数、求积阶数或宽度方案都应生成新版本结果和 metadata。

---

## 附录导航与阅读顺序

- 需要检查三体积分限、振幅和自旋迹：阅读附录 A。
- 需要复现 AFH 密度矩阵和核响应：阅读附录 B。
- 需要核对 AFH 因子 4：阅读附录 C。
- 需要核对天然氙靶组成：阅读附录 D。
- 需要理解 \(v_{\min}\) 和 halo-folding：阅读附录 E。
- 需要重新运行程序或审查验收边界：阅读附录 F。

**最终归档原则：** 正文和附录在同一个 Markdown 文件中统一维护；数值数据、源程序和机器可读输出仍保存在各自研究目录中，并由本文链接。这样既保持单一的叙述入口，也避免把大体积 CSV、程序和原始输入重复复制进文档。
