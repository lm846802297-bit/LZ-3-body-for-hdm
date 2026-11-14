> 所属主报告：[AFH v6.0 氙核响应与三体暗物质散射](../09_afh_xe131_three_body_scattering_natural_xenon.md)

# 附录 C：AFH isoscalar 归一化与物理核子耦合的因子 4

## C.1 先区分两种不同的 \(c_0\)

标准 isospin 基底中，质子和中子耦合写成

\[
c_{\rm std}^{0}=\frac{c^p+c^n}{2},
\qquad
c_{\rm std}^{1}=\frac{c^p-c^n}{2}.
\]

对物理等质子、等中子耦合

\[
g_p=g_n=g_{VN},
\]

标准 isospin 系数是

\[
\boxed{
c_{\rm std}^{0}=g_{VN},\qquad c_{\rm std}^{1}=0.
}
\]

但 AFH v6.0 分发版 Mathematica 程序的 setter 接口参数不是直接等同于上述标准系数。为避免符号混淆，下面将接口输入记作 \(c_{\rm set}\)。

AFH 的

\[
\texttt{SetCoeffsNonrel[op,c,0]}
\]

在接口内部将质子、中子系数分别设置为

\[
c_p=c_n=\frac{c_{\rm set}}{2}.
\]

因此，要让接口实际产生物理耦合 \(c_p=c_n=g_{VN}\)，必须输入

\[
\boxed{
c_{\rm set}=2g_{VN}.
}
\]

所以“标准 isoscalar 系数 \(c_{\rm std}^{0}=g_{VN}\)”与“AFH setter 输入 \(c_{\rm set}=2g_{VN}\)”并不矛盾；它们是不同层级、不同定义的变量。后续文档不应把这两个量都不加区分地写成同一个 \(c_0\)。

## C.2 从 AFH 原始 \(W_M^{00}\) 到 \(A^2/4\)

AFH 包的调用

\[
\texttt{ResponseNuclear[y,1,0,0]}
\]

返回原始等标量核响应 \(W_{M,\rm AFH}^{00}(y)\)。按 AFH v6.0 包自己的 isoscalar 归一化，定义

\[
R_{\rm AFH,raw}(q)
=
\frac{4\pi}{2J_A+1}
W_{M,\rm AFH}^{00}(y).
\]

在零动量转移处，等标量核算符的单核子电荷带有 \(1/2\)，故相干振幅为 \(A/2\)，对应

\[
\boxed{
R_{\rm AFH,raw}(0)=\left(\frac A2\right)^2=\frac{A^2}{4}.
}
\]

这正是 AFH 原始 isoscalar response 的归一化。它不是已经按物理单核子耦合 \(g_{VN}\) 归一化的 \(A^2\) 响应。

## C.3 物理等质子、等中子耦合为何产生因子 4

对物理相干矢量电荷，

\[
g_p=g_n=g_{VN},
\]

零动量转移时的核振幅为

\[
Zg_p+(A-Z)g_n
=Ag_{VN}.
\]

若截面前因子已经显式提出 \(g_{VN}^2\)，与之相乘的核响应必须满足

\[
R_A^{\rm phys}(0)=A^2.
\]

由上一节 AFH 原始响应的 \(A^2/4\) 归一化，得到

\[
R_A^{\rm phys}(q)=4R_{\rm AFH,raw}(q).
\]

因此

\[
\boxed{
R_A^{\rm phys}(q)
=
\frac{16\pi}{2J_A+1}
W_{M,\rm AFH}^{00}(y)
}
\]

并且在精确的未舍入密度矩阵极限下

\[
R_A^{\rm phys}(0)=A^2.
\]

对有限小数位打印的密度矩阵，数值实现引入一个与 \(q\) 无关的归一化常数

\[
\boxed{
C_A=
\frac{A^2}{4R_{\rm AFH,raw}(0)}
=
\frac{A^2}{
\dfrac{16\pi}{2J_A+1}W_{M,\rm AFH}^{00}(0)}
},
\qquad
R_A^{\rm phys}(q)=
C_A\frac{16\pi}{2J_A+1}W_{M,\rm AFH}^{00}(y).
\]

因此有限精度实现仍只包含一次因子 4；\(C_A\) 只移除打印精度造成的整体归一化偏差，不改变 \(q\) 依赖或响应极小值。在未舍入极限下 \(C_A=1\)。

同一结果也可以在振幅层面理解：AFH setter 要输入 \(c_{\rm set}=2g_{VN}\)，平方后产生 \(c_{\rm set}^2=4g_{VN}^2\)。因此，若把 \(g_{VN}^2\) 留在论文截面前因子中，就必须把这四倍包含在核响应里。

