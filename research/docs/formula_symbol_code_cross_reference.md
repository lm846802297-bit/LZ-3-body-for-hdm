# 公式—符号—正文—程序—结果交叉引用索引

> 所属主报告：[09_afh_xe131_three_body_scattering_natural_xenon.md](09_afh_xe131_three_body_scattering_natural_xenon.md)  
> 当前主线集成分支：`research/afh-mainline-integration-20261113`（PR #27，目标 `main`）  
> 文档性质：可追溯性索引；P1-PhaseSpace 的数值验证范围和结果见独立审计报告，不改变振幅或 UV 模型假设。

## 1. 使用方法与统一约定

本索引为每个核心公式分配稳定编号 F1–F12。推荐沿以下路径阅读：

1. 从主报告相应小节读取物理定义和最终使用的公式；
2. 进入对应附录查看完整推导、约定和适用条件；
3. 检查表中列出的程序入口，确认公式实际由哪一段代码实现；
4. 检查结果文件及 metadata，确认数值输出、输入参数和验证边界。

主报告中的 Eq. (6) 是单一核同位素、固定入射速度下的微分截面。它不是天然氙事件率，也不是已经包含 LZ 探测器响应的观测谱。以下 F5、F10、F11 分别对应这三个不同层级，不能互相替代。

全项目微观运动学和矩阵元使用自然单位 \(\hbar=c=1\)，质量、能量和动量在程序内部以 GeV 表示。速度接口以 km/s 输入并转换为 \(\beta=v/c\)。天然氙速率输出单位为 events/(kg day keV)。LZ efficiency-weighted event yield 是无量纲预期事件数。

## 2. 核心公式追溯矩阵

