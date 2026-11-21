"""Plot the absolute event densities, window counts and digitized manuscript reference spectra."""
import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter, LogFormatterMathtext
import numpy as np
import pandas as pd
import pymupdf

import event_spectra as spectra
from plot_event_counts import GRID, INK, MUTED, read_counts, setup

OUT = spectra.OUT
PDF = OUT.parent / "pdf" / "xenon_count_spectra_vs_recoil.pdf"
PARAMETERS = (r"$m_{\chi_1}=1$ TeV，$m_{A'}=5$ GeV，$m_s=300$ keV，$\Delta m=10$ MeV"
              r"       $g_1=0.1$，$g_2=1.725$，$g_{VN}=0.04857$")
METHODS = ("M_paper","A_time","B_time","C_time","D")
STYLES = {
    "paper": dict(color="#b73d4d",ls="-",lw=2.45,zorder=4),
    "M_paper": dict(color="#58656c",ls=":",lw=1.5,marker="D",ms=3.3,
                    mfc="white",mew=.9,zorder=6),
    "A_time": dict(color="#806698",ls="-.",lw=1.6,zorder=4),
    "B_time": dict(color="#bf6d1a",ls=(0,(5.8,3.6)),lw=1.65,zorder=5),
    "C_time": dict(color="#377eae",ls="none",marker="o",ms=4.1,
                   mfc="white",mew=1.1,zorder=7),
    "D": dict(color="#007369",ls="-",lw=2.15,zorder=3),
}
WINDOWS = (("lower","低能窗",100.,200.), ("candidate","候选窗",215.5,280.5))
WINDOW_COLORS = ("#dfefe9","#fae7c8")
BENCHMARKS = ("red","green","black","blue")
NAMES = ("manuscript_event_spectrum","manuscript_window_count_curves","four_benchmark_event_spectra")


def frame(title, subtitle):
    fig = plt.figure(figsize=(14.4,9.15),facecolor="white")
    fig.text(.052,.925,title,fontsize=24,weight="bold")
    fig.text(.054,.872,subtitle,fontsize=12,color=MUTED)
    rule(fig,.848)
    return fig


def rule(fig,y):
    fig.add_artist(Line2D([.052,.957],[y,y],transform=fig.transFigure,color=GRID,lw=1))


def footer(fig, first, second):
    rule(fig,.086)
    fig.text(.054,.053,first,fontsize=9.6)
    fig.text(.054,.025,second,fontsize=9.1,color=MUTED)


def axis_style(ax):
    ax.spines[["top","right"]].set_visible(False)
    ax.spines[["bottom","left"]].set_color("#becacd")
    ax.set_axisbelow(True)
    ax.grid(axis="y",color=GRID,lw=.65)
    ax.tick_params(labelsize=9.4,length=3.4,width=.65,pad=4)


def window_bands(ax):
    for (_,_,lo,hi),color in zip(WINDOWS,WINDOW_COLORS):
        ax.axvspan(lo,hi,color=color,lw=0,zorder=0)


def plot_line(ax,x,y,key):
    kw = STYLES[key].copy()
    if "marker" in kw:
        kw["markevery"] = (.02,.103) if key=="C_time" else (.052,.155)
    ax.plot(x,y,**kw)


def plot_densities(ax,curve,reference,log=False):
    for key in METHODS:
        y = curve[key+"_events_per_keV"].to_numpy()
        plot_line(ax,curve.ER_keV,np.where(y>0,y,np.nan) if log else y,key)
    plot_line(ax,reference.ER_keV,reference.paper_events_per_keV,"paper")


def method_key(fig,y=.818,archived=False):
    labels = ["附件原图（各面板对应曲线）" if archived else "论文原图红线",
              "静态电荷重算","A  静态核子形状因子","B  有限动量基准","C  仅时间分量","D  六通道候选"]
    handles = [Line2D([],[],**STYLES[key]) for key in ("paper",*METHODS)]
    fig.legend(handles,labels,ncol=6,loc="center",bbox_to_anchor=(.51,y),frameon=False,
               columnspacing=1.45,handlelength=2.6,handletextpad=.48,fontsize=9.8)


