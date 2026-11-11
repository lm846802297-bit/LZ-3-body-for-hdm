(* AFH-native Xe-131 default-density response runner. *)
(* Requires official DMFormFactor v6.0 package: dmformfactor.m *)
scriptDir = DirectoryName[$InputFileName];
envPath = Environment["DMFormFactorPath"];
packagePath = If[StringQ[envPath] && envPath =!= "", envPath, FileNameJoin[{scriptDir, "dmformfactor.m"}]];
If[!FileExistsQ[packagePath], Print["ERROR: official AFH dmformfactor.m not found: ", packagePath]; Exit[2]];
Get[packagePath];
A = 131; Z = 54; J = 3/2;
mA = 131.0*0.93149410242; (* recoil-coordinate convention only *)
fmToGeVInv = 5.067730716;
qMin = 0.0; qMax = 0.60; dq = 0.00025;
bFM = Sqrt[41.467/(45.0 A^(-1.0/3.0) - 25.0 A^(-2.0/3.0))];
bGeVInv = bFM*fmToGeVInv;
SetIsotope[Z, A, "default", "default"];
wmExpr = ResponseNuclear[y, 1, 0, 0];
If[wmExpr === $Failed || wmExpr === Null, Print["ERROR: AFH ResponseNuclear did not return W_M^{00}."]; Exit[3]];
qGrid = N[Range[0, Round[(qMax - qMin)/dq]]*dq, 16];
rows = Table[Module[{q = qGrid[[i]], yy, wm, response, er},
  yy = (q*bGeVInv/2.0)^2;
  wm = N[wmExpr /. y -> yy, 30];
  response = N[4.0 Pi/(2.0 J + 1.0)*wm, 30];
  er = (Sqrt[mA^2 + q^2] - mA)*10^6;
  {q, yy, wm, response, response/A^2, er}
], {i, Length[qGrid]}];
r0 = rows[[1, 4]];
normalizationRelErr = Abs[r0/A^2 - 1.0];
If[!NumericQ[r0] || normalizationRelErr > 10^-8,
  Print["ERROR: AFH zero-momentum normalization failed."];
  Print["R(0) = ", N[r0, 16], "; A^2 = ", A^2, "; relative error = ", N[normalizationRelErr, 8]];
  Exit[4];
];
csvPath = FileNameJoin[{scriptDir, "afh_default_xe131_WM00.csv"}];
metaPath = FileNameJoin[{scriptDir, "afh_default_xe131_metadata.txt"}];
Export[csvPath, Prepend[rows, {"q_GeV", "y=(q*b/2)^2", "W_M00_isoscalar", "R_A=4Pi/(2J+1)*W_M00", "R_A_over_A2", "ER_keV_recoil_coordinate"}], "CSV"];
metadata = {
  "reference = Anand, Fitzpatrick, Haxton, arXiv:1308.6288, Sections 5 and 7.2",
  "package = official DMFormFactor v6.0",
  "density_matrix = AFH original default; SetIsotope[54,131,...,default]",
  "oscillator_length = AFH default; SetIsotope[...,default,...]",
  "response = ResponseNuclear[y,1,0,0] = W_M^{00}",
  "J_A = 3/2", "A = 131", "Z = 54",
  "b_A_fm = " <> ToString[InputForm[N[bFM, 16]]],
  "b_A_GeV_inverse = " <> ToString[InputForm[N[bGeVInv, 16]]],
  "R_A_0 = " <> ToString[InputForm[N[r0, 16]]],
  "A_squared = 17161",
  "relative_normalization_error = " <> ToString[InputForm[N[normalizationRelErr, 8]]],
  "q_grid_GeV = 0 to 0.6 in 0.00025 steps",
  "recoil_energy_mass_convention = m_A = 131*0.93149410242 GeV; this only maps q to E_R"
};
Export[metaPath, StringRiffle[metadata, "\n"] <> "\n", "Text"];
Print["AFH Xe-131 default-density response completed."];
Print["b_A = ", N[bFM, 10], " fm"];
Print["R_A(0) = ", N[r0, 16], "; A^2 = ", A^2];
Print["relative normalization error = ", N[normalizationRelErr, 8]];
Print["CSV: ", csvPath]; Print["Metadata: ", metaPath];