| ID | 公式 / 物理任务 | 主报告位置 | 完整推导或定义 | 程序入口 | 主要归档结果 | 关键条件与边界 | 本轮状态 |
|---|---|---|---|---|---|---|
| F1 | 核反冲四动量、精确空间动量 \(Q\) 与不变量 \(t\) | §2、§12.1 | [附录 A，§A.1](appendices/09A_three_body_kinematics_amplitude.md)；[附录 G，§G.1–G.5](appendices/09G_recoil_momentum_convention_audit.md) | [rate_kinematics.py](../figure2_full_reproduction/rate_kinematics.py)：`momentum_transfer`；[eq6_kernel.py](../figure2_full_reproduction/eq6_kernel.py)：`limits`、`build_point` | [natural_xenon_q_convention_audit.csv](../afh_default_density_natural_xenon_halo/results/natural_xenon_q_convention_audit.csv)；[xe131_fixed_benchmark_q_comparison.csv](../afh_default_density_natural_xenon_halo/results/xe131_fixed_benchmark_q_comparison.csv) | 初态核静止、初末核均在质量壳上。AFH 使用空间动量 \(Q=|\mathbf q|\)；传播子使用 \(t=-2m_AE_R\)。两者不是同一个 \(q^2\)。  | 已验证 |
| F2 | 三体子系统边界、相空间开闭、\(m_{s,\max}\) 与最优 \(E_R^*\) | §2.4、§6.3 | [附录 A，§A.2–A.2.1](appendices/09A_three_body_kinematics_amplitude.md) | `eq6_kernel.py`：`limits`；`rate_kinematics.py`：`wmax_squared` | corrected benchmark CSV；逐速度阈值结果 | 最优反冲点只最大化运动学允许的标量质量，不代表速率峰值。 |
| F3 | 三体相空间分解、\((W^2,z,\phi_*)\) Jacobian 与 reduced kernel \(I_6\) | §2.5.1–2.5.9 | [附录 A，§A.3–A.4.2](appendices/09A_three_body_kinematics_amplitude.md) | [eq6_kernel.py](../figure2_full_reproduction/eq6_kernel.py)：`build_point`、`reduced_kernel`；[phase_space_convergence.py](../figure2_full_reproduction/phase_space_convergence.py)：(W^2/W/u^2) 映射与 raw-(d\Phi_3) 路径 | `phase_space_mapping_convergence.csv`、`phase_space_angular_convergence.csv`、`phase_space_threshold_convergence.csv`、`phase_space_li_prefactor_crosscheck.csv`；六项测试与 [P1 audit report](supplements/phase_space_convergence_audit_2026-11-14.md) | (I_6) 单位 GeV(^2)；代表点和阈值邻域收敛通过；近极点及完整连续反冲网格仍待验收。 |
| F4 | 前发射、后发射、干涉项及 \(\mathcal L_{00}\) Dirac trace | §2 中 \(\mathcal L_{00}\) 的定义；完整图结构在附录 | [附录 A，§A.5–A.6](appendices/09A_three_body_kinematics_amplitude.md) | [eq6_kernel.py](../figure2_full_reproduction/eq6_kernel.py)：`vertices`、`spin_trace`；[test_eq6_kernel.py](../figure2_full_reproduction/tests/test_eq6_kernel.py) | kernel 测试、四动量闭合与壳条件检查；积分阶数对照见附录 F.4 | 两张辐射图先在振幅层面相加，再平方；干涉项不能省略。当前 pole width 只放在 after 图可能接近极点的传播子中。  | 条件性验证 |
| F5 | 单同位素、固定速度微分截面 Eq. (6) | §2 Eq. (6)、§2.3 归一化推导；附录 H | [附录 A，§A.4.1–A.4.2、A.8](appendices/09A_three_body_kinematics_amplitude.md)；[主报告附录 H](09_afh_xe131_three_body_scattering_natural_xenon.md) | [eq6_kernel.py](../figure2_full_reproduction/eq6_kernel.py)：`reduced_kernel`；[run_afh_eq6_full_dsigma.wls](../afh_default_density_xe131/run_afh_eq6_full_dsigma.wls)；[compare_full_dsigma_mathematica.py](../afh_default_density_xe131/compare_full_dsigma_mathematica.py) | [历史四 benchmark 截面对照](../afh_default_density_xe131/output/figure2_four_benchmarks_AFH_GCN_JJ55_corrected.csv)；[原生完整截面 audit](../afh_default_density_xe131/output/NATIVE_MATHEMATICA_FULL_DSIGMA_AUDIT.md) | (R_A) 无量纲，(I_6) 为 GeV\(^2\)，故自然单位下 (d\sigma/dE_R) 为 GeV\(^{-3}\)。历史四 benchmark 表格复用已归档 (I_6)，不是完整 Mathematica 独立复算；新的端到端对照需固定相同宽度、求积阶数和 AFH PCHIP。 | **条件性验证：历史 Python 曲线；完整 Mathematica/Python 截面对照待完成** |
| F6 | AFH 谐振子变量、密度矩阵响应及物理归一化 \(R_A^{\rm phys}\) | §3.1–§3.3 | [附录 B，§B.1–B.4，特别是 B.2.1](appendices/09B_afh_v6_density_matrix_response.md)；[附录 C，§C.1–C.6](appendices/09C_afh_isoscalar_factor4_normalization.md)；[附录 G，§G.1–G.5](appendices/09G_recoil_momentum_convention_audit.md) | run_afh_default_xe131.py、run_afh_default_xe131.wls、verify_afh_xe131_native.wls、compare_afh_mathematica_python.py | Python response CSV；[native Mathematica CSV](../afh_default_density_xe131/afh_default_xe131_WM00_mathematica.csv)；[native comparison JSON](../afh_default_density_xe131/output/native_audit/afh_mathematica_python_comparison.json)；[native manifest](../afh_default_density_xe131/output/native_audit/afh_native_audit_manifest.json)；[audit record](../afh_default_density_xe131/output/native_audit/NATIVE_MATHEMATICA_AUDIT.md) | AFH v6.0 Xe-131 default，67 项密度矩阵，固定文献 \(b_A\)，2401 个 \(q\) 节点。原始 AFH isoscalar 零动量归一化 \(A^2/4\)，物理等质子等中子响应 \(R_A^{\rm phys}(0)=A^2\)；因子 4 只计一次。mpmath 与 Wolfram 14.0 原生对照均通过，最大相对差异 \(3.59\times10^{-9}\)；q=0 有限精度形状修正另为 \(1.0000825298\)。完整 AFH 天然氙连续谱仍未完成。 | 已验证（Xe-131 response-level） |
| F7 | 同位素核质量、天然丰度 \(x_A\) 与每 kg 靶核数 \(N_T\) | §6.2 | [附录 D，§D.1–D.5，特别是 D.1.1、D.3.1](appendices/09D_natural_xenon_isotope_target.md) | 天然氙 halo/spectrum runners | NIST isotope weights；natural-xenon metadata | \(N_T\) 使用完整九种天然同位素平均原子质量；AFH 速率只求和七种可用响应且不重归一化。 |
| F8 | 三体最小入射速度 \(v_{\min,A}\) | §6.3；阈值讨论见 §7 | [附录 A，§A.2](appendices/09A_three_body_kinematics_amplitude.md)；[附录 E，§E.2](appendices/09E_halo_velocity_vmin_folding.md) | [rate_kinematics.py](../figure2_full_reproduction/rate_kinematics.py)：`vmin_three_body_beta`；halo-fold runner 中的逐同位素阈值实现 | [vmin_by_isotope_at_101keV.csv](../afh_default_density_natural_xenon_halo/results/vmin_by_isotope_at_101keV.csv) | 来自 \(W_{\max,A}^2=(m_{\chi_1}+m_s)^2\)，是 \(\chi_1+A\to\chi_1+A+s\) 的三体阈值。不能替换为弹性或普通两体非弹性散射的标准 \(v_{\min}\)。  | 已验证 |
| F9 | 实验室系速度模长 PDF \(f_{\rm lab}(v)\) | §6.4 | [附录 E，§E.1–E.1.1](appendices/09E_halo_velocity_vmin_folding.md) | `shm_truncated_pdf`、`mb_untruncated_pdf` | halo_pdf_normalization.csv | 从银河系静止系三维截断 Maxwell 分布经 Galilean boost 和方向积分得到；速度模长 PDF 归一化为 1。 |
| F10 | 天然氙 halo-folded 微分事件率 \(dR/dE_R\) | §2.2、§6.3、§7 | [附录 D，§D.3–D.4](appendices/09D_natural_xenon_isotope_target.md)；[附录 E，§E.2–E.3.2](appendices/09E_halo_velocity_vmin_folding.md) | AFH selected-point / GCN-JJ55 continuous-spectrum runners | natural-xenon rates；isotope contributions | 由暗物质数密度、速度通量、单核截面和每 kg 靶核数推导；每个同位素单独使用阈值和 kernel。 |
| F11 | LZ 一维效率加权预期事件数 \(N_{\rm sig}^{\rm ROI}\) | §11.1、§11.4、§11.6 | 主报告 §11.6；附录 F.5 | `fold_lz_2026_rate_level.py` | LZ efficiency CSV；rate-level yield CSV | 一维效率是二维重建响应概率在 ROI 上的投影；不是二维 likelihood 或 90% CL 排除。 |
| F12 | 条件性 \(\chi_2\to\chi_1s\) pole width | §5、§7 的 width prescription | [附录 A，§A.5–A.6.1](appendices/09A_three_body_kinematics_amplitude.md) | [eq6_kernel.py](../figure2_full_reproduction/eq6_kernel.py)：`chi2_width_dirac_scalar` | benchmark metadata：`width_scheme`、`g2` | 从 Dirac 纯标量 Yukawa 振幅和二体相空间推导；仅适用于 Dirac、实标量、纯标量耦合及单一开放衰变道。 |

