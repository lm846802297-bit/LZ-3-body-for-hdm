# Figure 2 三体暗物质计算：物理公式交叉审查

日期：2026-11-13  
审查对象：`paper-source/main.tex`、主报告、附录 A–G、Eq. (6) kernel、AFH 响应生成与自然氙 halo-fold 程序。  
审查原则：解析推导、代码实现、输入约定和数值验证分别判定；其中一项通过不自动代表其余层次通过。

## 1. 审查结论摘要

本轮完成了当前 vector–vector、Dirac 外部态基准下的主要公式交叉审查。Eq. (6) 的三体相空间、\(256\pi^3\) 前因子、精确反冲动量、三体 \(v_{\min}\) 和天然氙速率单位链相互一致。发现并修正了两项真实文档/完整性问题：

1. **AFH factor-of-four 与 exact-\(q\) 定义：** 原始 `paper-source/main.tex` 把 AFH raw isoscalar response 的 \(4\pi W_M^{00}/(2J_A+1)\) 与物理 \(R_A(0)=A^2\) 并列，且将 \(y=b_A^2m_AE_R/2\) 写成无条件定义。这与 AFH v6.0 raw 输出不一致。现已将物理 response 改为 \(16\pi W_{M,\mathrm{AFH,v6}}^{00}/(2J_A+1)\)，并将 \(y\) 改为 exact spatial-\(q\) 定义。
2. **SHA-256 字段误用 Git blob SHA-1：** 天然氙 metadata 的 `response_sample_sha256` 曾是 40 位 Git blob SHA-1，却标记为 SHA-256。现已换成实际文件的 64 位 SHA-256，并在 archive validator 与后续 runner 中加入自动检查。

本轮没有改变三体振幅代码、核响应数值表或已归档物理结果。当前结果仍受 Dirac/Majorana 模型定义、条件性 \(\chi_2\) 宽度、AFH 缺失同位素和完整 LZ likelihood 等边界限制。

## 2. 公式—文档—代码对照表

| 审查对象 | 主报告 / 附录 | 代码实现 | 审查结论 |
|---|---|---|---|
| vector–vector 相互作用与两张辐射图 | 主报告 §1.1–1.2；附录 A.5–A.6；`paper-source/main.tex` | `eq6_kernel.py`: `vertices`, `spin_trace` | 当前 Dirac、实耦合基准下结构一致；Dirac/Majorana 和完整 CP/手征约定仍未由原模型文本唯一固定 |
| \(q^\mu,t,Q\) 的定义 | 主报告 §1.3；附录 G；附录 B.2 | `rate_kinematics.py`: `momentum_transfer`; `joint_xe131.py`: `NuclearResponse.at_recoil` | 一致：AFH 用空间 \(Q\)，传播子用 \(t\) |
| \(W_{\min},W_{\max}\) 与 Källén 因子 | 主报告 §2.4；附录 A.2–A.4 | `eq6_kernel.py`: `limits`, `lambda_dimensionless`, `build_point` | 解析式与实现一致 |
| \(L_{00}\) 的 Dirac trace 和干涉 | 主报告 §2.3；附录 A.5 | `eq6_kernel.py`: `spin_trace` | 自旋平均、末态求和、两图相干相加一致；适用范围限于 Dirac 基准 |
| \(256\pi^3\) 前因子 | 主报告 §2.5；附录 A.4.1 | `eq6_kernel.py` 的 \(I_6\) 与 `joint_xe131.py` 的 Eq. (6) 前因子 | 独立相空间推导通过 |
| AFH factor 4 与 \(R_A(0)\) | 主报告 §3.2–3.3；附录 B、C | AFH response CSV；`compute_four_benchmark_dsigma.py`; `recompute_afh_four_benchmarks.py` | raw-to-physical 映射一致；已修正源论文 |
| 三体 \(v_{\min}\) | 主报告 §6.3；附录 E.2 | `rate_kinematics.py`: `vmin_three_body_beta` | 解析推导一致；独立求根数值对照通过 |
| 天然氙速率与单位 | 主报告 §6–7；附录 D、E | `run_natural_xenon_halo_fold.py`; `run_afh_natural_xenon_halo_fold.py` | 通量、靶数、丰度、单位换算一致；AFH 仍为 selected points |
| LZ 一维效率折叠 | 主报告 §11.6；LZ rate-level metadata | `fold_lz_2026_rate_level.py` | 解析分段积分与稠密梯形交叉检查一致；不等于二维 likelihood |

