"""Render the two fixed-benchmark comparisons without dividing at endpoints."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def make_figures(out, rows):
    def column(key):
        return np.asarray([row[key] for row in rows], dtype=float)

    energy = column('ER_keV')
    opened = column('phase_space_open').astype(bool)
    blue, orange, teal, purple = '#21618A', '#A14A15', '#067568', '#714596'
    with plt.rc_context({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.spines.top': False,
                         'axes.spines.right': False, 'axes.grid': True, 'grid.alpha': .18,
                         'legend.frameon': False, 'lines.linewidth': 2}):
        fig, axes = plt.subplots(2, 2, figsize=(10.2, 7.2), sharex=True, layout='constrained')
        fig.suptitle(r'Xe-131  |  Three-body charge projection at $v=776$ km/s', fontsize=16)
        strength, tensor, correction, diagrams = axes.flat
        strength.set_title('A   Charge weight', loc='left', fontweight='bold')
        strength.plot(energy, column('LC_GeV2') / 1e6, color=blue, lw=3, label=r'$L_C$')
        strength.plot(energy, column('L00_GeV2') / 1e6, color=orange, ls=(0, (4, 4)), lw=1.4, label=r'$L_{00}$ (overlaps)')
        strength.set_ylabel(r'Integrated weight [$10^6$ GeV$^2$]'); strength.legend()
        tensor.set_title('B   Longitudinal decomposition', loc='left', fontweight='bold')
        for key, label, color, style in [('LL_GeV2', r'$L_{LL}$ (unweighted)', blue, '-'),
                                        ('mix_0L_GeV2', r'$|-2r\,\mathrm{Re}\,L_{0L}|$ (term is negative)', orange, '--'),
                                        ('LL_weighted_GeV2', r'$r^2 L_{LL}$', teal, '-.')]:
            tensor.semilogy(energy[opened], np.abs(column(key)[opened]), color=color, ls=style, label=label)
        tensor.set_ylabel(r'Magnitude [GeV$^2$]'); tensor.legend(fontsize=9)
        correction.set_title('C   Same nuclear charge in both spectra', loc='left', fontweight='bold')
        correction.plot(energy, column('LC_over_L00_minus_one') * 1e6, color=teal)
        correction.set_ylabel(r'$10^6\,(L_C/L_{00}-1)$  [ppm]')
        diagrams.set_title('D   Interference of the two radiation diagrams', loc='left', fontweight='bold')
        diagrams.plot(energy, 100 * column('diagram_interference_fraction'), color=purple)
        diagrams.set_ylabel(r'$100\,L_{C,ab}/L_C$  [%]')
        for axis in axes[1]:
            axis.set_xlabel(r'Nuclear recoil $E_R$ [keV]')
        fig.savefig(out / 'charge_weights.png', dpi=175); plt.close(fig)

        fig, (spectrum, ratios) = plt.subplots(2, 1, figsize=(8.7, 7.0), sharex=True, layout='constrained')
        fig.suptitle(r'Xe-131  |  What is the point-charge reference?', fontsize=16)
        spectrum.set_title(r'Fixed $\Delta m=450$ keV, zero width, unit coupling product squared', loc='left')
        spectrum.semilogy(energy[opened], column('dsigma_point_M_cm2_per_keV')[opened], color=orange,
                          ls='--', label=r'Point-nucleon $M$: $F_1(0)^2 W_M L_C$')
        spectrum.semilogy(energy[opened], column('dsigma_ch_cm2_per_keV')[opened], color=blue,
                          label=r'Finite-$Q^2$ charge: $M+\Phi^{\prime\prime}$, signed interference')
        spectrum.set_ylabel(r'$d\sigma/dE_R$ [cm$^2$/keV]'); spectrum.legend(fontsize=9)
        ratios.plot(energy, column('full_over_point_M'), color=blue, label=r'Full / point-nucleon $M$ at common $L_C$')
        ratios.plot(energy, column('full_over_finite_M'), color=teal, ls='--', label=r'Full / finite-$Q^2$ $M$ at common $L_C$')
        ratios.axhline(1., color='#787878', lw=.9, ls=':')
        ratios.set_ylabel('Nuclear response ratio'); ratios.set_xlabel(r'Nuclear recoil $E_R$ [keV]'); ratios.legend(fontsize=9)
        fig.savefig(out / 'point_charge_comparison.png', dpi=175); plt.close(fig)