## C.4 三种响应必须分开记录

| 对象 | 定义 | 零动量归一化 |
|---|---|---:|
| AFH 原始 isoscalar response | \(R_{\rm AFH,raw}=4\pi W_M^{00}/(2J_A+1)\) | \(A^2/4\) |
| 物理等 \(p,n\) 相干响应 | \(R_A^{\rm phys}=4C_A R_{\rm AFH,raw}\)（未舍入极限 \(C_A=1\)） | \(A^2\) |
| 论文 Eq. (6) 中的核响应 | 前因子保留 \(g_{VN}^2\)，使用 \(R_A^{\rm phys}\) | \(A^2\) |

等价的另一种记账方式是保留原始 AFH response，但把 \(c_{\rm set}=2g_{VN}\) 的平方显式放在粒子—核子耦合收缩中。两种方式只能选一种，不能既把响应乘 4，又把耦合平方再乘 4。

特别地，夸克到核子的匹配

\[
g_{VN}=3g_{Vq}
\]

是另一条物理关系，与 AFH isoscalar 归一化因子 4 无关；不能通过修改该匹配关系来吸收因子 4。

## C.5 Xe-131 的有限小数精度修正

AFH 内置密度矩阵系数以有限小数位打印。对 Xe-131 的源翻译结果，

\[
R_{\rm AFH,raw}(0)=4289.895955714993,
\]

而理论值为

\[
\frac{A^2}{4}=\frac{131^2}{4}=4290.25.
\]

相对偏差为

\[
8.2522996\times10^{-5}.
\]

先乘因子 4 得到物理等 \(p,n\) 原始响应，其零动量值为

\[
4R_{\rm AFH,raw}(0)=17159.58382285997,
\]

与 \(A^2=17161\) 的差异仍来自密度矩阵的有限打印精度。

为只去除这一整体常数偏差，归档的物理响应采用

\[
\boxed{
C_A=\frac{A^2}{4R_{\rm AFH,raw}(0)}
=1.0000825298069376,
\qquad
R_A^{\rm phys}(q)=C_A\,4R_{\rm AFH,raw}(q)
=A^2\frac{R_{\rm AFH,raw}(q)}{R_{\rm AFH,raw}(0)}.
}
\]

这正是 C.3 中的 \(q\)-independent 修正因子。因子 4 将 AFH 原始 \(A^2/4\) 归一化映射到物理 \(A^2\) 归一化；\(C_A\) 只校正有限打印精度导致的 \(8.2522996\times10^{-5}\) 相对偏差。这个修正不改变 \(q\) 依赖，也不移动响应极小值；它不是对 \(b_A\)、密度矩阵或谷值的拟合。

## C.6 独立文献和源代码核查

源代码审计记录指出：

1. AFH v6.0 的 Response 表达式对 isoscalar 系数使用 \((a_n+a_p)/2\)；
2. FF 例程对质子/中子系数的二阶导数构造包含 \(1/2\)；
3. ResponseNuclear 的 \(00\) 分支对四个质子/中子矩阵项作 \(1/4\) 的组合；
4. setter 接口将输入 \(c_{\rm set}\) 转换为 \(c_p=c_n=c_{\rm set}/2\)。

这与 \(R_{\rm AFH,raw}(0)=A^2/4\) 的数值归一化一致。

独立文献对照：Oliver C. Gorton, *Shell Model Methods, Statistical Nuclear Reactions, and Beta-delayed Neutron Emission*, UC Irvine PhD dissertation (2024), Sec. 2.2, pp. 29–30。该节讨论标准 isospin 系数与分发版 dmformfactor-prc.m / dmformfactor-V6.m 的接口约定差异，并给出

\[
W_M^{00}(0)=\frac{1}{4\pi}\left(\frac A2\right)^2.
\]

参考：

https://www.escholarship.org/content/qt3ns8f1r8/qt3ns8f1r8.pdf

仓库中的源代码归一化记录：

- research/afh_default_density_xe131/AFH_COUPLING_NORMALIZATION_MAPPING.md
- research/afh_default_density_xe131/AFH_DEFAULT_XE131_NORMALIZATION_AUDIT.md
- research/figure2_full_reproduction/ANAND_WM_RESPONSE_AUDIT.md

最终论文 Eq. (6) 的选择是：前因子保留物理单核子耦合 \(g_{VN}\)，核响应使用 \(16\pi W_{M,\rm AFH}^{00}/(2J_A+1)\)，因子 4 只出现一次。

