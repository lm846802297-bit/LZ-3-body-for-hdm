# Finite-\(Q^2\) charge-sector ratio

This result compares the finite-\(Q^2\) Dirac–Pauli charge response
including \(M\), \(\Phi''\), and their interference with the
\(M\)-only result for Xe-131 at the two recoil points in the calculation
script.

## Run

From any working directory, run:

```powershell
wolframscript -file "C:\path\to\main\research\afh_default_density_xe131\finite_q2_charge_response_ratio.wls"
```

The script reads the committed AFH response grid at
`../phi_response_native/afh_default_xe131_M_PhiPP_native.csv`, interpolates
the physical equal-proton/equal-neutron responses with shape-preserving cubic
Hermite interpolation (PCHIP), prints the matching coefficients and response
terms, and refreshes the result CSV and run manifest in this directory.

## Formula and scope

The reported quantity is

\[
R_{\rm charge}=
1+2\frac{c_{\Phi''}}{c_M}\frac{W_{M\Phi''}}{W_M}
+\left(\frac{c_{\Phi''}}{c_M}\right)^2\frac{W_{\Phi''}}{W_M}.
\]

The common three-body dark-matter kernel cancels in this ratio. Thus the result
is a response correction to the differential cross section, not an absolute
cross section or a halo-folded event rate. The supplied \(F_1^V\) and
\(F_2^V\) center-diagnostic values are inputs and are not refitted by the
script. The spatial nuclear current is omitted as specified for this
calculation. The same width prescription in numerator and denominator also
cancels algebraically.
