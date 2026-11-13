(* AFH-native Xe-131 response using the official DMFormFactor v6.0 package. *)
(* Run: wolframscript -file run_afh_default_xe131.wls *)
ClearAll["Global`*"];
scriptDir = DirectoryName[$InputFileName];
envPath = Environment["DMFormFactorPath"];
packagePath = If[StringQ[envPath] && envPath =!= "", envPath, FileNameJoin[{scriptDir, "dmformfactor-V6.m"}]];
If[!FileExistsQ[packagePath], Print["ERROR: AFH dmformfactor-V6.m not found: ", packagePath]; Exit[2]];
Get[packagePath];
A = 131; Z = 54; JA = 3/2;
mA = A*0.93149410242; (* recoil-coordinate convention only *)
fmToGeVInv = 5.0677; (* exact constant in AFH v6 source *)
qMax = 0.60; dq = 0.00025;
bFM = Sqrt[41.467/(45.0 A^(-1.0/3.0) - 25.0 A^(-2.0/3.0))];
bGeVInv = bFM*fmToGeVInv;
SetIsotope[Z, A, "default", "default"];
wmExpr = ResponseNuclear[y, 1, 0, 0];
If[wmExpr === $Failed || wmExpr === Null, Print["ERROR: AFH ResponseNuclear did not return W_M^{00}."]; Exit[3]];
qGrid = N[Range[0, Round[qMax/dq]]*dq, 16];
rows = Table[
  Module[{q = qGrid[[i]], yy, wm, rAFH, rEqualRaw, er},
    yy = (q*bGeVInv/2.0)^2;
    wm = N[wmExpr /. y -> yy, 30];
    rAFH = 4.0 Pi/(2.0 JA + 1.0)*wm;
    rEqualRaw = 4.0*rAFH;
    rEqualFormula = 16.0 Pi/(2.0 JA + 1.0)*wm;
    factor4Residual = Abs[rEqualRaw - rEqualFormula]/Max[1.0, Abs[rEqualFormula]];
    If[factor4Residual > 10^-12,
      Print["ERROR: factor-four mapping disagrees with 16 Pi W_M/(2J+1)."]; Exit[4]
    ];
    er = (Sqrt[mA^2 + q^2] - mA)*10^6;
    {q, yy, wm, rAFH, rEqualRaw, er}
  ], {i, Length[qGrid]}
];
rAFH0 = rows[[1, 4]];
expectedAFH0 = A^2/4.0;
packageNormRelErr = Abs[rAFH0/expectedAFH0 - 1.0];
If[!NumericQ[rAFH0] || packageNormRelErr > 2.0*10^-4,
  Print["ERROR: AFH W_M^{00}(0) does not match A^2/4 within rounded-matrix tolerance."];
  Print["R_AFH(0) = ", N[rAFH0, 16], "; A^2/4 = ", expectedAFH0,
    "; relative error = ", N[packageNormRelErr, 8]];
  Exit[4];
];
normalizationFactor = A^2/rows[[1, 5]];
normalizedRows = Map[Append[#, normalizationFactor*#[[5]]] &, rows];
normalizedRows = Map[Append[#, normalizationFactor*#[[5]]/A^2] &, normalizedRows];
csvPath = FileNameJoin[{scriptDir, "afh_default_xe131_WM00_mathematica.csv"}];
Export[csvPath,
  Prepend[normalizedRows, {"q_GeV", "y", "W_M00_AFH_package", "R_AFH_4Pi_over_2Jplus1",
    "R_equal_pn_raw", "ER_keV", "R_equal_pn_normalized", "R_over_A2"}], "CSV"];
metaPath = FileNameJoin[{scriptDir, "afh_default_xe131_mathematica_metadata.txt"}];
metadata = {
  "source = AFH DMFormFactor v6.0; built-in sdgXe131, 67 entries",
  "SetIsotope = SetIsotope[54,131,default,default]",
  "response = ResponseNuclear[y,1,0,0] = W_M^{00}",
  "AFH isoscalar convention: (4 Pi/(2 J_A+1))*W_M00(0) = A^2/4",
  "equal physical proton/neutron charge response = 4 * AFH isoscalar response = 16 Pi W_M00/(2 J_A+1)",
  "factor-four algebraic identity checked at every q grid point to relative tolerance 1e-12",
  "exact q=0 normalization applied only to remove rounded density-matrix offset",
  "A = 131", "Z = 54", "J_A = 3/2",
  "b_A_fm = " <> ToString[InputForm[N[bFM, 16]]],
  "b_A_GeV_inverse = " <> ToString[InputForm[N[bGeVInv, 16]]],
  "AFH_package_R0 = " <> ToString[InputForm[N[rAFH0, 16]]],
  "expected_AFH_package_R0_A2_over_4 = " <> ToString[InputForm[N[expectedAFH0, 16]]],
  "package_normalization_relative_error = " <> ToString[InputForm[N[packageNormRelErr, 8]]],
  "physical_equal_pn_R0 = " <> ToString[InputForm[N[normalizationFactor*rows[[1,5]], 16]]],
  "A_squared = " <> ToString[A^2],
  "normalization_factor = " <> ToString[InputForm[N[normalizationFactor, 16]]],
  "q_grid_GeV = 0 to 0.6 in 0.00025 steps",
  "recoil mass convention = m_A = A*0.93149410242 GeV; used only to map q to E_R"
};
Export[metaPath, StringRiffle[metadata, "\n"] <> "\n", "Text"];
Print["AFH Xe-131 default-density response completed."];
Print["b_A = ", N[bFM, 12], " fm"];
Print["AFH R(0) = ", N[rAFH0, 16], "; expected A^2/4 = ", expectedAFH0];
Print["physical equal-pn R(0) = ", N[normalizationFactor*rows[[1,5]], 16], "; A^2 = ", A^2];
Print["normalization factor = ", N[normalizationFactor, 12]];
Print["CSV: ", csvPath]; Print["Metadata: ", metaPath];

