#!/usr/bin/env python3
from pathlib import Path
import argparse
import pandas as pd
import matplotlib.pyplot as plt

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--csv",type=Path,default=Path("output/afh_default_xe131_WM00.csv"))
    p.add_argument("--output",type=Path,default=Path("output/afh_default_xe131_WM00.png"))
    a=p.parse_args()
    d=pd.read_csv(a.csv)
    fig,ax=plt.subplots(figsize=(9,5.8))
    ax.plot(d["ER_keV"],d["R_over_A2"],label=r"AFH default $W_M^{00}$ (equal $g_p=g_n$)")
    ax.plot(d["ER_keV"],d["R_equal_J0_normalized"]/(131**2),linestyle="--",label=r"$J=0$")
    ax.plot(d["ER_keV"],d["R_equal_J2_normalized"]/(131**2),linestyle=":",label=r"$J=2$")
    for x in (101,267,542):
        ax.axvline(x,linestyle=":",linewidth=0.8)
    ax.set_xlim(0,800)
    ax.set_ylim(1e-9,2)
    ax.set_yscale("log")
    ax.set_xlabel(r"$E_R$ [keV]")
    ax.set_ylabel(r"$\mathcal{R}_{131}(E_R)/A^2$")
    ax.grid(True,which="both",alpha=0.2)
    ax.legend()
    fig.tight_layout()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(a.output,dpi=220)
    plt.close(fig)

if __name__=="__main__":
    main()

