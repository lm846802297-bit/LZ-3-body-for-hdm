# Figure 2 三体暗物质计算：科学结果状态表

日期：2026-11-14  
本表按“当前可证明的范围”给状态，不把某个局部 benchmark 的通过推广成整个模型或整条连续谱均已验证。

## 1. 状态定义

| 状态 | 判定标准 |
|---|---|
| **已验证** | 公式、代码和输入约定在明确范围内一致，并有独立解析推导、数值对照或可复现检查支撑 |
| **部分验证** | 主要链路已有结果和检查，但仍缺输入覆盖、独立实现、模型定义或更高层物理环节 |
| **待补输入** | 计算方法可以继续，但缺少必要的原始物理输入或模型定义 |
| **尚未完成** | 研究任务尚未执行到可判断正确性的阶段，不能给出完成性结论 |

## 2. 粒子物理与三体运动学

| 子任务 | 当前状态 | 已有证据 | 尚存边界 |
|---|---|---|---|
| vector–vector 分支的两张辐射图 | **部分验证** | 主报告 §1.1–1.2、附录 A.5；`eq6_kernel.py` 的 before/after propagator 和完整振幅相加 | 当前按 Dirac、实耦合实现；原模型未完全固定 Dirac/Majorana 与复耦合相位 |
| Dirac \(L_{00}\) trace 的程序实现 | **已验证（限定 Dirac 基准）** | 显式自旋求和与 Dirac trace 对照；before、after、interference 三项恢复完整迹；450 keV pointwise benchmark 与回归测试 | 不能自动外推为 Majorana 外部态 |
| \(\chi_2\) 条件性 pole width | **部分验证** | 附录 A.6 的 Dirac–scalar 两体衰变推导；代码宽度函数 | 依赖纯 scalar Yukawa、实标量、单一开放衰变道；不是完整自能 |
| \(q^\mu,t,Q\) 运动学关系 | **已验证** | 核质量壳解析推导；`rate_kinematics.py` 与 `joint_xe131.py` 使用 exact spatial \(Q\) | fixed-speed Xe-131 与 natural-xenon 使用不同且已记录的核质量输入方案 |
| \(W_{\min},W_{\max}\) 与三体相空间开放条件 | **已验证** | 主报告 §2.4、附录 A.2；`eq6_kernel.limits` 与 `rate_kinematics.wmax_squared` 一致 | 不是对任意 UV 模型和任意传播子方案的验证 |
| \(W^2,z,\phi_*\) 相空间 Jacobian 与 \(256\pi^3\) | **已验证（解析层）** | 正文 §2.5.1–2.5.8、附录 A.4.1–A.4.2；独立分解 \(d\Phi_3\)、flux、azimuthal average；\([I_6]={\rm GeV}^2\) 维度检查 | 解析结论限定于未极化相干靶和 leading \(J_A^0\) 近似；数值收敛另列如下 |
| \(I_6\) 数值求积收敛（P1-PhaseSpace） | **部分验证（四个固定速度点和阈值邻域）** | 线性 \(W^2\)、线性 \(W\)、threshold-\(u^2\) 对照；四组 benchmark、五个 \(v_{\min}\) 邻域点；角积分阶数扫描；raw-\(d\Phi_3\) 与 Eq. (6) 截面比为 1；六项回归测试和 CI run [43491572746](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43491572746) 通过 | 未覆盖近传播子极点窄峰、不同宽度处方系统比较、完整连续反冲网格、halo fold 或 detector likelihood |
| 三体 \(v_{\min}\) 闭式公式 | **已验证** | 从 \(W_{\max}=m_{\chi_1}+m_s\) 独立推导；64 组输入与独立求根最大 \(|\Delta\beta|=3.89\times10^{-13}\) | 仍需对新增质量区间和完整连续谱网格做专门数值检查 |
| 450 keV pointwise \(L_{00}\) benchmark | **已验证（单点数值范围）** | \(48\times40\times24\) 求积、run manifest、局部验证记录、SHA-256 manifest | 单点 kernel 结果，不代表整条 \(d\sigma/dE_R\)、halo-fold 或 LZ 事件数 |
| 固定速度 Xe-131 \(d\sigma/dE_R\) 曲线 | **部分验证** | 105 个内部能量点、GCN/JJ55、metadata 与 SHA-256 校验 | 与 450 keV pointwise \(L_{00}\) 不同；端点外推/积分和 halo-fold 不包含在该曲线内 |

