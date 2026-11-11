> 所属主报告：[AFH v6.0 氙核响应与三体暗物质散射](../09_afh_xe131_three_body_kernel_natural_xenon_halo_2026-11-11.md)

# 附录 B：AFH v6.0 密度矩阵、谐振子基底与响应实现

## B.1 源文件、版本与 Xe-131 输入

本研究使用用户提供的 AFH/DMFormFactor v6.0 压缩包。归档的来源信息为：

- ZIP SHA-256：**4e0f70e6e780f3f4a40faa14792cae239d1989cf15d1e211b4fd7389b0460727**
- Mathematica 源文件：**v6/dmformfactor-V6.m**
- 源文件 SHA-256：**dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372**
- 同位素选择：**SetIsotope[54,131,"default","default"]**
- 内置密度矩阵：**sdgXe131**，共 67 项。

提取后的密度矩阵归档在

**research/afh_default_density_xe131/afh_default_xe131_density_matrix.csv**。

每一行包含：

| 字段 | 含义 |
|---|---|
| index | AFH 内置矩阵条目序号 |
| coefficient | 一体密度矩阵系数 |
| rank | 多极秩 \(J\) |
| isospin | 等标量/等矢量通道标记 \(\tau\) |
| Nprime, two_jprime | 单粒子末态轨道的振子主壳量子数和 \(2j'\) |
| N, two_j | 单粒子初态轨道的振子主壳量子数和 \(2j\) |

这 67 项不是 67 个独立的实验参数，而是壳模型单粒子轨道之间的约化一体密度矩阵元。其系数与轨道标签共同决定多极核矩阵元。

条目分布为：

| rank \(J\) | \(\tau=0\) | \(\tau=1\) | 合计 |
|---:|---:|---:|---:|
| 0 | 16 | 5 | 21 |
| 1 | 9 | 9 | 18 |
| 2 | 8 | 8 | 16 |
| 3 | 6 | 6 | 12 |
| **合计** | **39** | **28** | **67** |

当前使用的是弹性 \(M\) 响应 \(W_M^{00}\)：\(\tau=\tau'=0\)，且宇称选择规则使偶数多极 \(J=0,2\) 贡献进入该响应。因此实际参与本次 \(W_M^{00}\) 有限和的是 16 个 \(J=0,\tau=0\) 条目和 8 个 \(J=2,\tau=0\) 条目；其他条目仍保留在完整提取表中，以保证源矩阵归档完整。

Xe-131 的输入量为

\[
A=131,\qquad Z=54,\qquad J_A=\frac32,
\qquad T_{\rm iso}=|A/2-Z|=11.5.
\]

## B.2 AFH 默认谐振子长度与单位

AFH default 的振子长度处方为

\[
\boxed{
b_A=
\sqrt{\frac{41.467}
{45A^{-1/3}-25A^{-2/3}}}\ {\rm fm}
}.
\]

源程序采用

\[
1\ {\rm fm}=5.0677\ {\rm GeV}^{-1}.
\]

对于 Xe-131，

\[
b_{131}=2.2923417985218975\ {\rm fm}
=11.61690053236942\ {\rm GeV}^{-1}.
\]

核响应的无量纲谐振子变量是

\[
y=\left(\frac{qb_A}{2}\right)^2,
\]

其中 \(q=|\mathbf q|\)。因此 \(b_A\) 是核结构处方的一部分，不是用来拟合 Figure 2 谷值的自由参数。

**为什么不能调节 \(b_A\) 拟合谷值？** 因为 \(b_A\) 决定 \(q\mapsto y\) 的映射，并进入所有径向振子矩阵元。改变它会系统性移动有限动量响应的节点和极小值，相当于改变核模型输入。若为了匹配图中某个谷值而任意调节 \(b_A\)，得到的就不再是 AFH default 处方，也无法再把结果称为对该文献核响应的复现。

## B.3 单粒子轨道、多极角动量与径向矩阵元

AFH 源程序的轨道映射由单粒子振子主壳数 \(N\) 和总角动量 \(j\) 决定。当前 Python 翻译采用：

\[
j_+=j+\frac12.
\]

若 \(N-j_+\) 为偶数，则 \(\ell=j_+\)；否则 \(\ell=j_+-1\)。径向量子数为

\[
n=1+\frac{N-\ell}{2}.
\]

对每一条密度矩阵记录，程序计算一个约化角矩阵元和一个径向 Bessel 矩阵元。角部分用 Wigner \(3j\) 与 \(6j\) 符号：

\[
\begin{aligned}
\mathcal A^{(J)}_{N'j',Nj}
={}&(-1)^{1/2+j+J}
\left[
\frac{(2j+1)(2j'+1)(2\ell+1)(2\ell'+1)(2J+1)}
{4\pi}
\right]^{1/2}\\
&\times
\begin{pmatrix}
\ell'&J&\ell\\
0&0&0
\end{pmatrix}
\left\{
\begin{matrix}
\ell'&j'&1/2\\
j&\ell&J
\end{matrix}
\right\}.
\end{aligned}
\]

径向部分由 AFH 的 BesselElement 有限和实现。其结构为

\[
\begin{aligned}
\mathcal B_{n'\ell',n\ell}^{(J)}(y)
={}&
\frac{2^J}{(2J+1)!!}
y^{J/2}e^{-y}
\sqrt{(n'-1)!(n-1)!}\\
&\times
\sqrt{\Gamma(n'+\ell'+1/2)\Gamma(n+\ell+1/2)}
\sum_{r=0}^{n-1}\sum_{s=0}^{n'-1}
\mathcal C_{rs}\,
{}_1F_1\!\left(
\frac{J-\ell-\ell'-2r-2s}{2};
J+\frac32;y
\right),
\end{aligned}
\]

其中

\[
\begin{aligned}
\mathcal C_{rs}
={}&
\frac{(-1)^{r+s}}
{r!\,s!\,(n-1-r)!\,(n'-1-s)!}\\
&\times
\frac{
\Gamma[(\ell+\ell'+J+2r+2s+3)/2]
}{
\Gamma(\ell+r+3/2)\Gamma(\ell'+s+3/2)
}.
\end{aligned}
\]

这里 \({}_1F_1\) 是合流超几何函数。上式是当前 Python 翻译所实现的 AFH 有限和结构；具体系数和轨道标签仍以归档的 AFH v6.0 源文件及 67 项 CSV 为准。

## B.4 从密度矩阵到 \(W_M^{00}(y)\)

对每个允许的 \(J,\tau=0\)，程序将密度矩阵系数、等标量约化因子、角矩阵元和径向矩阵元求和：

\[
\mathcal A_J(y)
=
\sqrt{\frac{2}{2T_{\rm iso}+1}}
\sum_{\alpha\in D_{J,0}}
\rho_\alpha\,
\mathcal A_{\alpha}^{(J)}
\mathcal B_{\alpha}^{(J)}(y).
\]

对 Xe-131 的弹性 \(M\) 响应，当前程序保留 \(J=0,2\)。AFH v6.0 的 isoscalar 响应归一化在程序翻译中写为

\[
\boxed{
W_{M,\rm AFH}^{00}(y)
=\frac14\left[\mathcal A_0(y)^2+\mathcal A_2(y)^2\right]
}.
\]

这一步返回的是 AFH 包自身的原始 isoscalar response；它还没有自动变成论文中以物理单核子耦合 \(g_{VN}\) 为前因子的等质子、等中子相干响应。两者之间的因子 4 见附录 C。

## B.5 网格、插值、极小值搜索和边界处理

Xe-131 AFH 响应表采用

\[
0\le q\le0.60\ {\rm GeV},
\qquad \Delta q=0.00025\ {\rm GeV}=0.25\ {\rm MeV},
\]

共 2401 个节点。完整结果保存在

**research/afh_default_density_xe131/output/afh_default_xe131_WM00.csv**。

极小值搜索不是简单读取某个粗网格点：

1. 先在离散物理响应数组上用 find_peaks 对 \(-R\) 找局部极小值候选，prominence 取 \(A^2\times10^{-8}\)，distance 取 10 个网格点；
2. 只保留 \(0.08\le q\le0.50\) GeV 的候选；
3. 对每个候选，在相邻网格节点 \([q_{i-1},q_{i+1}]\) 内使用 bounded minimize_scalar；
4. 每次目标函数调用都重新计算 AFH 翻译核，而不是仅对谷值位置作多项式拟合；
5. 数值停止参数为 \(10^{-14}\) GeV。

代码中创建了 PCHIP 插值对象，但**极小值细化实际使用的是直接响应函数**，不是 PCHIP 插值曲线。PCHIP 的实际用途是后续把 AFH 响应插入固定速度的 5 keV 反冲网格：四 benchmark 截面程序使用 shape-preserving PCHIP，并设置 extrapolate=False；网格外不允许外推。超出响应表支持范围时计算应报错，而不是静默生成值。

## B.6 当前核响应结果

AFH default Xe-131 物理等质子、等中子响应的细化极小值为：

| \(q_{\min}\) [MeV] | \(E_{R,\min}\) [keV] | \(R_{\min}/A^2\) |
|---:|---:|---:|
| 157.93578 | 102.20672 | \(1.23638\times10^{-5}\) |
| 256.27187 | 269.10390 | \(6.34070\times10^{-8}\) |
| 365.06657 | 546.08690 | \(1.56194\times10^{-7}\) |
| 499.37189 | 1021.79779 | \(1.67063\times10^{-8}\) |

前三个极小值位于 Figure 2 讨论的反冲能量范围附近。它们是 AFH default 核响应的计算结果，不是通过调整 \(b_A\) 得到的拟合谷值。

## B.7 独立验证的实际范围

已完成的 Python 侧验证：

- 从官方 AFH v6.0 源文件解析 67 项矩阵，并与 CSV 逐项核对；
- 检查 \(q=0\) AFH 原始 isoscalar 归一化；
- 六个 \((q,J)\) 代表点的 60 位精度 mpmath spot checks；
- **全网格独立 mpmath 验证：** 重新组织 BesselElement 有限和，按超几何函数参数分组，使用 60 位精度 mpmath，而不调用 SciPy 的 hyp1f1；对完整 2401 个 q 节点逐点比较；
- 六项 AFH Xe-131 Python 回归测试；
- 保存完整 2401 点响应表、谷值表、Figure 2 参考点表和 metadata。

全网格验收结果：

| 指标 | 结果 |
|---|---:|
| 参考精度 | 60 decimal digits |
| q 网格节点 | 2401 |
| 最大振幅绝对差 | \(3.9782\times10^{-14}\) |
| 最大相对振幅差（参考振幅绝对值大于 \(10^{-10}\)） | \(8.8322\times10^{-13}\) |
| 最大响应绝对差除以 \(A^2\) | \(1.2159\times10^{-15}\) |
| 最大相对响应差（\(R/A^2>10^{-12}\)） | \(1.3376\times10^{-13}\) |
| 状态 | PASS |

完整的 2401 行逐点比较表和 JSON summary 作为 GitHub Actions artifact 保存：

- workflow run：**43038372836**
- artifact：**afh-xe131-mpmath-full-grid-validation**
- [查看完整 CI 运行和 artifact](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43038372836)

此前六个代表点的 mpmath 结果仍保留为早期 spot-check 记录；现在它们已被完整 2401 点验证覆盖。

AFH 原生 Mathematica runner 和 Python/Mathematica 比较程序已经归档：

- run_afh_default_xe131.wls
- verify_afh_xe131_native.wls
- compare_afh_mathematica_python.py

但 Wolfram kernel 尚未在当前计算环境中执行。因此原生 Mathematica 逐点对照仍为待完成项目。全网格 mpmath 是独立高精度数值实现，不应被称为官方 Mathematica 原生复算。

## B.8 核响应动量与精确运动学动量必须分开

论文明确规定

\[
y=\frac{b_A^2m_AE_R}{2},
\]

而 AFH 振子变量为 \(y=(qb_A/2)^2\)。因此，在论文当前写法下，固定反冲能量时的核响应查询动量是

\[
\boxed{q_{\rm resp}^{\rm NR}=\sqrt{2m_AE_R}}.
\]

三体运动学则由核质量壳条件给出精确空间反冲动量

\[
\boxed{q_{\rm kin}^{\rm exact}=\sqrt{2m_AE_R+E_R^2}}.
\]

AFH 响应网格本身以 \(q\) 为自变量；把网格上的 \(q\) 极小值换算成物理反冲能量时，程序使用精确逆映射 \(E_R=\sqrt{m_A^2+q^2}-m_A\)。但在给定 \(E_R\) 查询论文定义的响应 \(y(E_R)\) 时，应使用 \(q_{\rm resp}^{\rm NR}\)。这两个操作应分别命名，不能用同一个未说明约定的 q 代替。

当前代码约定为：

- 固定 Xe-131 benchmark 和 joint Xe-131 响应查询：使用 \(q_{\rm resp}^{\rm NR}\)；
- Eq. (6) 的三体运动学、\(W_{\max}\) 和 \(v_{\min}\)：使用 \(q_{\rm kin}^{\rm exact}\)；
- 旧天然氙 halo 输入的 28 个 AFH response samples：实际使用 \(q_{\rm kin}^{\rm exact}\)，属于 legacy 样本，尚未按论文 \(q_{\rm resp}^{\rm NR}\) 重新生成。

本轮 q 审计显示，28 个天然氙样本的 \(q_{\rm exact}-q_{\rm NR}\) 约为 0.032–0.409 keV（相对 0.20–1.14 ppm）。对 Xe-131 的 2401 点 AFH 响应表直接插值后，四个 selected recoil 点的 \(R_A(q_{\rm exact})/R_A(q_{\rm NR})-1\) 约为 -5.5 至 -212.7 ppm。完整数据和数值见附录 G。

固定 Xe-131 benchmark 仍使用 \(M_A=131u\) 的历史质量约定；天然氙 halo 程序使用 NIST 原子质量减去 54 个电子质量的核质量。质量方案是另一个独立输入维度，不应与上述两个 q 的定义混为一谈。

天然氙脚本现默认要求 manuscript-NR 响应样本；旧的 exact-q 样本只能通过显式的 --response-q-convention legacy_exact 复现。若所选 q 与样本不一致，程序会报错，不会仅修改 q 标签或静默复用旧 \(R_A\)。

