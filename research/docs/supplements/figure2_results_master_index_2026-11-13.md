# Figure 2 三体暗物质计算：数值结果总索引

日期：2026-11-13  
适用分支：`docs/update-figure2-documentation-20261113`  
用途：将 benchmark、物理输入、参数、结果文件、验证记录和 SHA-256 汇总到同一入口。

机器可读清单：[figure2_results_master_index_2026-11-13.json](figure2_results_master_index_2026-11-13.json)。该 JSON 收录 8 个结果组和 48 个文件条目，记录每个文件的仓库相对路径、完整 SHA-256、字节数（可用时）及用途。

## 1. 结果总览

| 结果组 | 物理对象与参数 | 主要结果 | 解释边界 |
|---|---|---|---|
| AFH Xe-131 核响应 | AFH v6.0 `sdgXe131`，67 个密度矩阵条目，\(J_A=3/2\)，\(b_A=2.2923417985\) fm，2401 个 \(q\) 节点 | [AFH 响应表](../../afh_default_density_xe131/output/afh_default_xe131_WM00.csv)，SHA-256 `1b936abf07f54a669ae0680fe230ca7d858297f579ba3113bbbc55c3e76ed83c` | 核响应计算，不是三体截面或 halo 事件率 |
| 四组固定速度 Xe-131 benchmark | \(m_{\chi_1}=1\) TeV，\(m_V=10\) GeV，\((g_1g_2g_{VN})^2=10^{-8}\)，\(g_2=1\)，\(v=800\) km/s，\(M_A=131u\)；Red/Green/Black/Blue 的 \(m_s,\Delta m\) 见 JSON | [AFH/GCN/JJ55 截面表](../../afh_default_density_xe131/output/figure2_four_benchmarks_AFH_GCN_JJ55_corrected.csv)，SHA-256 `43acdbb49053fe9967c6389922658d8176200505f26096228a7f787e389271f7` | 固定单一速度的诊断；800 km/s 高于截断 SHM 的 776 km/s，不能当作该 SHM 下的实际 halo 事件率 |
| AFH 天然氙 selected points | 7 种有 AFH default 响应的同位素；101、200、267、542 keV；截断 SHM 与 untruncated MB 诊断 | [总速率表](../../afh_default_density_natural_xenon_halo/results/natural_xenon_halo_rates.csv)，SHA-256 `93ae142ab66bde2fd8b60c017c1d02c9a5a708fcce35c51ef06706b11521fb16`；[逐同位素贡献](../../afh_default_density_natural_xenon_halo/results/isotope_halo_contributions_compact.csv)，SHA-256 `15b97626c5f118e7ff403726b7c01f9be654374902c7b63e5502538fcc292b5b` | 28 个 AFH 响应样本、98 个同位素贡献、14 个总速率点；不是连续 AFH 谱 |
| AME2020 direct exact-\(q\) 对照 | 7 种同位素、选定反冲点；独立核质量输入路径 | [七同位素结果](../../afh_default_density_natural_xenon_halo/output/ame2020_direct_exactq_fold/seven_isotope_halo_rates.csv)，SHA-256 `755217e6f0d44b22023b920e56d74c6d709102d1e3fbf009a00fcdbdd51dfb80` | selected-point 交叉检查；Xe-131-only hybrid 不等于完整 AME2020 七同位素重算 |
| GCN/JJ55 天然氙连续谱 | Red/Green/Blue/Black；NIST 核质量、exact spatial \(q\)、截断 SHM | 四个 `natural_xenon_continuous_spectrum.csv` 及其 metadata、quadrature crosschecks 均列在 JSON | 连续谱来自 GCN/JJ55；不能标记为 AFH 连续谱 |
| LZ 2026 rate-level fold | 2.84 tonne-year，ROI 5.4–269.9 keV，一维 final-ROI efficiency | [事件数结果](../../lz_detector_response/lz_2026_extended_nr/rate_level_event_yields/lz_2026_rate_level_event_yields.csv)，SHA-256 `82bea75d6a0ae470b2e6ddc26c75f4ae3822739e41638dfa4ebfe9e285a37645` | 没有能量分辨卷积、二维 \(S1_c\)–\(\log_{10}S2_c\) PDF、背景 likelihood 或 90% CL 排除 |
| 450 keV pointwise \(L_{00}\) | \(m_{\chi_1}=1\) TeV，\(m_s=300\) keV，\(\Delta m=450\) keV，\(m_V=10\) GeV，\(v=776\) km/s，\(E_R=200\) keV，\(48\times40\times24\) 求积 | [pointwise JSON](../../figure2_full_reproduction/results/USER_L00_BENCHMARK_450KEV_LOCAL_2026-11-13/USER_L00_BENCHMARK_450KEV_48x40x24.json)，SHA-256 `b1861ccc7c802af9ea5953a60f4d27f9910c70bae0d05d5094c8248395d1cfe0` | 单点 Dirac trace / \(I_6\) 诊断；不是固定速度整条截面曲线 |
| 450 keV 固定速度 \(d\sigma/dE_R\) | Xe-131，\(v=776\) km/s，\(M_A=131u\)，zero-width，GCN/JJ55，105 个内部反冲网格点 | [截面曲线](../../figure2_full_reproduction/results/fixed_speed_xe131_dsigma_450kev.csv)，SHA-256 `0d1376a64bff21bc7a00555271e5692bddc4a4836bc6e91e0bb102bcdc39c42c` | 与 pointwise \(L_{00}\) 测试分开归档；不是 halo-folded 谱 |

## 2. 关键输入与参数约定

### 2.1 AFH 与核响应