## 3. 粒子物理：相互作用、内部传播子与自旋振幅

### 3.1 当前计算分支的相互作用

Eq. (6) 的当前数值 kernel 对应 vector–vector 分支：
\[
\mathcal L_{\rm int}\supset
\left(
g_1V_\mu\bar\chi_2\gamma^\mu\chi_1
+g_2s\bar\chi_2\chi_1+\mathrm{h.c.}
\right)
+g_{Vq}V_\mu\sum_q\bar q\gamma^\mu q.
\]
对普适轻夸克矢量电荷，低能核子匹配为
\[
g_{VN}=3g_{Vq}.
\]
这个因子 3 来自核子三个价夸克的矢量数荷；它与 AFH isoscalar response 的因子 4 完全不同。

暗扇区顶点是非对角的，因此外部态为
\[
\chi_1+A\to\chi_1+A+s,
\]
\(\chi_2\) 只出现在内部费米子传播子中。标量发射前、后的两张图分别为
\[
\Gamma_b^\mu=
\frac{\gamma^\mu(\slashed p-\slashed k+m_{\chi_2})}
{(p-k)^2-m_{\chi_2}^2},
\qquad
\Gamma_a^\mu=
\frac{(\slashed p'+\slashed k+m_{\chi_2})\gamma^\mu}
{W^2-m_{\chi_2}^2+i m_{\chi_2}\Gamma_{\chi_2}}.
\]
代码使用 \(\Gamma^\mu=\Gamma_b^\mu+\Gamma_a^\mu\)，再计算完整迹；交叉项不能丢弃。

在 \(m_{\chi_2}>m_{\chi_1}>m_s\) 下，
\[
(p-k)^2\le(m_{\chi_1}-m_s)^2<m_{\chi_2}^2,
\]
所以 before 图不能到达 \(\chi_2\) 极点。after 图的内部不变量是 \(W^2=(p'+k)^2\)，只有它可能接近极点。全局要求
\[
W_{\max}<m_{\chi_2}
\]
是参数空间筛选条件；kernel 本身不会对所有任意输入自动保证这一条件。

### 3.2 Dirac trace 与模型边界

当前实现采用
\[
\mathcal L_{00}
=\frac12\operatorname{Tr}
\left[
(\slashed p'+m_{\chi_1})\Gamma^0
(\slashed p+m_{\chi_1})\overline\Gamma^{\,0}
\right],
\qquad
\overline\Gamma^{\,0}=\gamma^0(\Gamma^0)^\dagger\gamma^0.
\]
这里 \(1/2\) 是初态 Dirac 自旋平均，末态自旋求和由完备关系完成。代码中的 `spin_trace` 分别计算 before、after 和完整振幅；干涉项由完整迹减去两个单图平方得到。

当前计算隐含实耦合约定；若 \(g_1,g_2\) 有一般复相位，两个图的耦合因子和相对相位必须从完整拉格朗日量重新保留。原始模型文本也没有唯一固定 \(\chi_{1,2}\) 是 Dirac 还是 Majorana。因此当前数值结果不能自动外推为 Majorana 版本。

条件性宽度
\[
\Gamma_{\chi_2\to\chi_1s}
=\frac{|g_2|^2}{16\pi m_{\chi_2}^3}
\sqrt{\lambda_K(m_{\chi_2}^2,m_{\chi_1}^2,m_s^2)}
\left[(m_{\chi_2}+m_{\chi_1})^2-m_s^2\right]
\]
仅适用于 Dirac 费米子、实标量、纯 scalar off-diagonal Yukawa 和唯一开放衰变道。它不是完整自能或 Dyson-resummed 传播子的替代品。

## 4. 精确反冲动量：空间 \(Q\) 与不变量 \(t\)

令靶核初态静止：
\[
P^\mu=(m_A,\mathbf0),\qquad
P'^\mu=(m_A+E_R,\mathbf q),\qquad
q^\mu=P'^\mu-P^\mu.
\]
由初末核质量壳条件，
\[
q_\mu q^\mu=t=-2m_AE_R.
\]
但 AFH 核响应使用空间动量模长
\[
Q=|\mathbf q|=\sqrt{2m_AE_R+E_R^2},
\qquad Q^2=E_R^2-t.
\]
因此
\[
(m_V^2-t)^{-2}=(m_V^2+2m_AE_R)^{-2}
\]
进入传播子，而
\[
y=(b_AQ/2)^2
\]
进入 AFH 响应。代码中的 `momentum_transfer`、`NuclearResponse.at_recoil` 和三体 `limits` 都使用 exact spatial \(Q\)。NR 近似 \(\sqrt{2m_AE_R}\) 仅作为敏感性对照，不应与传播子不变量 \(t\) 混写。

固定速度 Xe-131 曲线采用 \(M_A=131u\)，天然氙折叠采用逐同位素 NIST 核质量。这是两条计算链明确记录的质量输入差异，不是同一结果中混用两种 \(m_A\)。

## 5. 三体相空间与 \(256\pi^3\) 前因子独立推导

令
\[
K=p'+k=p-q,\qquad K^2=W^2.
\]
三体相空间按子系统不变质量分解：
\[
d\Phi_3
=\frac{dW^2}{2\pi}
d\Phi_2(p+P;P',K)
d\Phi_2(K;p',k).
\]
初态通量不变量为
\[
\Lambda_{\rm in}
=\sqrt{\lambda_K((p+P)^2,m_{\chi_1}^2,m_A^2)}
=2m_Ap_{\chi_1}.
\]
第一段两体相空间在积分掉 recoil azimuth 后满足
\[
\frac{d\Phi_2}{dt}=\frac{1}{8\pi\Lambda_{\rm in}},
\qquad
\left|\frac{dt}{dE_R}\right|=2m_A,
\]
故
\[
\frac{d\Phi_2(p+P;P',K)}{dE_R}
=\frac{m_A}{4\pi\Lambda_{\rm in}}
=\frac{1}{8\pi p_{\chi_1}}.
\]
第二段两体相空间在 \(K\) 静止系为
\[
d\Phi_2(K;p',k)
=\frac{|\mathbf k_*|}{16\pi^2W}dz\,d\phi_*
=\frac{\sqrt{\lambda_{\rm dim}}}{32\pi^2}dz\,d\phi_*,
\]
其中
\[
\lambda_{\rm dim}
=\frac{\lambda_K(W^2,m_{\chi_1}^2,m_s^2)}{W^4}.
\]
因此
\[
\frac{d\Phi_3}{dE_R\,dW^2\,dz\,d\phi_*}
=\frac{\sqrt{\lambda_{\rm dim}}}{512\pi^4p_{\chi_1}}.
\]
按
\[
\langle\mathcal L_{00}\rangle_{\phi_*}
=\frac1{2\pi}\int_0^{2\pi}d\phi_*\,\mathcal L_{00}
\]
定义方位角平均后，系数变为
\[
\frac{\sqrt{\lambda_{\rm dim}}}{256\pi^3p_{\chi_1}}.
\]
再乘不变通量 \(1/(2\Lambda_{\rm in})=1/(4m_Ap_{\chi_1})\) 和 leading nuclear charge current 的平方 \((J_A^0)^2\simeq4m_A^2\)，得到
\[
\frac{4m_A^2}{4m_Ap_{\chi_1}}
\frac1{256\pi^3p_{\chi_1}}
=\frac{m_A}{256\pi^3p_{\chi_1}^2}.
\]
所以 Eq. (6) 的前因子
\[
\boxed{\frac{m_A(g_1g_2g_{VN})^2}
{256\pi^3p_{\chi_1}^2(m_V^2+2m_AE_R)^2}}
\]
与当前 \(\phi_*\) 平均约定一致。若把方位角当作未归一化积分，就必须重新处理 \(2\pi\)，不能照搬同一个系数。

三体积分
\[
I_6=\int_{W_{\min}^2}^{W_{\max}^2}dW^2
\sqrt{\lambda_{\rm dim}}\int_{-1}^{1}dz
\langle\mathcal L_{00}\rangle_{\phi_*}
\]
具有 \([I_6]={\rm GeV}^2\)，故 \([d\sigma/dE_R]={\rm GeV}^{-3}\)。代码的 Gauss–Legendre 方位角权重 \(\mathrm{wp}/2\) 正好实现 \(1/(2\pi)\) 平均，不应再额外乘一次 \(2\pi\)。

## 6. \(W_{\max}\)、三体阈值和 \(v_{\min}\)

精确三体边界为
\[
W_{\min}^2=(m_{\chi_1}+m_s)^2,
\]
\[
W_{\max}^2
=m_{\chi_1}^2+2p_{\chi_1}Q
-2(E_{\chi_1}+m_A)E_R.
\]
相空间开放当且仅当 \(W_{\max}^2\ge W_{\min}^2\)。

阈值处令 \(W_{\max}^2=(m_{\chi_1}+m_s)^2\)，定义
\[
a=m_s+\frac{m_AE_R+m_s^2/2}{m_{\chi_1}},
\qquad Q=\sqrt{2m_AE_R+E_R^2}.
\]
整理得到
\[
\gamma(\beta Q-E_R)=a.
\]
利用 \(\gamma^{-2}=1-\beta^2\)，得到
\[
(Q^2+a^2)\beta^2-2QE_R\beta+(E_R^2-a^2)=0.
\]
取物理正根：
\[
\boxed{
\beta_{\min}
=\frac{QE_R+a\sqrt{Q^2-E_R^2+a^2}}{Q^2+a^2},
\qquad
v_{\min}=c\beta_{\min}.
}
\]
\(\Delta m\) 不进入该阈值，因为 \(\chi_2\) 是内部态，不是末态粒子；阈值由 \(m_{\chi_1},m_s,m_A,E_R\) 决定。

**独立数值对照：** 对四组 benchmark、四个代表性 Xe 同位素质量和四个反冲点，共 64 组输入，用独立求根解 \(W_{\max}^2-(m_{\chi_1}+m_s)^2=0\)，与 `rate_kinematics.py` 的闭式 \(\beta_{\min}\) 比较。最大 \(|\Delta\beta|=3.89\times10^{-13}\)，对应速度差约 \(1.17\times10^{-7}\) km/s。该检查验证闭式阈值与 exact-\(Q\) 的 \(W_{\max}\) 公式相容；它不是对所有可能模型输入的穷举扫描。

## 7. AFH factor-of-four：从 raw package 到物理核子耦合

AFH v6.0 setter 的接口输入满足 \(c_p=c_n=c_{\rm set}/2\)。因此物理等核子耦合 \(g_p=g_n=g_{VN}\) 对应 \(c_{\rm set}=2g_{VN}\)。AFH raw response
\[
R_{\rm AFH,raw}
=\frac{4\pi}{2J_A+1}W_{M,\rm AFH}^{00}
\]
在 \(q=0\) 的理论极限为
\[
R_{\rm AFH,raw}(0)=A^2/4.
\]
而 Eq. (6) 已将 \(g_{VN}^2\) 显式放在耦合前因子中，所以核响应必须改为
\[
\boxed{
R_A^{\rm phys}
=4R_{\rm AFH,raw}
=\frac{16\pi}{2J_A+1}W_{M,\rm AFH}^{00},
\qquad R_A^{\rm phys}(0)=A^2.
}
\]
Xe-131 raw source translation 给出 \(R_{\rm AFH,raw}(0)=4289.895955714993\)，理论 \(A^2/4=4290.25\)，相对偏差 \(8.2523\times10^{-5}\)，来自密度矩阵有限打印精度。形状表使用
\[
R_A^{\rm phys}(q)
=A^2\frac{R_{\rm AFH,raw}(q)}{R_{\rm AFH,raw}(0)}
\]
只消除整体常数偏差，不移动 \(q\) 极小值。

代码交叉检查：
- Xe-131 AFH 输出同时保留 raw 与 physical normalized columns；
- `recompute_afh_four_benchmarks.py` 读取 `R_equal_pn_normalized`，要求 \(R_A(0)=A^2\)；
- `compute_four_benchmark_dsigma.py` 将该物理响应直接代入 Eq. (6)，没有再乘一次 4；
- 天然氙 selected sample 的 `R_A` 也是 physical response，halo fold 直接使用，不再额外乘 4。

因此当前 AFH factor 4 只出现一次。夸克—核子匹配 \(g_{VN}=3g_{Vq}\) 不受此核归一化因子影响。

### 7.1 已修正的原始工作稿

原始 `paper-source/main.tex` 曾同时写
\[
\mathcal R_A=\frac{4\pi}{2J_A+1}W_M^{00},
\qquad \mathcal R_A(0)=A^2,
\]
这对 AFH v6.0 raw package output 不成立。现已改为
\[
\mathcal R_A^{\rm phys}
=\frac{16\pi}{2J_A+1}W_{M,\rm AFH,v6}^{00},
\qquad
y=(b_AQ/2)^2,\quad Q^2=2m_AE_R+E_R^2.
\]
`paper-source/SHA256SUMS` 中 `main.tex` 的 hash 已同步更新。历史原稿 `main_original.tex` 保留不动，以保留来源追溯。

## 8. 从单同位素截面到天然氙速率

对每个同位素单独计算 \(m_A,R_A,v_{\min,A},I_{6,A}\)，再按原始天然丰度 \(x_A\) 求和：
\[
\frac{dR}{dE_R}
=N_T\frac{\rho_\chi}{m_{\chi_1}}c
\sum_Ax_A\int_{v_{\min,A}}^{v_{\max}}dv\,
f_{\rm lab}(v)\frac vc\frac{d\sigma_A}{dE_R}.
\]
其中 \(f_{\rm lab}(v)\) 是归一化的一维速度模长 PDF，\(\int f_{\rm lab}(v)dv=1\)；额外的 \(v/c\) 是通量因子，不可用一个平均速度替代积分。

天然氙每 kg 的靶核数为
\[
N_T=\frac{N_{\rm Av}1000}{\bar M_{\rm Xe}},
\qquad
\bar M_{\rm Xe}=131.2927614479\ {\rm g/mol},
\]
数值 \(N_T=4.5868033345\times10^{24}\ {\rm kg}^{-1}\)。该平均原子质量使用完整九种天然同位素丰度；速率求和目前只使用七种有 AFH default response 的同位素，并保留原始丰度、不重新归一化。覆盖率为 99.8158%，缺失 Xe-124、Xe-126 的丰度为 0.1842%；该数值是原子丰度缺口，不是已证明的事件率误差上界。

代码单位链为
\[
1\ {\rm GeV}^{-2}=0.3893793721\times10^{-27}\ {\rm cm}^2,
\]
\[
1\ {\rm GeV}^{-3}=0.3893793721\times10^{-33}\ {\rm cm}^2/{\rm keV}.
\]
再乘 \(\rho_\chi/m_{\chi_1}\)、\(c\)、\(N_T\)、\(86400\) s/day 和速度积分后得到 events/(kg day keV)。当前程序中速度节点 \(v\) 与 \(f(v)\) 分别使用 km/s 和 (km/s)\(^{-1}\)，所以 \(f(v)dv\) 无量纲；物理通量速度由 \(c(v/c)\) 给出，单位链一致。

## 9. LZ rate-level 折叠的边界

LZ 的一维效率折叠是
\[
N_{\rm sig}^{\rm ROI}
=\mathcal E\int_{E_{\min}}^{E_{\max}}dE_R\,
\epsilon_{\rm ROI}(E_R)\frac{dR}{dE_R}.
\]
当前实现使用 2.84 tonne-year、5.4–269.9 keV ROI 和一维 final-ROI efficiency。代码将 rate 与 efficiency 的分段线性插值乘积解析积分，并与稠密梯形积分交叉检查。

它没有完成
\[
\frac{d^2R}{dS1_c\,d\log_{10}S2_c}
\]
的二维响应卷积，没有加入能量分辨、NEST nuisance covariance、背景 likelihood 或 profile likelihood。因此该结果是 rate-level expected yield，不是完整 LZ detector-level likelihood，也不是 90% CL 排除。

## 10. 当前发现的问题与处理状态

| 编号 | 问题 | 处理 | 状态 |
|---|---|---|---|
| P1-01 | 原始工作稿 AFH response 使用 \(4\pi W_M/(2J+1)\) 却声明 \(R_A(0)=A^2\) | 改为 \(16\pi W_{M,\rm AFH,v6}/(2J+1)\)，明确 raw \(A^2/4\) 到 physical \(A^2\) 的映射 | **已修正** |
| P1-02 | 原始工作稿将 \(y=b_A^2m_AE_R/2\) 写成无条件定义 | 改为 \(y=(b_AQ/2)^2\)，并标明前式为小反冲近似 | **已修正** |
| P1-03 | 天然氙 metadata 的 `response_sample_sha256` 实际为 40 位 Git blob SHA-1 | 替换为文件真实 64 位 SHA-256；runner 和 validator 增加校验 | **已修正** |
| P1-04 | Dirac/Majorana、复耦合相位、完整 \(\chi_2\) 自能未由原始模型文本固定 | 明确保留为模型输入/理论扩展，不将条件性宽度推广 | <span>待补模型定义</span> |
| P1-05 | Xe-124、Xe-126 的 AFH default response 缺失；完整 16807 行七同位素响应表未提交 | 在主索引中登记 checksum-only provenance 与缺失输入 | <span>待补输入</span> |
| P1-06 | 原始 Figure 2 的单同位素/天然氙靶定义不明确 | 不把当前 LZ 天然氙扩展误称为原图已确认靶定义 | <span>待补原始输入</span> |
| P1-07 | 完整 AFH 天然氙连续谱与 LZ 二维 likelihood 未完成 | 继续保留为后续研究，不以 selected points 或一维效率折叠替代 | <span>尚未完成</span> |

## 11. 审查范围与下一轮

本轮公式审查确认的是当前 vector–vector、Dirac 外部态、物理 equal-\(p,n\) response、exact spatial-\(q\) 和既定 halo 约定下的计算链。没有证明任意 UV completion、Majorana 版本、任意复耦合相位或所有参数空间都自动满足相同公式。

下一轮应优先：
1. 由模型作者/原始拉格朗日量固定 Dirac/Majorana 与 CP/手征约定；
2. 取得完整 AFH 七同位素 response 输入，补齐 Xe-124、Xe-126，并生成连续 AFH 天然氙谱；
3. 执行 AFH v6.0 原生 Mathematica runner，作为 Python source translation 之外的独立实现验证；
4. 只有在以上输入和模型约定固定后，才推进 LZ 二维 NEST/background/profile-likelihood recast。

