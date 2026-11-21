"""Shared Matplotlib style for manuscript-ready Xe-131 figures."""
from __future__ import annotations
import matplotlib as mpl
import matplotlib.pyplot as plt

PAPER_RC = {
    "font.family": "serif",
    "font.serif": ["STIX Two Text", "STIXGeneral", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "font.size": 9.5,
    "axes.labelsize": 10.5,
    "axes.titlesize": 10.5,
    "legend.fontsize": 8.5,
    "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5,
    "axes.linewidth": 0.8,
    "lines.linewidth": 1.65,
    "lines.markersize": 3.5,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.top": True,
    "ytick.right": True,
    "xtick.minor.visible": True,
    "ytick.minor.visible": True,
    "legend.frameon": False,
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.035,
}

def apply_paper_style() -> None:
    mpl.rcParams.update(PAPER_RC)

def save_paper_figure(fig, stem) -> None:
    stem = str(stem)
    fig.savefig(stem + ".svg", format="svg")
    fig.savefig(stem + ".pdf", format="pdf")
    plt.close(fig)
