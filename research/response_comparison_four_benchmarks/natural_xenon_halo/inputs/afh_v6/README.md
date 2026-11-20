# 七种氙同位素的原生 AFH 参考网格

事例数程序读取 `native/` 中 Xe-128、129、130、131、132、134、136 各自的核响应。每份表有 2,401 个等距动量点，$q=0$ 至 $0.6$ GeV，步长 $0.00025$ GeV。表内为 AFH v6.0 原始同位旋标量 $W_X^{00}$，包含八个实部和对应的虚部。质子与中子等耦合的转换在散射程序中进行，约定为 $R_M(0)=A^2$。[事例数计算和参数](../../event_counts/README.md)

这些文件由 2026-11-18 的本机 Wolfram 14.2 验收运行导出，使用 AFH v6.0 默认核密度。原生导出和独立 Python 实现比较了 16,807 个动量点，每点八个响应。原生 CSV、逐点比较摘要和源码索引按原始 SHA-256 核对并保存。[原生计算程序](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/blob/dcefbeb7ad705b6c03f2b4689200eb1d9252e67b/research/afh_full_response_database/run_afh_full_response_database.wls) · [原生与 Python 对照程序](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/blob/dcefbeb7ad705b6c03f2b4689200eb1d9252e67b/research/afh_full_response_database/compare_native_afh_full_response.py) · [源码文件及 Git blob](source-files.json)

本目录的校验清单摘录了上游验收包中对应九个文件的原始摘要。路径相对于本目录。重算命令以本目录作为 `--native-archive` 的参数。[验收结果与容差](native-comparison.json) · [输入 SHA-256](SHA256SUMS.txt)
