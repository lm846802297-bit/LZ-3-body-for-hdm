(* Xe-131 elastic vector-vector benchmark. Run with wolframscript -file. *)
base = DirectoryName[DirectoryName[$InputFileName]];
Get[FileNameJoin[{base, "dmformfactor-V6.m"}]];

(* All energies are in GeV unless explicitly labelled otherwise. *)
a = 131; jA = 3/2; mN = 0.938272; mA = a mN;
mChi = 1000.; mV = 10.; gChi = 1.; gN = 10^-4;
speedKms = 500.; beta = speedKms dmformfactor`KilometerPerSecond;
referenceMass = 246.2; recoilValues = {1., 5., 20., 50., 100.};
dmformfactor`ZeroCoeffs[];
dmformfactor`SetJChi[1/2];
dmformfactor`SetMChi[mChi dmformfactor`GeV];
dmformfactor`SetIsotope[54, a, "default", "default"];
dmformfactor`SetHelm[False];
response = dmformfactor`ResponseNuclear[Global`y, 1, 0, 0];
oscillator = 5.0677 Sqrt[41.467/(45. a^(-1/3)-25. a^(-2/3))];
wzero = N[response /. Global`y -> 0];
rawRzero = N[4 (4 Pi/(2 jA + 1)) wzero];

(* Equal p and n couplings: direct nuclear density is 2 times the AFH isoscalar density. *)
evaluate[er_?NumericQ] := Module[{q2, yval, w, rRaw, rNormalized, c, afh, direct, normalized},
 q2 = 2 mA er 10^-6;
 yval = q2 oscillator^2/4;
 w = N[response /. Global`y -> yval];
 rRaw = 4 (4 Pi/(2 jA + 1)) w;
 rNormalized = a^2 w/wzero;
 (* AFH divides its dimensionless input by the fixed scale 246.2 GeV squared. *)
 c = gChi gN referenceMass^2/(mV^2+q2);
 dmformfactor`ZeroCoeffs[];
 dmformfactor`SetCoeffsNonrel[1, c, "p"];
 dmformfactor`SetCoeffsNonrel[1, c, "n"];
 afh = N[dmformfactor`DiffCrossSection[er, beta] dmformfactor`GeV^3 /. dmformfactor`GeV -> 1];
 direct = N[mA (gChi gN)^2 rRaw/(2 Pi beta^2 (mV^2+q2)^2)];
 normalized = N[mA (gChi gN)^2 rNormalized/(2 Pi beta^2 (mV^2+q2)^2)];
 {er, afh, direct, direct/afh-1, normalized, normalized/afh-1}
];
rows = evaluate /@ recoilValues;
Print["mass_GeV=",mA,"; beta=",beta,"; raw_R0=",rawRzero,"; A2=",a^2];
Print["{ER_keV, AFH_GeV^-3, direct_raw_GeV^-3, direct_raw_rel_diff, direct_normalized_GeV^-3, normalized_rel_diff}"];
Scan[Print[InputForm[#]] &, rows];
If[!And @@ (NumericQ /@ Flatten[rows]) || Max[Abs[rows[[All, 4]]]] > 10^-8,
 Print["FAIL: direct raw response does not match AFH"],
 Print["PASS: raw response matches AFH at all tested points."]
];
