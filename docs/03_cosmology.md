# 冻结出后演化、标量衰变与额外暗辐射

## 1. 这一部分在整篇研究中的作用

直接探测部分要求轻标量 \(s\) 能够作为额外辐射粒子出现在

\[
\chi_1+A\to\chi_1+A+s
\]

的末态中。宇宙学部分则研究 \(s\) 在早期宇宙中的产生、热化、温度演化及其向无菌中微子 \(N_s\) 的衰变。

因此，两部分必须使用同一组 \(m_s,g_2,y_\nu\) 等参数。不能在直接探测扫描中任意选择 \(s\) 的质量和耦合，再在宇宙学部分独立挑选一个不相关的寿命。

## 2. 草稿采用的热史假设

草稿从重粒子冻结出温度 \(T_f\) 开始演化轻部门，并假设：

- \(V\) 与标准模型保持动理学和化学平衡，\(T_V=T_\gamma\equiv T\)；
- \(V\) 和 \(s\) 使用 Maxwell–Boltzmann 分布；
- 标量具有独立温度 \(T_s\) 和 fugacity \(z_s=n_s/n_s^{\rm eq}(T_s)\)；
- 重粒子历史由 micrOMEGAs 导入；
- 冻结出后 \(n_{\rm heavy}\propto a^{-3}\)；
- 近似 \(\rho_{\rm heavy}\simeq m_{\chi_1}n_{\rm heavy}\)，忽略其动能、质量劈裂修正及对导入冻结出历史的反馈。

这些是模型假设，不是由方程自动保证的结论。最终论文应说明它们在所选 benchmark 下的适用性。

## 3. 标量的数密度与能量矩

草稿定义

\[
f_V=e^{-E_V/T},\qquad
f_s=z_s e^{-E_s/T_s},\qquad
z_s=\frac{n_s}{n_s^{\rm eq}(T_s)}.
\]

玻色/费米统计的精确处理并非当前 MB 基准的一部分。草稿使用

\[
n_i^{\rm eq}(T_i)=
\frac{g_i m_i^2T_i}{2\pi^2}K_2(m_i/T_i),
\]

\[
u_i(T_i)=3T_i+
m_i\frac{K_1(m_i/T_i)}{K_2(m_i/T_i)},
\]

并取 \(g_V=3,\ g_s=1\)。于是

\[
\rho_s=n_su_s(T_s),\qquad P_s=n_sT_s.
\]

重粒子历史写为

\[
n_{\rm heavy}=
\sum_{i=1,2}(n_{\chi_i}+n_{\bar\chi_i})
=s_{\rm SM}Y_{\rm heavy},
\qquad
\rho_{\rm heavy}\simeq m_{\chi_1}n_{\rm heavy}.
\]

## 4. 宇宙学背景与标量源项

草稿采用

\[
\rho_{\rm bath}=\rho_{\rm SM}+n_V^{\rm eq}u_V,
\]

\[
P_{\rm bath}=Ts_{\rm SM}-\rho_{\rm SM}+n_V^{\rm eq}T,
\]

\[
H^2=\frac{8\pi}{3M_{\rm Pl}^2}
(\rho_{\rm bath}+\rho_s+\rho_{N_s}+\rho_{\rm heavy}).
\]

与无菌衰变无关的标量源项分为

\[
C_0=C_{\rm pair}+C_{\rm conv}+C_{\chi_2},
\]

\[
Q_0=Q_{\rm pair}+Q_{\rm elastic}+Q_{\rm conv}
+Q_{\rm heavy}+Q_{\chi_2}^{\rm SM}.
\]

草稿中各项的物理含义为：

- \(VV\leftrightarrow ss\)：标量对产生/湮灭；
- \(Vh\leftrightarrow sh\)，\(h=\chi_1,\bar\chi_1,\chi_2,\bar\chi_2\)：转换过程；
- \(Vs\leftrightarrow Vs\) 与 \(sh\leftrightarrow sh\)：保持标量数目的弹性散射；
- \(\chi_2\leftrightarrow\chi_1s\) 及重态再布居：重态相关的标量源项。

加入衰变源项后，标量矩方程为

\[
\dot n_s+3Hn_s=C_s,\qquad
\dot\rho_s+3H(\rho_s+P_s)=Q_s,
\]