- AFH v6.0 source archive：SHA-256 `4e0f70e6e780f3f4a40faa14792cae239d1989cf15d1e211b4fd7389b0460727`。
- AFH Mathematica source `dmformfactor-V6.m`：SHA-256 `dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372`。
- 两者为来源校验信息，原始 ZIP / `.m` 并未作为当前仓库文件提交；仓库提交了 67 项 Xe-131 密度矩阵及其 Python source translation。
- AFH raw isoscalar response 的零动量归一化为 \(A^2/4\)；物理等质子、等中子耦合的 response 为 \(A^2\)，因子 4 只计一次。
- AFH 物理响应使用 \(Q=\sqrt{2m_AE_R+E_R^2}\) 和 \(y=(b_AQ/2)^2\)。\(y\simeq b_A^2m_AE_R/2\) 仅是小反冲近似。

### 2.2 天然氙与 halo

- 天然氙使用 NIST 同位素原子质量减去 54 个电子质量，忽略电子结合能。
- 当前有 AFH default response 的同位素为 Xe-128、129、130、131、132、134、136，天然原子丰度覆盖率为 0.998158。
- Xe-124、Xe-126 合计丰度 0.001842，当前没有相应 AFH default 密度矩阵；没有把其余同位素丰度重新归一化。
- 天然氙每千克靶核数使用完整天然丰度加权平均原子质量 \(\bar M_{\rm Xe}=131.2927614479\) g/mol：
  \[
  N_T=\frac{N_{\rm Av}\,1000}{\bar M_{\rm Xe}}
  =4.5868033345\times10^{24}\ {\rm kg}^{-1}.
  \]
- 截断 SHM：\(v_0=220\)、\(v_E=232\)、\(v_{\rm esc}=544\) km/s，故 \(v_{\max}=776\) km/s。
- untruncated boosted Maxwell–Boltzmann 的 1600 km/s 积分上限仅作为高速尾部诊断。

### 2.3 单位转换

\[
1\ {\rm GeV}^{-2}=0.389379\times10^{-27}\ {\rm cm}^2,
\qquad
1\ {\rm GeV}^{-3}=0.389379\times10^{-33}\ {\rm cm}^2/{\rm keV}.
\]

速率折叠还包括 \(\rho_\chi/m_{\chi_1}\)、\(c\)、每千克靶核数、\(86400\) s/day、速度模长 PDF \(f_{\rm lab}(v)\) 和显式通量因子 \(v/c\)。各项定义及代码入口见[公式—符号—代码索引](../formula_symbol_code_cross_reference.md)。

## 3. 当前未提交或不完整的输入

1. 完整 16807 行 AFH 七同位素 response 文件没有提交；目前仅保存其 SHA-256：
   `44c88f3aaf2fb212facbe68432d38389374255432eec04ce8a76437c82c1be3a`，并提交 28 行 selected samples。
2. Xe-124、Xe-126 的 AFH default density matrices 缺失；0.1842% 是原子丰度缺口，不等于已经证明的事件率误差。
3. 原始 Figure 2 的靶核究竟是单一 Xe-131 还是天然氙，原稿没有给出足够明确的输入说明；当前天然氙路线是面向 LZ 靶材的独立扩展，不应倒称为原图已确认设置。
4. Dirac/Majorana、完整 CP/手征约定和完整 \(\chi_2\) 自能尚未固定；当前宽度只适用于附录 A.6 明确列出的 Dirac / real scalar / pure scalar / single open channel 假设。

## 4. 本轮完整性修复

- 原始 `paper-source/main.tex` 中 AFH response 的 \(4\pi\) 归一化与 \(R_A(0)=A^2\) 不相容；已修正为物理响应 \(16\pi W_{M,\mathrm{AFH,v6}}^{00}/(2J_A+1)\)，并把 \(y\) 改为 exact spatial-\(q\) 定义。
- 已同步更新 `paper-source/SHA256SUMS` 中 `main.tex` 的 SHA-256。
- 天然氙 metadata 的 `response_sample_sha256` 曾误存 Git blob SHA-1（40 位），字段却标为 SHA-256；现已改为实际文件 SHA-256：
  `919bae8f7d3dbe89d090c3ab182e743049e4088b8add57671b635c1d5426aa47`。
- 天然氙 archive validator 已增加对该 SHA-256 的逐字节检查；后续 runner 也会自动写入样本 SHA-256。
- 本索引中的文件 SHA-256 均为 64 位十六进制；Git blob SHA-1 不再冒充 SHA-256。

## 5. 相关研究文档

- [主报告：AFH Xe-131、Eq. (6)、天然氙与 LZ 接口](../09_afh_xe131_three_body_scattering_natural_xenon.md)
- [公式—符号—代码交叉索引](../formula_symbol_code_cross_reference.md)
- [附录 A：三体运动学、振幅与相空间](../appendices/09A_three_body_kinematics_amplitude.md)
- [附录 B：AFH 密度矩阵响应](../appendices/09B_afh_v6_density_matrix_response.md)
- [附录 C：AFH factor-of-four 归一化](../appendices/09C_afh_isoscalar_factor4_normalization.md)
- [附录 D：天然氙同位素靶](../appendices/09D_natural_xenon_isotope_target.md)
- [附录 E：三体 \(v_{\min}\) 与 halo folding](../appendices/09E_halo_velocity_vmin_folding.md)
- [附录 G：空间动量与四动量不变量审计](../appendices/09G_recoil_momentum_convention_audit.md)
- [AFH / Anand 响应原始归一化审计](../../figure2_full_reproduction/ANAND_WM_RESPONSE_AUDIT.md)
