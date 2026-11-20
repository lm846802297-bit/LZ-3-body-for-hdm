"""Two-page Chinese figure with per-curve definitions and numerical tables."""
import json

import matplotlib
matplotlib.use("Agg")
from matplotlib import font_manager, pyplot as plt, ticker
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
from scipy.integrate import simpson

from run_fold import BENCHMARKS, OUT, fixed

PDF = OUT/"pdf"/"xenon_halo_spectra_and_ratios.pdf"
TEAL, RUST, BLUE, GRAY, PURPLE = "#08665d", "#b34b22", "#24508a", "#666775", "#775087"
INK, MUTED, RULE = "#182c37", "#435966", "#d0dadd"
STYLE = {
    "D": dict(color=TEAL, lw=1.8),
    "B": dict(color=RUST, lw=1.45, ls=(0,(5.5,3))),
    "C": dict(color=BLUE, marker="o", markerfacecolor="white", markeredgewidth=.85, ms=3.6, ls="none"),
    "M0": dict(color=GRAY, lw=1.0, ls=(0,(1.2,2.1)), marker="D", ms=2.6, markerfacecolor="white"),
    "spatial": dict(color=PURPLE, lw=1.45),
}


def configure():
    for font in ("Microsoft YaHei","Noto Sans CJK SC","SimHei","Source Han Sans SC"):
        if any(f.name == font for f in font_manager.fontManager.ttflist):
            break
    else:
        raise RuntimeError("A Simplified Chinese font is needed for the figure")
    plt.rcParams.update({"font.family":font, "font.size":9, "mathtext.fontset":"stix",
                         "axes.unicode_minus":False, "pdf.fonttype":42, "axes.labelcolor":INK,
                         "xtick.color":MUTED, "ytick.color":MUTED, "axes.edgecolor":"#aebfc2"})


def page_base(page):
    fig = plt.figure(figsize=(14.6,9.25),facecolor="white")
    title = "天然氙的三体核反冲谱" if page==1 else "六通道修正相对于 B 基准的大小"
    subtitle = ("四组参数下的绝对微分率  ·  逐同位素三体截面经实验室系速度积分"
                if page==1 else "同一反冲能先对各同位素做速度积分并按丰度相加，再用两条总谱相除")
    fig.text(.057,.946,title,fontsize=22,fontweight="bold",color=INK,va="center")
    fig.text(.058,.899,subtitle,fontsize=10.7,color=MUTED)
    fig.text(.958,.947,f"{page} / 2",fontsize=12,color=MUTED,ha="right")
    fig.add_artist(Line2D([.057,.96],[.878,.878],transform=fig.transFigure,color=RULE,lw=.85))
    fig.add_artist(Line2D([.733,.733],[.102,.850],transform=fig.transFigure,color=RULE,lw=.75))
    fig.add_artist(Line2D([.057,.96],[.068,.068],transform=fig.transFigure,color=RULE,lw=.75))
    fig.text(.057,.033,"AFH v6.0 原生默认密度  ·  AME2020 核质量  ·  七同位素占天然氙原子数的 99.8158%，使用原始丰度权重。",fontsize=8.8,color=MUTED)
    fig.text(.96,.033,"理论反冲率，折叠前的真实反冲能",ha="right",fontsize=8.8,color=MUTED)
    return fig


