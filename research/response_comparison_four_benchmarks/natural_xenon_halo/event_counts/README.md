# 单位探测效率下的天然氙三体信号事例数

2026-11-21 收到的论文图 3 保留了原红线，更新了蓝线和下框比值。新附件与编译论文、红蓝面积和静态电荷绝对事例数的独立对照见[新版图 3 核查](figure3_source_audit/README.md)。以下归档保留本次核查前的源码版本和数值。

[随反冲能变化的事例谱与累计事例数（三页 PDF）](output/pdf/xenon_count_spectra_vs_recoil.pdf) · [新版正文基准的绝对谱与比值](output/recoil_curves/manuscript_event_spectrum.png) · [两个能窗的累计事例数曲线](output/recoil_curves/manuscript_window_count_curves.png) · [同包四组参数的逐组谱图](output/recoil_curves/four_benchmark_event_spectra.png)

第一页将新版论文正文的三体信号红线与按相同质量、耦合重算的 $dN/dE_R$ 叠在一起，单位为本次曝光下的例/keV。第二页的 $N([E_{\min},E_R])$ 从每个能窗的左端开始累计，单位为例。第三页逐一对照新版压缩包另附的四组固定耦合曲线。另存的[能窗积分总数图](output/pdf/xenon_expected_counts.pdf)可按窗查阅总数。

采用新版论文的 **2.84 吨·年**曝光，按 365.25 天/年折合 **1,037,310 kg·天**。对每个真核反冲能窗 $[E_1,E_2]$，信号期望值为

$$
N_X(E_1,E_2)=1{,}037{,}310\;\int_{E_1}^{E_2}dE_R\,
  \left(\frac{dR}{dE_R}\right)_X,\qquad \epsilon(E_R)=1 .
$$