## 3. 符号、定义与单位表

### 3.1 暗物质与粒子物理参数

| 符号 | 定义 | 单位 / 约定 | 易混淆点 |
|---|---|---|---|
| \(\chi_1\) | 入射及末态稳定暗物质态 | 粒子标签 | 本过程前后均为 \(\chi_1\) |
| \(\chi_2\) | 暗物质内部中间态 | 粒子标签 | \(m_{\chi_2}=m_{\chi_1}+\Delta m\) |
| \(s\) | 辐射出的实标量 | 粒子标签 | 末态标量质量为 \(m_s\) |
| \(m_{\chi_1},m_{\chi_2}\) | 两个暗物质态质量 | GeV | 不要将 \(\Delta m\) 当作 \(m_{\chi_2}\) |
| \(\Delta m\) | 暗物质态质量劈裂 | GeV；benchmark 表常用 MeV | \(m_{\chi_2}-m_{\chi_1}\) |
| \(m_s\) | 末态标量质量 | GeV；benchmark 表常用 keV/MeV | 决定三体末态阈值 |
| \(m_V\) | 交换矢量媒介子质量 | GeV | 传播子分母为 \((m_V^2+2m_AE_R)^2\) |
| \(g_1,g_2,g_{VN}\) | 模型顶点耦合 | 无量纲 | \((g_1g_2g_{VN})^2\) 是 benchmark 截面耦合乘积；宽度方案还单独需要 \(g_2\) |
| \(\Gamma_{\chi_2}\) | 中间态 pole width | GeV | 当前采用条件性单通道宽度，不等于完整 UV 自能 |

