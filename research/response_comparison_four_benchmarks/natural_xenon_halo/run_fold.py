"""Four radiative benchmarks on AFH seven-isotope xenon, per natural kg and day."""
import argparse
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from scipy.integrate import quad

from three_body_tensor import fixed, integrated

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parents[1]
OUT = HERE / "output"
MASSES = RESEARCH / "afh_default_density_xe131/output/ame2020_exact_spatial_xe131_partial/xenon_isotope_ame2020_masses.csv"
ABUNDANCES = RESEARCH / "afh_default_density_natural_xenon_halo/input/natural_xenon_isotope_weights.csv"
NATIVE = OUT / "native_recoil_responses.csv"
sys.path.append(str(RESEARCH/"three_body_calculation_and_validation"))
from rate_kinematics import vmin_three_body_km_s
from run_natural_xenon_halo_fold import shm_truncated_pdf

SPIN = {128: 0, 129: .5, 130: 0, 131: 1.5, 132: 0, 134: 0, 136: 0}
BENCHMARKS = {name: (ms, gap) for name, ms, gap in fixed.BENCHMARKS}
V0, VEARTH, VESC = 220., 232., 544.
VMAX = VESC + VEARTH
RHO = .3
ORDER = (12, 12, 4, 4)  # halo speed, pair invariant mass, polar cosine, azimuth
CHANNELS = ("M", "PhiPP", "MPhiPP", "Delta", "SigmaPrime", "SigmaPrimeDelta")
COMPONENTS = tuple("ch_"+name for name in CHANNELS)
KEYS = ["benchmark", "ER_keV"]


@lru_cache(maxsize=1)
def inputs():
    masses = pd.read_csv(MASSES).set_index("A")
    abundance = pd.read_csv(ABUNDANCES).set_index("A").natural_atom_fraction
    if set(abundance.index) != {124, 126, *SPIN} or abs(abundance.sum()-1.) > 1e-12:
        raise ValueError("incomplete natural atom fraction table")
    np.testing.assert_allclose(abundance, masses.natural_atom_fraction, rtol=0, atol=1e-15)
    molar = float(masses.atomic_mass_u_AME2020 @ abundance)
    number = 1000*6.02214076e23/molar
    native = pd.read_csv(NATIVE).set_index(["A", "ER_keV"]).sort_index()
    if native.index.has_duplicates or set(native.index.get_level_values(0)) != set(SPIN):
        raise ValueError("unexpected native rows")
    if native.isna().any().any() or native.max_abs_imaginary.abs().max() > 2e-12:
        raise ValueError("invalid native response")
    if any(not np.array_equal(native.loc[a].index, native.loc[131].index) for a in SPIN):
        raise ValueError("native grids differ")
    return masses, abundance, molar, number, native


def isotope_input(a):
    masses, abund, _, nt, tables = inputs()
    mass = masses.at[a, "mA_AME2020_CODATA2022_GeV"]
    table = tables.loc[a]
    convention = 4*4*np.pi/(2*SPIN[a]+1)
    c0 = a**2/(convention*table.at[0, "M"])
    physical = table.loc[:, CHANNELS]*convention*c0
    np.testing.assert_allclose(physical.at[0, "M"], a**2, rtol=3e-15)
    er = table.index.to_numpy()*1e-6
    np.testing.assert_allclose(table.Q_A_GeV, np.sqrt(er*(2*mass+er)), rtol=2e-14)
    if not SPIN[a] and np.any(physical.loc[:, CHANNELS[3:]].to_numpy() != 0):
        raise ValueError("transverse response for a J=0 isotope")
    return mass, float(abund[a]), nt, c0, physical


def coefficients(mass, er, form_factors):
    t = -2*mass*er
    q2 = er*er - t
    f1, f2 = (f/3 for f in form_factors(-t))
    mn2 = fixed.ff.M_N_GEV**2
    cphi = q2*(f1+2*f2)/(4*mn2)
    cm = f1+t*(f1+2*f2)/(8*mn2)
    return np.array([cm**2, cphi**2, 2*cm*cphi, q2*f1**2/(2*mn2),
                     q2*(f1+f2)**2/(8*mn2), -q2*f1*(f1+f2)/(2*mn2)])


def dsigma_terms(mass, er, raw_physical, time, long_diff, transverse):
    """Arrays are cm^2/keV per evaluated speed; the overall prefactor is already applied."""
    strengths = coefficients(mass, er, fixed.ff.bishara_linear)*raw_physical
    alt = coefficients(mass, er, fixed.ff.isoscalar_zexp)*raw_physical
    charge = strengths[:3].sum()
    spatial = strengths[3:].sum()
    if charge <= 0 or spatial < -1e-16:
        raise ArithmeticError("nonpositive nuclear kernel")
    coulomb = time + long_diff
    channel = np.column_stack([coulomb*x for x in strengths[:3]] +
                              [transverse*x for x in strengths[3:]])
    cm0 = 1 - (2*mass*er)*(1-2*.184)/(8*fixed.ff.M_N_GEV**2)
    answers = {
        "M0_time": time*raw_physical[0], "A_time": time*cm0**2*raw_physical[0],
        "B_time": time*strengths[0], "B_Coul": coulomb*strengths[0],
        "C_time": time*charge, "D": channel.sum(axis=1),
        "space_delta": long_diff*charge+transverse*spatial,
        "B_time_zexp": time*alt[0], "C_time_zexp": time*sum(alt[:3]),
        "D_zexp": coulomb*sum(alt[:3])+transverse*sum(alt[3:]),
    }
    answers.update(zip(COMPONENTS, channel.T))
    return answers


