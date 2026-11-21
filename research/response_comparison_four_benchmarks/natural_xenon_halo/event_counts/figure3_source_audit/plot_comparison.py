"""Render the Fig. 3 spectrum comparison and its equal-area check from the audit outputs."""
import hashlib
import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import font_manager
import numpy as np
import pandas as pd
from scipy.special import exprel

HERE = Path(__file__).resolve().parent
OUT = HERE/"output"
RED, BLUE, GRAY, TEAL = "#b02e27", "#286793", "#4e4b51", "#07796b"


def configure():
    fonts={f.name for f in font_manager.fontManager.ttflist}
    font=next((f for f in ("Microsoft YaHei","Noto Sans CJK SC","SimHei","Source Han Sans SC") if f in fonts),None)
    if font is None:
        raise RuntimeError("Install a CJK font to render the Chinese figure captions")
    mpl.rcParams.update({"font.family":font,"font.size":10.5,"axes.spines.top":False,
                         "axes.spines.right":False,"axes.unicode_minus":False,"pdf.fonttype":42,
                         "axes.labelcolor":"#292b31","xtick.color":"#34363a","ytick.color":"#34363a",
                         "mathtext.fontset":"stix","svg.fonttype":"none"})


def layout(title, subtitle):
    fig,(ax,lower)=plt.subplots(2,1,figsize=(9.4,8.15),sharex=True,gridspec_kw={"height_ratios":[1.55,1]})
    fig.subplots_adjust(left=.115,right=.96,top=.85,bottom=.25,hspace=.13)
    fig.text(.112,.947,title,fontsize=19,weight="bold",va="top")
    fig.text(.114,.887,subtitle,fontsize=10,color="#41454b",va="top")
    for panel in (ax,lower):
        panel.set_xlim(80,805)
        panel.grid(axis="y",color="#d9dce0",lw=.65)
        panel.set_axisbelow(True)
    lower.set_xlabel(r"真核反冲能 $E_R$（keV）")
    return fig,ax,lower