谱的单位是事例/(kg·天·keV)，表中数值的单位是例。只计算 $\chi_1 A\to\chi_1 A s$ 辐射信号，按真实反冲能直接积分。天然氙靶核数、七个同位素的原子丰度及实验室暗物质通量已包含在率中。七种 AFH 默认同位素占天然丰度 99.8158%，保留原始丰度。halo 沿用截断标准晕，$(v_0,v_E,v_{\rm esc})=(220,232,544)$ km/s，$\rho_\chi=0.3$ GeV/cm³。[原子核和粒子流约定](../README.md) · [新版论文的能窗与曝光](../../../../paper-source/main.tex) · [LZ 的曝光量](https://arxiv.org/abs/2609.02823)

## 新版论文谱图上标出的质量与耦合

谱图标注 $m_{\chi_1}=1$ TeV，$m_{A'}=5$ GeV，$m_s=300$ keV，$\Delta m=10$ MeV，$g_1=0.1$，$g_2=1.725$，$g_{A'N}=g_{VN}=0.04857$。由此 $(g_1g_2g_{VN})^2=7.01963298\times10^{-5}$。按这组 $g_2$ 重新计算单衰变道极点宽度，得到 $\Gamma_2=4.73365$ MeV。[原图中的参数标注](../../../../paper-source/figures/DM_signal_v2.pdf)

| 真反冲能窗 [keV] | 本计算静态相干电荷 $M_0$ | A | B | C（仅时间分量） | D（六通道候选） | $(N_D/N_B-1)$ |
|---|---:|---:|---:|---:|---:|---:|
| 215.5–280.5，候选窗 | 0.202534 | 0.200495 | 0.142497 | 0.14154270 | **0.14154207** | −0.6698% |
| 100–200，低能窗 | 0.877785 | 0.871060 | 0.675391 | 0.67386246 | **0.67385980** | −0.2267% |
| 全部允许运动学区间 | 1.786133 | 1.767765 | 1.252011 | 1.24933778 | **1.24933230** | −0.2140% |

$M_0$ 取 $c_M=1$。A 在 $M$ 电荷系数中取核子 $F_{1,2}(0)$ 并保留反冲项。B 采用有限 $t_N=-2m_AE_R$ 的核子形状因子并保留 $W_M$。C 在时间分量上增加 $\Phi''$ 和带符号的 $M\Phi''$ 干涉。D 进一步计入纵向核流及 $\Delta,\Sigma',\Sigma'\Delta$ 三个横向响应。五种计算共享外部质量、耦合、宽度、三体相空间、同位素权重和速度分布。

候选窗内，A 到 B 的变化为 **−28.93%**，体现核子形状因子的动量依赖。B 到 D 的变化为 **−0.00095445 例（−0.6698%）**，其中 C 到 D 的净变化为 **−4.48 ppm**。D 的低能窗／候选窗比为 4.76084。

### 与论文红线的数值对照

独立读出论文 PDF 中代表三体辐射的红色矢量折线。在已标示的 0–800 keV 横轴和对数纵轴上逐段积分，得到候选窗 **0.974 例**、低能窗 **5.99 例**，与正文“约 1 例、6 例”一致。红线纵轴已含 2.84 吨·年曝光，读图时只对能量积分一次。这些数值是图上折线的积分，图中参数重算的结果见上表。[图面读数与本计算并列](manuscript_figure_comparison.csv)

在当前计算中，即使只保留静态相干电荷，候选窗仍为 0.202534 例，与红线的绝对归一化已存在差距。两者的运动学覆盖也不同。原图红线在 750 keV 仍约为 $1.35\times10^{-7}$ 例/keV。按本计算的质量，七个靶核在此能量所需的最低速度至少为 787.75 km/s，高于本次采用的 776 km/s 上限。原图在两个能窗内的绝对差距分别受到哪些输入影响，仍需原始绘图参数逐项对齐。D 的束缚核单体流匹配仍属候选。

新曲线图中的灰色菱形点线采用新版补充材料的领先阶核电荷 $c_M=1$、$L_{00}W_M^{00}(y_p)$、$y_p=b_A^2m_AE_R/2$，保留本项目的三体暗振幅和晕积分。它与上表 $M_0$ 的区别是原子核响应的自变量。上表使用 $y_A=b_A^2(2m_AE_R+E_R^2)/4$。红色实线直接读取原图 393 个矢量顶点，两者在图例中分别标明。新版主稿给出速度平均的形式，未列出谱图全部晕参数，重算所用数值见上文。[新版补充材料的电荷截面](../../../../paper-source/main.tex)

论文红线的主峰约在 180 keV，峰高约 0.113 例/keV。六通道重算的主峰约在 183.5 keV，峰高约 0.0143 例/keV。原图红线可见段为 90.996–796.002 keV，在这同一区间上，原图积分为 **10.877 例**，B 为 **1.25201 例**，D 为 **1.24933 例**。该区间包含重算的全部七核运动学支撑。原图积分仅覆盖实际绘出的红线。[原图与各模型的三能区计数及比值](output/recoil_curves/manuscript_window_comparison.csv) · [逐能量事例谱与累计量](output/recoil_curves/recoil_event_spectra.csv) · [原图红线坐标](output/recoil_curves/manuscript_red_curve.csv)

## 此前四组固定耦合基准

共同取 $m_{\chi_1}=1$ TeV，$m_V=10$ GeV，$g_2=1$，$(g_1g_2g_{VN})^2=10^{-8}$。每格计数均为同样的 2.84 吨·年曝光。

| $m_s$ [keV] | $\Delta m$ [MeV] | 候选窗 B | 候选窗 D | 候选窗 D 相对 B | 低能窗 D | 全能区 D |
|---:|---:|---:|---:|---:|---:|---:|
| 200 | 1 | 0.00980830 | 0.00974469 | −0.6485% | 0.165145 | 0.281481 |
| 300 | 1 | $1.62497\times10^{-4}$ | $1.61409\times10^{-4}$ | −0.6699% | $7.62560\times10^{-4}$ | $1.42051\times10^{-3}$ |
| 360 | 1 | $7.61341\times10^{-9}$ | $7.70025\times10^{-9}$ | +1.1406% | 0 | $2.90100\times10^{-7}$ |
| 300 | 10 | $1.32362\times10^{-6}$ | $1.31475\times10^{-6}$ | −0.6698% | $6.25396\times10^{-6}$ | $1.16037\times10^{-5}$ |

对于 $m_s=360$ keV，最快的可用入射粒子产生的最低反冲能仍为 209.244 keV，100–200 keV 窗的计数严格为零。$(m_s,\Delta m)=(300\ \mathrm{keV},1\ \mathrm{MeV})$ 在 267 keV 单点的 D/B 为 1.01248，候选窗积分后则为 0.99330。能窗比值按窗内事例贡献加权，包含衍射谷两侧的正负修正。

曲线图第三页使用同一份新版论文压缩包中的四组附图。附图按每吨·年、每 keV 给出原始率，乘 2.84 后与重算的绝对谱比较。附图标出耦合乘积，重算中的 $m_V=10$ GeV、$g_2=1$ 取自项目四组截面基准。附图标量质量的后两个图例写为 MeV，第三页按项目基准采用 360 keV 和 300 keV。在四个候选窗中分别积分了各自的原图曲线和重算曲线，绝对归一化差异保留在图和表中。[原始四组附图](../../../../paper-source/figures/DM_signal.pdf) · [附图候选窗积分与 B、D 对照](output/recoil_curves/four_figure_window_comparison.csv)

## 计算与核对

- 按各同位素的精确运动学端点与能窗边界分段，对反冲能用 Gauss–Legendre 求积，每段至多 30 keV。所有节点重新计算三体张量和截断 halo 速度积分，核响应由已验收的每核 2,401 点原生 AFH 动量表作五次样条求值。七核分别加权后求和。全能区用 0–1000 keV 包含五组参数的全部运动学支撑。
- 从六点加密到十点后，五组天然氙基准在三个能区的绝对事例数及空间修正中，最大相对变化为 $7.06\times10^{-8}$。另一条路径在原反冲能网格上用各核的原生响应计算谱，再对分同位素的谱作三次样条积分，最大相对差为 $2.56\times10^{-7}$。这些数值描述积分精度。
- 用程序独立检查了 D 等于六个带符号通道之和、D 等于 C 加空间修正、各运动学关闭能窗严格为零。用带图示极点宽度的独立 Dirac 迹在 Xe-131、267 keV、750 km/s 处核对暗电流 $L_{00}$，相对差约为 $5.04\times10^{-10}$。

[15 组基准与能窗总计数](event_counts.csv) · [105 行逐同位素事例贡献](isotope_event_counts.csv) · [逐通道积分核对](energy_integration_checks.csv) · [参数、原图核查与 SHA-256](count_validation.json)

在本目录运行以下四行，可从仓库随附的分同位素输入重新计算能窗总数、原图读数、逐能量谱及两份 PDF。前两行包含三体和速度积分。后两行分别绘制能窗总数和随反冲能变化的曲线。七核原生 AFH 网格与验收记录已按原始字节入库。[输入与来源](../inputs/afh_v6/README.md)

```powershell
python -B integrate_event_counts.py --native-archive ../inputs/afh_v6
python -B event_spectra.py --native-archive ../inputs/afh_v6
python -B plot_event_counts.py
python -B plot_recoil_event_spectra.py
```

逐能量程序重新计算 5 组参数 × 7 种同位素，每组每核取 530 个真实反冲能节点。每核在其物理端点补零，用保形分段三次插值在 0.5 keV 网格输出绝对谱，并用相同插值的原函数得到累计曲线。静态电荷另用独立能量求积节点直接收缩 $L_{00}W_M^{00}(y_p)$。对六种重算处方、五组参数和三个能区，绘图曲线与独立能量积分的最大相对差为 $6.49\times10^{-6}$，关闭能窗的事例数为零。[逐窗积分核对](output/recoil_curves/window_integral_checks.csv)

本次运行环境为 Windows、Python 3.14.7、NumPy 2.5.4、SciPy 1.18.1、pandas 3.1.1、Matplotlib 3.11.2、PyMuPDF 1.28.2。图件使用微软雅黑，绘图程序亦支持 Noto Sans CJK SC 和黑体。原始数表和代码按字节核验。若 Git 会自动转换换行符，可用 `git clone -c core.autocrlf=false` 检出。校验清单里的路径相对于仓库根目录。[程序、原图、核响应、数表与图件 SHA-256](SHA256SUMS.txt)

## 干净检出复算记录

2026-11-20 在独立检出运行下列完整流程。先核对归档的 61 项 SHA-256，再用仓库内的原生网格计算。七个 Python 入口均正常退出。[实际命令及控制台输出](reproduction_log.txt) · [复算使用的源码提交](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/commit/bac73b47076885b2f748aee43ba7b4d2e3cbfeef)

```powershell
git clone -c core.autocrlf=false https://github.com/lm846802297-bit/LZ-3-body-for-hdm.git
cd LZ-3-body-for-hdm
git checkout --detach bac73b47076885b2f748aee43ba7b4d2e3cbfeef
cd research/response_comparison_four_benchmarks/natural_xenon_halo
python -B run_fold.py
python -B validate.py --native-archive inputs/afh_v6
python -B make_figures.py
cd event_counts
python -B integrate_event_counts.py --native-archive ../inputs/afh_v6
python -B event_spectra.py --native-archive ../inputs/afh_v6
python -B plot_event_counts.py
python -B plot_recoil_event_spectra.py
```

| 复核对象 | 干净检出的结果 |
|---|---|
| 事例数目录的 10 份 CSV | 全部重新生成，与归档逐字节一致。五组基准共 10,005 行逐能量数据、105 行同位素能窗贡献、90 个独立积分对照 |
| 上游 10 份 CSV 和 CSV.gz | 所有输入、数表和解压副本与归档逐字节一致。两个解压副本另与各自的 gzip 内容核对 |
| 两能窗与原图可见段 | 候选窗的论文红线、B、D 分别为 0.973617662、0.142496519、0.141542067 例。90 项中非零积分的最大相对差为 $6.49001\times10^{-6}$ |
| 5 张 PNG 与 3 份 PDF | PNG 的 RGB 像素完全一致。PDF 共 7 页，在相同的 PyMuPDF 渲染设置下逐页像素一致。重新导出的 PDF 带有本次创建时间，运行清单记录本次提交及产物哈希 |

原生核响应用随仓库提交的 Wolfram 导出表及其上游验收记录；本次干净检出重新执行了 Python 的逐核核对、三体与晕积分、计数和作图。
