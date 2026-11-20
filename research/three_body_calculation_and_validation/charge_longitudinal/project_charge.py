"""Target-rest-frame Xe-131 charge projection, in the reduced Eq. (6) measure."""
from __future__ import annotations

import math
from pathlib import Path
import sys

import numpy as np

CALC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CALC))
import eq6_kernel as eq6
from isotope_mass_schemes import isotope_mass_GeV
from phase_space_convergence import _stable_build_point

MCHI = 1000.
MS = 300e-6
GAP = 450e-6
MA = isotope_mass_GeV(131, 'nist_nuclear')
SPEED = 776.
G2 = 1.
MV = 10.
TRACE_COLUMNS = ('L00_GeV2', 'Re_L0L_GeV2', 'LL_GeV2', 'LC_GeV2',
                 'LC_a_GeV2', 'LC_b_GeV2', 'LC_ab_interference_GeV2')


def point_traces(point, delta_w2, pole_width):
    """Spin-average two upper-index projections and the two radiation orderings."""
    heavy = MCHI + GAP
    mass_term = heavy * eq6.ID4
    gamma_time = eq6.GAMMA[0]
    gamma_long = sum(weight * gamma for weight, gamma in zip(point.q_A[1:] / point.Q_A, eq6.GAMMA[1:]))
    directions = np.stack((gamma_time, gamma_long))
    den_before = MS**2 - GAP * (2 * MCHI + GAP) - 2 * eq6.dot(point.p, point.k_s)
    den_after = (MS - GAP) * (2 * MCHI + MS + GAP) + delta_w2 + 1j * heavy * pole_width
    before = directions @ ((eq6.slash(point.p - point.k_s) + mass_term) / den_before)
    after = ((eq6.slash(point.K) + mass_term) / den_after) @ directions
    time, longitudinal = before + after
    ratio = point.E_R / point.Q_A
    before_c = before[0] - ratio * before[1]
    after_c = after[0] - ratio * after[1]
    vertices = np.stack((time, longitudinal, before_c + after_c, before_c, after_c))
    left = gamma_time @ (eq6.slash(point.p_prime) + MCHI * eq6.ID4)
    right = (eq6.slash(point.p) + MCHI * eq6.ID4) @ gamma_time
    images = (left @ vertices @ right) * .5
    squares = np.einsum('aij,aij->a', images, vertices.conj()).real
    mixed = np.vdot(vertices[1], images[0]).real
    diagram_cross = 2 * np.vdot(vertices[4], images[3]).real
    return np.array([squares[0], mixed, squares[1], squares[2], squares[3], squares[4], diagram_cross])


def integrate(recoil_keV, speed=SPEED, order=(12, 6, 4), pole=False):
    """Fixed recoil and speed; disallow on-shell production in this off-shell study."""
    if not math.isfinite(recoil_keV) or recoil_keV < 0 or not 0 < speed < eq6.C_KM_S:
        raise ValueError('Require finite nonnegative recoil and subluminal positive speed')
    if len(order) != 3 or min(order) < 2 or order[2] < 4:
        raise ValueError('Require at least two Gauss nodes and four periodic azimuths')
    recoil = recoil_keV * 1e-6
    beta = speed / eq6.C_KM_S
    energy = MCHI / math.sqrt(1 - beta**2)
    momentum = energy * beta
    spatial_q = math.sqrt(recoil * (2 * MA + recoil))
    ratio = math.sqrt(recoil / (2 * MA + recoil))
    threshold = (MCHI + MS)**2
    span = 2 * (momentum * spatial_q - (energy + MA) * recoil) - MS * (2 * MCHI + MS)
    pole_gap_w2 = (GAP - MS) * (2 * MCHI + GAP + MS) - span
    if pole_gap_w2 <= 0:
        raise ValueError('On-shell chi2 accessible: outside the off-shell benchmark')
    is_open = span > 2 * math.ulp(threshold)
    values = np.zeros(len(TRACE_COLUMNS))
    if is_open:
        width = eq6.chi2_width_dirac_scalar(MCHI, MS, GAP, G2) if pole else 0.
        nodes_w, weights_w = eq6._cached_leggauss(order[0])
        nodes_z, weights_z = eq6._cached_leggauss(order[1])
        azimuths = 2 * math.pi * (np.arange(order[2]) + .5) / order[2]
        for node_w, weight_w in zip(nodes_w, weights_w):
            unit = (node_w + 1) / 2
            delta_w2 = span * unit**2
            root_lambda = math.sqrt(delta_w2 * (4 * MCHI * MS + delta_w2)) / (threshold + delta_w2)
            measure = weight_w * span * unit * root_lambda / order[2]
            for cos_theta, weight_z in zip(nodes_z, weights_z):
                for phi in azimuths:
                    point = _stable_build_point(MCHI, MS, MA, recoil, speed, delta_w2, cos_theta, phi)
                    values += measure * weight_z * point_traces(point, delta_w2, width)
    temporal, mixed, longitudinal, projected, before, after, interference = values
    mixing = -2 * ratio * mixed
    weighted_long = ratio**2 * longitudinal
    if is_open:
        if temporal <= 0 or projected <= 0 or longitudinal < 0 or mixed**2 > temporal * longitudinal * (1 + 2e-12):
            raise ArithmeticError('Invalid integrated Gram tensor')
        if not (math.isclose(projected, temporal + mixing + weighted_long, rel_tol=2e-12)
                and math.isclose(projected, before + after + interference, rel_tol=2e-12)):
            raise ArithmeticError('Projected trace did not close under both decompositions')
    return {
        'ER_keV': recoil_keV, 'v_km_s': speed, 'phase_space_open': is_open,
        'width': 'pole' if pole else 'zero', 'r_ER_over_Q': ratio,
        'pole_clearance_keV': 1e6 * pole_gap_w2 / (MCHI + GAP + math.sqrt(threshold + span))
        if threshold + span >= 0 else None,
        **dict(zip(TRACE_COLUMNS, map(float, values))),
        'mix_0L_GeV2': mixing, 'LL_weighted_GeV2': weighted_long,
        'LC_over_L00': projected / temporal if is_open else None,
        'LC_over_L00_minus_one': (mixing + weighted_long) / temporal if is_open else None,
        'diagram_interference_fraction': interference / projected if is_open else None,
    }