def legend(fig, page):
    x = .752
    def txt(y,s,**kw):
        fig.text(x,y,s,ha="left",va="top",color=kw.pop("color",INK),**kw)
    def entry(y, style, title, desc):
        points = [x, x+.014, x+.028]
        fig.add_artist(Line2D(points,[y-.007]*3,transform=fig.transFigure,**STYLE[style]))
        fig.text(x+.037,y,title,ha="left",va="top",fontsize=9.6,fontweight="bold",color=INK)
        txt(y-.029, desc, fontsize=8.5,linespacing=1.5,color=MUTED)
    txt(.848,"图例与计算约定",fontsize=13.3,fontweight="bold")
    if page==1:
        entry(.797,"M0","静态相干电荷对照",r"$c_M=1$，仅 $L_{00}W_M$，保留核有限尺寸。"
              "\n两张辐射图先相加，三体积分与 B 相同。")
        entry(.704,"B","B  ·  本文比值分母",r"核子形状因子取有限 $t_N$ 值，仅以时间分量"
              "\n"+r"$L_{00}$ 收缩 $c_M^2 W_M$。")
        entry(.611,"C","C  ·  仅时间分量",r"同 B，加上 $W_{\Phi^{\prime\prime}}$ 和带符号的 $W_{M\Phi^{\prime\prime}}$。"
              "\n空心圆标出部分计算点。")
        entry(.518,"D","D  ·  六通道单体核流候选",r"三项电荷用 $L_C$，横向用 $L_T$ 收缩"
              "\n"+r"$W_\Delta, W_{\Sigma^{\prime}}, W_{\Sigma^{\prime}\Delta}$，保留干涉符号。")
    else:
        entry(.797,"B","B/B  ·  比值为一",r"各基准均以相同参数的 $L_{00}c_M^2 W_M$"
              "\n天然氙速度积分为分母。")
        entry(.704,"C","C/B  ·  电荷响应修正",r"仅用 $L_{00}$，在 B 上加入 $\Phi^{\prime\prime}$ 和"
              "\n"+r"带符号的 $M\Phi^{\prime\prime}$，空心圆为部分计算点。")
        entry(.611,"D","D/B  ·  六通道修正",r"包含核流纵向分量，以及横向的 $\Delta$、"
              "\n"+r"$\Sigma^{\prime}$ 和 $\Sigma^{\prime}\Delta$。")
        entry(.518,"spatial","各面板下方  ·  空间分量",r"$10^6(D/C-1)$。此处以 C 为分母，"
              "\n纵轴单位 ppm（百万分之一）。")
    fig.add_artist(Line2D([x,.959],[.426,.426],transform=fig.transFigure,color=RULE,lw=.8))
    txt(.407,"共同输入",fontsize=11.2,fontweight="bold")
    txt(.370,r"$m_{\chi_1}=1$ TeV，$m_V=10$ GeV，$g_2=1$" "\n"
        r"$(g_1 g_2 g_{VN})^2=10^{-8}$，$g_{VN}=3g_{Vq}$" "\n"
        r"$\widehat F_1=1+(8.392/3)\,t_N/{\rm GeV}^2$，$\widehat F_2=-0.184$" "\n"
        r"$t_N=-2m_AE_R$，$Q_A^2=2m_AE_R+E_R^2$" "\n"
        r"AFH 响应取 $y_A=(b_A Q_A/2)^2$" "\n"
        r"$\rho_\chi=0.3$ GeV/cm$^3$，截断 SHM" "\n"
        r"$(v_0,v_E,v_{\rm esc})=(220,232,544)$ km/s" "\n"
        r"$v_{\max}=776$ km/s，每个核各用其 $v_{\min,A}$。",fontsize=8.65,color=MUTED,linespacing=1.58)
    txt(.153,"D 使用当前阶的单体核流匹配。束缚核的独立\n振幅与相位验证仍待完成。",fontsize=8.5,color=MUTED,linespacing=1.4)


def format_axis(ax):
    ax.spines[["top","right"]].set_visible(False)
    ax.tick_params(axis="both",labelsize=8,pad=3)
    ax.grid(axis="y",color="#e3e9e9",lw=.6)
    ax.set_axisbelow(True)
    ax.xaxis.set_major_locator(ticker.MaxNLocator(6,steps=[1,2,2.5,5,10]))


