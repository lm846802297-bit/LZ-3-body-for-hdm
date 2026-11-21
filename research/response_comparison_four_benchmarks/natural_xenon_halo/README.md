# 天然氙的三体核反冲谱与六通道修正

在四组参数下逐同位素计算了微观截面，再按实验室系入射通量和天然原子丰度求和。在 267 keV，六通道单体核流候选 D 相对于时间分量基准 B 的修正为 +0.736% 至 +2.296%。在相同形状因子和质量约定下单取 Xe-131，四组相应的 D/B 均约为 0.91465。七种同位素的衍射极小位置、阈值和速度权重不同。

[两页合订图，第一页为绝对反冲率，第二页为比值](output/pdf/xenon_halo_spectra_and_ratios.pdf) · [各能量的总谱及六项分解](output/halo_spectra.csv) · [四组基准摘要](output/benchmark_summary.csv)

按新版正文基准的 2.84 吨·年曝光重算后，215.5–280.5 keV 候选窗的论文红线积分为 0.974 例，B 为 0.14250 例，六通道候选 D 为 0.14154 例。绝对谱、累计事例数、同包四组质量点的对照以及逐步复算命令见[事例数计算记录](event_counts/README.md)和[三页合订图](event_counts/output/pdf/xenon_count_spectra_vs_recoil.pdf)。

## 从粒子振幅到微观截面

过程为矢量中介子介导的 $\chi_1 A\to\chi_1 A s$。采用 Dirac $\chi_{1,2}$、实的 CP 偶标量 $s$、纯标量非对角 Yukawa 耦合以及等质子／中子矢量耦合。计算使用树级有效相互作用。$m_{\chi_1}=1000$ GeV，$m_V=10$ GeV，$g_2=1$，$(g_1g_2g_{VN})^2=10^{-8}$，$g_{VN}=3g_{Vq}$。$m_2=m_{\chi_1}+\Delta m$。两张标量辐射图先在振幅层相加，再对初始暗费米子的两种自旋取平均并对末态自旋求和。前辐射传播子取实分母，后辐射传播子包含 $+i m_2\Gamma_2$，其中极点宽度按唯一开放的 $\chi_2\to\chi_1s$ 道计算。按表中次序，宽度约为 155.94、151.82、148.48、1590.81 keV。

在靶静止系固定 $E_R$ 和 $v$。用 $E_\chi=\gamma m_\chi$，$p_\chi=\gamma m_\chi v/c$，$Q_A=\sqrt{2m_AE_R+E_R^2}$，定义 $K=p_\chi^\mu-q_A^\mu$，$W^2=K^2$。积分边界为

$$
W^2_{\min}=(m_\chi+m_s)^2,\qquad
W^2_{\max}=m_\chi^2+2p_\chi Q_A-2(E_\chi+m_A)E_R .
$$

在 $K$ 的静止系中，$z=\cos\theta_*$ 相对于 boost 后的入射暗物质方向，$\phi_*$ 绕同一轴，零方位取散射平面。对 $z\in[-1,1]$ 积分并做 $\phi_*$ 平均。积分按 $W^2=W^2_{\min}+u^2(W^2_{\max}-W^2_{\min})$ 变换，含 Jacobian 和 $\sqrt{[W^2-(m_\chi+m_s)^2][W^2-(m_\chi-m_s)^2]}/W^2$。当 $W^2_{\max}\le W^2_{\min}$ 时，三体截面为零。

设 $L_{00},L_C,L_T$ 已包含以上三体相空间积分。以 $r=E_R/Q_A$ 表示连续性约定下的纵向核流，$L_C=L_{00}-2r\,\mathrm{Re}\,L_{0L}+r^2L_{LL}$，$L_T=L_{xx}+L_{yy}$，其中 $z$ 轴沿实验室核反冲。公共绝对归一化为

$$
P_A=\frac{m_A(g_1g_2g_{VN})^2}
{256\pi^3p_\chi^2(m_V^2+2m_AE_R)^2},\qquad
1\ {\rm GeV}^{-3}=3.893793721\times10^{-34}\ {\rm cm}^2/{\rm keV}.
$$

