#!/usr/bin/env python3
"""Lightweight integrity checks for the archived AFH natural-xenon halo fold."""
from __future__ import annotations
import csv, json, math
from pathlib import Path

HERE=Path(__file__).resolve().parent
R=HERE/"results"
I=HERE/"input"

def read(path):
    with path.open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))

weights=read(I/"natural_xenon_isotope_weights.csv")
resp=read(I/"afh_response_samples.csv")
iso=read(R/"isotope_halo_contributions_compact.csv")
rates=read(R/"natural_xenon_halo_rates.csv")

available=[r for r in weights if r["AFH_default_density_available"].lower()=="true"]
coverage=sum(float(r["natural_atom_fraction"]) for r in available)
assert math.isclose(coverage,0.998158,rel_tol=0,abs_tol=1e-12)
assert len(resp)==28
assert len(iso)==98
assert len(rates)==14

# AFH defines its response argument using the spatial momentum transfer q.
# The archived samples use the exact mass-shell value; q_NR=sqrt(2*m_A*E_R)
# is only the small-recoil approximation.
metadata=json.loads((R/"metadata.json").read_text(encoding="utf-8"))
assert metadata["response_q_convention"]=="exact_spatial"
weights_by_A={int(r["A"]):r for r in weights}
for sample in resp:
    A=int(sample["A"])
    ER=float(sample["ER_keV"])*1e-6
    atom_mass=float(weights_by_A[A]["atomic_mass_u"])
    mA=(atom_mass-54*0.000548579909065)*0.93149410242
    q_nr=math.sqrt(2*mA*ER)
    q_exact=math.sqrt(2*mA*ER+ER*ER)
    q_sample=float(sample["q_response_GeV"])
    assert math.isclose(q_sample,q_exact,rel_tol=0,abs_tol=2e-10)
    assert not math.isclose(q_sample,q_nr,rel_tol=0,abs_tol=2e-10)

groups={}
for row in iso:
    key=(row["benchmark"],row["ER_keV"],row["halo_model"])
    groups.setdefault(key,[]).append(row)
assert len(groups)==14
for key,rows in groups.items():
    assert len(rows)==7
    summed=sum(float(r["rate_contribution_events_kg_day_keV"]) for r in rows)
    stored=next(r for r in rates if (r["benchmark"],r["ER_keV"],r["halo_model"])==key)
    assert math.isclose(summed,float(stored["rate_events_kg_day_keV"]),rel_tol=2e-10,abs_tol=1e-300)

expected={
    "red_ms200_dm1":{128,129,130,131,132,134,136},
    "green_ms300_dm1":{136},
    "blue_ms300_dm10":{136},
    "black_ms360_dm1":set(),
}
for benchmark,opened in expected.items():
    rows=[r for r in iso if r["benchmark"]==benchmark and
          float(r["ER_keV"])==101.0 and r["halo_model"]=="shm_cutoff"]
    actual={int(r["A"]) for r in rows if r["open"].lower()=="true"}
    assert actual==opened,(benchmark,actual,opened)

kc=read(R/"kernel_order_crosschecks.csv")
sc=read(R/"speed_quadrature_crosschecks.csv")
assert max(abs(float(r["rel_884_to_16168"])) for r in kc)<3e-4
assert max(abs(float(r["relative_difference_nv64_to_nv32"])) for r in sc)<1e-5
print(f"PASS: {len(iso)} isotope rows, {len(rates)} rate rows, "
      f"AFH abundance coverage={coverage:.6f}, "
      f"max kernel-grid delta={max(abs(float(r['rel_884_to_16168'])) for r in kc):.3e}, "
      f"max speed-grid delta={max(abs(float(r['relative_difference_nv64_to_nv32'])) for r in sc):.3e}, "
      f"AFH response q={metadata['response_q_convention']}")