def detailed_key(fig):
    fig.text(.700,.802,"图线与核流处方",weight="bold",fontsize=14.5)
    rows = (
        ("paper","论文红线  ·  原图读数","新版正文谱图中三体辐射的红色实线。\n按原图纵轴读取，保留绝对高度。"),
        ("M_paper","静态电荷  ·  按论文补充材料重算",
         r"$L_{00}\,W_M^{00}(y_p)$，$c_M=1$。"+"\n"+r"$y_p=b_A^2m_A E_R/2$。"),
        ("A_time","A  ·  静态核子形状因子",
         r"$F_{1,2}^{V,N}(0)$ 进入电荷系数，保留反冲项，"+"\n"+r"时间分量仅取 $W_M^{00}(y_A)$。"),
        ("B_time","B  ·  本次计算基准",
         r"采用有限 $t_N$ 的核子形状因子 $F_{1,2}^{V,N}(t_N)$，"+"\n"+r"时间分量仅取 $W_M^{00}(y_A)$。"),
        ("C_time","C  ·  仅取时间分量",
         r"在 B 的电荷响应中加入 $W_{\Phi''}$"+"\n"+r"及带符号的 $W_{M\Phi''}$ 干涉。"),
        ("D","D  ·  六通道单体核流候选",
         r"保留 C 的电荷响应并计入纵向流，另含"+"\n"+r"$W_\Delta,\ W_{\Sigma'},\ W_{\Sigma'\Delta}$，保留干涉符号。"),
    )
    for i,(key,title,detail) in enumerate(rows):
        y = .753-.095*i
        fig.add_artist(Line2D([.700,.717,.734],[y+.005]*3,transform=fig.transFigure,
                              markevery=[1],**STYLES[key]))
        fig.text(.744,y,title,fontsize=11.1,weight="bold",color=STYLES[key]["color"])
        fig.text(.744,y-.022,detail,fontsize=9.55,linespacing=1.38,va="top")
    fig.text(.701,.198,r"B–D 取 $\hat F_1=1+(8.392\,{\rm GeV}^{-2})\,t_N/3$，$\hat F_2=-0.184$。",fontsize=9.4,color=MUTED)
    fig.text(.701,.170,r"$\hat F_i=F_i^{uds,N}/3$，$t_N=-2m_AE_R$，$y_A=b_A^2(2m_AE_R+E_R^2)/4$。",fontsize=9.4,color=MUTED)
    fig.text(.701,.142,r"$F_{1,2}^{V,N}$ 描述核子结构，$W_X^{00}$ 描述原子核多体响应。",fontsize=9.4,color=MUTED)


def full_spectrum(curve,red,upper,displayed):
    fig = frame("新版论文基准下的天然氙三体信号谱",PARAMETERS)
    grid = fig.add_gridspec(3,1,left=.080,right=.659,top=.805,bottom=.148,
                            height_ratios=[3.25,1.14,1.14],hspace=.18)
    ax = fig.add_subplot(grid[0])
    ref = fig.add_subplot(grid[1],sharex=ax)
    corr = fig.add_subplot(grid[2],sharex=ax)
    for panel in (ax,ref,corr):
        axis_style(panel)
        window_bands(panel)
        panel.set_xlim(75,800)
    ax.set_yscale("log")
    ax.set_ylim(1e-12,.45)
    ax.set_yticks(10.**np.arange(-11,0,2))
    plot_densities(ax,curve,red,log=True)
    ax.set_ylabel(r"$dN/dE_R$  [例/keV]",fontsize=12)
    ax.axvline(upper,color="#87979b",ls=(0,(2,3)),lw=.8)
    ax.text(upper-5,.945,f"重算的运动学上限 {upper:.1f} keV",
            transform=ax.get_xaxis_transform(),ha="right",va="top",fontsize=9,color=MUTED)
    for (_,label,lo,hi) in WINDOWS:
        ax.text((hi+lo)/2,1.012,label,transform=ax.get_xaxis_transform(),
                ha="center",va="bottom",fontsize=9.3,color=INK)
    s = curve[curve.ER_keV.between(red.ER_keV.min(),red.ER_keV.max())]
    red_at_e = np.exp(np.interp(s.ER_keV,red.ER_keV,np.log(red.paper_events_per_keV)))
    for key in ("M_paper","D"):
        plot_line(ref,s.ER_keV,s[key+"_events_per_keV"]/red_at_e,key)
    ref.set_ylim(-.012,.28)
    ref.set_yticks([0,.1,.2])
    ref.set_ylabel("重算谱 /\n论文红线",fontsize=10.3)
    positive = curve[curve.B_time_events_per_keV>0]
    for key in ("C_time","D"):
        corr_y = 100*(positive[key+"_events_per_keV"]/positive.B_time_events_per_keV-1)
        plot_line(corr,positive.ER_keV,corr_y,key)
    corr.axhline(0,color="#89989e",lw=.7,zorder=1)
    corr.set_ylim(-2.7,2.7)
    corr.set_yticks([-2,0,2])
    corr.set_ylabel("相对 B 的\n谱修正 [%]",fontsize=10.3)
    ax.tick_params(labelbottom=False)
    ref.tick_params(labelbottom=False)
    corr.set_xticks(np.arange(100,801,100))
    corr.set_xlabel(r"真实核反冲能 $E_R$  [keV]",fontsize=11)
    detailed_key(fig)
    fig.text(.701,.111,f"原图可见段 {displayed.ER_min_keV:.0f}–{displayed.ER_max_keV:.0f} keV    "
             f"论文 {displayed.paper_red_curve_events:.2f} 例    D {displayed.D:.3f} 例",
             fontsize=9.6,weight="bold")
    footer(fig,"曝光 2.84 吨·年，效率取 1。两幅辐射图先相干相加并取模平方，再逐核做三体相空间和晕速度积分，按七种氙同位素的天然原子丰度加权（合计 99.8158%）。",
           r"重算使用项目的截断标准晕，$(v_0,v_E,v_{\rm esc})=(220,232,544)$ km/s，$v_{\max}=776$ km/s，$\rho_\chi=0.3$ GeV/cm$^3$。新版稿未给出原图采用的整套晕参数。")
    return fig


