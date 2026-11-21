"""Draw unit-efficiency expected counts and window-integrated changes from the verified tables."""
from pathlib import Path
import hashlib
import json

import matplotlib
matplotlib.use("Agg")
from matplotlib import font_manager, pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D
from matplotlib.ticker import NullLocator
import numpy as np
import pandas as pd
import pymupdf

HERE = Path(__file__).resolve().parent
OUT = HERE / "output"
PDF = OUT / "pdf" / "xenon_expected_counts.pdf"
INK, MUTED, GRID = "#1c3039", "#4e6570", "#dce4e6"
PALETTE = {"paper":"#ad4543","M0_time":"#65757d","A_time":"#806f95",
           "B_time":"#b46822","C_time":"#417aa0","D":"#087267"}
METHODS = list(PALETTE)
WINDOWS = [("candidate","候选窗","215.5–280.5 keV"),("lower","低能窗","100–200 keV"),
           ("all_recoils","全能区","全部运动学允许的反冲能")]
BENCHMARKS = ["red","green","black","blue"]


def setup():
    installed = {f.name for f in font_manager.fontManager.ttflist}
    font = next(f for f in ("Microsoft YaHei","Noto Sans CJK SC","SimHei") if f in installed)
    plt.rcParams.update({"font.family":font,"mathtext.fontset":"stix","pdf.fonttype":42,
                         "font.size":11,"text.color":INK,"axes.labelcolor":MUTED,
                         "xtick.color":MUTED,"ytick.color":INK,"axes.unicode_minus":False})


def read_counts():
    audit = json.loads((HERE/"count_validation.json").read_text(encoding="utf-8"))
    frames = []
    for name in ("event_counts.csv","manuscript_figure_comparison.csv"):
        path = HERE/name
        expected, = [v for k,v in audit["sha256"].items() if k.endswith("/"+name)]
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
            raise ValueError(f"count-table checksum mismatch: {name}")
        frames.append(pd.read_csv(path))
    table = frames[0].set_index(["benchmark","window"])
    original = frames[1].set_index("window")
    if not table.index.is_unique or len(table)!=15 or len(original)!=2 or set(original.index)!={"candidate","lower"}:
        raise ValueError("unexpected benchmark or manuscript window coverage")
    assert audit["exposure_kg_days"]==1037310 and audit["efficiency"]==1
    for w in original.index:
        np.testing.assert_allclose(table.loc[("manuscript_figure",w),"D"],original.loc[w,"current_D"])
    return table, original


def page(title,subtitle):
    fig = plt.figure(figsize=(15,9.2),facecolor="white")
    fig.text(.055,.922,title,fontsize=24,weight="bold")
    fig.text(.056,.870,subtitle,fontsize=12,color=MUTED)
    rule(fig,.842)
    return fig


def rule(fig,y):
    fig.add_artist(Line2D([.055,.96],[y,y],transform=fig.transFigure,color=GRID,lw=1))


def finish(fig):
    rule(fig,.075)
    fig.text(.055,.035,"2.84 吨·年曝光   ·   探测器效率 100%   ·   真实核反冲能，未做能量展宽",
             fontsize=10.5,color=INK)
    fig.text(.96,.035,"重算采用 AFH 七同位素（天然丰度 99.8158%）及截断速度分布，最高 776 km/s",
             fontsize=9.5,ha="right",color=MUTED)


def axes_style(ax):
    ax.spines[["top","right","left"]].set_visible(False)
    ax.spines["bottom"].set_color("#bac8ca")
    ax.set_axisbelow(True)
    ax.grid(axis="x",color=GRID,lw=.65)
    ax.tick_params(axis="y",length=0,pad=6,labelsize=10.5)
    ax.tick_params(axis="x",length=3,labelsize=9)


