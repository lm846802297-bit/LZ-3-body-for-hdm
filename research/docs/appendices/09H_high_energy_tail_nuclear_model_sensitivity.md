# 高能候选能区核模型敏感性与 AFH 原生 Mathematica 验证计划

**研究阶段：** Phase II — high-energy tail and native AFH validation  
**日期：** 2026-11-14  
**基准数据版本：** `main` at `ce4e500363778832c672117819dfd385f9346be7`  
**状态：** 高能尾部积分已完成；原生 Mathematica 执行尚待实际 Wolfram kernel。

## 1. 研究问题与积分区间

本审计比较 AFH-7、Hybrid-9、Helm-9、GCN 和 JJ55 在 LZ 候选高能区间内的效率加权预期事件数。候选能量区间取 (248\pm23\,\mathrm{keV})，并与 LZ 一维效率 ROI 相交：

\[
E_R\in[225,269.9]\;\mathrm{keV}.
\]

对核模型 (M)，定义

\[
N_{\rm tail}^{(M)}
=\mathcal E\int_{225\,\mathrm{keV}}^{269.9\,\mathrm{keV}}
\epsilon_{\rm LZ}(E_R)\,
\frac{dR_M}{dE_R}\,dE_R,
\qquad
\mathcal E=2.84\;\mathrm{tonne\,year}
=1.03731\times10^6\;\mathrm{kg\,day}.
\]

同时计算完整一维效率 ROI 的 (N_{\rm ROI}^{(M)})，并报告

\[
f_{\rm tail}^{(M)}=\frac{N_{\rm tail}^{(M)}}{N_{\rm ROI}^{(M)}}.
\]

积分并非简单地对离散点做粗糙梯形求积：在速率谱和效率曲线各自的节点并集上分段，两者在每段均为线性函数，其乘积为二次函数，因此对每段解析积分。中心效率用于中心值；灰色效率包络分别用于上下界。灰色包络不是置信区间。

## 2. 统一物理输入与核模型覆盖

所有模型比较保持相同的粒子物理和 halo 基准：

- (m_{\chi_1}=1000\,\mathrm{GeV})，(m_V=10\,\mathrm{GeV})；
- ((g_1g_2g_{VN})^2=10^{-8})，(g_2=1)，(ho_\chi=0.3\,\mathrm{GeV\,cm^{-3}})；
- 截断 SHM：((v_0,v_E,v_{\rm esc})=(220,232,544)\,\mathrm{km\,s^{-1}})，(v_{\max,\rm lab}=776\,\mathrm{km\,s^{-1}})；
- NIST nuclear masses；逐同位素采用 (q_A=\sqrt{2m_AE_R+E_R^2})；
- 相同的条件性常数极点宽度假设：Dirac (\chi_2\)、实标量、纯 scalar off-diagonal Yukawa，且仅 (\chi_2\to\chi_1s) 开放。

四组 benchmark：

| 名称 | (m_s) [MeV] | (\Delta m) [MeV] |
|---|---:|---:|
| red | 0.2 | 1 |
| green | 0.3 | 1 |
| black | 0.36 | 1 |
| blue | 0.3 | 10 |

必须区分以下模型：

1. **AFH-7：** 七种有官方 AFH v6.0 default density matrix 的同位素，Xe-124/Xe-126 不计入，天然丰度不重新归一化。
2. **Hybrid-9：** 七种 AFH 同位素不变，只对 AFH default 缺失的 Xe-124/Xe-126 使用 Helm。
3. **Helm-9：** 九种天然氙同位素全部使用 Helm。这是独立的全 Helm 模型比较，不是 AFH-7 缺失同位素的修正。
4. **GCN/JJ55：** 七同位素 shell-model 响应；与 AFH-7 有相同的同位素覆盖。
5. **AFH-7 + (A^2)-2 ceiling：** 仅作缺失同位素的相干 (A^2) 上限诊断，不是物理核模型。

AFH-7 覆盖天然氙原子丰度 0.998158；缺失 Xe-124/Xe-126 的丰度为 0.001842。所有结果均不重新归一化丰度。

## 3. 效率加权高能尾部结果

以下均为已乘 (2.84\) tonne-year 曝光量的预期事件数，不是 events/(kg day) 积分率，也不是观测事件数。

