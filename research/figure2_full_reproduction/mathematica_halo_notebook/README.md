# 三体微分截面与天然氙事件率

打开 `Figure2_三体微分截面与天然氙事件率.nb`，将 `dmformfactor-V6.m` 放在同一目录，并从头依次运行。需要本机 Mathematica 和 FeynCalc；部分末尾验证还需要 FeynArts 或 FeynRules。

主计算采用极点宽度、FeynCalc 自旋迹及 Mathematica NIntegrate。笔记本依次计算固定速度单核素微分截面、速度与同位素平均、总截面及事件率。完整嵌套积分耗时，示例开关默认关闭。AFH 核响应包含核 form factor；单核子 form factor 采用常数近似。

提交前在 Xe-131 单点运行了主计算并检查阈值，尚未重新计算完整反冲能谱和所有嵌套积分。