### 3.2 三体运动学与积分量

| 符号 | 定义 | 单位 / 约定 | 易混淆点 |
|---|---|---|---|
| \(p^\mu,P^\mu\) | 入射暗物质和初态核四动量 | GeV | 核静止系 \(P^\mu=(m_A,\mathbf 0)\) |
| \(p'^\mu,P'^\mu,k^\mu\) | 末态暗物质、核和标量四动量 | GeV | 所有外腿满足各自质量壳条件 |
| \(q^\mu=P'^\mu-P^\mu\) | 核反冲四动量转移 | GeV | \(q^2=t=-2m_AE_R\) |
| \(Q=|\mathbf q|\) | 空间动量转移模长 | GeV | \(Q^2=2m_AE_R+E_R^2\)，不要写成四动量不变量 \(t\) |
| \(t\) | Mandelstam 型核动量转移不变量 | GeV\(^2\) | \(t=-2m_AE_R\) |
| \(E_R\) | 核反冲能量 | GeV（程序）；keV（报告表格） | \(1\) keV \(=10^{-6}\) GeV |
| \(E_\chi,p_{\chi_1}\) | 入射暗物质能量和三动量模长 | GeV | \(E_\chi=m_{\chi_1}\gamma\)，\(p_{\chi_1}=m_{\chi_1}\gamma\beta\) |
| \(\beta,\gamma\) | 入射速度除以光速、Lorentz 因子 | 无量纲 | \(\beta=v/(299792.458\ {\rm km/s})\) |
| \(K^\mu=p^\mu-q^\mu\) | \(\chi_1+s\) 子系统总四动量 | GeV | \(K^2=W^2\) |
| \(W^2\) | 子系统不变质量平方，三体积分变量 | GeV\(^2\) | \(W\) 是不变质量，\(W^2\) 才是积分变量 |
| \(W_{\min}^2,W_{\max}^2\) | 三体相空间积分边界 | GeV\(^2\) | 由末态阈值和固定 \(v,E_R\) 的运动学共同决定 |
| \(a_A\) | 推导三体阈值速度时引入的辅助量 | GeV | \(a_A=m_s+(m_AE_R+m_s^2/2)/m_{\chi_1}\) |
| \(\theta_q\) | 入射暗物质三动量与核反冲空间动量之间的夹角 | rad | 用于确定 \(W^2\) 的运动学边界；不等于子系统静止系中的 \(\theta_*\) |
| \(z=\cos\theta_*\) | \(K\) 静止系中的两体衰变极角余弦 | 无量纲，\([-1,1]\) | 不等于核反冲角 \(\cos\theta_q\) |
| \(\phi_*\) | \(K\) 静止系中的衰变方位角 | rad | 在 \(I_6\) 中按 \(2\pi\) 归一化平均 |
| \(\lambda_K,\lambda_{\rm dim}\) | Källén 函数及无量纲版本 | \(\lambda_K\): GeV\(^4\)；\(\lambda_{\rm dim}\): 无量纲 | \(I_6\) 中使用 \(\lambda_{\rm dim}\) |
| \(\mathcal L_{00}\) | 时间分量粒子侧自旋迹 | 无量纲 | 包含 before、after 和干涉项 |
| \(I_6\) | reduced three-body kernel | GeV\(^2\) | 不包含 Eq. (6) 已显式写出的整体前因子、核响应和媒介子分母 |

### 3.3 核响应与天然氙靶

| 符号 | 定义 | 单位 / 约定 | 易混淆点 |
|---|---|---|---|
| \(A,Z,J_A\) | 同位素质量数、质子数、核自旋 | 整数 / 自旋量子数 | Xe-131 为 \(A=131,Z=54,J_A=3/2\) |
| \(m_A\) | 目标核质量 | GeV | 天然氙使用逐同位素 NIST 核质量方案 |
| \(M_{\rm atom}(A)\) | 同位素原子质量 | u | \(m_A=[M_{\rm atom}(A)-54m_e]u\)，忽略电子结合能 |
| \(u,m_e\) | 原子质量单位、电子质量 | \(u=0.93149410242\) GeV；\(m_e=0.000548579909065\,u\) | 电子质量在此式中以 u 表示 |
| \(N_{\rm Av}\) | 阿伏伽德罗常数 | mol\(^{-1}\) | 用于将平均摩尔质量转换为每 kg 靶核数 |
| \(x_A\) | 天然氙同位素原子丰度 | 无量纲 | 使用原始丰度；当前 AFH 可用七种覆盖 0.998158，不重归一化 |
| \(\bar M_{\rm Xe}\) | 天然氙丰度加权平均原子质量 | g/mol | 用于每 kg 靶核数，不是单一同位素核质量 |
| \(N_T\) | 每 kg 天然氙中的靶核数 | kg\(^{-1}\) | \(N_T=N_{\rm Av}1000/\bar M_{\rm Xe}\) |
| \(b_A\) | 核谐振子长度 | fm 或 GeV\(^{-1}\) | AFH default 处方值，不是拟合参数；\(1\) fm \(=5.0677\) GeV\(^{-1}\) |
| \(y\) | AFH 无量纲谐振子变量 | 无量纲 | \(y=(Qb_A/2)^2\)，使用空间动量 \(Q\) |
| \(W_M^{00}\) | AFH 原始 isoscalar \(M\) 响应 | 按 AFH 约定 | 零动量原始归一化为 \(A^2/4\) |
| \(R_A^{\rm phys}\) | Eq. (6) 使用的物理相干核响应 | 无量纲 | \(R_A^{\rm phys}=16\pi W_M^{00}/(2J_A+1)\)，零动量为 \(A^2\) |
| \(q_{\rm exact}\) | 精确空间反冲动量 | GeV | \(\sqrt{2m_AE_R+E_R^2}\) |
| \(q_{\rm NR}\) | 非相对论小反冲近似 | GeV | \(\sqrt{2m_AE_R}\)，仅作独立近似对照 |

### 3.4 Halo、事件率与探测器量

| 符号 | 定义 | 单位 / 约定 | 易混淆点 |
|---|---|---|---|
| \(v,v_{\min,A},v_{\max}\) | 实验室系暗物质速度、同位素阈值速度、积分上限 | km/s | 截断 SHM 下 \(v_{\max}=776\) km/s |
| \(v_0,v_E,v_{\rm esc}\) | SHM 速度尺度、地球速度、银河系逃逸速度 | km/s | 当前基准为 220、232、544 km/s |
| \(f_{\rm lab}(v)\) | 实验室系速度模长 PDF | (km/s)\(^{-1}\) | \(\int dv\,f_{\rm lab}(v)=1\)，不是三维速度矢量 PDF |
| \(\rho_\chi\) | 局域暗物质质量密度 | GeV/cm\(^3\) | 当前基准 0.3 GeV/cm\(^3\) |
| \(c\) | 光速 | halo 积分中 \(v/c\) 用 km/s 的 \(c\)；通量前因子用 cm/s | 代码分别使用 \(299792.458\) km/s 与 \(2.99792458\times10^{10}\) cm/s |
| \(dR/dE_R\) | 每单位靶质量、时间和反冲能量的理论速率 | events/(kg day keV) | AFH 当前为 selected points；GCN/JJ55 有连续谱 |
| \(\epsilon_{\rm LZ}(E_R)\) | LZ final-ROI 一维效率 | 无量纲 | 不是完整二维 NEST 响应 |
| \(\mathcal E\) | 有效曝光 | kg day | 当前名义值 \(2.84\) tonne-year \(=1.03731\times10^6\) kg day |
| \(N_{\rm sig}^{\rm ROI}\) | efficiency-weighted 预期事件数 | 无量纲 | 当前为 rate-level 估计，不是 likelihood 或排除限 |

## 4. 近似、质量方案与适用范围对照

| 项目 | 当前默认 | 对照 / 非默认选项 | 必须保留的边界 |
|---|---|---|---|
| 空间反冲动量 | \(q_{\rm exact}=\sqrt{2m_AE_R+E_R^2}\) | \(q_{\rm NR}=\sqrt{2m_AE_R}\) | AFH 响应和三体运动学均使用 exact spatial q；NR 只作敏感性对照 |
| 传播子动量 | \(t=-2m_AE_R\) | 不用 \(Q^2\) 替代 \(t\) | \(Q^2=2m_AE_R+E_R^2\)，而 \(t=-2m_AE_R\) |
| AFH \(b_A\) | AFH 文献 default 处方 | 不拟合谷值 | 调节 \(b_A\) 会改变核响应形状，不能用于强行对齐 Figure 2 |
| AFH 归一化 | 物理响应 \(R_A(0)=A^2\) | 原始 AFH isoscalar \(A^2/4\) | 因子 4 只计入一次 |
| 同位素质量 | 天然氙 halo fold 使用 NIST 原子质量减去 54 个电子质量 | 固定 Figure-2 Xe-131 截面对照使用 \(M_A=131u\) | 两种质量方案各自有 metadata；不要把一套结果的质量输入与另一套 \(q\) 或阈值混用 |
| 同位素丰度 | 原始 \(x_A\)，可用 AFH 七同位素覆盖 0.998158 | 不把七种丰度重归一化到 1 | Xe-124/Xe-126 的缺失贡献保持显式边界 |
| 速度分布 | 截断 SHM，\(v_{\max}=776\) km/s | 不截断 boosted MB 仅作尾部诊断 | 固定 \(v=800\) km/s 的 Figure-2 截面对照不是截断 SHM halo rate |
| 方位角 | \(I_6\) 中对 \(\phi_*\) 作归一化平均 | 不使用未归一化方位角积分 | 否则 Eq. (6) 的整体相空间前因子需要重新定义 |
| 核流 | 靶核时间分量 leading non-relativistic 近似 \(J_A^0\simeq2m_A\) | 更高阶核流修正不在当前 Eq. (6) 基准中 | 该近似已与 \(R_A\) 和整体前因子定义绑定 |
| \(\chi_2\) 宽度 | 条件性 pole width | zero-width / running-width diagnostic | 不等同于完整自能；running width 是诊断 ansatz |
| LZ 响应 | 一维 final-ROI efficiency rate fold | 完整二维 NEST + likelihood 尚未实现 | 不包含能量分辨卷积、二维 PDF、背景 nuisance 和 profile likelihood |

## 5. 结果文件和复现入口总表

| 计算层 | 主输出 | 元数据 / 验收 |
|---|---|---|
| AFH Xe-131 响应 | `research/afh_default_density_xe131/output/afh_default_xe131_WM00.csv` | `metadata.json`、`mpmath_full_grid_summary.json`、`minima.csv` |
| AFH/GCN/JJ55 四 benchmark 截面 | `research/afh_default_density_xe131/output/figure2_four_benchmarks_AFH_GCN_JJ55_corrected.csv` | `four_benchmark_metadata.json`；共享既有 \(I_6\)，不是重新独立计算 640 个三体积分 |
| AFH 天然氙 selected-point rate | `research/afh_default_density_natural_xenon_halo/results/natural_xenon_halo_rates.csv` | `metadata.json`、`isotope_halo_contributions_compact.csv`、`speed_quadrature_crosschecks.csv` |
| GCN/JJ55 天然氙连续谱 | `research/figure2_full_reproduction/results/natural_xenon_continuous_spectrum/<benchmark>/natural_xenon_continuous_spectrum.csv` | 每个 benchmark 子目录的 `metadata.json` 与 `quadrature_crosschecks.csv` |
| LZ 效率输入 | `research/lz_detector_response/lz_2026_extended_nr/lz_2026_nr_efficiency_digitized.csv` | 同目录的 `lz_2026_nr_efficiency_metadata.json` 和 `lz_2026_figS2.svg` |
| LZ rate-level yields | `research/lz_detector_response/lz_2026_extended_nr/rate_level_event_yields/lz_2026_rate_level_event_yields.csv` | 同目录的 `lz_2026_rate_level_metadata.json` |

复现命令以[附录 F，§F.3](appendices/09F_numerical_validation_reproduction.md)为准。建议先运行 Eq. (6) kernel tests，再运行 AFH response、halo fold、continuous-spectrum 和 LZ rate-level workflows。不要仅凭某个 workflow 成功，就把未被该 workflow 覆盖的物理层级标记为已验证。

## 6. 维护规则

1. 新增或改变核心公式时，必须同时更新本索引中的公式编号、主报告位置、附录推导、程序入口、结果文件和近似条件。
2. 变量改名时，先更新代码及机器可读 metadata，再同步主报告、附录和本符号表；不得只改正文显示名称。
3. 新增质量方案、halo 模型、宽度方案、\(q\) 约定或积分阶数时，必须生成独立输出和 metadata，不覆盖既有归档。
4. 公式相同但输入假设不同的计算必须分开登记。例如固定速度 \(v=800\) km/s 截面、截断 SHM halo fold 和不截断 MB 尾部诊断不能合并成同一个“预测”。
5. 结果状态只采用“已完成”“selected-point”“连续谱”“rate-level”及“待完成”等可核实标签；软件测试通过不自动代表完整物理模型或实验 likelihood 已验证。
6. 本索引与主报告、附录 A–G 同步维护；若程序路径或输出路径发生变化，必须先验证新路径存在，再修改链接。



## 7. 本轮验证状态口径（2026-11-14）

- **已验证：** 在明确声明的输入、单位和适用范围内，公式、程序与归档结果已完成可重复的数值闭合；不代表超出该范围的模型扫描也已验证。
- **条件性验证：** 核心实现与代表性回归检查通过，但仍受独立推导、参数覆盖、核模型输入或物理假设限制。
- **未完成：** 尚无对应的数值结果或所需物理输入；不得以 CI 通过、脚本存在或其他核模型结果替代。

F1–F12 的逐项状态见第 2 节。F6 的 AFH 振子长度处方说明见 B.2.1；F7 的核质量与靶数推导见 D.1.1、D.3.1，F9 的实验室速度 PDF 推导见 E.1.1，F10 的通量折叠推导见 E.3.1，F12 的条件性宽度推导见 A.6.1。F3 的三体相空间 Jacobian 与整体 \\(256\\pi^3\\) 因子已从 Lorentz-invariant 测度独立推导；P1-PhaseSpace 进一步完成四组 fixed-speed benchmark、五个阈值邻域速度点、三种积分映射、代表点角积分和 raw-\\(d\\Phi_3\\) 前因子数值对照，CI run [43491572746](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43491572746) 复算四组 CSV 并通过。近极点与完整连续反冲网格的 \\(I_6\\) 收敛仍需单独验收。F6 的 Python/60 位 mpmath 网格与原生 Wolfram/Mathematica 2401 点运行均已通过；AFH-7/Hybrid-9 连续谱与一维高能尾部效率折叠现已归档；二维 NEST/背景/profile-likelihood 仍未实现。完整 Eq. (6) 的 Mathematica–Python 截面对照仍待最后执行。


## 8. Phase II high-energy tail and full-cross-section validation status

- AFH-7 and Hybrid-9 natural-xenon continuous spectra: archived with isotope-resolved exact-spatial-(q) kernels and high-order quadrature checks.
- Candidate-window tail (225\text{--}269.9\,\mathrm{keV}): archived for AFH-7, Hybrid-9, Helm-9, GCN and JJ55 in `afh_default_density_natural_xenon_halo/results/high_energy_tail_model_sensitivity_2026-11-14.csv`.
- The tail comparison is one-dimensional efficiency-weighted rate-level output. It is not a detector-level reconstructed spectrum or a profile likelihood.
- Full Eq. (6) cross-section implementation: `afh_default_density_xe131/run_afh_eq6_full_dsigma.wls`; independent Python comparator: `afh_default_density_xe131/compare_full_dsigma_mathematica.py`.
- The native full-(I_6)/(d\sigma_A/dE_R) run remains the final Mathematica verification gate; no PASS is claimed before its CSV and comparator metadata are inspected.