| Benchmark | AFH-7 | Hybrid-9 | GCN | JJ55 | Helm-9 |
|---|---:|---:|---:|---:|---:|
| red ((0.2,1)) | (6.7310\times10^{-3}) | (6.8092\times10^{-3}) | (7.6068\times10^{-3}) | (8.0151\times10^{-3}) | (3.0009\times10^{-2}) |
| green ((0.3,1)) | (1.1683\times10^{-4}) | (1.1760\times10^{-4}) | (1.3135\times10^{-4}) | (1.3873\times10^{-4}) | (5.4326\times10^{-4}) |
| black ((0.36,1)) | (2.6512\times10^{-9}) | (2.6512\times10^{-9}) | (2.6485\times10^{-9}) | (2.6711\times10^{-9}) | (1.4664\times10^{-8}) |
| blue ((0.3,10)) | (9.5137\times10^{-7}) | (9.5763\times10^{-7}) | (1.0696\times10^{-6}) | (1.1297\times10^{-6}) | (4.4218\times10^{-6}) |

相对 AFH-7 的尾部事件数变化：

| Benchmark | Hybrid-9 | GCN | JJ55 | Helm-9 |
|---|---:|---:|---:|---:|
| red | +1.16% | +13.01% | +19.08% | +345.83% |
| green | +0.66% | +12.42% | +18.74% | +364.99% |
| black | 0.00% | −0.10% | +0.75% | +453.12% |
| blue | +0.66% | +12.43% | +18.75% | +364.79% |

### 3.1 尾部占完整 ROI 的比例

| Benchmark | AFH-7 | Hybrid-9 | GCN | JJ55 | Helm-9 |
|---|---:|---:|---:|---:|---:|
| red | 2.12% | 2.14% | 2.25% | 2.32% | 4.71% |
| green | 8.36% | 8.40% | 8.62% | 8.78% | 14.71% |
| black | 92.75% | 92.75% | 92.84% | 92.76% | 94.76% |
| blue | 8.31% | 8.35% | 8.57% | 8.74% | 14.64% |

**不能只看尾部占比。** black benchmark 的尾部占比超过 92%，但 AFH-7 完整 ROI 的预期事件数也只有约 (2.86\times10^{-9})。这是运动学阈值接近关闭时的比例效应，并不意味着该 benchmark 在 LZ 中有可观的绝对信号。

### 3.2 灰色效率包络

完整的中心值、下包络和上包络均保存在：

`results/high_energy_tail_model_sensitivity_2026-11-14.csv`

例如 red benchmark 的 AFH-7 尾部预期事件数为：

\[
N_{\rm tail}=0.006731,
\qquad
N_{\rm tail}^{\rm envelope}=[0.006290,0.006976].
\]

该区间仅反映数字化效率曲线的灰色包络，不应解释为 (1\sigma)、(90\%\) CL 或其他统计置信区间。

## 4. Helm-9 差异的物理解释：AFH 高能衍射极小值

Helm-9 与 AFH-7 的大差异不是因子 4 重复计数，也不是整体归一化错误。关键是 AFH response 在高 (q) 区域存在非常深的衍射极小值，而 Helm 参数化不会在相同位置复现这些极小值。

在现有 5 keV recoil 网格上：

| 同位素 | (E_R) [keV] | AFH (R_A/A^2) | Helm (R_A/A^2) | Helm/AFH |
|---|---:|---:|---:|---:|
| Xe-131 | 267 | (3.94\times10^{-7}) | (4.28\times10^{-5}) | 108.5 |
| Xe-132 | 265 | (2.85\times10^{-8}) | (3.66\times10^{-5}) | 1282.9 |
| Xe-134 | 260 | (2.54\times10^{-8}) | (2.99\times10^{-5}) | 1177.5 |

因此，先前 metadata 中的最大绝对差异 (|R_{\rm AFH}-R_{\rm Helm}|/A^2) 不能充分描述候选高能区的模型敏感性：当 AFH 响应本身接近零时，绝对差异可以很小，但相对差异可以达到数百至上千倍。

对天然氙求和并乘入三体核积分、传播子和效率后，red/green/blue 的 Helm-9 尾部预期事件数约为 AFH-7 的 4.5–4.7 倍。这个结果是高能尾部核模型敏感性的真实信号，但 Helm-9 仍然只是独立的 phenomenological comparison，不应取代 AFH 基准。

## 5. GCN/JJ55 对照的解释

GCN 和 JJ55 与 AFH-7 使用相同的七同位素覆盖、NIST 核质量、精确空间 (q) 和截断 SHM。三组 benchmark 的尾部事件数相对 AFH-7 高约 12–19%；black benchmark 则在 1% 以内。

这说明核结构选择对高能尾部的影响依赖粒子物理 benchmark 和相空间支持区间，并不是一个可以用单一整体比例描述的常数。

