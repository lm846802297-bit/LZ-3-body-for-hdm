(* Muon decay in the massless-final-state Fermi limit; PDG Dalitz phase space. *)
ClearAll["Global`*"];
gf=1.1663787*10^-5; mass=0.1056583755; hbar=6.582119569*10^-25;
(* s=(p_e+p_nu_mu)^2, t is the second independent invariant. *)
ampSquared[s_?NumericQ]:=16 gf^2 s (mass^2-s);
gammaNumeric=NIntegrate[ampSquared[s]/(256 Pi^3 mass^3),{s,0,mass^2},{t,0,mass^2-s},WorkingPrecision->MachinePrecision,PrecisionGoal->10];
gammaAnalytic=gf^2 mass^5/(192 Pi^3);
tau=hbar/gammaNumeric;
Print["numeric width GeV=",gammaNumeric];Print["PDG tree-level width GeV=",N[gammaAnalytic,16]];
Print["relative difference=",gammaNumeric/gammaAnalytic-1];Print["tree-level lifetime s=",tau];
If[Abs[gammaNumeric/gammaAnalytic-1]>10^-10,Exit[1]];Exit[0];
