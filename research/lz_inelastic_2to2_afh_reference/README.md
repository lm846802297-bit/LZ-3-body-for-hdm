# LZ 非弹性二体 O1 反冲谱：AFH 参考对照

**状态：可复算的归档对照；尚未验证为对 LZ 曲线的精确复现。**

## 研究问题与范围

本目录计算非弹性二体过程 \(\chi_1+A\to\chi_2+A\) 的天然氙 O1 反冲率，并将 AFH v6.0 结果与 LZ 论文 Figure 1 上方面板中数字化的三条曲线作图比较。它用于检查 AFH 的 O1、同位素求和和速度平均工作流。

这项计算是单独的 **2\(\to\)2 NR-EFT 参考对照**，不是本仓库主要研究的三体过程 \(\chi_1+A\to\chi_1+A+s\)。它也不是 LZ 探测器级拟合、似然分析或排除限。

## 模型、输入与约定

- 暗物质质量：\(m_\chi=1000\) GeV；核子质量参数：\(m_N=0.938272\) GeV；O1 的参考质量：\(m_\nu=246.2\) GeV。
- NR EFT 耦合：`SetCoeffsNonrel[1,2,0]`。AFH 把等标量输入平均分给质子和中子，因此输入 2 对应 \(c_p=c_n=1/m_\nu^2\)。
- 天然氙采用代码中的七种 AFH 同位素丰度并将其和归一化为 1。反冲动量使用 \(q=\sqrt{2 A m_N E_R}\)，即质量数乘核子质量的近似；此对照没有采用 AME2020 同位素核质量。
- 晕参数：\(\rho_\chi=0.3\) GeV/cm\(^3\)、\(v_0=238\) km/s、固定年平均近似 \(v_E=250.24\) km/s、\(v_{\rm esc}=544\) km/s。
- AFH 的 `MBcutoff` 使用平滑截断。对 O1，脚本按速度积分之比逐同位素校正为标准锐截断 Maxwell 分布。
- 反冲网格为 `Range[5,350,5]` 与 `Range[28,45,1]` 的并集，共 84 个能点；\(\delta=0,200,300\) keV。

AFH 包文件不在本目录重复保存。计算脚本从仓库唯一的 `v6/dmformfactor-V6.m` 加载 AFH v6.0；运行前请从仓库根目录执行命令。

## 文件与复算

| 文件 | 用途 |
|---|---|
| `LZ_inelastic_2to2_xenon_recoil.nb` | Mathematica 阅读入口，依次调用下面两个脚本。 |
| `compute_lz_inelastic.wls` | 计算七同位素 AFH 反冲谱，导出 CSV 和 AFH 谱图。 |
| `compare_lz_digitized.wls` | 将 AFH 谱与数字化 LZ 曲线叠图，并显示已归档的点值比较表。 |
| `lz_fig1_digitized_long.csv` | 从 LZ Figure 1 上方面板提取的曲线点；它是图像数字化输入，不是 HEPData 原始表。 |
| `lz_inelastic_o1_spectra.csv` | AFH 反冲谱，单位 events/(tonne year keV)。 |
| `lz_overlay_benchmark_comparison.csv` | 选定反冲能量上的 LZ 数字化值、AFH 值与比值。 |
| `lz_inelastic_o1_spectra.png` | AFH 单独谱图。 |
| `lz_fig1_vs_afh_overlay.png` | 数字化 LZ 曲线与 AFH 谱的叠图。 |
| `lz_fig1_original_panel_crop.png` | 用作数字化来源定位的论文图像裁剪，许可信息见 `THIRD_PARTY_NOTICES.md`。 |
| `run_manifest.json`、`SHA256SUMS.txt` | 输入、结果、运行边界和文件校验记录。 |

在 Mathematica/WolframScript 环境下，从仓库根目录运行：

```powershell
wolframscript -file research/lz_inelastic_2to2_afh_reference/compute_lz_inelastic.wls
wolframscript -file research/lz_inelastic_2to2_afh_reference/compare_lz_digitized.wls
```

也可以打开 `.nb` 文件，按笔记本顺序运行。脚本会把结果写回本目录，重新运行会覆盖同名输出。

## 归档结果

当前保留的 AFH 与图像数字化对照值包括：

| \(E_R\) (keV) | \(\delta\) (keV) | LZ 图像数字化率 | AFH 率 | 单位 |
|---:|---:|---:|---:|---|
| 150 | 0 | 37193.7 | 33685.9 | events/(tonne year keV) |
| 150 | 200 | 1899（约） | 1729（约） | events/(tonne year keV) |
| 175 | 300 | 68.5（约） | 65.7（约） | events/(tonne year keV) |

更多对照点见 `lz_overlay_benchmark_comparison.csv`。原目录中的 `AFH修正前速率.csv` 是已被修正计算取代的旧结果，本归档不收录。

## 数据来源、验证状态与限制

- 参考图：LZ Collaboration, *Search for dark matter particle interactions in an extended nuclear recoil energy window with the LUX-ZEPLIN (LZ) experiment*, arXiv:2609.02823v1, Figure 1 上方面板；数据发布 DOI：10.17182/hepdata.182472.v1。数字化点来自论文 PDF 图像，不是 HEPData 原始逐点数据。图像像素误差在凹点附近尤其明显；`lz_fig1_digitized_long.csv` 应视为近似比较输入。
- 当前提交只归档本机已有的 CSV、图和脚本，**没有在本次提交中重新运行 Mathematica**。`run_manifest.json` 明确记录该边界；保存的输出时间戳不能替代原始运行日志。
- 已归档结果在选定点与数字化 LZ 图像接近，但这不证明两者完全一致。LZ 论文使用 WimPyDD 和经修改的核输入；本计算使用 AFH 默认核密度矩阵、固定地球速度近似及质量数乘核子质量。残差来源尚未逐项分离，也未与 HEPData 表逐点核验。
- 计算仅为理论反冲率；没有探测器效率、能量分辨率、曝光量折叠或 LZ 似然。不能将此对照解释为对 LZ 高能事件的解释或对三体模型的验证。

运行状态、运行时版本、输入/输出摘要和 SHA-256 见 `run_manifest.json` 与 `SHA256SUMS.txt`。