数值求积的独立收敛审计已显示：AFH-7 高阶谱的最大基准—最终差异约 (6.64\times10^{-6})；GCN/JJ55 归档 metadata 的最大 kernel 阶数差异约 (2.07\times10^{-4})，速度求积差异约 (1.60\times10^{-6})。这些误差远小于 red/green/blue 中观测到的 12–19% 模型差异。

## 6. 原生 Mathematica 验证：脚本已准备，执行仍待完成

仓库原先已有 `run_afh_default_xe131.wls`，但它主要负责原生输出，并没有将全部 2401 个 (q) 节点与 Python 归档逐点自动比较。

本阶段新增：

`research/afh_default_density_xe131/validate_afh_mathematica_vs_python.wls`

该脚本在真正的 Wolfram kernel 中：

1. `Get` 官方 `v6/dmformfactor-V6.m`；
2. 执行 `SetIsotope[54,131,"default","default"]`；
3. 原生调用 `ResponseNuclear[y,1,0,0]`；
4. 对 2401 个 (q=0\ldots0.6\,\mathrm{GeV}) 节点计算 (W_M^{00})；
5. 与 `output/afh_default_xe131_WM00.csv` 中 Python 结果逐点比较；
6. 输出逐点 comparison CSV 和 metadata JSON。

运行命令（在仓库根目录的 Windows PowerShell 中）：

```powershell
wolframscript -file research/afh_default_density_xe131/validate_afh_mathematica_vs_python.wls
```

可选地通过环境变量指定官方包、Python reference CSV 和输出目录：

```powershell
$env:DMFormFactorPath = "C:\path\to\dmformfactor-V6.m"
$env:AFHPythonReferenceCSV = "research/afh_default_density_xe131/output/afh_default_xe131_WM00.csv"
$env:AFHMathematicaOutDir = "research/afh_default_density_xe131/output/mathematica_native"
wolframscript -file research/afh_default_density_xe131/validate_afh_mathematica_vs_python.wls
```

验收条件包括：2401 个节点完整、(q) 网格差异低于 (10^{-12}\,\mathrm{GeV})、AFH 原始 (q=0) 归一化符合 (A^2/4)、物理归一化满足 (R_A(0)=A^2)，以及全网格物理响应的最大绝对差异除以 (A^2) 小于 (10^{-10})。

**重要状态说明：** 当前执行环境没有 Wolfram kernel / `wolframscript`，因此这里没有声称原生 Mathematica 已运行或通过。新增脚本是原生验证 harness，不是执行结果。只有实际运行并归档 CSV/JSON 后，才能将 Mathematica 项标记为 PASS。

## 7. 当前结论与下一步

1. AFH-7 与 Hybrid-9 的高能尾部差异小于约 1.2%；在当前四组 benchmark 中，缺失 Xe-124/Xe-126 的 Helm-2 补充不是主要不确定性。
2. GCN/JJ55 相对 AFH-7 的尾部差异约 12–19%（除 black 阈值受限 benchmark 外），值得作为核模型系统敏感性保留。
3. Helm-9 与 AFH-7 的大差异来自高 (q) 区域的深衍射极小值差异，不能把 Helm-9 当作 Hybrid-9 的等价替代。
4. black benchmark 尾部占比很高，但绝对事件数极小；必须同时报告 (N_{\rm tail}) 和 (f_{\rm tail})。
5. 下一项 P0 是在 Windows 上真正运行原生 Mathematica harness，并归档 2401 点比较结果。完成之前，不启动完整 LZ likelihood recast。

## 8. 可复现文件

- 计算程序：`research/afh_default_density_natural_xenon_halo/audit/audit_high_energy_tail_model_sensitivity.py`
- 单元/回归测试：`research/afh_default_density_natural_xenon_halo/tests/test_high_energy_tail_model_sensitivity.py`
- 输出 CSV：`research/afh_default_density_natural_xenon_halo/results/high_energy_tail_model_sensitivity_2026-11-14.csv`
- 原生 Mathematica 验证：`research/afh_default_density_xe131/validate_afh_mathematica_vs_python.wls`
- AFH-7/Hybrid-9 原始谱与 metadata：`research/afh_default_density_natural_xenon_halo/results/afh7_hybrid9_continuous_2026-11-14/`
- GCN/JJ55 原始谱：`research/figure2_full_reproduction/results/natural_xenon_continuous_spectrum/`
- LZ 效率曲线：`research/lz_detector_response/lz_2026_extended_nr/lz_2026_nr_efficiency_digitized.csv`
