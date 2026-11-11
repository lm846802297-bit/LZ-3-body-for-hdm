# AFH default Xe-131 nuclear response

Adopt the original AFH/DMFormFactor default density matrix for Xe-131, not GCN5082 or JJ55.

Reference: N. Anand, A. L. Fitzpatrick, and W. C. Haxton, arXiv:1308.6288, Sections 5 and 7.2.

AFH documents SetIsotope[Z,A,bFM,filename]. The AFH default density matrix and default oscillator length are selected by:

    SetIsotope[54,131,"default","default"]

The isoscalar charge response is ResponseNuclear[y,1,0,0] = W_M^{00}(y), with y=(q b_A/2)^2 and R_131(q)=4 pi/(2J+1) W_M^{00}(y).

The AFH default oscillator prescription is b_A[fm]=sqrt(41.467/(45 A^(-1/3)-25 A^(-2/3))). The required normalization check is R_131(0)=131^2=17161.

## Reproduction

Obtain the official AFH DMFormFactor Version 6.0 archive from https://www.ocf.berkeley.edu/~nanand/software/dmformfactor/ and extract dmformfactor.m. Put it beside the runner or set DMFormFactorPath. Run with wolframscript.

## Provenance

The existing xe131_GCN_WM.csv and xe131_JJ55_WM.csv files were generated from the separate dmscatter target library. They are not AFH original default-density results and must not be relabeled as such.

The AFH software archive is a binary ZIP. This execution environment can inspect the AFH paper and software landing page but cannot retrieve that ZIP binary or run the user's local Mathematica kernel. Numerical AFH-default CSV output must only be added after the official package is supplied and the A^2 normalization check passes.

This stage is the nuclear response only. The three-body cross section, four Figure 2 benchmarks, isotope sum, and halo average are subsequent stages.