def halo_nodes(vmin, nv):
    """A quadratic map smooths the three-body threshold at the lower limit."""
    x, w = fixed.eq6._cached_leggauss(nv)
    u = (x+1)/2
    split = VESC-VEARTH
    edges = [vmin] + ([split] if vmin < split else []) + [VMAX]
    v, dv = [], []
    for low, high in zip(edges[:-1], edges[1:]):
        v.extend(low+(high-low)*u**2)
        dv.extend((high-low)*u*w)
    return np.asarray(v), np.asarray(dv)


def one_isotope(task):
    name, a, selection, order, keep_nodes = task
    mass, atom_fraction, nt, _, physical = isotope_input(a)
    selected = physical.loc[selection] if selection is not None else physical
    ms_kev, gap_mev = BENCHMARKS[name]
    ms, gap = ms_kev*1e-6, gap_mev*1e-3
    # Multiply cm^2/keV by (nuclei/kg)*(chi/cm^3)*(km/s -> cm/s)*(s/day).
    flux_factor = nt*atom_fraction*(RHO/fixed.MCHI)*1e5*86400
    rows, nodes = [], []
    for energy, response in selected.iterrows():
        er = energy*1e-6
        threshold = vmin_three_body_km_s(fixed.MCHI, ms, mass, er)
        opened = threshold < VMAX
        if opened:
            speed, dv = halo_nodes(threshold, order[0])
            pdf = np.array([shm_truncated_pdf(float(v), V0, VEARTH, VESC) for v in speed])
            weight = dv*pdf*speed*flux_factor
            l00, dl, lt, p2 = integrated(mass, energy, ms, gap, speed, order[1:])
            prefactor = mass*fixed.GPROD2*fixed.CONVERT/(
                256*np.pi**3*p2*(fixed.MV**2+2*mass*er)**2)
        else:
            # A single integration placeholder retains a physical zero at a closed recoil.
            l00 = dl = lt = weight = np.zeros(1)
            prefactor = 1.
        values = dsigma_terms(mass, er, response.to_numpy(),
                              l00*prefactor, dl*prefactor, lt*prefactor)
        info = dict(benchmark=name, ER_keV=int(energy), A=a)
        if opened and keep_nodes:
            nodes.append(pd.DataFrame(dict(**info, speed_km_s=speed, dv_km_s=dv,
                             f_speed_per_km_s=pdf, fold_weight=weight,
                             B_time_cm2_keV=values["B_time"], C_time_cm2_keV=values["C_time"],
                             D_cm2_keV=values["D"],
                             **{k+"_cm2_keV":values[k] for k in COMPONENTS})))
        rows.append(dict(**info, atom_fraction=atom_fraction, mass_GeV=mass, vmin_km_s=threshold,
                         is_open=opened, R_M=response.M, **{k: float(weight@v) for k,v in values.items()}))
    return pd.DataFrame(rows), (pd.concat(nodes, ignore_index=True) if nodes else None)


def combine(iso):
    metrics = list(iso.loc[:, "M0_time":].columns)
    grouped = iso.groupby(KEYS, sort=False)
    total = grouped[metrics].sum()
    total["open_isotopes"] = grouped.is_open.sum().astype(int)
    for out, num, den in [
        ("M0_over_B_time", "M0_time", "B_time"), ("A_over_B_time", "A_time", "B_time"),
        ("D_over_B_time", "D", "B_time"), ("C_over_B_time", "C_time", "B_time"),
        ("D_over_B_Coul", "D", "B_Coul"), ("D_over_B_time_zexp", "D_zexp", "B_time_zexp"),
        ("D_over_C_time_minus1_ppm", "space_delta", "C_time"),
    ]:
        total[out] = total[num].div(total[den].where(total[den] > 0))
    total["D_over_C_time_minus1_ppm"] *= 1e6
    total["Xe131_fraction_of_D"] = iso[iso.A==131].set_index(KEYS).D / total.D.where(total.D>0)
    return total.reset_index()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workers", type=int, default=5)
    args = ap.parse_args()
    _, _, molar, nt, _ = inputs()
    pdf_integral = quad(lambda v: shm_truncated_pdf(v,V0,VEARTH,VESC), 0, VMAX,
                        points=[VESC-VEARTH], epsabs=1e-13)[0]
    if abs(pdf_integral-1.) > 1e-12:
        raise ArithmeticError("halo normalization")
    print(f"Natural Xe {molar:.12f} g/mol, {nt:.9g} atoms/kg, halo integral {pdf_integral:.16f}", flush=True)
    tasks = [(name, a, None, ORDER, True) for name in BENCHMARKS for a in SPIN]
    isotopes, micro = [], []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for (name, a, *_), (frame, nodes) in zip(tasks, pool.map(one_isotope, tasks)):
            isotopes.append(frame)
            if nodes is not None:
                micro.append(nodes)
            print(f"{name}  Xe-{a}  {frame.is_open.sum()} open recoil energies", flush=True)
    iso = pd.concat(isotopes, ignore_index=True)
    total = combine(iso)
    iso.to_csv(OUT/"isotope_contributions.csv.gz", index=False, compression={"method":"gzip","mtime":0})
    pd.concat(micro,ignore_index=True).to_csv(OUT/"microscopic_cross_sections.csv.gz", index=False,
                                             compression={"method":"gzip","mtime":0})
    total.to_csv(OUT/"halo_spectra.csv", index=False)
    print(total[total.ER_keV==267][KEYS+["B_time","D","D_over_B_time","Xe131_fraction_of_D"]].to_string(index=False))


if __name__ == "__main__":
    main()