其中 \(C_s=C_0+C_{\rm dec}\)，\(Q_s=Q_0+Q_{\rm dec}\)。草稿还给出 \(T_s\) 与可见部门温度 \(T\) 的演化方程。

实现时要对每个碰撞项分别核对 detailed balance、初末态对称因子、总能量权重和符号约定，不能只检查最后的 \(\Delta N_{\rm eff}\)。

## 5. 标量衰变到无菌中微子

草稿引入一个有效无质量 Majorana 无菌中微子 \(N_s\)：

\[
\mathcal L_{\rm dec}=-\frac{y_\nu}{2}sN_sN_s,
\qquad
\Gamma_s=\frac{y_\nu^2m_s}{16\pi}.
\]

该宽度公式依赖于草稿采用的 Majorana 归一化和质量近似；实现时应重新从所定义的拉格朗日量计算衰变矩阵元，并确认是否还有其他开放衰变道。

草稿使用 MB moment closure 描述 \(N_s\)，并同时演化 \(n_{N_s}\) 和 \(\rho_{N_s}\)。标量衰变与逆衰变项分别进入 \(C_{\rm dec}\) 和 \(Q_{\rm dec}\)。当无菌中微子初始丰度为零时，逆衰变项消失；仅有正向衰变时，草稿给出 \(Q_{\rm dec}=-m_s\Gamma_s n_s\)。

草稿还写出总数和总能量矩的守恒关系，作为内部衰变过程的数值验收条件。实现必须逐时刻检查这些关系，而不应只在最终时刻检查。

## 6. 活跃中微子解耦与 \(\Delta N_{\rm eff}\)

草稿在 MeV 时期令 \(V\) 指数稀少，使用光子/电子正电子电磁浴，并以

\[
T_{\nu,\rm dec}=2\ {\rm MeV}
\]

近似活跃中微子瞬时解耦。解耦前 \(T_\nu=T_\gamma\)，解耦后分别演化 \(T_\nu\) 与 \(T_\gamma\)。

在标量衰变和电子正电子湮灭完成后，额外无菌辐射对应

\[
\Delta N_{\rm eff}
=
\frac{\rho_{N_s}}
{\left[\frac78\left(\frac4{11}\right)^{4/3}\right]\rho_\gamma},
\qquad
\rho_\gamma=\frac{\pi^2}{15}T_\gamma^4 .
\]

注意：这个表达式中标准单个中微子物种的能量密度系数位于分母。写代码时应以该物理定义为准，并用纯辐射极限作单元测试，避免排版或括号造成倒数错误。

草稿报告的参考 benchmark 为：

- MB 处理：\(\Delta N_{\rm eff}\simeq0.043\)；
- 单独的量子平衡热力学检查：\(\Delta N_{\rm eff}\simeq0.046\)；
- 关闭重态对产生或将其速率提高两个数量级，\(\Delta N_{\rm eff}\) 约变化 1%。

这些是当前草稿报告的数值，不代表已经完成全参数扫描，也不应表述为百分比精度预测。草稿明确指出尚未对额外暗辐射存在时的活跃中微子 reheating 作精密重算。

## 7. 宇宙学部分尚未完成的工作

1. 明确完整 benchmark：\(m_V,m_{\chi_1},\Delta m,m_s,g_1,g_2,g_{Vq},y_\nu\) 及冻结出历史。
2. 验证 micrOMEGAs 导入的 \(Y_{\rm heavy}\) 与直接探测参数采用同一组耦合和质量。
3. 对 \(VV\leftrightarrow ss\)、\(Vh\leftrightarrow sh\)、弹性散射和重态源项分别做 detailed-balance 与能量守恒测试。
4. 独立复算 \(\chi_2\to\chi_1s\) 宽度，并核对它与直接探测振幅中的 \(\Gamma_{\chi_2}\) 一致。
5. 扫描 \(y_\nu\) 和 \(m_s\)，检查标量衰变时刻、无菌辐射产生及其对 \(N_{\rm eff}\) 的影响。
6. 将 \(\Delta N_{\rm eff}\) 与 BBN、CMB 及相关暗辐射限制对照；若有可见衰变分支，还需检查能量注入。
7. 检查 \(s\) 在 LZ 探测器尺度上的衰变长度及末态可见性，确保实验信号模型与宇宙学衰变模型一致。
