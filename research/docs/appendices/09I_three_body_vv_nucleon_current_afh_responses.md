# 附录 I：三体 VV 核子矢量流、Dirac–Pauli 匹配与 AFH 非 \(M\) 响应

> **状态：** 理论匹配与算符映射已整理；完整三体核流收缩及 \(\Phi''\)、\(M\Phi''\)、\(\Delta\)、\(\Sigma'\) 的物理速率贡献尚未完成。  
> **适用过程：** \(\chi_1+A\to\chi_1+A+s\)，其中标量 \(s\) 从暗物质线上辐射，媒介子 \(V\) 与核子的矢量流耦合。  
> **数值边界：** 本附录不把 AFH \(M\) 响应的已验证结果升级为完整 VV 核流结果；所有初步空间响应和点核诊断均标明其证据等级。

## I.1 变量、四动量方向与三体流的分工

采用度规 \((+,-,-,-)\)，定义媒介子传给原子核的四动量为
\[
q_A^\mu=P_A'^\mu-P_A^\mu.
\]
在单核子冲量近似下，受击核子的动量变化满足
\[
q_N^\mu=p_N'^\mu-p_N^\mu\simeq q_A^\mu.
\]
若初态原子核静止，则
\[
q_A^0=E_R,\qquad
Q_A^2\equiv |\mathbf q_A|^2=2m_AE_R+E_R^2,
\qquad
t_A=q_A^2=-2m_AE_R.
\]
这里 \(Q_A\) 是 AFH 核响应使用的空间动量模长，而 \(t_A\) 是核子 form factor 与媒介子传播子使用的 Minkowski 不变量；两者不能用同一个无区分的 \(q^2\) 表示。

三体四动量守恒给出
\[
p_\chi+P_A=p_\chi'+P_A'+k_s,
\]
从而
\[
\boxed{q_A^\mu=-q_\chi^\mu-k_s^\mu,\qquad
q_\chi^\mu=p_\chi'^\mu-p_\chi^\mu.}
\]
因此三体过程中一般 \(q_A\ne-q_\chi\)。AFH 的自变量始终是原子核实际获得的 \(\mathbf q_A\)，不是暗物质外线动量差，也不是末态标量动量。

另定义受击核子的平均内部动量
\[
\mathbf K_N=\frac{\mathbf p_N'+\mathbf p_N}{2}.
\]
\(\mathbf K_N\) 不是三体相空间中暗物质—标量子系统的四动量 \(K^\mu=p_\chi-q_A\)。两者属于不同自由度，不能混用。

## I.2 完整三体振幅与核流张量

把暗物质侧两张标量辐射图相干相加，定义
\[
\mathcal T_3^\mu
=\bar u_{\chi_1}(p_\chi')\Gamma_3^\mu u_{\chi_1}(p_\chi),
\qquad
\Gamma_3^\mu=\Gamma_{\rm before}^\mu+\Gamma_{\rm after}^\mu.
\]
其中
\[
\Gamma_{\rm before}^\mu
=\frac{\gamma^\mu(\slashed p_\chi-\slashed k_s+m_{\chi_2})}
{(p_\chi-k_s)^2-m_{\chi_2}^2},
\]
\[
\Gamma_{\rm after}^\mu
=\frac{(\slashed p_\chi'+\slashed k_s+m_{\chi_2})\gamma^\mu}
{(p_\chi'+k_s)^2-m_{\chi_2}^2+i m_{\chi_2}\Gamma_{\chi_2}}.
\]
具体耦合常数和宽度处方以正文及附录 A 的振幅约定为准；两张图必须在振幅层面相加，不能把两张图的截面非相干相加。

把核子 form factor 和核结构统一放入
\[
J_A^\nu(q_A)=\langle A(P_A')|J_V^\nu(q_A)|A(P_A)\rangle,
\]
则单次媒介子交换下的振幅结构为
\[
\boxed{
\mathcal M_3=C_3\,\mathcal T_3^\mu
D_{\mu\nu}(q_A)J_A^\nu(q_A),
}
\]
其中 \(C_3\) 表示暗物质侧整体耦合；若把 \(g_{Vq}\) 或 \(g_{VN}\) 提到 \(C_3\) 外，核流定义中就不能再次包含同一个耦合。

暗物质侧完整张量为
\[
L_3^{\mu\rho}
=\frac12\operatorname{Tr}\!\left[
(\slashed p_\chi'+m_{\chi_1})\Gamma_3^\mu
(\slashed p_\chi+m_{\chi_1})\overline{\Gamma}_3^{\,\rho}
\right],
\qquad
\overline{\Gamma}_3^{\,\rho}
=\gamma^0(\Gamma_3^\rho)^\dagger\gamma^0.
\]
靶核的矢量流张量可写为
\[
W_A^{\nu\sigma}
=\frac{1}{2J_A+1}
\sum_{M_A,M_A'}
J_A^\nu(M_A'\!,M_A)
J_A^{\sigma *}(M_A'\!,M_A).
\]
于是自旋平均后的平方振幅具有结构
\[
\overline{|\mathcal M_3|^2}
\propto
L_3^{\mu\rho}
D_{\mu\nu}D_{\rho\sigma}^{*}
W_A^{\nu\sigma}.
\]
在媒介子传播子可约化为度规张量的相应极限下，这一表达式才简化为常写的 \(L_{\mu\nu}W_A^{\mu\nu}\)。

当前 Eq. (6) benchmark 实际保留的是
\[
\mathcal L_{00}
=\frac12\sum_{s,s'}
|\bar u_{s'}(p')\Gamma_3^0u_s(p)|^2
=\frac12\operatorname{Tr}\!\left[
(\slashed p'+m_{\chi_1})\Gamma_3^0
(\slashed p+m_{\chi_1})\overline\Gamma_3^{\,0}
\right],
\]
并在核侧采用领先 \(M\) 电荷近似
\[
|\mathcal M_3|^2\simeq |\mathcal K_3|^2W_M^{00}.
\]
这不是已经完成的完整 \(L_3^{\mu\nu}W^A_{\mu\nu}\) 收缩。还必须区分两个不同截断：
1. 只保留暗物质张量的 \(L^{00}\)；
2. 在核子 \(J_N^0\) 中也只保留领先 \(F_1\) 电荷项，并将其映射为 AFH \(M\) 响应。

第二项比第一项更强。即使暗物质侧只使用 \(L^{00}\)，核子时间分量本身仍含有次领先的自旋—轨道电荷结构；所以“只取时间分量”不自动等于“只取 \(M\)”。

## I.3 从 flavor-universal 夸克流到核子 \(F_1/F_2\)

对夸克味道 \(q\)，核子矩阵元采用 Dirac–Pauli 分解。定义当前三体核反冲方向
\[
q_N^\mu=p_N'^\mu-p_N^\mu\simeq q_A^\mu,
\]
则使用
\[
\boxed{
\langle N(p_N')|J_V^\mu|N(p_N)\rangle
=
\bar u_N(p_N')
\left[
F_1^{V,N}(t_A)\gamma^\mu
+\frac{iF_2^{V,N}(t_A)}{2m_N}
\sigma^{\mu\nu}q_{A,\nu}
\right]
u_N(p_N),
}
\]
其中 \(\sigma^{\mu\nu}=i[\gamma^\mu,\gamma^\nu]/2\)。这里 Pauli 项前的正号对应 \(q_A=p_N'-p_N\)。Hoferichter–Klos–Schwenk 的文献约定使用 \(q=p_N-p_N'\)，因此其式中的 Pauli 项写成 \(-iF_2\sigma^{\mu\nu}q_\nu/(2m_N)\)；两种写法仅是动量方向不同，不能混用。

对指定的低能活动味道集合，
\[
F_i^{V,N}(t)=\sum_q c_q^V F_i^{q,N}(t).
\]
当前 flavor-universal 三味 benchmark 取 \(q=u,d,s\) 且 \(c_u^V=c_d^V=c_s^V=1\)。零动量处的 Dirac 电荷为
\[
F_1^{u,N}(0)+F_1^{d,N}(0)+F_1^{s,N}(0)=3,
\]
故
\[
g_{Vp}=g_{Vn}=3g_{Vq}.
\]
这是等质子、等中子领先电荷耦合的来源；它不意味着有限 \(t\) 下所有质子、中子 form factor 都可用同一个常数替代。

Bishara、Brod、Grinstein 和 Zupan 的显式 flavor-separated form-factor 分解（arXiv:1707.06998，附录 A.1）给出质子的零动量中心值
\[
F_2^{u/p}(0)=1.609,\qquad
F_2^{d/p}(0)=-2.097,\qquad
F_2^{s/p}(0)=-0.064,
\]
因此当前采用的 flavor-universal 三味 benchmark 输入为
\[
\boxed{F_2^{V,p}(0)=
F_2^{u/p}(0)+F_2^{d/p}(0)+F_2^{s/p}(0)=-0.552.}
\]
在同位旋对称近似下，中子交换 \(u,d\) 分量，三味总和相同。与 \(F_1^V(0)=3\) 相比，中心值比例为
\[
F_2^V(0)/F_1^V(0)\simeq-0.184.
\]
输入 \(F_2^{s/p}(0)=-0.064(17)\) 的不确定度会同时进入 \(F_2^{u/p}\)、\(F_2^{d/p}\) 和三味总和；没有完整协方差时，不能把这些误差当作独立量简单平方相加。当前 benchmark 明确采用该 2017 年显式 flavor-separated 输入，而不把电磁 \(F_2^p\) 直接代入 universal quark current。

**HKS 2015 的对照与使用边界：** HKS Eq. (21) 给出显式 flavor 重构
\[
F_2^{u/p}=2F_2^{\rm EM,p}+F_2^{\rm EM,n}+F_2^{s,N},\qquad
F_2^{d/p}=F_2^{\rm EM,p}+2F_2^{\rm EM,n}+F_2^{s,N}.
\]
结合其 isospin 关系和经验的质子/中子电磁 Pauli form factors、strange Pauli form factor，得到与 Bishara et al. (2017) Appendix A.1 相同的 flavor-separated 中心值 \(1.609,-2.097,-0.064\)，其等权重三味和为 \(-0.552\)。HKS Eq. (23) 的紧凑写法若按字面、并把其中 \(\kappa_N\) 与 Eq. (24) 的物理核子反常磁矩采用同一含义来相加，会形式上得到零和；但它不能在不核清符号定义和近似条件的情况下，作为独立的 flavor-sum 恒等式去覆盖 Eq. (21) 的显式重构。**因此本项目不再使用“由 HKS 紧凑式可知三味 \(F_2^V(0)=0\)”这一历史判断；当前 benchmark 明确采用 Bishara et al. Appendix A.1 的显式 flavor-separated 输入。** 有限 \(t_A\) 的形状、误差和协方差仍待生产级匹配。

这一非零 Pauli 输入会改变两个 NR 系数。以零动量中心值为例，
\[
F_1^V+2F_2^V=3-1.104=1.896,\qquad
F_1^V+F_2^V=3-0.552=2.448.
\]
因此时间分量自旋—轨道电荷项和空间磁化项都必须使用同一套 flavor-separated form-factor 输入。

参考：M. Hoferichter, P. Klos and A. Schwenk, *Chiral power counting of one- and two-body currents in direct detection of dark matter*, Phys. Lett. B 746 (2015) 410–416, arXiv:1503.04811，特别是矢量流分解和式 (19)–(26)。

## I.4 Dirac–Pauli 核子流的非相对论展开

在协变归一化 \(\bar u u=2m_N\) 下，令
\[
\mathbf K_N=\frac{\mathbf p_N'+\mathbf p_N}{2},
\qquad
\mathbf q_A=\mathbf p_N'-\mathbf p_N.
\]
对上面的 Dirac–Pauli 矩阵元作低动量展开，保留与当前响应匹配直接相关的结构，有
\[
\frac{J_N^0}{2m_N}
=
F_1^{V,N}
+\delta_{\rm SI}^{(0)}
+\frac{i\,[F_1^{V,N}+2F_2^{V,N}]}{4m_N^2}
\boldsymbol\sigma_N\cdot
(\mathbf q_A\times\mathbf K_N)
+\cdots,
\]
\[
\frac{\mathbf J_N}{2m_N}
=
\frac{F_1^{V,N}}{m_N}\mathbf K_N
+\frac{i\,[F_1^{V,N}+F_2^{V,N}]}{2m_N}
\boldsymbol\sigma_N\times\mathbf q_A
+\cdots.
\]
\(\delta_{\rm SI}^{(0)}\) 表示这里未逐项展开的自旋无关相对论修正；省略项还包括更高阶 \(Q_A^2/m_N^2\)、\(K_N^2/m_N^2\) 结构。上式给出的是匹配所需的算符结构和 form-factor 组合，不替代对实际 UV 味道组合、有限 \(t\) 输入和三体系数的逐项推导。

以当前 2017 年 flavor-separated 零动量中心值 \(F_1^V=3\)、\(F_2^V=-0.552\) 为例，
\[
F_1^V+2F_2^V=1.896,\qquad F_1^V+F_2^V=2.448.
\]
这两行必须分别阅读：

- 时间分量的自旋—轨道项正比于 \(F_1+2F_2\)，其核子算符含 \(\boldsymbol\sigma_N\cdot(\mathbf q_A\times\mathbf K_N)\)。因此即使 \(L^{ij}\) 很小，\(L^{00}\) 仍可与这个次领先核电荷项相乘。
- 空间分量的对流项正比于 \(F_1\mathbf K_N/m_N\)。
- 空间分量的磁化项正比于 \(F_1+F_2\)，而不是单独正比于 \(F_2\)。Pauli form factor 的具体值会改变磁化系数，但不能把磁化流简单等同于 Pauli 项本身。

\(\mathbf K_N\) 是核内单核子平均动量。把核子内部速度 \(v_N\sim0.1\text{--}0.3\) 直接与暗物质 halo 速度 \(v_\chi\sim10^{-3}\) 比较，并不能判断相应核响应的大小；还需要三体暗物质张量系数、核矩阵元、角动量选择定则和干涉项。

## I.5 从单核子算符到 AFH 响应的对应关系

在单体冲量近似下，核流可示意写成
\[
\rho_V(\mathbf q_A)
=\sum_a e^{i\mathbf q_A\cdot\mathbf r_a}
\left[
F_1^{V,N_a}
+\frac{i(F_1^{V,N_a}+2F_2^{V,N_a})}{4m_N^2}
\boldsymbol\sigma_a\cdot(\mathbf q_A\times\mathbf K_a)
+\cdots
\right],
\]
\[
\mathbf J_V(\mathbf q_A)
=\sum_a e^{i\mathbf q_A\cdot\mathbf r_a}
\left[
\frac{F_1^{V,N_a}}{m_N}\mathbf K_a
+\frac{i(F_1^{V,N_a}+F_2^{V,N_a})}{2m_N}
\boldsymbol\sigma_a\times\mathbf q_A
+\cdots
\right].
\]
这里 \(a\) 遍历核子；若质子和中子 form factor 不同，必须保留相应同位旋结构，不能直接把它们合并成一个等标量系数。

| AFH 响应 | 单核子流的来源 | 当前 VV 匹配中的地位 |
|---|---|---|
| \(M\) | 领先矢量电荷密度 \(F_1\sum_a e^{i\mathbf q\cdot\mathbf r_a}\) | 已有七同位素数值基线；必须保留 |
| \(\Phi''\) | 时间分量中的自旋—轨道电荷项 \(\boldsymbol\sigma\cdot(\mathbf q_A\times\mathbf K_N)\) | 第一优先级；不能由小 \(L^{ij}\) 排除 |
| \(M\Phi''\) | 领先电荷与自旋—轨道电荷振幅的干涉 | 必须与 \(\Phi''\) 同时计算；干涉可正可负 |
| \(\Delta\) | 空间流中的对流/轨道项 \(\mathbf K_N/m_N\)，经相应多极投影 | AFH DeltaJ 已纠正为同阶 MJLDivQ 映射；native Wolfram 输出与逐点对照待完成 |
| \(\Sigma'\) | 空间流中的横向磁化自旋项 \(\boldsymbol\sigma_N\times\mathbf q_A\) | 先前 selected-\(q\) 数值表已撤回；native Wolfram 输出与逐点对照待完成 |
| \(\Sigma''\) | 完整投影中可能出现的纵向自旋结构 | 不因核自旋非零而自动加入；由实际流分解决定 |
| \(\widetilde\Phi'\) | AFH 横向电/自旋—速度张量算符 | 当前不预设为非零；若完整 NR 投影产生相应算符再计算 |

\(\Phi''\) 不是普通意义上只测量总核自旋的传统 SD 响应；它编码核子自旋与轨道运动的耦合，可具有半相干结构。AFH 的 \(M\Phi''\) 是允许的干涉响应，不是一个可直接当作正数“修正百分比”的独立通道。

## I.6 完整收缩、流守恒与为什么点核 ppm 不能代替核内响应

将核子流按时间、纵向和横向分量分解后，完整三体收缩包含
\[
L^{00}W_A^{00},\qquad
L^{0i}W_A^{0i},\qquad
L^{ij}W_A^{ij},
\]
以及各核多极响应之间的干涉。对当前矢量流，单核子 on-shell 矢量流满足
\[
q_{A,\mu}J_N^\mu=0.
\]
在核层面，连续性方程约束纵向电流与电荷密度；若采用相互作用核哈密顿量，严格守恒还要求核流与核力/交换流处方一致。流守恒并不消除横向磁化流，因此不能据此删掉 \(\Sigma'\)。

需要特别区分两种完全不同的“空间流”：

1. **核质心平动流：** \(J_A^\mu\propto(P_A+P_A')^\mu\)。它只反映整个原子核的 recoil convection。
2. **核内部一体流：** \(\sum_a e^{i\mathbf q\cdot\mathbf r_a}\mathbf K_a\) 和 \(\sum_a e^{i\mathbf q\cdot\mathbf r_a}\boldsymbol\sigma_a\times\mathbf q\)。它依赖壳模型轨道、内部动量和核子自旋。

核质心点电荷流只有 ppm 级修正，并不能约束第二类核内矩阵元。反过来，核响应比值 \(W_{\Sigma'}/W_M\) 或 \(W_{\Phi''}/W_M\) 在 \(W_M\) 深极小值附近变大，也不等于完整截面必然出现同样大小的修正；必须把实际三体 Wilson/运动学系数、响应归一化和干涉一起收缩。

## I.7 当前数值证据与不可越过的状态边界

### I.7.1 已归档的 \(M\) 响应

AFH v6.0 七种可用 Xe 同位素的 \(M\) 电荷响应网格、因子 4 映射、零动量归一化和多极重构闭合已归档。Xe-131 的 rank-0/rank-2 分解属于同一个 \(M\) 电荷响应，不能误标为 \(\Phi''\)、\(\Delta\) 或自旋响应。AFH-7 仍不包含缺少官方 default density matrix 的 Xe-124/Xe-126。

### I.7.2 \(\Sigma'\) 的当前状态：先前 selected-\(q\) 数值表已撤回

PR #51 分支中曾出现一张由 Python 源代码翻译生成的 Xe-129/Xe-131 selected-\(q\) \(W_{\Sigma'} / W_M\) 比值表。后续对 AFH v6.0 实际调用链的复核确认，该表不能作为有效 AFH 数值结果使用，现正式撤回；不得在正文、图表或截面估算中继续引用其中的比值。此前同一翻译链中伴随报告的 \(W_M\) / \(W_{\Sigma'}\) 选点值也不作为 native AFH 证据。

AFH v6.0 的空间响应索引为
\[
i=3:\quad \mathrm{SigmaPJ}\longrightarrow W_{\Sigma'},
\qquad
i=6:\quad \mathrm{DeltaJ}\longrightarrow W_\Delta,
\qquad
i=8:\quad W_{\Sigma'\Delta}.
\]
当前 Python 代码仍属于 development translation。PR #51 同时准备了 native Wolfram exporter [run_afh_spatial_response_audit.wls](../../afh_default_density_xe131/run_afh_spatial_response_audit.wls)，用于对 Xe-129 和 Xe-131 在相同 \(q_A\) 网格上导出 package-native 响应。只有完成 native 输出、逐点差异比较、归一化和多极收敛检查后，才可重新发布 \(\Sigma'\) 数值表。

### I.7.3 \(\Delta\) 的 AFH 算符映射已纠正，数值验证待完成

AFH v6.0 的真实调用链为
\[
\mathrm{DeltaJ}\to\mathrm{DeltaJE}\to\mathrm{Deltaop}
\to\mathrm{MJLDivQ}[\ldots,jcap=L,lcap=L].
\]
先前 Python 翻译错误使用了 rank-\(L\pm1\) 的 \(\mathrm{DeltaPrime}\)，而不是 \(\mathrm{DeltaJ}\) 实际调用的同阶 \(L\) 分量。修正后，AFH \(\mathrm{DeltaJ}\) 的 abnormal-parity wrapper 与内部 \(3j\) 选择定则相容；此前声称存在内在 parity contradiction 的判断已撤回。

因此当前正确状态不是“\(\Delta\) 因 parity 矛盾而被阻断”，而是：**算符映射已纠正，但 \(W_\Delta\) 和 \(W_{\Sigma'\Delta}\) 尚无通过 native Wolfram 对照的数值结果。** 相关响应索引为 \(i=6\) 和 \(i=8\)。必须对 native package 输出与 Python development translation 作相同网格的逐点比较，之后才可发布数值。

### I.7.4 Xe-131 的 \(M,\Phi'',M\Phi''\) native 响应已完成（response-level）

PR #51 已归档 AFH v6.0 原生 Wolfram 输出，调用
\(\mathrm{ResponseNuclear}\) 索引
\[
i=1:\ M,\qquad i=4:\ \Phi'',\qquad i=7:\ M\Phi''.
\]
计算对象为 Xe-131（\(A=131,Z=54,J_A=3/2\)）、官方内置
\(sdgXe131\) 67-entry density matrix；网格为 2,401 个 \(q_A\) 节点，
范围 \(0\)–\(0.6\) GeV，步长 \(0.25\) MeV。AFH source 和 density-matrix
SHA-256、Wolfram 14.2.0 版本及 oscillator length 均记录在 metadata。

三个响应统一采用
\[
R_X^{\rm raw}=\frac{4\pi}{2J_A+1}W_{X,\rm AFH}^{00},
\qquad
R_X^{\rm phys}=4R_X^{\rm raw},
\qquad X\in\{M,\Phi'',M\Phi''\},
\]
factor four 只放置一次；不叠加旧 \(W_M\) 表中的独立零动量形状重归一化。
原生 CSV、metadata、Python validation summary 和 SHA-256 manifest 位于
research/afh_default_density_xe131/output/phi_response_native/。

专用 validator 报告 **PASS**：2,401 点网格和 \(y=(q_Ab_A/2)^2\) 一致；
\(4\pi/(2J_A+1)\) 与 factor-four 映射残差为零；对角响应非负；
虚部残差为零；\(M\)-\(\Phi''\) 响应矩阵满足 Cauchy–Schwarz；
\(R_M^{\rm raw}(0)=4289.895955714992\)，相对 \(A^2/4=4290.25\) 的
偏差为 \(8.25230\times10^{-5}\)。该 validator 检查响应 bookkeeping、
正定性和 provenance，不是独立核结构计算或三体截面比较。

在四个采样到的 \(M\) 局部极小值处，raw response 为：

| \(q_A\) [GeV] | \(R_M^{\rm raw}\) | \(R_{\Phi''}^{\rm raw}\) | \(R_{M\Phi''}^{\rm raw}\) | \(R_{\Phi''}/R_M\) |
|---:|---:|---:|---:|---:|
| 0.15800 | 5.31451e-2 | 7.14832e-1 | 2.62061e-2 | 13.45 |
| 0.25625 | 2.72531e-4 | 3.15623e-2 | -5.24943e-4 | 115.81 |
| 0.36500 | 6.70326e-4 | 1.51514e-3 | 2.21762e-4 | 2.26 |
| 0.49925 | 7.16871e-5 | 4.96083e-5 | -7.30759e-6 | 0.692 |

\(q_A=0.25625\) GeV 处的 115.81 倍比值来自 \(M\) 响应深极小值；
该点 \(R_{\Phi''}^{\rm raw}=0.03156\)，仅为其 q=0 值的
\(2.11\times10^{-4}\)。因此不能把裸响应比解释为截面增强倍数。
必须保留有符号的 \(M\)-\(\Phi''\) 干涉，并乘上完整三体振幅导出的
实际系数后，才能判断其对速率的影响。

这一步不确定有限 \(t_A\) 的核子 \(F_1/F_2\)，不导出完整三体 NR
Wilson coefficients，也不计算 \(\Delta\)、\(\Sigma'\)、\(\Sigma''\)、
\(\widetilde\Phi'\) 或 \(L_{\mu\nu}W_A^{\mu\nu}\)。完整 VV 核流收缩、
天然氙谱和 LZ likelihood 仍未完成。

### I.7.5 PR #53 的四分量暗物质流诊断

相关的 [PR #53 — full three-body vector-current audit](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/pull/53) 已有一个可复现的分支级诊断：构造完整 \(L^{\mu\nu}\)，保留两张辐射图和干涉，并与守恒的核质心点电荷流收缩。其 exact-source workflow 记录为 8/8 tests passed、12 行结果重算与归档表完全一致；扫描中 target-rest-frame
\[
r_\chi=\sqrt{\frac{L^{11}+L^{22}+L^{33}}{L^{00}}}
\simeq2.47\times10^{-3},
\]
点核完整流相对 charge-only 收缩的差异约为 4.3–5.1 ppm。

该诊断只包含原子核质心对流，不包含核内 \(\mathbf K_N\)、磁化或自旋—轨道矩阵元；也没有进行 \(F_1/F_2\) 到 AFH 非 \(M\) 响应的匹配。它能说明当前扫描点的暗物质空间流相对时间流较小，**不能**证明 \(\Phi''\)、\(\Sigma'\) 或 \(\Delta\) 可忽略。PR #53 仍是独立开放的 draft PR，合并前不把其结果写成 main 上已归档的完整核流验证。

此前讨论中报告过的其他点核 ppm 数值、单核子 \(\mathcal O_3/\mathcal O_1\) 百分比和未找回脚本的估算继续保留为历史诊断，不作为本附录的可复现结果。

## I.8 实施顺序与验收条件

建议按物理依赖关系推进：

1. **固定 flavor 和 form-factor 输入。** 明确活动味道、UV 权重、重味阈值匹配、\(F_1^{V,p/n}(t_A)\)、\(F_2^{V,p/n}(t_A)\) 的来源、误差和 \(t\) 区间；验证零动量电荷和当前三味分解的 Pauli 常数项。
2. **完成自由核子 Dirac–Pauli 对照。** 对选定 \(q_A\)、\(\mathbf K_N\) 和自旋态，将完整 Dirac 自旋量计算与上面的 NR 展开逐项比较；检查 \(J_N^\mu\) 的符号、\(F_1+2F_2\)、\(F_1+F_2\) 及 on-shell 流守恒。
3. **执行已准备的 Xe-131 native \(M,\Phi'',M\Phi''\) 导出。** 先运行 PR #51 的 Wolfram exporter，完成 2,401 点输出、metadata/SHA-256 核对和 Python validator；通过后再扩展 Xe-129，并在 Xe-131 的 \(q_A\simeq158,256,365\) MeV 附近做局部高分辨率扫描。
4. **完成 AFH 空间响应的 source/native 对照。** 使用 AFH 正确的 \(\Sigma'\)、\(\Delta J\)、\(\Sigma'\! -\! \Delta J\) 索引，对 Xe-129/Xe-131 的 native Wolfram 输出与 Python development translation 作逐点比较；\(\Delta J\) 已纠正为同阶 \(MJLDivQ\) 映射，不再沿用旧 parity-conflict 判断。每种响应都要单独检查归一化、相位、\(q/m_N\) 因子和选择定则。
5. **进行完整三体张量收缩。** 在每个三体相空间点计算 \(L^{\mu\nu}\)，与含有正确 \(F_1/F_2\) 系数的核流多极响应收缩；分别输出 \(M\)、\(\Phi''\)、\(M\Phi''\)、空间对流和磁化项，保留所有允许干涉。
6. **分别检查求积收敛。** 三体 \(W^2,z,\phi_*\) 求积、核响应 \(q_A\) 网格/插值和多极截断误差必须分别收敛；不能用一个积分收敛测试代替另一个。
7. **最后再生成天然氙谱。** 对各同位素使用各自核质量和核响应，按原始天然丰度求和；保留 AFH-7 / Hybrid-9 的输入边界，不把缺失同位素静默补齐。

最低验收集合包括：\(q_A\to0\) 电荷归一化、AFH factor-four 唯一放置、自由核子直接 Dirac 对照、\(q_\mu J_N^\mu=0\)、AFH native response 对照、parity/角动量选择定则、\(M\Phi''\) 干涉符号、两张暗物质辐射图干涉、\(L^{\mu\nu}\) Hermiticity/positivity、三体相空间和核响应插值的独立收敛，以及天然氙同位素加权检查。

## I.9 本附录的最终适用范围

当前可以严谨表述为
\[
\boxed{W_M^{00}\ \text{是已归档三体 VV benchmark 的领先阶核电荷响应。}}
\]
当前不能表述为
\[
W_M^{00}\ \text{已经完整描述了三体 VV 核子流。}
\]
要得到后一个结论，必须先完成
\[
\boxed{
\mathcal T_3^\mu\otimes\Gamma_N^\nu(F_1,F_2)
\longrightarrow
\{M,\Phi'',M\Phi'',\Delta,\Sigma',\Sigma'',\ldots\}
}
\]
并对 Xe-129、Xe-131 进行数值收缩和收敛审计。只有在完整一体流结果表明其余响应在目标精度内确实可忽略后，才能将 \(M\)-only 近似提升为经过验证的完整 VV 结果。

本附录是主报告的正式理论补充；完整理论讨论档案仍保存在 [QUARK_TO_NUCLEON_VECTOR_CURRENT_MATCHING.md](../../afh_isotope_response_equivalence/docs/QUARK_TO_NUCLEON_VECTOR_CURRENT_MATCHING.md)，用于追溯备选解释、历史估算和研究过程。
