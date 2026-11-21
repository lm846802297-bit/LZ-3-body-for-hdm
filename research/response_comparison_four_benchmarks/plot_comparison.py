"""Publication-size four-panel spectra and ratios, with a spatial-current inset."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import AutoMinorLocator, MaxNLocator

HERE = Path(__file__).resolve().parent
OUT = HERE / 'results'
COLORS = dict(full='#007F91', time='#E18D25', paper='#414651', inset='#8156A6')
BENCHMARK_COLORS = dict(red='#B83E3E', green='#2B794E', black='#30363D', blue='#365DAD')


def make_figures(rows):
    plt.rcParams.update({
        'font.family': 'DejaVu Sans', 'font.size': 11,
        'axes.titlesize': 12, 'axes.labelsize': 12,
        'axes.spines.top': False, 'axes.spines.right': False,
        'axes.linewidth': .9, 'xtick.direction': 'in', 'ytick.direction': 'in',
        'pdf.fonttype': 42, 'ps.fonttype': 42, 'savefig.facecolor': 'white',
    })
    order = ('red', 'green', 'black', 'blue')
    groups = [[r for r in rows if r['benchmark']==name and r['phase_space_open']] for name in order]
    params = r'$m_\chi=1$ TeV, $m_V=10$ GeV, $v=800$ km/s, $(g_1g_2g_{VN})^2=10^{-8}$, $g_2=1$'
    footer = ('Full-current candidate: leading one-body vector current with six AFH terms; finite-$Q^2$ nucleon form factors.\n'
              'Common pole width, Xe-131 mass and normalization; bound-nucleus amplitude matching remains provisional.')
    handles = [
        Line2D([], [], color=COLORS['full'], lw=3, label='Full current (candidate)'),
        Line2D([], [], color=COLORS['time'], lw=1.8, ls=(0,(4,3)), label='Time component only'),
        Line2D([], [], color=COLORS['paper'], lw=1.8, ls=(0,(7,3,1.5,3)), label='Original-paper approximation'),
    ]
    fig, axes = plt.subplots(2,2,figsize=(12.8,9.4))
    fig.subplots_adjust(top=.805,bottom=.12,left=.09,right=.975,hspace=.30,wspace=.24)
    fig.suptitle('Xe-131 differential cross sections', x=.53,y=.973,fontsize=21,fontweight='bold')
    fig.text(.53,.925,params,ha='center',fontsize=11.5)
    fig.legend(handles=handles, loc='upper center',bbox_to_anchor=(.53,.895),ncol=3,frameon=False,fontsize=11)
    for i,(ax,name,group) in enumerate(zip(axes.flat,order,groups)):
        x=np.array([r['ER_keV'] for r in group])
        full=np.array([r['full_candidate_cm2_per_keV'] for r in group])
        time=np.array([r['time_only_cm2_per_keV'] for r in group])
        paper=np.array([r['paper_cm2_per_keV'] for r in group])
        ax.semilogy(x,paper,color=COLORS['paper'],lw=1.8,ls=(0,(7,3,1.5,3)),zorder=1)
        ax.semilogy(x,full,color=COLORS['full'],lw=3,zorder=2)
        ax.semilogy(x,time,color=COLORS['time'],lw=1.7,ls=(0,(4,3)),zorder=3)
        ax.set_title(f'({chr(97+i)})  '+rf'$m_s={group[0]["ms_keV"]:.0f}$ keV, $\Delta m={group[0]["delta_m_MeV"]:.0f}$ MeV',loc='left',color=BENCHMARK_COLORS[name],pad=10)
        ax.set_xlim(0,1020)
        ax.set_xticks(np.arange(0,1001,200))
        top=max(paper.max(),full.max())
        ax.set_ylim(top*1e-7,top*2.5)
        ax.set_xlabel(r'Recoil energy $E_R$ [keV]')
        ax.set_ylabel(r'$\mathrm{d}\sigma/\mathrm{d}E_R$ [cm$^2$/keV]')
        ax.grid(True,which='major',color='#D7DBE1',lw=.6,alpha=.7)
        ax.xaxis.set_minor_locator(AutoMinorLocator(2))
        ax.text(.97,.95,'Full and time-only overlap\nat the spectrum scale',transform=ax.transAxes,ha='right',va='top',fontsize=9,color='#65707B')
    fig.text(.09,.025,footer,fontsize=9,color='#535D68',linespacing=1.6)
    for ext in ('png','pdf','svg'):
        fig.savefig(OUT/f'differential_cross_sections.{ext}',dpi=220)
    plt.close(fig)

    fig,axes=plt.subplots(2,2,figsize=(12.8,10.1))
    fig.subplots_adjust(top=.805,bottom=.105,left=.09,right=.975,hspace=.31,wspace=.24)
    fig.suptitle('Nuclear-response comparison: cross-section ratios',x=.53,y=.975,fontsize=19,fontweight='bold')
    fig.text(.53,.932,params,ha='center',fontsize=11.5)
    ratio_handles=[
        Line2D([],[],color=COLORS['full'],lw=3,label='Full candidate / original paper'),
        Line2D([],[],color=COLORS['time'],lw=1.8,ls=(0,(4,3)),label='Time only / original paper'),
        Line2D([],[],color=COLORS['paper'],lw=1.3,ls='--',label='Original paper / itself = 1'),
    ]
    fig.legend(handles=ratio_handles,loc='upper center',bbox_to_anchor=(.53,.905),ncol=3,frameon=False,fontsize=10.5)
    all_ratio=np.array([r['full_over_paper'] for r in rows if r['phase_space_open']])
    ymin=max(0.,min(all_ratio.min()*.88,.35))
    ymax=max(1.17,all_ratio.max()*1.13)
    for i,(ax,name,group) in enumerate(zip(axes.flat,order,groups)):
        x=np.array([r['ER_keV'] for r in group])
        ax.plot(x,[r['full_over_paper'] for r in group],color=COLORS['full'],lw=3,zorder=2)
        ax.plot(x,[r['time_over_paper'] for r in group],color=COLORS['time'],lw=1.7,ls=(0,(4,3)),zorder=3)
        ax.axhline(1,color=COLORS['paper'],ls='--',lw=1.2,zorder=1)
        ax.set_title(f'({chr(97+i)})  '+rf'$m_s={group[0]["ms_keV"]:.0f}$ keV, $\Delta m={group[0]["delta_m_MeV"]:.0f}$ MeV',loc='left',color=BENCHMARK_COLORS[name],pad=10)
        ax.set_xlim(0,1020)
        ax.set_xticks(np.arange(0,1001,200))
        ax.set_ylim(ymin,ymax)
        ax.set_xlabel(r'Recoil energy $E_R$ [keV]')
        ax.set_ylabel(r'$(\mathrm{d}\sigma/\mathrm{d}E_R)\,/\,(\mathrm{d}\sigma/\mathrm{d}E_R)_{\rm paper}$',fontsize=11)
        ax.grid(True,color='#D7DBE1',lw=.6,alpha=.7)
        ax.xaxis.set_minor_locator(AutoMinorLocator(2))
        inset=ax.inset_axes([.48,.56,.48,.37])
        inset.patch.set_facecolor('#FAFAFD')
        inset.plot(x,[r['full_over_time_minus_1_ppm'] for r in group],color=COLORS['inset'],lw=1.3)
        inset.set_xlim(0,1020)
        inset.set_title(r'$10^6\,[(\mathrm{d}\sigma/\mathrm{d}E_R)_{\rm full}/(\mathrm{d}\sigma/\mathrm{d}E_R)_{\rm time}-1]$',fontsize=8,pad=5)
        inset.tick_params(labelsize=8,length=3)
        inset.yaxis.set_major_locator(MaxNLocator(3))
        inset.xaxis.set_major_locator(MaxNLocator(4))
        inset.grid(True,lw=.45,alpha=.5)
    fig.text(.09,.023,'Ratios are defined only inside open three-body phase space; endpoints with 0/0 are omitted.\n'
             'Inset resolves the spatial-current correction in ppm. Full current is a leading one-body candidate.',fontsize=9,color='#535D68',linespacing=1.6)
    for ext in ('png','pdf','svg'):
        fig.savefig(OUT/f'cross_section_ratios.{ext}',dpi=220)
    plt.close(fig)


if __name__=='__main__':
    import csv
    with (OUT/'differential_cross_sections.csv').open(encoding='utf-8',newline='') as stream:
        rows=list(csv.DictReader(stream))
    for row in rows:
        for key,val in list(row.items()):
            if key=='phase_space_open': row[key]=val=='True'
            elif key not in ('benchmark','response_sampling'): row[key]=float(val) if val else None
    make_figures(rows)
