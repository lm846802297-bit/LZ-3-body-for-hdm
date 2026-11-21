# Xe-131：三体电荷权重、两种干涉与绝对截面对照

**状态：已复算。** 本地以 Dirac 迹直接计算两张辐射图，在相同网格上与独立的显式自旋振幅归档对照。检验范围是单同位素、固定速度、核矢量流的电荷—纵向部分，不是全部核流，也不是探测器事件率。

**如何使用这组结果：** `results/weights.csv` 的 299 个反冲点取两张图都为零宽度，用于复核同一约定下的自旋振幅归档，不是正式的有限宽度谱。主线 Eq. (19) 的正式约定是：前发射的 $p-k_s$ 传播子不加有限宽度，后发射的 $p'+k_s$ 传播子加极点宽度 $+i m_2\Gamma_{\rm pole}$。`results/controls.csv` 仅在六个反冲能量上给出这一约定与零宽度的对照。

## 基准与输入

| 输入 | 此处采用的约定 |
|---|---|
| 暗粒子 | 条件性 Dirac 基准；实标量、实耦合、宇称偶的非手征标量跃迁与纯矢量跃迁；不假设暗跃迁流守恒，不指定规范 UV 完成 |
| 质量与速度 | $m_{\chi_1}=1000$ GeV，$m_s=300$ keV，所有反冲均取 $\Delta m=450$ keV；$v=776$ km/s，$m_V=10$ GeV |
| 核质量 | 与本次绝对截面基准一致：$(130.90508406-54m_e/u)u=121.90971983538435$ GeV（本仓库 `nist_nuclear` 选项，无电子束缚能修正）；不是 $131u$，也不是含电子束缚修正的 AME2020 方案 |
| 外部耦合与宽度 | 中心曲线取 $(g_1g_2g_{VN})^2=1$、零宽度。另对 $g_2=1$、仅开放 $\chi_2\to\chi_1s$ 的极点宽度做对照，只在 $p'+k_s$ 传播子加 $+i m_2\Gamma_2$；前一传播子由 $p\cdot k_s\ge m_1m_s$ 可知不通极点 |
| 核输入 | 原生 AFH v6.0 的 2,401 点 Xe-131 网格，三列 `R_*_physical_equal_pn` 已含等质子/中子归一化，**不再乘 4**。PCHIP 在 $Q_A$ 上插值，不外推；$F_1^V,F_2^V$ 使用上游 CSV 的各点中心值，不独立拟合。$F_1^V(0)=3$ 已包含在核子电荷系数中 |

## 从两张图到五个输出

度规 $(+---)$。$q_A=P'-P=(E_R,\mathbf q_A)$，$Q_A=|\mathbf q_A|$，$K=p-q_A=p'+k_s$，$w=K^2$。靶静止系中按每个积分点自己的 $\hat{\mathbf q}_A$ 投影 $\Gamma^L=\hat{\mathbf q}_A\cdot\boldsymbol\Gamma$，不是取束流方向的 $\Gamma^3$。从[当前论文](../../../paper-source/main.tex)的顶点计算：

$$
\Gamma^\mu=\gamma^\mu\frac{\slashed p-\slashed k_s+m_2}{(p-k_s)^2-m_2^2}
+\frac{\slashed K+m_2}{w-m_2^2+i m_2\Gamma_2}\gamma^\mu.
$$

