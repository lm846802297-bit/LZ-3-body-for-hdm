"""Fixed-speed Xe-131: paper, temporal finite-Q2, and full-current candidate.

All curves share parameters, phase space, width, C0 and gVN normalization.
The current is exact on the DM side. Nuclear current matching is provisional.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time

import numpy as np
import scipy
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq

HERE = Path(__file__).resolve().parent
UPSTREAM = HERE / 'inputs/upstream/research'
for name in ('three_body_calculation_and_validation', 'vector_current_response_audit',
             'three_body_spin_resolved_current', 'three_body_full_current_nucleon_match'):
    sys.path.insert(0, str(UPSTREAM / name))
import eq6_kernel as eq6
import phase_space_convergence as psc
import nucleon_vector_form_factors as ff

MCHI, MA, MV, SPEED = 1000., 131 * .93149410242, 10., 800.
G2, GPROD2 = 1., 1e-8
CONVERT = 3.893793721e-34
BETA = SPEED / eq6.C_KM_S
ECHI = MCHI / math.sqrt(1 - BETA**2)
PCHI = ECHI * BETA
BENCHMARKS = (('red', 200., 1.), ('green', 300., 1.), ('black', 360., 1.), ('blue', 300., 10.))
CHANNELS = ('M', 'SigmaDoublePrime', 'SigmaPrime', 'PhiPP', 'PhiTildePrime', 'Delta', 'MPhiPP', 'SigmaPrimeDelta')
ORDER = (16, 8, 8)
FINE = (32, 16, 16)
OUT = HERE / 'results'


def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csv_read(path):
    with path.open(encoding='utf-8', newline='') as stream:
        return list(csv.DictReader(stream))


def csv_write(path, rows):
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def span_at(recoil_keV, ms):
    er = np.asarray(recoil_keV) * 1e-6
    q = np.sqrt(er * (2 * MA + er))
    return 2 * (PCHI * q - (ECHI + MA) * er) - ms * (2 * MCHI + ms)


def endpoints(ms):
    grid = np.linspace(0, 1500, 3001)
    vals = span_at(grid, ms)
    brackets = [(a, b) for a, b, va, vb in zip(grid[:-1], grid[1:], vals[:-1], vals[1:]) if va * vb < 0]
    if len(brackets) != 2:
        raise ArithmeticError('Expected two recoil endpoints')
    return [brentq(lambda e: float(span_at(e, ms)), *b, xtol=1e-10) for b in brackets]


def boost_batch(p, beta):
    b2 = np.sum(beta * beta, axis=-1)
    gamma = 1 / np.sqrt(1 - b2)
    spatial = np.broadcast_to(p[..., 1:], beta.shape)
    energy = np.broadcast_to(p[..., 0], b2.shape)
    bp = np.sum(spatial * beta, axis=-1)
    factor = gamma**2 / (gamma + 1) * bp + gamma * energy
    return np.column_stack((gamma * (energy + bp), spatial + factor[:, None] * beta))


def slash_batch(p):
    return np.einsum('ni,ijk->njk', p * np.array([1., -1., -1., -1.]), np.asarray(eq6.GAMMA))


def spinors_batch(p):
    root = np.sqrt(p[:, 0] + MCHI)
    upper = root[:, None, None] * eq6.I2
    lower = np.einsum('ni,ijk->njk', p[:, 1:], np.asarray([eq6.s1, eq6.s2, eq6.s3])) / root[:, None, None]
    return np.concatenate((upper, lower), axis=1)


def phase_points(recoil_keV, ms, order):
    """Vectorized threshold-u2 map; identical angle convention to _stable_build_point."""
    er = recoil_keV * 1e-6
    q = math.sqrt(er * (2 * MA + er))
    span = float(span_at(recoil_keV, ms))
    nw, nz, nphi = order
    xw, ww = eq6._cached_leggauss(nw)
    z, wz = eq6._cached_leggauss(nz)
    u, z, phi = np.meshgrid((xw + 1) / 2, z, 2 * np.pi * (np.arange(nphi) + .5) / nphi, indexing='ij')
    u, z, phi = (item.ravel() for item in (u, z, phi))
    delta = span * u**2
    w2 = (MCHI + ms)**2 + delta
    rootw = np.sqrt(w2)
    cosq = (ms * (2 * MCHI + ms) + delta + 2 * (ECHI + MA) * er) / (2 * PCHI * q)
    if np.any(np.abs(cosq) > 1 + 1e-11):
        raise ArithmeticError('Invalid recoil angle')
    cosq = np.clip(cosq, -1, 1)
    q4 = np.column_stack((np.full_like(u, er), q * np.sqrt(1 - cosq**2), np.zeros_like(u), q * cosq))
    p = np.array([ECHI, 0, 0, PCHI])
    K = p - q4
    betaK = K[:, 1:] / K[:, :1]
    pstar = boost_batch(p, -betaK)
    e3 = pstar[:, 1:] / np.linalg.norm(pstar[:, 1:], axis=1)[:, None]
    reference = np.tile([1., 0, 0], (len(u), 1))
    reference[np.abs(e3[:, 0]) > .9] = [0, 1., 0]
    e1 = np.cross(reference, e3)
    e1 /= np.linalg.norm(e1, axis=1)[:, None]
    e2 = np.cross(e3, e1)
    direction = z[:, None] * e3 + np.sqrt(1 - z*z)[:, None] * (np.cos(phi)[:, None] * e1 + np.sin(phi)[:, None] * e2)
    kabs = np.sqrt(delta * (4 * MCHI * ms + delta)) / (2 * rootw)
    ek = (2 * ms * (MCHI + ms) + delta) / (2 * rootw)
    ep = (2 * MCHI * (MCHI + ms) + delta) / (2 * rootw)
    k = boost_batch(np.column_stack((ek, kabs[:, None] * direction)), betaK)
    pp = boost_batch(np.column_stack((ep, -kabs[:, None] * direction)), betaK)
    weights = (ww[:, None, None] * wz[None, :, None] * np.ones((1, 1, nphi)) / nphi).ravel()
    weights *= span * u * np.sqrt(delta * (4 * MCHI * ms + delta)) / w2
    return p, pp, k, K, q4, delta, weights, z, phi


def integrate(recoil_keV, ms, gap, order=ORDER, validate=False):
    span = float(span_at(recoil_keV, ms))
    if span <= 2 * math.ulp((MCHI + ms)**2):
        return dict(L00=0., ReL0L=0., LLL=0., LC=0., LT=0., deltaLC=0., phase_open=False)
    clearance_w2 = (gap - ms) * (2 * MCHI + gap + ms) - span
    if clearance_w2 <= 0:
        raise ArithmeticError('On-shell chi2 reached')
    p, pp, k, K, q4, delta, weights, z, phi = phase_points(recoil_keV, ms, order)
    heavy = MCHI + gap
    width = eq6.chi2_width_dirac_scalar(MCHI, ms, gap, G2)
    den_b = ms**2 - gap * (2 * MCHI + gap) - 2 * (p[0] * k[:, 0] - k[:, 1:] @ p[1:])
    den_a = (ms - gap) * (2 * MCHI + ms + gap) + delta + 1j * heavy * width
    prop_b = (slash_batch(p - k) + heavy * eq6.ID4) / den_b[:, None, None]
    prop_a = (slash_batch(K) + heavy * eq6.ID4) / den_a[:, None, None]
    gammas = np.asarray(eq6.GAMMA)
    vertices = gammas[None] @ prop_b[:, None] + prop_a[:, None] @ gammas[None]
    uin = spinors_batch(p[None])[0]
    ubar = spinors_batch(pp).conj().swapaxes(-1, -2) @ eq6.GAMMA[0]
    current = ubar[:, None] @ vertices @ uin
    qnorm = np.linalg.norm(q4[:, 1:], axis=1)
    qhat = q4[:, 1:] / qnorm[:, None]
    transverse1 = np.cross(np.tile([0., 1., 0.], (len(qhat), 1)), qhat)
    transverse1 /= np.linalg.norm(transverse1, axis=1)[:, None]
    transverse2 = np.cross(qhat, transverse1)
    time_current = current[:, 0]
    longitudinal = np.einsum('ni,niab->nab', qhat, current[:, 1:])
    t1 = np.einsum('ni,niab->nab', transverse1, current[:, 1:])
    t2 = np.einsum('ni,niab->nab', transverse2, current[:, 1:])
    r = recoil_keV * 1e-6 / qnorm[0]
    coulomb = time_current - r * longitudinal
    def norm(a):
        return .5 * np.sum(np.abs(a)**2, axis=(-1, -2))
    l00 = float(weights @ norm(time_current))
    mix = float(weights @ (.5 * np.sum(time_current * longitudinal.conj(), axis=(-1, -2)).real))
    lll = float(weights @ norm(longitudinal))
    lc = float(weights @ norm(coulomb))
    lt = float(weights @ (norm(t1) + norm(t2)))
    dlc = -2 * r * mix + r*r * lll
    if abs(lc - (l00 + dlc)) > 2e-13 * l00 or min(l00, lc, lll, lt) < 0:
        raise ArithmeticError('Invalid current contraction')
    result = dict(L00=l00, ReL0L=mix, LLL=lll, LC=lc, LT=lt, deltaLC=dlc, phase_open=True)
    if validate:
        errors = []
        trace_errors = []
        for i in [0, len(delta)//3, len(delta)//2, len(delta)-1]:
            point = psc._stable_build_point(MCHI, ms, MA, recoil_keV * 1e-6, SPEED, float(delta[i]), float(z[i]), float(phi[i]))
            errors.append(max(float(np.max(np.abs(pp[i] - point.p_prime))), float(np.max(np.abs(k[i] - point.k_s)))))
            # Dirac spin sum is independent of the 2x2 explicit-spinor calculation.
            a = (eq6.slash(point.p_prime) + MCHI * eq6.ID4)
            b = (eq6.slash(point.p) + MCHI * eq6.ID4)
            tensors = .5 * np.einsum('mij,nji->mn', a @ vertices[i] @ b, eq6.GAMMA[0] @ vertices[i].conj().swapaxes(-1, -2) @ eq6.GAMMA[0])
            spin = .5 * np.einsum('mab,nab->mn', current[i], current[i].conj())
            trace_errors.append(float(np.linalg.norm(tensors - spin) / np.linalg.norm(spin)))
        result['kinematics_max_abs_GeV'] = max(errors)
        result['trace_vs_spinor_max_rel'] = max(trace_errors)
        result['conservation_max_abs_GeV'] = float(np.max(np.abs(p - pp - k - q4)))
        result['scalar_mass_shell_max_abs_GeV2'] = float(np.max(np.abs(k[:, 0]**2 - np.sum(k[:, 1:]**2, axis=1) - ms**2)))
    return result


def load_nuclear():
    for record in json.loads((HERE/'inputs/provenance.json').read_text()):
        if hash_file(HERE/record['path']) != record['sha256']:
            raise ValueError('Pinned source/input checksum changed: ' + record['path'])
    gate = json.loads((HERE/'inputs/native-comparison.json').read_text())
    if gate['status'] != 'PASS' or not gate['native_afh_validated'] or gate['rows_compared'] != 16807:
        raise ValueError('Native response gate is not valid')
    table = csv_read(HERE/'inputs/afh_v6_xe131_eight_response_native.csv')
    q = np.array([float(row['q_GeV']) for row in table])
    raw = np.array([[float(row[f'W_{c}00_AFH']) for c in CHANNELS] for row in table])
    if len(q) != 2401 or np.max(np.abs(q - np.linspace(0, .6, 2401))) > 1e-13:
        raise ValueError('Unexpected native q grid')
    if any(abs(float(row[f'Im_W_{c}00_AFH'])) > 2e-12 for row in table for c in CHANNELS):
        raise ValueError('Nonreal native response')
    # 4pi/(2J+1) times the equal-pn factor 4, and common rounded-density C0.
    c0 = 131**2 / (4 * math.pi * raw[0, 0])
    physical = 4 * math.pi * c0 * raw
    return q, physical, PchipInterpolator(q, physical, extrapolate=False), c0


def assemble(recoil_keV, tensor, responses, name, ms_keV, gap_MeV, source):
    er = recoil_keV * 1e-6
    q = math.sqrt(er * (2 * MA + er))
    wm, wss, ws, wp, wpt, wd, wmp, wsd = responses
    f1_raw, f2_raw = ff.isoscalar_zexp(q*q)
    # gVN already contains F1V(0)=3. Normalize coefficients to unit nucleon charge.
    f1, f2 = f1_raw/3, f2_raw/3
    cm, cp = ff.charge_coefficients(q, F1=f1, F2=f2)
    nuclear_charge = cm*cm*wm + 2*cm*cp*wmp + cp*cp*wp
    spatial_terms = q*q / ff.M_N_GEV**2 * np.array([f1*f1/2*wd, (f1+f2)**2/8*ws, -f1*(f1+f2)/2*wsd])
    nuclear_transverse = float(np.sum(spatial_terms))
    if nuclear_charge <= 0 or nuclear_transverse < -1e-13:
        raise ArithmeticError('Nonpositive nuclear contraction')
    scale = MA * GPROD2 / (256*math.pi**3*PCHI**2*(MV**2 + 2*MA*er)**2) * CONVERT
    paper = scale * tensor['L00'] * wm
    temporal = scale * tensor['L00'] * nuclear_charge
    full = scale * (tensor['LC'] * nuclear_charge + tensor['LT'] * nuclear_transverse)
    # Difference evaluated directly to avoid subtracting two nearly equal cross sections.
    change = (tensor['deltaLC'] + tensor['LT'] * nuclear_transverse/nuclear_charge) / tensor['L00'] if tensor['phase_open'] else None
    return {
        'benchmark': name, 'ms_keV': ms_keV, 'delta_m_MeV': gap_MeV,
        'ER_keV': recoil_keV, 'Q_A_GeV': q, 'response_sampling': source,
        'phase_space_open': tensor['phase_open'],
        'paper_cm2_per_keV': paper, 'time_only_cm2_per_keV': temporal,
        'full_candidate_cm2_per_keV': full,
        'time_over_paper': temporal/paper if paper > 0 else None,
        'full_over_paper': full/paper if paper > 0 else None,
        'full_over_time': 1+change if change is not None else None,
        'full_over_time_minus_1_ppm': 1e6*change if change is not None else None,
        'longitudinal_relative_ppm': 1e6*tensor['deltaLC']/tensor['L00'] if tensor['phase_open'] else None,
        'transverse_relative_ppm': 1e6*tensor['LT']*nuclear_transverse/(tensor['L00']*nuclear_charge) if tensor['phase_open'] else None,
        'F1_over_3': f1, 'F2_over_3': f2, 'cM': cm, 'cPhiPP': cp,
        'R_M': wm, 'R_charge': nuclear_charge, 'R_transverse': nuclear_transverse,
        **{key+'_GeV2': tensor[key] for key in ('L00','ReL0L','LLL','LC','LT','deltaLC')},
    }


def validate_numerics(q, response, c0):
    checks = []
    for name, ms_keV, gap_MeV in BENCHMARKS:
        low, high = endpoints(ms_keV*1e-6)
        for er in (low+.1, 200., 267., 269., 546., high-.1):
            base = integrate(er, ms_keV*1e-6, gap_MeV*1e-3, ORDER, True)
            fine = integrate(er, ms_keV*1e-6, gap_MeV*1e-3, FINE)
            errors = {key: abs(base[key]/fine[key]-1) for key in ('L00','ReL0L','LLL','LC','LT')}
            if max(errors.values()) > 1e-6:
                raise ArithmeticError(f'Quadrature did not converge: {name}, {er}: {errors}')
            if base['trace_vs_spinor_max_rel'] > 2e-12 or base['kinematics_max_abs_GeV'] > 2e-10:
                raise ArithmeticError('Independent current/kinematics check failed')
            checks.append({'benchmark': name, 'ER_keV': er, 'quadrature_max_rel': max(errors.values()),
                           **{key: base[key] for key in ('trace_vs_spinor_max_rel','kinematics_max_abs_GeV','conservation_max_abs_GeV','scalar_mass_shell_max_abs_GeV2')}})
    # Native Mathematica absolute paper-style spectra: all four benchmarks, three anchors.
    repo = HERE.parents[1]
    original = repo/'research/afh_default_density_xe131/output/full_dsigma_mathematica/mathematica_full_dsigma_xe131.csv'
    crosschecks = []
    for row in csv_read(original):
        er = float(row['ER_keV'])
        if er not in (200., 300., 500.):
            continue
        name, ms_keV, gap_MeV = next(b for b in BENCHMARKS if row['benchmark'].startswith(b[0]))
        tensor = integrate(er, ms_keV*1e-6, gap_MeV*1e-3)
        qr = math.sqrt(er*1e-6*(2*MA+er*1e-6))
        calculated = assemble(er, tensor, response(qr), name, ms_keV, gap_MeV, 'PCHIP_anchor')
        # Actual native column is checked by caller before main execution.
        expected = float(row['dsigma_cm2_per_keV'])
        error = abs(calculated['paper_cm2_per_keV']/expected-1) if expected else 0.
        crosschecks.append({'benchmark':name,'ER_keV':er,'relative_error':error,'native_cm2_per_keV':expected,'new_cm2_per_keV':calculated['paper_cm2_per_keV']})
    if len(crosschecks) != 12 or max(c['relative_error'] for c in crosschecks) > 2e-7:
        raise ArithmeticError(f'Native absolute baseline comparison failed: {crosschecks}')
    return checks, crosschecks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--validate-only', action='store_true')
    args = parser.parse_args()
    started = time.perf_counter()
    q, physical, response, c0 = load_nuclear()
    checks, crosschecks = validate_numerics(q, response, c0)
    print('Numerical checks passed:', len(checks), 'convergence anchors;', len(crosschecks), 'native absolute cross sections', flush=True)
    if args.validate_only:
        print(json.dumps({'convergence_max':max(x['quadrature_max_rel'] for x in checks),'native_max':max(x['relative_error'] for x in crosschecks)},indent=2))
        return
    OUT.mkdir(exist_ok=True)
    all_rows = []
    intervals = {}
    # Use exact native q nodes so no response interpolation biases diffraction dips.
    energies = 1e6*q*q / (np.sqrt(MA*MA + q*q) + MA)
    for name, ms_keV, gap_MeV in BENCHMARKS:
        lo, hi = endpoints(ms_keV*1e-6)
        intervals[name] = [lo, hi]
        selected = np.where((energies > lo) & (energies < hi))[0]
        samples = [(float(energies[i]), physical[i], 'exact_native_q_node') for i in selected]
        for er in (lo, lo+.01, lo+.1, 200., 267., 269., 300., 500., 546., hi-.1, hi-.01, hi):
            qr = math.sqrt(er*1e-6*(2*MA+er*1e-6))
            samples.append((er, response(qr), 'PCHIP_anchor_or_endpoint'))
        rows = [assemble(er, integrate(er, ms_keV*1e-6, gap_MeV*1e-3), nuclear, name, ms_keV, gap_MeV, source)
                for er, nuclear, source in sorted(samples, key=lambda x:x[0])]
        all_rows.extend(rows)
        print(name, len(rows), 'recoil points complete', flush=True)
    csv_write(OUT/'differential_cross_sections.csv', all_rows)
    csv_write(OUT/'convergence_checks.csv', checks)
    csv_write(OUT/'native_baseline_comparison.csv', crosschecks)
    anchors = [r for r in all_rows if r['ER_keV'] in (200.,267.,269.,300.,500.)]
    csv_write(OUT/'selected_energy_comparison.csv', anchors)
    import plot_comparison
    plot_comparison.make_figures(all_rows)
    import validate_outputs
    validate_outputs.main()
    independent = json.loads((OUT/'independent_validation.json').read_text())
    manifest = {
        'status':'NUMERICALLY_CHECKED_LEADING_ONE_BODY_FULL_CURRENT_CANDIDATE',
        'full_bound_nuclear_current_validated':False,
        'paper_benchmark_source':'research/afh_default_density_xe131/output/full_dsigma_mathematica/mathematica_full_dsigma_xe131_metadata.json',
        'local_base_commit':'7456b7743adbed46b09b430ea2a54e8d0545aaa6',
        'remote_main_observed':'7bd2c59f3bf48979c2e9046fbba847dd28f8c26a',
        'matching_source_commit':'07e044e76bdfac2cd5559659fa2d458d49b97255',
        'parameters':dict(mchi_GeV=MCHI,mA_GeV=MA,mV_GeV=MV,v_km_s=SPEED,g2=G2,coupling_product_squared=GPROD2),
        'mass_scheme':'A*u approximation, identical to archived four-benchmark absolute cross-section comparison',
        'form_factors':'isoscalar_zexp central diagnostic; divide F1V and F2V by F1V(0)=3 because gVN=3*gVq',
        'nuclear_normalization':dict(C0=c0,raw_to_physical_factor=4*math.pi*c0,R_M_at_zero=physical[0,0]),
        'width':'before emission zero; after emission constant pole width; Dirac, real scalar, pure scalar, sole decay chi2->chi1+s',
        'widths_keV':{name:1e6*eq6.chi2_width_dirac_scalar(MCHI,ms*1e-6,gap*1e-3,G2) for name,ms,gap in BENCHMARKS},
        'recoil_intervals_keV':intervals,
        'quadrature':dict(base=ORDER,high=FINE,W2='threshold-u2',phi='uniform periodic normalized average'),
        'number_of_recoil_points':len(all_rows),
        'maximum_quadrature_relative_difference':max(x['quadrature_max_rel'] for x in checks),
        'maximum_native_absolute_baseline_relative_difference':max(x['relative_error'] for x in crosschecks),
        'maximum_trace_vs_spinor_relative_difference':max(x['trace_vs_spinor_max_rel'] for x in checks),
        'maximum_independent_integrated_tensor_relative_difference':max(max(x['relative_errors'].values()) for x in independent['independent_upstream_tensor_checks']),
        'maximum_independent_six_channel_contraction_relative_difference':max(x['six_channel_contraction_relative_error'] for x in independent['independent_upstream_tensor_checks']),
        'response_interpolation':'Main curves sampled at exact native q nodes; PCHIP only at requested anchors and endpoint zoom nodes; no extrapolation',
        'environment':dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,matplotlib=plot_comparison.matplotlib.__version__),
        'elapsed_seconds':time.perf_counter()-started,
        'limitations':['Leading one-body NR truncation; bound-nucleus covariant/AFH amplitude matching and interaction currents remain open.',
                       'Signed transverse SigmaPrimeDelta particle-side matching remains provisional.',
                       'Finite-Q2 nucleon form factors are diagnostic central values without propagated covariance.',
                       'Fixed speed Xe-131; not a halo average, natural-xenon sum or detector-level spectrum.',
                       'Native q grid finite spacing; extrema reported as sampled extrema, not continuous optimizations.'],
    }
    # The B-normalized analysis consumes this manifest and has its own checksums.
    manifest['sha256'] = {p.relative_to(HERE).as_posix(): hash_file(p) for p in sorted(HERE.rglob('*'))
                          if p.is_file() and '__pycache__' not in p.parts
                          and not p.is_relative_to(HERE/'ABCD') and p != OUT/'run_manifest.json'}
    native_baseline = HERE.parents[1]/'research/afh_default_density_xe131/output/full_dsigma_mathematica/mathematica_full_dsigma_xe131.csv'
    manifest['native_absolute_baseline_sha256'] = hash_file(native_baseline)
    (OUT/'run_manifest.json').write_text(json.dumps(manifest,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({k:manifest[k] for k in ('status','number_of_recoil_points','maximum_quadrature_relative_difference','maximum_native_absolute_baseline_relative_difference','elapsed_seconds')},indent=2),flush=True)


if __name__ == '__main__':
    main()
