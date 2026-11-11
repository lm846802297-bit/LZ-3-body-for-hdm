> 所属主报告：[AFH v6.0 氙核响应与三体暗物质散射](../09_afh_xe131_three_body_kernel_natural_xenon_halo_2026-11-11.md)

# 附录 G：核响应动量与精确三体运动学动量的约定审计

## G.1 两个 \(q\) 的物理定义

论文在核响应中采用

\[
y=\frac{b_A^2m_AE_R}{2}.
\]

由于 AFH 的谐振子变量为 \(y=(qb_A/2)^2\)，这对应

\[
\boxed{q_{\rm resp}^{\rm NR}=\sqrt{2m_AE_R}}.
\]

另一方面，核初末态均在质量壳上：

\[
P^\mu=(m_A,\mathbf 0),\qquad
P'^\mu=(m_A+E_R,\mathbf q_{\rm kin}),
\qquad P'^2=P^2=m_A^2.
\]

因此

\[
\boxed{q_{\rm kin}^{\rm exact}
=|\mathbf q_{\rm kin}|
=\sqrt{2m_AE_R+E_R^2}}.
\]

这两个量分别服务于不同的近似层次：

- \(q_{\rm resp}^{\rm NR}\)：论文明确采用的非相对论核响应变量；
- \(q_{\rm kin}^{\rm exact}\)：三体运动学中的精确空间反冲动量。

在 \(E_R\ll m_A\) 时二者很接近，但不应在代码中共用一个没有语义区分的 q 变量。尤其不能把精确的 \(q_{\rm kin}\) 代入 \(y\) 后，仍声称严格使用了论文当前写出的 \(y=b_A^2m_AE_R/2\)。

## G.2 28 个天然氙样本的实际约定

对当前七种有 AFH default density matrix 的氙同位素，以及

\[
E_R=101,\ 200,\ 267,\ 542\ {\rm keV},
\]

逐点读取

**research/afh_default_density_natural_xenon_halo/input/afh_response_samples.csv**

并使用 NIST 核质量

\[
m_A=(M_{\rm atom}-54m_e)u
\]

重新计算两种动量。28 个归档样本的 q_response_GeV 均与 \(q_{\rm kin}^{\rm exact}\) 相符，而不是与论文的 \(q_{\rm resp}^{\rm NR}\) 相符。

| \(E_R\) [keV] | \(\Delta q=q_{\rm exact}-q_{\rm NR}\) [keV] | 相对差异 [ppm] |
|---:|---:|---:|
| 101 | 0.031899–0.032882 | 0.199–0.212 |
| 200 | 0.088887–0.091626 | 0.395–0.420 |
| 267 | 0.137106–0.141332 | 0.527–0.560 |
| 542 | 0.396542–0.408764 | 1.071–1.138 |

因此，原天然氙 halo-fold 的 \(R_A\) 样本采用了精确空间动量；不能把它们直接描述成按论文 \(y(E_R)\) 处方重新生成的 AFH 响应样本。

## G.3 Xe-131 响应曲线上的直接数值影响

为避免只凭 \(\Delta q/q\) 判断响应误差，使用本轮 CI 重新生成的 2401 点 AFH default Xe-131 响应表，对同一 NIST Xe-131 核质量分别在 \(q_{\rm resp}^{\rm NR}\) 和 \(q_{\rm kin}^{\rm exact}\) 处进行 PCHIP 插值。

| \(E_R\) [keV] | \(q_{\rm NR}\) [MeV] | \(q_{\rm exact}\) [MeV] | \(R_A(q_{\rm NR})\) | \(R_A(q_{\rm exact})\) | \(\Delta R/R_{\rm NR}\) [ppm] |
|---:|---:|---:|---:|---:|---:|
| 101 | 156.925981 | 156.926013 | 0.321015586 | 0.321008412 | -22.35 |
| 200 | 220.825469 | 220.825560 | 9.628602910 | 9.628550361 | -5.46 |
| 267 | 255.146606 | 255.146745 | 0.006769034 | 0.006767594 | -212.68 |
| 542 | 363.524602 | 363.525006 | 0.003280695 | 0.003280375 | -97.35 |

这些数值说明：

1. 动量本身的差异只有约 \(0.2\)–\(1.1\) ppm；
2. 在核响应斜率较大的反冲点，响应相对变化可以达到约 \(2.1\times10^{-4}\)；
3. 这组 Xe-131 数值不能作为所有六种其他同位素的响应误差上界；
4. 更不能仅凭小的 \(\Delta q/q\) 就断言天然氙 halo-fold 事件率完全不变。