定义 $S(X,Y)=\tfrac12\mathrm{Tr}[(\slashed p'+m_1)X(\slashed p+m_1)\gamma^0Y^\dagger\gamma^0]$。只平均一次入射暗粒子的两个自旋，求和出射自旋；标量无自旋，相空间无相同末态粒子对称因子。核自旋平均已在物理响应内。记 $r=E_R/Q_A$，核连续性仅给出 $J_L=rJ^0$。下列 $0,L$ 是上指标分量的标签，**混合项的度规负号只计一次**：

$$
L_{ij}=\int d\mu\, S(\Gamma^i,\Gamma^j),\qquad
L_C=L_{00}-2r\,\mathrm{Re}\,L_{0L}+r^2 L_{LL}.
$$

直接计算 $S(\Gamma_C,\Gamma_C)$ 作为独立的组装检验，其中 $\Gamma_C=\Gamma^0-r\Gamma^L$。分别投影两图还给出另一条恒等式 $L_C=L_{C,a}+L_{C,b}+2\,\mathrm{Re}\int d\mu\,S(\Gamma_{a,C},\Gamma_{b,C})$；这最后一项**不是** $-2r\,\mathrm{Re}\,L_{0L}$。所有结果已剥离外部耦合、介子传播子及核响应。

### 固定反冲的测度和量纲

$$
d\mu=dw\,\frac{\sqrt{[w-(m_1+m_s)^2][w-(m_1-m_s)^2]}}{w}\,dz\,\frac{d\varphi_*}{2\pi},\qquad
w_{\min}=(m_1+m_s)^2,\quad w_{\max}=m_1^2+2p_\chi Q_A-2(E_\chi+m_A)E_R.
$$

这里 $-1\le z\le1$，$0\le\varphi_*<2\pi$；$z$ 是 $\chi_1s$ 静止系内标量相对于 **boost 后的入射暗粒子** 的极角余弦。横轴为与该极轴垂直的正交基，定义和 boost 复用 `../phase_space_convergence.py` 的 `_stable_build_point`。它先取 $|\mathbf k_*|=\sqrt{\lambda_{\rm K}}/(2\sqrt w)$，在该系构造 $\mathbf p'_*=-\mathbf k_*$ 后一起 boost 回实验室。$w=m_1^2-2(E_\chi+m_A)E_R+2p_\chi Q_A\cos\theta_q$，故 $d\cos\theta_q=dw/(2p_\chi Q_A)$；取 $\cos\theta_q=1$ 得上界，衰变阈值给出下界。闭区间外截面为零；存储边界在 $w_{\min}$ 的两个浮点 ULP 内按零处理，比值留空而不填 1。

具体地，若 $d\Phi_3=(2\pi)^4\delta^4(\sum p)\prod_i d^3p_i/[2E_i(2\pi)^3]$，核反冲测度给出 $Q_A\,dE_R\,d\Omega_q/[2(2\pi)^3]$，内部二体测度给出 $\sqrt{\lambda_{\rm K}}\,d\Omega_*/(32\pi^2 w)$。积分整体方位角、保留归一化 $\varphi_*$ 平均后，$d\Phi_3/dE_R=d\mu/(256\pi^3 p_\chi)$（微分测度意义）。因此，配套原稿印出的截面前因子时，应使用 **$d\mu$ 而非再乘一次原始相空间**。顶点夹在外线旋量之间后无量纲，$[L_C]=\mathrm{GeV}^2$，截面前因子为 $\mathrm{GeV}^{-5}$，$[d\sigma/dE_R]=\mathrm{GeV}^{-3}$。

## 结果和分母对照

| 同一 $\Delta m=450$ keV，零宽度 | $E_R=200$ keV | $E_R=267$ keV |
|---|---:|---:|
| $L_{00}$ [GeV²] | 16,087,108.53 | 27,356,625.99 |
| $\mathrm{Re}\,L_{0L}$ [GeV²] | 38,645.79 | 65,122.29 |
| $-2r\,\mathrm{Re}\,L_{0L}$ [GeV²] | −70.00239 | −136.29531 |
| $L_{LL}$ [GeV²] | 92.88523 | 155.11987 |
| $r^2L_{LL}$ [GeV²] | 0.00007619 | 0.00016987 |
| $L_C$ [GeV²] | 16,087,038.53 | 27,356,489.70 |
| $10^6(L_C/L_{00}-1)$ [ppm] | −4.35145 | −4.98216 |
| 两图交叉项 / $L_C$ | +22.9965% | +21.3368% |
| 完整电荷截面 [cm²/keV]，单位耦合积平方 | $9.67407\times10^{-32}$ | $9.64189\times10^{-35}$ |

电荷扇区取 $N_{\rm ch}=c_M^2W_M+2c_Mc_{\Phi''}W_{M\Phi''}+c_{\Phi''}^2W_{\Phi''}$，此处 $W$ 简写为已换算的物理响应。$c_{\Phi''}=Q_A^2(F_1^V+2F_2^V)/(4m_N^2)$、$c_M=F_1^V-c_{\Phi''}/2$，$m_N=0.938918$ GeV。各点使用

$$
\frac{d\sigma_{\rm ch}}{dE_R}=\frac{m_A(g_1g_2g_{VN})^2 L_C N_{\rm ch}}{256\pi^3p_\chi^2(m_V^2-t_A)^2},\qquad t_A=-2m_AE_R,\qquad Q_A^2=-t_A+E_R^2.
$$

| 分子 / 分母 | 含义 | 200 keV | 267 keV |
|---|---|---:|---:|
| $L_C/L_{00}$ | 完全相同的核电荷，只改变暗电流投影 | 0.999995649 | 0.999995018 |
| $N_{\rm ch}/(F_1^V(0)^2 W_M)$ | 两者均用 $L_C$；完整电荷 / 点状核子 $M$ | 0.77830934 | 0.64921591 |
| $N_{\rm ch}/(c_M^2 W_M)$ | 两者均用 $L_C$；相对有限动量 $M$ 添加 $\Phi''$ | 0.99655805 | 0.89961039 |
| $L_C N_{\rm ch}/(L_{00}F_1^V(0)^2 W_M)$ | 旧基准若同时取纯时间分量和点状核子 $M$ | 0.77830595 | 0.64921268 |

这里的“点状核子 $M$”仍保留 Xe-131 的 $W_M(Q_A)$，不是把整个核的形状因子置为 1。若另改用严格的点标量核 $J^0=2m_A+E_R$，与原稿的 $2m_A$ 外线归一化比较还会多出 $(1+E_R/(2m_A))^2$；它不是暗侧 $L_C/L_{00}$，此处未混入。有限动量形状因子为条件性中心输入，不将这些核响应比值视为普适修正。

## 数值检验、宽度与速度

- 299 个反冲节点（297 个开放），边界约 109.38223、653.70191 keV。整个开放网格的纵向相对修正为 −7.812 至 −3.366 ppm。100 keV 可用于说明 $E_R/Q_A$，但**在这个基准下没有开放的三体相空间**。
- 各点用 $w=w_{\min}+(w_{\max}-w_{\min})u^2$ 的雅可比，$12\times6\times4$ 阶、方位角用等距周期平均。在 110、200、267、324、546、652 keV 升至 $24\times12\times8$，七个原始迹积分的最大相对变化为 $8.6\times10^{-13}$ 以内。独立自旋振幅归档对全开放网格的 $L_{00},L_C,d\sigma_{\rm ch}/dE_R$ 最大相对差均小于 $8.0\times10^{-8}$；共用运动学约定和核输入，不是对核模型的独立验证。
- 网格最小极点间距约 85.97 keV；极点宽度控制取 $\Gamma_2=53.3822$ keV。200、267 keV 用此宽度后 $L_C$ 分别变为零宽度的 0.952107、0.942202，说明极点不可达不等价于宽度可忽略。另在 $v=750$ km/s、零宽度时，这两点的 $L_C$ 分别降至 $6.16673\times10^6$ 和 $1.10151\times10^7$ GeV²。两者均是控制计算，不替代中心谱。
- 单元检验：倾斜的 $\hat{\mathbf q}_A$ 上以显式自旋器交叉检验 $00,0L,LL,C$ 四项，检验在壳与四动量守恒；检验两类分解、闭相空间、零/极点宽度和排除在壳内线。每个开放反冲点另检验积分 Gram 不等式和两种积分分解的闭合。

## 复现与产物

从仓库根目录运行（Python、NumPy、SciPy、Matplotlib；版本记录于 `checks.json`，确定性求积，不需随机种子或网络）：

```powershell
python -B -m unittest discover -s research/three_body_calculation_and_validation/tests -p test_charge_longitudinal.py -v
python -B research/three_body_calculation_and_validation/charge_longitudinal/run_scan.py
```

- [逐点权重和截面](results/weights.csv)；[高阶、宽度、速度对照](results/controls.csv)；[精度、输入输出 SHA-256](results/checks.json)。
- [两种干涉与权重曲线](results/charge_weights.png)；[绝对截面与点电荷基准曲线](results/point_charge_comparison.png)。
- `input/` 保留两份逐字节解出的上游原生文件：固定基准 CSV 和元数据。来源为同仓库的[计算执行 44324056946](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44324056946)，代码 `c5bfcf6c5494d036b078af8299a2fca2e86248ce`，产物 `14437568189`；通过 `gh api repos/lm846802297-bit/LZ-3-body-for-hdm/actions/artifacts/14437568189/zip` 取得、`Expand-Archive` 解出，对照了 ZIP 的服务端 SHA-256。未将上游谱当成新迹积分输入；仅复用其反冲网格和核子形状因子，并在新积分后对照。核响应直接读取[已入库的 AFH 表](../../afh_default_density_xe131/output/phi_response_native/afh_default_xe131_M_PhiPP_native.csv)。
- 约定参考：[PDG Kinematics](https://pdg.lbl.gov/2024/reviews/rpp2024-rev-kinematics.pdf) 和 [Anand、Fitzpatrick、Haxton 的核响应原文](https://arxiv.org/abs/1308.6288)。不涉及天然氙丰度求和、晕速度积分、横向核多极、LZ 响应或似然。
