# AFH v6.0 Xe-131 核响应、三体暗物质散射与天然氙反冲率

> 整理日期：2026-11-11（原始主报告整理日期）
> 最近文档更新：2026-11-13（补入 Wolfram 14.0.0 原生 Mathematica/Python 2401 点响应审计及 SHA-256 归档；更新 F6 验证状态。该结果限定于 Xe-131 AFH response-level，不代表完整天然氙连续谱或 LZ likelihood）
> 对话来源：[ChatGPT 分享对话](https://chatgpt.com/share/6af4660e-e388-83ea-a86a-2482b065dcea)  
> 对应研究仓库：`lm846802297-bit/LZ-3-body-for-hdm`  
> 当前正式归档：main；PR #10 于 2026-11-13 合并，merge commit 724d9e7877fb76f4cc477fbb9e24e1e706bf37a6。PR #7 是此前研究分支内的历史合并记录。
> 研究对象：\(\chi_1+A\rightarrow\chi_1+A+s\) 三体核反冲过程

## 文档更新记录

- **2026-11-12：** 在附录 A 增加显式 Lorentz boost 及正交基构造，补全从 \(K\) 静止系到靶核静止系的四动量重建说明。
- **2026-11-12：** 修正附录 D.5 的旧动量约定描述，统一说明固定速度 Xe-131 benchmark 与天然氙 halo fold 均使用精确空间动量；两者区别在核质量输入。
- **2026-11-12：** 曾将动量约定审计暂列为独立补充文档；随后根据其对 AFH 响应输入和三体运动学的直接影响，将其恢复为正式附录 G。研究决定登记 H 仍独立存放。
- **2026-11-12：** 将主报告统一命名为 `09_afh_xe131_three_body_scattering_natural_xenon.md`；本轮进一步将动量约定审计纳入正式附录 G，H 保留为独立研究决定登记，并同步更新交叉引用。
- **2026-11-12：** 修复 detector-level 接口章节的重复编号。
- **2026-11-12：** PR #7 已 squash-merge 至 `research/figure2-p0-4-mainline`；更新本报告的归档状态、LZ 效率折叠完成项与尚未完成的 detector-level likelihood 边界。
- **2026-11-12：** 统一正文、附录 F 与 LZ detector-level 接口的状态描述，区分 GCN/JJ55 连续谱、AFH selected-point 结果及效率加权 rate-level 事件数。
- **2026-11-12：** 新增独立的阶段性结论章节，汇总理论核响应、天然氙结果、LZ rate-level event yields 与当前不可声称的实验结论。
- **2026-11-12：** 新增公式—符号—正文—程序—结果交叉引用索引；在 Eq. (6)、AFH 响应、halo-folded rate 和 LZ rate-level 公式旁加入推导与程序入口，并新增第 13 节快速导航。该工作为文档追溯性整理，不代表新增物理验证或数值计算。
- **2026-11-12：** 交叉核对主报告与附录 A 的 \(I_6\) 维度约定，将主公式明确写为无量纲 \(\lambda_{\rm dim}\)；在正文补出三体 \(v_{\min,A}\) 显式表达式，并补齐 \(a_A,\theta_q,N_{\rm Av}\) 的符号定义。该工作为公式记号和追溯性修订，不代表新增数值计算。
- **2026-11-13：** 将 450 keV supplied benchmark 的 pointwise \(\mathcal L_{00}\)/\(I_6\) 本地验收记录纳入主报告导航；明确其条件性 Dirac / pure-scalar / single-open-channel 宽度假设及单一诊断运动学点，不将其解释为天然氙速率。
- **2026-11-13：** 将独立的 Xe-131 fixed-speed 450 keV 曲线纳入结果覆盖表：GCN/JJ55 response、\(v=776\) km/s、\(M_A=131u\)、zero-width，105 个内部网格点；明确两端未覆盖的开放相空间区间仍需高阶积分。
- **2026-11-13：** PR #10 将研究成果正式提升至 main；同步修订主报告、附录 F、公式索引和 README 导航。该轮只做文档追溯和状态整理，不新增物理验证或数值计算。
- **2026-11-13：** 扩充主报告正文的物理推导和解释：补入非对角相互作用与虚 \(\chi_2\) 图像、核反冲空间动量与四动量不变量的区别、两张辐射图的 Dirac trace 和干涉、三体相空间及 Eq. (6) 前因子的来源、AFH 响应极小值的核结构含义、\(m_s/\Delta m\) 的不同作用、三体 \(v_{\min}\) 与 SHM 端点抑制，以及 LZ 一维效率折叠的概率解释。本轮不修改模型输入、数值程序或已归档数值结果。
- **2026-11-13：** 建立 P0 Figure 2 benchmark / 输入 / 参数 / 输出 / SHA-256 总索引（9 组、60 个文件条目，已纳入原生 Mathematica 输出和 AFH v6.0 `.m` 源文件），P1 物理公式交叉审查和 P2 科学结果状态表，并在第 13.5 节加入导航。交叉审查发现原始工作稿的 AFH raw-to-physical factor-of-four 与 exact spatial-q 定义不一致，已修正 `paper-source/main.tex` 并刷新 `paper-source/SHA256SUMS`；同时将天然氙 metadata 中误写为 SHA-256 的 40 位 Git blob SHA-1 改为真实 64 位文件 SHA-256，并在 runner / validator 中加入检查。本轮修复的是公式定义和 provenance，不重算已归档物理数值。

- **2026-11-13：** 将独立 Lorentz-invariant 三体相空间推导并入正文 §2.5.1–2.5.8 和附录 A.4.2；进一步补齐固定速度下 (m_{s,max}) 与 (E_R^*) 的解析极值、条件性 (chi_2	ochi_1s) 宽度、截断 SHM 实验室速度 PDF、天然氙靶核数及 halo 通量折叠的逐步推导，并同步主报告嵌入附录、独立附录文件和公式索引。本轮为解析推导与文档一致性更新，不修改数值程序、输入或归档结果。

- **2026-11-13：** 将 `research/p1-mma-local` 中已完成的 Wolfram 14.0.0 原生 AFH Xe-131 2401 点结果、Python 对照、minima、源文件和 SHA-256 manifest 逐文件纳入本 PR；更新 README、附录 B/G、F6 索引和 P0–P2 状态。该归档不改变 Eq. (6) kernel 或天然氙连续谱的完成边界。

## 摘要

本次讨论的核心，是把论文 Eq. (6) 中的三体微分散射截面与真实氙靶的核结构和银河系暗物质速度分布连接起来。研究分成三个层次：

1. **单一同位素、固定入射速度：** 计算 \(d\sigma_A/dE_R\)，其中核响应 \(R_A(E_R)\) 与三体相空间积分 \(I_6\) 在给定同位素和运动学条件下因式分解。
2. **核结构输入：** 采用 AFH/DMFormFactor v6.0 内置的 Xe-131 default density matrix，严格使用文献给出的谐振子长度处方，不把 \(b_A\) 当作拟合参数；并处理 AFH 原始 isoscalar response 与物理等质子、等中子耦合之间的因子 4。
3. **真实天然氙靶的理论速率：** 对可用氙同位素按天然丰度求和，并对实验室系暗物质速度分布积分，得到 \(dR/dE_R\)。这一步与固定速度下的 \(d\sigma_A/dE_R\) 是不同的物理量。

目前已经形成 AFH default Xe-131 响应、GCN/JJ55 核模型对照、四组固定速度 benchmark、AFH 天然氙 selected-point halo-folded rates，以及 GCN/JJ55 天然氙连续反冲谱。LZ 2026 Fig. S2 的一维 final-ROI efficiency 曲线及灰色系统包络也已从官方 PDF 提取，并与独立数字化结果对照；基于 GCN/JJ55 连续谱、2.84 tonne-year exposure 和该效率曲线，已得到初步 efficiency-weighted rate-level event yields。该结果不是完整的 LZ likelihood recast。Xe-131 AFH 响应现已同时通过 60 位精度 mpmath 独立有限和检查，以及 Wolfram 14.0.0 原生 Mathematica 对 2401 个 q 节点的逐点比较；Python 与 Mathematica 的 q 网格完全一致，四种响应量的最大相对差异为 \\(3.59\\times10^{-9}\\)，全部 2401 点通过。原始 AFH 响应、物理等质子等中子响应、因子 4 一次转换和有限密度矩阵精度导致的 q=0 小归一化修正均分别归档。该原生验证仅针对 Xe-131 响应层，不等于完整 AFH 天然氙连续谱或 LZ likelihood。进一步核查 AFH 原始定义后，确认其响应变量 \(y=(q b_A/2)^2\) 中的 \(q\) 是空间动量转移；现有 28 个天然氙响应样本采用的 exact spatial q 与精确三体质量壳关系一致。exact spatial q 作为默认，NR-q 仅作小反冲近似对照。当前 AFH 天然氙结果仍限于 selected points；连续谱和 LZ rate-level yields 使用 GCN/JJ55 响应，不能混称为 AFH 连续谱或完整实验重铸。

本轮正文还补入了从相互作用拉格朗日量到两张树图、Dirac trace、三体相空间和 Eq. (6) 整体前因子的连贯推导；附录进一步逐步推导最优反冲能量与最大标量质量、条件性二体 pole width、截断 SHM 实验室速度 PDF、天然氙靶核数和通量事件率，并解释核响应极小值、三体阈值、halo 端点和 LZ 效率折叠各自代表的物理机制。完整的 Lorentz boost、相空间归一化、AFH 密度矩阵有限和、因子 4、同位素输入和 halo 数值约定仍分别保留在附录 A–G，避免正文与附录互相替代。

另外，仓库还归档了一个独立的 450 keV benchmark：其一是单一运动学点的 \(\mathcal L_{00}\) 与 reduced \(I_6\) 对照，使用条件性标量 pole width；其二是 Xe-131 固定速度微分截面曲线，使用 GCN/JJ55 响应、\(v=776\) km/s、\(M_A=131u\) 和 zero-width prescription。两者的输入与物理层级不同，均不替代天然氙 halo fold 或 LZ detector-level likelihood。

| 研究层级 | 当前归档结果 | 明确边界 |
|---|---|---|
| AFH Xe-131 核响应 | 2401 个 \(q\) 节点；60 位精度 mpmath 与 Wolfram 14.0.0 原生逐点对照均通过，最大相对差异 \(3.59\times10^{-9}\) | 仅验证 Xe-131 AFH response-level；不代表完整天然氙连续谱或 LZ likelihood |
| AFH 天然氙速率 | 七种可用同位素的 selected-point halo fold | Xe-124/Xe-126 缺少当前 AFH default density matrix；尚无完整 AFH 连续谱 |
| GCN/JJ55 天然氙谱 | 四组 benchmark 的连续反冲谱，覆盖当前可用七种同位素 | 是独立核模型对照，不代表 LZ 合作组使用的修改后 WimPyDD 核输入 |
| 450 keV supplied benchmark | 单点 \(\mathcal L_{00}\)/\(I_6\) 本地验收；另有 105 点 Xe-131 fixed-speed curve | 不是天然氙 halo rate；curve 使用 \(M_A=131u\)、zero width，且未积分两端开放区间 |
| LZ rate-level interface | Fig. S2 一维效率曲线与 2.84 tonne-year exposure 折叠，得到 GCN/JJ55 预期事件数 | 未构造二维 \(S1_c\)–\(\log_{10}S2_c\) PDF、完整 nuisance/background likelihood 或实验排除 |


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

### 1.1 相互作用结构：为什么末态会多出一个标量？

当前 Eq. (6) 数值主线对应论文中的 vector–vector 交换与 scalar emission 结构。相关相互作用可写为
\[
\mathcal L_{\rm int}\supset
\left(
g_1 V_\mu\bar\chi_2\gamma^\mu\chi_1
+g_2s\bar\chi_2\chi_1
+\mathrm{h.c.}
\right)
+g_{Vq}V_\mu\sum_q\bar q\gamma^\mu q
\]
这里 \(V_\mu\) 是连接暗物质与核子的矢量媒介子，\(s\) 是末态标量，\(\chi_1,\chi_2\) 是两个不同质量的暗扇区费米子。对于普适的夸克矢量耦合，在低能核子匹配中，核子矢量电荷给出
\[
g_{VN}=3g_{Vq},
\]
其中因子 3 来自核子中三个价夸克的矢量数荷；这条夸克—核子匹配关系与 AFH isoscalar response 的归一化因子 4 是两件不同的事。

需要注意，这组相互作用在暗费米子空间中是非对角的：顶点连接 \(\chi_1\) 与 \(\chi_2\)，而不是直接给出 \(\chi_1\chi_1V\) 或 \(\chi_1\chi_1s\) 顶点。因此，入射的 \(\chi_1\) 通过矢量交换与核靶发生作用，同时在暗费米子线上辐射出 \(s\)，最后又回到 \(\chi_1\)。这解释了为什么末态是
\[
\chi_1+A\longrightarrow\chi_1+A+s,
\]
而不是简单的 \(\chi_1+A\to\chi_2+A\)。

论文源文件还列出了 scalar–pseudoscalar 的另一种相互作用结构。本文 Eq. (6)、当前 Dirac kernel 和以下核响应讨论针对上面的 vector–vector 基准；不能把另一种模型的顶点或耦合约定混入这条数值计算链。

相互作用的原始写法见论文工作稿 [paper-source/main.tex](../../paper-source/main.tex) 的 Model 一节；本段只解释当前采用的 vector–vector 计算分支。

### 1.2 为什么 \(\chi_2\) 是虚中间态，而不是末态粒子？

定义
\[
m_{\chi_2}=m_{\chi_1}+\Delta m.
\]
\(\chi_2\) 出现在内部费米子传播子中。它不是本过程的外部末态粒子；最终暗物质仍然是 \(\chi_1\)。因此，\(\Delta m\) 首先决定的是内部传播子的极点位置，而不是末态两体阈值。

尤其是标量发射发生在矢量交换之后的图，其内部动量为
\[
K=p'+k=p-q,\qquad K^2=W^2,
\]
相应传播子分母包含
\[
W^2-m_{\chi_2}^2+i m_{\chi_2}\Gamma_{\chi_2}.
\]
若某个允许的运动学点达到 \(W^2=m_{\chi_2}^2\)，内部 \(\chi_2\) 就可能到达质量壳，振幅会出现极点增强，并需要认真处理真实中间态产生、窄宽度极限以及相应的双重计数问题。

本文采用的参数筛选要求在整个可达 halo 速度和反冲能量范围内
\[
\boxed{W_{\max}(v,E_R)<m_{\chi_2}.}
\]
因为任何允许的 \(W\) 都不超过 \(W_{\max}\)，这个条件保证第二张图中的 \(\chi_2\) 仍然是虚态。它是参数空间筛选条件，不是程序对任意输入自动成立的恒等式。

第一张图的内部动量为 \(p-k\)。对于未来指向的壳上四动量，有 \(p\cdot k\ge m_{\chi_1}m_s\)，从而
\[
(p-k)^2=m_{\chi_1}^2+m_s^2-2p\cdot k
\le(m_{\chi_1}-m_s)^2<m_{\chi_2}^2.
\]
所以在本文的质量排序下，第一张图不会到达 \(\chi_2\) 极点；需要考虑极点宽度的是第二张图。

这也解释了两个质量参数的不同作用：

- \(m_s\) 是真实末态粒子的质量，直接决定末态相空间是否开放；
- \(\Delta m\) 决定虚态 \(\chi_2\) 的质量，控制传播子离极点有多远，并通过所采用的宽度处方影响振幅。

若采用 \(\Gamma_{\chi_2}\)，必须明确它来自什么衰变道。本文当前使用的 \(\chi_2\to\chi_1s\) 宽度仅在 Dirac 费米子、实标量、纯 scalar off-diagonal Yukawa 耦合且该道是唯一开放道的假设下成立；它不是完整模型的通用自能。

### 1.3 核反冲的两个动量变量：空间动量与四动量不变量

在靶核静止系，令
\[
P^\mu=(m_A,\mathbf 0),\qquad
P'^\mu=(m_A+E_R,\mathbf q),
\]
并定义核反冲四动量
\[
q^\mu=P'^\mu-P^\mu=(E_R,\mathbf q).
\]
初末核都在质量壳上，故
\[
(P+q)^2=P^2
\quad\Longrightarrow\quad
q_\mu q^\mu=-2m_AE_R.
\]
因此传播子所使用的 Mandelstam 不变量是
\[
t=q_\mu q^\mu=-2m_AE_R.
\]
而核响应所使用的是空间动量模长
\[
\boxed{Q\equiv|\mathbf q|
=\sqrt{2m_AE_R+E_R^2}.}
\]
两者满足 \(Q^2=E_R^2-t\)，并不相等。于是矢量传播子平方给出
\[
\frac{1}{(m_V^2-t)^2}
=\frac{1}{(m_V^2+2m_AE_R)^2},
\]
AFH 核响应则通过
\[
y=\left(\frac{Qb_A}{2}\right)^2
\]
依赖空间动量 \(Q\)。

在 \(E_R\ll m_A\) 时，才可以近似 \(Q\simeq\sqrt{2m_AE_R}\)。本文默认使用精确的空间动量关系；不能把传播子中的 \(-t\) 直接代入 AFH 的 \(q\)，也不能把空间 \(Q^2\) 误写成四动量不变量 \(t\)。完整质量壳推导和 NR 近似比较见附录 G。

### 1.4 暗物质的速度能量尺度

虽然 \(m_{\chi_1}=1\) TeV 很大，但银河系暗物质速度远小于光速，其入射动能只有 MeV 或亚 MeV 量级：
\[
T_{\chi_1}\simeq\frac12m_{\chi_1}\left(\frac vc\right)^2.
\]
例如
\[
T_{\chi_1}\simeq
0.269\ {\rm MeV}
\left(\frac{m_{\chi_1}}{1\ {\rm TeV}}\right)
\left(\frac{v}{220\ {\rm km/s}}\right)^2,
\]
而在截断 SHM 的最大实验室速度 \(776\ {\rm km/s}\) 处，
\[
T_{\chi_1}\simeq
3.35\ {\rm MeV}
\left(\frac{m_{\chi_1}}{1\ {\rm TeV}}\right).
\]
这给出了为什么 sub-MeV 标量质量值得研究的直观能量尺度：在高速尾部，入射暗物质的动能有可能支持标量辐射和核反冲同时发生。不过，这部分动能还要在末态暗物质、标量和核反冲之间分配，不能把 \(T_{\chi_1}\) 直接等同于标量可获得的能量。

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
\sqrt{\lambda_{\rm dim}(W^2,m_{\chi_1}^2,m_s^2)}
\int_{-1}^{1} dz\,
\left\langle\mathcal L_{00}\right\rangle_{\phi_*}.
\]

