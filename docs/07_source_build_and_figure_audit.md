> 更新说明（2026-11-11）：本文前述编译记录针对原始源码。原始文件现保存在 `paper-source/main_original.tex`，整理后的工作稿为 `paper-source/main.tex`。本轮整理及新的构建流程见 `paper-source/EDITORIAL_STATUS.md` 和 `paper-source/README.md`。

# 原始论文源码编译与图像审计

## 1. 源码完整性

从用户提供的 \`3body_for_HDM.zip\` 解压后核对：
- \`main_original.tex\`：17,254 bytes，SHA-256 与原 ZIP 完全一致；
- \`ref.bib\`：2,332 bytes，SHA-256 与原 ZIP 完全一致；
- \`utphys28mod.bst\`：30,776 bytes，压缩后提交为 \`utphys28mod.bst.gz\`；解压可恢复原始 SHA-256。
- 七个 figure PDF：按字节原样提交到 \`paper-source/figures/\`，校验清单见 \`paper-source/SHA256SUMS\`。

源码文件没有进行物理内容修改。

## 2. 编译发现与修复方式

原始 \`main_original.tex\` 末尾写为：

\`\`\`tex
\\bibliography{ref.bib}{}
\\bibliographystyle{utphys28mod}
\`\`\`

RevTeX/BibTeX 将 \`ref.bib\` 当作数据库 basename 后再追加扩展名，因此会尝试读取 \`ref.bib.bib\`，造成文献数据库无法正确加载。

为避免静默修改原稿，仓库增加 \`paper-source/build.sh\`：它保留原始 \`main_original.tex\`，生成临时 \`main_build.tex\`，只将上述命令规范化为 \`\\bibliography{ref}\`，随后执行 \`pdflatex \to bibtex8 \to pdflatex \to pdflatex\`。

## 3. 实际编译结果

在完整解压的原始源文件目录中，执行相同的临时构建流程：
- BibTeX 数据库成功读取 \`main_buildNotes.bib\` 和 \`ref.bib\`；
- 六个引用键均成功解析；
- 最终 PDF 为 5 页；
- 三次 LaTeX 构建均以退出码 0 完成。

最终版构建日志仍有非致命排版警告：
- 一处 float 无法在首次尝试位置放置；
- 两处轻微 overfull hbox；
- 一处 underfull hbox；
- 一个重复的 PDF destination（figure.4），来自原稿重复图环境/标签设置；
- hyperref 对若干数学标题书签给出 token 警告。

这些是原稿排版问题，不影响本轮源码完整性核验，但正式投稿前应逐项处理。

## 4. 图像视觉核查

对七张原始 PDF 与 Ghostscript \`/prepress\` 重封装的候选压缩版本，按 180 dpi 栅格化后逐像素比较。五张较复杂的图，超过 8 灰阶级差异阈值的像素占比为 0.094%–0.245%；两张简单 Feynman 图的渲染结果完全一致。

本轮只完成本地压缩候选版本的视觉比较。这些压缩候选版尚未提交到 GitHub；分支中提交的是原 ZIP 的原始图文件，不能把压缩候选版误称为已上传资源。

## 5. 构建依赖

`paper-source/build.sh` 在 TeX Live 2026（pdfTeX 1.40.29）上验证通过。除常见宏包外，还需额外安装以下包（缺任意一个都会在构建中途停在 `File '…' not found`）：

- `revtex`：提供 `revtex4-2.cls`；
- `bibtex8`：`build.sh` 用它跑 `.aux`；
- `textcase`、`cases`：`main_original.tex` 显式 `\usepackage{cases}`，`textcase` 为 RevTeX 依赖；
- `bbm-macros`：提供 `bbm.sty`。只装 `bbm` 只有 Metafont 字体，仍会报 `File 'bbm.sty' not found`；
- `jknapltx`：提供 `mathrsfs.sty`；
- `subfigure`、`orcidlink`、`comment`、`epstopdf-pkg`、`float`；
- `tools`（`dcolumn`、`array`、`verbatim`）、`graphics`（`epsfig`、`color`）。

依赖装齐后脚本退出码为 0，产出 `main_build.pdf`：5 页、359,966 bytes、7 个矢量 Form XObject、0 个位图，即七张 figure PDF 以矢量形式内嵌、未被栅格化。

## 6. "构建成功"不等于"字节可复现"

- PDF 内嵌的 `/CreationDate`、`/ModDate`、`/ID` 每次运行都会变化，逐字节比较前须先剔除这三个字段；
- 任何线性化/重封装步骤都会重写文件结构并改变版本行：pdfTeX 直接输出 `%PDF-1.7` 且不做线性化；`qpdf --linearize`、Ghostscript `-dFastWebView`（配 `-dCompatibilityLevel=1.5` 等）之类工具会产出 `%PDF-1.5` 并带 `/Linearized` 标记，对象数与 xref 形式也随之改变。

因此重新构建出的 PDF 只能保证页数、图形结构、版面与分发版本一致；若对外分发前做过上述后处理，应在分发说明中写明，否则"由本仓库源码构建"这一结论无法用哈希逐字节核对。

## 7. 论文状态

视觉检查确认五页 PDF 能正常排版并显示图形，但论文仍是未完成草稿：Introduction、relic abundance、constraints、conclusion 和 supplement 仍含占位文字，若干图注仍是通用描述。因此本轮不将 PR 标记为 ready for review，也不合并。