def window_counts(curve,red,table,paper):
    fig = frame("两个真反冲能窗中的累计事例数",PARAMETERS)
    method_key(fig)
    grid = fig.add_gridspec(2,2,left=.085,right=.956,bottom=.204,top=.729,
                            height_ratios=[1,1.12],wspace=.25,hspace=.44)
    for i,(name,title,lo,hi) in enumerate(WINDOWS):
        upper = fig.add_subplot(grid[0,i])
        lower = fig.add_subplot(grid[1,i],sharex=upper)
        for panel in (upper,lower):
            axis_style(panel)
            panel.set_xlim(lo,hi)
        g = curve[curve.ER_keV.between(lo,hi)]
        x = g.ER_keV.to_numpy()
        red_x = np.unique(np.r_[lo,red.loc[red.ER_keV.between(lo,hi),"ER_keV"],hi])
        red_y = np.exp(np.interp(red_x,red.ER_keV,np.log(red.paper_events_per_keV)))
        ref = pd.DataFrame({"ER_keV":red_x,"paper_events_per_keV":red_y})
        plot_densities(upper,g,ref)
        upper.set_title(f"{title}    {lo:g}–{hi:g} keV",loc="left",fontsize=14,weight="bold",pad=10)
        upper.set_ylim(0,red_y.max()*1.15)
        upper.set_ylabel(r"$dN/dE_R$  [例/keV]")
        upper.tick_params(labelbottom=False)
        red_n = spectra.red_integral(red,x)-spectra.red_integral(red,lo)
        plot_line(lower,x,red_n,"paper")
        for key in METHODS:
            n = g[key+"_events_below_ER"].to_numpy()
            plot_line(lower,x,n-n[0],key)
        lower.set_ylim(0,red_n[-1]*1.13)
        lower.set_ylabel(r"$N([E_{\min},E_R])$  [例]")
        lower.set_xlabel(r"能窗积分上限 $E_R$  [keV]",fontsize=11)
        ticks = [100,120,140,160,180,200] if i==0 else [215.5,230,245,260,275,280.5]
        lower.set_xticks(ticks)
        lower.xaxis.set_major_formatter(FuncFormatter(lambda value,_: f"{value:g}"))
        row = table.loc[(spectra.counts.FIGURE,name)]
        fig.text([.085,.573][i],.127,
                 f"整窗积分    论文 {paper.at[name,'paper_red_curve_events']:.3f} 例"
                 f"     B {row.B_time:.5f} 例     D {row.D:.5f} 例",fontsize=10.4,weight="bold")
        fig.text([.085,.573][i],.101,
                 f"D 相对 B  {row.D_vs_B_percent:+.3f}%      D 相对仅时间分量 C  {row.D_vs_C_ppm:+.2f} ppm",
                 fontsize=9.4,color=STYLES["D"]["color"])
    footer(fig,"下排从各窗左端的 0 例开始累加。横坐标取右端时，曲线高度就是整个能窗内的预期信号事例数。红线按原图对数纵轴分段积分。",
           r"七同位素、三体相空间、速度积分及各核流处方同第一页。曝光 2.84 吨·年，效率取 1。B、C、D 在这一纵轴尺度上接近，第一页下框单独显示相对 B 的修正。")
    return fig