> **公式追溯：** Eq. (6) 与 \(I_6\) 的完整相空间和前因子推导见[附录 A，§A.3–A.4.2](appendices/09A_three_body_kinematics_amplitude.md)；正文逐项推导见§2.5.1–2.5.8；对应程序为 [eq6_kernel.py](../figure2_full_reproduction/eq6_kernel.py)。全部公式—符号—程序—结果映射见[交叉引用索引 F3–F5](formula_symbol_code_cross_reference.md)。

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
- \(\lambda_{\rm dim}\)：无量纲 Källén 函数，定义为 \(\lambda_K(W^2,m_{\chi_1}^2,m_s^2)/W^4\)，见附录 A.3。

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

### 2.3 从相互作用顶点到两张辐射图的振幅

在靶核静止系，矢量核电荷流的 leading non-relativistic 分量是时间分量。把核结构因子从核子耦合中提出后，振幅的结构可以写成
\[
\mathcal M_A\ \propto\
\frac{g_1g_2g_{VN}}{m_V^2+2m_AE_R}
\,\mathcal J_{A,\mu}(q)\,
\bar u(p')\Gamma^\mu u(p),
\]
其中 \(\mathcal J_A^\mu\) 表示已剥离单核子耦合的核电流矩阵元，\(\Gamma^\mu\) 是暗费米子线上的辐射顶点结构。两张树图分别为
\[
\Gamma^\mu=\Gamma^\mu_{\rm before}+\Gamma^\mu_{\rm after},
\]
\[
\Gamma^\mu_{\rm before}
=\frac{\gamma^\mu(\slashed p-\slashed k+m_{\chi_2})}
{(p-k)^2-m_{\chi_2}^2},
\qquad
\Gamma^\mu_{\rm after}
=\frac{(\slashed p'+\slashed k+m_{\chi_2})\gamma^\mu}
{W^2-m_{\chi_2}^2+i m_{\chi_2}\Gamma_{\chi_2}}.
\]
before/after 指标量 \(s\) 相对于矢量交换发生在暗费米子线上的先后次序，不是两个不同的末态过程。

在核靶非相对论极限，核的空间电流相对时间分量受到核速度或 \(|\mathbf q|/m_A\) 抑制，因此当前相干电荷近似保留 \(\Gamma^0\) 对应的粒子侧张量：
\[
\mathcal L_{00}
=\frac12\sum_{s,s'}
\left|\bar u_{s'}(p')\Gamma^0u_s(p)\right|^2.
\]
对 Dirac 外部态使用自旋完备关系，可得到
\[
\boxed{
\mathcal L_{00}
=\frac12\operatorname{Tr}
\left[
(\slashed p'+m_{\chi_1})\Gamma^0
(\slashed p+m_{\chi_1})\overline\Gamma^{\,0}
\right],
\qquad
\overline\Gamma^{\,0}=\gamma^0(\Gamma^0)^\dagger\gamma^0.
}
\]

令 \(\mathcal M_b\) 和 \(\mathcal M_a\) 分别表示 before 与 after 两张图，则
\[
|\mathcal M_b+\mathcal M_a|^2
=|\mathcal M_b|^2+|\mathcal M_a|^2
+2\,\mathrm{Re}(\mathcal M_b\mathcal M_a^*).
\]
最后一项就是干涉项。它可以为正，也可以为负；但完整自旋求和后的 \(\mathcal L_{00}\) 必须非负。若把两张图的平方直接相加而不保留交叉项，就不再是原拉格朗日量所定义的完整树级振幅。本文程序将两张图先相加，再计算 Dirac trace；附录 A.5 给出迹表达式和实现检查。

### 2.4 为什么积分变量是 \((W^2,z,\phi_*)\)？

三体末态的相空间可以按子系统不变质量分解：
\[
d\Phi_3(p+P;P',p',k)
=\frac{dW^2}{2\pi}
\,d\Phi_2(p+P;P',K)\,
d\Phi_2(K;p',k).
\]
第一段描述入射暗物质与核靶产生反冲核 \(P'\) 和子系统 \(K\)；第二段描述 \(K\) 再分解为 \(\chi_1+s\)。这样，三体问题被拆成一个不变质量积分和一个子系统两体角积分。

在 \(K\) 静止系中，
\[
|\mathbf k_*|
=\frac{\sqrt{\lambda_K(W^2,m_{\chi_1}^2,m_s^2)}}{2W}
=\frac W2\sqrt{\lambda_{\rm dim}},
\]
其中
\[
\lambda_{\rm dim}
=\left[1-\frac{(m_{\chi_1}+m_s)^2}{W^2}\right]
\left[1-\frac{(m_{\chi_1}-m_s)^2}{W^2}\right].
\]
因此 \(\sqrt{\lambda_{\rm dim}}\) 正比于子系统静止系中的末态三动量；当 \(W=m_{\chi_1}+m_s\) 时，末态两粒子相对动量降为零，二体相空间关闭。

固定 \(E_R\) 和入射速度后，核反冲方向与 \(W^2\) 一一对应：
\[
W^2=m_{\chi_1}^2+2p_{\chi_1}Q\cos\theta_q
-2(E_{\chi_1}+m_A)E_R,
\]
\[
\frac{dW^2}{d\cos\theta_q}=2p_{\chi_1}Q.
\]
而 \(z=\cos\theta_*\) 和 \(\phi_*\) 描述标量在 \(K\) 静止系中的发射方向。它们不是靶核静止系中 \(\mathbf p\) 与 \(\mathbf q\) 的夹角；后者记为 \(\theta_q\)。

由此得到
\[
W_{\min}^2=(m_{\chi_1}+m_s)^2,
\]
\[
W_{\max}^2=
m_{\chi_1}^2+2p_{\chi_1}Q
-2(E_{\chi_1}+m_A)E_R.
\]
\(W_{\max}\) 对应 \(\cos\theta_q=1\)，即固定反冲能量时允许的最大子系统不变质量。积分开放条件为
\[
\boxed{W_{\max}^2\ge W_{\min}^2.}
\]
等价地，在给定 \(v,E_R\) 时允许的标量质量满足
\[
m_s\le W_{\max}(v,E_R)-m_{\chi_1}.
\]
若进一步对 \(E_R\) 最大化，得到的是该入射速度下的标量质量运动学上限；使这个上限达到最大值的 \(E_R\)，只是最有利于保留 \(\chi_1+s\) 子系统不变质量的反冲点，并不意味着该点的散射概率或探测器事件数最大。

对给定入射速度，最大允许标量质量可通过对 \(W_{\max}(E_R)\) 关于反冲能量最大化得到。定义
\[
s_{\rm tot}=(p+P)^2=m_{\chi_1}^2+m_A^2+2m_AE_\chi,
\qquad B=E_\chi+m_A.
\]
由
\[
\frac{dW_{\max}^2}{dE_R}
=2p_{\chi_1}\frac{m_A+E_R}{Q}-2B=0
\]
得到最有利的反冲点
\[
\boxed{
E_R^*
=m_A\left(\frac{E_\chi+m_A}{\sqrt{s_{\rm tot}}}-1\right).
}
\]
在该点
\[
W_{\max}(E_R^*)=\sqrt{s_{\rm tot}}-m_A,
\qquad
\boxed{
m_{s,\max}=\sqrt{s_{\rm tot}}-m_A-m_{\chi_1}.
}
\]
这里的 \(E_R^*\) 是使运动学允许的 \(m_s\) 上限最大的反冲能量，不是使 \(d\sigma/dE_R\) 或探测器事件率最大的能量。完整求导和代数化简见附录 A.2。


所以 \(I_6\) 不只是一个可随意提高精度的数值积分：它的积分区间本身编码了三体过程能否发生。靠近阈值时，区间缩短，同时 \(\sqrt{\lambda_{\rm dim}}\) 也趋于零，二者共同压低积分。

\[
I_6=
\int_{W_{\min}^2}^{W_{\max}^2}dW^2
\sqrt{\lambda_{\rm dim}}
\int_{-1}^{1}dz\,
\langle\mathcal L_{00}\rangle_{\phi_*}.
\]
由于 \(\lambda_{\rm dim}\) 与 \(\mathcal L_{00}\) 无量纲，而 \(dW^2\) 带有 GeV\(^2\)，故
\[
[I_6]={\rm GeV}^2.
\]
方位角平均定义为
\[
\langle\mathcal L_{00}\rangle_{\phi_*}
=\frac{1}{2\pi}\int_0^{2\pi}d\phi_*\,\mathcal L_{00};
\]
若程序已经执行这一平均，就不能再额外乘入一次 \(2\pi\)。

### 2.5 Eq. (6) 整体前因子的 Lorentz-invariant 独立推导

本节在正文中独立重建 Eq. (6) 的整体归一化。目的不是从现有数值程序反推常数，而是从单粒子 Lorentz-invariant 测度出发，逐项核对两个两体子过程、变量 Jacobian、方位角约定、不变通量和核电荷流。详细的扩展审计另见[附录 A.4.2](appendices/09A_three_body_kinematics_amplitude.md)。

#### 2.5.1 不变相空间约定与三体分解

采用自然单位制和单粒子不变测度
\[
d\Pi_i=\frac{d^3\mathbf p_i}{(2\pi)^3\,2E_i},
\]
两体相空间定义为
\[
d\Phi_2(Q;a,b)
=(2\pi)^4\delta^{(4)}(Q-p_a-p_b)d\Pi_a d\Pi_b.
\]
在母系统静止系，令 \(M=\sqrt{Q^2}\)。先积分三维动量 delta 函数，再利用能量 delta 函数，可得
\[
d\Phi_2
=\frac{p_*^2dp_*\,d\Omega_*}{16\pi^2E_aE_b}
\delta(M-E_a-E_b).
\]
因为
\[
\frac{d(E_a+E_b)}{dp_*}
=\frac{p_*M}{E_aE_b},
\]
径向动量积分给出标准结果
\[
\boxed{
d\Phi_2(Q;a,b)
=\frac{p_*}{16\pi^2M}d\Omega_*
=\frac{\sqrt{\lambda_K(M^2,m_a^2,m_b^2)}}{32\pi^2M^2}d\Omega_*.
}
\]
这里
\[
\lambda_K(x,y,z)=x^2+y^2+z^2-2xy-2xz-2yz
\]
为有量纲 Källén 函数。末态 \(\chi_1\) 与 \(s\) 是不同粒子，因此三体相空间没有额外的 \(1/2!\) 对称因子。

定义
\[
q=P'-P,\qquad K=p-q=p'+k,\qquad W^2=K^2,
\]
其中 \(p,P\) 是入射暗物质和靶核四动量，\(P'\) 是末态核四动量，\(p',k\) 分别是末态暗物质和标量四动量。插入中间子系统的不变质量后，
\[
\boxed{
d\Phi_3(p+P;P',p',k)
=\frac{dW^2}{2\pi}
d\Phi_2(p+P;P',K)d\Phi_2(K;p',k).
}
\]
这里的积分变量是 \(W^2\)，故分解中不产生额外的 \(2W\)；只有改用 \(W\) 作为积分变量时才需使用 \(dW^2=2W\,dW\)。

#### 2.5.2 第一段两体相空间与 \(t\leftrightarrow E_R\) Jacobian

令
\[
s_{\rm tot}=(p+P)^2,\qquad
\Lambda_{\rm in}
=\sqrt{\lambda_K(s_{\rm tot},m_{\chi_1}^2,m_A^2)}.
\]
在初态质心系中，初态和末态相对动量大小分别为
\[
p_i^*=\frac{\Lambda_{\rm in}}{2\sqrt{s_{\rm tot}}},
\qquad
p_f^*=\frac{\sqrt{\lambda_K(s_{\rm tot},m_A^2,W^2)}}{2\sqrt{s_{\rm tot}}}.
\]
对第一段过程 \(p+P\to P'+K\)，
\[
d\Phi_2
=\frac{p_f^*}{16\pi^2\sqrt{s_{\rm tot}}}
d\cos\theta\,d\phi_q.
\]
由
\[
t=q^2=(P'-P)^2,\qquad
\left|\frac{dt}{d\cos\theta}\right|=2p_i^*p_f^*
\]
可得
\[
\frac{d\Phi_2}{dt\,d\phi_q}
=\frac{1}{32\pi^2\sqrt{s_{\rm tot}}p_i^*}
=\frac{1}{16\pi^2\Lambda_{\rm in}}.
\]
在未极化靶核、相干且只保留核电荷时间分量 \(J_A^0\) 的近似下，体系绕入射轴具有旋转对称性，可以积分掉核反冲方位角 \(\phi_q\)：
\[
\boxed{
\frac{d\Phi_2}{dt}
=\int_0^{2\pi}d\phi_q\,
\frac{d\Phi_2}{dt\,d\phi_q}
=\frac{1}{8\pi\Lambda_{\rm in}}.
}
\]
靶核静止系中
\[
t=q^2=-2m_AE_R,\qquad
\left|\frac{dt}{dE_R}\right|=2m_A,
\qquad
\Lambda_{\rm in}=2m_Ap_{\chi_1}.
\]
因此
\[
\boxed{
\frac{d\Phi_2(p+P;P',K)}{dE_R}
=\frac{2m_A}{8\pi\Lambda_{\rm in}}
=\frac{1}{8\pi p_{\chi_1}}.
}
\]
这里的 \(\phi_q\) 是第一段核反冲方位角；它与下文第二段子系统中的 \(\phi_*\) 不是同一个角变量。

#### 2.5.3 第二段两体相空间与 \((z,\phi_*)\) 变量

在 \(K\) 静止系，令 \(W=\sqrt{W^2}\)。末态相对动量为
\[
|\mathbf k_*|
=\frac{\sqrt{\lambda_K(W^2,m_{\chi_1}^2,m_s^2)}}{2W}.
\]
取
\[
z=\cos\theta_*,\qquad d\Omega_*=dz\,d\phi_*,
\]
并定义无量纲 Källén 函数
\[
\lambda_{\rm dim}(W^2,m_{\chi_1}^2,m_s^2)
=\frac{\lambda_K(W^2,m_{\chi_1}^2,m_s^2)}{W^4}.
\]
于是
\[
\boxed{
d\Phi_2(K;p',k)
=\frac{\sqrt{\lambda_{\rm dim}}}{32\pi^2}
dz\,d\phi_*.
}
\]
由于使用 \(z=\cos\theta_*\)，角测度已经是 \(dz\,d\phi_*\)，不应再额外乘入 \(\sin\theta_*\)。

#### 2.5.4 合并三体相空间：\(512\pi^4\) 的来源

将前两段相空间代入三体分解，得到尚未对 \(\phi_*\) 积分的测度：
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
因此，未积分方位角时的系数是 \(1/(512\pi^4p_{\chi_1})\)，而不是 \(1/(256\pi^3p_{\chi_1})\)。后者对应的是对 \(\phi_*\) 完成平均之后的约定。

#### 2.5.5 方位角积分改写为平均：\(512\pi^4\to256\pi^3\)

本文定义
\[
\left\langle\mathcal L_{00}\right\rangle_{\phi_*}
=\frac{1}{2\pi}\int_0^{2\pi}d\phi_*\,
\mathcal L_{00}.
\]
所以
\[
\int_0^{2\pi}d\phi_*\,\mathcal L_{00}
=2\pi\left\langle\mathcal L_{00}\right\rangle_{\phi_*}.
\]
将它代入上一节的未积分相空间，得到
\[
\boxed{
\frac{\sqrt{\lambda_{\rm dim}}}{512\pi^4p_{\chi_1}}
\int_0^{2\pi}d\phi_*\,\mathcal L_{00}
=
\frac{\sqrt{\lambda_{\rm dim}}}{256\pi^3p_{\chi_1}}
\left\langle\mathcal L_{00}\right\rangle_{\phi_*}.
}
\]
因此，从 \(512\pi^4\) 到 \(256\pi^3\) 的变化只来自将未归一化的方位角积分写成 \(1/(2\pi)\) 平均；不能在采用平均定义后再次额外乘 \(2\pi\)。

#### 2.5.6 不变通量、核电荷流与 Eq. (6)

不变通量因子为
\[
F=4\sqrt{(p\cdot P)^2-m_{\chi_1}^2m_A^2}
=4m_Ap_{\chi_1}
\]
（最后一个等号使用靶核静止系）。在本研究的 leading non-relativistic 核电荷近似下，
\[
J_A^0\simeq2m_A.
\]
因此，在当前核响应定义下，振幅平方写成
\[
|\mathcal M|^2
=
\frac{
4m_A^2(g_1g_2g_{VN})^2R_A(E_R)
}{
(m_V^2-t)^2
}\mathcal L_{00}
=
\frac{
4m_A^2(g_1g_2g_{VN})^2R_A(E_R)
}{
(m_V^2+2m_AE_R)^2
}\mathcal L_{00}.
\]
这里 \(\mathcal L_{00}\) 已包含暗物质初态自旋平均和末态自旋求和；核态的自旋处理则包含在 \(R_A\) 的定义中。故不应再对同一自由度重复添加平均因子。

将振幅平方、通量 \(1/F\) 和方位角平均后的相空间系数合并：
\[
\frac{4m_A^2}{4m_Ap_{\chi_1}}
\frac{1}{256\pi^3p_{\chi_1}}
=
\boxed{
\frac{m_A}{256\pi^3p_{\chi_1}^2}.
}
\]
最终得到正文 Eq. (6)：
\[
\boxed{
\frac{d\sigma_A}{dE_R}
=
\frac{
m_A(g_1g_2g_{VN})^2R_A(E_R)
}{
256\pi^3p_{\chi_1}^2(m_V^2+2m_AE_R)^2
}
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

#### 2.5.7 与数值实现的约定对照

| 理论量 | 本文约定 | Python 实现/后续 Mathematica 约定 |
|---|---|---|
| 无量纲 Källén 函数 | \(\lambda_K/W^4\) | \(\texttt{lambda\_dimensionless}\)，不得再乘或除 \(W^2\) |
| \(W^2\) 积分 | \(dW^2\) | \(\texttt{wvals}\)、\(\texttt{wweights}\) |
| 极角积分 | \(\int_{-1}^{1}dz\) | \(\texttt{xz}\)、\(\texttt{wz}\)，权重和为 2 |
| 方位角处理 | \((2\pi)^{-1}\int_0^{2\pi}d\phi_*\) | \(\texttt{phis}\)、\(\texttt{phiweights=0.5*wp}\)，权重和为 1 |
| 自旋约定 | \(\frac12\sum_{s_i,s_f}\) | \(\texttt{spin\_trace}\) 中初态平均 \(\texttt{/2}\) |
| 三体积分 | \(I_6\) | \(\texttt{reduced\_kernel}\)，不包含 Eq. (6) 外部的 \(256\pi^3\) |
| 截面前因子 | \(m_A/(256\pi^3p_{\chi_1}^2)\) | \(\texttt{joint\_xe131.py}\) 的 \(\texttt{C\_A}\) |

对 Gauss–Legendre 方位角节点 \(x_i\in[-1,1]\)，变量映射
\[
\phi_i=\pi(x_i+1),\qquad d\phi_*=\pi\,dx
\]
给出
\[
\frac{1}{2\pi}\int_0^{2\pi}f(\phi_*)d\phi_*
=\frac12\int_{-1}^{1}f(\pi(x+1))dx
\simeq\sum_i\frac{w_i}{2}f(\phi_i).
\]
所以程序中的 \(0.5\,w_i\) 是平均权重，权重和为 1；若在 Mathematica 中改用未归一化的 \(\phi_*\) 积分，则相应地必须把截面前因子改写为 \(m_A/(512\pi^4p_{\chi_1}^2)\)，二者不能混搭。

作为交叉检查，若定义未归一化积分
\[
I_6^{\rm raw}
=\int dW^2\sqrt{\lambda_{\rm dim}}
\int_{-1}^{1}dz\int_0^{2\pi}d\phi_*\,
\mathcal L_{00},
\]
则 \(I_6^{\rm raw}=2\pi I_6\)，并且
\[
\frac{m_A}{512\pi^4p_{\chi_1}^2}I_6^{\rm raw}
=
\frac{m_A}{256\pi^3p_{\chi_1}^2}I_6.
\]
这是同一物理截面的两种等价积分约定。

#### 2.5.8 维度、适用范围与 AFH 因子 4 的区分

\[
[I_6]={\rm GeV}^2,\qquad
\left[\frac{d\sigma_A}{dE_R}\right]={\rm GeV}^{-3},
\]
与自然单位下的微分截面维度一致。上述 \(256\pi^3\) 结论适用于未极化靶核、相干散射、只保留 \(J_A^0\simeq2m_A\) 的近似，并采用本文对暗物质自旋迹和核响应的定义。若保留靶极化、横向核流或非平凡的核反冲方位角依赖，必须重新保留相应角变量，不能直接沿用已经积分掉 \(\phi_q\) 的表达式。

最后，必须区分两个彼此独立的归一化问题：
\[
\underbrace{256\pi^3}_{\text{三体相空间、角平均与不变通量}}
\qquad\text{和}\qquad
\underbrace{4}_{\text{AFH 响应从包定义到物理等核子耦合的转换}}.
\]
AFH 的因子 4 不参与上述相空间推导，也不能用来补偿或修改 \(256\pi^3\)。本节解析推导确认了 Eq. (6) 与当前 Python 积分约定的一致性；完整连续反冲网格上的 \(I_6\) 数值收敛仍按第 8 节单独验收。

### 2.6 参数分别控制归一化、阈值还是谱形？

| 参数或输入 | 主要进入的位置 | 物理作用 |
|---|---|---|
| \(m_s\) | \(W_{\min}=m_{\chi_1}+m_s\)、\(v_{\min}\)、\(I_6\) | 增大末态质量门槛，压缩三体相空间并提高最小入射速度 |
| \(\Delta m\) | \(m_{\chi_2}=m_{\chi_1}+\Delta m\)、传播子分母和宽度 | 改变虚中间态离极点的距离；在 \(\chi_2\) 不外显的前提下，不直接改变末态 \(\chi_1+s\) 的阈值 |
| \(m_V\) | \((m_V^2+2m_AE_R)^{-2}\) | 控制矢量交换强度及其反冲能量依赖 |
| \(g_1,g_2,g_{VN}\) | 振幅整体因子和 \(\Gamma_{\chi_2}\) | 耦合乘积控制主要归一化，但 \(g_2\) 还单独进入条件性 pole width |
| \(m_{\chi_1}\) | \(p_{\chi_1}\)、\(W_{\max}\)、\(v_{\min}\)、传播子 | 决定入射动能尺度和整个三体运动学 |
| 核模型与 \(b_A\) | \(R_A(E_R)\) | 决定核相干响应的有限动量形状和极小值 |
| halo 参数 | \(f_{\rm lab}(v)\)、\(v_{\max}\) | 决定哪些速度能贡献以及高速度尾部的权重 |


在当前 \(m_V=10\) GeV benchmark 中，\(m_V^2=100\ {\rm GeV}^2\)，而 Xe 核在 \(E_R=0.2\)–\(0.8\) MeV 时的 \(2m_AE_R\) 只有约 \(0.05\)–\(0.20\ {\rm GeV}^2\)。因此该 benchmark 处于重媒介子近似 \(m_V^2\gg |t|\) 的区域，传播子因子在所考察反冲窗口内变化很小，主要给出近似整体归一化 \(\propto m_V^{-4}\)。这时谱形的显著结构主要来自核响应 \(R_A\) 与三体积分 \(I_6\)，而不是矢量传播子的快速反冲依赖。若研究更轻的 \(m_V\)，这一判断必须重新评估。

特别要避免把耦合乘积 \((g_1g_2g_{VN})^2\) 当成足以确定所有传播子效应的参数：若改变 \(g_2\) 而同时调整其他耦合以保持该乘积不变，条件性 \(\Gamma_{\chi_2}\propto |g_2|^2\) 仍会改变。因此，比较不同耦合点时必须同时报告 \(g_2\) 和宽度处方。

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

> **公式追溯：** AFH default \(b_A\) 处方、fm 到 GeV\(^{-1}\) 的转换和 \(y\) 的定义见[附录 B，§B.2](appendices/09B_afh_v6_density_matrix_response.md)；公式与数值输入映射见[索引 F6](formula_symbol_code_cross_reference.md)。

Xe-128 至 Xe-136 这组可用同位素的处方值约为 \(2.284596\)–\(2.304942\) fm。GCN/JJ55 的同核素比较使用相同的 \(b_A\) 处方。

**重要决策：不把 \(b_A\) 当作任意拟合参数，也不通过调节 \(b_A\) 去匹配 Figure 2 的谷值。** 这样可以避免把核模型输入的人为调参误认为独立的物理验证。

来源和数据完整性信息：

- AFH 原始压缩包 SHA-256：`4e0f70e6e780f3f4a40faa14792cae239d1989cf15d1e211b4fd7389b0460727`；
- Mathematica 源文件：`v6/dmformfactor-V6.m`；
- 源文件 SHA-256：`dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372`。

### 3.2 AFH isoscalar response 的因子 4

这是本轮最重要的归一化问题之一。

AFH v6.0 的原始 isoscalar response 并不直接等于以物理单核子耦合 \(g_{VN}\) 定义的等质子、等中子相干响应。标准 isospin 基底中的系数定义为

\[
c_{\rm std}^{0}=\frac{c^p+c^n}{2},
\qquad
c_{\rm std}^{1}=\frac{c^p-c^n}{2}.
\]

AFH 分发版 Mathematica setter 的接口输入是另一个量 \(c_{\rm set}\)，其内部映射见附录 C.1；不能把 setter 输入与标准 isospin 系数混为同一个符号。

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

在 AFH 接口的系数约定下，物理单核子耦合对应的 isoscalar 输入系数为 \(c_{\rm set}=2g_{VN}\)，所以振幅平方带来因子 4。这里的 \(c_{\rm set}\) 是 AFH setter 输入，不是标准基底中的 \(c_{\rm std}^{0}=g_{VN}\)；两者定义不同。若截面前因子仍写成物理的 \(g_{VN}\)，就必须把这一个因子 4 放入核响应定义中。

对于原始 AFH v6.0 输出，物理响应的解析映射写作

\[
R_A^{\rm phys}(E_R)
=
\frac{16\pi}{2J_A+1}
W_{M,\mathrm{AFH}}^{00}(y).
\]

> **公式追溯：** \(b_A\)、\(y\) 和 AFH 密度矩阵有限和见[附录 B，§B.2–B.4](appendices/09B_afh_v6_density_matrix_response.md)；raw-to-physical response 映射及因子 4 见[附录 C](appendices/09C_afh_isoscalar_factor4_normalization.md)；空间动量约定见[附录 G](appendices/09G_recoil_momentum_convention_audit.md)。对应程序和 2401 点输出见[索引 F6](formula_symbol_code_cross_reference.md)。

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

### 3.5 AFH 响应极小值的物理意义：核相干与衍射结构

矢量媒介子在当前近似下耦合到核的相干矢量电荷。直观地说，有限空间动量 \(Q\) 下，核内不同位置的核子带有不同的 Fourier 相位 \(e^{i\mathbf q\cdot\mathbf r_i}\)，总核振幅是这些贡献的相干和：
\[
\mathcal A_A(\mathbf q)\sim
\sum_{i=1}^{A}g_{Vi}e^{i\mathbf q\cdot\mathbf r_i}.
\]
在 \(Q\to0\) 时，各核子的相位趋于一致。若 \(g_p=g_n=g_{VN}\)，核振幅正比于
\[
Zg_p+(A-Z)g_n=Ag_{VN},
\]
所以物理相干响应满足 \(R_A^{\rm phys}(0)=A^2\)。这就是零动量处的 \(A^2\) 相干增强。

当 \(Q\) 增大到能够分辨核的有限空间分布时，不同轨道和不同径向区域的贡献不再同相。它们在振幅求和中可以相互抵消，导致响应出现很深的局部极小值。这种结构可以类比有限尺寸电荷分布的 form-factor diffraction minima，但 AFH 的实际计算还包含壳模型轨道、角动量耦合和密度矩阵，不能简单替换成一个均匀球体的解析 form factor。

对 Xe-131，AFH v6.0 的弹性 \(M\) 响应可写成
\[
W_{M,\rm AFH}^{00}(y)
=\frac14\left[\mathcal A_0(y)^2+\mathcal A_2(y)^2\right].
\]
与正文采用的物理等质子、等中子耦合归一化相对应，
\[
R_A^{\rm phys}(Q)
=\frac{16\pi}{2J_A+1}W_{M,\rm AFH}^{00}(y),
\qquad y=\left(\frac{Qb_A}{2}\right)^2.
\]
其中 \(\mathcal A_J\) 是给定多极 \(J\) 下对密度矩阵条目、角矩阵元和径向矩阵元的相干求和。当前 Xe-131 计算保留 \(J=0,2\)。因此：
- 每个 \(\mathcal A_J\) 内部的轨道与密度矩阵贡献可以发生相消；
- \(J=0\) 与 \(J=2\) 的响应强度在这里以平方和相加，不能把不同 \(J\) 通道之间描述成同一个振幅的相干抵消；
- 总响应非负，极小值表示核相干振幅受到强抑制，不表示核靶不存在或散射严格禁止；它也不是暗费米子传播子的 \(\chi_2\) 共振，更不是三体相空间关闭的运动学阈值。

空间动量极小值与反冲能量的精确换算为
\[
E_R(Q)=\sqrt{m_A^2+Q^2}-m_A.
\]
因此表中的 \(q_{\min}\) 和 \(E_{R,\min}\) 是同一个核响应结构的两种标记。改变 \(b_A\) 会改变 \(y=(Qb_A/2)^2\) 的映射，并系统移动响应结构；这就是不能为了匹配 Figure 2 的谷值而拟合 \(b_A\) 的物理原因。

最后，**核响应的极小值不必然等于完整截面或 halo-folded 事件率的极小值**。固定速度截面还乘有 \(I_6(v,E_R)\) 和矢量传播子；天然氙速率还对同位素与速度求和/积分。不同同位素的极小值位置不完全相同，速度积分也会对不同反冲点施加不同阈值权重。因此，必须分别讨论 \(R_A\)、\(d\sigma_A/dE_R\) 和 \(dR/dE_R\) 的谱形。

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

### 4.1 核模型对照应如何作物理解读？

在相同同位素、相同 \(E_R\)、相同入射速度和相同粒子物理输入下，AFH、GCN、JJ55 的差异只通过各自的 \(R_A(E_R)\) 进入 Eq. (6)。因此同一运动学点上的截面比可以直接用响应比解释。表中三个主要极小值的位置在不同核模型间相对接近，这提示这些结构与 Xe 核有限尺寸及主要壳结构的动量尺度有关；但极小值深度差异明显，说明核波函数和密度矩阵对相消程度十分敏感。

这类差异不应被压缩成一个常数“核模型误差条”：响应模型可能同时改变极小值的深度、位置和极小值之间的谱形。反过来，也不能仅凭某个模型在一个 \(E_R\) 点给出更大的 \(R_A\)，就断言它在整个 LZ 能区给出更大的事件数。天然氙的逐同位素求和和速度阈值会重新加权这些差异。

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

### 5.3 \(m_s\) 与 \(\Delta m\) 在 benchmark 中扮演不同角色

四组 benchmark 的参数选择可以直接展示“末态阈值”和“虚态传播子”是两种不同的物理效应。

首先，固定 \(v,E_R,m_{\chi_1},m_A\) 时，三体末态开放条件是
\[
W_{\max}^2(v,E_R)\ge(m_{\chi_1}+m_s)^2.
\]
因此增大 \(m_s\) 会提高 \(W_{\min}\)，压缩允许的 \(W^2\) 区间，并使 \(v_{\min}\) 增大。表中第一个开放的 5 keV 网格点由 \(m_s=200\) keV 时的 35 keV，移动到 300 keV 时的 100 keV，再移动到 360 keV 时的 190 keV。这不是核响应谷值移动，而是三体相空间开始开放的运动学门槛在改变。

其次，\(\Delta m\) 不出现在 \(W_{\min}=m_{\chi_1}+m_s\) 中，因为末态并没有真实的 \(\chi_2\)。它改变的是
\[
W^2-m_{\chi_2}^2
=W^2-(m_{\chi_1}+\Delta m)^2
\]
这一内部传播子虚度。因而 Green 与 Blue 具有相同的 \(m_s=300\) keV，运动学开放阈值相同；但 \(\Delta m\) 从 1 MeV 增至 10 MeV 后，传播子离极点更远，截面归一化和谱形会改变。若同时改变 \(g_2\)，还必须重新计算条件性宽度，不能只按耦合乘积缩放。

在当前 \(m_{\chi_1}=1\) TeV 的例子中，\(v=800\) km/s 的固定速度曲线是论文图形的运动学诊断；它高于截断 SHM 的 \(776\) km/s 实验室速度上限。它不能直接解释为 halo 中有粒子以 800 km/s 入射的真实事件率。这个区分尤其重要：固定速度下三体相空间开放，并不保证所选 halo 模型下有足够的粒子通量。


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

> **公式追溯：** 核质量转换、天然丰度和每 kg 靶核数的定义见[附录 D，§D.1–D.3](appendices/09D_natural_xenon_isotope_target.md)；对应输入表和 metadata 见[索引 F7](formula_symbol_code_cross_reference.md)。

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

> **公式追溯：** 天然氙靶数和逐同位素求和见[附录 D](appendices/09D_natural_xenon_isotope_target.md)；三体 \(v_{\min,A}\)、实验室系 PDF 和 halo folding 见[附录 E，§E.1–E.3](appendices/09E_halo_velocity_vmin_folding.md)。AFH selected-point 与 GCN/JJ55 连续谱使用不同 runner 和结果目录，详见[索引 F7–F10](formula_symbol_code_cross_reference.md)。

其中：

- \(x_A\)：天然氙中同位素 \(A\) 的原子丰度；
- \(f_{\rm lab}(v)\)：实验室系暗物质速度分布；
- \(v_{\min,A}\)：该同位素在给定 \(E_R\) 下允许三体过程的最低入射速度；
- \(v_{\max}\)：所采用 halo 模型的实验室系速度上限；
- \(v/c\)：速度通量因子。

这里的 \(v_{\min,A}\) 应从本三体过程的相空间支持条件得到，并且依赖同位素质量；不能不加检查地用普通弹性 \(2\to2\) 散射的 \(v_{\min}\) 公式代替。

其显式阈值表达式为

\[
a_A=m_s+\frac{m_AE_R+m_s^2/2}{m_{\chi_1}},\qquad
Q_A=\sqrt{2m_AE_R+E_R^2},
\]

\[
\beta_{\min,A}=
\frac{Q_AE_R+a_A\sqrt{Q_A^2-E_R^2+a_A^2}}
{Q_A^2+a_A^2},
\qquad v_{\min,A}=c\beta_{\min,A}.
\]

> **公式追溯：** 完整阈值推导见[附录 E，§E.2](appendices/09E_halo_velocity_vmin_folding.md)；数值实现和逐同位素阈值输出见[索引 F8](formula_symbol_code_cross_reference.md)。

这一阈值公式可以从三体相空间边界直接推导，而不是套用弹性散射的标准表达式。令
\[
Q_A=\sqrt{2m_AE_R+E_R^2},\qquad
a_A=m_s+\frac{m_AE_R+m_s^2/2}{m_{\chi_1}},
\]
并用 \(p_{\chi_1}=m_{\chi_1}\gamma\beta\)、\(E_{\chi_1}=m_{\chi_1}\gamma\)。在阈值处令
\[
W_{\max,A}^2=(m_{\chi_1}+m_s)^2.
\]
代入 \(W_{\max,A}\) 后得到
\[
\gamma(\beta Q_A-E_R)=a_A.
\]
再使用 \(\gamma^{-2}=1-\beta^2\)，可化为
\[
(Q_A^2+a_A^2)\beta^2
-2Q_AE_R\beta+(E_R^2-a_A^2)=0.
\]
取物理的正根便得到正文的 \(\beta_{\min,A}\)。这一步说明 \(v_{\min,A}\) 由真实末态标量质量、核反冲和入射暗物质质量共同决定；\(\Delta m\) 不进入这个阈值方程，是因为 \(\chi_2\) 只是内部传播子，而不是外部末态。

速度积分本身也有明确的通量含义。每千克靶中同位素 \(A\) 的核数是 \(N_Tx_A\)，暗物质数密度是 \(n_\chi=\rho_\chi/m_{\chi_1}\)，速度为 \(v\) 的暗物质通量正比于 \(n_\chi v\)。因此从单核微分截面得到单位靶质量的事件率，结构上必然是
\[
\frac{dR}{dE_R}
=N_T n_\chi\sum_Ax_A
\int dv\,f_{\rm lab}(v)\,v\,
\frac{d\sigma_A}{dE_R}(v).
\]
本文以 \(v\) 的 km/s 数值输入，并将物理速度写成 \(c(v/c)\)，于是得到正文公式中的 \(c\) 与 \(v/c\)。这里 \(f_{\rm lab}(v)\) 是速度模长的概率密度，满足 \(\int dv\,f_{\rm lab}(v)=1\)，不是三维速度矢量分布；额外的 \(v\) 是通量因子，不能用一个平均速度简单替代整个积分。

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

> **公式追溯：** 截断 SHM 的分段速度 PDF、归一化和支持区间见[附录 E，§E.1](appendices/09E_halo_velocity_vmin_folding.md)；对应数值归一化结果见[索引 F9](formula_symbol_code_cross_reference.md)。

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

### 6.5 为什么“刚好开放”仍然可能几乎没有事件？

运动学开放只意味着积分区间非空，并不意味着事件率可观。截断 SHM 的实验室速度支持区间是
\[
0\le v\le v_{\max}=v_{\rm esc}+v_E=776\ {\rm km/s}.
\]
在高速度分支，PDF 含有
\[
e^{-(v-v_E)^2/v_0^2}-e^{-v_{\rm esc}^2/v_0^2}.
\]
当 \(v\) 从下方接近 \(v_{\max}\) 时，两项相互抵消，故
\[
f_{\rm SHM}(v)\propto v_{\max}-v.
\]
于是若 \(v_{\min}\) 只比 \(v_{\max}\) 低一个很小的量，单纯速度 PDF 所提供的积分权重就按速度窗口宽度的平方趋于零；同时，三体积分 \(I_6\) 也会在相空间阈值处缩小。因此“低于 776 km/s”只是开放条件，不是事件率足够大的保证。

Green/Blue 在 \(E_R=101\) keV 时是一个极端例子：七种可用同位素中只有 Xe-136 的阈值低于截断端点，且
\[
v_{\min,136}=775.806\ {\rm km/s},\qquad
v_{\max}-v_{\min,136}\simeq0.194\ {\rm km/s}.
\]
所以它虽然在数学上开放，实际只剩一个极窄且 PDF 接近零的速度区间。相比之下，在 \(E_R=200\) keV，Green 的阈值条件明显放宽，速率上升到 \(1.8136\times10^{-11}\) events/(kg day keV)。这说明反冲能量变化不仅改变核响应，还会改变哪些 halo 速度可以贡献。

同样，Black 在 \(E_R=101\) keV 的截断 SHM 速率为零，准确含义是当前可用同位素的 \(v_{\min,A}\) 全部高于 \(776\) km/s，故该 halo 模型的积分支持区间为空；这不是说该粒子物理模型在任意更高速度下的微分截面恒等于零。untruncated boosted Maxwell–Boltzmann 诊断允许更高速度，因此给出非零结果，但那是另一个 halo 假设，不应拿它替代截断 SHM 的基准结论。


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

### 7.1 如何区分运动学关闭、halo 抑制和核响应抑制？

这三种情况在数值上都可能表现为很小的 \(dR/dE_R\)，但物理含义不同：

1. **三体运动学关闭：** \(W_{\max,A}<m_{\chi_1}+m_s\)，或等价地 \(v<v_{\min,A}\)。对应同位素在该速度和反冲点没有允许的三体末态，kernel 返回零。
2. **Halo 端点抑制：** \(v_{\min,A}<v_{\max}\)，但两者非常接近。积分并非严格为零，只是速度 PDF 在截断端点趋于零，且可用速度区间很窄。
3. **核响应抑制：** \(R_A(E_R)\) 位于核 form-factor 极小值附近。此时粒子侧三体过程可能仍然开放，但核内相干电荷振幅发生强烈相消。

判断一个小事件率时，应分别检查 \(W_{\max}-W_{\min}\)、\(v_{\max}-v_{\min}\) 和 \(R_A(E_R)/A^2\)，而不是仅看最终速率一个数字。Green 在 101 keV 的主要问题是 halo 端点抑制；Black 在同一点是运动学关闭；核响应极小值则是另一条独立的核结构效应。三者不能混为同一种“截面谷值”。


## 8. 数值验证、归档状态与限制

### 8.1 已完成的检查

- 从官方 AFH v6.0 源文件解析 Xe-131 的 67 项密度矩阵，并与归档 CSV 逐项比较；
- AFH source-to-Python 翻译与源文件数据一致；
- **独立 60 位精度 mpmath 全网格对照已通过：** 对全部 2401 个 q 节点逐点比较，最大振幅绝对差为 \(3.98\times10^{-14}\)，最大相对振幅差（参考振幅绝对值大于 \(10^{-10}\)）为 \(8.83\times10^{-13}\)，最大响应绝对差除以 \(A^2\) 为 \(1.22\times10^{-15}\)；
- Xe-131 AFH 脚本的 Python regression tests 通过；
- 四组 benchmark 的 AFH/GCN/JJ55 响应替换表完成逐点重构检查，并已统一改用 exact spatial q；
- 天然氙 Eq. (6) kernel 与速度积分完成 selected-point 网格收敛检查；
- 天然氙归档完整性验证 workflow 通过；
- AFH exact_spatial 默认模式重新计算 98 个逐同位素贡献和 14 个总速率，与归档结果的最大总速率相对差异为 \(2.67\times10^{-12}\)，CI run 43044583357 通过；
- 核响应 (q) 与精确三体运动学 (q) 的定义、质量壳推导及 NR 近似对照见正式附录 G。
- AFH q 审计、NR 近似敏感性和固定 (M_A=131u) 的四点对照已由 CI run 43045857679 通过；四组 fixed-speed benchmark 已按 exact spatial q 重算并上传 artifact。
- LZ 2026 Fig. S2 的 final-ROI central efficiency 曲线与灰色系统包络已从官方 PDF 的矢量路径提取，并与独立数字化在 248 keV 处对照；灰色包络仅作为系统范围，不赋予置信水平（CI run 43151814368）。
- GCN/JJ55 天然氙连续谱已与 LZ 2026 一维效率曲线及 2.84 tonne-year exposure 做 rate-level 折叠；分段线性函数乘积采用解析积分，稠密梯形交叉检查的最大相对差异为 \(3.77\times10^{-7}\)（CI run 43151727539）。该事件数只对应 GCN/JJ55 连续谱，不对应 AFH selected-point 结果。

### 8.2 尚未完成或不能过度声称的事项

1. **AFH 空间 q 与 NR 近似必须继续分开表述。** AFH 定义 \(y=(q b_A/2)^2\)，其中 \(q\) 是空间动量转移；精确质量壳关系给出 \(q_{\rm exact}=\sqrt{2m_AE_R+E_R^2}\)。28 个天然氙样本全部匹配 exact spatial q，现作为默认物理基线。\(q_{\rm NR}=\sqrt{2m_AE_R}\) 仅作为小反冲近似，其 Xe-131 响应差异已定量记录。
2. **Xe-124/Xe-126 尚未纳入 AFH default-density 天然氙求和。** 缺少当前 AFH v6.0 内置 density matrix；七种可用同位素覆盖天然丰度 0.998158，未对这七种同位素重新归一化。
3. **连续谱的核模型覆盖并不相同。** GCN/JJ55 已有四组 benchmark 的天然氙连续反冲谱；AFH 目前仍是 selected-point rates，因为尚未恢复完整的七同位素 AFH 响应网格。不能把 GCN/JJ55 连续谱称为 AFH 连续谱。
4. **LZ detector mapping 已完成 rate-level 的第一层，但尚非完整 recast。** 已提取 LZ 2026 Fig. S2 的一维 final-ROI efficiency central curve 和灰色系统包络，并使用 2.84 tonne-year exposure 对 GCN/JJ55 连续谱计算 efficiency-weighted event yields。尚缺能量分辨/重建卷积、二维 \({S1_c,\log_{10}S2_c}\) 信号 PDF、NEST 响应及其 nuisance covariance、背景样本与相关约束、profile likelihood。因此这些 event yields 不是 90% CL 排除，也不能单独解释 248 keV 候选事件。
5. **极点宽度是条件性的。** 只包括给定假设下的 \(\chi_2\to\chi_1s\) 标量通道，不等于完整模型的矢量加标量自能。
6. **halo 模型依赖尚未做系统扫描。** untruncated MB 只用于高速度尾部敏感性诊断，不作为默认 halo 结果。

### 8.3 数据修正记录

早期 AFH benchmark CSV 曾出现两类归档问题：

- AFH CSV 中两处缺失换行，导致相邻记录拼接；现已修复，完整 2401 点表可正确解析；
- 早期 benchmark CSV 的 AFH \(R_A\) 列曾误复制 GCN 值，而截面列已经按 AFH/GCN 响应比缩放。现已改为保存真实插值 AFH 响应，并由显示的 \(R_A\) 和 \(I_6\) 直接重构截面。

修正后 AFH 开放点截面相对早期旧值的最大变化为 \(2.7406\times10^{-4}\)。此外，四组 benchmark 已从 NR-q 近似统一到 exact spatial q；在 101、200、267、542 keV 四个 selected recoil 点，Xe-131 的 NR 近似响应偏差最大约 225 ppm。引用结果时应使用当前 exact-spatial corrected archive，不应使用早期 CSV。

## 9. 当前研究决策与下一步

本阶段已经固定的决定：

1. AFH v6.0 default density 作为本阶段 Xe 核响应的标准输入；
2. 固定 AFH 文献默认 \(b_A\)，不拟合谷值；
3. 物理等质子、等中子耦合与 AFH 原始 isoscalar response 之间的因子 4 只计入一次；
4. 对固定同位素和运动学条件，AFH/GCN/JJ55 共用同一个 \(I_6\)，只替换核响应；
5. 天然氙采用逐同位素丰度加权，且不对当前缺失的 Xe-124/Xe-126 丰度重新归一化；
6. 截断 SHM 作为 halo 基准，untruncated MB 仅作为尾部敏感性诊断；
7. GCN/JJ55 连续谱的 LZ efficiency-weighted event yields 仅为 rate-level 结果，灰色效率包络不是置信区间；
8. 不把固定速度截面、AFH selected-point 速率、GCN/JJ55 连续谱和完整 LZ detector-level likelihood 混为一谈。

后续研究事项按物理依赖关系排列；Xe-131 原生 Mathematica 2401 点响应对照已经完成并归档，不再列为待执行任务：

1. **AFH 连续谱输入。** 恢复完整七同位素 AFH 响应网格后，才能将 AFH selected-point halo fold 扩展为连续谱。Xe-124/Xe-126 的密度矩阵缺失应单独处理，不得用丰度重归一化掩盖。
2. **完整 LZ detector-level likelihood。** 现有一维效率曲线和 GCN/JJ55 rate-level yields 是接口基线；真正的 recast 还需 NEST 二维响应、能量分辨/重建、校准与 nuisance covariance、背景数据及 profile likelihood。不能直接移植 LZ 的两体非弹性 WIMP 限制。
3. **模型与 halo 系统误差。** 在固定基准定义后，分别评估核响应模型、halo 参数和条件性 \(\chi_2\) 极点宽度对结果的影响；各项假设应分开报告，不用统一经验缩放代替。

本报告的下一轮编辑优先任务是让摘要、状态表、数值验收矩阵和 detector-level 接口章节对上述完成状态使用完全一致的术语。本报告的下一轮编辑优先任务是让摘要、状态表、数值验收矩阵和 detector-level 接口章节对上述完成状态使用完全一致的术语。
---

## 10. 代码、数据和文献入口

### 仓库内的主要研究记录

- 公式—符号—正文—程序—结果交叉引用索引：`research/docs/formula_symbol_code_cross_reference.md`（F1–F12 公式追溯、单位、近似、代码入口和结果文件）。
- 450 keV pointwise L00 benchmark：[输入与计算记录](../figure2_full_reproduction/results/USER_L00_BENCHMARK_G1_G2_GVN_1_DELTA_M_450KEV.md)；[本地验收记录](../figure2_full_reproduction/results/USER_L00_BENCHMARK_450KEV_LOCAL_2026-11-13/LOCAL_VALIDATION_2026-11-13.md)。
- 450 keV fixed-speed Xe-131 curve：[结果记录](../figure2_full_reproduction/results/USER_DSIGMA_CURVE_450KEV_LOCAL_2026-11-13.md)；该结果仅是内部反冲能量网格上的固定速度诊断。
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

**归档状态说明：** 本文是 AFH 核响应、三体积分、天然氙同位素、halo folding 与 LZ rate-level 接口的阶段性研究主报告。PR #7（merge commit f4f2ee91f6a51399dd3b5c06d64878b7f79322d7）是此前将报告纳入研究分支的历史记录；随后 PR #10 已于 2026-11-13 将研究主线正式合并到默认分支 main，merge commit 为 724d9e7877fb76f4cc477fbb9e24e1e706bf37a6。本轮在原有 450 keV 结果导航和归档状态基础上，增加了主报告正文的物理推导与物理意义说明；没有修改模型输入、数值程序或已归档数值结果，也没有声称完成新的物理验证或数值计算。

---

## 附录导航与独立文件

主报告后文保留完整附录 A–G。为便于检索、单独引用和维护，七份附录还分别保存为独立 Markdown 文件；主报告正文与七份独立副本保持同步：

| 附录 | 内容 | 文件 |
|---|---|---|
| A | 三体运动学、相空间边界与 Dirac 振幅 | [09A_three_body_kinematics_amplitude.md](appendices/09A_three_body_kinematics_amplitude.md) |
| B | AFH v6.0 密度矩阵、谐振子基底与响应实现 | [09B_afh_v6_density_matrix_response.md](appendices/09B_afh_v6_density_matrix_response.md) |
| C | AFH isoscalar 归一化与因子 4 | [09C_afh_isoscalar_factor4_normalization.md](appendices/09C_afh_isoscalar_factor4_normalization.md) |
| D | 天然氙同位素、丰度和核靶归一化 | [09D_natural_xenon_isotope_target.md](appendices/09D_natural_xenon_isotope_target.md) |
| E | 实验室系速度分布、三体最小速度与 halo folding | [09E_halo_velocity_vmin_folding.md](appendices/09E_halo_velocity_vmin_folding.md) |
| F | 计算程序、数据文件、收敛验收和复现命令 | [09F_numerical_validation_reproduction.md](appendices/09F_numerical_validation_reproduction.md) |
| G | AFH 空间动量转移、精确质量壳关系与 NR 近似审计 | [09G_recoil_momentum_convention_audit.md](appendices/09G_recoil_momentum_convention_audit.md) |

### 独立研究记录（不属于主报告附录）

- [研究决定登记](supplements/research_decision_register.md)：记录讨论中的候选处理、当前采用的约定和适用边界。

七项主要文档内容分别由附录 A–G 承担。公式交叉引用索引是导航文件，不是新增正式附录；研究决定登记用于专项追溯，也不改变主报告 A–G 的正式结构。

附录与主报告使用同一研究分支维护。程序、CSV 和机器可读结果仍保存在各自计算目录中；附录负责解释其定义、调用方式和验证边界，不复制大体积数据。

---

## 11. LZ 2026 extended nuclear-recoil search: detector-level interface

The relevant experimental target is the LUX-ZEPLIN (LZ) dual-phase liquid-xenon TPC. Its 2026 extended nuclear-recoil analysis uses a \(2.84\ {\rm tonne\,year}\) exposure, corresponding to 220 live days and a \(4.71\pm0.08\) tonne fiducial mass. The active TPC contains 7 tonnes of liquid xenon.

The WIMP-search region of interest is defined in reconstructed observables, not directly in true recoil energy:

\[
3\le S1_c\le600\ {\rm phd},\qquad
S2>645\ {\rm phd},\qquad
2.75\le\log_{10}S2_c\le4.15.
\]

The final nuclear-recoil signal efficiency is energy dependent. It exceeds 50% between approximately \(5.4\) and \(269.9\) keV and averages 96% over \(14\)–\(250\) keV. The latter is an average, not a constant efficiency to apply over the entire spectrum. The analysis uses tuned NEST v2.4.5 response modeling and signal/background probability-density functions in \(\{S1_c,\log_{10}S2_c\}\) space.

### 11.1 What can be compared immediately

The continuous GCN/JJ55 spectra and the AFH selected-point rates are **true nuclear-recoil rates before detector response**. For a first rate-level comparison, the expected accepted signal count is

\[
N_{\rm sig}^{\rm ROI}
=
\mathcal E
\int_{5.4\,{\rm keV}}^{269.9\,{\rm keV}}
dE_R\,
\epsilon_{\rm LZ}(E_R)
\frac{dR}{dE_R},
\]

where

\[
\mathcal E=2.84\ {\rm tonne\,year}
=1.03731\times10^6\ {\rm kg\,day}.
\]

> **公式追溯：** 一维效率折叠的程序、输入曲线、事件数 CSV 和 metadata 见[交叉引用索引 F11](formula_symbol_code_cross_reference.md)；其适用范围和未完成的二维 likelihood 项见附录 F.5。

This is an efficiency-weighted event-yield estimate. It is not, by itself, a 90% confidence-level exclusion or a full LZ likelihood recast.

### 11.2 What is required for a genuine LZ recast

The final LZ selection is applied in the two-dimensional \(S1_c\)–\(\log_{10}S2_c\) plane. The one-dimensional final-ROI efficiency curve and its gray envelope have already been digitized from Fig. S2 and used for a preliminary rate-level fold. A full recast still requires:

1. the underlying efficiency calibration information and its nuisance/covariance treatment; the plotted gray envelope is retained as a systematic range, not assigned a confidence level;
2. the tuned NEST v2.4.5 signal response, including the joint S1/S2 distributions, correlations and energy-reconstruction smearing;
3. the model-specific two-dimensional signal PDF generated from this model's own \(dR/dE_R\), rather than borrowing an LZ PDF for a different interaction; a continuous AFH prediction additionally requires the full isotope response grids;
4. the science, prompt-veto and delayed-veto samples and their correlated background constraints;
5. the published profile-likelihood construction and nuisance-parameter treatment.

### 11.3 Scope boundary for the present calculation

The current \(5\)–\(800\) keV theoretical recoil grid is intentionally wider than the high-efficiency LZ search window. The continuous GCN/JJ55 numerical scan uses 5 keV spacing through 270 keV, then 20 keV spacing from 280 to 800 keV; the selected comparison points 101, 200, 267 and 542 keV are inserted explicitly. The AFH natural-xenon result remains selected-point only. For the 2026 LZ comparison, only the \(5.4\)–\(269.9\) keV interval enters the quoted WIMP-search ROI at greater than 50% efficiency. The \(270\)–\(800\) keV part remains a theoretical prediction and should not be counted as accepted LZ exposure. The efficiency-weighted event yields reported below apply only to the continuous GCN/JJ55 spectra.

The central final-ROI efficiency curve and the gray uncertainty envelope have now been extracted from the vector paths in Fig. S2 and archived at:

- `research/lz_detector_response/lz_2026_extended_nr/lz_2026_nr_efficiency_digitized.csv`;
- `research/lz_detector_response/lz_2026_extended_nr/lz_2026_nr_efficiency_metadata.json`;
- the extracted vector page `lz_2026_figS2.svg`.

The extraction is reproducible from the official arXiv PDF using `research/figure2_full_reproduction/extract_lz_2026_nr_efficiency.py`; [CI run #43151814368](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43151814368) passes the extraction and independent-digitization regression tests. The central curve gives a mean final-ROI efficiency of 95.471% over 14–250 keV, 0.529 percentage points below the paper's rounded 96%. Its high-energy 50% crossing is 269.868 keV, consistent with 269.9 keV. At low energy, the central vector curve crosses 50% near 5.090 keV, whereas the paper text/caption quotes 5.4 keV; the central curve is 57.18% at 5.4 keV. This discrepancy is retained explicitly, and the published 5.4 keV lower ROI boundary is used without rescaling the curve.

A useful independent check comes from Di Mauro, arXiv:2609.02608v2, Appendix D. That independent digitization reports \(\epsilon(248\,{\rm keV})=0.9457\), with lower/upper envelope values 0.8835 and 0.9800. Our extracted central/lower/upper values are 0.9456876, 0.8835461 and 0.9800029, respectively; all three agree within the quoted precision. At 269.9 keV the extracted central/lower/upper values are 0.49882, 0.46599 and 0.51687. The gray envelope is treated as a detector-systematic range only: LZ does not assign a confidence level to this plotted envelope.

The HEPData YAML/JSON endpoints for DOI `10.17182/hepdata.182472.v1` returned HTTP 403 Cloudflare challenge pages. The workflow explicitly rejects HTML challenge pages rather than treating them as downloaded data; see [retrieval and extraction run #43151814368](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43151814368). Thus the current numerical efficiency inputs are a reproducible digitization of the official PDF, not an HEPData machine-readable table. The raw HEPData table and the tuned NEST parameter/covariance files remain unavailable from the current CI route.

### 11.4 Preliminary LZ rate-level event-yield calculation

The central efficiency and gray envelope have been folded with the continuous natural-xenon GCN/JJ55 spectra over \(5.4\le E_R\le269.9\) keV, using the published nominal exposure
\[
\mathcal E=2.84\ {\rm tonne\,year}=1.03731\times10^6\ {\rm kg\,day}.
\]
The integration is exact for the adopted piecewise-linear interpolation: the recoil-spectrum and efficiency knot sets are merged, and the product of two linear functions is integrated analytically on each interval. A dense trapezoidal cross-check differs from the exact result by at most \(3.77\times10^{-7}\); doubling the dense grid changes the result by at most \(2.29\times10^{-7}\).

The following values use \((g_1g_2g_{VN})^2=10^{-8}\), \(g_2=1\), \(m_{\chi_1}=1\) TeV, \(m_V=10\) GeV, \(\rho_\chi=0.3\ {\rm GeV/cm^3}\), and the truncated SHM with \((v_0,v_E,v_{\rm esc})=(220,232,544)\) km/s. The \(\chi_2\) propagator uses the conditional pole-width prescription described above. Brackets denote the lower/upper gray detector-efficiency envelope, not a statistical confidence interval.

| Benchmark | GCN expected events | JJ55 expected events |
|---|---:|---:|
| Red: \(m_s=0.20\) MeV, \(\Delta m=1\) MeV | \(0.338\ [0.316,0.350]\) | \(0.346\ [0.323,0.359]\) |
| Green: \(m_s=0.30\) MeV, \(\Delta m=1\) MeV | \(1.525\times10^{-3}\ [1.424,1.580]\times10^{-3}\) | \(1.579\times10^{-3}\ [1.475,1.637]\times10^{-3}\) |
| Black: \(m_s=0.36\) MeV, \(\Delta m=1\) MeV | \(2.853\times10^{-9}\ [2.666,2.957]\times10^{-9}\) | \(2.879\times10^{-9}\ [2.691,2.984]\times10^{-9}\) |
| Blue: \(m_s=0.30\) MeV, \(\Delta m=10\) MeV | \(1.248\times10^{-5}\ [1.166,1.293]\times10^{-5}\) | \(1.293\times10^{-5}\ [1.208,1.340]\times10^{-5}\) |

At the reference coupling, only the red benchmark approaches an appreciable fraction of one expected event. Holding \(g_2\) and the conditional pole width fixed, the squared coupling product needed to obtain one expected event is \(2.96\times10^{-8}\) (GCN) or \(2.89\times10^{-8}\) (JJ55) for red; \(6.56\times10^{-6}\) or \(6.33\times10^{-6}\) for green; \(3.51\) or \(3.47\) for black; and \(8.01\times10^{-4}\) or \(7.73\times10^{-4}\) for blue. These are rate-normalization values only, not exclusion limits.

The GCN/JJ55 central-yield differences are about 0.94–3.59%, smaller than the changes between the four particle-physics benchmarks. The gray efficiency envelope changes the integrated yields by approximately \(-6.6\%\) to \(+3.6\%\) for these spectra. The black benchmark is especially suppressed because the ROI overlaps only its extreme high-speed tail; at \(E_R=267\) keV, \(v_{\min}\) for Xe-131 is about 775 km/s, close to the truncated-SHM endpoint of 776 km/s.

The results are archived in `research/lz_detector_response/lz_2026_extended_nr/rate_level_event_yields/`; the successful rate-fold CI run is [#43151727539](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43151727539). The event yields are preliminary rate-level estimates for the GCN/JJ55 nuclear-response spectra. No AFH continuous-spectrum event yield is quoted. They do not include energy-resolution smearing, the two-dimensional \(\{S1_c,\log_{10}S2_c\}\) signal PDFs, the NEST nuisance-parameter covariance, background samples or the LZ profile likelihood. They are not a 90% confidence-level exclusion and do not establish an interpretation of the 248 keV event.

### 11.5 High-energy-tail diagnostic around the 248 keV candidate

To separate spectral hardness from overall normalization, I also integrated the efficiency-weighted spectrum over \(225\le E_R\le269.9\) keV. The lower boundary is \(248-23\) keV, i.e. the lower statistical-error edge of the reported candidate energy; this is only a high-energy-tail diagnostic. It is not a likelihood window, and no energy-resolution or systematic-energy smearing is applied.

| Benchmark | Fraction of accepted events above 225 keV (GCN/JJ55) | Accepted events in 225--269.9 keV (GCN/JJ55) |
|---|---:|---:|
| Red | 2.25% / 2.32% | \(7.61\times10^{-3}\) / \(8.02\times10^{-3}\) |
| Green | 8.62% / 8.78% | \(1.31\times10^{-4}\) / \(1.39\times10^{-4}\) |
| Black | 92.84% / 92.76% | \(2.65\times10^{-9}\) / \(2.67\times10^{-9}\) |
| Blue | 8.57% / 8.74% | \(1.07\times10^{-6}\) / \(1.13\times10^{-6}\) |

This separates two distinct properties. Red has the largest total accepted rate but places only about 2.3% of its accepted events above 225 keV. Black has an extremely hard spectrum, with more than 92% of its already tiny accepted rate above 225 keV, but its total rate is only about \(3\times10^{-9}\) events. Green and Blue are intermediate in spectral hardness but remain strongly rate-suppressed at the reference coupling. Thus a hard spectrum alone does not establish an explanation of the 248 keV event: the normalization must also be viable.

A nuclear-response distinction is also necessary. The LZ 2026 paper states that its published theory spectra use WimPyDD with one-body density matrices developed for DMFormFactor-v6, modified as described in Ref. [31]. The continuous spectra archived in this repository use the available GCN/JJ55 isotope-response grids as an independent nuclear-model comparison; they are not claimed to reproduce the LZ collaboration's modified nuclear-response inputs. The AFH v6.0 calculation remains a separate selected-point result until the full seven-isotope AFH response grid is recovered.

**Experimental reference:** LZ Collaboration, D. S. Akerib et al., *Search for dark matter particle interactions in an extended nuclear recoil energy window with the LUX-ZEPLIN (LZ) experiment*, arXiv:2609.02823v1 (2026), data release DOI: [10.17182/hepdata.182472.v1](https://doi.org/10.17182/hepdata.182472.v1).

### 11.6 从真实核反冲到 LZ 重建信号：一维效率折叠的含义

理论计算得到的 \(dR/dE_R\) 是真实核反冲能量 \(E_R\) 的分布；LZ 事件选择则作用在重建观测量 \(S1_c\) 和 \(\log_{10}S2_c\) 上。两者之间需要探测器响应概率
\[
\mathcal P(S1_c,\log_{10}S2_c\mid E_R),
\]
它描述一个真实能量为 \(E_R\) 的核反冲在探测器中产生何种光信号、电离信号和重建值。

若有完整二维响应，则对应的信号分布结构为
\[
\frac{d^2R}{dS1_c\,d\log_{10}S2_c}
=\int dE_R\,
\frac{dR}{dE_R}
\mathcal P(S1_c,\log_{10}S2_c\mid E_R).
\]
一维 final-ROI efficiency 实际上是将该二维条件概率在选定区域积分：
\[
\epsilon_{\rm ROI}(E_R)
=\int_{\rm ROI}dS1_c\,d\log_{10}S2_c\,
\mathcal P(S1_c,\log_{10}S2_c\mid E_R).
\]

若将 \(\mathcal P\) 视为在完整重建观测空间上归一化的条件概率密度，则
\[
\int_{\rm all}dS1_c\,d\log_{10}S2_c\,
\mathcal P(S1_c,\log_{10}S2_c\mid E_R)=1,
\]
而对 ROI 的积分就是该真实反冲能量下通过相应选择的概率，因此
\(0\le\epsilon_{\rm ROI}(E_R)\le1\)。当前使用的 Fig. S2 一维效率曲线已经是该二维响应在 ROI 上的投影；不能再把相同的 S1/S2 选择效率重复乘一次。若未来使用完整二维 PDF，则应直接在观测空间构造信号分布并进入 likelihood，而不是再把一维效率曲线重复应用。

因此
\[
N_{\rm sig}^{\rm ROI}
=\mathcal E\int dE_R\,
\epsilon_{\rm ROI}(E_R)\frac{dR}{dE_R}
\]
给出的是预计通过该选择的事件数。

这解释了当前 rate-level fold 的边界：它使用一维 \(\epsilon_{\rm ROI}(E_R)\) 计算总接受数，但没有保留 \(S1_c\) 与 \(S2_c\) 的联合形状，也没有对能量重建分辨率、相关 nuisance parameters 和背景 PDF 作 profile likelihood。灰色效率包络是图中给出的系统范围，不是统计置信区间。故一维效率折叠是完整 detector-level likelihood 的一个投影量，而不是它的替代品。


## 12. 阶段性结论与结果解释

本报告已经把三体核散射的理论截面、核结构输入、天然氙靶求和、halo 速度积分以及 LZ 一维效率加权接口连接起来。但这些层级的完成程度不同，不能将某一层的结果自动视为下一层已经完成。

### 12.1 理论与核响应层面的结论

1. **三体截面具有清晰的因式分解结构。** 对固定同位素和入射运动学，Eq. (6) 可写为粒子物理与三体相空间部分乘以核响应 \(R_A(E_R)\)。在 AFH、GCN、JJ55 之间进行受控核模型比较时，可以在相同运动学点复用同一个 \(I_6\)，只替换核响应；这不是对每个核模型重新计算一套独立三体积分。
2. **AFH 归一化约定已经固定。** AFH 原始 isoscalar response 的零动量归一化为 \(A^2/4\)，而论文前因子显式提出物理单核子耦合 \(g_{VN}^2\) 时，使用的物理相干响应应满足 \(R_A^{\rm phys}(0)=A^2\)。因子 4 只计入一次。
3. **AFH 响应使用空间动量。** 默认输入为 \(q_{\rm exact}=\sqrt{2m_AE_R+E_R^2}\)，而传播子使用不变量 \(t=-2m_AE_R\)。\(q_{\rm NR}=\sqrt{2m_AE_R}\) 只作为小反冲近似对照，不与 \(t\) 混淆。
4. **AFH Xe-131 response-level 数值验证已完成。** 2401 个 \(q\) 节点的 60 位精度 mpmath 有限和检查与 Wolfram 14.0.0 原生 Mathematica/Python 逐点比较均通过；原生比较的最大相对差异为 \(3.59\times10^{-9}\)，q 网格完全一致。该结果只验证 Xe-131 AFH 核响应及其归一化，不代表完整 AFH 天然氙连续谱。

### 12.2 当前结果覆盖范围

| 研究层级 | 当前结果 | 不能据此声称 |
|---|---|---|
| AFH Xe-131 | default density matrix、固定 \(b_A\)、2401 点响应网格 | mpmath 与原生 Mathematica/Python 逐点对照均已通过；最大相对差异 \(3.59\times10^{-9}\) |
| 固定速度截面 | 四组 Figure 2 benchmark；AFH/GCN/JJ55 受控响应替换 | \(v=800\) km/s 是截断 SHM 支持区间内的 halo 速度 |
| AFH 天然氙 | 七种可用同位素的 selected-point halo fold | 已得到连续 AFH 天然氙反冲谱，或已包含 Xe-124/Xe-126 |
| GCN/JJ55 天然氙 | 四组 benchmark 的连续反冲谱 | 这些核响应等同于 LZ 合作组的修改后 WimPyDD 输入 |
| LZ rate-level interface | 一维效率曲线、灰色系统包络和 2.84 tonne-year exposure 折叠 | 已构造二维信号 PDF、背景 likelihood 或实验排除 |

AFH 可用的七种同位素覆盖天然氙原子丰度的 0.998158；缺失的 Xe-124 与 Xe-126 丰度没有重新分配给其他同位素。AFH 当前的天然氙结果仍是 selected-point rates。连续谱和下表的 LZ efficiency-weighted yields 使用 GCN/JJ55 核响应。

### 12.3 LZ rate-level event yields 与高能尾部

在参考耦合 \((g_1g_2g_{VN})^2=10^{-8}\)、\(g_2=1\) 和名义曝光 2.84 tonne-year 下，GCN/JJ55 连续谱给出的效率加权预期事件数为：

| Benchmark | GCN expected events | JJ55 expected events | \(225\)–\(269.9\) keV 接受事件比例（GCN/JJ55） |
|---|---:|---:|---:|
| Red | 0.338 | 0.346 | 2.25% / 2.32% |
| Green | \(1.525\times10^{-3}\) | \(1.579\times10^{-3}\) | 8.62% / 8.78% |
| Black | \(2.853\times10^{-9}\) | \(2.879\times10^{-9}\) | 92.84% / 92.76% |
| Blue | \(1.248\times10^{-5}\) | \(1.293\times10^{-5}\) | 8.57% / 8.74% |

表中事件数的灰色效率包络上下变化见第 11.4 节；它是系统范围，不是置信区间。高能尾部比例是 \(225\)–\(269.9\) keV 区间积分占整个 WIMP-search ROI 接受事件数的比例，不是经过能量分辨卷积的候选事件窗口概率。

这组结果体现了**谱形硬度与总归一化必须分开判断**：

- Red 的总接受事件数最大，但只有约 2.3% 位于 225 keV 以上；
- Black 的高能尾部比例超过 92%，但总接受事件数只有约 \(3\times10^{-9}\)；
- Green 与 Blue 的高能尾部比例约为 8.6%–8.8%，但在参考耦合下总事件数仍很小。

因此，单独拥有较硬的高能谱尾并不足以解释 248 keV 候选事件；总归一化、探测器响应和完整统计模型同样重要。上述事件数只对应 GCN/JJ55 连续谱，不是 AFH 连续谱预测。

### 12.4 本阶段结论的适用边界

当前结果可以支持以下表述：已经建立并归档了从三体微分截面到天然氙理论反冲谱、再到一维效率加权 rate-level event-yield estimate 的计算链，并对 AFH、GCN、JJ55 核响应作了分层比较。

当前结果**不能**支持以下更强结论：

1. 不能称为完整 LZ detector-level recast 或 90% CL exclusion；
2. 不能把 LZ 论文中的两体 \(\chi_1+A\to\chi_2+A\) 限制直接移植到本研究的三体过程；
3. 不能把 GCN/JJ55 连续谱或其 LZ 效率加权事件数标记为 AFH 预测；
4. 不能把 248 keV 单个候选事件当作信号计数进行拟合；
5. 不能把 mpmath 高精度交叉检查描述为官方 Mathematica 原生验证。

后续物理工作仍取决于完整 AFH 同位素响应输入，以及 LZ 的二维 NEST 响应、校准协方差、背景数据和 profile likelihood；Xe-131 原生 Mathematica 对照已完成。

### 12.5 450 keV supplied benchmark 与固定速度曲线

450 keV 结果包含两个彼此独立的计算层级，必须分开引用。

**A. 单一运动学点的 \(\mathcal L_{00}\) 与 \(I_6\) benchmark。** 输入为 \(g_1=g_2=g_{VN}=1\)、\(m_{\chi_1}=1\) TeV、\(\Delta m=450\) keV、\(m_s=300\) keV 和 \(m_V=10\) GeV。由于 supplied particle benchmark 本身没有指定唯一的点态运动学，数值验收沿用明确标记的诊断点：\(m_A=122\) GeV、\(E_R=200\) keV、\(v=776\) km/s、\(W^2\) midpoint、\(z=0.2\)、\(\phi_*=1.1\)。在该点，zero-width 与条件性 Dirac / pure-scalar / single-open-channel pole-width 结果分别为
\[
\mathcal L_{00}^{(0)}=3.3933323921\times10^{14},\qquad
\mathcal L_{00}^{(\Gamma)}=3.2510906491\times10^{14},
\]
\[
I_6^{(0)}=1.6218103154\times10^7\ {\rm GeV}^2,\qquad
I_6^{(\Gamma)}=1.5439364806\times10^7\ {\rm GeV}^2.
\]
对应变化分别为 \(-4.1918\%\) 和 \(-4.8017\%\)。显式自旋求和与 Dirac trace 的相对差异为 \(2.22\times10^{-16}\)，最大四动量闭合残差为 \(2.13\times10^{-13}\) GeV；\((40,32,20)\) 与 \((48,40,24)\) 的 \(I_6\) 相对差异约为 \(6.54\times10^{-7}\)（zero width）和 \(6.66\times10^{-7}\)（pole width）。这些数值只验收该点态 trace 和 reduced integral，不代表完整矢量加标量自能或任何 halo-folded spectrum。

**B. Xe-131 fixed-speed differential curve。** 另一份独立曲线使用 \(m_{\chi_1}=1\) TeV、\(\Delta m=450\) keV、\(m_s=300\) keV、\(m_V=10\) GeV、\((g_1g_2g_{VN})^2=1\)，固定 \(v=776\) km/s，采用 \(m_A=131u\) 的质量近似、GCN/JJ55 response tables 和 zero-width prescription。已归档 105 个内部点（130–650 keV，5 keV 间隔）；该网格上的最大值位于 175 keV，GCN/JJ55 分别为 \(1.874622684\times10^{-32}\) 和 \(1.985254401\times10^{-32}\) cm\(^2\)/keV。1 keV 局部细化得到的 dip 位置是离散采样极小值，不是连续极小值。

该固定速度开放反冲区间约为
\[
109.150286\ {\rm keV}<E_R<654.955583\ {\rm keV}.
\]
当前曲线只覆盖 130–650 keV；两端尚未完成高阶 \(I_6\) 积分。边界 bracket 测试只证明运动学开放/关闭位置，不等于端点附近的积分收敛验证。该曲线也不是截断 SHM 的 halo average：即使速度数值取到 776 km/s，也不能将单一速度点当作对速度分布的积分。

完整复现命令、输入质量方案、响应插值和限制分别记录在附录 F.7、固定速度曲线结果记录及 pointwise benchmark local-validation record 中。

### 12.6 科学状态表（P0–P2，2026-11-13）

状态定义：**已验证**表示公式、程序与归档数值在明确适用范围内闭合；**条件性验证**表示核心实现和代表性测试通过，但仍受参数覆盖、独立推导或物理假设限制；**未完成**表示所需计算或物理输入尚不存在。

| 公式 / 工作项 | 状态 | 已有证据 | 尚存边界 |
|---|---|---|---|
| F1 精确空间动量、四动量转移与 \(t\) | 已验证 | 核质量壳关系、28 个 AFH 样本 q 审计、exact/NR 对照 | NR 仅为小反冲敏感性对照 |
| F2 \(W_{\min}^2,W_{\max}^2\) 与相空间开闭 | 条件性验证 | limits、wmax_squared、开闭区间和阈值回归 | 尚未对更宽质量—速度区域做独立扫描 |
| F3 三体相空间变量与 \(I_6\) | 条件性验证 | 独立 \(d\Phi_3\) 推导、\(256\pi^3\) 因子核查、方位角平均权重测试、代表点积分收敛 | 完整连续反冲网格的 \(I_6\) 收敛仍需验证 |
| F4 两张辐射图与 Dirac trace | 条件性验证 | before/after/干涉分解、显式自旋求和、壳条件与四动量闭合 | 目前是代表性测试点，不是全参数扫描 |
| F5 单同位素固定速度 Eq. (6) | 条件性验证 | 四 benchmark 的 AFH/GCN/JJ55 响应替换与截面重构 | 共用既有 \(I_6\)，并非 640 个独立三体积分重算 |
| F6 AFH 响应与因子 4 归一化 | 已验证（限定 Xe-131 response-level） | 原始 \(A^2/4\)、物理 \(A^2\)；2401 点 mpmath 与原生 Mathematica/Python 比较通过；最大相对差异 \(3.59\times10^{-9}\) | 完整 AFH 天然氙连续谱仍缺 Xe-124/Xe-126 输入和完整同位素响应网格 |
| F7 同位素质量、丰度与 \(N_T\) | 已验证 | 九同位素质量—丰度表、精确加权平均质量和每 kg 靶核数 | 电子结合能忽略；AFH 响应可用同位素仅七种 |
| F8 三体 \(v_{\min,A}\) | 已验证 | 28/28 逐同位素阈值复算；最大速度差 \(4.35\times10^{-10}\) km/s | 适用范围为当前 benchmark 与输入质量约定 |
| F9 实验室系速度 PDF | 已验证 | untruncated MB 与 truncated SHM 数值积分归一化 | 物理预测仍依赖所选 halo 参数 |
| F10 天然氙 \(dR/dE_R\) | 条件性验证 | AFH selected-point；GCN/JJ55 连续谱及速度积分收敛 | 完整 AFH 连续谱和 Xe-124/Xe-126 响应未完成 |
| F11 LZ 效率加权事件数 | 条件性验证 | 一维 Fig. S2 efficiency、2.84 tonne-year、rate-level 折叠 | 二维 NEST、能量分辨、背景与 profile likelihood 未完成 |
| F12 \(\chi_2\to\chi_1s\) pole width | 条件性验证 | 条件性 Dirac 纯标量单通道宽度公式和数值测试 | 非完整自能；未纳入所有可能开放衰变道 |
| 三体相空间 Jacobian / \(256\pi^3\) 独立推导 | 已验证 | 从单粒子不变测度独立重建 \(d\Phi_3\)，并逐项核对 \(t\leftrightarrow E_R\)、\(z,\phi_*\)、通量与核电荷流 | 适用于未极化靶、相干且仅保留 \(J_A^0\) 的近似；完整数值积分收敛另行检查 |
| AFH 原生 Mathematica 全网格运行 | 已完成 PASS | Wolfram 14.0.0 Windows；2401 点；q 网格完全一致；四种响应量比较全部通过；最大相对差异 \(3.59\times10^{-9}\)；SHA-256 manifest 已归档 | 适用范围仅为 Xe-131 AFH response-level；不替代三体积分、天然氙连续谱或 LZ likelihood 验证 |
| AFH 完整天然氙连续谱 | 未完成 | 七种可用同位素 selected-point rate 已完成 | 需要七同位素完整响应网格；Xe-124/Xe-126 还缺 AFH density matrix |
| 完整 LZ detector-level recast | 未完成 | GCN/JJ55 一维效率加权 rate-level yields | 需要二维信号 PDF、NEST nuisance、背景和 profile likelihood |

**P0 判定：** 精确空间动量 Python 复算、60 位 mpmath 全网格检查、Wolfram 14.0.0 原生 Mathematica/Python 2401 点比较和归档输出核验均已完成。**P1 判定：** F1–F12 的追溯索引和重点一致性检查已完成；F3 的解析相空间 Jacobian 与 \(256\pi^3\) 已独立验证，但完整连续反冲网格收敛仍未完成。**P2 判定：** 完整 AFH 天然氙连续谱和完整 LZ likelihood 仍未完成，不能因 Xe-131 response-level 对照通过而升级状态。

## 13. 公式—符号—程序—结果交叉引用

本节提供正文核心公式的快速导航。完整符号表、单位、近似条件、程序函数和机器可读结果路径集中维护在独立文件：[公式—符号—正文—程序—结果交叉引用索引](formula_symbol_code_cross_reference.md)。

### 13.1 核心公式导航

| 索引 | 正文公式 / 物理对象 | 完整推导 | 主要程序 |
|---|---|---|---|
| F1 | \(q^\mu\)、\(Q=|\mathbf q|\)、\(t\) 的关系 | [A.1](appendices/09A_three_body_kinematics_amplitude.md)、[G.1–G.5](appendices/09G_recoil_momentum_convention_audit.md) | `rate_kinematics.py`、`eq6_kernel.py` |
| F2 | \(W_{\min}^2,W_{\max}^2\)、相空间开闭、\(m_{s,\max}\) 与最优 \(E_R^*\) | §2.4、§6.3 | [A.2–A.2.1](appendices/09A_three_body_kinematics_amplitude.md) | `eq6_kernel.limits`、`rate_kinematics.wmax_squared` | 四 benchmark corrected CSV；逐速度阈值结果 | 固定同位素和入射速度；最优反冲能量最大化运动学质量上限，不是事件率峰值。 |
| F3 | 三体 Lorentz-invariant 相空间、\((W^2,z,\phi_*)\) Jacobian 与 \(I_6\) | §2.5.1–2.5.8 | [A.3–A.4.2](appendices/09A_three_body_kinematics_amplitude.md) | `eq6_kernel.py`：`build_point`、`reduced_kernel` | phase-space prefactor tests；joint-Xe131 convergence；quadrature crosschecks | \(I_6\) 为 GeV\(^2\)；\(256\pi^3\) 来自不变相空间、通量和方位角平均；完整连续反冲网格收敛仍单独验收。 |
| F4 | 两张辐射图、干涉项和 \(\mathcal L_{00}\) | [A.5–A.6](appendices/09A_three_body_kinematics_amplitude.md) | `eq6_kernel.vertices`、`spin_trace` |
| F5 | 单同位素固定速度截面 Eq. (6) | [A.4.1](appendices/09A_three_body_kinematics_amplitude.md) | joint_xe131.py、compute_four_benchmark_dsigma.py、run_user_dsigma_curve.py |
| F6 | AFH \(b_A,y,W_M^{00},R_A^{\rm phys}\) | [B.2–B.4](appendices/09B_afh_v6_density_matrix_response.md)、[C](appendices/09C_afh_isoscalar_factor4_normalization.md)、[G](appendices/09G_recoil_momentum_convention_audit.md) | `run_afh_default_xe131.py`、`joint_xe131.py` |
| F7 | \(m_A,x_A,N_T\) 天然氙靶归一化 | §6.2 | [D.1–D.5，特别是 D.3.1](appendices/09D_natural_xenon_isotope_target.md) | 两个天然氙 halo/spectrum runner | NIST 丰度质量表；natural-xenon metadata | \(N_T\) 使用完整九同位素平均原子质量；AFH 速率只求和七种可用响应且不重归一化。 |
| F8 | 三体阈值速度 \(v_{\min,A}\) | [A.2](appendices/09A_three_body_kinematics_amplitude.md)、[E.2](appendices/09E_halo_velocity_vmin_folding.md) | `rate_kinematics.vmin_three_body_beta` |
| F9 | 截断 SHM 与实验室系速度 PDF \(f_{\rm lab}(v)\) | §6.4 | [E.1–E.1.1](appendices/09E_halo_velocity_vmin_folding.md) | `shm_truncated_pdf`、`mb_untruncated_pdf` | halo PDF normalization CSV | 从银河系静止系三维截断 Maxwell 分布作 Galilean boost，再对速度方向积分；\(f_{\rm lab}\) 按速度模长归一化。 |
| F10 | 天然氙 halo-folded 微分事件率 \(dR/dE_R\) | §2.2、§6.3、§7 | [D.3–D.4](appendices/09D_natural_xenon_isotope_target.md)；[E.2–E.3.2](appendices/09E_halo_velocity_vmin_folding.md) | AFH selected-point / GCN-JJ55 continuous-spectrum runners | natural-xenon rate CSV；isotope contribution CSV | 由数密度、速度通量、单核截面和每 kg 靶核数推导；逐同位素使用自己的阈值和 kernel。 |
| F11 | LZ 一维效率加权预期事件数 \(N_{\rm sig}^{\rm ROI}\) | §11.1、§11.4、§11.6 | §11.6 的二维响应概率投影；附录 F.5 | `fold_lz_2026_rate_level.py` | efficiency CSV；rate-level yield CSV | 一维效率是二维重建响应在 ROI 上的概率投影；当前结果不是二维 likelihood 或 90% CL 排除。 |
| F12 | 条件性 \(\chi_2\to\chi_1s\) pole width | §1.2、§5 | [A.5–A.6.1](appendices/09A_three_body_kinematics_amplitude.md) | `eq6_kernel.chi2_width_dirac_scalar` | benchmark metadata：`width_scheme`、`g2` | 从 Dirac 纯标量 Yukawa 振幅和二体相空间推导；仅适用于 Dirac、实标量、纯标量耦合及单一开放衰变道。 |

### 13.2 必须区分的符号和物理层级

| 不应混用的量 | 正确区分 |
|---|---|
| \(q^\mu\)、\(Q\)、\(t\) | \(q^\mu\) 是四动量转移；\(Q=|\mathbf q|\) 是空间动量模长；\(t=(q^\mu)^2=-2m_AE_R\)。 |
| \(W\) 与 \(W^2\) | \(W\) 是 \(\chi_1+s\) 子系统不变质量；\(W^2\) 是数值积分变量。 |
| \(m_A\) 与 \(M_A\) | 天然氙使用逐同位素 NIST 核质量；固定 Figure-2 Xe-131 benchmark 使用 \(M_A=131u\)。必须读取对应 metadata。 |
| AFH raw response 与 \(R_A^{\rm phys}\) | AFH 原始 isoscalar 零动量归一化为 \(A^2/4\)；Eq. (6) 中的物理响应归一化为 \(A^2\)，因子 4 只计一次。 |
| \(I_6\)、\(d\sigma_A/dE_R\)、\(dR/dE_R\)、\(N_{\rm sig}^{\rm ROI}\) | 依次是三体 reduced kernel、单核固定速度微分截面、天然氙 halo-folded 理论速率、再经过一维效率和曝光折叠的预期事件数。 |
| 固定 \(v=800\) km/s 与截断 SHM | 前者是 Figure-2 固定速度截面诊断；后者的最大实验室速度为 776 km/s，二者不是同一 halo 预测。 |

### 13.3 单位总约定

- 微观公式与 kernel：自然单位；质量、能量、三动量均为 GeV，\(W^2\) 为 GeV\(^2\)，\(I_6\) 为 GeV\(^2\)，\(R_A\) 与耦合无量纲。
- AFH 核结构：\(b_A\) 先以 fm 给出，进入 \(y=(Qb_A/2)^2\) 前转换为 GeV\(^{-1}\)；\(Q\) 以 GeV 输入。
- halo：速度和 \(v_{\min}\) 以 km/s 报告，\(f_{\rm lab}\) 的单位为 (km/s)\(^{-1}\)；通量因子中 \(v/c\) 无量纲，外部光速换算为 cm/s。
- 截面：程序内部 \(d\sigma/dE_R\) 为 GeV\(^{-3}\)，报告中的 benchmark 表换算为 cm\(^2\)/keV。
- 事件率：\(dR/dE_R\) 为 events/(kg day keV)；LZ exposure 为 kg day，最终 \(N_{\rm sig}^{\rm ROI}\) 无量纲。

### 13.4 复现与维护

详细的逐公式输出文件、metadata、验证状态和复现命令见[独立交叉引用索引第 2–6 节](formula_symbol_code_cross_reference.md)。附录 F.3 是命令行复现入口；附录 F.4 区分软件测试、数值收敛和物理完整性。任何公式、变量或计算方案改变时，必须同步更新本节和独立索引，不得只更新正文显示公式。

### 13.5 数值结果索引、物理公式审查与科学状态

为避免主报告、附录和结果目录分别维护不同的 benchmark 口径，当前归档另设三份互相对应的维护记录：

- [Figure 2 数值结果总索引](supplements/figure2_results_master_index_2026-11-13.md)：benchmark、输入、参数、输出文件与 SHA-256；机器可读清单见 [JSON manifest](supplements/figure2_results_master_index_2026-11-13.json)。
- [物理公式交叉审查](supplements/figure2_physics_formula_audit_2026-11-13.md)：从原始拉格朗日量、两张辐射图、Dirac trace、三体相空间、\(256\pi^3\)、AFH factor 4、三体 \(v_{\min}\) 到天然氙速率逐项对照主报告、附录和代码。
- [科学结果状态表](supplements/figure2_scientific_status_2026-11-13.md)：将每项结果明确标记为已验证、部分验证、待补输入或尚未完成，并注明适用范围和剩余限制。

这三份记录是本报告的复现与审查入口，不替代附录 A–G 中的正式推导，也不把 selected-point、fixed-speed 或 rate-level 结果升级表述为完整模型或完整 LZ likelihood 的验证。

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


#### A.6.1 从 Dirac 标量 Yukawa 振幅推导条件性二体宽度

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


#### B.2.1 该谐振子长度公式的性质

\[
b_A=
\sqrt{\frac{41.467}{45A^{-1/3}-25A^{-2/3}}}\ {\rm fm}
\]
是 AFH/DMFormFactor v6.0 所采用的 default 核结构处方。这里的常数属于壳模型谐振子基底的经验/模型输入，不是从本文暗扇区拉格朗日量、Eq. (6) 或三体运动学推导出来的动力学关系。本研究的任务是忠实采用并评估该处方，而不是重新拟合它。若改变 \(b_A\)，就等于改变核结构模型输入，必须作为独立核模型变体报告。

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

#### B.7.1 原生 Mathematica 2401 点对照（2026-11-13）

用户本地 Windows 环境使用 Wolfram 14.0.0 执行了 AFH v6.0 原生程序，并将原始 \(W_M^{00}\)、AFH package response、物理等质子等中子 raw response 和 q=0-normalized response 与 Python 参考表逐点比较。\(q\) 网格为 \(0\)–\(0.6\) GeV、步长 \(0.00025\) GeV，共 2401 点；两套网格完全一致，不做插值。采用 \(2\times10^{-8}\) 相对容差与 \(2\times10^{-10}\) 绝对容差，四种响应量全部 PASS，最大相对差异 \(3.59087\times10^{-9}\)，最坏点位于 \(q=0.2565\) GeV，失败点数为零。

原始 package response 在 \(q=0\) 为 \(4289.895955714992\)，相对 \(A^2/4=4290.25\) 偏差 \(8.2523\times10^{-5}\)，来自有限精度密度矩阵。物理 raw response 由 AFH response 乘因子 4 得到；随后独立使用 \(C_0=1.0000825298069378\) 做 q=0 形状归一化，使 \(R_A(0)=A^2\)。\(C_0\) 不是因子 4。完整环境、源文件哈希、逐点差异和 manifest 见 [native audit record](../afh_default_density_xe131/output/native_audit/NATIVE_MATHEMATICA_AUDIT.md)。

这项验证只覆盖 Xe-131 AFH response-level，不代表 Eq. (6) 三体积分、天然氙连续谱或 detector-level likelihood。60 位 mpmath 检查仍作为另一条独立高精度数值交叉验证保留。

### B.8 AFH 空间动量与精确三体反冲

AFH 原始定义为

\[
y=\left(\frac{q b_A}{2}\right)^2,
\]

其中 \(q\) 是空间动量转移的大小。对初态静止的核，精确质量壳关系给出

\[
q_{\rm exact}=\sqrt{2m_AE_R+E_R^2},
\qquad
y_{\rm exact}=\frac{b_A^2}{4}(2m_AE_R+E_R^2).
\]

常见的 \(y_{\rm NR}=b_A^2m_AE_R/2\) 对应 \(q_{\rm NR}=\sqrt{2m_AE_R}\)，是 \(E_R\ll m_A\) 的近似，而不是 AFH 对空间 \(q\) 的定义本身。

因此，本项目在精确三体运动学下统一采用 exact spatial q：

- AFH 响应插值：\(q_{\rm exact}\)；
- 三体末态四动量、\(W_{\max}\)、\(v_{\min}\)：\(q_{\rm exact}\)；
- 媒介子传播子：\(t=-2m_AE_R\)，故分母 \(m_V^2-t=m_V^2+2m_AE_R\)；
- \(q_{\rm NR}\)：只作为独立的非相对论响应近似对照。

28 个天然氙 AFH 响应样本全部与 exact spatial q 相符，因此不需要为当前 selected-point halo fold 重新生成响应。NR 近似的响应影响及 Xe-131 的 2401 点 AFH 响应网格对照见附录 G。

代码默认值现统一为 exact_spatial；nr_approx 只用于敏感性对照，legacy_exact 保留为向后兼容别名。若响应样本与所选 q 不匹配，程序会显式报错。

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


#### D.1.1 从中性原子质量得到核质量

NIST 表给出的是中性原子的原子质量，而散射运动学使用原子核质量。忽略电子结合能时，中性原子质量可写为
\[
M_{\rm atom}(A)u\simeq m_A+Z m_e.
\]
因此
\[
\boxed{
m_A\simeq [M_{\rm atom}(A)-Z m_e]u.
}
\]
这里 \(M_{\rm atom}(A)\) 和 \(m_e\) 均以原子质量单位 \(u\) 表示，转换因子为
\[
1u=0.93149410242\ {\rm GeV},
\qquad
m_e=0.000548579909065u.
\]
对氙 \(Z=54\)。忽略的是电子结合能带来的极小修正，而不是核结合能；核结合能已经包含在实测原子质量所对应的核质量中。天然氙每千克靶质量的摩尔数仍使用中性原子的平均摩尔质量 \(\bar M_{\rm Xe}\)，只有单核散射运动学使用扣除电子质量后的 \(m_A\)。

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


#### D.3.1 从天然同位素丰度推导每千克靶核数

这里的 \(x_A\) 是原子丰度，因此也等于天然混合物中的摩尔分数，而不是质量分数。完整天然氙的丰度加权平均摩尔质量为
\[
\bar M_{\rm Xe}=\sum_{A\in{\rm natural}}x_A M_{\rm atom}(A).
\]
一千克靶物质包含
\[
n_{\rm mol}=\frac{1000\ {\rm g}}{\bar M_{\rm Xe}}
\]
摩尔氙原子。乘以阿伏伽德罗常数，得到每千克靶物质中的核总数
\[
\boxed{
N_T=N_{\rm Av}n_{\rm mol}
=\frac{N_{\rm Av}\,1000}{\bar M_{\rm Xe}}
=4.586803334466193\times10^{24}\ {\rm kg}^{-1}.
}
\]
其中本轮使用
\[
\bar M_{\rm Xe}=131.29276144779053\ {\rm g/mol},
\qquad
N_{\rm Av}=6.02214076\times10^{23}\ {\rm mol}^{-1}.
\]
第 \(A\) 种同位素在一千克天然氙中的靶核数为
\[
N_{T,A}=x_A N_T.
\]
因此按每千克靶质量写事件率时，必须先乘总靶核数 \(N_T\)，再以原始原子丰度 \(x_A\) 分配到各同位素；不能再额外乘一次质量分数或 \(A\) 因子。

这里有两个不同的同位素集合：\(\bar M_{\rm Xe}\) 使用完整九种天然同位素，决定真实的一千克天然氙有多少个原子；当前 AFH 响应求和只覆盖七种有 default density matrix 的同位素，且不把七种丰度重新归一化到 1。缺失的 \(0.001842\) 是原子丰度缺口，并不自动等于事件率缺失比例。

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

AFH 响应插值采用精确空间动量转移

\[
q_{\rm resp}=\sqrt{2M_AE_R+E_R^2}.
\]

天然氙 halo-fold 程序也采用同一质量壳关系，但使用每种同位素各自的 NIST 原子质量减去电子质量所得核质量：

\[
m_A=[M_{\rm atom}(A)-54m_e]u,\qquad
q_{{\rm resp},A}=\sqrt{2m_AE_R+E_R^2}.
\]

因此，两个计算链当前的区别是**核质量输入约定**：固定速度 Xe-131 benchmark 使用参考质量 \(M_A=131u\)，天然氙计算使用逐同位素 NIST 核质量；它们不再采用不同的 \(q_{\rm resp}\) 近似。两者都使用精确空间动量。传播子中的四动量转移不变量则分别按对应核质量写成 \(t=-2M_AE_R\) 或 \(t=-2m_AE_R\)，不能与空间 \(q^2\) 混淆。

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


#### E.1.1 从银河系静止系截断 Maxwell 分布推导实验室速度 PDF

标准晕模型先在银河系静止系定义三维速度矢量分布
\[
f_{\rm gal}(\mathbf u)
=\frac{1}{N_{\rm esc}\pi^{3/2}v_0^3}
e^{-u^2/v_0^2}\,
\Theta(v_{\rm esc}-u).
\]
归一化常数由
\[
1=\int d^3u\,f_{\rm gal}(\mathbf u)
=\frac{4\pi}{N_{\rm esc}\pi^{3/2}v_0^3}
\int_0^{v_{\rm esc}}du\,u^2e^{-u^2/v_0^2}
\]
确定。令 \(z_{\rm esc}=v_{\rm esc}/v_0\)，径向积分给出
\[
N_{\rm esc}
=\operatorname{erf}(z_{\rm esc})
-\frac{2z_{\rm esc}}{\sqrt\pi}e^{-z_{\rm esc}^2}.
\]
实验室相对银河系以速度 \(\mathbf v_E\) 运动。伽利略变换只平移速度矢量，
\[
\mathbf u=\mathbf v+\mathbf v_E,
\]
不改变速度空间体积元。实验室系速度模长 PDF 因而是对方向积分：
\[
f_{\rm lab}(v)
=v^2\int d\Omega_v\,
f_{\rm gal}(\mathbf v+\mathbf v_E).
\]
取 \(\mu=\cos\theta=\hat{\mathbf v}\cdot\hat{\mathbf v}_E\)，则
\[
u^2=v^2+v_E^2+2vv_E\mu.
\]
在没有逃逸速度截断时，角积分为
\[
\int_{-1}^{1}d\mu\,
e^{-(v^2+v_E^2+2vv_E\mu)/v_0^2}
=\frac{v_0^2}{2vv_E}
\left[
e^{-(v-v_E)^2/v_0^2}
-e^{-(v+v_E)^2/v_0^2}
\right].
\]
乘上 \(2\pi v^2/(N_{\rm esc}\pi^{3/2}v_0^3)\)，得到第一段速度分布的解析形式。

加入 \(u\le v_{\rm esc}\) 后，角积分还必须满足
\[
\mu\le
\mu_{\max}(v)
=\frac{v_{\rm esc}^2-v^2-v_E^2}{2vv_E}.
\]
当 \(0\le v<v_{\rm esc}-v_E\) 时，所有方向都允许，恢复上面的两指数之差；当
\(v_{\rm esc}-v_E\le v\le v_{\rm esc}+v_E\) 时，只允许
\(-1\le\mu\le\mu_{\max}\)，上端指数固定为
\(e^{-v_{\rm esc}^2/v_0^2}\)，从而得到正文 E.1 的第二个分支；当
\(v>v_{\rm esc}+v_E\) 时，不存在满足银河系逃逸速度条件的方向，PDF 为零。因此
\[
v_{\max,\rm lab}=v_{\rm esc}+v_E.
\]
速度平移不改变三维积分的归一化，所以方向积分后的模长 PDF 满足
\[
\int_0^\infty dv\,f_{\rm lab}(v)=1.
\]
这也解释了为什么它的单位为 \(({\rm km/s})^{-1}\)，而不是三维速度分布的 \(({\rm km/s})^{-3}\)。当前计算未加入年度调制；\(v_E\) 被视为固定 benchmark。

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


平方前的阈值方程还要求
\[
\gamma(\beta Q-E_R)=a>0,
\]
所以物理解必须满足 \(\beta Q>E_R\)。二次方程的两个代数根中，回代原始未平方方程后，只有
\[
\beta_{\min}
=\frac{QE_R+a\sqrt{Q^2-E_R^2+a^2}}{Q^2+a^2}
\]
满足这一符号条件；这就是上式选取正号分支的原因。数值上还应检查 \(0\le\beta_{\min}<1\)。若 \(v_{\min,A}>v_{\max,\rm lab}\)，该同位素在当前截断 halo 下没有速度支持，事件率积分严格为零。

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


### E.3.1 从暗物质数密度和粒子通量推导天然氙事件率

暗物质质量密度除以单粒子质量给出数密度
\[
n_\chi=\frac{\rho_\chi}{m_{\chi_1}}.
\]
实验室系速度落在 \([v,v+dv]\) 的粒子数密度为
\(n_\chi f_{\rm lab}(v)\,dv\)，它们穿过单位面积的通量为
\[
d\mathcal F_\chi
=n_\chi f_{\rm lab}(v)\,v_{\rm phys}\,dv.
\]
对一个固定同位素核，单位时间、单位反冲能量的散射率等于入射通量乘以微分截面：
\[
\frac{d\Gamma_A}{dE_R}
=n_\chi\int_{v_{\min,A}}^{v_{\max}}
dv\,f_{\rm lab}(v)\,v_{\rm phys}
\frac{d\sigma_A}{dE_R}(v).
\]
每千克天然氙含有 \(N_Tx_A\) 个该同位素核，因此对所有可用同位素求和：
\[
\frac{dR}{dE_R}
=N_T\sum_Ax_A\frac{d\Gamma_A}{dE_R}.
\]
将 \(v_{\rm phys}=c(v/c)\) 写成程序使用的混合单位形式，就得到
\[
\boxed{
\frac{dR}{dE_R}
=N_T\frac{\rho_\chi}{m_{\chi_1}}c
\sum_Ax_A
\int_{v_{\min,A}}^{v_{\max}}
dv\,f_{\rm lab}(v)\frac vc
\frac{d\sigma_A}{dE_R}(v).
}
\]
这里 \(v\) 与 \(f_{\rm lab}\) 的单位分别为 km/s 和 \(({\rm km/s})^{-1}\)，所以
\(f_{\rm lab}(v)\,dv\) 与 \(v/c\) 都无量纲；前面的 \(c\) 在通量换算时使用 cm/s。程序在每个速度节点重新计算
\[
p_{\chi_1}(v)=\frac{m_{\chi_1}\beta}{\sqrt{1-\beta^2}}
\]
和 \(I_{6,A}(v,E_R)\)，因此不能用一个固定速度截面乘以平均速度代替速度积分。

若截面先以自然单位计算，则
\[
\left[\frac{d\sigma}{dE_R}\right]={\rm GeV}^{-3}.
\]
使用
\[
1\ {\rm GeV}^{-2}=0.389379\times10^{-27}\ {\rm cm}^2
\]
以及 \(1\ {\rm GeV}=10^6\ {\rm keV}\)，得到
\[
1\ {\rm GeV}^{-3}
\longrightarrow
0.389379\times10^{-33}\ {\rm cm}^2/{\rm keV}.
\]
最后将秒换算为天，乘以 \(86400\ {\rm s/day}\)，输出单位为
events/(kg day keV)。这里得到的仍是真实核反冲理论率；探测器效率和重建响应要在下一层单独折叠。

### E.3.2 AFH 响应动量与三体运动学

AFH 响应函数使用空间动量转移 \(q\)，满足 \(y=(qb_A/2)^2\)。本节的精确三体质量壳关系给出

\[
q_{\rm exact}=\sqrt{2m_AE_R+E_R^2}.
\]

因此 halo fold 中 \(R_A(E_R)\)、\(W_{\max,A}\)、\(v_{\min,A}\) 和三体 reduced kernel 均使用同一个精确空间动量。常见的

\[
q_{\rm NR}=\sqrt{2m_AE_R}
\]

只是 \(E_R\ll m_A\) 的非相对论反冲近似，保留为独立的响应敏感性对照。

当前归档的 28 个 AFH 天然氙响应样本全部是在 \(q_{\rm exact}\) 处取值，与精确三体运动学一致，不属于需要修正的 legacy 错误样本。附录 G 给出精确质量壳推导、28 个样本核查及 Xe-131 NR 近似的响应影响。

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

### E.7 exact-spatial-q 归档与 NR 近似对照

当前天然氙 selected-point halo fold 使用 AFH exact spatial q：

\[
q_{\rm response}=q_{\rm kin}
=\sqrt{2m_AE_R+E_R^2}.
\]

当前 exact_spatial 默认模式已完成完整回归复现。CI 对照了 98 个逐同位素贡献和 14 个总速率，最大逐同位素贡献相对差异为 \(4.32\times10^{-10}\)，最大总速率相对差异为 \(2.67\times10^{-12}\)。

- [exact-spatial CI run 43044583357](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43044583357)
- 机器可读比较：results/exact_spatial_reproduction_comparison.json
- 旧的 legacy_exact 别名回归记录仍保留在 results/legacy_exact_reproduction_comparison.json。

当前代码默认 exact_spatial，可直接运行：

~~~bash
python research/afh_default_density_natural_xenon_halo/run_afh_natural_xenon_halo_fold.py
~~~

若显式选择 nr_approx，程序会因输入样本仍采用 exact spatial q 而报错，除非同时提供在 NR q 处重新计算的匹配响应值。该检查用于防止把一个 q 点的 \(R_A\) 错误地标记成另一个 q 点的响应。

本节的 selected-point 速率保留 exact spatial q，不进行经验重标度。NR 近似的响应变化见附录 G；连续反冲谱仍需恢复完整七同位素 AFH 响应网格后再开展。

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
python research/afh_default_density_natural_xenon_halo/run_afh_natural_xenon_halo_fold.py
python research/afh_default_density_natural_xenon_halo/validate_archived_results.py
~~~

默认 exact_spatial 使用 AFH 定义的空间动量转移 (q=\sqrt{2m_AE_R+E_R^2})，与精确核质量壳关系一致。nr_approx 是 (q=\sqrt{2m_AE_R}) 的小反冲近似；当前 28 个响应样本不采用该近似，因此程序会拒绝将其与 exact-q 样本混用。legacy_exact 仍是 exact_spatial 的向后兼容别名。

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
| AFH 67 项密度矩阵解析 | 已完成 | 官方源解析、CSV 逐项核对、67 项计数；原生 Mathematica 已加载 built-in matrix 并完成全网格比较 | 无 Xe-131 矩阵解析遗留项 |
| AFH 默认 \(b_A\) | 已完成 | 公式、单位转换、Xe-131 数值回归测试 | 不需要拟合；不得用谷值调参 |
| AFH 零动量归一化 | 已完成（含有限精度修正） | 原始 \(A^2/4\)、物理响应 \(A^2\)、偏差 \(8.2523\times10^{-5}\) | 记录 AFH 空间 q 的精确质量壳关系，并区分 NR 近似 |
| AFH 谷值 | 已完成 | 离散候选点、直接响应局部极小化、minima.csv | 不需要调整 \(b_A\) |
| mpmath 独立有限和 | 已完成全网格 | 60 位精度、2401 个 q 节点；最大振幅绝对差 \(3.98\times10^{-14}\)，最大响应绝对差除以 \(A^2\) 为 \(1.22\times10^{-15}\) | 与原生 Mathematica 对照为独立验证；两者均已通过 |
| AFH 原生 Mathematica | 已完成 PASS | Wolfram 14.0.0 Windows；2401 点；raw \(W_M^{00}\)、AFH response、物理 raw 与 normalized response 全部逐点通过；最大相对差异 \(3.59\times10^{-9}\) | 仅 Xe-131 response-level；不是完整 Eq. (6) 或天然氙 rate 验证 |
| GCN/JJ55 对照 | 已完成归档 | 三种响应、四 benchmark、1920 行 long table | 对照共享既有 \(I_6\)，不是 640 次独立重算 |
| 三体运动学/Dirac trace | 已完成代表性检查 | 壳条件、四动量闭合、显式自旋求和、干涉分解 | 扩展到更宽的参数和质量网格 |
| 450 keV pointwise \(\mathcal L_{00}\)/\(I_6\) benchmark | 已完成本地验收 | 六项 regression tests、显式自旋求和、四动量闭合、三阶求积对照；见 local validation record | 仅覆盖指定诊断运动学点；pole width 依赖 Dirac / pure-scalar / single-channel 假设 |
| 450 keV Xe-131 fixed-speed curve | 已归档的内部网格诊断 | 105 点 130–650 keV、独立 PCHIP 重构、Eq. (6) anchor convergence、运动学端点 bracket | 109.150–654.956 keV 两端尚未完成高阶积分；固定速度、A×u 质量近似、zero width，不是 halo rate |
| 三体积分收敛 | 已有 selected-point 验证 | 六个天然氙点 \(8×8×4\) 对 \(16×16×8\)，最大差异 \(2.19×10^{-4}\)；独立 Eq. (6) 测试点 \(16×16×8\) 对 \(32×32×16\)，相对差异小于 \(5×10^{-5}\) | 连续反冲谱全网格收敛 |
| 天然氙速度积分 | 已有 selected-point 验证（exact spatial q） | 五个点 32 对 64 速度节点，最大差异 \(3.31×10^{-6}\)；98 个逐同位素贡献和 14 个总速率在 exact_spatial 默认模式下复现，最大总速率差异 \(2.67×10^{-12}\)，CI run 43044583357 | 连续谱和 halo 参数扫描 |
| AFH 空间 q 与 NR 近似 | 已完成审计与代码保护 | 28 个天然氙样本匹配 exact spatial q；Xe-131 四点 NR 近似响应差异约 5.5–225 ppm；halo fold CI run 43044583357 通过 | 连续反冲谱需要完整七同位素 AFH 响应网格 |
| Xe-124/Xe-126 | 输入缺失 | 缺失丰度合计 0.001842 | 取得密度矩阵并补算响应、阈值和速率 |
| 天然氙连续反冲谱 | GCN/JJ55 已完成；AFH 为 selected points | 四组 GCN/JJ55 连续谱，5–800 keV、七种可用同位素、exact spatial q 和截断 SHM | 完整七同位素 AFH 响应网格及连续 AFH 谱；Xe-124/Xe-126 AFH 输入 |
| LZ efficiency-weighted rate-level fold | GCN/JJ55 已完成初步折叠 | Fig. S2 一维效率曲线及灰色包络；2.84 tonne-year；四组 benchmark 事件数；解析分段积分与稠密梯形对照 | NEST 二维响应、能量分辨/重建、nuisance covariance、背景样本和 profile likelihood；AFH 连续谱尚不能折叠 |

这张表把软件测试、局部数值收敛和物理模型完整性分开。测试通过只说明被测试的代码路径满足相应断言，不等于所有参数点、所有核模型、halo 假设或实验响应都已验证。

### F.5 LZ detector-response interface：已完成部分与剩余工作

当前已经超出单纯的 pre-detector theoretical rate，但仍未达到完整 detector-level recast。已完成的第一层接口包括：

1. 从 LZ 2026 Fig. S2 的官方 PDF 矢量路径提取 final-ROI 一维 central efficiency 曲线及灰色上下包络，并保存 CSV、SVG 和提取 metadata；
2. 在 248 keV 处与独立数字化结果对照；灰色包络作为 detector-systematic range 使用，不赋予置信水平；
3. 使用公开的名义曝光 \(2.84\ {\rm tonne\,year}=1.03731\times10^6\ {\rm kg\,day}\)；
4. 将该效率曲线与 GCN/JJ55 连续天然氙谱在 \(5.4\le E_R\le269.9\) keV 内折叠，得到四组 benchmark 的 preliminary rate-level expected event yields；
5. 对分段线性谱与分段线性效率的乘积执行区间解析积分，并以稠密梯形积分交叉检查。

这组事件数**只对应 GCN/JJ55 连续核响应谱**。AFH 当前只有 selected-point 天然氙速率，因此不能将 GCN/JJ55 的连续谱折叠结果标记为 AFH 预测。效率曲线的机器可读 HEPData 端点当前受到 HTTP 403 challenge；归档数据来自官方 PDF 的可复现矢量提取，而不是声称下载到了 HEPData 原始 YAML/JSON 表。

完整 detector-level recast 仍至少需要：

1. tuned NEST v2.4.5 的联合 \(S1_c\)–\(\log_{10}S2_c\) 响应分布、相关性和能量重建/分辨模型；
2. 效率与探测器响应的校准 nuisance parameters 及其 covariance；当前 Fig. S2 灰色包络不是完整协方差矩阵，也不是置信区间；
3. 与该 LZ 数据集对应的 science、prompt-veto、delayed-veto 数据样本及背景约束；
4. 由本模型自己的 recoil spectrum 构造的二维信号 PDF；AFH 分支还需先恢复完整同位素响应网格；
5. LZ profile likelihood、系统误差参数化及信号/背景联合统计处理。

因此，当前结果应称为 **efficiency-weighted rate-level event-yield estimate**，而不是完整 LZ recast、90% CL 排除或对 248 keV 候选事件的统计解释。LZ 论文中的两体 \(\chi_1+A\to\chi_2+A\) 限制也不能直接移植到本研究的三体 \(\chi_1+A\to\chi_1+A+s\) 过程。

### F.6 历史数据和版本管理原则

1. 保留官方 AFH ZIP 与源文件 SHA-256。
2. 保留原始 67 项密度矩阵，不通过改写系数或 \(b_A\) 修正谷值。
3. 保留 AFH raw response 与物理 equal-\(p,n\) response 两列，因子 4 只应用一次。
4. 早期错误的 AFH response CSV 拼接换行和 benchmark CSV 中 AFH 列误复制 GCN 的版本应标记为 superseded；当前使用 corrected archive。
5. 任何新的 \(q_{\rm resp}\)、核质量、halo 参数、宽度方案或求积阶数都应产生新的输出和 metadata，不覆盖历史结果。
6. 主报告包含完整附录 A–G；本目录中的七份独立附录与主报告对应章节保持同步。
7. 程序、CSV、JSON 和源文件继续保存在各自计算目录，文档只解释其定义、来源、调用方式和验证边界。

## F.7 450 keV supplied benchmark：复现与适用边界

本节记录两个独立的 450 keV benchmark。它们共享粒子质量点，但并不共享全部运动学、核响应或传播子处方。

本节所列 native outputs 与 validation records 均已归档在 main。这里的 main-branch 状态只说明文件归档位置，不扩大各 benchmark 的物理适用范围。

### F.7.1 Pointwise \(\mathcal L_{00}\) 与 reduced \(I_6\)

输入为 \(g_1=g_2=g_{VN}=1\)、\(m_{\chi_1}=1\) TeV、\(\Delta m=450\) keV、\(m_s=300\) keV、\(m_V=10\) GeV。点态运动学为显式指定的诊断点：\(m_A=122\) GeV、\(E_R=200\) keV、\(v=776\) km/s、\(W^2\) midpoint、\(z=0.2\)、\(\phi_*=1.1\)。这不是由 supplied particle benchmark 唯一确定的运动学点。

从仓库根目录复现：

~~~bash
python research/figure2_full_reproduction/run_user_l00_benchmark.py \
  --nw 48 --nz 40 --nphi 24 \
  --output /tmp/USER_L00_BENCHMARK_450KEV_48x40x24.json
python -m unittest discover \
  -s research/figure2_full_reproduction/tests \
  -p test_user_l00_benchmark.py -v
~~~

本地验收记录位于：

- research/figure2_full_reproduction/research/figure2_full_reproduction/results/USER_L00_BENCHMARK_450KEV_LOCAL_2026-11-13/LOCAL_VALIDATION_2026-11-13.md；
- 同目录的 JSON、quadrature convergence CSV、run manifest、validation log 和 SHA256SUMS。

该结果比较 zero-width 与条件性 pole-width；后者只在 Dirac 费米子、实标量、纯 scalar off-diagonal Yukawa 且仅 \(\chi_2\to\chi_1s\) 通道开放的假设下成立。它不是完整 vector-plus-scalar self-energy，也不是 halo-folded 或 detector-level prediction。该本地验收没有使用 GitHub Actions；不能将未运行的 CI 描述为通过。

### F.7.2 Fixed-speed Xe-131 \(d\sigma/dE_R\) 曲线

该曲线采用 \(v=776\) km/s、\(m_A=131u\)、GCN/JJ55 response tables 和 zero-width prescription，扫描 130–650 keV 共 105 个内部点。它与 F.7.1 的 \(m_A=122\) GeV 点态 trace benchmark 不是同一核质量或传播子宽度方案。

从仓库根目录复现：

~~~bash
python research/figure2_full_reproduction/run_user_dsigma_curve.py \
  --step-keV 5 --nw 20 --nz 16 --nphi 12 \
  --output /tmp/xe131_dsigma_450kev.csv
python research/figure2_full_reproduction/plot_user_dsigma_curve.py
python -m unittest discover \
  -s research/figure2_full_reproduction/tests \
  -p test_user_dsigma_curve.py -v
~~~

结果与 provenance：

- research/figure2_full_reproduction/results/fixed_speed_xe131_dsigma_450kev.csv；
- research/figure2_full_reproduction/results/local_minima_refinement_1keV.csv；
- research/figure2_full_reproduction/results/kernel_quadrature_convergence_450kev.csv；
- research/figure2_full_reproduction/results/metadata_user_dsigma_450kev.json；
- research/figure2_full_reproduction/results/USER_DSIGMA_CURVE_450KEV_LOCAL_2026-11-13.md；
- research/figure2_full_reproduction/results/SHA256SUMS_user_dsigma_450kev.txt；
- research/figure2_full_reproduction/results/plots/fixed_speed_xe131_dsigma_450kev.svg；
- research/figure2_full_reproduction/results/plots/xe131_gcn_jj55_response_ratio_450kev.svg。

开放反冲区间约为 109.150286–654.955583 keV；当前曲线只覆盖 130–650 keV。两端的 kinematic bracket tests 不等于端点附近的高阶积分收敛，故当前归档只能称为内部网格 fixed-speed diagnostic。它不是天然氙 halo-folded spectrum、事件率、LZ detector-level prediction 或 exclusion。

### F.7.3 两项 benchmark 的不可互换性

| 项目 | Pointwise L00 benchmark | Fixed-speed Xe-131 curve |
|---|---|---|
| 核质量 | 122 GeV 诊断近似 | 131 u 质量近似 |
| 运动学 | 单一点：200 keV、776 km/s、指定角变量 | 105 个反冲能量点、固定 776 km/s |
| 核响应 | 点态 \(\mathcal L_{00}\)/\(I_6\)，不构成完整核响应谱 | GCN/JJ55 响应表 |
| 宽度 | zero-width 与条件性 scalar pole-width 对照 | zero width |
| 输出层级 | pointwise trace 与 reduced integral | 单同位素固定速度 \(d\sigma/dE_R\) |
| 不能声称 | 完整自能、halo rate、LZ 预测 | 完整开放区间、halo rate、detector likelihood |



---

## 附录 G：AFH 空间动量转移与非相对论反冲近似

### G.1 AFH 响应函数中的 \(q\) 是什么？

AFH 原始文献定义谐振子变量

\[
y=\left(\frac{qb_A}{2}\right)^2,
\]

其中 \(q=|\mathbf q|\) 是**空间动量转移的大小**。AFH 的核响应 \(W_M(y)\) 是这个空间动量变量的函数，而不是直接以洛伦兹不变量 \(t\) 为自变量。

参考：Fitzpatrick et al., *Model-independent WIMP Scattering Responses and Event Rates*, JCAP 02 (2013) 004, arXiv:1203.3542, Secs. 4 and 7.

### G.2 精确质量壳关系与常见 NR 近似

靶核初态静止：

\[
P^\mu=(m_A,\mathbf 0).
\]

反冲后的核满足

\[
P'^\mu=(m_A+E_R,\mathbf q),\qquad P'^2=P^2=m_A^2.
\]

因此

\[
(m_A+E_R)^2-|\mathbf q|^2=m_A^2,
\]

从而得到精确的空间反冲动量

\[
\boxed{q_{\rm exact}=\sqrt{2m_AE_R+E_R^2}}.
\]

代入 AFH 变量：

\[
\boxed{
y_{\rm exact}
=\frac{b_A^2}{4}(2m_AE_R+E_R^2)
}.
\]

在 \(E_R\ll m_A\) 时，忽略 \(E_R^2\) 项，才得到常用近似

\[
q_{\rm NR}=\sqrt{2m_AE_R},\qquad
y_{\rm NR}=\frac{b_A^2m_AE_R}{2}.
\]

所以两种表达的关系是：

| 量 | 精确三体计算 | 非相对论反冲近似 |
|---|---|---|
| 空间动量 | \(\sqrt{2m_AE_R+E_R^2}\) | \(\sqrt{2m_AE_R}\) |
| AFH 变量 | \(b_A^2(2m_AE_R+E_R^2)/4\) | \(b_A^2m_AE_R/2\) |
| 物理定位 | 质量壳精确关系 | \(E_R/m_A\) 展开最低阶 |

本项目的三体运动学保留精确质量壳关系，因此采用 \(q_{\rm exact}\) 作为 AFH 响应输入。\(q_{\rm NR}\) 只作为误差对照，不应被称为唯一正确的响应动量。

### G.3 28 个天然氙响应样本的约定核查

对七种有 AFH default density matrix 的氙同位素

\[
A=128,129,130,131,132,134,136
\]

及

\[
E_R=101,\ 200,\ 267,\ 542\ {\rm keV},
\]

逐点读取

research/afh_default_density_natural_xenon_halo/input/afh_response_samples.csv

并使用 NIST 原子质量减去 54 个电子质量得到核质量。28 个样本的 q_response_GeV 全部与 \(q_{\rm exact}\) 相符。

| \(E_R\) [keV] | \(q_{\rm exact}-q_{\rm NR}\) [keV] | \((q_{\rm exact}/q_{\rm NR}-1)\) [ppm] |
|---:|---:|---:|
| 101 | 0.031899–0.032882 | 0.199–0.212 |
| 200 | 0.088887–0.091626 | 0.395–0.420 |
| 267 | 0.137106–0.141332 | 0.527–0.560 |
| 542 | 0.396542–0.408764 | 1.071–1.138 |

结论：旧 28 点样本采用的是精确空间动量；这与 AFH 的 \(q\) 定义以及精确三体质量壳关系一致，不需要重新生成才能用于当前选定反冲点。

### G.4 响应曲线斜率会放大微小的动量差

虽然 \(q_{\rm exact}-q_{\rm NR}\) 只有亚 keV 量级，但 Xe-131 AFH 响应在衍射谷附近变化很快。使用新生成的 2401 点 AFH default Xe-131 响应网格做 PCHIP 插值，得到：

#### NIST Xe-131 核质量

| \(E_R\) [keV] | \(q_{\rm exact}-q_{\rm NR}\) [keV] | \(R_A(q_{\rm NR})/R_A(q_{\rm exact})-1\) [ppm] |
|---:|---:|---:|
| 101 | 0.032503 | +22.346 |
| 200 | 0.090569 | +5.458 |
| 267 | 0.139702 | +212.729 |
| 542 | 0.404049 | +97.363 |

#### Figure-2 固定 benchmark 质量 \(M_A=131u\)

| \(E_R\) [keV] | \(q_{\rm exact}-q_{\rm NR}\) [keV] | \(R_A(q_{\rm NR})/R_A(q_{\rm exact})-1\) [ppm] |
|---:|---:|---:|
| 101 | 0.032487 | +21.191 |
| 200 | 0.090526 | +5.478 |
| 267 | 0.139636 | +224.967 |
| 542 | 0.403857 | +89.607 |

这些差异是 NR 近似相对于精确空间动量的响应变化，不是对现有事件率施加的经验修正。固定 \(E_R\) 下，如果 \(I_6\) 和其他因子不变，微分截面的相对变化与 \(R_A\) 的相对变化相同。

### G.5 不要混淆空间 \(q^2\) 与不变量 \(-t\)

虽然 AFH 响应使用空间动量 \(q=|\mathbf q|\)，媒介子传播子使用的是四动量转移不变量：

\[
t=(P'-P)^2=E_R^2-q_{\rm exact}^2=-2m_AE_R.
\]

因此传播子分母

\[
m_V^2-t=m_V^2+2m_AE_R
\]

本身是精确的，并不意味着空间动量也必须满足 \(q^2=2m_AE_R\)。

这是本次审计最重要的区分：

- AFH 核响应：使用空间动量 \(q_{\rm exact}\)；
- 三体相空间、\(W_{\max}\)、\(v_{\min}\)：使用 \(q_{\rm exact}\)；
- 媒介子传播子：使用不变量 \(t=-2m_AE_R\)；
- \(q_{\rm NR}\)：仅是核反冲能量关系的非相对论近似。

### G.6 代码约定

当前统一约定：

- research/figure2_full_reproduction/rate_kinematics.py：精确 \(q_{\rm exact}\)，用于三体运动学；
- research/figure2_full_reproduction/eq6_kernel.py：精确 \(q_{\rm exact}\)，用于三体末态构造；
- research/figure2_full_reproduction/joint_xe131.py：AFH 响应插值使用精确空间 \(q_{\rm exact}\)；
- research/afh_default_density_xe131/recompute_afh_four_benchmarks.py：固定速度四组 benchmark 使用精确空间 \(q_{\rm exact}\)；
- research/afh_default_density_xe131/compute_four_benchmark_dsigma.py：同样使用精确空间 \(q_{\rm exact}\)；
- research/afh_default_density_natural_xenon_halo/run_afh_natural_xenon_halo_fold.py：默认 exact_spatial；nr_approx 仅用于近似对照；legacy_exact 保留为向后兼容别名。

若输入样本的 q 与所选约定不一致，程序会报错，不会静默复用不匹配的 \(R_A\)。

### G.7 机器可读结果

q 审计程序保存以下文件：

- research/afh_default_density_natural_xenon_halo/results/natural_xenon_q_convention_audit.csv：28 个天然氙样本；
- research/afh_default_density_natural_xenon_halo/results/xe131_afh_response_shift_NR_vs_exact.csv：NIST Xe-131 质量下的响应对照；
- research/afh_default_density_natural_xenon_halo/results/xe131_fixed_benchmark_q_comparison.csv：\(M_A=131u\) 下的固定 benchmark 对照；
- research/afh_default_density_natural_xenon_halo/results/q_convention_audit_summary.json：机器可读汇总。

当前完整 16807 行的七同位素原始响应表仅保留哈希和 28 个选定点样本。对于本附录所列的 selected-point exact-q 计算，28 个样本已足够；若要扩展到连续反冲谱，则仍需恢复完整 AFH v6.0 响应输入或官方源包。

### G.7.1 原生 AFH 响应验证的状态边界

Xe-131 AFH default response 的原生 Mathematica/Python 2401 点比较已通过，详见 research/afh_default_density_xe131/output/native_audit/。这不改变本附录对精确空间 q 与 NR 近似的结论，也不补齐 Xe-124/Xe-126 的 AFH density matrix 或完整天然氙连续谱。

### G.8 验收标准

| 项目 | 状态 | 说明 |
|---|---|---|
| AFH 的 \(q\) 定义 | 已核实 | \(q\) 是空间动量转移 |
| 精确质量壳关系 | 已推导 | \(q^2=2m_AE_R+E_R^2\) |
| 28 个天然氙样本 | 已核实 | 全部匹配 exact spatial q |
| Xe-131 NR 近似影响 | 已计算 | NIST 与 \(M_A=131u\) 两种质量约定均有对照 |
| 天然氙 halo fold | exact-q 基线 | 98 个同位素贡献、14 个总速率复现；最大总速率差异 \(2.67\\times10^{-12}\)，CI run 43044583357 通过 |
| 连续反冲谱 | 待完成 | 需要完整七同位素 AFH 响应输入 |
| 原生 Mathematica 复算 | 已完成 PASS | Wolfram 14.0.0；2401 点；最大相对差异 \(3.59\times10^{-9}\)；manifest 与 SHA-256 均已归档 |

