"""Two-page comparison of actual Fig. 3 data, independent predictions, and window yields."""
import hashlib
from pathlib import Path
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
from scipy.integrate import cumulative_trapezoid

import paper_kernels as k

sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"figure3_source_audit"))
from plot_comparison import configure

OUT=k.OUT
PAPER, FORMAL, LEADING, OLD = "#b82d35","#234f80","#007661","#898a8c"
METHODS=[
    ("paper_AME_pole",OLD,(0,(1.2,2.6)),"原项目输入 · 式 (22)"),
    ("published_AFHmass_pole",FORMAL,(0,(6,2.8)),"公开 halo 参数 · 式 (22)"),
    ("blue_mean_AFHmass_ID_contact",LEADING,(0,(6,2,1.3,2)),"蓝线约束 halo · 正文 "+r"$I(D)$"),
]


def legend_handles():
    return [Line2D([],[],color=PAPER,lw=2.,marker="o",mfc="white",markersize=4,label="新版图 3 红线")] + [
        Line2D([],[],color=color,ls=style,lw=1.9,label=label) for _,color,style,label in METHODS]


def captions(fig,method_table):
    b=method_table.loc["blue_mean_AFHmass_ID_contact"]
    fig.text(.108,.129,r"红线及空心点取自原图。灰点线采用 AME 核质量与 $(v_0,v_{\rm esc},v_{\rm lab})=(220,544,232)$ km/s。",fontsize=9.4)
    fig.text(.108,.100,r"蓝虚线采用 $m_A=A\times0.938272$ GeV、$(238,544,254)$ km/s，积分两图的相干振幅，辐射后传播子取极点宽度。",fontsize=9.4)
    line=(r"绿点划线取相同 $m_A$，按正文常振幅 $I(D)$ 和重中介子极限计算。固定 $v_{\rm lab}=250.2$，由蓝线得到 "
          +rf"$v_0={b.v0:.2f}$、$v_{{\rm esc}}={b.vesc:.2f}$ km/s。")
    fig.text(.108,.071,line,fontsize=9.4)
    fig.text(.108,.042,r"三条计算线均采用七种氙同位素的 AFH 电荷响应，$g_1=0.1$、$g_2=1.725$、$g_{VN}=0.04857$，$\rho_\chi=0.3$ GeV/cm$^3$。",fontsize=9.4)


def title(fig,headline,sub):
    fig.text(.105,.953,headline,va="top",fontsize=19,weight="bold")
    fig.text(.108,.891,sub,va="top",fontsize=10,color="#41454b")


def style(ax):
    ax.grid(axis="y",color="#dadbdd",lw=.6)
    ax.set_axisbelow(True)


def add_legends(fig,table):
    fig.legend(handles=legend_handles(),ncol=2,loc="lower left",bbox_to_anchor=(.101,.154),
               handlelength=3.6,columnspacing=2.0,frameon=False,fontsize=9.5)
    captions(fig,table)


