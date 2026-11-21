# 核子电荷匹配系数 \(c_M\)：原始归一化、因子 3 与 AFH \(W_M\) 的区别

**状态：** 本文固定当前三体 VV、AFH 电荷型 \(M\)-only rate-level 实现中的符号和归一化规范。它是 [B 核子形状因子基准](README.md)、[P0/P 点状 Dirac 基准](P0_VS_P_POINTLIKE_DIRAC_BASELINES.md) 和 [P0/P/A0/B 四级比较](POINTLIKE_NUCLEON_P_A_B_COMPARISON.md) 的共同记号依据。

## 1. 结论：取 1 的是归一化系数，不是原始系数

本项目必须区分：

\[
\boxed{
c_M^{\rm raw}(t_N),\qquad
\widehat c_M(t_N),\qquad
F_M(t_N),\qquad
W_M(y_A).
}
\]

它们的定义为

\[
\boxed{
c_M^{\rm raw}(t_N)
=
F_1^{uds,N}(t_N)
+\frac{t_N}{8m_N^2}
\left[F_1^{uds,N}(t_N)+2F_2^{uds,N}(t_N)\right],
}
\tag{1}
\]

\[
\boxed{
\widehat c_M(t_N)
\equiv F_M(t_N)
\equiv \frac{c_M^{\rm raw}(t_N)}{3},
\qquad
\mathcal C_N(t_N)=|\widehat c_M(t_N)|^2.
}
\tag{2}
\]

在零动量转移处，

\[
\boxed{
c_M^{\rm raw}(0)=3,\qquad
\widehat c_M(0)=F_M(0)=1.
}
\tag{3}
\]

因此，项目文档和代码中凡是写成 \(c_M=1\) 的 P0 结论，都应明确理解为归一化系数 \(\widehat c_M=1\)。原始 flavor-summed 系数并不是 1，而是 3。

**一句话区分：** \(c_M^{\rm raw}\) 是对单位 \(u+d+s\) 夸克流定义的原始系数；\(\widehat c_M=F_M\) 是已经除去共同因子 3、与本项目外部核子耦合约定配套的无量纲核子电荷因子；\(W_M\) 则是原子核多体响应。

## 2. 因子 3 从哪里来？

### 2.1 当前模型采用的夸克矢量流

当前匹配使用三个味道具有相同单位矢量耦合的流：

\[
J_{uds}^{\mu}
=
\bar u\gamma^\mu u
+\bar d\gamma^\mu d
+\bar s\gamma^\mu s.
\tag{4}
\]

在零动量转移处，Dirac 形状因子 \(F_1(0)\) 给出相应矢量荷。矢量荷计数的是净夸克数，即夸克数减反夸克数：

| 核子 | 净 \(u\) 数 | 净 \(d\) 数 | 净 \(s\) 数 | \(u+d+s\) 总矢量荷 |
|---|---:|---:|---:|---:|
| 质子 \(p\) | 2 | 1 | 0 | 3 |
| 中子 \(n\) | 1 | 2 | 0 | 3 |

海夸克对在零动量转移的净矢量荷中相互抵消。因此，质子和中子在这个等耦合流下具有相同的零动量矢量荷：

\[
F_1^{uds,p}(0)=F_1^{uds,n}(0)=3.
\tag{5}
\]

### 2.2 仓库采用的电磁—奇异流重建

代码中的同位旋重建约定是

\[
F_i^{uds,N}(t_N)
=
3\left[
F_i^{\mathrm{EM},p}(t_N)
+F_i^{\mathrm{EM},n}(t_N)
+F_i^{s,N,\mathrm{unit}}(t_N)
\right].
\tag{6}
\]

这里的奇异形状因子必须对应单位流
\(\bar s\gamma^\mu s\)，而不是已经乘入电荷 \(e_s=-1/3\) 的电磁加权流。不同奇异流输入的换算规则见 [strange-current convention audit](strange_current_convention_audit.md)。

在零动量转移处，

\[
F_1^{\mathrm{EM},p}(0)=1,\qquad
F_1^{\mathrm{EM},n}(0)=0,\qquad
F_1^{s,N,\mathrm{unit}}(0)=0.
\tag{7}
\]

代入式 (6)：

\[
\boxed{
F_1^{uds,N}(0)=3(1+0+0)=3.
}
\tag{8}
\]

由于式 (1) 中有限转移项正比于 \(t_N\)，在 \(t_N=0\) 时它消失，于是

\[
c_M^{\rm raw}(0)=F_1^{uds,N}(0)=3.
\tag{9}
\]

这就是因子 3 的来源：它是 \(u+d+s\) 单位矢量流对一个核子的零动量电荷归一化，不是 AFH 核响应的归一化，也不是额外拟合参数。