当前归档的七同位素事件率没有用 \(q_{\rm NR}\) 重新计算，故本附录不把上表解释为已经完成的天然氙速率修正。

## G.4 代码中的明确分离

本轮代码审计和防误用改动为：

- **research/figure2_full_reproduction/rate_kinematics.py**：momentum_transfer 保持精确 \(q_{\rm kin}^{\rm exact}\)，供三体运动学使用；
- **research/figure2_full_reproduction/joint_xe131.py**：固定 Xe-131 响应查询使用论文定义的 \(q_{\rm resp}^{\rm NR}\)；
- **research/afh_default_density_xe131/recompute_afh_four_benchmarks.py**：固定速度 AFH 响应插值使用 \(q_{\rm resp}^{\rm NR}\)；
- **research/afh_default_density_xe131/compute_four_benchmark_dsigma.py**：同样使用 \(q_{\rm resp}^{\rm NR}\)；
- **research/afh_default_density_natural_xenon_halo/run_afh_natural_xenon_halo_fold.py**：现在将响应动量约定与三体运动学动量分开，默认选择 manuscript_nr；只有显式传入 --response-q-convention legacy_exact 才能复现旧的精确-q 样本。

若选择的响应动量与样本文件中的 q 不一致，程序现在会报错，并要求重新生成 \(R_A\)，不会静默地只修改 q 标签。

## G.5 为什么还没有直接更新七同位素 \(R_A\) 样本

旧天然氙响应来源表的归档记录为：

- 文件名：afh_xe_isotope_responses.csv
- 数据行数：16,807（另有一行表头）
- SHA-256：44c88f3aaf2fb212facbe68432d38389374255432eec04ce8a76437c82c1be3a

这份完整七同位素响应表目前没有随 PR #7 提交；仓库只保存了 28 个 selected-point 样本和该文件的哈希。当前可直接复用的 AFH v6.0 源翻译完整响应网格只有 Xe-131。

因此，不能仅把 28 个样本中的 q_response_GeV 改成 \(q_{\rm NR}\)，同时保留旧 \(R_A\) 数值；那样会把“响应在 \(q_{\rm exact}\) 处计算”错误地标记成“响应在 \(q_{\rm NR}\) 处计算”。

要完成严格修正，需要重新取得七同位素的完整 AFH v6.0 响应表（或官方 AFH v6.0 源包和相应 default density matrices），在每个反冲点直接计算

\[
R_A^{\rm new}(E_R)
=
R_A\!\left(\sqrt{2m_AE_R}\right),
\]

随后重新运行逐同位素三体积分和 halo fold。旧的精确-q 结果必须保留为 legacy 对照。

## G.6 机器可读审计结果

本轮 CI 运行 43038372836 已通过，并保存 q-convention audit artifact。相同结果已提交到仓库：

- research/afh_default_density_natural_xenon_halo/results/natural_xenon_q_convention_audit.csv（28 行逐同位素、逐反冲点动量对照）；
- research/afh_default_density_natural_xenon_halo/results/xe131_afh_response_shift_NR_vs_exact.csv（Xe-131 四点 PCHIP 响应对照）；
- research/afh_default_density_natural_xenon_halo/results/q_convention_audit_summary.json（机器可读汇总）。

[查看 CI 运行及其 artifact](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43038372836)。

## G.7 当前状态与验收标准

| 项目 | 状态 | 说明 |
|---|---|---|
| 两种 \(q\) 的解析定义 | 已完成 | \(q_{\rm resp}^{\rm NR}\) 与 \(q_{\rm kin}^{\rm exact}\) 分开 |
| 28 个天然氙样本约定识别 | 已完成 | 归档样本全部匹配 exact-q |
| Xe-131 的 \(R_A(q_{\rm NR})\) 与 \(R_A(q_{\rm exact})\) 对照 | 已完成 | 使用新生成的 2401 点 AFH Xe-131 表 |
| 天然氙 halo 程序防误用与 legacy 回归 | 已完成 | 默认 NR 会拒绝旧样本；legacy_exact 重算 98 个贡献和 14 个总速率，最大总速率差异 \(2.67\times10^{-12}\)，CI 通过 |
| 七同位素 AFH 响应样本重新生成 | 待完成 | 需要完整 AFH 七同位素响应表或源包 |
| 七同位素三体积分与 halo fold 更新 | 待完成 | 必须在新的 \(R_A\) 样本生成后执行 |

本审计不改变三体运动学中的精确 \(q_{\rm kin}\)，也不对已有 halo rate 作经验重标度。它只明确响应函数的输入约定，并阻止今后把两种不同的动量定义混用。

