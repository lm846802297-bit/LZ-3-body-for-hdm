> 所属主报告：[AFH v6.0 氙核响应与三体暗物质散射](../09_afh_xe131_three_body_kernel_natural_xenon_halo_2026-11-11.md)
> 本文件为该主报告的独立技术附录，保留推导、约定和复现边界。

# 附录 C：AFH isoscalar 归一化与物理核子耦合的因子 4

### C.1 物理相干核电荷

对于等质子、等中子矢量耦合，

\[
g_p=g_n=g_{VN}.
\]

零动量转移时，核子的相干振幅正比于

\[
Zg_p+(A-Z)g_n=A g_{VN}.
\]

因此，若截面前因子已经显式提出 \(g_{VN}^2\)，核响应必须满足

\[
R_A^{\rm phys}(0)=A^2.
\]

### C.2 AFH 系数定义

AFH 标准 isospin 分解写作

\[
c^0=\frac{c^p+c^n}{2},
\qquad
c^1=\frac{c^p-c^n}{2}.
\]

对 \(c^p=c^n=g_{VN}\)，得到

\[
c^0=g_{VN},\qquad c^1=0
\]

是标准数学定义下的分解结果。但分布的 DMFormFactor v6.0 Mathematica 接口在其系数设置和响应构造中采用了不同的内部归一化：其 \`SetCoeffsNonrel[op,c,0]\` 接口对应的等质子、等中子输入为 \(c_p=c_n=c/2\)，而 \`ResponseNuclear[y,1,0,0]\` 返回的单个 isoscalar response 在零动量处按 \(A^2/4\) 归一化。

因此，不能仅凭“标准 isospin 分解”这几个字就把接口输入 \(c\) 与论文中定义的物理单核子耦合 \(g_{VN}\) 直接等同。必须按实际包接口的定义进行映射。

### C.3 因子 4 的物理响应映射

对 AFH v6.0 的原始输出，

\[
R_{\rm AFH,raw}(q)
=\frac{4\pi}{2J_A+1}W_{M,\rm AFH}^{00}(q),
\]

其零动量值为

\[
R_{\rm AFH,raw}(0)\simeq\frac{A^2}{4}.
\]

而论文截面前因子使用的是物理的 \(g_{VN}^2\)，故必须使用

\[
\boxed{
R_A^{\rm phys}(q)=4R_{\rm AFH,raw}(q)
=\frac{16\pi}{2J_A+1}W_{M,\rm AFH}^{00}(q)
}
\]

使得

\[
R_A^{\rm phys}(0)=A^2.
\]

这与 \(g_{VN}=3g_{Vq}\) 的夸克到核子匹配是不同问题。因子 4 不改变 \(g_{VN}=3g_{Vq}\)，也不应通过修改 \(b_A\) 或密度矩阵来补偿。

### C.4 有限小数精度修正

Xe-131 的源翻译结果为

\[
R_{\rm AFH,raw}(0)=4289.895955714993,
\qquad
A^2/4=4290.25.
\]

相对偏差

\[
8.2522996\times10^{-5}.
\]

归档物理响应使用

\[
R_A^{\rm phys}(q)
=A^2\frac{R_{\rm AFH,raw}(q)}
{R_{\rm AFH,raw}(0)}.
\]

这是整体零动量归一化修正，不改变响应的 \(q\) 依赖，也不移动响应极小值。其目的在于避免有限小数密度矩阵使零动量相干归一化略微偏离理论值。

### C.5 独立文献对照

Oliver C. Gorton, *Shell Model Methods, Statistical Nuclear Reactions, and Beta-delayed Neutron Emission*, UC Irvine PhD dissertation (2024), Sec. 2.2, pp. 29–30，讨论了标准 isospin 约定与分发的 \`dmformfactor-prc.m\`、\`dmformfactor-V6.m\` 脚本之间的系数约定，并给出

\[
W_M^{00}(0)=\frac{1}{4\pi}\left(\frac A2\right)^2.
\]

参考链接：

https://www.escholarship.org/content/qt3ns8f1r8/qt3ns8f1r8.pdf

该文献是对 AFH v6.0 原始 isoscalar 零动量归一化的独立交叉检查；它不能替代对实际包版本和接口调用的源代码核查。

---
