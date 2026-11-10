# P0-4b：\(\chi_2\) 一圈费米子自能——标量道完整计算

> 状态：\(\chi_1+s\) 标量道的一圈自能、吸收部、MS-bar 有限部分及实 on-shell 重整化已推导并数值实现。  
> **完整模型自能尚未闭合**：原稿另有 \(g_1V_\mu\bar\chi_2\gamma^\mu\chi_1+\mathrm{h.c.}\) 相互作用，但没有给出 \(m_V\) 和规范/Goldstone 完成，故不能唯一计算该矢量道。  
> 基准分支：\`research/figure2-p0-4-mainline\`。  
> 单位：自然单位制；质量、动量和能量均以 GeV 输入。  
> PV 函数采用 \(\overline{\mathrm{MS}}\) 有限部分，重整化尺度 \(\mu_R=1\) TeV。

---

## 1. 从原稿读取的模型，而不是额外假设

原稿 vector–vector 模型在 Eq. (1) 给出：

\[
\mathcal L_{\mathrm{int}}
=
g_1V^\mu\bar\chi_2\gamma_\mu\chi_1
+
g_2s\bar\chi_2\chi_1
+\mathrm{h.c.}
+
g_{Vq}V^\mu\sum_q\bar q\gamma_\mu q.
\]

原稿在公式 (6) 的振幅中采用：

\[
\frac{\not K+m_{\chi_2}}
{W^2-m_{\chi_2}^2+i m_{\chi_2}\Gamma_{\chi_2}},
\qquad
\Gamma_{\chi_2}=\Gamma(\chi_2\to\chi_1s)
\]

并说明宽度在 pole mass 处计算。

源码位置：

- [模型相互作用 Eq. (1)](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/blob/main/paper-source/main.tex#L94-L121)
- [公式 (6) 的两个传播子与宽度定义](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/blob/main/paper-source/main.tex#L194-L206)

当前原稿明确给出了标量顶点和矢量顶点，但**没有明确说明 \(\chi_1,\chi_2\) 是 Dirac 还是 Majorana，也没有给出完整的手征/CP 约定**。

因此本轮先严格限定为以下可计算子问题：

- \(\chi_1,\chi_2\)：Dirac 费米子；
- \(s\)：实标量；
- \(g_2s\bar\chi_2\chi_1+\mathrm{h.c.}\)：纯标量 Yukawa 顶点；
- 只计算内部 \(\chi_1+s\) 的一圈图；
- 暂不把 \(g_1\) 矢量道混入标量道结果。

若最终模型的粒子统计性质或顶点结构不同，必须重新计算，不能直接沿用本轮数值。

---

## 2. 一圈图与完整 Dirac 分解

考虑外部 \(\chi_2(p)\)，内部传播 \(\chi_1(k)\) 和 \(s(p-k)\)。

定义自能约定：

\[
S^{-1}_{\chi_2}(p)
=
\not p-m_{\chi_2}-\Sigma_{\chi_2}(\not p).
\]

Lorentz 不变性和纯标量顶点给出：

\[
\boxed{
\Sigma_{\chi_2}^{(s)}(\not p)
=
\not p\,\Sigma_V(p^2)+\Sigma_S(p^2)
}
\]

其中 \(\Sigma_V\) 无量纲，\(\Sigma_S\) 的量纲为质量。

采用：

\[
\mathcal L_{\mathrm{int}}\supset
g_2s\bar\chi_2\chi_1+
g_2^*s\bar\chi_1\chi_2,
\]

一圈 1PI 插入为：

\[
-i\Sigma_{\chi_2}^{(s)}(p)
=
|g_2|^2
\int\frac{\mathrm d^dk}{(2\pi)^d}
\frac{\not k+m_{\chi_1}}
{(k^2-m_{\chi_1}^2+i0)
[(p-k)^2-m_s^2+i0]}.
\]

注意：两个顶点给出 \(|g_2|^2\)，不是 \(g_2^2\)。这也是为什么复耦合相位不会出现在这一阶对角自能中。

---

## 3. Passarino–Veltman 约化

定义：

\[
\Delta(x)=
x m_{\chi_1}^2
+(1-x)m_s^2
-x(1-x)p^2-i0.
\]

在本轮采用的动量分配下：

\[
B_0(p^2;m_{\chi_1}^2,m_s^2)
=
\Delta_{\mathrm{UV}}
-\int_0^1\mathrm dx
\ln\frac{\Delta(x)}{\mu_R^2},
\]

\[
B_1(p^2;m_{\chi_1}^2,m_s^2)
=
\frac12\Delta_{\mathrm{UV}}
-\int_0^1\mathrm dx\,(1-x)
\ln\frac{\Delta(x)}{\mu_R^2},
\]

其中：

\[
\Delta_{\mathrm{UV}}
=
\frac1\epsilon-\gamma_E+\ln4\pi.
\]

分子经过 Feynman 参数化和移位 \(k=\ell+(1-x)p\) 后：

\[
\boxed{
\Sigma_V(p^2)
=
-\frac{|g_2|^2}{16\pi^2}B_1(p^2)
}
\]

\[
\boxed{
\Sigma_S(p^2)
=
-\frac{|g_2|^2m_{\chi_1}}{16\pi^2}B_0(p^2)
}
\]

所以：

\[
\boxed{
\Sigma_{\chi_2}^{(s)}(\not p)
=
-\frac{|g_2|^2}{16\pi^2}
\left[
\not p B_1(p^2)+m_{\chi_1}B_0(p^2)
\right].
}
\]

### 3.1 UV pole

发散部分为：

\[
\boxed{
\Sigma_{\mathrm{UV}}^{(s)}
=
-\frac{|g_2|^2}{16\pi^2}
\Delta_{\mathrm{UV}}
\left(\frac12\not p+m_{\chi_1}\right).
}
\]

它由 \(\chi_2\) 的动能和质量 counterterms 吸收。

因此不能只保留 \(m_{\chi_1}B_0\) 的标量项；\(\not p B_1\) 是完整自能的一部分，也会影响传播子 residue 和离壳行为。

### 3.2 有限部分的解析表达式

当：

\[
p^2>(m_{\chi_1}+m_s)^2
\]

时，令：

\[
x_\pm=
\frac{p^2-m_{\chi_1}^2+m_s^2
\pm\sqrt{\lambda_{\mathrm{dimful}}}}
{2p^2},
\]

\[
\lambda_{\mathrm{dimful}}
=
[p^2-(m_{\chi_1}+m_s)^2]
[p^2-(m_{\chi_1}-m_s)^2].
\]

利用：

\[
\ln|\Delta(x)|
=
\ln p^2+\ln|x-x_-|+\ln|x-x_+|,
\]

可将 \(B_0,B_1\) 的实部解析积分，不需要在两个极近的阈值根之间做粗网格积分。

吸收部为：

\[
\boxed{
\operatorname{Im}B_0
=
\pi\frac{\sqrt{\lambda_{\mathrm{dimful}}}}{p^2}
}
\]

\[
\boxed{
\operatorname{Im}B_1
=
\pi\frac{\sqrt{\lambda_{\mathrm{dimful}}}}{p^2}
\frac{p^2+m_{\chi_1}^2-m_s^2}{2p^2}.
}
\]

导数 \(B_0'(p^2),B_1'(p^2)\) 也已解析实现，包括主值实部和 cut 的虚部。

---

## 4. 重要结果：running width 的吸收部是精确的一圈 cut

定义正能量投影：

\[
\delta M(W)
=
W\Sigma_V(W^2)+\Sigma_S(W^2).
\]

由上面的 \(B_0,B_1\) 虚部：

\[
\Gamma_{\mathrm{cut}}(W)
=
-2\operatorname{Im}\delta M(W).
\]

代入后得到：

\[
\boxed{
\Gamma_{\mathrm{cut}}(W)
=
\frac{|g_2|^2}{16\pi W^3}
\sqrt{\lambda_{\mathrm{dimful}}
(W^2,m_{\chi_1}^2,m_s^2)}
\left[(W+m_{\chi_1})^2-m_s^2\right].
}
\]

这正是一个不变质量为 \(W\) 的 Dirac 费米子衰变：

\[
\chi_2^*(W)\to\chi_1+s
\]

的两体衰变宽度。

因此，本轮得到一个比 P0-4a 更强的结论：

\[
\boxed{
\text{上一轮的 }\Gamma_{\mathrm{run}}(W)
\text{ 正是标量道一圈自能的 absorptive part。}
}
\]

它不是任意构造的经验函数。

但必须区分：

- \(iW\Gamma_{\mathrm{run}}(W)\)：正确重现该标量道的一圈吸收部；
- \(\operatorname{Re}\Sigma_V,\operatorname{Re}\Sigma_S\)：还需要同时保留；
- \(\Sigma_V,\Sigma_S\) 的 Dirac 结构：不能简单压缩成一个标量宽度。

因此，**running-width Breit–Wigner 只补齐了吸收部，还不是完整一圈传播子。**

---

## 5. Pole benchmark 的数值结果

取：

\[
m_{\chi_1}=1000~\mathrm{GeV},\qquad
\mu_R=1000~\mathrm{GeV}.
\]

以下 \(B_0,B_1\) 是 \(\overline{\mathrm{MS}}\) 有限部分；宽度按一圈 cut 计算。

| Benchmark | \(B_0^{\rm fin}\) | \(B_1^{\rm fin}\) | \(\Gamma_{\rm cut}(g_2=1)\) |
|---|---:|---:|---:|
| 300 keV, 1 MeV | \(2.000026464+i\,5.994\times10^{-6}\) | \(1.500025464+i\,5.994\times10^{-6}\) | 0.151824 MeV |
| 300 keV, 10 MeV | \(2.000216435+i\,6.280\times10^{-5}\) | \(1.500206433+i\,6.280\times10^{-5}\) | 1.590809 MeV |
| 360 keV, 1 MeV | \(2.000026538+i\,5.862\times10^{-6}\) | \(1.500025538+i\,5.862\times10^{-6}\) | 0.148484 MeV |
| 360 keV, 10 MeV | \(2.000216451+i\,6.279\times10^{-5}\) | \(1.500206449+i\,6.279\times10^{-5}\) | 1.590494 MeV |

宽度按 \(|g_2|^2\) 缩放：

| Benchmark | \(g_2=0.1\) | \(g_2=1\) | \(g_2=3\) |
|---|---:|---:|---:|
| 300 keV, 1 MeV | 0.001518 MeV | 0.151824 MeV | 1.366415 MeV |
| 300 keV, 10 MeV | 0.015908 MeV | 1.590809 MeV | 14.317283 MeV |
| 360 keV, 1 MeV | 0.001485 MeV | 0.148484 MeV | 1.336354 MeV |
| 360 keV, 10 MeV | 0.015905 MeV | 1.590494 MeV | 14.314445 MeV |

### 5.1 与原来的两体宽度公式逐点对照

对四组 benchmark 和 \(g_2=0.1,1,3\)，数值验证：

\[
\frac{\Gamma_{\mathrm{cut}}(m_{\chi_2})}
{\Gamma_{\mathrm{two-body}}(m_{\chi_2})}
=1
\]

在双精度数值精度内成立。

这意味着上一轮使用的 Dirac 纯标量两体宽度公式，确实是该一圈图的正确 absorptive part。

---

## 6. 重整化：不能把 \(\overline{\mathrm{MS}}\) 质量修正当作物理质量

在 \(\mu_R=1\) TeV 下，pole 处的 \(\overline{\mathrm{MS}}\) 有限质量投影：

\[
\delta M_{\overline{\mathrm{MS}}}
=
m_{\chi_2}\Sigma_V(m_{\chi_2}^2)
+\Sigma_S(m_{\chi_2}^2).
\]

例如：

| \(g_2\) | \(\operatorname{Re}\delta M_{\overline{\mathrm{MS}}}\) |
|---:|---:|
| 0.1 | 约 \(-0.222\) GeV |
| 1 | 约 \(-22.16\) GeV |
| 3 | 约 \(-199.48\) GeV |

这些数值依赖 \(\mu_R\) 和重整化方案，**不是预测 \(m_{\chi_2}\) 会发生 22 GeV 或 199 GeV 的物理移动**。

因为原稿把 \(m_{\chi_2}\) 作为物理 pole mass 输入，本轮进一步构造实 on-shell counterterms。

在本报告的自能符号约定下，定义：

\[
\Sigma=\not p\Sigma_V+\Sigma_S,
\]

\[
\Gamma_R^{(2)}
=
(1+\delta Z-\Sigma_V)\not p
-
\left[
M+M\delta Z+\delta m+\Sigma_S
\right],
\]

其中 \(M=m_{\chi_1}+\Delta m\)。

由实 pole 质量条件和单位 residue 条件得到：

\[
\boxed{
\delta m_{\mathrm{OS}}
=
-\operatorname{Re}
\left[M\Sigma_V(M^2)+\Sigma_S(M^2)\right]
}
\]

\[
\boxed{
\delta Z_{\mathrm{OS}}
=
\operatorname{Re}
\left[
\Sigma_V(M^2)
+M^2\Sigma'_V(M^2)
+M\Sigma'_S(M^2)
\right].
}
\]

注意这里的 \(\delta Z_{\mathrm{OS}}\) 是由完整 Dirac 逆传播子行列式的 residue 条件得到的，不是只对正能量质量投影求导。

### 6.1 On-shell counterterm 的数值

| Benchmark | \(\delta Z_{\rm OS}(g_2=1)\) | \(\delta Z_{\rm OS}(g_2=3)\) |
|---|---:|---:|
| 300 keV, 1 MeV | −0.1590 | −1.4311 |
| 300 keV, 10 MeV | −0.1307 | −1.1761 |
| 360 keV, 1 MeV | −0.1588 | −1.4289 |
| 360 keV, 10 MeV | −0.1307 | −1.1760 |

这是一个重要的扰动论诊断：

- \(g_2=0.1\)：\(|\delta Z|\sim10^{-3}\)，一圈修正很小；
- \(g_2=1\)：\(|\delta Z|\sim0.13\)–0.16，阈值附近的波函数修正不可忽略；
- \(g_2=3\)：\(|\delta Z|>1\)，一圈展开已没有明显的扰动论控制。

因此此前用 \(g_2=3\) 做宽度敏感性测试是有价值的压力测试，但不能把它当成已经通过微扰论验收的 benchmark。

---

## 7. 完整标量道 Dirac 传播子

定义 on-shell 重整化后的 form factors：

\[
\Sigma_V^R=\Sigma_V-\delta Z_{\rm OS},
\]

\[
\Sigma_S^R=\Sigma_S+M\delta Z_{\rm OS}+\delta m_{\rm OS}.
\]

则标量道一圈自能重求和后的传播子为：

\[
\boxed{
S_{\chi_2}^R(K)
=
i\,
\frac{
[1-\Sigma_V^R(W^2)]\not K+
[M+\Sigma_S^R(W^2)]
}{
[1-\Sigma_V^R(W^2)]^2W^2-
[M+\Sigma_S^R(W^2)]^2
}.
}
\]

这里的分母包含完整的 \(\Sigma_V\) 和 \(\Sigma_S\)，不是简单把常数宽度放进 \(W^2-M^2\)。

若只保留一致的一圈阶，逆传播子分母展开为：

\[
D_{\rm 1loop}(W^2)
=
W^2-M^2
-2W^2\Sigma_V^R(W^2)
-2M\Sigma_S^R(W^2).
\]

Dyson-resummed determinant 也已在程序中保留作诊断，但它会自动包含一圈自能的高次幂；当 \(|\delta Z|\gtrsim1\) 时，不能将这种部分重求和当作受控结果。

在 pole 处：

\[
\operatorname{Re}D_{\rm 1loop}(M^2)=0,
\]

\[
\boxed{
D_{\rm 1loop}(M^2)
=
iM\Gamma_{\rm pole}
}
\]

在数值精度内严格成立。

---

## 8. 离壳积分区间内的实部修正

取前一轮四组 benchmark 的 \(W_{\max}\)，比较：

\[
D_{\rm base}=W_{\max}^2-M^2,
\]

\[
D_{\rm run}=D_{\rm base}+iW_{\max}\Gamma(W_{\max}),
\]

以及完整标量道一圈 on-shell 逆传播子 \(D_{\rm 1loop}\)。

### 8.1 \(g_2=1\)

| Benchmark | \(D_{\rm base}\) (GeV\(^2\)) | \(D_{\rm 1loop}\) (GeV\(^2\)) | 实部修正 |
|---|---:|---:|---:|
| 300 keV, 1 MeV | −1.305180 | \(-1.317552+i\,0.027883\) | 0.948% |
| 300 keV, 10 MeV | −19.305279 | \(-19.727257+i\,0.027884\) | 2.186% |
| 360 keV, 1 MeV | −1.229238 | \(-1.239633+i\,0.021891\) | 0.846% |
| 360 keV, 10 MeV | −19.229337 | \(-19.643255+i\,0.021891\) | 2.153% |

### 8.2 与 running-width 方案的关系

在这四个点：

\[
\operatorname{Im}D_{\rm 1loop}
=
W_{\max}\Gamma(W_{\max})
\]

在数值精度内成立。

因此，P0-4a 的 running-width 方案准确重现了标量道的一圈吸收部；它缺少的是实部色散修正和完整的 Dirac 分子结构。

对 \(g_2=0.1\)，实部修正只有约 \(0.008\%\)–\(0.022\%\)。

对 \(g_2=3\)，一圈线性化实部修正约为 \(7.6\%\)–\(19.7\%\)，同时 \(|\delta Z|>1\)。因此该区域不应继续用一圈结果给出精确的完整截面结论。

---

## 9. 必须补充的矢量道：当前不能宣称整个模型自能已完成

原稿还包含：

\[
g_1V^\mu\bar\chi_2\gamma_\mu\chi_1+\mathrm{h.c.}
\]

它在一圈阶产生另一个自能：

\[
\Sigma_{\chi_2}^{(V)}(p)
\sim
|g_1|^2
\int\frac{\mathrm d^dk}{(2\pi)^d}
\frac{
\gamma^\mu(\not k+m_{\chi_1})\gamma^\nu
D_{\mu\nu}(p-k)
}{
k^2-m_{\chi_1}^2
}.
\]

这项不能仅凭现有 \(\mathcal L_{\rm int}\) 唯一计算，原因有三点：

1. 原稿没有给出 \(m_V\) 的 benchmark 数值；
2. 没有给出矢量传播子的规范选择和完整规范/Goldstone 相互作用；
3. \(\chi_1\)-\(\chi_2\) 矢量流在质量不相等时不是守恒流：

\[
q_\mu\bar\chi_2\gamma^\mu\chi_1
=
(m_{\chi_2}-m_{\chi_1})
\bar\chi_2\chi_1
\]

（外线满足自由 Dirac 方程时）。

因此纵向矢量传播子不能无条件丢掉，单独用 Feynman gauge 的 \(g_{\mu\nu}\) 项也不能自动代表 gauge-independent 的完整答案。

此外：

- 若 \(m_V>\Delta m\)，\(\chi_2\to\chi_1V\) 的实衰变道关闭，但矢量圈图仍会贡献实部；
- 若 \(m_V<\Delta m\)，该衰变道打开，原稿只写 \(\Gamma(\chi_2\to\chi_1s)\) 的宽度定义就需要重新审查是否遗漏总宽度。

因此本轮准确的状态是：

<badge color="success">标量道一圈自能完成</badge>

<badge color="warning">全模型一圈自能待矢量道输入</badge>

这不是计算技术上的障碍，而是原稿尚未提供足够的 UV/gauge 输入。

---

## 10. 数值实现与可复现文件

新增程序：

- \`chi2_scalar_self_energy.py\)：\(B_0,B_1\)、导数、\(\Sigma_V,\Sigma_S\)、cut 宽度和 OS counterterms；
- \`run_p0_4b_scalar_self_energy.py\)：四组 benchmark 与三组 \(g_2\) 的扫描；
- \`tests/test_chi2_scalar_self_energy.py\)：PV 数值、阈值、cut-width identity 和 pole renormalization 测试。

运行：

\`\`\`bash
python -m unittest discover -s research/figure2_full_reproduction/tests -v
python research/figure2_full_reproduction/run_p0_4b_scalar_self_energy.py
\`\`\`

扫描结果输出：

- \`results/P0-4B_SCALAR_SELF_ENERGY.csv\)
- \`results/P0-4B_OS_DENOMINATOR_COMPARISON.csv\)

本轮解析公式、阈值 cut 和数值基准已经通过独立计算交叉检查；仓库中的新增测试尚需实际运行并取得 CI 状态，不能预先标记为 CI 通过。

---

## 11. 本轮结论与下一步

### 已完成

- [x] 从原稿 \(g_2s\bar\chi_2\chi_1+\mathrm{h.c.}\) 推导完整标量道一圈自能；
- [x] 得到 \(\Sigma_V\) 和 \(\Sigma_S\) 两个独立 Dirac form factors；
- [x] 分离 UV pole 和 \(\overline{\mathrm{MS}}\) 有限部分；
- [x] 解析计算 \(B_0,B_1\) 的吸收部；
- [x] 证明 running width 是该标量道的一圈 absorptive part；
- [x] 计算导数并建立实 on-shell mass/residue counterterms；
- [x] 得到完整标量道 Dirac 传播子；
- [x] 量化离壳区间的色散实部修正；
- [x] 识别 \(g_2=3\) 在当前近阈值 benchmark 下的扰动论失控迹象。

### 尚未完成

1. \(g_1V_\mu\bar\chi_2\gamma^\mu\chi_1\) 矢量道自能；
2. \(\chi_1,\chi_2\) 的 Dirac/Majorana 性质最终确认；
3. \(m_V\)、矢量传播子和 Goldstone 相互作用；
4. 将完整矩阵传播子代入公式 (6)，而不是只替换分母；
5. 对完整振幅做一圈修正后的求积收敛测试。

### 下一步

先闭合矢量道的模型定义，再把：

\[
\Sigma_{\chi_2}
=
\Sigma_{\chi_2}^{(s)}
+
\Sigma_{\chi_2}^{(V)}
+\text{必要的 counterterms}
\]

组合成完整模型的重整化自能。

随后才把完整的 \(S_{\chi_2}^R(K)\) 代入公式 (6) 的 after-emission 图，重新计算 \(I_6\)，与零宽度、pole-width 和 running-width 结果逐点比较。

\[
\boxed{
\text{P0-4b 的标量道已完成；全模型定案需要矢量道的 }m_V
\text{ 与 gauge completion。}
}
\]
