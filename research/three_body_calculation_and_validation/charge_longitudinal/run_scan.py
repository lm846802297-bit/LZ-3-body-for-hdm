"""Recompute the two interferences and compare to the fixed 450-keV spinor archive."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
import platform

import matplotlib
import numpy as np
import scipy
from scipy.interpolate import PchipInterpolator

import project_charge as charge

HERE = Path(__file__).resolve().parent
INPUT = HERE / 'input'
OUT = HERE / 'results'
REFERENCE = INPUT / 'xe131_fixed_benchmark_absolute_dsigma_450keV.csv'
METADATA = INPUT / 'xe131_fixed_benchmark_absolute_dsigma_450keV_metadata.json'
NATIVE = HERE.parents[1] / 'afh_default_density_xe131/output/phi_response_native/afh_default_xe131_M_PhiPP_native.csv'
ORDER = (12, 6, 4)
FINE = (24, 12, 8)
GEV_TO_CM2_PER_KEV = 3.893793721e-34
INPUT_HASHES = {
    REFERENCE: 'af963a90e40bf0e68d2e7df171c0b1ba930fb63732d596ff64d2261deab76285',
    METADATA: 'a03ff43f23b43fa765d162632835b9c9bc757b862d40aaae51571e9d3896201e',
    NATIVE: 'b1b65708cd103058c3bcaea50bf65550d5671a88e97000b94f2536fbc60a59ff',
}


def digest(path):
    data = path.read_bytes()
    if path.suffix != '.png':
        data = data.replace(b'\r\n', b'\n')
    return hashlib.sha256(data).hexdigest()


def read_csv(path):
    with path.open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


def save_csv(path, rows):
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, rows[0], lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def combine(row, reference, response):
    recoil = row['ER_keV'] * 1e-6
    spatial_q = math.sqrt(recoil * (2 * charge.MA + recoil))
    transfer = -2 * charge.MA * recoil
    beta = row['v_km_s'] / charge.eq6.C_KM_S
    momentum = charge.MCHI * beta / math.sqrt(1 - beta**2)
    prefactor = charge.MA / (256 * math.pi**3 * momentum**2 * (charge.MV**2 - transfer)**2)
    wm, wphi, winter = response(spatial_q)
    result = {key: 0. for key in ('dsigma_ch_GeVminus3', 'dsigma_ch_cm2_per_keV', 'dsigma_point_M_cm2_per_keV', 'dsigma_temporal_point_M_cm2_per_keV')}
    result.update({key: None for key in ('full_over_point_M', 'full_over_finite_M', 'full_over_temporal_point_M')})
    if row['phase_space_open']:
        f1, f2 = float(reference['F1V']), float(reference['F2V'])
        cphi = spatial_q**2 * (f1 + 2 * f2) / (4 * .938918**2)
        cm = f1 - cphi / 2
        point_m = 3.**2 * wm
        finite_m = cm**2 * wm
        nuclear = finite_m + 2 * cm * cphi * winter + cphi**2 * wphi
        result['dsigma_ch_GeVminus3'] = prefactor * row['LC_GeV2'] * nuclear
        scale = prefactor * GEV_TO_CM2_PER_KEV
        result['dsigma_ch_cm2_per_keV'] = scale * row['LC_GeV2'] * nuclear
        result['dsigma_point_M_cm2_per_keV'] = scale * row['LC_GeV2'] * point_m
        result['dsigma_temporal_point_M_cm2_per_keV'] = scale * row['L00_GeV2'] * point_m
        result['full_over_point_M'] = nuclear / point_m
        result['full_over_finite_M'] = nuclear / finite_m
        result['full_over_temporal_point_M'] = result['dsigma_ch_cm2_per_keV'] / result['dsigma_temporal_point_M_cm2_per_keV']
    return {'Q_A_GeV': spatial_q, 't_A_GeV2': transfer, 'prefactor_GeVminus5': prefactor, **result}


def main():
    if any(digest(path) != expected for path, expected in INPUT_HASHES.items()):
        raise ValueError('A pinned input hash changed; check the benchmark before comparison')
    references = read_csv(REFERENCE)
    native = read_csv(NATIVE)
    response_keys = ('R_M_physical_equal_pn', 'R_PhiPP_physical_equal_pn', 'R_MPhiPP_physical_equal_pn')
    response = PchipInterpolator([float(item['q_GeV']) for item in native],
                                 [[float(item[key]) for key in response_keys] for item in native], extrapolate=False)
    comparisons = {'L00_GeV2': 'L00_GeV2', 'LC_GeV2': 'L_C_GeV2', 'LC_over_L00_minus_one': 'L_C_over_L00_minus_one',
                   'dsigma_ch_cm2_per_keV': 'full_charge_cm2_per_keV', 'full_over_point_M': 'full_charge_over_pointlike_M'}
    errors = dict.fromkeys(comparisons, 0.)
    rows = []
    for reference in references:
        row = charge.integrate(float(reference['ER_keV']), order=ORDER)
        if row['phase_space_open'] != (reference['phase_space_open'] == 'True'):
            raise ArithmeticError(f"Mismatched kinematic boundary at {row['ER_keV']} keV")
        row.update(combine(row, reference, response))
        if row['phase_space_open']:
            for key, archived in comparisons.items():
                errors[key] = max(errors[key], abs(row[key] / float(reference[archived]) - 1))
        rows.append(row)
    if max(errors.values()) > 5e-7:
        raise ArithmeticError(f'Spinor archive comparison failed: {errors}')
    anchors = []
    refinement = {}
    for recoil in (110., 200., 267., 324., 546., 652.):
        central = next(row for row in rows if row['ER_keV'] == recoil)
        fine = charge.integrate(recoil, order=FINE)
        refinement[recoil] = max(abs(fine[key] / central[key] - 1) for key in charge.TRACE_COLUMNS)
        anchors.extend([fine, charge.integrate(recoil, order=FINE, pole=True)])
    if max(refinement.values()) > 2e-8:
        raise ArithmeticError(f'Quadrature comparison failed: {refinement}')
    for recoil in (200., 267.):
        anchors.append(charge.integrate(recoil, speed=750., order=FINE))
    open_rows = [row for row in rows if row['phase_space_open']]
    if len(rows) != 299 or len(open_rows) != 297:
        raise ArithmeticError('Unexpected recoil grid')
    OUT.mkdir(exist_ok=True)
    save_csv(OUT / 'weights.csv', rows)
    save_csv(OUT / 'controls.csv', anchors)
    from plot_weights import make_figures
    make_figures(OUT, rows)
    manifest = {
        'scope': 'Xe-131, coherent charge sector only; no halo or detector fold',
        'reference_commit': 'c5bfcf6c5494d036b078af8299a2fca2e86248ce', 'reference_run': 44324056946,
        'artifact_id': 14437568189, 'upstream_zip_bytes': 170529,
        'upstream_zip_sha256': '6f4267d1f0bb5536e5a403b84ec19e778fd42f8c94f84ec1735cbc4e045869a9',
        'baseline_main': '7456b7743adbed46b09b430ea2a54e8d0545aaa6',
        'mass_scheme': '130.90508406 u minus 54 electron masses, no electronic binding correction',
        'parameters': {'mA_GeV': charge.MA, 'mchi_GeV': charge.MCHI, 'ms_keV': 300, 'delta_m_keV': 450,
                       'v_km_s': charge.SPEED, 'mV_GeV': charge.MV, 'coupling_product_squared': 1, 'g2_width': charge.G2},
        'central_width': 'zero', 'pole_width_control_keV': 1e6 * charge.eq6.chi2_width_dirac_scalar(charge.MCHI, charge.MS, charge.GAP, charge.G2),
        'quadrature': {'W2': 'threshold u^2 Gauss', 'z': 'Gauss on [-1,1]', 'phi': 'uniform periodic mean', 'orders': ORDER, 'anchor_orders': FINE},
        'rows': len(rows), 'open': len(open_rows), 'endpoints_keV': [rows[0]['ER_keV'], rows[-1]['ER_keV']],
        'minimum_sampled_pole_clearance_keV': min(row['pole_clearance_keV'] for row in open_rows),
        'max_relative_error_vs_reference_open_grid': errors, 'max_relative_refinement_over_seven_components': refinement,
        'correction_range_ppm_open_grid': [operation(row['LC_over_L00_minus_one'] * 1e6 for row in open_rows) for operation in (min, max)],
        'runtime': {'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__, 'matplotlib': matplotlib.__version__},
        'hash_policy': 'SHA-256, canonical LF for text, raw bytes for PNG',
        'sha256': {path.name: digest(path) for path in [*INPUT_HASHES, Path(__file__), HERE/'project_charge.py', HERE/'plot_weights.py',
                   charge.CALC/'eq6_kernel.py', charge.CALC/'phase_space_convergence.py', charge.CALC/'isotope_mass_schemes.py',
                   OUT/'weights.csv', OUT/'controls.csv', OUT/'charge_weights.png', OUT/'point_charge_comparison.png']},
    }
    (OUT / 'checks.json').write_text(json.dumps(manifest, indent=2, allow_nan=False) + '\n', encoding='utf-8', newline='\n')
    print(f'{len(rows)} rows, {len(open_rows)} open; reference errors: {errors}; refinement: {max(refinement.values()):.3g}')


if __name__ == '__main__':
    main()
