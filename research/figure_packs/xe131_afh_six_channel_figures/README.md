# Xe-131 AFH 六通道：原图与中文图注

这组文件在原有数值图下方增加中文说明，逐条对照原图中的颜色、线型、点型、坐标和数值。每页保留完整原图，不重新绘制其曲线；新说明是可搜索的 PDF 文字，位于图框下方。

## 文件

- [三页插值审计 PDF（中文图注）](chinese_captions/xe131_six_channel_interpolation_audit_zh.pdf)。
- [五页六通道比较 PDF（中文图注）](chinese_captions/xe131_afh_six_channel_comparison_zh.pdf)。
- 三张插值审计图：[$W_M$ 衍射极小值](chinese_captions/xe131_WM_diffraction_minimum_interpolation_zh.png)、[插值相对差异](chinese_captions/xe131_WM_pchip_vs_cheb10_relative_difference_zh.png)、[近极点六通道比值](chinese_captions/xe131_nearpole_full_over_pointlike_interpolation_zh.png)。
- 六通道比较单图：[B1 远极点比值](chinese_captions/xe131_six_channel_comparison_B1_zh.png)、[B2 近极点比值](chinese_captions/xe131_six_channel_comparison_B2_zh.png)、[B3 空间流修正](chinese_captions/xe131_six_channel_comparison_B3_zh.png)、[B4 电荷响应](chinese_captions/xe131_six_channel_comparison_B4_zh.png)、[B5 空间响应](chinese_captions/xe131_six_channel_comparison_B5_zh.png)。
- 原始无中文图注的 [三页 PDF](originals/xe131_six_channel_interpolation_audit.pdf) 和 [五页 PDF](originals/xe131_afh_six_channel_comparison.pdf) 单独保存在 `originals/`，未覆盖用户原有文件。
- [输出清单](chinese_captions/manifest.json) 记录原稿、输入的 SHA-256 和全部成品的大小与 SHA-256。

**图像分辨率：**三页审计原稿内嵌的三张图分别只有 667×397、667×397 和 667×398 像素。成品 PNG 按 200 dpi 输出，新增的中文文字清晰，但原图部分仍受原稿像素限制；未找到单独的高分辨率原始 PNG。五页比较原稿的曲线为矢量，PDF 保持矢量形式。

## 数值与科学范围

- 曲线与数据来自固定速度 Xe-131 六通道扫描，GitHub Actions run `44307471788`，artifact `14430267797`，扫描代码提交 `f5e22bcb0f1a3d215724168397737a505b945824`。归档的响应网格、扫描数据和元数据位于 `data/`，其摘要与原 artifact 的 `SHA256SUMS.txt` 一致。
- `data/xe131_six_channel_interpolation_audit.csv` 是使用原审计脚本重新计算的 140 行表，输入为上述扫描和响应网格；脚本的 Git blob 为 `1c11aad843e42633894f4cbab8f9b349f2d8f0e3`，位于 `research/three_body_full_current_nucleon_match/audit_xe131_six_channel_interpolation.py` 的相关研究分支。
- 插值审计图 A2 的纵轴为 $100(W_M^{\rm PCHIP}/W_M^{\rm Cheb10}-1)$。图内连续曲线的正峰约为 2.23%；扫描表所报约 1.685% 使用离散扫描点和另一相对差异分母，两者不能直接当成同一个最大值。
- 图 A3 及 B1、B2 的点状 $M$ 分母在代码中为 $9L_CW_M$：点状近似用于核子耦合，分母仍保留有限动量下的核响应 $W_M$。图 B3 是空间与电荷散射核之比，单位为十亿分数，不是裸核响应之比。
- 图中的六通道和宽度比较属于归档的固定速度、领先阶静态单体矢量流诊断。三个空间响应是 AFH 源码的 Python 转写，归档时尚未独立通过原生 Wolfram 验证。PCHIP 与局部多项式采用同一个粗网格，不能取代更密网格的原生 AFH 计算。这里没有重新积分三体相空间，也没有计算天然氙或探测器事例率。

## 重建

在本目录运行 `python build_chinese_captions.py`。需要 Python、`matplotlib`、`pymupdf`、`reportlab` 和 `fonttools`，以及 Windows 字体 `NotoSerifSC-VF.ttf`、`NotoSansSC-VF.ttf`；STIX 数学字体使用 Matplotlib 自带版本。程序校验两个原稿和三个扫描输入的 SHA-256，随后生成 PDF、八张 PNG 和 `manifest.json`。上述作图部分沿用原页，重建过程不改变物理曲线和数据。
