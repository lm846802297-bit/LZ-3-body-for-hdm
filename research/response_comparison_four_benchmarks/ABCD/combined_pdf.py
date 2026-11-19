"""Create two A4 pages with vector plots and a self-contained legend on each page."""
from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D
from matplotlib.ticker import LogLocator
from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

from figures_abcd import BENCHMARKS, SPATIAL_COLOR, STYLES, configure_font, ratio_panel, spectrum_panel


WIDTH, HEIGHT = A4
LEFT, RIGHT = 33, WIDTH - 27
TABLE_TOP, ROW_TOP, ROW_HEIGHT = 474, 493, 30
TITLES = ("氙-131 三体散射的微分截面", "以 B 为基准的微分截面比值")
INK, MUTED = "#20313C", "#445661"

# Each entry matches a line on both pages. The last pair describes the ratio itself.
LEGEND = {
    "A": ("静态核子输入", r"$F_{1,2}^{V,N}(0)$", "取静态值并保留电荷反冲项",
          r"仅 $J^0$ 的相干密度 $W_M(y_A)$。", r"$S_A=K_{00}(c_M^A)^2 R_M(y_A)$",
          r"分子仅取 $W_M(y_A)$，与 B 共用电荷算符。", r"$S_A/S_B=(c_M^A/c_M^B)^2$"),
    "B": ("计算基准", r"$F_{1,2}^{V,N}(t_N)$", r"同位旋标量 $z$ 展开中心值",
          r"仅 $J^0$ 的 $W_M(y_A)$，用有限动量核子电荷系数。", r"$S_B=K_{00}(c_M^B)^2 R_M(y_A)$",
          r"分子、分母均为 B 的 $J^0$、$W_M(y_A)$ 截面。", r"开放区间内 $S_B/S_B=1$，也是插图中的水平参考线。"),
    "C": ("完整电荷", r"$F_{1,2}^{V,N}(t_N)$", "与 B 相同",
          r"仅 $J^0$，取 $W_M$、$W_{\Phi''}$ 及带符号的 $W_{M\Phi''}$。", r"$S_C=K_{00}R_{\rm ch}$",
          r"分子含 $W_M$、$W_{\Phi''}$ 和 $W_{M\Phi''}$ 的完整电荷。", r"$S_C/S_B=R_{\rm ch}/[(c_M^B)^2 R_M(y_A)]$"),
    "D": ("当前阶单体核流", r"$F_{1,2}^{V,N}(t_N)$", "与 B 相同",
          r"$S_D=P(L_C R_{\rm ch}+L_T R_T)$，纵向取 $J_L=(E_R/Q_A)J^0$。", r"横向含 $W_\Delta$、$W_{\Sigma'}$ 和带符号的 $W_{\Sigma'\Delta}$。",
          r"分子在 C 上加入纵向及横向 $\Delta,\Sigma',\Sigma'\Delta$ 项。", r"$S_D/S_B=(L_C R_{\rm ch}+L_T R_T)/[L_{00}(c_M^B)^2R_M]$"),
    "paper": ("当前论文领先阶", r"$c_M=1$", r"静态矢量电荷已计入 $g_{VN}$",
              r"仅 $J^0$ 的 $M$ 通道，用当前论文的 $y_6$ 保留整核有限尺寸。", r"$S_6=K_{00} R_M(y_6)$",
              r"分子按当前论文领先阶 取 $c_M=1$，只取 $J^0$ 的 $M$ 通道。", r"$S_6/S_B=W_M^{00}(y_6)/[(c_M^B)^2W_M^{00}(y_A)]$"),
}


def text_at(fig, x, top, value, size=8.6, color=INK, **options):
    fig.text(x / WIDTH, 1 - top / HEIGHT, value, va="top", fontsize=size, color=color, **options)