## 3. AFH 核响应与核靶输入

| 子任务 | 当前状态 | 已有证据 | 尚存边界 |
|---|---|---|---|
| AFH v6.0 Xe-131 67 项密度矩阵提取 | **已验证（source + translation）** | 官方 v6.0 来源哈希、67 项逐项解析、CSV 与 source translation 对照；`v6/dmformfactor-V6.m` 已提交 | 原始 ZIP 仍为 checksum-only provenance；完整七同位素响应表未提交 |
| AFH Xe-131 2401 点响应 | **已验证（限定 response-level）** | 0–0.6 GeV、2401 节点；60 位 mpmath 与 Wolfram 14.0.0 原生 Mathematica/Python 逐点比较；四种响应量全部通过，最大相对差异 \(3.59087\times10^{-9}\) | 仅验证 Xe-131 AFH response-level，不代表三体 kernel、天然氙连续谱或 LZ likelihood |
| AFH factor-of-four 物理归一化 | **已验证（当前 AFH v6.0 接口约定）** | raw \(A^2/4\)；setter \(c_{\rm set}=2g_{VN}\)；physical \(R_A(0)=A^2\)；代码不重复乘 4；源论文已修正 | 若更换 AFH 版本或响应接口，必须重新核对 setter 约定 |
| AFH Xe-131 响应极小值 | **部分验证** | 固定文献 \(b_A\)、精确空间 \(q\)、AFH default 67 项矩阵，三个 Figure 2 范围内的主要极小值已提取 | 这些是核响应极小值，不自动等于完整截面或 halo 事件率极小值 |
| AFH 七同位素 selected-point 响应 | **部分验证** | 七种可用同位素；28 个 halo-fold 样本；另有 56 个 NIST/AME2020 direct exact-\(q\) 响应点的 60 位 mpmath 检查 | 不是连续响应网格；完整 16807 行响应表未提交 |
| Xe-124、Xe-126 AFH default 密度矩阵 | **AFH v6.0 default dispatch 未提供** | 官方源文件第 1555–1597 行只列出 128、129、130、131、132、134、136；124/126 进入通用回退；新增静态 dispatch 回归测试 | 需独立、可追溯的核结构密度矩阵；0.1842% 原子丰度不是事件率误差上界 |
| 原始 Figure 2 的靶核定义 | **待补输入** | 已区分 Xe-131 固定靶诊断和 LZ 天然氙扩展 | 原稿未充分说明单一 Xe-131 还是天然氙混合物 |

## 4. 天然氙、halo 与探测器

| 子任务 | 当前状态 | 已有证据 | 尚存边界 |
|---|---|---|---|
| 天然氙靶核数与同位素丰度 | **已验证** | NIST 同位素输入；完整平均原子质量用于 \(N_T\)；原始丰度求和不重新归一化 | AFH 速率求和仅包括七种有响应的同位素 |
| AFH 天然氙 halo selected points | **部分验证** | 98 个逐同位素贡献、14 个总速率点；exact-spatial-\(q\)；kernel 与速度求积交叉检查；对归档总速率最大相对差异 (2.67\times10^{-12}) | 仍只使用 28 个 AFH response samples；不是连续 AFH 天然氙谱 |
| AME2020 direct exact-\(q\) selected-point 对照 | **部分验证** | 七同位素选定点输出、metadata 和独立 SHA-256 manifest | Xe-131-only hybrid 不等于完整 AME2020 七同位素重算 |
| GCN/JJ55 天然氙连续谱 | **已验证（限 GCN/JJ55 谱层）** | 四组 benchmark 连续输出、逐 benchmark metadata、quadrature crosschecks | 不是 AFH 连续谱；也不是探测器重建谱 |
| halo 模型系统扫描与年度调制 | **尚未完成** | 当前有截断 SHM 基准和 untruncated MB 尾部诊断 | 尚未进行完整 \(v_0,v_E,v_{\rm esc}\) 系统扫描或年度调制 |
| LZ 2026 一维效率折叠 | **部分验证** | 2.84 tonne-year、5.4–269.9 keV ROI；分段线性乘积解析积分；稠密梯形交叉检查 | 仅 rate-level yield；没有二维信号 PDF、NEST nuisance、背景 likelihood |
| LZ 二维 detector likelihood / profile likelihood | **尚未完成** | 已有一维 efficiency 输入和 rate-level output | 尚无完整 \(S1_c\)–\(\log_{10}S2_c\) response、背景 PDF 与 nuisance covariance |

