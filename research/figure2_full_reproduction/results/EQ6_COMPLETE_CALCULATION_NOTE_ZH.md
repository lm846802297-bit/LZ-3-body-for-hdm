# Figure 2 与公式 (6) 独立计算：完整推导、数值结果及审计记录

> 文档性质：研究过程记录与数值审计，不是最终物理结论，也不代表已经复现 LZ 事件率。  
> 计算分支：\`research/figure2-eq6-kernel\`  
> 主要代码：\`research/figure2_full_reproduction/eq6_kernel.py\`  
> 参考源码：\`paper-source/main.tex\`  
> 单位约定：自然单位制 \(\hbar=c=1\)，程序内部质量和能量均以 GeV 输入。

---

## 0. 摘要与结论边界

本轮工作分为两个彼此独立、但逻辑上衔接的计算层次：

1. **三体散射运动学审计**：给定暗物质入射速度 \(v\) 和核反冲能量 \(E_R\)，确定末态 \(\chi_1+s\) 系统允许的不变质量区间，并检验 Figure 2 图例中的 300、360 MeV 是否可能对应非零三体相空间。
2. **公式 (6) 的独立数值核**：在明确采用 Dirac 外线自旋器的基准假设下，重建三体末态四动量，计算两张图的完整 Dirac trace（包含干涉），并对 \(W^2,z,\varphi_*\) 进行数值积分。

当前可以确认：

- 在 \(m_{\chi_1}=1\) TeV、\(m_A=122\) GeV 的运动学基准下，速度为 544–800 km/s 时，最大允许标量质量约为 179–387 keV。
- 300 keV 和 360 keV 在高速端具有非空相空间；300 MeV 和 360 MeV 在本轮测试的 544–800 km/s 速度区间内没有三体相空间。
- Dirac trace 与显式四种初末态自旋组合求和在代表点符合，相对差异约 \(3.9\times10^{-16}\)。
- 代表性 \(W^2,z,\varphi_*\) 积分随求积阶数增加呈现收敛；最高两组求积结果的相对差异约 \(9.1\times10^{-7}\)。
- Breit–Wigner 宽度对积分有可见影响，而且宽度依赖单独的 \(g_2\)。Figure 2 图注给出的耦合乘积不能单独确定该宽度。

当前**尚未**得到完整的 \(d\sigma_A/dE_R\)，更没有得到 \(dR/dE_R\) 或复现 Figure 2 的事件率曲线。原因是仍缺少明确的粒子统计性质/顶点约定、独立 \(g_2\) 或宽度处方、媒介质量 \(m_V\) 和数值核响应 \(\mathcal R_A(E_R)\)。

本文件中所有数值均标明其计算层次，不能把“运动学允许”“约化相空间积分”与“实验事件率”混为一谈。

---

## 1. 原稿提供的信息与本轮采用的输入

### 1.1 原稿中可以直接读取的模型信息

当前 \`paper-source/main.tex\` 的 vector–vector 模型给出相互作用：

\[
\mathcal L_{\mathrm{int}}
=
g_1 V^\mu\bar\chi_2\gamma_\mu\chi_1
+g_2s\bar\chi_2\chi_1+\mathrm{h.c.}
+g_{Vq}V^\mu\sum_q\bar q\gamma_\mu q.
\]

并定义：

\[
g_{VN}=3g_{Vq},\qquad
\Delta m=m_{\chi_2}-m_{\chi_1}.
\]

Figure 2 图注明确给出：

\[
m_{\chi_1}=1~\mathrm{TeV},
\qquad
(g_1g_2g_{VN})^2=10^{-8}.
\]

原稿还写明：

- 标量 \(s\) 被假设为 sub-MeV；
- 采用相干核电荷响应；
- \(g_p=g_n=g_{VN}\)；
- \(\mathcal R_A(0)=A^2\)；
- 传播子分母含 \(m_V^2+2m_AE_R\)；
- 第二个暗费米子传播子使用 pole-width 形式；
- 运动学区域要求 \(W_{\max}<m_{\chi_2}\)，以排除真实的 on-shell \(\chi_2\) 产生。

### 1.2 本轮数值计算的输入

| 输入 | 数值 | 性质 |
|---|---:|---|
| \(m_{\chi_1}\) | \(1000\) GeV | Figure 2 图注 |
| \(m_A\) | \(122\) GeV | Xe-131 核质量的近似值，仅作运动学诊断 |
| \(\Delta m\) | \(1\) 或 \(10\) MeV | Figure 2 benchmark 讨论所用值 |
| \(m_s\) | \(200,300,360\) keV | 检验图例单位的候选值 |
| \(v\) | \(544,600,770,776,800\) km/s | 运动学敏感性测试点 |
| \(E_R\) | 由运动学求根或指定 benchmark | 核反冲能量 |
| \(\Gamma_{\chi_2}\) | 先取 0，再按条件性 Dirac 宽度计算 | 独立诊断输入 |

速度转换为自然单位时使用：

\[
v_{\mathrm{natural}}=\frac{v_{\mathrm{km/s}}}{299792.458}.
\]

**重要限制：** \(m_A=122\) GeV 是单一氙核近似，不是天然氙同位素混合物的完整核响应计算。它足以用于本轮运动学量级和相空间审计，但不能替代最终 LZ 核响应。

---

## 2. 三体运动学：\(W_{\min}\)、\(W_{\max}\) 的推导

考虑：

\[
\chi_1(p)+A(P)\longrightarrow
\chi_1(p')+A(P')+s(k).
\]

定义核反冲四动量：

\[
q=P'-P,\qquad t=q^2=-2m_AE_R,
\]

其中靶核初始静止：

\[
P=(m_A,\mathbf 0).
\]

因此：

\[
q^0=E_R,\qquad
|\mathbf q|=\sqrt{2m_AE_R+E_R^2}.
\]

定义末态暗物质与标量组成的总四动量：

\[
K=p-q=p'+k,\qquad W^2=K^2=(p'+k)^2.
\]

在靶核静止系取入射暗物质沿 \(z\) 轴：

\[
p=(E_{\chi_1},0,0,p_{\chi_1}),
\]

并将 \(\mathbf q\) 与入射方向的夹角记为 \(\theta_q\)。由 \(K=p-q\) 得：

\[
W^2
=m_{\chi_1}^2
+2p_{\chi_1}|\mathbf q|\cos\theta_q
-2(E_{\chi_1}+m_A)E_R.
\]

由于 \(-1\leq\cos\theta_q\leq1\)，固定 \(v,E_R\) 时最大的 \(W^2\) 出现在 \(\cos\theta_q=1\)：

\[
\boxed{
W_{\max}^2=
m_{\chi_1}^2
+2p_{\chi_1}\sqrt{2m_AE_R+E_R^2}
-2(E_{\chi_1}+m_A)E_R
}.
\]

末态 \(\chi_1+s\) 的最小不变质量由两者在质心系静止时取得：

\[
\boxed{W_{\min}^2=(m_{\chi_1}+m_s)^2.}
\]

所以三体相空间非空的必要条件是：

\[
\boxed{W_{\max}^2(v,E_R)\geq(m_{\chi_1}+m_s)^2.}
\]

给定 \(v,E_R\)，最大允许标量质量为：

\[
\boxed{
m_s^{\max}(v,E_R)=
\sqrt{W_{\max}^2(v,E_R)}-m_{\chi_1}
}
\]

（仅当根号内的运动学上限足以打开末态时使用）。

### 2.1 对核反冲能量优化，得到最大可产生标量质量

对固定入射速度 \(v\)，在物理允许的 \(E_R\) 范围内最大化 \(m_s^{\max}(v,E_R)\)。得到：

| 入射速度 | 最大允许 \(m_s\) | 达到最大值的 \(E_R\) |
|---:|---:|---:|
| 544 km/s | 179.0 keV | 159.6 keV |
| 600 km/s | 217.8 keV | 194.1 keV |
| 770 km/s | 358.7 keV | 319.7 keV |
| 776 km/s | 364.3 keV | 324.7 keV |
| 800 km/s | 387.1 keV | 345.1 keV |

这里的“最佳 \(E_R\)”只表示：**在给定入射速度下，使运动学允许的最大 \(m_s\) 达到最大值的核反冲能量。** 它不是 LZ 探测效率最佳点，也不是 \(dR/dE_R\) 的峰值。

### 2.2 固定 \(m_s\) 后，允许的核反冲能量范围

求解：

\[
W_{\max}^2(v,E_R)=(m_{\chi_1}+m_s)^2
\]

得到相空间开启和关闭的两个边界。结果为：

| \(v\) | \(m_s\) | 允许的 \(E_R\) 区间 |
|---:|---:|---:|
| 776 km/s | 200 keV | 35.0–907.1 keV |
| 776 km/s | 300 keV | 109.2–654.7 keV |
| 776 km/s | 360 keV | 258.2–398.7 keV |
| 800 km/s | 200 keV | 32.0–991.7 keV |
| 800 km/s | 300 keV | 95.3–750.1 keV |
| 800 km/s | 360 keV | 186.5–552.0 keV |

这说明较大的 \(m_s\) 不仅要求更高的入射速度，而且会压缩允许的 \(E_R\) 区间。

### 2.3 指定标量质量所需的最低入射速度

对 \(E_R\) 优化后，求解：

\[
\max_{E_R}m_s^{\max}(v,E_R)=m_s
\]

得到：

| \(m_s\) | 最低入射速度（约） |
|---:|---:|
| 200 keV | 575.00 km/s |
| 300 keV | 704.23 km/s |
| 360 keV | 771.44 km/s |

因此，360 keV benchmark 只在非常高速的入射粒子中打开相空间。实际事件率还要乘上 halo 速度分布权重，不能仅由相空间开启推断事件数。

### 2.4 对 Figure 2 图例 MeV/keV 问题的判断

在本轮测试速度范围 \(544\)–\(800\) km/s 内，最大允许质量从约 \(179\) keV 增加到约 \(387\) keV。

因此：

- 若图例质量实际为 300 keV、360 keV，则高速端存在非空相空间；
- 若图例质量确实为 300 MeV、360 MeV，则在本轮测试速度范围内 \(W_{\max}<W_{\min}\)，三体积分区间为空。

在 \(v=800\) km/s 时：

\[
m_s^{\max}\simeq387.1~\mathrm{keV}.
\]

这比 300 MeV 和 360 MeV 分别小约三个数量级。故**运动学证据强烈支持 300/360 keV 假设，而不支持在该速度范围内按 MeV 解释**。

但这个结果只证明运动学一致性，不是原作者绘图输入的直接证据。最终确认仍需追踪原始绘图脚本和参数文件；在获得证据前不修改原图图例。

---

## 3. 公式 (6)：从振幅到微分截面的结构

原稿考虑的两个标量发射位置分别是矢量交换之前和之后。按原稿定义：

\[
\Gamma^\mu=\Gamma^\mu_{\mathrm{before}}
+\Gamma^\mu_{\mathrm{after}},
\]

其中：

\[
\Gamma^\mu_{\mathrm{before}}
=
\frac{\gamma^\mu(\not p-\not k+m_{\chi_2})}
{(p-k)^2-m_{\chi_2}^2},
\]

\[
\Gamma^\mu_{\mathrm{after}}
=
\frac{(\not p'+\not k+m_{\chi_2})\gamma^\mu}
{W^2-m_{\chi_2}^2+i m_{\chi_2}\Gamma_{\chi_2}}.
\]

第二项含 pole-width 形式。第一项在当前源码中没有加入有限宽度。

核电荷流的非相对论主导近似选取靶核静止系时间分量 \(\Gamma^0\)。原稿定义：

\[
\mathcal L_{00}
=
\frac12\sum_{\mathrm{spins}}
|\bar u(p')\Gamma^0u(p)|^2.
\]

完整公式为：

\[
\begin{aligned}
\frac{d\sigma_A}{dE_R}
={}&
\frac{m_A(g_1g_2g_{VN})^2}
{256\pi^3p_{\chi_1}^2}
\frac{\mathcal R_A(E_R)}
{(m_V^2+2m_AE_R)^2}
\\
&\times
\int_{W_{\min}^2}^{W_{\max}^2}dW^2
\sqrt{\lambda(W^2,m_{\chi_1}^2,m_s^2)}
\int_{-1}^{1}dz\,
\langle\mathcal L_{00}\rangle_{\varphi_*}.
\end{aligned}
\tag{6}
\]

本轮程序只计算公式 (6) 的积分部分：

\[
\boxed{
I_6(v,E_R)=
\int_{W_{\min}^2}^{W_{\max}^2}dW^2
\sqrt{\lambda}
\int_{-1}^{1}dz\,
\langle\mathcal L_{00}\rangle_{\varphi_*}
}.
\]

它不包含前面的耦合、核响应和媒介传播子整体因子。

### 3.1 自旋迹的矩阵表达式

采用 Dirac 外线自旋器基准：

\[
\boxed{
\mathcal L_{00}
=
\frac12\operatorname{Tr}
\left[
(\not p'+m_{\chi_1})
\Gamma^0
(\not p+m_{\chi_1})
\overline{\Gamma}^{\,0}
\right]
}
\]

其中：

\[
\overline{\Gamma}^{\,0}
=\gamma^0(\Gamma^0)^\dagger\gamma^0.
\]

将两张图分别记为 \(\Gamma_1^0,\Gamma_2^0\)，则：

\[
\mathcal L_{00}
=
\mathcal L_{11}+\mathcal L_{22}+\mathcal L_{12}.
\]

这里 \(\mathcal L_{12}\) 是两张图的相干干涉贡献。程序通过计算完整振幅的 trace，再减去两张单图 trace，得到干涉项；不是将两个单图平方后直接相加。

### 3.2 Dirac 矩阵约定

程序采用 Dirac 表象：

\[
\gamma^0=
\begin{pmatrix}
I&0\\0&-I
\end{pmatrix},
\qquad
\gamma^i=
\begin{pmatrix}
0&\sigma^i\\-\sigma^i&0
\end{pmatrix}.
\]

并使用：

\[
\not p=\gamma^0p^0-\gamma^1p^1-\gamma^2p^2-\gamma^3p^3.
\]

初态自旋平均因子 \(1/2\) 只放在 trace 定义中一次；末态自旋求和由完备关系：

\[
\sum_su(p,s)\bar u(p,s)=\not p+m
\]

实现。

### 3.3 模型定义边界

当前源码的相互作用含有 \(\bar\chi_2\gamma_\mu\chi_1\) 和 \(\bar\chi_2\chi_1\) 及其 hermitian conjugate，但当前相关段落没有明确规定 \(\chi_1,\chi_2\) 是 Dirac 还是 Majorana 费米子，也没有完整列出所有手征、CP 和场相位约定。

因此本轮计算明确标记为：

> **Dirac 外线自旋器 + 原稿所写费米子流的基准实现。**

这不是对原模型粒子统计性质的最终判定。若底层粒子为 Majorana，必须重新检查顶点、反对称化、可能的因子和干涉结构；不能直接把当前 Dirac 结果当作 Majorana 结果。

---

## 4. 三体末态四动量重建

数值积分需要在每个 \((W^2,z,\varphi_*)\) 点构造 \(p',k\)，并保证它们处于正确的质量壳上。

### 4.1 靶核静止系中的核反冲方向

取：

\[
p=(E_{\chi_1},0,0,p_{\chi_1}),
\]

\[
q=(E_R,|\mathbf q|\sin\theta_q,0,
|\mathbf q|\cos\theta_q).
\]

由 \(K=p-q\) 和 \(K^2=W^2\) 得：

\[
\cos\theta_q=
\frac{W^2-m_{\chi_1}^2+
2(E_{\chi_1}+m_A)E_R}
{2p_{\chi_1}|\mathbf q|}.
\]

积分范围由 \(|\cos\theta_q|\leq1\) 限制；上限 \(W_{\max}\) 对应 \(\cos\theta_q=1\)。

### 4.2 在 \(\chi_1+s\) 质心系构造两体末态

令 \(W=\sqrt{W^2}\)。在 \(K\) 的静止系中：

\[
E_{s*}=
\frac{W^2-m_{\chi_1}^2+m_s^2}{2W},
\]

\[
E_{\chi_1*}=
\frac{W^2+m_{\chi_1}^2-m_s^2}{2W},
\]

\[
|\mathbf k_*|=
\frac{\sqrt{\lambda_{\mathrm{dimful}}}}
{2W},
\]

其中：

\[
\lambda_{\mathrm{dimful}}
=
[W^2-(m_{\chi_1}+m_s)^2]
[W^2-(m_{\chi_1}-m_s)^2].
\]

\(\mathbf k_*\) 的方向由 \(z=\cos\theta_*\) 和 \(\varphi_*\) 指定，极轴沿该质心系中的入射 \(\chi_1\) 方向。随后对 \(p'_*,k_*\) 使用 \(K\) 的速度作 Lorentz boost，返回靶核静止系。

这一步确保 \(\Gamma^0\) 确实在原稿指定的靶核静止系计算，而不是把不同参考系的时间分量混用。

### 4.3 数值检查点的质量壳和四动量守恒

代表点取：

\[
\begin{aligned}
m_{\chi_1}&=1000~\mathrm{GeV},&
m_s&=3.0\times10^{-4}~\mathrm{GeV},\\
\Delta m&=1.0\times10^{-3}~\mathrm{GeV},&
m_A&=122~\mathrm{GeV},\\
E_R&=2.0\times10^{-4}~\mathrm{GeV},&
v&=776~\mathrm{km/s},\\
z&=0.2,&
\varphi_*&=1.1.
\end{aligned}
\]

取 \(W^2\) 积分区间中点。检查结果：

| 检查量 | 残差 |
|---|---:|
| \(p^2-m_{\chi_1}^2\) | \(-2.33\times10^{-10}\ \mathrm{GeV}^2\) |
| \(p'^2-m_{\chi_1}^2\) | \(-1.16\times10^{-10}\ \mathrm{GeV}^2\) |
| \(k^2-m_s^2\) | \(2.44\times10^{-17}\ \mathrm{GeV}^2\) |
| \(P'^2-m_A^2\) | \(1.82\times10^{-12}\ \mathrm{GeV}^2\) |
| \(K^2-W^2\) | \(-1.16\times10^{-10}\ \mathrm{GeV}^2\) |
| 四动量守恒的最大分量残差 | \(9.91\times10^{-14}\ \mathrm{GeV}\) |

这些残差与双精度浮点计算和当前大质量、小能量差的数值条件相符。它们验证的是代表点的运动学重建，不等价于所有积分点的全局误差证明。

---

## 5. Dirac trace 的独立交叉验证

在上述代表点、\(\Gamma_{\chi_2}=0\) 下，计算两张图的 trace 分解：

| 贡献 | \(\mathcal L_{00}\) |
|---|---:|
| before 图 \(\mathcal L_{11}\) | \(2.2828830\times10^{12}\) |
| after 图 \(\mathcal L_{22}\) | \(8.7456187\times10^{12}\) |
| 干涉项 \(\mathcal L_{12}\) | \(8.9364924\times10^{12}\) |
| 完整振幅 \(\mathcal L_{00}\) | \(1.9964994\times10^{13}\) |

数值满足：

\[
\mathcal L_{11}+\mathcal L_{22}+\mathcal L_{12}
=\mathcal L_{00}.
\]

本点干涉项为正且不可忽略。因此，若把两个图的贡献非相干相加，会丢失一个与单图贡献同量级的项。

### 5.1 显式自旋器求和

另外使用：

\[
u(p,s)=
\sqrt{E+m}
\begin{pmatrix}
\xi_s\\
\frac{\boldsymbol\sigma\cdot\mathbf p}{E+m}\xi_s
\end{pmatrix}
\]

显式构造两个初态和两个末态自旋态，计算：

\[
\frac12\sum_{s,s'}
|\bar u(p',s')\Gamma^0u(p,s)|^2.
\]

与 trace 结果比较：

\[
\frac{\mathcal L_{\mathrm{explicit}}-
\mathcal L_{\mathrm{trace}}}
{\mathcal L_{\mathrm{trace}}}
\simeq-3.9\times10^{-16}.
\]

这验证了该代表点上的 gamma 矩阵、Dirac 共轭、初态自旋平均和末态自旋求和的一致性。

**解释边界：** 这是对同一套 Dirac 振幅的两种数值实现交叉检查，并不是独立的解析振幅推导，也不能解决 Dirac/Majorana 模型定义尚未明确的问题。

---

## 6. 公式 (6) 的三重积分与收敛性

程序计算：

\[
I_6=
\int_{W_{\min}^2}^{W_{\max}^2}dW^2
\sqrt{\lambda}
\int_{-1}^{1}dz\,
\langle\mathcal L_{00}\rangle_{\varphi_*}.
\]

数值策略：

- \(W^2\)：Gauss–Legendre 求积；
- \(z\in[-1,1]\)：Gauss–Legendre 求积；
- \(\varphi_*\in[0,2\pi]\)：将 Gauss–Legendre 节点映射到完整方位角区间，并按 \(1/(2\pi)\) 进行方位角平均。

这里 \(\lambda\) 是原稿定义的无量纲 Källén 函数：

\[
\lambda(W^2,m_{\chi_1}^2,m_s^2)
=
\left[1-\frac{(m_{\chi_1}+m_s)^2}{W^2}\right]
\left[1-\frac{(m_{\chi_1}-m_s)^2}{W^2}\right].
\]

注意不要将它与上一节的有量纲 \(\lambda_{\mathrm{dimful}}\) 混淆：

\[
\lambda_{\mathrm{dimful}}=W^4\lambda.
\]

### 6.1 代表点求积收敛

使用第 4 节的代表点，先取零宽度：

| \(n_W\) | \(n_z\) | \(n_\varphi\) | \(I_6\)（GeV\(^2\)） |
|---:|---:|---:|---:|
| 16 | 16 | 8 | 878098.5567 |
| 24 | 24 | 16 | 878078.8408 |
| 32 | 32 | 16 | 878073.8896 |
| 40 | 32 | 20 | 878072.0973 |
| 48 | 40 | 24 | 878071.2968 |

最高两组结果的相对差异：

\[
\frac{|878072.0973-878071.2968|}
{878071.2968}
\simeq9.1\times10^{-7}.
\]

这表明该代表点的三重积分对当前求积阶数已经稳定。

### 6.2 量纲检查

在当前约定下，\(\Gamma^\mu\) 的量纲为 GeV\(^{-1}\)，外线自旋迹使 \(\mathcal L_{00}\) 无量纲；\(\lambda\) 也无量纲。因此：

\[
[I_6]=\mathrm{GeV}^2.
\]

公式 (6) 的整体前因子量纲为 GeV\(^{-5}\)，所以：

\[
\left[\frac{d\sigma_A}{dE_R}\right]
=\mathrm{GeV}^{-3},
\]

符合截面对能量微分的量纲要求。

**收敛结论只适用于该代表点、当前 Dirac 基准和所采用的宽度输入。** 仍需对积分边界附近、不同 \(E_R\)、不同 \(m_s\)、不同 \(\Delta m\) 和近传播子极点区域重复收敛测试。

---

## 7. Breit–Wigner 宽度：条件性推导与敏感性

原稿的第二个传播子分母为：

\[
D_2=W^2-m_{\chi_2}^2
+i m_{\chi_2}\Gamma_{\chi_2}.
\]

因此，若要数值确定有限宽度效应，必须确定：

\[
\Gamma_{\chi_2}=\Gamma(\chi_2\to\chi_1s).
\]

### 7.1 宽度公式的条件性推导

当前原稿相关段落写明了 pole-width 传播子和 \(\chi_2\to\chi_1s\) 的宽度定义，但没有在该处给出完整的两体宽度公式。因此下面的公式是**根据原稿的纯标量相互作用自行推导的条件性结果**，不是原稿已明确列出的公式。

仅在以下条件成立时使用：

1. \(\chi_1,\chi_2\) 按 Dirac 费米子处理；
2. 顶点为纯标量 Yukawa 耦合 \(g_2s\bar\chi_2\chi_1+\mathrm{h.c.}\)；
3. 只考虑 \(\chi_2\to\chi_1s\) 这一条开放衰变道；
4. 不存在额外衰变道或额外的统计因子。

衰变自旋平均矩阵元为：

\[
\overline{|\mathcal M_{\mathrm{dec}}|^2}
=
|g_2|^2
\left[(m_{\chi_2}+m_{\chi_1})^2-m_s^2\right].
\]

定义有量纲 Källén 函数：

\[
\lambda_{\mathrm{dimful}}(a,b,c)
=a^2+b^2+c^2-2ab-2ac-2bc.
\]

则：

\[
\boxed{
\Gamma_{\chi_2}
=
\frac{|g_2|^2}
{16\pi m_{\chi_2}^3}
\sqrt{\lambda_{\mathrm{dimful}}
(m_{\chi_2}^2,m_{\chi_1}^2,m_s^2)}
\left[(m_{\chi_2}+m_{\chi_1})^2-m_s^2\right]
}.
\]

若 \(\chi_2\) 的粒子性质、手征结构或开放衰变道不同，必须重新推导宽度。

### 7.2 为什么图注给出的耦合乘积不足以确定宽度

Figure 2 图注给出：

\[
(g_1g_2g_{VN})^2=10^{-8}.
\]

这只固定了三个耦合的乘积，不能确定 \(g_2\) 本身。可是上述条件性宽度满足：

\[
\Gamma_{\chi_2}\propto |g_2|^2.
\]

所以，在使用有限宽度的 Breit–Wigner 传播子时，仅给出耦合乘积不足以唯一确定传播子分母。必须另外给出 \(g_2\)，或给出可验证的宽度处方。

### 7.3 宽度敏感性数值诊断

参数：

\[
m_{\chi_1}=1000~\mathrm{GeV},\quad
m_s=0.3~\mathrm{MeV},\quad
\Delta m=1~\mathrm{MeV},
\]

\[
E_R=0.2~\mathrm{MeV},\quad
v=776~\mathrm{km/s}.
\]

以下统一使用 \((n_W,n_z,n_\varphi)=(24,24,16)\)：

| \(g_2\) | 条件性 \(\Gamma_{\chi_2}\)（GeV） | \(I_6\)（GeV\(^2\)） |
|---:|---:|---:|
| 0（零宽度诊断） | 0 | 878078.8408 |
| 0.1 | \(1.51824\times10^{-6}\) | 878077.8430 |
| 1 | \(1.51824\times10^{-4}\) | 868227.2836 |
| 3 | \(1.36641\times10^{-3}\) | 481505.2617 |

可以看到：

- \(g_2=0.1\) 时，宽度效应在该点很小；
- \(g_2=1\) 时，积分已经出现约百分之一量级的变化；
- \(g_2=3\) 时，变化显著。

这些数值是**宽度敏感性诊断**，不是 Figure 2 的拟合 benchmark，也不代表原作者使用了这些 \(g_2\)。

此外，原稿要求 \(W_{\max}<m_{\chi_2}\)，排除真实 on-shell \(\chi_2\) 产生。这一条件不等于有限宽度一定可以忽略：若 \(m_{\chi_2}^2-W^2\) 与 \(m_{\chi_2}\Gamma_{\chi_2}\) 同量级，离壳传播子仍可能对宽度敏感。

---

## 8. 四组 benchmark 的约化积分诊断

以下结果统一采用零宽度、求积阶数 \((32,32,16)\)，并只报告 \(I_6\)，不包含公式 (6) 的整体前因子。

| \(m_s\) | \(\Delta m\) | \(E_R\) | \(v\) | \(I_6\)（GeV\(^2\)） |
|---:|---:|---:|---:|---:|
| 300 keV | 1 MeV | 200 keV | 776 km/s | 878073.8896 |
| 300 keV | 10 MeV | 200 keV | 776 km/s | 6998.1820 |
| 360 keV | 1 MeV | 300 keV | 800 km/s | 400885.1043 |
| 360 keV | 10 MeV | 300 keV | 800 km/s | 2967.0537 |

这四个点的 \(W_{\max}<m_{\chi_2}\) 条件检查如下：

| \(m_s\) | \(\Delta m\) | \(\sqrt{W_{\max}^2}\)（GeV） | \(m_{\chi_2}\)（GeV） | \(m_{\chi_2}^2-W_{\max}^2\)（GeV\(^2\)） |
|---:|---:|---:|---:|---:|
| 300 keV | 1 MeV | 1000.0003474 | 1000.001 | 1.30518 |
| 300 keV | 10 MeV | 1000.0003474 | 1000.010 | 19.30528 |
| 360 keV | 1 MeV | 1000.0003854 | 1000.001 | 1.22924 |
| 360 keV | 10 MeV | 1000.0003854 | 1000.010 | 19.22934 |

这四组点满足所写的 off-shell 条件。不过，\(\Delta m=1\) MeV 时传播子离 pole 更近，故有限宽度敏感性值得优先检查。

### 8.1 对 \(\Delta m\) 的敏感性

在本轮选取的点上，从 1 MeV 增加到 10 MeV 后，约化积分显著下降。这是内部 \(\chi_2\) 传播子分母改变的结果。

不能将这一变化简单解释成“标量产生概率”或“实验事件率”的变化，因为：

- 目前还没有乘上完整的整体耦合因子；
- 尚未加入 \(m_V\) 传播子和 \(\mathcal R_A(E_R)\)；
- 尚未进行 halo 速度积分；
- 当前 benchmark 点不是由 Figure 2 的原始绘图脚本完整恢复的参数输入。

---

## 9. 当前计算实际完成到哪一步？

公式 (6) 可以分成：

\[
\frac{d\sigma_A}{dE_R}
=
\underbrace{
\frac{m_A(g_1g_2g_{VN})^2}
{256\pi^3p_{\chi_1}^2}
\frac{\mathcal R_A(E_R)}
{(m_V^2+2m_AE_R)^2}
}_{\text{整体前因子}}
\underbrace{I_6(v,E_R)}_{\text{本轮数值核}}.
\]

本轮已经计算的是右侧第二个因子 \(I_6\)。完整微分截面还需要以下输入：

| 输入 | 当前状态 | 影响 |
|---|---|---|
| \(m_V\) | 未从 Figure 2 原始输入恢复 | 决定媒介传播子随 \(E_R\) 的变化 |
| \(\mathcal R_A(E_R)\) | 仅有定义和零动量归一化条件 | 决定核结构与反冲能量依赖 |
| 独立 \(g_2\) | 未恢复 | 决定条件性 \(\Gamma_{\chi_2}\) |
| Dirac/Majorana 性质 | 原稿相关段落未明确 | 影响顶点与自旋振幅定义 |
| 手征/CP 约定 | 尚未完整明确 | 可能影响顶点结构和干涉 |
| 天然氙同位素加权 | 未实现 | 最终实验核响应需要处理 |

因此，目前不能声称已经计算出完整 \(d\sigma_A/dE_R\)。

同样，当前没有执行：

\[
\frac{dR}{dE_R}
=
\frac{\rho_\chi}{m_{\chi_1}m_A}
\int d^3v\,f_{\mathrm{lab}}(\mathbf v)\,
v\frac{d\sigma_A(v,E_R)}{dE_R}.
\]

这一步才是 halo 速度积分，必须等单速度微分截面通过验证后再做。

---

## 10. 数值程序、复现入口与测试

### 10.1 文件结构

\`\`\`text
research/figure2_full_reproduction/
├── README.md
├── eq6_kernel.py
├── tests/
│   └── test_eq6_kernel.py
└── results/
    ├── EQ6_MILESTONE_1.md
    ├── eq6_diagnostic_values.csv
    └── EQ6_COMPLETE_CALCULATION_NOTE_ZH.md
\`\`\`

### 10.2 主要函数

| 函数 | 作用 |
|---|---|
| \`limits\` | 计算 \(W_{\min}^2,W_{\max}^2\) |
| \`build_point\` | 重建 \(p,p',k,K,q\) |
| \`slash\` | 构造 \(\not p\) |
| \`vertices\` | 构造 before/after 两张图的 \(\Gamma^0\) |
| \`spin_trace\` | 计算单图、干涉和完整 trace |
| \`chi2_width_dirac_scalar\` | 在明确假设下计算 Dirac 纯标量衰变宽度 |
| \`reduced_kernel\` | 计算公式 (6) 的 \(W^2,z,\varphi_*\) 积分 |
| \`residuals\` | 检查质量壳和四动量守恒 |

### 10.3 运行测试

在仓库根目录执行：

\`\`\`bash
python -m unittest discover -s research/figure2_full_reproduction/tests -v
\`\`\`

当前测试文件覆盖：

1. 300 MeV benchmark 的闭相空间测试；
2. 300 keV benchmark 的开相空间测试；
3. 末态质量壳和四动量守恒；
4. 完整 trace 的实数性、非负性和分解闭合；
5. trace 与显式自旋器求和对照；
6. 条件性两体宽度函数；
7. 代表点求积收敛。

本轮记录的本地测试结果为 7 项通过。当前计算分支尚无与最新提交关联的 GitHub Actions 状态检查，因此“本地测试通过”不应表述为“CI 已通过”。

---

## 11. 已知问题与下一阶段验收计划

### P0-A：模型定义闭合

- 明确 \(\chi_1,\chi_2\) 的 Dirac/Majorana 性质；
- 明确 \(g_1,g_2\) 的手征、CP 和相位约定；
- 根据最终模型重新推导两张图的顶点和宽度；
- 明确 Figure 2 的独立 \(g_2\) 或原作者采用的宽度处方。

验收标准：振幅、传播子宽度和外线统计性质来自同一个明确模型，不混用不同假设。

### P0-B：传播子审计

- 比较零宽度与 pole-width；
- 在模型允许时比较常数 pole-width 与能量依赖自能宽度；
- 检查 \(W_{\max}<m_{\chi_2}\) 的整个目标 halo 速度区域；
- 对 \(m_{\chi_2}^2-W^2\) 最小的区域加密积分。

验收标准：说明宽度是否对每条 benchmark 曲线重要，且不能通过任意调节宽度拟合原图。

### P0-C：核响应审计

- 从原稿引用的核响应定义恢复 \(W_M^{00}(y)\)；
- 固定核质量、核自旋、振子长度和同位素约定；
- 检查 \(\mathcal R_A(0)=A^2\)；
- 对照独立核响应实现。

验收标准：核响应的归一化和 \(E_R\) 依赖均有来源、可复现。

### P0-D：完整单速度微分截面

只有 P0-A 至 P0-C 通过后，才把所有因子组合为：

\[
d\sigma_A(v,E_R)/dE_R.
\]

验收标准：量纲正确、耦合标度正确、不同求积阶数稳定、独立实现一致。

### P0-E：Halo 积分

最后再使用明确的实验室速度分布 \(f_{\mathrm{lab}}\)，得到：

\[
dR/dE_R.
\]

验收标准：速度分布归一化、速度阈值、尾部收敛和单位曝光归一化全部通过。

---

## 12. 总结

本轮工作已经把 Figure 2 的问题从“图例单位是否写错”推进到可审查的数值计算框架：

- 运动学上，300/360 keV 与高速端的相空间起始位置相容，而 300/360 MeV 在本轮测试速度范围内关闭；
- 振幅上，已实现两张图的相干求和，并以显式自旋器求和验证 Dirac trace；
- 相空间上，已完成代表点的 \(W^2,z,\varphi_*\) 三重积分和求积收敛检查；
- 传播子上，已显示独立 \(g_2\) 和宽度处方会影响结果；
- 实验预测上，完整 \(d\sigma_A/dE_R\)、halo 积分和 LZ 事件率仍未完成。

因此，本阶段的正确结论是：

\[
\boxed{
\text{运动学审计与公式 (6) 的 Dirac 基准数值核已建立，}
\quad
\text{完整截面及事件率尚待参数闭合和独立验证。}
}
\]

不得将当前约化积分 \(I_6\) 直接称为微分截面、暗物质事件率或 LZ 信号预测。