## 3. 为什么计算中使用除以 3 的系数？

本项目的外部核子耦合约定为

\[
g_{VN}=3g_{Vq},
\tag{10}
\]

其中 \(g_{Vq}\) 是每个 \(u,d,s\) 味道的共同夸克矢量耦合，\(g_{VN}\) 是已经包含三个净价夸克单位电荷的核子耦合。

因此，振幅中的耦合与原始系数满足

\[
g_{Vq}\,c_M^{\rm raw}
=
(3g_{Vq})\,\frac{c_M^{\rm raw}}{3}
=
g_{VN}\,\widehat c_M.
\tag{11}
\]

这条恒等式说明了为什么程序把 \(c_M^{\rm raw}\) 除以 3：

- 如果振幅前因子使用夸克耦合 \(g_{Vq}\)，就配套使用原始系数 \(c_M^{\rm raw}\)；
- 如果振幅前因子已经使用核子耦合 \(g_{VN}=3g_{Vq}\)，就配套使用归一化系数 \(\widehat c_M=c_M^{\rm raw}/3\)。

本项目采用第二种写法。因此实际 rate-level 核子因子为

\[
F_M=\widehat c_M=\frac{c_M^{\rm raw}}{3},
\qquad
\mathcal C_N=|F_M|^2.
\tag{12}
\]

**因子 3 只计入一次。** 不能在已经使用 \(g_{VN}=3g_{Vq}\) 的同时，再把原始 \(c_M^{\rm raw}\) 不经归一化地乘入振幅；那样会重复计算同一个核子矢量荷。

## 4. \(c_M\) 如何从 Dirac–Pauli 核子流得到？

核子级矢量流写为

