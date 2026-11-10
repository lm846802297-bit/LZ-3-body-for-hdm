# P0-4：\(\chi_2\) 传播子与宽度审计（第一轮）

> 状态：第一轮数值诊断完成；尚未完成完整费米子一圈自能计算。  
> 基准分支：\`research/figure2-p0-4-mainline\`  
> 基础：PR #1 已 squash-merge 至 \`main\`。  
> 单位：自然单位制，质量和能量均以 GeV 输入；表格中按需要换算为 MeV/keV。

---

## 1. 本阶段要回答的问题

公式 (6) 的暗费米子第二个传播子为：

\[
S_2(K)\ \propto\
\frac{\not K+m_{\chi_2}}
{W^2-m_{\chi_2}^2+i m_{\chi_2}\Gamma_{\chi_2}},
\qquad W^2=K^2.
\]

本阶段针对四个问题：

1. 零宽度、常数 pole-width 和随虚质量变化的 running-width，对约化积分 \(I_6\) 有多大影响？
2. 虽然原稿要求 \(W_{\max}<m_{\chi_2}\)，积分区间是否仍可能接近 Breit–Wigner pole？
3. 在不同 \(\Delta m\) 下，宽度敏感性如何变化？
4. 是否可以仅凭图注中的 \((g_1g_2g_{VN})^2\) 确定宽度？

结论先行：

- 在当前四组 benchmark 中，整个 \(W^2\) 积分区间均低于 pole mass，满足 \(W_{\max}<m_{\chi_2}\)。
- 但“禁止 on-shell \(\chi_2\)”并不等于“常数宽度可以忽略”。在 \(\Delta m=1\) MeV、\(g_2=3\) 的 pole-width 诊断中，宽度项与最大 \(W\) 处的实部失谐量同量级，\(I_6\) 相对零宽度结果降低约 45%–48%。
- 若采用由同一标量衰变道得到的 running-width 近似，积分区间中的虚态质量 \(W\) 仅略高于 \(\chi_1+s\) 阈值，\(\Gamma(W)\) 显著小于 pole width；相同 benchmark 的 \(I_6\) 变化降至约 1.3%–1.8%（\(\Delta m=1\) MeV、\(g_2=3\)）。
- 这一差异说明宽度方案是重要模型输入，不能通过拟合 Figure 2 任意选择。running-width 结果目前只是诊断性 Breit–Wigner ansatz，不是完整费米子自能计算。

---

## 2. 宽度公式与两种传播子处方

### 2.1 条件性 Dirac 纯标量两体宽度

从原稿的标量相互作用：

\[
\mathcal L\supset g_2s\bar\chi_2\chi_1+\mathrm{h.c.}
\]

出发，在以下假设下推导宽度：

- \(\chi_1,\chi_2\) 为 Dirac 费米子；
- 顶点为纯标量 Yukawa 耦合；
- 只考虑 \(\chi_2\to\chi_1s\)；
- 没有其他开放衰变道。

若衰变母粒子不变质量为 \(M\)，则：

\[
\overline{|\mathcal M|^2}
=
|g_2|^2\left[(M+m_{\chi_1})^2-m_s^2\right].
\]

因此：

\[
\boxed{
\Gamma(M)=
\frac{|g_2|^2}{16\pi M^3}
\sqrt{\lambda_{\rm dimful}
(M^2,m_{\chi_1}^2,m_s^2)}
\left[(M+m_{\chi_1})^2-m_s^2\right]
}
\]

其中：

\[
\lambda_{\rm dimful}(a,b,c)
=a^2+b^2+c^2-2ab-2ac-2bc.
\]

pole width 取：

\[
\Gamma_{\rm pole}=\Gamma(m_{\chi_2}),
\qquad m_{\chi_2}=m_{\chi_1}+\Delta m.
\]

running width 诊断则将母粒子不变质量替换为传播子当前虚质量：

\[
\Gamma_{\rm run}(W)=\Gamma(W).
\]

在该公式下，当 \(W\to m_{\chi_1}+m_s\) 时：

\[
\Gamma_{\rm run}(W)\to0.
\]

注意：当前 \`paper-source/main.tex\` 明确写出了 pole-width 分母和 \(\Gamma_{\chi_2}\) 的定义，但没有在该段落明确列出上述两体宽度公式。它是根据所写相互作用在 Dirac 纯标量假设下推导的，不应标成原稿已经给出的公式。

### 2.2 零宽度方案

\[
D_0(W^2)=W^2-m_{\chi_2}^2.
\]

这只作为对照，不代表在所有参数下都可以忽略不稳定粒子的宽度。

### 2.3 常数 pole-width 方案

\[
D_{\rm pole}(W^2)=
W^2-m_{\chi_2}^2+i m_{\chi_2}\Gamma_{\rm pole}.
\]

这是当前论文源码明确采用的 Breit–Wigner 形式。

### 2.4 Running-width 诊断方案

本轮另外测试：

\[
D_{\rm run}(W^2)=
W^2-m_{\chi_2}^2+iW\Gamma_{\rm run}(W).
\]

这里采用 \(W\Gamma(W)\) 作为虚部，是常见的 running-width Breit–Wigner 诊断形式。它并不等价于完整的费米子传播子一圈重求和。

完整费米子自能一般具有：

\[
S^{-1}(K)=\not K-m_{\chi_2}-\Sigma(\not K),
\]

其中 \(\Sigma(\not K)\) 可包含不同 Dirac 结构以及实部和虚部。严格的 pole scheme / running scheme 比较最终需要从该自能出发，统一处理质量重整化、波函数重整化和虚部，而不能仅凭替换一个标量宽度就宣称完成了完整自能审计。

因此，本报告把 running-width 结果称为**诊断性近似**。

---

## 3. \(W_{\max}<m_{\chi_2}\) 的全反冲区间检查

固定 \(v\) 时：

\[
W_{\max}^2(E_R)=
m_{\chi_1}^2
+2p_{\chi_1}\sqrt{2m_AE_R+E_R^2}
-2(E_{\chi_1}+m_A)E_R.
\]

为了检查整个反冲能量范围，不能只在某一个 \(E_R\) 点比较 \(W_{\max}\) 和 \(m_{\chi_2}\)。本轮对 \(E_R\) 做一维最大化，得到：

| \(v\) (km/s) | \(E_R\) 处于最大值时 (keV) | \(\max_{E_R}(\sqrt{W_{\max}^2}-m_{\chi_1})\) (keV) | \(\Delta m=1\) MeV 的最小 pole 间隔 (keV) | \(\Delta m=10\) MeV 的最小 pole 间隔 (keV) |
|---:|---:|---:|---:|---:|
| 544 | 159.553 | 179.017 | 820.983 | 9820.983 |
| 600 | 194.092 | 217.771 | 782.229 | 9782.229 |
| 770 | 319.659 | 358.657 | 641.343 | 9641.343 |
| 776 | 324.660 | 364.268 | 635.732 | 9635.732 |
| 800 | 345.051 | 387.149 | 612.851 | 9612.851 |

本表采用 \(m_{\chi_1}=1\) TeV、\(m_A=122\) GeV，速度范围是本轮指定的 544–800 km/s。

对 \(\Delta m=1\) MeV 和 10 MeV：

\[
\max_{E_R}\sqrt{W_{\max}^2}<m_{\chi_1}+\Delta m.
\]

因此，在该速度区间和所有正的可达 \(E_R\) 上，off-shell 条件成立。最接近 pole 的点出现在最高测试速度 800 km/s。

这一结论不能自动外推到高于 800 km/s 的速度，也不能替代最终 halo 分布的速度截断审计；必须在最终采用的 \(v_{\max}\) 上重新检查。

---

## 4. 四组 Figure 2 诊断 benchmark 的 pole 间隔

采用：

\[
m_{\chi_1}=1000~\mathrm{GeV},\quad m_A=122~\mathrm{GeV}.
\]

| \(m_s\) | \(\Delta m\) | \(E_R\) | \(v\) | \(W_{\max}\) (GeV) | \(m_{\chi_2}-W_{\max}\) |
|---:|---:|---:|---:|---:|---:|
| 300 keV | 1 MeV | 200 keV | 776 km/s | 1000.000347410 | 652.590 keV |
| 300 keV | 10 MeV | 200 keV | 776 km/s | 1000.000347410 | 9652.590 keV |
| 360 keV | 1 MeV | 300 keV | 800 km/s | 1000.000385381 | 614.619 keV |
| 360 keV | 10 MeV | 300 keV | 800 km/s | 1000.000385381 | 9614.619 keV |

全部满足 \(W_{\max}<m_{\chi_2}\)。

但是，对 \(\Delta m=1\) MeV，最大 \(W\) 与 pole 的能量间隔只有约 0.615–0.653 MeV。是否可以忽略宽度，要比较的是传播子分母中的两个量：

\[
|m_{\chi_2}^2-W^2|,
\qquad
m_{\chi_2}\Gamma_{\rm pole}
\quad\text{或}\quad
W\Gamma_{\rm run}(W).
\]

仅仅验证 \(W_{\max}<m_{\chi_2}\) 并不能回答宽度是否重要。

---

## 5. 在积分区间上比较 pole width 与 running width

取 \(m_s=300\) keV、\(\Delta m=1\) MeV、\(E_R=200\) keV、\(v=776\) km/s。

此时：

\[
W_{\min}=1000.000300~\mathrm{GeV},
\quad
W_{\max}=1000.000347410~\mathrm{GeV}.
\]

在 \(g_2=1\) 下：

\[
\Gamma_{\rm pole}=0.151824~\mathrm{MeV},
\]

而：

\[
\Gamma_{\rm run}(W_{\max})=0.027899~\mathrm{MeV}.
\]

在 \(g_2=3\) 下：

\[
\Gamma_{\rm pole}=1.366414~\mathrm{MeV},
\]

而：

\[
\Gamma_{\rm run}(W_{\max})=0.251088~\mathrm{MeV}.
\]

因为 \(W\) 只比 \(\chi_1+s\) 阈值高约 0–0.0474 MeV，running width 受到明显的末态相空间抑制；pole width 则在母粒子质量 \(m_{\chi_2}\) 处计算，其可用衰变能量由 \(\Delta m-m_s\) 决定。

### 5.1 最大 \(W\) 处实部失谐量与虚部之比

定义：

\[
R_{\rm pole}
=
\frac{m_{\chi_2}^2-W_{\max}^2}
{m_{\chi_2}\Gamma_{\rm pole}},
\]

\[
R_{\rm run}
=
\frac{m_{\chi_2}^2-W_{\max}^2}
{W_{\max}\Gamma_{\rm run}(W_{\max})}.
\]

\(R\lesssim1\) 表示虚部与实部失谐量同量级；\(R\gg1\) 表示该点的分母主要由实部失谐量控制。

| \(m_s\) | \(\Delta m\) | \(R_{\rm pole}(g_2=1)\) | \(R_{\rm pole}(g_2=3)\) | \(R_{\rm run}(g_2=1)\) | \(R_{\rm run}(g_2=3)\) |
|---:|---:|---:|---:|---:|---:|
| 300 keV | 1 MeV | 8.597 | 0.955 | 46.783 | 5.198 |
| 300 keV | 10 MeV | 12.135 | 1.348 | 691.978 | 76.886 |
| 360 keV | 1 MeV | 8.279 | 0.920 | 56.092 | 6.232 |
| 360 keV | 10 MeV | 12.090 | 1.343 | 877.467 | 97.496 |

因此：

- 对 \(g_2=1\)，pole-width 虚部小于实部失谐量，但在 \(\Delta m=1\) MeV 下并非无限小；
- 对 \(g_2=3\)，\(\Delta m=1\) MeV 时 pole-width 虚部已经与实部失谐量相当；
- running-width 方案在相同点的虚部明显较小；
- \(\Delta m=10\) MeV 时，pole 距离增大，但 pole width 本身也随可用衰变相空间增大，因此不能只根据 \(\Delta m\) 增大就断言宽度效应单调变小。

---

## 6. \(I_6\) 的三种宽度方案数值对照

所有数值均采用：

\[
(n_W,n_z,n_\varphi)=(24,24,16),
\]

并计算公式 (6) 的约化积分 \(I_6\)，单位为 GeV\(^2\)。不包含整体耦合、核响应和媒介传播子前因子。

### 6.1 \(g_2=1\)

| \(m_s\) | \(\Delta m\) | \(I_6\) 零宽度 | \(I_6\) pole-width | pole 相对变化 | \(I_6\) running-width | running 相对变化 |
|---:|---:|---:|---:|---:|---:|---:|
| 300 keV | 1 MeV | 878078.841 | 868227.284 | −1.122% | 877875.033 | −0.0232% |
| 300 keV | 10 MeV | 6998.223 | 6962.200 | −0.515% | 6998.217 | −0.0000941% |
| 360 keV | 1 MeV | 400887.427 | 395846.462 | −1.257% | 400820.231 | −0.0168% |
| 360 keV | 10 MeV | 2967.071 | 2951.612 | −0.521% | 2967.070 | −0.0000592% |

### 6.2 \(g_2=3\)

| \(m_s\) | \(\Delta m\) | \(I_6\) 零宽度 | \(I_6\) pole-width | pole 相对变化 | \(I_6\) running-width | running 相对变化 |
|---:|---:|---:|---:|---:|---:|---:|
| 300 keV | 1 MeV | 878078.841 | 481505.262 | −45.164% | 861978.979 | −1.834% |
| 300 keV | 10 MeV | 6998.223 | 5100.403 | −27.119% | 6997.690 | −0.00762% |
| 360 keV | 1 MeV | 400887.427 | 207824.152 | −48.159% | 395540.068 | −1.334% |
| 360 keV | 10 MeV | 2967.071 | 2155.234 | −27.362% | 2966.929 | −0.00480% |

### 6.3 数值收敛交叉检查

对最敏感的点：

\[
m_s=300~\mathrm{keV},\quad
\Delta m=1~\mathrm{MeV},\quad
g_2=3,
\]

使用更高求积阶数 \((48,40,24)\) 得：

| 宽度方案 | \((24,24,16)\) | \((48,40,24)\) | 相对变化 |
|---|---:|---:|---:|
| zero | 878078.841 | 878071.297 | \(-8.59\times10^{-6}\) |
| pole | 481505.262 | 481500.947 | \(-8.96\times10^{-6}\) |
| running | 861978.979 | 861977.675 | \(-1.51\times10^{-6}\) |

这说明上述宽度对照不是低阶求积误差造成的；至少在该最敏感代表点，三种方案之间的差异远大于求积收敛误差。

---

## 7. 物理解释：为什么 \(\Delta m\) 和宽度方案会产生不同结果？

### 7.1 \(\Delta m\) 改变 pole 的位置

\[
m_{\chi_2}=m_{\chi_1}+\Delta m.
\]

而积分区间 \(W_{\min}\) 和 \(W_{\max}\) 由外部运动学确定，不直接依赖 \(\Delta m\)。因此增大 \(\Delta m\) 会把 pole 推离固定的 \(W\) 积分区间。

### 7.2 但 pole width 也随 \(\Delta m\) 改变

在当前条件性 Dirac 标量模型中：

\[
\Gamma_{\rm pole}
\propto
|g_2|^2
\times
\text{两体末态相空间}.
\]

增大 \(\Delta m\) 会增加 \(\chi_2\to\chi_1s\) 的衰变相空间，因此 pole width 也增大。

所以 \(\Delta m\) 增大同时造成：

- 实部失谐量增大；
- pole width 增大。

最终结果取决于两者的相对变化，而不是只由 pole 距离决定。

### 7.3 running width 为什么在这里较小？

running-width 处方在每个积分点使用当前虚质量 \(W\)，而不是 pole mass \(m_{\chi_2}\)。

当前 benchmark 的 \(W\) 只略高于 \(m_{\chi_1}+m_s\)，故 \(\chi_1+s\) 两体相空间很小：

\[
\Gamma_{\rm run}(W)\ll\Gamma_{\rm pole}.
\]

因此运行宽度的虚部被明显压低，\(I_6\) 更接近零宽度结果。

这不是说 running width 必然是正确答案，而是说明**常数 pole-width 与 running-width 在远离 pole、且接近衰变阈值的离壳区域可能给出显著不同的数值结果**。最终选择必须由完整自能或原作者明确的计算约定决定。

---

## 8. 图注耦合乘积不能确定宽度

Figure 2 图注只给出：

\[
(g_1g_2g_{VN})^2=10^{-8}.
\]

但：

\[
\Gamma_{\rm pole}\propto |g_2|^2.
\]

所以即使该耦合乘积固定，改变 \(g_2\) 并相应改变 \(g_1g_{VN}\)，仍会改变传播子宽度。

例如在 \(m_s=300\) keV、\(\Delta m=1\) MeV 下：

\[
\Gamma_{\rm pole}(g_2=1)=0.1518~\mathrm{MeV},
\]

\[
\Gamma_{\rm pole}(g_2=3)=1.3664~\mathrm{MeV}.
\]

相差 9 倍。对应 pole-width 的 \(I_6\) 也从约 \(8.68\times10^5\) 降到约 \(4.82\times10^5\) GeV\(^2\)。

因此，在没有单独 \(g_2\) 或明确宽度处方时，Figure 2 的有限宽度谱不能由图注的耦合乘积唯一确定。

---

## 9. 本轮结论与未完成事项

### 已完成的 P0-4 第一轮工作

- [x] 零宽度、pole-width、running-width 三种方案的数值实现；
- [x] 对四组 benchmark 进行宽度敏感性比较；
- [x] 检查 \(W_{\max}<m_{\chi_2}\) 在 544–800 km/s 测试速度范围内成立；
- [x] 量化最大 \(W\) 处实部失谐量与虚部的相对大小；
- [x] 检查最敏感点的高阶求积收敛；
- [x] 将宽度模型假设与原稿明确内容分开记录。

### 仍未完成

1. **完整费米子自能**：计算 \(\Sigma(\not K)\) 的实部、虚部及 Dirac 结构；不能把 running-width ansatz 当成它的替代品。
2. **模型定义**：确认 Dirac/Majorana、标量实/复性质、手征与 CP 约定。
3. **原作者宽度输入**：寻找 Figure 2 的 \(g_2\) 或宽度具体处方。
4. **最终 halo 最大速度**：将 \(W_{\max}<m_{\chi_2}\) 检查扩展到最终使用的 \(v_{\max}\)，而不是只限于当前 800 km/s。
5. **完整截面**：仍需核响应 \(\mathcal R_A(E_R)\) 和媒介质量 \(m_V\)。

### 当前不作出的结论

- 不宣称 running-width 一定优于 pole-width；
- 不宣称 Figure 2 的原作者一定采用零宽度或某一种宽度；
- 不将当前 \(I_6\) 直接解释为事件率；
- 不在缺少 \(g_2\) 的情况下从耦合乘积反推出唯一宽度；
- 不把 \(W_{\max}<m_{\chi_2}\) 误解为宽度效应必然可以忽略。

---

## 10. 复现脚本与机器可读结果

本轮宽度扫描由以下脚本统一复现：

```bash
python research/figure2_full_reproduction/run_p0_4_width_scan.py
```

脚本调用 `eq6_kernel.reduced_kernel` 的 `zero`、`pole` 和 `running` 三种宽度方案，并输出：

- `results/P0-4_WIDTH_SENSITIVITY.csv`：四组 benchmark、两种 (g_2) 取值和三种宽度方案的机器可读积分结果；
- `results/P0-4_GLOBAL_WMAX_CHECK.csv`：固定速度后对所有正 (E_R) 优化得到的全局 (W_{max}) 检查。

本报告中的积分结果使用 ((n_W,n_z,n_\varphi)=(24,24,16))。最敏感 benchmark 另以 ((48,40,24)) 做高阶求积交叉检查。

当前 GitHub 分支上的测试文件包含 9 项单元测试；本轮尚未取得对应 GitHub Actions CI 运行结果，因此不将代码状态表述为 CI 已通过。数值表由本轮独立 Python 计算得到，复现脚本已归档，仍需在仓库运行环境实际执行并对照 CSV，作为下一项软件验收。

## 11. 下一步建议

P0-4 的第一轮数值比较已经完成。建议下一步先补齐模型和自能层面的证据：

1. 从完整 UV 相互作用确定 \(\chi_1,\chi_2\) 的统计性质和顶点约定；
2. 独立计算 \(\chi_2\) 的费米子一圈自能 \(\Sigma(\not K)\)；
3. 用同一重整化方案比较 pole 质量、pole width 和离壳传播子；
4. 确定原作者 benchmark 是否给出独立 \(g_2\)；
5. 在上述问题明确后，冻结 P0-4 的传播子处方。

然后进入 P0-5：从 Anand et al. 的 \(W_M^{00}\) 响应恢复氙核 form factor，验证 \(\mathcal R_A(0)=A^2\)，并建立独立核响应实现。

\[
\boxed{
\text{P0-4 第一轮诊断完成；完整自能与模型定义仍是最终定案前置条件。}
}
\]


---

## P0-4b 后续结果：对 running-width 解释的精确化

后续的一圈自能计算已经证明：在 Dirac 费米子、实标量、纯标量 Yukawa 顶点且只保留 \\(\\chi_1+s\\) cut 的条件下，

[
-2\operatorname{Im}\left[
W\Sigma_V(W^2)+\Sigma_S(W^2)
\right]
=\Gamma_{\chi_2^*(W)\to\chi_1s}.
]

因此，本报告中的 running-width 虚部 (W\Gamma(W)) 不是任意的诊断 ansatz，而是该标量道的一圈 absorptive part。

但它仍然不包含 \\(\\operatorname{Re}\\Sigma_V\\)、`\\(\\operatorname{Re}\\Sigma_S\\)`、on-shell counterterms 以及完整的 Dirac 分子结构。完整推导见：

`results/P0-4B_SCALAR_SELF_ENERGY_AUDIT_ZH.md`.

此外，原稿另有 off-diagonal vector interaction。其一圈自能需要 (m_V) 和规范/Goldstone 完成；因此标量道结果不等于全模型总自能。
