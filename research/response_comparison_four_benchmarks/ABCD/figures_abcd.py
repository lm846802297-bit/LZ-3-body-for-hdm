"""Draw the A–D spectra and B-normalized comparisons with a spatial-current scale."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.ticker import AutoMinorLocator, LogLocator, MaxNLocator
import numpy as np


LABELS = {
    "A": r"A　$F_{1,2}(0),\,W_M$",
    "B": r"B 基准　$F_{1,2}(t_N),\,W_M$",
    "C": r"C　完整电荷 $J^0$",
    "D": r"D　单体核流 $J^\mu$",
    "paper": "当前论文领先阶",
}
STYLES = {
    "A": dict(color="#885596", linewidth=2.1, linestyle=(0, (6, 3))),
    "B": dict(color="#174A79", linewidth=1.2, linestyle="-"),
    "C": dict(color="#C36419", linewidth=1.6, linestyle=(0, (4, 3.2))),
    "D": dict(color="#168374", linewidth=3.0, linestyle="-"),
    "paper": dict(color="#4F555E", linewidth=1.45, linestyle=(0, (1.1, 2.3)),
                  marker="D", markersize=4, markeredgewidth=.95, markerfacecolor="white"),
}
BENCHMARKS = ("red", "green", "black", "blue")
SPATIAL_COLOR = "#545A8D"
BACKGROUND = "#DCE1E6"


def configure_font():
    available = {f.name for f in font_manager.fontManager.ttflist}
    fonts = ("Microsoft YaHei", "Noto Sans CJK SC", "Source Han Sans SC", "SimHei", "PingFang SC")
    cjk = next((f for f in fonts if f in available), None)
    if cjk is None:
        raise RuntimeError("Chinese plot labels require a CJK font such as Noto Sans CJK SC.")
    plt.rcParams.update({
        "font.family": [cjk, "DejaVu Sans"], "mathtext.fontset": "dejavusans",
        "font.size": 10.5, "axes.titlesize": 12, "axes.labelsize": 10.5,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.linewidth": .85, "axes.edgecolor": "#435260",
        "xtick.direction": "out", "ytick.direction": "out", "xtick.color": "#384653",
        "ytick.color": "#384653", "axes.labelcolor": "#24303B",
        "savefig.facecolor": "white", "pdf.fonttype": 42, "ps.fonttype": 42,
        "svg.hashsalt": "abcd-xe131-b-reference",
    })


def add_header(fig, title, *, ratios=False):
    fig.text(.085, .974, title, fontsize=18, weight="bold", ha="left", va="top", color="#23323D")
    fig.text(.085, .933,
             r"$^{131}\mathrm{Xe}$　·　$m_{\chi_1}=1$ TeV　·　$m_V=10$ GeV　·　$v=800$ km/s　·　"
             r"$(g_1g_2g_{VN})^2=10^{-8}$　·　$g_2=1$", fontsize=10.2, color="#475665", va="top")
    handles = []
    for name in ("A", "B", "C", "D"):
        label = LABELS[name]
        if ratios:
            label = {"A": r"A/B　静态 $F_{1,2}(0)$", "B": "B/B = 1　基准",
                     "C": r"C/B　完整电荷 $J^0$", "D": r"D/B　单体核流 $J^\mu$"}[name]
        symbols = dict(marker="o", markerfacecolor="white", markersize=4, markeredgewidth=1.1) if name == "B" else {}
        handles.append(Line2D([], [], label=label, **STYLES[name], **symbols))
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(.08, .901), ncol=4,
               frameon=False, columnspacing=2.25, handlelength=2.65, handletextpad=.55,
               borderaxespad=0, fontsize=10)

    if ratios:
        reference = (LABELS["paper"] + r" / B　　 $S_6/S_B=W_M^{00}(y_6)\,/\,[(c_M^B)^2 W_M^{00}(y_A)]$"
                     r"　　 分子取 $c_M=1$，分母取 B 的核子电荷系数 $c_M^B$。")
        detail = (r"$y_6=b_A^2m_A E_R/2$，$y_A=b_A^2(2m_A E_R+E_R^2)/4$。"
                  r"分子和分母均保留原子核有限尺寸，$c_M^B$ 由核子 $F_{1,2}^{V,N}(t_N)$ 决定。")
    else:
        reference = (LABELS["paper"] + r"　　 $S_6=K_{00}\,131^2\, W_M^{00}(y_6)/W_M^{00}(0)$"
                     r"　　 只取时间分量 $J^0$ 的相干电荷，核子电荷系数 $c_M=1$。")
        detail = (r"$y_6=b_A^2m_A E_R/2$。$W_M^{00}$ 保留原子核有限尺寸，上标 $00$ 为同位旋指标。"
                  r"$K_{00}$ 含耦合、传播子和暗电流时间分量的三体相空间积分。")
    fig.legend(handles=[Line2D([], [], label=reference, **STYLES["paper"])],
               loc="upper left", bbox_to_anchor=(.08, .861), frameon=False, handlelength=2.65,
               handletextpad=.55, borderaxespad=0, fontsize=10)
    fig.text(.123, .821, detail, fontsize=9.2, color="#394954", va="top")


def panel_header(ax, i, rows):
    benchmark = rows.iloc[0]
    txt = (f"({chr(97+i)})   " +
           rf"$m_s={benchmark.ms_keV:g}$ keV,   $\Delta m={benchmark.delta_m_MeV:g}$ MeV")
    ax.set_title(txt, loc="left", pad=7, fontsize=11.2, color="#263642")


def format_x(ax, *, label=True):
    ax.set_xlim(0, 1010)
    ax.set_xticks(np.arange(0, 1001, 200))
    ax.xaxis.set_minor_locator(AutoMinorLocator(2))
    ax.tick_params(which="major", labelsize=9, length=3.5)
    if label:
        ax.set_xlabel(r"反冲能 $E_R$ [keV]")
    else:
        ax.tick_params(labelbottom=False)


def plot_versions(ax, rows, *, ratios=False):
    x = rows.ER_keV.to_numpy()
    suffix = "_over_B" if ratios else "_cm2_per_keV"
    # C/D overlap to a few ppm. Use a broad D and a narrower dashed C; put
    # open B markers on top so all three remain identifiable on a log scale.
    paper_markers = np.searchsorted(x, x[0] + (x[-1] - x[0]) * np.linspace(.10, .90, 6))
    for zorder, name in enumerate(("B", "D", "C", "A", "paper"), start=2):
        ax.plot(x, rows[name+suffix], zorder=zorder, **STYLES[name],
                markevery=paper_markers if name == "paper" else None)
    samples = np.linspace(.055, .945, 11)
    indices = np.searchsorted(x, x[0] + (x[-1] - x[0]) * samples)
    ax.plot(x[indices], rows["B"+suffix].to_numpy()[indices], linestyle="none", marker="o",
            markerfacecolor="white", markeredgecolor=STYLES["B"]["color"], markeredgewidth=.95,
            markersize=3.4, zorder=8)
    ax.grid(axis="y", which="major", color=BACKGROUND, linewidth=.65)
    ax.set_axisbelow(True)


def save(fig, dest):
    for extension in ("png", "pdf", "svg"):
        fig.savefig(dest.with_suffix("."+extension), dpi=190)
    plt.close(fig)


def charge_zoom(parent, data, bounds):
    ax = parent.inset_axes(bounds)
    small = data[data.ER_keV.between(263, 275)]
    ax.set_facecolor("#F7F9FA")
    ax.axhline(1, color=STYLES["B"]["color"], linewidth=.8)
    ax.plot(small.ER_keV, small.C_over_B, color=STYLES["C"]["color"], linewidth=1.5)
    ax.set_xlim(263, 275)
    ax.set_ylim(.82, 1.16)
    ax.set_xticks([264, 269, 274])
    ax.set_yticks([.9, 1., 1.1])
    ax.tick_params(labelsize=7, length=2, pad=1.5)
    ax.set_title("四组共有的 C/B 局部结构", fontsize=8, loc="left", pad=3)
    ax.grid(axis="y", color=BACKGROUND, linewidth=.5)


def spectrum_panel(ax, i, group):
    panel_header(ax, i, group)
    plot_versions(ax, group)
    ax.set_yscale("log")
    values = group[[f"{n}_cm2_per_keV" for n in LABELS]].to_numpy()
    ax.set_ylim(values.min() * .58, values.max() * 2.3)
    ax.yaxis.set_major_locator(LogLocator(base=10, numticks=7))
    ax.set_ylabel(r"$\mathrm{d}\sigma/\mathrm{d}E_R$ [cm$^2$/keV]")
    format_x(ax)


def ratio_panel(fig, cell, i, group, *, zoom_bounds=(.125, .48, .35, .37)):
    inner = cell.subgridspec(2, 1, height_ratios=[3.0, 1], hspace=.08)
    top = fig.add_subplot(inner[0])
    strip = fig.add_subplot(inner[1], sharex=top)
    panel_header(top, i, group)
    plot_versions(top, group, ratios=True)
    upper = max(group.A_over_B.max(), group.paper_over_B.max(), group.C_over_B.max())
    top.set_ylim(.78, upper + .075*(upper-.78))
    top.yaxis.set_major_locator(MaxNLocator(5))
    top.set_ylabel("微分截面 / B")
    format_x(top, label=False)
    if i == 0:
        charge_zoom(top, group, zoom_bounds)
    strip.set_facecolor("#F6F7FA")
    strip.plot(group.ER_keV, group.D_over_C_minus_1_ppm, color=SPATIAL_COLOR, linewidth=1.6)
    strip.set_ylim(-10.25, -1.25)
    strip.set_yticks([-9, -6, -3])
    strip.set_ylabel("D/C 偏移\n[ppm]", fontsize=8, color=SPATIAL_COLOR, labelpad=8)
    strip.grid(axis="y", color=BACKGROUND, linewidth=.55)
    format_x(strip)
    strip.tick_params(axis="y", labelsize=8)
    return top, strip


def draw_figures(data, out: Path):
    configure_font()
    groups = [data[(data.benchmark == name) & data.phase_space_open] for name in BENCHMARKS]
    fig, axes = plt.subplots(2, 2, figsize=(12.8, 9.75))
    fig.subplots_adjust(left=.085, right=.975, top=.744, bottom=.132, hspace=.38, wspace=.20)
    add_header(fig, "四组基准参数下的三体散射微分截面")
    for i, (ax, group) in enumerate(zip(axes.flat, groups)):
        spectrum_panel(ax, i, group)
    fig.text(.085, .047, r"当前论文将核子静态电荷计入 $g_{VN}$。A 保留用 $F_{1,2}(0)$ 计算的电荷反冲项，B 在同一算符中取 $F_{1,2}(t_N)$。",
             fontsize=9.0, color="#465563")
    fig.text(.085, .022, r"C 加入 $\Phi''$ 与 $M\Phi''$ 电荷响应，D 再加入纵向和横向空间电流。C 与 D 的差异见比值图。",
             fontsize=9.0, color="#465563")
    save(fig, out/"abcd_differential_cross_sections")

    fig = plt.figure(figsize=(12.8, 10.95))
    add_header(fig, "以 B 为基准的微分截面比值", ratios=True)
    outer = fig.add_gridspec(2, 2, left=.085, right=.975, top=.746, bottom=.12, hspace=.35, wspace=.20)
    for i, group in enumerate(groups):
        ratio_panel(fig, outer[i//2, i%2], i, group)
    fig.text(.085, .050, r"主图各点除以同一反冲能下的 B。紫色小图给出 $10^6[(\mathrm{d}\sigma/\mathrm{d}E_R)_D/(\mathrm{d}\sigma/\mathrm{d}E_R)_C-1]$，单位为 ppm。",
             fontsize=9.0, color="#465563")
    fig.text(.085, .026, "曲线仅覆盖各组开放的三体相空间。D 采用当前阶的单体核流，束缚核振幅的独立匹配仍待完成。",
             fontsize=9.0, color="#465563")
    save(fig, out/"abcd_ratios_to_B")