## 5. 数据完整性与文档一致性

| 子任务 | 当前状态 | 已有证据 | 尚存边界 |
|---|---|---|---|
| Figure 2 结果总索引 | **已验证（当前归档范围）** | [机器可读总清单](figure2_results_master_index_2026-11-13.json)：9 组、60 个文件条目，含 SHA-256、参数和用途，并纳入原生 Mathematica 输出 | 对外部未提交输入只保留 checksum provenance，不能将其标记为已下载/可复现 |
| AFH response sample SHA-256 | **已验证（PR #27 CI）** | 真实 64 位 SHA-256 与 28 点输入文件一致；archive validator 已检查 sample digest、exact-spatial-q、98 个同位素贡献和 14 个总速率点 | GitHub Actions run `43458906653` 的 archived-sample/SHA-256/exact-q 步骤通过；连续 AFH 谱仍未完成 |
| 原始论文 AFH response 公式 | **已修正** | `paper-source/main.tex` 改为 factor 4 physical mapping 和 exact spatial \(q\)；`paper-source/SHA256SUMS` 同步 | 合并后仍需在正式 Overleaf / PDF 构建中检查排版 |
| 主报告—附录 A–G—代码公式索引 | **部分验证** | F1–F12 公式索引、附录 A–G、代码入口和主报告已交叉检查 | 仍需按最终固定的 Dirac/Majorana 模型约定做一轮完整 UV 层复核 |

## 6. 不得混淆的四组结果

1. **AFH Xe-131 核响应**：只描述核结构 \(R_A(Q)\)，不是散射截面。
2. **四组 \(v=800\) km/s 固定速度曲线**：用于 Figure 2 核响应替换诊断；该速度高于截断 SHM 的 \(776\) km/s。
3. **450 keV pointwise \(L_{00}\)** 与 **450 keV fixed-speed \(d\sigma/dE_R\)**：前者是单点 Dirac trace / \(I_6\) 检查，后者是整条固定速度曲线，求积、核模型和宽度约定并不相同。
4. **GCN/JJ55 连续天然氙谱与 LZ 一维效率折叠**：连续谱来自 GCN/JJ55；一维 efficiency fold 不能标记为 AFH 连续谱或完整 LZ likelihood。

## 7. 下一阶段的关闭条件

- **P0 关闭条件：** 总索引中的每个已提交输入/输出都有 64 位 SHA-256；外部输入和缺失文件明确标注 checksum-only / missing；每个 benchmark 都能追溯到参数和结果。
- **P1 关闭条件：** 原始拉格朗日量、主报告、附录 A–G、代码和单位约定无未解释的符号冲突；Dirac/Majorana 与宽度模型的边界由物理输入明确固定。
- **P2 关闭条件：** 每个科学结论都有状态、证据、输入缺口和适用范围；任何 selected-point、fixed-speed 或 rate-level 结果都不被表述为更高层的完整验证。

当前 P0 总索引已建立，P1 已修正公式和 provenance 不一致；Xe-131 原生 Mathematica/Python 2401 点响应验证已完成。P1-PhaseSpace 的代表点和阈值邻域数值收敛及 raw-\(d\Phi_3\) 前因子对照也已通过本地六项测试和 CI 复算。剩余开放项集中在模型定义、近传播子极点积分、完整连续反冲网格、Xe-124/Xe-126 AFH 输入、完整 AFH 连续谱，以及完整 LZ detector likelihood。
