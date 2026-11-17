# 矢量夸克耦合到氙核子的匹配与当前 AFH 响应计算边界

## 1. 目的与结论

本文固定当前论文采用的 flavor-universal vector-quark benchmark，并给出其在零动量转移下的核子匹配；同时区分已经归档的 AFH 电荷响应计算与尚未完成的横向空间流响应计算。

**当前 benchmark 的等质子、等中子耦合不是任意假设。** 若媒介子与所有轻夸克的矢量流普适耦合，
`g_u=g_d=g_s=\cdots=g_{Vq}`,
则在零动量转移下
`g_p=2g_u+g_d=3g_{Vq}`,
`g_n=g_u+2g_d=3g_{Vq}`。
这对应重子数型矢量流（整体归一化可吸收到耦合常数中）。

该结论是零动量矢量电荷匹配，不意味着有限 `q^2` 下质子、中子的 Dirac/Pauli 形状因子相同，也不意味着所有核流响应都由 `W_M` 描述。

## 2. 夸克—核子匹配

取
[
J_q^\mu=g_u\bar u\gamma^\mu u+g_d\bar d\gamma^\mu d+\cdots .
]
零动量转移时，矢量电荷等于各 flavor 的净数目。忽略重味核子净价夸克数后，
[
g_p=2g_u+g_d,\qquad g_n=g_u+2g_d.
]
定义
[
g_0=\frac{g_p+g_n}{2}=\frac32(g_u+g_d),\qquad
g_1=\frac{g_p-g_n}{2}=\frac12(g_u-g_d).
]
故 flavor-universal benchmark 给出 `g_1=0`、`g_0=3g_{Vq}`。这正是等标量核子耦合。

对一般 `U(1)'`，`g_u,g_d` 由具体电荷赋值决定，不能在没有 UV charge assignment 时任意指定 `g_p/g_n`。例如纯电磁电荷方向（暗光子极限）满足 `g_u=2e\epsilon/3`、`g_d=-e\epsilon/3`，于是 `g_p=e\epsilon`、`g_n=0`。这是不同的模型 benchmark，不是当前普适重子数型 benchmark 的修正。

## 3. 有限动量转移

有限动量转移时应使用核子矢量流形状因子：
[
\langle N(p')|J^\mu|N(p)\rangle=
\bar u_N(p')\left[
F_1^N(Q^2)\gamma^\mu+
i\frac{F_2^N(Q^2)}{2m_N}\sigma^{\mu\nu}q_\nu
\right]u_N(p).
]
这里 `F_1^N(0)` 固定净矢量电荷；`F_2^N(0)` 是 Pauli 磁矩项。因而有限 `Q^2` 的电荷、对流和磁化流分别涉及不同的 form-factor 组合。将 `g_p=g_n` 直接当作所有空间分量的相同点状系数，只能作为点核/低能基准，不能替代完整单核子流匹配。

在非相对论展开中，核子流包含电荷密度、对流电流以及磁化电流。后两者可投影到 AFH 的轨道/自旋相关核响应；其大小必须通过与三体暗物质流张量的收缩判断，不能仅凭核子内部速度或 (J_A\ne0) 推断。

## 4. 已完成的 AFH 电荷响应计算

本分支已有七同位素 AFH v6.0 default-density 计算档案。其适用范围为：

- Xe-128、129、130、131、132、134、136；
- 每种同位素 2,401 个空间动量节点，共 16,807 个响应节点；
- 物理等核子耦合归一化为 `R_A(0)=A^2`；
- AFH 原始 isoscalar 响应的因子 4 只映射一次；
- Xe-131 的弹性电荷多极包含 rank-0 与 rank-2。

已有数值闭合结果：
[
\max_{A,q}\left|\frac{R_{A,\mathrm{reconstructed}}(q)}
{R_{A,\mathrm{archived}}(q)}-1\right|
=2.2204\times10^{-16}.
]
这验证已归档的电荷响应及其多极重构的一致性，不是独立核结构模型之间的比较。

Xe-131 的 rank-2 电荷多极在 `q=0.158 GeV` 网格点占总 `M` 响应约 99.51%。这是 `M` 电荷响应内部的多极结构，不是 `W_{\Sigma'}`、`W_\Delta` 或其干涉项。

## 5. 仍未完成的空间核流计算

本分支**没有**声称已经数值计算以下响应：
[
W_\Delta^{00}(q),\quad W_{\Sigma'}^{00}(q),\quad
W_{\Sigma'\Delta}^{00}(q).
]
也没有完成把三体暗物质流张量 `L^{\mu\nu}` 与完整核子流矩阵元收缩后的天然氙总速率。

下一步计算必须按以下顺序完成：

1. 从 AFH v6.0 的 operator definitions 明确映射非相对论单核子矢量流的电荷、对流和磁化项；逐项核对相位、`q/m_N` 因子、isospin convention 与 AFH normalization。
2. 从 Xe-129、Xe-131 对应的 AFH default density matrices 生成 `M`、`Delta`、`Sigma'` 及允许的干涉响应；不得将 `M` 的 rank-2 多极误命名为 `Sigma'`。
3. 对每个三体相空间点计算 `L^{\mu\nu}`，构造完整的 `L_{\mu\nu}W_A^{\mu\nu}`；保留干涉项及 longitudinal/transverse 投影。
4. 做网格/积分收敛和独立极限检查，再比较完整响应与 `L_{00}W_M` 的差异。
5. 只有在上述步骤通过后，才报告横向空间核流对固定速度截面及天然氙 halo-folded rate 的百分比修正。

矢量流守恒给出 longitudinal current 的约束，但不能消去 transverse current。因此仅由 `q_\mu J_A^\mu=0` 不能推出 `W_\Delta` 或 `W_{\Sigma'}` 可忽略。

## 6. 状态

- **已完成：** 七同位素 AFH 电荷响应、factor-four 映射、rank-0/rank-2 重构闭合、同位素有限动量形状比较。
- **解析匹配已完成：** 当前 flavor-universal quark-vector benchmark 在 `Q^2=0` 给出 `g_p=g_n=3g_{Vq}`。
- **未完成：** 单核子有限-`Q^2` form factors 与 AFH 空间流算符匹配；Xe-129/Xe-131 的 `Delta/Sigma'` 数值响应；完整三体张量收缩；完整天然氙 rate comparison。
- **禁止的结论：** 不能依据本档案宣称完整矢量核流已经验证，也不能宣称 `W_M` 对所有反冲能量和所有同位素都足够。

## 7. 复现

从仓库根目录运行：

```bash
python research/afh_isotope_response_equivalence/run_afh_isotope_response_equivalence.py
python -m unittest discover -s research/afh_isotope_response_equivalence/tests -p 'test_*.py' -v
```

生成器输入、输出和 provenance 见本目录 README 及 results 文件。