\[
J_N^\mu
=
\bar u_N(p_N')
\left[
F_1^V(t_N)\gamma^\mu
+\frac{iF_2^V(t_N)}{2m_N}
\sigma^{\mu\nu}q_{N,\nu}
\right]
u_N(p_N).
\tag{13}
\]

其中：

- \(F_1^V\) 是 Dirac 形状因子；
- \(F_2^V\) 是 Pauli 形状因子；
- \(t_N=q_N^2\) 是核子流的不变动量转移；
- \(m_N\) 是核子质量。

在本项目采用的核子电荷型非相对论匹配约定中，进入 \(M\)-only rate-level 实现的系数是

\[
c_M^{\rm raw}(t_N)
=
F_1^{uds,N}(t_N)
+\frac{t_N}{8m_N^2}
\left[F_1^{uds,N}(t_N)+2F_2^{uds,N}(t_N)\right].
\tag{14}
\]

将式 (6) 的整体因子 3 提出，可定义归一化形状因子

\[
\widehat F_i^N(t_N)
\equiv \frac{F_i^{uds,N}(t_N)}{3},
\tag{15}
\]

从而

\[
\boxed{
\widehat c_M(t_N)=F_M(t_N)
=
\widehat F_1^N(t_N)
+\frac{t_N}{8m_N^2}
\left[\widehat F_1^N(t_N)+2\widehat F_2^N(t_N)\right].
}
\tag{16}
\]

式 (14) 与式 (16) 是同一个匹配系数的两种归一化写法，二者满足式 (2)。不能把式 (14) 的原始 flavor-summed 形状因子与式 (16) 的归一化形状因子混用。

这里的 \(c_M\) 公式是当前 \(M\)-only rate-level 匹配处方中的核子电荷型系数。它用于当前 P0/P/A0/B 比较，不等同于已经完成完整三体核流的所有多极矩和所有 AFH 响应的协变张量匹配。

## 5. \(c_M\) 与 AFH \(W_M\) 为什么不是同一个量？

将外部核子耦合 \(g_{VN}\) 提出后，核子电荷型算符的示意形式为

\[
J_A^0(\mathbf q_A)
\sim
\sum_{i=1}^{A}
\widehat c_M^{N_i}(t_N)
e^{i\mathbf q_A\cdot\mathbf r_i}.
\tag{17}
\]

式 (17) 中：

- \(\widehat c_M^{N_i}\) 是第 \(i\) 个核子的单体电荷型匹配系数；
- \(e^{i\mathbf q_A\cdot\mathbf r_i}\) 描述核子在原子核内部的位置相位；
- 对全部核子求和并在核态之间取矩阵元，才形成原子核的多体电荷算符。

AFH 将该类核算符投影到原子核多极矩，得到 \(M\) 型核响应 \(W_M(y_A)\)。因此两个量处在不同层次：

| 量 | 所属层次 | 物理含义 | 是否描述原子核内部多体结构 |
|---|---|---|---|
| \(F_1,F_2\) | 单核子 | Dirac、Pauli 形状因子 | 否 |
| \(c_M^{\rm raw}\) | 单核子流匹配 | 原始 flavor-summed 电荷型系数 | 否 |
| \(\widehat c_M=F_M\) | 单核子流匹配 | 除去公共因子 3 后的核子电荷因子 | 否 |
| \(W_M(y_A)\) | 原子核 | AFH 多体电荷响应 | 是 |
| \(y_A\) | 原子核运动学 | AFH 振子变量 | 不适用 |

AFH 振子变量为

\[
y_A=\frac{b_A^2Q_A^2}{4}.
\tag{18}
\]

所以

\[
\boxed{\widehat c_M=1\quad\not\Rightarrow\quad W_M(y_A)=1.}
\tag{19}
\]

\(\widehat c_M=1\) 只表示采用单位归一化的点状核子电荷基准；它不表示把整个氙原子核当成点核。当前计算仍保留 AFH 有限尺寸 \(W_M(y_A)\)。

## 6. P0 与 P：为什么一个取 1，另一个保留有限转移项？

P0 与 P 使用相同的点状 Dirac 形状因子：

\[
\widehat F_1=1,\qquad \widehat F_2=0.
\tag{20}
\]

区别在于当前 \(M\)-only 匹配中保留到哪一阶。

### P0：领先阶点核子电荷基准

P0 忽略式 (16) 中有限转移的 \(1/m_N^2\) 项：

\[
\boxed{
\widehat c_M^{P0}=F_M^{P0}=1,
\qquad
c_M^{\rm raw,P0}=3.
}
\tag{21}
\]

它是项目早期三体反冲率的领先阶 charge-only 基准。

### P：有限动量点状 Dirac 电荷基准

P 保持相同的点状形状因子，但保留有限转移项：

\[
\widehat c_M^P
=
1+\frac{t_N}{8m_N^2}
=
1-\frac{Q_N^2}{8m_N^2},
\qquad Q_N^2\equiv -t_N.
\tag{22}
\]

对应的原始系数为

\[
c_M^{\rm raw,P}=3\widehat c_M^P.
\tag{23}
\]

因此 P0 与 P 的区别不是核子内部结构不同，而是当前匹配处方保留的有限转移阶数不同。P0 是 P 的领先阶近似。

## 7. 必须分开的动量变量

在本项目采用的形式冲量约定下，

\[
t_N=t_A=-2m_AE_R,
\tag{24}
\]

\[
Q_N^2=-t_N=2m_AE_R,
\tag{25}
\]

而 AFH 使用的精确空间动量平方是

\[
Q_A^2=|\mathbf q_A|^2=2m_AE_R+E_R^2.
\tag{26}
\]

因此：

- \(t_N\) 是核子形状因子和匹配系数的洛伦兹不变变量；
- \(Q_N^2=-t_N\) 是当前 P 有限转移修正使用的正数；
- \(Q_A^2\) 是 AFH 核响应的空间傅里叶变量；
- \(y_A=b_A^2Q_A^2/4\) 进入 AFH \(W_M\)。

不能把 \(Q_A^2\) 直接替换到式 (22) 中，也不能把 P 的核子有限转移修正称为 AFH 核有限尺寸修正。

## 8. 对振幅、微分率和天然氙求和的影响

对单个同位素、固定 \(E_R\)，在当前只保留 \(W_M\) 且其他动力学输入相同的 P0/P 比较中，

\[
\frac{\mathcal M_P}{\mathcal M_{P0}}
=
\frac{\widehat c_M^P}{\widehat c_M^{P0}}
=
1-\frac{Q_N^2}{8m_N^2},
\tag{27}
\]

因此

\[
\boxed{
\frac{d\sigma_P/dE_R}{d\sigma_{P0}/dE_R}
=
\left|\,\widehat c_M^P\,\right|^2
=
\left(1-\frac{Q_N^2}{8m_N^2}\right)^2.
}
\tag{28}
\]

天然氙必须逐同位素乘上各自的核子因子后再求和：

\[
\frac{dR_P}{dE_R}
=
\sum_A \eta_A
\frac{dR_{P0,A}}{dE_R}
\left|\,\widehat c_{M,A}^P(E_R)\,\right|^2,
\tag{29}
\]

\[
\frac{dR_{P0}}{dE_R}
=
\sum_A\eta_A\frac{dR_{P0,A}}{dE_R}.
\tag{30}
\]

所以天然氙总谱的 P/P0 比值是由各同位素 P0 贡献加权后的结果，不是简单地取某一个同位素的 \(|\widehat c_M|^2\)。

## 9. Xe-131 数值示例

使用

\[
m_A(^{131}\mathrm{Xe})=121.933\ \mathrm{GeV},
\qquad m_N=0.938919\ \mathrm{GeV},
\]

并按 \(Q_N^2=2m_AE_R\) 计算：

| \(E_R\) (keV) | \(Q_N\) (MeV) | \(\widehat c_M^P\) | P/P0 微分率比 |
|---:|---:|---:|---:|
| 5.4 | 36.29 | 0.9998133 | 0.9996266 |
| 50 | 110.42 | 0.9982711 | 0.9965451 |
| 100 | 156.16 | 0.9965422 | 0.9930963 |
| 200 | 220.85 | 0.9930843 | 0.9862165 |
| 269.9 | 256.55 | 0.9906673 | 0.9814217 |

例如 \(E_R=200\ \mathrm{keV}\) 时，

\[
\widehat c_M^P=0.9930843,
\qquad
\frac{d\sigma_P/dE_R}{d\sigma_{P0}/dE_R}
=0.9862165.
\tag{31}
\]

即该点的微分率相对 P0 降低约 \(1.38\%\)。这只是单同位素、固定反冲能量的 P/P0 核子匹配效应，不是天然氙探测器级总事件数比值。

## 10. 代码变量与输出列的对应关系

代码实现应与式 (1)–(2) 一一对应：

| 代码位置 | 字段/函数 | 规范含义 |
|---|---|---|
| borah2020_lowq2.py | flavor_sum_form_factors 的 F1uds、F2uds | 原始 \(u+d+s\) flavor-summed 形状因子 |
| borah2020_lowq2.py | cM_raw | 式 (1) 的原始系数 |
| borah2020_lowq2.py | cM_hat | 式 (2) 的归一化系数 |
| borah2020_lowq2.py | F_M | 与 cM_hat 相同的归一化核子电荷因子 |
| borah2020_lowq2.py | rate_multiplier | \(|F_M|^2=|\widehat c_M|^2\) |
| compare_pointlike_A_B_nucleon_baselines.py | cMhat_P0、cMhat_P、cMhat_A0、cMhat_B | 均为归一化系数，不是原始 \(c_M^{\rm raw}\) |

为保持旧结果和脚本兼容，已有输出字段 cM、c_M 保留为原始系数的历史别名；新输出同时提供显式字段 cM_raw / c_M_raw 和 cM_hat / c_M_hat。已有 F_M、F_M_normalized 是归一化系数的别名。新代码和新文档优先使用带 raw 或 hat 的显式名称。

## 11. 后续统一记号规则

| 推荐写法 | 含义 | 不应混用为 |
|---|---|---|
| \(c_M^{\rm raw}\) | 原始 flavor-summed 匹配系数，零转移为 3 | P0 中取 1 的系数 |
| \(\widehat c_M\) | 除以 3 后的归一化匹配系数 | 原始 flavor-summed 系数 |
| \(F_M\) | 本项目定义的归一化核子电荷因子，\(F_M=\widehat c_M\) | AFH 核响应 |
| \(W_M(y_A)\) | AFH 有限尺寸原子核 \(M\) 响应 | 核子形状因子或单核子匹配系数 |
| \(Q_N^2\) | 当前形式冲量约定下的核子不变转移正数 \(-t_N\) | AFH 空间动量平方 \(Q_A^2\) |
| \(Q_A^2\) | AFH 核响应使用的精确空间动量平方 | 核子形状因子的 \(Q_N^2\) |

今后凡是写“\(c_M=1\)”，必须注明这是 \(\widehat c_M=1\)。若指原始系数，必须写 \(c_M^{\rm raw}\)。

## 12. 适用范围

本文规范解决的是当前 P0/P/A0/B 比较中单核子电荷型系数的原始归一化、外部耦合归一化和 AFH \(W_M\) 的层次区分。当前 P0/P/A0/B 数值比较采用 \(M\)-only rate-level 处方，并保留 AFH 有限尺寸 \(W_M\)。

它不把 \(W_{\Phi''}\)、\(W_{M\Phi''}\) 等其他 AFH 响应自动包含进来，也不把当前 \(c_M\) 因子解释为完整三体协变核流的全部匹配系数。扩展到完整单体核流时，必须对相应核子流分量、AFH 响应和干涉项分别进行匹配，不能把本节的单一 \(\widehat c_M\) 乘子直接套用到所有核响应。

## 13. 相关项目文件

- [B baseline README](README.md)：有限核子形状因子与 AFH 有限尺寸电荷响应的计算入口。
- [P0/P detailed baseline](P0_VS_P_POINTLIKE_DIRAC_BASELINES.md)：P0/P 公式、动量约定、Xe-131 曲线和 LZ 探测器级比较。
- [Four-level P0/P/A0/B comparison](POINTLIKE_NUCLEON_P_A_B_COMPARISON.md)：四级基准及数值事件率。
- [Strange-current convention audit](strange_current_convention_audit.md)：单位奇异流与电磁加权奇异流的换算。
