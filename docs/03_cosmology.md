# 冻结出后演化、标量衰变与额外暗辐射

## 1. 这一部分在整篇研究中的作用

论文主源码 \`paper-source/main.tex\` 在补充部分研究轻标量 \(s\) 从重粒子冻结出温度 \(T_f\) 开始的演化，以及其衰变到有效无质量 Majorana 无菌中微子 \(N_s\) 后对 \(\Delta N_{\rm eff}\) 的贡献。本文件以主源码实际保留的碰撞项为准。

## 2. 主源码采用的热史假设和初始条件

源码假设：
- \(V\) 与 SM 保持动理学和化学平衡，\(T_V=T_\gamma\equiv T\)；
- \(V\) 和 \(s\) 使用 Maxwell–Boltzmann 分布；
- 标量有独立温度 \(T_s\) 和 fugacity \(z_s=n_s/n_s^{\rm eq}(T_s)\)；
- 重粒子 \(\chi_{1,2},\bar\chi_{1,2}\) 的冻结出历史从 micrOMEGAs 导入；
- 冻结出完成后 \(n_{\rm heavy}\propto a^{-3}\)，并近似 \(\rho_{\rm heavy}\simeq m_{\chi_1}n_{\rm heavy}\)，忽略动能、质量劈裂修正及其对导入冻结出历史的反馈。

初始条件为
\[
T_s(T_f)=T_f,\qquad n_s(T_f)=n_s^{\rm eq}(T_f),
\]
\[
n_{N_s}(T_f)=0,\qquad \rho_{N_s}(T_f)=0.
\]

平衡密度与平均能量为
\[
n_i^{\rm eq}(T_i)=\frac{g_i m_i^2T_i}{2\pi^2}K_2(m_i/T_i),
\quad g_V=3,\quad g_s=1,
\]
\[
u_i(T_i)=3T_i+m_i\frac{K_1(m_i/T_i)}{K_2(m_i/T_i)}.
\]
于是 \(\rho_s=n_su_s(T_s)\)，\(P_s=n_sT_s\)。

## 3. 源码真正保留的标量源项

**重要：** 主源码只保留
\[
VV\leftrightarrow ss,\qquad Vs\leftrightarrow Vs,
\]
以及标量衰变/逆衰变 \(s\leftrightarrow N_sN_s\)。因此
\[
C_0=C_{\rm pair},\qquad
Q_0=Q_{\rm pair}+Q_{\rm elastic}.
\]

源码明确忽略：
- heavy-catalyzed conversion \(Vh\leftrightarrow sh\)；
- \(\chi_2\) 衰变和逆衰变导致的净标量源；
- 重粒子碰撞以及与 SM 热浴散射导致的激发态再生效应。

源码称这些省略对所考虑 benchmark 的最终 \(\Delta N_{\rm eff}\) 影响不大，但没有在主文件中给出完整 benchmark 输入和可复现的逐项对照。该判断应作为待独立检验的近似，而不是已经验证的普遍结论。

## 4. 标量矩方程

源码定义
\[
C_s=C_0+C_{\rm dec},\qquad Q_s=Q_0+Q_{\rm dec},
\]
并演化
\[
\dot n_s+3Hn_s=C_s,
\qquad
\dot\rho_s+3H(\rho_s+P_s)=Q_s.
\]
令 \(c_{V,s}={\rm d}u_s/{\rm d}T_s\)，温度方程为
\[
\dot T_s=
\frac{Q_s-u_sC_s-3Hn_sT_s}{n_sc_{V,s}},
\]
\[
\dot T=
-\frac{3H(\rho_{\rm bath}+P_{\rm bath})+Q_0}
{{\rm d}\rho_{\rm bath}/{\rm d}T}.
\]
源码强调 SM 热浴只损失 \(Q_0\)，不损失内部交换项 \(Q_{\rm dec}\)，并忽略残余重粒子湮灭加热。

## 5. \(VV\leftrightarrow ss\) 对产生

源码定义平衡事件密度
\[
\gamma_{VV\to ss}^{\rm eq}(T)
=\frac12[n_V^{\rm eq}(T)]^2\langle\sigma v_{\rm Mol}\rangle
\]
并给出相应的 Bessel 积分表达式。总能量矩 \(\mathcal E_{VV\to ss}^{\rm eq}\) 使用 \(K_2\) 权重。Detailed balance 给出
\[
C_{\rm pair}
=2\left[\gamma_{VV\to ss}^{\rm eq}(T)
-z_s^2\gamma_{VV\to ss}^{\rm eq}(T_s)\right],
\]
\[
Q_{\rm pair}
=\mathcal E_{VV\to ss}^{\rm eq}(T)
-z_s^2\mathcal E_{VV\to ss}^{\rm eq}(T_s).
\]
源码说明 \(Q_{\rm pair}\) 不再额外乘 2，因为 \(\mathcal E^{\rm eq}\) 已按每次反应的总能量加权。

## 6. \(Vs\leftrightarrow Vs\) 弹性热交换

该过程不改变标量数目，只转移能量。源码以动量转移截面
\[
\sigma_T(s)=\int{\rm d}\Omega_*(1-\cos\theta_*)
\frac{{\rm d}\sigma_{Vs\to Vs}}{{\rm d}\Omega_*}
\]
构造 \(Q_{\rm elastic}\)，并得到含
\[
\left(\frac1{T_s}-\frac1T\right)
\]
的积分表达式。因此该项在 \(T_s=T\) 时消失，并把能量传向较冷的分布。

## 7. 标量衰变和无菌暗辐射

源码引入
\[
\mathcal L_{\rm dec}
=-\frac{y_\nu}{2}s\overline{N_s}N_s,
\qquad
\Gamma_s=\frac{y_\nu^2m_s}{16\pi}.
\]
无菌中微子使用 MB moment closure：
\[
f_{N_s}=z_{N_s}e^{-p/T_{N_s}},\quad
n_{N_s}^{\rm eq}=\frac{2T_{N_s}^3}{\pi^2},
\quad
\rho_{N_s}=3n_{N_s}T_{N_s}.
\]

衰变和逆衰变源项分别为
\[
C_{\rm dec}
=\frac{\Gamma_sm_s^2}{2\pi^2}
\left[z_{N_s}^2T_{N_s}K_1(m_s/T_{N_s})
-z_sT_sK_1(m_s/T_s)\right],
\]
\[
Q_{\rm dec}
=\frac{\Gamma_sm_s^3}{2\pi^2}
\left[z_{N_s}^2T_{N_s}K_2(m_s/T_{N_s})
-z_sT_sK_2(m_s/T_s)\right].
\]
无菌初始丰度为空时逆衰变项为零；仅有正向衰变时，源码给出 \(Q_{\rm dec}=-m_s\Gamma_sn_s\)。并同时演化
\[
\dot n_{N_s}+3Hn_{N_s}=-2C_{\rm dec},
\qquad
\dot\rho_{N_s}+4H\rho_{N_s}=-Q_{\rm dec}.
\]

源码给出总共动数和总共动能量关系作为内部一致性检查。数值实现应逐步监测这些关系，而不是只检查最终值。

## 8. 活跃中微子解耦与 \(\Delta N_{\rm eff}\)

源码在 MeV 时期认为 \(V\) 指数稀少，电磁浴由光子和电子/正电子组成，后者使用 Fermi–Dirac 统计。活跃中微子瞬时解耦近似取
\[
T_{\nu,\rm dec}=2\ {\rm MeV}.
\]
解耦前 \(T_\nu=T_\gamma\)，解耦后 \(\dot T_\nu=-HT_\nu\)，并单独演化电磁浴温度。

标量衰变和电子正电子湮灭完成后，
\[
\Delta N_{\rm eff}
=\frac{\rho_{N_s}}
{\frac78(\frac4{11})^{4/3}\rho_\gamma},
\qquad
\rho_\gamma=\frac{\pi^2}{15}T_\gamma^4.
\]
源码将额外贡献单独报告，或用 \(N_{\rm eff}\simeq3.045+\Delta N_{\rm eff}\) 表示。

源码的参考 benchmark 报告：
- MB 处理：\(\Delta N_{\rm eff}\simeq0.043\)；
- 独立量子平衡热力学检查：\(\Delta N_{\rm eff}\simeq0.046\)；
- 关闭重粒子对再生或将其速率提高两个数量级，最终 \(\Delta N_{\rm eff}\) 约变化 1%。

这些数字尚缺少完整 benchmark 输入、代码和误差预算。源码也明确说明没有对存在暗辐射时的活跃中微子 reheating 作精密重算。

## 9. 后续必须验证的内容

1. 公开完整的 \(m_V,m_{\chi_1},\Delta m,m_s,g_1,g_2,g_{Vq},y_\nu,T_f\) benchmark。
2. 核对 micrOMEGAs 冻结出历史与直接探测模型参数一致。
3. 分别验证 \(VV\leftrightarrow ss\) 的事件密度、能量矩、对称因子和 detailed balance。
4. 独立验证 \(Vs\leftrightarrow Vs\) 的动量转移截面和能量转移积分。
5. 验证衰变/逆衰变的数密度与能量矩，以及总数/总能量守恒。
6. 对被忽略的 \(Vh\leftrightarrow sh\) 和 \(\chi_2\) 衰变/逆衰变源项做定量开关对照，检验“约 1%”近似是否适用于扫描范围。
7. 将同一组参数与 BBN、CMB 和 LZ 探测器尺度的标量衰变长度/可见性关联起来。
