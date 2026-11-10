# LZ 3-body dark matter interpretation

本仓库研究一种通过暗物质三体辐射过程解释 LZ 高能氙核反冲候选事件的模型：

\[
\chi_1 + A \longrightarrow \chi_1 + A + s .
\]

暗物质初态和末态均为 \(\chi_1\)，散射过程中通过虚中间态 \(\chi_2\) 传播并辐射一个轻标量 \(s\)。研究目标不是预设该机制能够解释实验，而是检验其能否同时满足：

1. 在 LZ 候选事件附近产生足够的高能核反冲；
2. 不在低能区及高能侧带产生过多事件；
3. 与暗物质遗迹丰度、标量衰变及额外暗辐射约束相容。

## 实验动机

LZ Collaboration 在 2.84 tonne-year 曝光的扩展核反冲分析中报告了一个与核反冲相符的候选事件：

\[
E_R = 248 \pm 23_{\rm stat} \pm 23_{\rm sys}\ {\rm keV}.
\]

该结果相对于背景假设的全局显著性为 \(2.6\sigma\)，最大局部显著性为 \(3.4\sigma\)。这不是暗物质发现。实验分析将核反冲能量窗口扩展到约 270 keV。

实验原文：arXiv:2609.02823  
公开数据：<https://doi.org/10.17182/hepdata.182472.v1>

## 模型的两个候选实现

### A. Vector–vector 基准

\[
\mathcal L_{\rm int} =
g_1 V_\mu\bar\chi_2\gamma^\mu\chi_1
+g_2s\bar\chi_2\chi_1+\mathrm{h.c.}
+g_{Vq}V_\mu\sum_q\bar q\gamma^\mu q .
\]

在通用夸克矢量耦合假设下，草稿采用
\(g_{VN}=3g_{Vq}\)。当前草稿中的式 (5)–(8) 和相应的核响应计算属于这一分支。

### B. Scalar–pseudoscalar 候选

草稿还列出

\[
\mathcal L_{\rm int} =
g_1\phi\bar\chi_2\chi_1
+g_2s\bar\chi_2\chi_1+\mathrm{h.c.}
+i g_{\phi N}\phi\sum_{N=p,n}\bar N\gamma^5N .
\]

这一分支尚未给出对应的完整振幅、核响应、截面和参数扫描。不能直接把 vector–vector 分支的核响应公式移植过来。

## 当前研究状态（2026-11-10）

这是一个进行中的研究草稿，不是已经完成的 LZ 拟合。

- 已有：vector–vector 模型的两张树图、振幅结构、三体相空间积分式、核响应函数写法，以及一个参数化的谱图和二维扫描图。
- 已有：标量 \(s\) 与有效无质量 Majorana 无菌中微子 \(N_s\) 的衰变模型，以及从重粒子冻结出后到标量衰变的矩方程框架。
- 草稿给出一个参考计算结果：\(\Delta N_{\rm eff}\simeq0.043\)（MB 处理），并报告一个量子平衡热力学交叉检查约为 \(0.046\)。该数值只属于草稿所称的参考 benchmark，尚需补全 benchmark 输入和独立复核。
- 未完成：完整 LZ 探测器响应、事件数归一化、背景和侧带似然、loop-induced \(2\to2\) 散射、完整遗迹丰度与直接探测参数匹配，以及最终宇宙学约束扫描。

## 文档导航

- [模型、三体振幅与 Breit–Wigner 宽度](docs/01_model_and_amplitude.md)
- [LZ 数据、事件率与统计重铸路线](docs/02_lz_recast.md)
- [冻结出后演化与 \(\Delta N_{\rm eff}\)](docs/03_cosmology.md)
- [草稿审计、未解决问题与执行路线](docs/04_audit_and_roadmap.md)
- [参考文献与数据来源](docs/05_references.md)

## 研究纪律

1. 将实验候选事件称为 candidate/event of interest，不称为 discovery。
2. 区分理论真核反冲谱 \(dR/dE_R\)、探测器卷积后的重建谱，以及最终的事件似然。
3. 将 vector–vector 与 scalar–pseudoscalar 视为两个独立模型分支，除非完成明确的统一推导。
4. 只有在说明自由度、统计构造和 nuisance treatment 后，才把参数扫描边界称为置信区间。
5. 对共振区同时报告有限宽度、零宽度和自能改进方案的差异。
6. 不把尚未执行的计算写成已验证结论。
