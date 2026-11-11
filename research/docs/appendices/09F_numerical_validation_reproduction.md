> 所属主报告：[AFH v6.0 氙核响应与三体暗物质散射](../09_afh_xe131_three_body_kernel_natural_xenon_halo_2026-11-11.md)
> 本文件为该主报告的独立技术附录，保留推导、约定和复现边界。

# 附录 F：计算程序、数据文件、收敛验收和复现命令

### F.1 主要程序入口

| 任务 | 程序或目录 |
|---|---|
| Eq. (6) 三体 kernel | \`research/figure2_full_reproduction/eq6_kernel.py\` |
| AFH Xe-131 response | \`research/afh_default_density_xe131/run_afh_default_xe131.py\` |
| AFH Xe-131 benchmark 截面替换 | \`research/afh_default_density_xe131/compute_four_benchmark_dsigma.py\` |
| AFH 天然氙 halo fold | \`research/afh_default_density_natural_xenon_halo/run_afh_natural_xenon_halo_fold.py\` |
| AFH Xe-131 源矩阵 | \`research/afh_default_density_xe131/afh_default_xe131_density_matrix.csv\` |
| 天然氙同位素权重 | \`research/afh_default_density_natural_xenon_halo/input/natural_xenon_isotope_weights.csv\` |
| 天然氙响应样本 | \`research/afh_default_density_natural_xenon_halo/input/afh_response_samples.csv\` |

### F.2 主要复现命令

从仓库根目录运行。

AFH Xe-131：

\`\`\`bash
python research/afh_default_density_xe131/run_afh_default_xe131.py --outdir research/afh_default_density_xe131/output
python -m unittest research.afh_default_density_xe131.test_afh_default_xe131
\`\`\`

四 benchmark 的 AFH/GCN/JJ55 截面对照需要提供归档的 GCN/JJ55 基础表和 AFH 响应表：

\`\`\`bash
python research/afh_default_density_xe131/compute_four_benchmark_dsigma.py \\
  --base-csv <archived-gcn-jj55-base.csv> \\
  --afh-response-csv research/afh_default_density_xe131/output/afh_default_xe131_WM00.csv \\
  --out-csv <output.csv> \\
  --metadata <metadata.json>
\`\`\`

天然氙 selected-point halo fold：

\`\`\`bash
python research/afh_default_density_natural_xenon_halo/run_afh_natural_xenon_halo_fold.py
\`\`\`

天然氙程序默认采用 \(m_{\chi_1}=1\) TeV、\(m_V=10\) GeV、耦合乘积平方 \(10^{-8}\)、\(g_2=1\)、\(\rho_\chi=0.3\) GeV/cm³、32 个速度节点和 \(8\times8\times4\) 的三体求积。修改输入时必须同步保存新的 metadata，不应覆盖历史输出。

### F.3 输出和审计文件

主要结果文件包括：

- \`output/afh_default_xe131_WM00.csv\`：Xe-131 AFH response 网格；
- \`output/minima.csv\`：响应极小值；
- \`output/figure2_four_benchmarks_AFH_GCN_JJ55_corrected.csv\`：修正后的四 benchmark 长表；
- \`output/FOUR_BENCHMARK_CROSS_SECTION_AUDIT.md\`：四 benchmark 截面审计；
- \`results/natural_xenon_halo_rates.csv\`：天然氙 selected-point halo-folded rates；
- \`results/isotope_halo_contributions_compact.csv\`：同位素贡献；
- \`results/kernel_order_crosschecks.csv\`：三体求积阶数对照；
- \`results/speed_quadrature_crosschecks.csv\`：速度积分阶数对照；
- \`results/halo_pdf_normalization.csv\`：速度 PDF 归一化；
- \`results/vmin_by_isotope_at_101keV.csv\`：101 keV 的逐同位素阈值；
- \`results/metadata.json\`：输入和计算约定。

### F.4 关键验收检查

**运动学与矩阵元**

- 四动量守恒；
- 所有外腿质量壳条件；
- \(K^2=W^2\)；
- Dirac trace 与显式自旋态求和对照；
- before、after、interference 三项之和等于完整迹；
- 关闭相空间时积分为零。

**核响应**

- 67 项 AFH density matrix 与官方源文件一致；
- \(R_A(0)=A^2\)；
- 不拟合 \(b_A\)；
- AFH、GCN、JJ55 的核响应替换保持相同 \(I_6\)；
- 插值不外推，且记录 \(q_{\rm resp}\) 约定。

**数值积分**

- 增加 \(W^2,z,\phi_*\) 求积阶数；
- 增加 halo 速度求积阶数；
- 检查速度 PDF 归一化；
- 检查逐同位素开放/关闭条件；
- 由 \(R_A\)、\(I_6\) 和总前因子重构 \(d\sigma_A/dE_R\)。

### F.5 结果状态的严格表述

当前应采用以下状态描述：

| 项目 | 状态 |
|---|---|
| AFH v6.0 源码翻译和 Xe-131 矩阵提取 | 已完成 |
| AFH 零动量物理归一化映射 | 已完成，含有限精度修正 |
| Xe-131 AFH/GCN/JJ55 对照 | 已归档 |
| 四 benchmark 固定速度截面替换 | 已归档；共用既有 \(I_6\) 网格 |
| 天然氙七同位素 selected-point halo fold | 已归档 |
| AFH 原生 Mathematica/Wolfram 执行 | 待完成 |
| Xe-124/Xe-126 AFH 响应 | 当前输入集中缺失 |
| 天然氙连续反冲谱全网格验证 | 待完成 |
| LZ detector response 与 likelihood | 尚未开展 |

通过软件测试只能说明程序满足相应的代码检查，不能自动证明未指定的粒子场性质、核模型选择、halo 假设或探测器模型已经得到验证。

### F.6 历史数据修正原则

旧结果不应被静默覆盖。特别是：

1. 早期 AFH response CSV 的拼接换行错误已经修复；
2. 早期 benchmark CSV 的 AFH \(R_A\) 列曾误复制 GCN 值，现已由真实 AFH response 插值重新生成；
3. corrected archive 是当前引用版本；
4. 旧版文件若保留，应标记为 superseded，并说明错误来源；
5. 任何新的动量转移约定、halo 参数、求积阶数或宽度方案都应生成新版本结果和 metadata。

---
