# Spin-resolved three-body dark-matter current

**Status:** current-level diagnostic; no nucleon or AFH response matching yet.

## Purpose

The existing PR #53 code computes the spin-averaged tensor
\(L^{\mu\nu}\). To perform a true nonrelativistic operator matching, we need
the underlying 2x2 matrix in external chi1 spin space for each Lorentz
component:
\[
T_3^\mu(s',s)=\bar u_{\chi_1}(p',s')\Gamma^\mu u_{\chi_1}(p,s).
\]

This study constructs all four matrices, preserves the coherent sum of the
two scalar-emission orderings, and verifies that their spin trace reproduces
the existing \(L^{\mu\nu}\).

## Exact spin-trace identity

With the spinor normalization \(\bar u u=2m_\chi\),
\[
L^{\mu\nu}=\frac12\operatorname{Tr}_{2}
\left[T_3^\mu T_3^{\nu\dagger}\right].
\]
The regression suite compares this expression against the independent
four-dimensional Dirac trace already used in PR #53.

## Ward contraction

With the project momentum routing
\[
q_A=p-p'-k_s=(p-k_s)-p'=p-(p'+k_s),
\]
and \(r_1=p-k_s,\ r_2=p'+k_s\), the zero-width identity is
\[
q_{A\mu}\Gamma^\mu
=(m_{\chi_2}-m_{\chi_1})
\left[
\frac{\slashed r_1+m_{\chi_2}}{D_1}
-\frac{\slashed r_2+m_{\chi_2}}{D_2}
\right].
\]
The code verifies this identity after sandwiching between external chi1
spinors. It also checks that the divergence vanishes in the degenerate-mass
limit.

This identity is important for the subsequent NR matching: for a nonzero
mass splitting, the transition current is not conserved by itself. One must
not import elastic-current simplifications without checking their Ward
identities.

## Reproduction

Python 3.12+ and NumPy are required.

~~~bash
python -m unittest discover \
  -s research/three_body_spin_resolved_current \
  -p 'test_*.py' -v

python research/three_body_spin_resolved_current/spin_resolved_three_body_current.py \
  --out /tmp/spin-resolved-current.json
~~~

The workflow runs the tests and archives the reference-point diagnostics.

## Scope limits

- No nucleon Dirac-Pauli current is contracted yet.
- No AFH response coefficient is derived.
- The width-modified propagator is used for spin-trace regression; the simple
  Ward identity is tested at zero width.
- No absolute cross section, halo integral, isotope sum, detector response,
  or likelihood is included.

## Next step

Combine the spin-resolved \(T_3^\mu\) with the exact nucleon Dirac-Pauli
current, reduce the product into Pauli-spin structures, and project the
result onto the AFH multipoles. This is where the physical coefficients of
\(M,\Phi'',\Sigma',\Sigma''\), and \(\Delta\) will be determined.