def page_background(canvas, page):
    """Lay out the printable document around the scientific artwork."""
    count = len(LEGEND) + page
    canvas.setFillColor(HexColor(INK))
    canvas.setFont("XeLegendBold", 20)
    canvas.drawString(LEFT, HEIGHT - 43, TITLES[page])
    canvas.setFont("XeLegend", 9)
    canvas.setFillColor(HexColor(MUTED))
    canvas.drawRightString(RIGHT, HEIGHT - 40, f"图 {page+1} / 2")
    canvas.setStrokeColor(HexColor("#AAB9C2"))
    canvas.setLineWidth(.5)
    canvas.line(LEFT, HEIGHT - 84, RIGHT, HEIGHT - 84)
    canvas.setFont("XeLegendBold", 12.4)
    canvas.setFillColor(HexColor(INK))
    canvas.drawString(LEFT, HEIGHT - 466, "曲线与计算方法" if page == 0 else "曲线、分子与分母")
    canvas.setFillColor(HexColor("#E9F0F3"))
    canvas.rect(LEFT - 3, HEIGHT - ROW_TOP, RIGHT - LEFT + 3, ROW_TOP - TABLE_TOP, fill=1, stroke=0)
    canvas.setFont("XeLegendBold", 9.1)
    canvas.setFillColor(HexColor(INK))
    for x, label in ((LEFT, "图例"), (147, "核子形状因子与电荷"), (293, "原子核响应与截面" if page == 0 else "同一反冲能处的截面比值")):
        canvas.drawString(x, HEIGHT - TABLE_TOP - 13, label)
    canvas.setFillColor(HexColor("#F1F6F9"))
    canvas.rect(LEFT - 3, HEIGHT - ROW_TOP - 2 * ROW_HEIGHT, RIGHT - LEFT + 3, ROW_HEIGHT, fill=1, stroke=0)
    canvas.setStrokeColor(HexColor("#CDD7DC"))
    canvas.setLineWidth(.38)
    for i in range(1, count + 1):
        y = HEIGHT - ROW_TOP - i * ROW_HEIGHT
        canvas.line(LEFT - 3, y, RIGHT, y)
    canvas.setFont("XeLegendBold", 11.3)
    canvas.setFillColor(HexColor(INK))
    canvas.drawString(LEFT, HEIGHT - ROW_TOP - count * ROW_HEIGHT - 19, "共同计算约定")
    canvas.showPage()


def legend_sample(fig, name, top):
    style = dict(color=SPATIAL_COLOR, linewidth=1.6) if name == "spatial" else dict(STYLES[name])
    if name == "B":
        style.update(marker="o", markerfacecolor="white", markeredgewidth=.95, markersize=4)
    style["linewidth"] *= .78
    if "markersize" in style:
        style["markersize"] *= .85
    y = 1 - top / HEIGHT
    sample = Line2D([LEFT / WIDTH, (LEFT+12) / WIDTH, (LEFT+24) / WIDTH], [y, y, y],
                    transform=fig.transFigure, markevery=[1], **style)
    fig.add_artist(sample)


def method_legend(fig, page):
    for i, (name, row) in enumerate(LEGEND.items()):
        title, form, convention, absolute, absolute_formula, ratio, ratio_formula = row
        top = ROW_TOP + i * ROW_HEIGHT + 4
        symbol = "6" if name == "paper" else name
        label = rf"$S_{{{symbol}}}/S_B$" if page else rf"$S_{{{symbol}}}$"
        legend_sample(fig, name, top+5)
        text_at(fig, LEFT + 30, top, label, size=9.2)
        text_at(fig, LEFT + 30, top+14, title, size=7.8)
        text_at(fig, 147, top, form, size=9.1)
        text_at(fig, 147, top+14, convention, size=8.0, color=MUTED)
        text_at(fig, 293, top, ratio if page else absolute)
        text_at(fig, 293, top+14, ratio_formula if page else absolute_formula, size=8.4)
    if page:
        top = ROW_TOP + len(LEGEND) * ROW_HEIGHT + 4
        legend_sample(fig, "spatial", top+5)
        text_at(fig, LEFT+30, top, "空间电流", size=8.8)
        text_at(fig, LEFT+30, top+14, "面板下方", size=7.8)
        text_at(fig, 147, top, r"$F_{1,2}^{V,N}(t_N)$", size=9.1)
        text_at(fig, 147, top+14, "分子 D 与分母 C 相同", size=8.0, color=MUTED)
        text_at(fig, 293, top, r"$10^6(S_D/S_C-1)$，单位为 ppm。")
        text_at(fig, 293, top+14, "相对于仅时间分量 C，给出加入空间电流后的修正。", size=8.3)