def main():
    configure()
    table=pd.read_csv(OUT/"matched_comparisons.csv").set_index("model")
    data=pd.read_csv(OUT/"matched_spectra.csv.gz")
    actual=k.reference()["red"]
    models={i:g.sort_values("ER_keV") for i,g in data.groupby("model") if i in table.index}
    (OUT/"pdf").mkdir(exist_ok=True)
    filename=OUT/"pdf/figure3_red_reproduction.pdf"
    with PdfPages(filename,metadata={"Title":"新版论文图 3 红线复现","CreationDate":None,"ModDate":None}) as pdf:
        fig,(ax,ratio)=plt.subplots(2,1,figsize=(10,8.75),gridspec_kw={"height_ratios":[1.55,1]})
        fig.subplots_adjust(left=.11,right=.95,top=.845,bottom=.295,hspace=.40)
        title(fig,"图 3 红线的绝对事例谱与计算对照",
              r"$m_{\chi_1}=1$ TeV，$m_{A^\prime}=5$ GeV，$m_s=300$ keV，$\Delta m=10$ MeV　｜　2.84 吨·年，探测效率取 1")
        ax.plot(*actual,color=PAPER,lw=2.2)
        for name,col,ls,_ in METHODS:
            f=models[name]; mask=f.red_prediction_events_keV>0
            ax.plot(f.ER_keV[mask],f.red_prediction_events_keV[mask],color=col,ls=ls,lw=1.65)
            if name!="paper_AME_pole":
                f=f[f.ER_keV.between(120,700)]
                ratio.plot(f.ER_keV,f.red_prediction_events_keV/f.red_pdf_events_keV,color=col,ls=ls,lw=1.75)
        ci=np.arange(6,len(actual[0])-1,29)
        ax.plot(actual[0,ci],actual[1,ci],ls="none",marker="o",mfc="white",mec=PAPER,ms=3.4,zorder=6)
        ax.set(xlim=(85,805),ylim=(1e-10,.32),yscale="log",ylabel=r"$dN/dE_R$（例 / keV）",
               xlabel=r"真核反冲能 $E_R$（keV）")
        ratio.axhline(1,color=PAPER,lw=.9,alpha=.8)
        ratio.set(xlim=(120,700),ylabel="计算 / 原图红线",xlabel=r"真核反冲能 $E_R$（keV）")
        ratio.text(.017,.91,"两种复现方案，120–700 keV",va="top",transform=ratio.transAxes,fontsize=9,
                   bbox=dict(facecolor="white",edgecolor="none",alpha=.85,pad=2))
        for panel in (ax,ratio):
            style(panel)
        add_legends(fig,table)
        pdf.savefig(fig)
        fig.savefig(OUT/"figure3_red_overlay.png",dpi=139)
        plt.close(fig)

        fig=plt.figure(figsize=(10,8.75))
        title(fig,"两个反冲能窗内的累计事例数","从各窗左边界开始累计。曲线的右端给出整窗总数。")
        axes=fig.subplots(1,2)
        fig.subplots_adjust(left=.105,right=.95,top=.79,bottom=.435,wspace=.27)
        for ax,(lo,hi),window,heading in zip(axes,[(100.,200.),(215.5,280.5)],["low_events","candidate_events"],["100–200 keV","215.5–280.5 keV"]):
            er,n=k.reference_cumulative(actual,lo,hi)
            ax.plot(er,n,color=PAPER,lw=2.3)
            for name,col,ls,_ in METHODS:
                f=models[name]; f=f[f.ER_keV.between(lo,hi)]
                count=cumulative_trapezoid(f.red_prediction_events_keV,f.ER_keV,initial=0.)
                assert abs(count[-1]-table.at[name,window])<2e-12
                ax.plot(f.ER_keV,count,color=col,ls=ls,lw=1.8)
            ax.plot(er[::max(1,len(er)//7)],n[::max(1,len(er)//7)],ls="none",marker="o",ms=3.5,mfc="white",mec=PAPER)
            ax.set(xlim=(lo,hi),ylim=(0,None),title=heading,xlabel=r"积分上限 $E_R$（keV）")
            style(ax)
        axes[0].set_ylabel(r"累计事例数 $N([E_{\rm low},E_R])$（例）")
        tab=fig.add_axes([.104,.249,.848,.105]);tab.axis("off")
        observed=[k.reference_cumulative(actual,lo,hi)[1][-1] for lo,hi in ((100.,200.),(215.5,280.5))]
        numbers=[observed]+[list(table.loc[n,["low_events","candidate_events"]]) for n,_,_,_ in METHODS]
        cells=tab.table(cellText=[[f"{pair[j]:.5f}" for pair in numbers] for j in (0,1)],
                        colLabels=["图 3 红线","原项目输入","公开 halo · 完整振幅","蓝线约束 · "+r"$I(D)$"],
                        rowLabels=["低能窗","候选窗"],cellLoc="center",rowLoc="center",loc="center")
        cells.auto_set_font_size(False);cells.set_fontsize(9.3);cells.scale(.93,1.38)
        for (row,col),cell in cells.get_celld().items():
            cell.set_edgecolor("#dce0e1");cell.set_linewidth(.5)
            if row==0:cell.set_facecolor("#edf1f2")
        add_legends(fig,table)
        pdf.savefig(fig)
        plt.close(fig)

    outputs=[p for p in OUT.rglob("*") if p.is_file() and p.suffix in {".csv",".gz",".json",".png",".pdf"}]
    files=sorted([k.HERE/"README.md",*k.HERE.glob("*.py"),*outputs])
    checksums=[f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(k.HERE).as_posix()}" for p in files]
    (k.HERE/"SHA256SUMS").write_text("\n".join(checksums)+"\n",encoding="utf8",newline="\n")


if __name__=="__main__":
    main()