def manuscript(table,original):
    fig=page("新版论文基准的预期事例数",
        r"$m_\chi=1$ TeV，$m_V=5$ GeV，$m_s=300$ keV，$\Delta m=10$ MeV"
        r"     |     $g_1=0.1$，$g_2=1.725$，$g_{VN}=0.04857$")
    fig.text(.955,.801,"各窗单独设置横轴范围",ha="right",fontsize=9.2,color=MUTED)
    grid=fig.add_gridspec(1,3,left=.125,right=.955,bottom=.503,top=.753,wspace=.19)
    names=["论文红线",r"$M_0$","A","B","C","D"]
    for i,(w,title,energy) in enumerate(WINDOWS):
        ax=fig.add_subplot(grid[i]); axes_style(ax)
        row=table.loc[("manuscript_figure",w)]
        counts=[original.at[w,"paper_red_curve_events"] if w in original.index else np.nan,
                *[row[k] for k in METHODS[1:]]]
        ax.set_title(title+"   "+energy,loc="left",fontsize=12,weight="bold",pad=13)
        ax.set_xlim(0,[1.26,7.9,2.38][i])
        ax.set_xticks([[0,.25,.5,.75,1.],[0,2,4,6],[0,.5,1,1.5,2]][i])
        ax.set_ylim(5.65,-.65)
        ax.set_yticks(range(6),names if i==0 else [""]*6)
        ax.set_xlabel("期望事例数  [例]",fontsize=10)
        for y,(method,v) in enumerate(zip(METHODS,counts)):
            if pd.isna(v):
                ax.text(.03,y,"原图全能区未积分",transform=ax.get_yaxis_transform(),
                        color=MUTED,fontsize=9,va="center")
                continue
            ax.barh(y,v,height=.53,color=PALETTE[method],zorder=2)
            label=f"{v:.3f}" if method=="paper" else f"{v:.6f}"
            ax.annotate(label,(v,y),xytext=(4,0),textcoords="offset points",va="center",
                        fontsize=9,color=PALETTE[method] if method=="D" else INK,
                        weight="bold" if method=="D" else "normal")
        ax.text(0,-.35,rf"$D/B-1$   {row.D_vs_B_percent:+.3f}%"
                +rf"      $D/C-1$   {row.D_vs_C_ppm:+.2f} ppm",transform=ax.transAxes,
                fontsize=10,color=PALETTE["D"],weight="bold")
    rule(fig,.383)
    fig.text(.055,.335,"各计算方法",fontsize=13,weight="bold")
    entries=[
        ("paper","论文红线","直接积分原图中三体辐射的红色矢量曲线。"),
        ("M0_time",r"静态相干电荷  $M_0$",r"取 $c_M=1$，时间分量仅耦合有限尺寸 $W_M$。"),
        ("A_time","A   静态核子形状因子",r"取 $F_{1,2}(0)$，在 $M$ 电荷中保留核子反冲项。"),
        ("B_time","B   比值的基准",r"取 $F_{1,2}(t_N)$，$t_N=-2m_AE_R$，仅保留 $L_{00}c_M^2 W_M$。"),
        ("C_time","C   仅时间分量",r"在 B 上加入 $W_{\Phi^{\prime\prime}}$ 及带符号的 $W_{M\Phi^{\prime\prime}}$。"),
        ("D","D   六通道单体核流候选",r"补全纵向核流，加入 $\Delta$、$\Sigma^{\prime}$ 及 $\Sigma^{\prime}\Delta$ 三项。")]
    for j,(key,title,desc) in enumerate(entries):
        x=.055+(j%3)*.309; y=.280-(j//3)*.099
        fig.add_artist(Line2D([x,x+.017],[y+.008]*2,transform=fig.transFigure,color=PALETTE[key],lw=4))
        fig.text(x+.022,y,title,fontsize=10.8,weight="bold")
        fig.text(x,y-.041,desc,fontsize=9.6,color=MUTED)
    finish(fig)
    return fig


def compact_number(v):
    if v>=.001:
        return f"{v:.3g}"
    power=int(np.floor(np.log10(v)))
    return rf"${v/10.**power:.2f}\times10^{{{power}}}$"


def four_sets(table):
    fig=page("四组基准的事例数与六通道修正",
             r"$m_\chi=1$ TeV，$m_V=10$ GeV，$g_2=1$，$(g_1g_2g_{VN})^2=10^{-8}$"
             r"     |     B 为有限 $t_N$ 的 $M$ 电荷基准，D 为六通道单体核流候选。")
    left,right=.159,.955
    gs=fig.add_gridspec(2,3,left=left,right=right,top=.705,bottom=.165,wspace=.22,hspace=1.0)
    fig.text(.055,.790,"预期事例数",fontsize=15,weight="bold")
    fig.text(.055,.748,r"左侧参数行按 $(m_s$ [keV]，$\Delta m$ [MeV]$)$ 标识。点旁标出 D 的计数。",color=MUTED,fontsize=10.2)
    for x,method,marker in ((.735,"B_time","o"),(.845,"D","D")):
        fig.add_artist(Line2D([x],[.783],marker=marker,ls="none",ms=6,
                              markerfacecolor="white" if method=="B_time" else PALETTE[method],
                              color=PALETTE[method],transform=fig.transFigure))
        fig.text(x+.012,.776,"B   电荷基准" if method=="B_time" else "D   六通道",fontsize=10)
    fig.text(.055,.431,"六通道相对 B 的计数变化",fontsize=15,weight="bold")
    fig.text(.055,.390,r"$100\,(N_D/N_B-1)$，零线处两种计算给出相同计数。",fontsize=10.2,color=MUTED)
    for col,(window,title,energy) in enumerate(WINDOWS):
        group=table.xs(window,level="window").loc[BENCHMARKS]
        labels=[rf"$({int(r.ms_keV)},\ {int(r.delta_m_MeV)})$" for r in group.itertuples()]
        ax=fig.add_subplot(gs[0,col]); change=fig.add_subplot(gs[1,col])
        for panel in (ax,change):
            axes_style(panel)
            panel.set_ylim(3.6,-.65)
            panel.set_yticks(range(4),labels if col==0 else [""]*4)
        ax.set_title(title+"   "+energy,loc="left",fontsize=10.8,weight="bold",pad=7)
        change.set_title(title,loc="left",fontsize=10.0,weight="bold",pad=5)
        ax.set_xscale("log"); ax.set_xlim(1.1e-9,6.)
        ax.set_xticks([1e-8,1e-6,1e-4,1e-2,1])
        ax.xaxis.set_minor_locator(NullLocator())
        ax.set_xlabel("期望事例数  [例，对数刻度]",fontsize=9.5)
        change.set_xlim(-1.16,1.75); change.set_xticks([-.5,0,.5,1,1.5])
        change.axvline(0,color="#707f86",lw=1)
        change.set_xlabel("事例数变化  [%]",fontsize=9.5)
        for y,row in enumerate(group.itertuples()):
            if row.B_time==0:
                assert row.D==0 and pd.isna(row.D_vs_B_percent)
                ax.text(.025,y,"B = D = 0 例",transform=ax.get_yaxis_transform(),va="center",color=MUTED,fontsize=9.5)
                change.text(.04,y,"未定义（0/0）",va="center",color=MUTED,fontsize=9.3)
                continue
            ax.plot(row.B_time,y-.105,"o",ms=5,mfc="white",mec=PALETTE["B_time"],zorder=3)
            ax.plot(row.D,y+.105,"D",ms=4.6,color=PALETTE["D"],zorder=3)
            ax.annotate(compact_number(row.D),(row.D,y+.105),xytext=(6,0),
                        textcoords="offset points",va="center",fontsize=9)
            v=row.D_vs_B_percent
            change.barh(y,v,height=.45,color=PALETTE["D"])
            change.annotate(f"{v:+.3f}%",(v,y),xytext=(4 if v>0 else -4,0),textcoords="offset points",
                            ha="left" if v>0 else "right",va="center",fontsize=9,color=INK)
    finish(fig)
    return fig


def main():
    setup()
    counts, original=read_counts()
    PDF.parent.mkdir(parents=True,exist_ok=True)
    with PdfPages(PDF,metadata={"Title":"天然氙三体散射的预期事例数"}) as pdf:
        for fig in (manuscript(counts,original),four_sets(counts)):
            pdf.savefig(fig)
            plt.close(fig)
    with pymupdf.open(PDF) as doc:
        for page,name in zip(doc,("manuscript_counts","four_benchmark_counts"),strict=True):
            scale=1760/page.rect.width
            page.get_pixmap(matrix=pymupdf.Matrix(scale,scale),alpha=False).save(OUT/(name+".png"))


if __name__=="__main__":
    main()