## 核子形状因子与原子核响应

核子形状因子描述单个核子的矢量流。图中 B、C、D 使用当前低动量处方 $f_1=F^{uds,N}_1/3=1+(8.392\ {\rm GeV}^{-2})t_N/3$，$f_2=F^{uds,N}_2/3=-0.184$。外部单体电流取 $q_N^\mu=q_A^\mu$，$t_N=t_A=-2m_AE_R$。空间动量平方 $Q_A^2=2m_AE_R+E_R^2$ 进入核响应和空间算符。B 的低动量截断与此前固定速度图的 isoscalar z 展开分别计算，后者见总谱的 `*_zexp` 列，也使用本次 $t_N$ 约定。[核子匹配文献](https://arxiv.org/abs/1707.06998) · [项目的外部四动量及 B 处方](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/blob/c9cf4b86babd3b29fbe6a80a2b2a7be647677e9c/research/three_body_full_current_nucleon_match/FORM_FACTOR_BASELINE_COMPARISON.md)

原子核的 $W_{X,A}^{00}(y_A)$ 描述原子核内核子的多体结构。使用 AFH v6.0 默认密度，Wolfram 14.2 在每一组 $(A,E_R)$ 直接计算八类原生响应。$y_A=(b_A Q_A/2)^2$，$b_A$ 和单位换算沿用原生 AFH 网格。所有通道用同一个因子 $4C_0(A)4\pi/(2J_A+1)$ 转成等质子／中子耦合的 $R_X$，$C_0(A)$ 由 $R_M(0)=A^2$ 唯一确定。$W$ 上标 $00$ 表示同位旋标量。原子核自旋平均已包含在该转换中。[AFH 论文](https://arxiv.org/abs/1308.6288) · [本次原生响应表](output/native_recoil_responses.csv)

$$
c_M=f_1+\frac{t_N(f_1+2f_2)}{8m_N^2},\qquad
c_\Phi=\frac{Q_A^2(f_1+2f_2)}{4m_N^2},\qquad m_N=0.938918\ {\rm GeV}.
$$

$$
R_{\rm ch}=c_M^2 R_M+c_\Phi^2R_{\Phi''}+2c_Mc_\Phi R_{M\Phi''},\qquad
R_T=\frac{Q_A^2}{m_N^2}\left[
\frac{f_1^2}{2}R_\Delta+\frac{(f_1+f_2)^2}{8}R_{\Sigma'}
-\frac{f_1(f_1+f_2)}2R_{\Sigma'\Delta}\right].
$$

| 数值列 | 每个速度上的微分截面，省略单位换算 | 用途 |
|---|---|---|
| `M0_time` | $P_A L_{00} R_M$ | 灰色菱形点线固定 $c_M=1$，保留与其他曲线相同的精确暗振幅、三体相空间和原子核有限尺寸。这个对照只改变核流处方。新版论文的常振幅 $I(D)$ 近似另有定义。 |
| `A_time` | $P_A L_{00} c_M(0;E_R)^2R_M$ | 在电荷系数中使用 $f_1(0),f_2(0)$，保留核子反冲项。 |
| **`B_time`** | $P_A L_{00} c_M^2 R_M$ | **两页图的 B 基准。** 与此前 A–D 对照保持同一时间分量定义。 |
| `B_Coul` | $P_A L_C c_M^2 R_M$ | PR #67 的另一个 M-only 分母，含连续性纵向补全，单独提供 D/B_Coul。 |
| `C_time` | $P_A L_{00}R_{\rm ch}$ | 仅靶静止系时间分量，含三项电荷响应。 |
| **`D`** | $P_A(L_C R_{\rm ch}+L_T R_T)$ | **当前阶单体核流候选。** 六项分别保存，包括带符号的两项干涉。$\Sigma''$、$\widetilde\Phi'$ 在本匹配阶的系数为零。 |

## 从微观截面到天然氙反冲率

采用银河系截断 Maxwell 分布，$v_0=220$、$v_E=232$、$v_{\rm esc}=544$ km/s，实验室最高速为 776 km/s，$\rho_\chi=0.3\ {\rm GeV/cm^3}$。$f_{\rm speed}$ 对 $dv$ 归一化为一。逐核从 $W^2_{\max}(E_R,v_{\min,A})=W^2_{\min}$ 求阈值，再对 $v$ 积分。[实验室速度加权的通式](https://pdg.lbl.gov/2023/reviews/rpp2023-rev-dark-matter.pdf)

$$
\frac{dR}{dE_R}=86400\,N_T\frac{\rho_\chi}{m_\chi}
\sum_A x_A \int_{v_{\min,A}}^{776}dv\ f_{\rm speed}(v)\,(10^5 v)\,
\frac{d\sigma_A}{dE_R}(v,E_R).
$$

$v$ 和 $dv$ 以 km/s 计，$10^5v$ 为 cm/s。$x_A$ 为天然原子丰度。用全部九种同位素计算每千克天然氙的靶核数 $N_T=4.58680334\times10^{24}$，平均摩尔质量为 131.292761278 g/mol。散射采用 AME2020 原子质量减去 54 个电子质量并加回总电子结合能所得的核质量。七种有 AFH 默认密度的同位素为 Xe-128、129、130、131、132、134、136，丰度合计 0.998158。Xe-124 和 Xe-126 合占 0.001842，缺少相应密度矩阵，七项保留各自天然权重。省略的丰度不直接给出省略的率。率单位为事例/(kg·天·keV)，能量积分后的单位为事例/(kg·天)。

| $m_s$ [keV] | $\Delta m$ [MeV] | 267 keV 的 B | 267 keV 的 D | 267 keV 的 D/B | 对整个运动学区间积分后的 D/B |
|---:|---:|---:|---:|---:|---:|
| 200 | 1 | $6.9372\times10^{-12}$ | $6.9882\times10^{-12}$ | 1.00736 | 0.99834 |
| 300 | 1 | $1.7895\times10^{-13}$ | $1.8118\times10^{-13}$ | 1.01248 | 0.99786 |
| 360 | 1 | $1.6223\times10^{-16}$ | $1.6595\times10^{-16}$ | 1.02296 | 1.00259 |
| 300 | 10 | $1.4506\times10^{-15}$ | $1.4686\times10^{-15}$ | 1.01242 | 0.99786 |

对于 $(300\ {\rm keV},1\ {\rm MeV})$，267 keV 时，Xe-131 的 D/B 为 0.91465，贡献七同位素 D 的 1.745%。Xe-136 的天然原子丰度为 8.8573%，此处贡献 54.22%。改取 $(360\ {\rm keV},1\ {\rm MeV})$ 后，该能量仅 Xe-131、132、134、136 开放，Xe-136 占 D 的 93.96%。读数中的相对效应同时取决于 $W_A$ 的衍射结构和 $v_{\min,A}$ 以上可用的速度尾部。[逐同位素贡献](output/isotope_contributions.csv.gz) · [每种核的运动学端点](output/kinematic_endpoints.csv)

在 $(300\ {\rm keV},1\ {\rm MeV})$ 的这个能量点，按 B 归一化，D 的带符号 $M\Phi''$ 干涉贡献 $+0.0121901$，$\Phi''$ 对角项贡献 $+0.00029065$。D 与 C 使用相同的三项电荷响应，D 中加入纵向与横向核流的净修正为 $10^6(D/C-1)=-4.7318$。以实际速度节点为例，Xe-131 在 $v=749.52188$ km/s、267 keV 的 B、D 微分截面分别为 $2.67183\times10^{-45}$、$2.44378\times10^{-45}$ cm²/keV。

## 数值数据与复算

- [逐速度三体截面](output/microscopic_cross_sections.csv.gz) 在 96,732 个开放速度节点列出 B、C、D 以及 D 的六个带符号分量，单位 cm²/keV。每行的 `fold_weight` 包含速度积分权重、每千克的该同位素核数、入射通量和秒到天的换算。对相同同位素与反冲能求和 `fold_weight * D_cm2_keV` 即得其天然氙贡献。关闭点在同位素表中记零，总谱分母为零时比值留空。
- [四组参数的 2,120 行总谱](output/halo_spectra.csv) 覆盖 0–1000 keV，常规网格步长 2 keV，在 241–295 keV 使用 1 keV，另含 101 keV。每个模型 530 个能量点。总谱及同位素表中 `ch_*` 为已乘粒子系数、相空间及速度权重的分量，单位与率相同。
- [收敛比较](output/quadrature_checks.csv) 在 101、200、267、269、300、542 keV 的 127 个开放同位素点，将 $(n_v,n_W,n_z,n_\phi)$ 从 $(12,12,4,4)$ 加密到 $(22,20,8,8)$。D 的最大相对变化为 $4.6\times10^{-13}$。四个固定速度对照中，独立实现的 $L_{00},L_C-L_{00},L_T$ 与已有自旋振幅算法相差至多 $8.9\times10^{-16}$。另在两个不同的核、速度和标量质量上与直接 Dirac 迹计算 $L_{00}$ 比较，最大相对差为 $6.7\times10^{-9}$。
- [绝对率交叉校验](output/archived_M_only_crosscheck.csv) 在 30 个开放同位素参考点重现旧 M-only 计算。沿用旧的线性 $W^2$ 八点与线性速度六十四点求积后，最大相对差为 $1.38\times10^{-6}$。换为本次阈值变量后与旧表最大相差 $2.52\times10^{-4}$。比较时已统一原子核响应归一化。此校验针对绝对密度率，不校准 D 的横向核流匹配。
- 把能量积分的网格从约 2 keV 改为 4 keV 时，四组 D 总率的最大相对变化为 $1.97\times10^{-5}$。原生响应、输入哈希、所有数值校验的范围和各道极点宽度见[运行记录](output/validation.json)。

在本目录依次运行以下命令。数值部分依赖 Python、NumPy、SciPy、pandas，图件使用 Matplotlib 和中文字体。已随附精确反冲动量的 Wolfram 输出，可直接从第二行重算。验证脚本的 `--native-archive PATH` 可指定已验收的七同位素原生网格目录。

```powershell
wolframscript -file native_recoil_responses.wls
python -B run_fold.py
python -B validate.py --native-archive inputs/afh_v6
python -B make_figures.py
```

本地原生数据已逐通道与此前通过独立检查的七同位素网格核对。D 的束缚核振幅、横向相对相位与相互作用电流仍待独立物理验证。该结果给出探测器响应之前的理论核反冲谱，未施加效率、分辨率或曝光量。[此前的 P4 研究记录](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/pull/67)

## 首次归档记录（提交 3a629fe2）

本目录归档已有本地计算及其记录，未为本次归档重新运行数值积分。`output/validation.json` 和 `event_counts/count_validation.json` 保留原有输入与输出哈希；2026-11-20 归档时分别核对了其中 21 和 10 项，均一致。以下 CSV 是同目录 `.csv.gz` 按 `gzip -dc` 解压得到的原生文件；压缩版本供既有复现脚本和原始哈希记录使用。

| 解压文件 | 字节数 | SHA-256 |
|---|---:|---|
| `output/isotope_contributions.csv` | 4,268,622 | `2ffad5e1bed4239762e7fccaf741651f9e4ac4ad72d0fd07c9ede9fa4154903f` |
| `output/microscopic_cross_sections.csv` | 24,928,999 | `e8f3572e7380aa90f4a6fe72a6ae7cdcd4bdd836b56754a90bc568a51599b689` |

本归档基于 PR #76 的四基准固定速度计算，包含尚未合并的上游分支；本次只归档已有研究记录和产物，不声称重新完成独立物理验证。