def scientific_page(data, manifest, page):
    fig = plt.figure(figsize=(WIDTH / 72, HEIGHT / 72))
    p = manifest["parameters"]
    mantissa, exponent = f"{p['coupling_product_squared']:e}".split("e")
    coefficient = "" if float(mantissa) == 1 else rf"{float(mantissa):g}\times "
    text_at(fig, LEFT, 52, rf"$^{{131}}\mathrm{{Xe}}$　固定入射速度 $v={p['v_km_s']:g}$ km/s　"
            rf"$m_A=131\,\mathrm{{u}}={p['mA_GeV']:.3f}$ GeV　"
            rf"$m_{{\chi_1}}={p['mchi_GeV']/1000:g}$ TeV　$m_V={p['mV_GeV']:g}$ GeV", size=9.3)
    text_at(fig, LEFT, 68, rf"质子与中子的矢量耦合相等　$g_p=g_n=g_{{VN}}=3g_{{Vq}}$　"
            rf"$g_2={p['g2']:g}$　$(g_1g_2g_{{VN}})^2={coefficient}10^{{{int(exponent)}}}$　Dirac 暗费米子、实标量辐射",
            size=9.0)
    grid = fig.add_gridspec(2, 2, left=60/WIDTH, right=1-25/WIDTH,
                            top=1-109/HEIGHT, bottom=1-408/HEIGHT, wspace=.32, hspace=.49)
    for i, name in enumerate(BENCHMARKS):
        group = data[data.benchmark.eq(name) & data.phase_space_open]
        cell = grid[i//2, i%2]
        if page == 0:
            main = fig.add_subplot(cell)
            spectrum_panel(main, i, group)
            main.yaxis.set_major_locator(LogLocator(base=10, numticks=6))
            axes = [main]
        else:
            main, strip = ratio_panel(fig, cell, i, group, zoom_bounds=(.115, .56, .32, .33))
            strip.yaxis.set_label_coords(-.115, .5)
            axes = [main, strip]
            if i == 0:
                inset = main.child_axes[0]
                inset.set_title("C/B 局部放大", loc="left", fontsize=6.5, pad=2)
                inset.tick_params(labelsize=5.8, length=1.7, pad=1)
        main.set_title(main.get_title(loc="left"), loc="left", fontsize=9.3, pad=4)
        for ax in axes:
            for line in ax.lines:
                line.set_linewidth(.78 * line.get_linewidth())
                line.set_markersize(.85 * line.get_markersize())
            ax.xaxis.label.set_size(8.4)
            ax.yaxis.label.set_size(7.5 if ax is not main else 8.4)
            ax.tick_params(labelsize=7.3, length=2.6, pad=2)
    note = (r"各面板给出 $(m_s,\Delta m)$。纵轴为微分截面 $S_X=(\mathrm{d}\sigma/\mathrm{d}E_R)_X$，采用对数刻度。"
            if page == 0 else r"主图将 $S_X=(\mathrm{d}\sigma/\mathrm{d}E_R)_X$ 逐点除以本组的 $S_B$。插图放大 263 至 275 keV 的 $S_C/S_B$，下方小图以 C 为分母。")
    text_at(fig, LEFT, 441, note, size=8.6)
    method_legend(fig, page)
    top = ROW_TOP + (len(LEGEND)+page) * ROW_HEIGHT + 25
    widths = "、".join(f"{manifest['widths_keV'][name]:.2f}" for name in BENCHMARKS)
    common = [
        r"核子　$f_i=F_i^{V,N}/3$，$F_1^{V,N}(0)=3$，$F_2^{V,N}(0)=-0.552$，$t_N\simeq -Q_A^2$。B、C、D 取有限动量中心值。",
        r"电荷　$c_\Phi=Q_A^2(f_1+2f_2)/(4m_N^2)$，$c_M=f_1-c_\Phi/2$，$m_N=0.938918$ GeV。A 用静态 $f_i$，B、C、D 用 $f_i(t_N)$。",
        r"整核　$Q_A^2=2m_AE_R+E_R^2$，$y_A=b_A^2 Q_A^2/4$，$y_6=b_A^2m_AE_R/2$，"
        rf"$b_A={manifest['numerical_checks']['b_A_GeV_inverse']:.4f}$ GeV$^{{-1}}$。使用 AFH v6 等标量响应。",
        r"响应　$R_M(y)=131^2 W_M^{00}(y)/W_M^{00}(0)$，$R_{\rm ch}=c_M^2R_M+2c_Mc_\Phi R_{M\Phi''}+c_\Phi^2R_{\Phi''}$。上标 $00$ 为同位旋指标。",
        r"横向　$R_T=(Q_A^2/m_N^2)[f_1^2 R_\Delta/2+(f_1+f_2)^2 R_{\Sigma'}/8-f_1(f_1+f_2)R_{\Sigma'\Delta}/2]$。",
        r"张量　$K_{00}=P L_{00}$，$r=E_R/Q_A$，$L_C=L_{00}-2r\,\mathrm{Re}\,L_{0L}+r^2 L_{LL}$，$L_T=L_{11}+L_{22}$。$P$ 含耦合和传播子，$L$ 已积分三体相空间。",
        r"宽度　两张辐射图相干相加，前发射传播子取零宽度，后发射取极点宽度。面板 (a) 至 (d) 的 $\Gamma_{\chi_2}$ 依次为 " + widths + " keV。",
        "质量　原始图 2 后两组标量质量标为 MeV，本图按四组数值归档采用 360 keV 和 300 keV。",
        r"范围　D 为当前阶单体矢量核流，$W_{\Sigma''}$ 与 $W_{\widetilde{\Phi}'}$ 的系数为零。束缚核振幅与干涉相位的独立匹配仍待完成。",
    ]
    for i, line in enumerate(common):
        text_at(fig, LEFT, top + 13.5*i, line, size=8.05, color=MUTED)
    return fig


def write_combined_pdf(data, manifest, destination: Path):
    configure_font()
    family = plt.rcParams["font.family"][0]
    for alias, weight in (("XeLegend", "normal"), ("XeLegendBold", "bold")):
        font_path = font_manager.findfont(font_manager.FontProperties(family=family, weight=weight))
        pdfmetrics.registerFont(TTFont(alias, font_path, subfontIndex=0))
    document, artwork = BytesIO(), BytesIO()
    canvas = Canvas(document, pagesize=A4, pageCompression=1, invariant=1)
    with PdfPages(artwork) as charts:
        for page in range(2):
            page_background(canvas, page)
            fig = scientific_page(data, manifest, page)
            try:
                charts.savefig(fig, facecolor="none", transparent=False)
            finally:
                plt.close(fig)
    canvas.save()
    document.seek(0)
    artwork.seek(0)
    writer = PdfWriter()
    writer.append(PdfReader(document))
    overlays = PdfReader(artwork)
    for i, base in enumerate(writer.pages):
        base.merge_page(overlays.pages[i])
        writer.add_outline_item(TITLES[i], i)
    writer.add_metadata({"/Title": "氙-131 三体散射的微分截面与比值",
                         "/Subject": "四组基准参数和逐曲线计算图例"})
    destination.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=destination.parent, suffix=".tmp", delete=False) as temporary:
        temp_path = Path(temporary.name)
    try:
        writer.write(temp_path)
        temp_path.replace(destination)
    finally:
        temp_path.unlink(missing_ok=True)