def archived_benchmarks(curves,refs,checks):
    fig = frame("同一压缩包中四组基准的事例谱对照",
                r"共同重算约定    $m_{\chi_1}=1$ TeV，$m_V=10$ GeV，$g_2=1$，$(g_1g_2g_{VN})^2=10^{-8}$"
                "       曝光 2.84 吨·年，效率取 1")
    method_key(fig,archived=True)
    grid = fig.add_gridspec(2,2,left=.078,right=.956,top=.741,bottom=.176,wspace=.22,hspace=.47)
    for i,name in enumerate(BENCHMARKS):
        ax = fig.add_subplot(grid[i//2,i%2])
        axis_style(ax)
        window_bands(ax)
        g = curves[curves.benchmark==name]
        original = refs[refs.benchmark==name]
        row = checks.loc[name]
        ax.set_xlim(0,1000)
        ax.set_yscale("log")
        ymin = int(np.floor(np.log10(g.D_events_per_keV.max())))-7
        ymax = int(np.ceil(np.log10(original.paper_events_per_keV.max()*1.2)))
        ax.set_ylim(10.**ymin,10.**ymax)
        ax.set_yticks(10.**np.arange(ymax,ymin-1,-3))
        ax.yaxis.set_major_formatter(LogFormatterMathtext())
        for key in METHODS:
            y = g[key+"_events_per_keV"].to_numpy()
            plot_line(ax,g.ER_keV,np.where(y>0,y,np.nan),key)
        for _,segment in original.groupby("segment"):
            plot_line(ax,segment.ER_keV,segment.paper_events_per_keV,"paper")
        ax.set_title(rf"$m_s={row.ms_keV:g}$ keV，$\Delta m={row.delta_m_MeV:g}$ MeV",
                     loc="left",fontsize=13,weight="bold",pad=8)
        ax.set_ylabel(r"$dN/dE_R$  [例/keV]",fontsize=10.5)
        if i>=2:
            ax.set_xlabel(r"真实核反冲能 $E_R$  [keV]",fontsize=10.3)
        ax.text(.975,.90,f"候选窗积分（例）\n附图  {row.attachment_curve_events:.3g}\nD  {row.D_events:.3g}",
                ha="right",va="top",fontsize=8.5,linespacing=1.23,transform=ax.transAxes,color=MUTED,
                bbox=dict(facecolor="white",edgecolor="none",alpha=.88,pad=2.2))
    fig.text(.078,.115,"各面板纵轴为绝对事例谱，对数刻度范围随参数组调整。米黄色带为 215.5–280.5 keV 候选窗，浅绿色带为 100–200 keV 低能窗。",fontsize=9.6)
    footer(fig,"红线取自同一压缩包内的四组谱图。附图按每吨·年、每 keV 给出，已乘 2.84。附图标出耦合乘积，重算中介子质量与单独耦合取本页页首的项目约定，晕参数同第一页。",
           "附图后两组将标量质量标为 MeV，此处依项目参数表取 360 keV 和 300 keV。新版正文采用的 5 GeV 中介子谱见前两页。")
    return fig


def main():
    setup()
    curves = pd.read_csv(OUT/"recoil_event_spectra.csv")
    red = pd.read_csv(OUT/"manuscript_red_curve.csv")
    windows = pd.read_csv(OUT/"manuscript_window_comparison.csv").set_index("window")
    archive = pd.read_csv(OUT/"four_figure_reference_curves.csv")
    archive_counts = pd.read_csv(OUT/"four_figure_window_comparison.csv").set_index("benchmark")
    table,paper = read_counts()
    benchmark = spectra.counts.FIGURE
    curve = curves[curves.benchmark==benchmark]
    if set(curves.benchmark)!={benchmark,*BENCHMARKS} or not curve.ER_keV.is_monotonic_increasing:
        raise ValueError("incomplete benchmark coverage or unordered recoil grid")
    endpoints = pd.read_csv(spectra.counts.SUPPORT)
    upper = endpoints[endpoints.benchmark==spectra.counts.spectrum_benchmark(benchmark)].ER_high_keV.max()
    PDF.parent.mkdir(parents=True,exist_ok=True)
    with PdfPages(PDF,metadata={"Title":"天然氙的预期事例谱与能窗累计事例数","Creator":"Matplotlib"}) as pdf:
        for figure in (full_spectrum(curve,red,upper,windows.loc["displayed_red_interval"]),window_counts(curve,red,table,paper),
                       archived_benchmarks(curves,archive,archive_counts)):
            pdf.savefig(figure)
            plt.close(figure)
    with pymupdf.open(PDF) as doc:
        assert len(doc)==len(NAMES)
        for page,name in zip(doc,NAMES):
            page.get_pixmap(matrix=pymupdf.Matrix(1.85,1.85),alpha=False).save(OUT/(name+".png"))
    print(PDF)


if __name__=="__main__":
    main()