def draw(total,bounds):
    PDF.parent.mkdir(exist_ok=True,parents=True)
    with PdfPages(PDF,metadata={"Title":"天然氙三体核反冲谱和六通道修正",
                                "Subject":"AFH 七同位素的三体截面与截断 SHM 速度积分"}) as pdf:
        for page in (1,2):
            fig=page_base(page)
            grid=fig.add_gridspec(2,2,left=.086,right=.706,bottom=.143,top=.812,
                                  hspace=.49 if page==2 else .43,wspace=.29)
            for i,(name,(ms,gap)) in enumerate(BENCHMARKS.items()):
                rows=total[(total.benchmark==name)&(total.B_time>0)]
                support=bounds[bounds.benchmark==name]
                lo,hi=support.ER_low_keV.min(),support.ER_high_keV.max()
                e=rows.ER_keV.to_numpy()
                selected=list(range(4,len(rows),max(5,len(rows)//17)))
                if page==1:
                    ax=fig.add_subplot(grid[i//2,i%2])
                    ax.semilogy(e,rows.M0_time,markevery=selected,**STYLE["M0"])
                    ax.plot(e,rows.D,**STYLE["D"])
                    ax.plot(e,rows.B_time,**STYLE["B"])
                    ax.plot(e[selected],rows.C_time.iloc[selected],**STYLE["C"])
                    ax.set_ylabel(r"$\mathrm{d}R/\mathrm{d}E_R$  [kg$^{-1}$ d$^{-1}$ keV$^{-1}$]",fontsize=8.8)
                    ax.yaxis.set_major_locator(ticker.LogLocator(base=10,numticks=7))
                    bottom=ax
                else:
                    sub=grid[i//2,i%2].subgridspec(2,1,height_ratios=[2.6,1],hspace=.15)
                    ax=fig.add_subplot(sub[0])
                    bottom=fig.add_subplot(sub[1],sharex=ax)
                    ax.plot(e,rows.D_over_B_time,**STYLE["D"])
                    ax.plot(e,np.ones(len(e)),**STYLE["B"])
                    ax.plot(e[selected],rows.C_over_B_time.iloc[selected],**STYLE["C"])
                    anchor=rows.loc[rows.ER_keV==267,"D_over_B_time"].iloc[0]
                    ax.scatter([267],[anchor],s=18,color=TEAL,zorder=5)
                    ax.set_title(f"267 keV · {anchor:.5f}",loc="right",fontsize=8,color=TEAL,pad=8)
                    ax.tick_params(labelbottom=False)
                    ax.set_ylabel("相对于 B 的比值",fontsize=8.8)
                    ax.yaxis.set_major_locator(ticker.MaxNLocator(4))
                    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.3f"))
                    bottom.plot(e,rows.D_over_C_time_minus1_ppm,**STYLE["spatial"])
                    bottom.set_ylabel("ppm",fontsize=8.5,color=PURPLE)
                    bottom.yaxis.set_major_locator(ticker.MaxNLocator(3,integer=True))
                    format_axis(bottom)
                title=rf"$m_s={int(ms)}$ keV"+r"    "+rf"$\Delta m={int(gap)}$ MeV"
                ax.set_title(title,loc="left",fontsize=12,pad=8,color=INK)
                format_axis(ax)
                ax.set_xlim(lo-.018*(hi-lo),hi+.018*(hi-lo))
                bottom.set_xlabel(r"核反冲能 $E_R$  [keV]",fontsize=9)
            legend(fig,page)
            pdf.savefig(fig)
            plt.close(fig)


def summary(total,bounds):
    rows=[]
    for name,(ms,gap) in BENCHMARKS.items():
        g=total[total.benchmark==name]
        anchor=g[g.ER_keV==267].iloc[0]
        co=g[g.ER_keV%4==0]
        integrated={k:simpson(g[k],x=g.ER_keV) for k in ["B_time","C_time","D"]}
        support=bounds[bounds.benchmark==name]
        rows.append(dict(benchmark=name,ms_keV=ms,delta_m_MeV=gap,
                         recoil_low_keV=support.ER_low_keV.min(),recoil_high_keV=support.ER_high_keV.max(),
                         B_267=anchor.B_time,C_267=anchor.C_time,D_267=anchor.D,
                         D_over_B_267=anchor.D_over_B_time,D_over_C_minus1_ppm_267=anchor.D_over_C_time_minus1_ppm,
                         D_over_B_Coul_267=anchor.D_over_B_Coul,D_over_B_zexp_267=anchor.D_over_B_time_zexp,
                         **{k+"_integrated_kg_day":v for k,v in integrated.items()},
                         integrated_D_over_B=integrated["D"]/integrated["B_time"],
                         D_coarse_4keV_over_fine_minus1=simpson(co.D,x=co.ER_keV)/integrated["D"]-1))
    pd.DataFrame(rows).to_csv(OUT/"benchmark_summary.csv",index=False)


if __name__=="__main__":
    configure()
    total=pd.read_csv(OUT/"halo_spectra.csv")
    bounds=pd.read_csv(OUT/"kinematic_endpoints.csv")
    draw(total,bounds)
    summary(total,bounds)
    audit_path=OUT/"validation.json"
    audit=json.loads(audit_path.read_text(encoding="utf-8"))
    audit["figure_outputs_sha256"]={p.relative_to(OUT).as_posix():fixed.hash_file(p)
                                    for p in [PDF,OUT/"benchmark_summary.csv"]}
    audit_path.write_text(json.dumps(audit,indent=2,allow_nan=False),encoding="utf-8")
