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
---

## 技术附录（独立文件）

为便于检索、引用和单独维护，详细推导与复现说明拆分为六份独立 Markdown 文件。正文保留研究主线和关键结果，技术细节见下列附录：

| 附录 | 内容 | 文件 |
|---|---|---|
| A | 三体运动学、相空间边界与 Dirac 振幅 | [09A_three_body_kinematics_amplitude.md](appendices/09A_three_body_kinematics_amplitude.md) |
| B | AFH v6.0 密度矩阵、谐振子基底与响应实现 | [09B_afh_v6_density_matrix_response.md](appendices/09B_afh_v6_density_matrix_response.md) |
| C | AFH isoscalar 归一化与因子 4 | [09C_afh_isoscalar_factor4_normalization.md](appendices/09C_afh_isoscalar_factor4_normalization.md) |
| D | 天然氙同位素、丰度和核靶归一化 | [09D_natural_xenon_isotope_target.md](appendices/09D_natural_xenon_isotope_target.md) |
| E | 实验室系速度分布、三体最小速度与 halo folding | [09E_halo_velocity_vmin_folding.md](appendices/09E_halo_velocity_vmin_folding.md) |
| F | 计算程序、数据文件、收敛验收和复现命令 | [09F_numerical_validation_reproduction.md](appendices/09F_numerical_validation_reproduction.md) |

附录与主报告使用同一研究分支维护。程序、CSV 和机器可读结果仍保存在各自计算目录中；附录负责解释其定义、调用方式和验证边界，不复制大体积数据。
