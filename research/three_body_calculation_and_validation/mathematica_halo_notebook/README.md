# 矢量耦合暗物质三体散射与天然氙反冲率

主天然氙笔记本与 AFH 输入位于 `../../three_body_natural_xenon/`。主计算需要 Mathematica；笔记本从仓库研究目录加载 FeynCalc，不依赖旧工作区副本或本机绝对路径。笔记本按固定速度单核素微分截面、速度与同位素平均、总截面、事件率排列，使用极点宽度和 NIntegrate。

- `独立验证/`：AFH 核响应、弹性散射、相空间和数值收敛检查。各报告列出验证范围。
- `FeynRules_check/`：矢量耦合模型、生成顶角与 FeynArts/UFO 脚本、第三方软件源码副本及许可证清单。主笔记本的 FeynRules/FeynArts 单元使用相对路径定位此目录。
- `历史笔记本备份/`：本地保存的历史版本，不作为当前计算入口。
- `three_body_rate_engine.wl`：独立验证脚本所需的 Dirac 自旋迹/截面引擎。
- `independent_nintegrate.wl`：独立运动学映射与 Mathematica `NIntegrate` 实现，供 `FeynRules_check/feynrules_feyncalc_*.wls` 调用；与主笔记本分布在不同目录，脚本通过相对路径定位。它与旧本机工作副本字节一致（SHA-256 `046df91518b5bec416c387fcd53dbd394368d2b0a08e20a97c607052baadb0ac`）。

固定速度 Xe-131 单点曾运行检查；完整事件率能谱和新增的全部嵌套积分尚未重新运行。设置耗时积分开关前请检查笔记本中的说明。第三方程序源码、版本、许可证和校验值见 `FeynRules_check/THIRD_PARTY_NOTICES.md` 与 `FeynRules_check/DEPENDENCY_MANIFEST.json`。运行仍需要 Mathematica。
