# 论文四组 benchmark 的微分截面对照

当前采用 **B 为计算基准**，即有限动量核子形状因子 \(F_{1,2}^{V,N}(t_N)\) 与原子核 \(W_M(y_A)\) 响应。四组参数的 A–D 截面图、以 B 为分母的比值图、原论文式参考线及逐点数据见 [A–D 计算与图件](ABCD/README.md)。

## 早期以原论文近似为分母的三曲线对照

本目录生成同一 Xe-131、固定入射速度下的两张图：三条微分截面曲线的 2×2 对照图，以及以原论文近似为分母的比值图（附完整候选/仅时间分量的 ppm 对照）。

状态：**已完成局部数值校验的单体核流候选对照**。4482 个反冲点已计算；24 个升阶节点、12 个原生 Mathematica 绝对截面节点、4 组独立积分张量分量对照均通过。本状态不表示束缚核完整多体电流已验证。输入来自本仓库已存在的核响应原生验收包及 PR #65 的固定源码快照；`results/run_manifest.json` 记录实际数值检查。

共同设置：条件性 Dirac 暗粒子、实标量、纯标量跃迁与纯矢量相互作用；Xe-131，mχ=1000 GeV，mV=10 GeV，v=800 km/s，mA=131×0.93149410242 GeV，(g1 g2 gVN)²=10⁻⁸，g2=1。采用原论文四组截面归档的 A×u 质量方案，目的是只改变响应处理。两张标量辐射图相干相加；仅后发射传播子含常数极点宽度。

四组 (ms [keV], Δm [MeV]) 为 (200,1)、(300,1)、(360,1)、(300,10)。这是固定速度的微观截面，无天然氙丰度求和、halo 积分或探测器折叠。

完整候选采用当前单体非相对论展开中非零的 M、Φ″、MΦ″、Δ、Σ′、Σ′Δ 六项；Σ″与Φ̃′在此阶系数为零。核响应表的原生验收并不完成束缚核多体振幅、相位及连续性匹配，因此完整候选不标记为最终验证的完整核流。

`inputs/upstream/` 是 commit `07e044e76bdfac2cd5559659fa2d458d49b97255` 的逐字节源码快照。有限动量核子形状因子采用该版本的 `isoscalar_zexp` 中心诊断。由于 gVN=3gVq，所有核子系数都除以 F1V(0)=3，使论文近似严格对应 L00×R_M，避免重复计算核子电荷的因子 9。

复现：在仓库根目录执行：

```powershell
python -B research/response_comparison_four_benchmarks/compare_responses.py
python -B research/response_comparison_four_benchmarks/validate_outputs.py
```

需要 NumPy、SciPy、Matplotlib。完整公式、实际数值对照、校验及局限见 [results/REPORT.md](results/REPORT.md)。

图件：`results/differential_cross_sections.{png,pdf,svg}`、`results/cross_section_ratios.{png,pdf,svg}`。逐点数据见 `results/differential_cross_sections.csv`；精确 200/267/269/300/500 keV 节点见 `results/selected_energy_comparison.csv`。

本次产物为本地文件，尚未提交或上传 GitHub；保留此前已有的未提交研究文件。