def main():
    configure()
    (OUT/"pdf").mkdir(exist_ok=True)
    audit=json.loads((OUT/"audit.json").read_text(encoding="utf8"))
    points=pd.read_csv(OUT/"independent_absolute_points.csv")
    curves=pd.read_csv(OUT/"figure_vertices.csv").query("version=='supplied'")
    red,blue=(curves.query("curve==@k") for k in ("red","blue"))
    rates=pd.read_csv(HERE.parent/"output/recoil_curves/recoil_event_spectra.csv").query("benchmark=='manuscript_figure'")
    low,high=audit["endpoints"]["all_nine_union_keV"]
    with PdfPages(OUT/"pdf/figure3_audit.pdf",metadata={"Title":"新版论文图 3 的事例谱与归一化核查",
                                                        "CreationDate":None,"ModDate":None}) as pdf:
        fig,ax,ratio=layout("图 3 红线与独立重算的天然氙事例谱",
                           r"$m_{\chi_1}=1$ TeV，$m_s=300$ keV，$\Delta m=10$ MeV，$m_{A^\prime}=5$ GeV　｜　2.84 吨·年，效率取 1")
        hred,=ax.plot(red.ER_keV,red.value,color=RED,lw=2.2,label="新版图 3 红线")
        mask=rates.ER_keV.between(low,high)
        overlap=rates.ER_keV.between(red.ER_keV.min(),red.ER_keV.max())
        E=rates.ER_keV[overlap].to_numpy()
        ref=np.exp(np.interp(E,red.ER_keV,np.log(red.value)))
        handles=[hred]
        for key,col,style,label in [("M_paper",GRAY,"--","静态电荷重算"),("B_time",TEAL,"-","项目基准 B")]:
            den=rates[key+"_events_per_keV"]
            h,=ax.plot(rates.ER_keV[mask],den[mask],color=col,ls=style,lw=1.8,label=label)
            ratio.plot(E,den[overlap]/ref,color=col,ls=style,lw=1.8)
            handles.append(h)
        dots=ax.scatter(points.ER_keV,points.lab_trace_events_keV,s=39,facecolors="white",
                        edgecolors="#26272a",zorder=7,label="独立积分的静态电荷")
        handles.append(dots)
        ratio.scatter(points.ER_keV,points.lab_trace_events_keV/points.red_events_keV,s=35,
                      facecolors="white",edgecolors="#26272a",zorder=5)
        ax.set_yscale("log")
        ax.set_ylim(2e-10,.45)
        ax.set_ylabel(r"$dN/dE_R$（例 / keV）")
        ratio.set_ylim(bottom=-.035)
        ratio.set_ylabel("计算谱 / 图 3 红线")
        for panel in (ax,ratio):
            panel.axvspan(high,805,color="#f0efeb",zorder=-5)
            panel.axvline(high,color="#8a8780",lw=.8)
        ax.text(high+4,.16,"高于计算端点",color="#60605e",va="center",fontsize=8.5)
        fig.legend(handles=handles,loc="lower left",bbox_to_anchor=(.1,.125),ncol=4,frameon=False,
                   handlelength=2.7,columnspacing=1.4,fontsize=9.6)
        fig.text(.114,.108,r"红线取自原图。灰虚线只取领先阶电荷 $c_M=1$ 和 $W_M^{00}(y)$。绿色 B 使用有限 $t_N$ 的核子形状因子，仍只取 $W_M$。",fontsize=9)
        fig.text(.114,.080,r"两条计算线均用七种氙同位素及截断标准晕，$v_0/v_{\rm esc}/v_{\rm lab}=220/544/232$ km/s，$\rho_\chi=0.3$ GeV/cm$^3$。",fontsize=9)
        fig.text(.114,.052,r"空心圆用实验室系标量能量和独立 Dirac 迹重算。下图每条曲线的分母均为原图红线。",fontsize=9)
        fig.text(.114,.026,r"图中耦合取 $g_1=0.1$、$g_2=1.725$、$g_{A'N}=0.04857$。",fontsize=9)
        pdf.savefig(fig)
        fig.savefig(OUT/"figure3_static_comparison.png",dpi=146)
        plt.close(fig)

        fig,ax,cum=layout("新版图 3 的红蓝曲线是否等面积",
                         "读取原图上框的红、蓝矢量曲线，按原图标度在真实反冲能上积分。")
        handles=[]
        for curve,col,ls,label in [(red,RED,"-","三体标量辐射（红实线）"),(blue,BLUE,"--","非弹性两体散射（蓝虚线）")]:
            e,y=curve.ER_keV.to_numpy(),curve.value.to_numpy()
            h,=ax.plot(e,y,color=col,lw=2.,ls=ls,label=label)
            handles.append(h)
            n=np.r_[0.,np.cumsum(np.diff(e)*y[:-1]*exprel(np.diff(np.log(y))))]
            cum.plot(e,n,color=col,lw=2.,ls=ls)
            cum.text(767,n[-1]+(.28 if col==RED else -.32),f"{n[-1]:.3f} 例",fontsize=9.5,
                     color=col,ha="right",va="bottom" if col==RED else "top")
        ax.set_ylim(bottom=0)
        ax.set_ylabel(r"$dN/dE_R$（例 / keV）")
        cum.set_ylim(-.25,12.4)
        cum.set_ylabel(r"累计事例数 $N(<E_R)$")
        fig.legend(handles=handles,loc="lower left",bbox_to_anchor=(.103,.13),ncol=2,
                   frameon=False,handlelength=3.2,columnspacing=2.2,fontsize=10)
        fig.text(.114,.108,"上图用线性纵轴展示各能段对积分的贡献。下图从各线首个可见顶点开始累计。",fontsize=9.4)
        fig.text(.114,.080,"图注声明蓝线归一到红线的积分。可见曲线给出红 / 蓝面积比 1.1474，两线相差约 1.40 例。",fontsize=9.4)
        fig.text(.114,.052,r"在 248 keV，原图上框读出的红 / 蓝为 1.6042，原图下框为 1.6046。",fontsize=9.4)
        pdf.savefig(fig)
        plt.close(fig)

    results=[*sorted(OUT.glob("*.csv")),OUT/"audit.json",OUT/"figure3_static_comparison.png",
             OUT/"pdf/figure3_audit.pdf"]
    lines=[hashlib.sha256(f.read_bytes()).hexdigest()+"  "+f.relative_to(OUT).as_posix() for f in results]
    (OUT/"SHA256SUMS").write_text("\n".join(lines)+"\n",encoding="utf8",newline="\n")


if __name__=="__main__":
    main()
