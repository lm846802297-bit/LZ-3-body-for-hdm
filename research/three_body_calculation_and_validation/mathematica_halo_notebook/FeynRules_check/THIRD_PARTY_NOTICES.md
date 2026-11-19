# 第三方 Mathematica 程序包

本目录包含用于复现本项目计算的外部软件原生文件。各软件的作者、版本与许可分别适用；本项目的物理模型文件不改变这些软件的许可。

| 程序 | 本地版本/来源 | 许可 | 上游 |
|---|---|---|---|
| FeynCalc | 本机安装副本；启动横幅版本 10.2.1-dev；复制日期 2026-11-18 | GPL-3.0；许可文本在 `FeynCalc/COPYING` | https://feyncalc.github.io/ |
| FeynRules | `feynrules-current` 发行归档；UFO 导出记录显示 2.3.49 | GPL-3.0；附上上游仓库许可文本 `feynrules-current/LICENSE-GPL-3.0.txt` | https://github.com/FeynRules/FeynRules |
| FeynArts | 3.12 | LGPL；随包提供 `FeynArts-3.12/manual/FA3Guide.pdf`，其许可说明要求再分发时一并提供手册 | https://feynarts.de/ |

## 使用范围

- FeynCalc 用于 Mathematica 主笔记本的振幅迹和数值积分；
- FeynRules 用于从 `ThreeBodyVV.fr` 推导顶角并重新导出模型；
- FeynArts 用于从导出模型生成树级图；
- 上述程序包是第三方依赖，需遵守各自许可证及引用要求。FeynCalc 的论文引用信息见其上游网站。

`DEPENDENCY_MANIFEST.json` 对复制后的每个文件记录字节数和 SHA-256。为 Windows 兼容，FeynArts 压缩包中的少数符号链接已物化为目标文件副本，内容未修改。
