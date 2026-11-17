(* Native AFH v6.0 Xe-131 response export: M, Phi'', and M-Phi'' interference. *)
scriptDir = DirectoryName[$InputFileName];
repoRoot = DirectoryName[DirectoryName[scriptDir]];
envPath = Environment["DMFormFactorPath"];
packagePath = If[StringQ[envPath] && envPath =!= "", envPath,
  FileNameJoin[{repoRoot, "v6", "dmformfactor-V6.m"}]];
If[!FileExistsQ[packagePath],
  Print["ERROR: AFH v6.0 source not found: ", packagePath]; Exit[2]];
Get[packagePath];
A = 131; Z = 54; JA = 3/2;
mA = A*0.93149410242;
fmToGeVInv = 5.0677;
bFM = Sqrt[41.467/(45.0 A^(-1.0/3.0) - 25.0 A^(-2.0/3.0))];
bGeVInv = bFM*fmToGeVInv;
qMax = 0.60; dq = 0.00025;
SetIsotope[Z, A, "default", "default"];
wmExpr = ResponseNuclear[y, 1, 0, 0];
phiExpr = ResponseNuclear[y, 4, 0, 0];
wmphiExpr = ResponseNuclear[y, 7, 0, 0];
If[wmExpr === $Failed || phiExpr === $Failed || wmphiExpr === $Failed,
  Print["ERROR: one or more AFH nuclear responses failed to initialize."]; Exit[3]];
qGrid = N[Range[0, Round[qMax/dq]]*dq, 18];
rows = Table[
  Module[{q = qGrid[[i]], yy, er, wm, phi, wmphi, rFactor},
    yy = (q*bGeVInv/2.0)^2;
    er = (Sqrt[mA^2 + q^2] - mA)*10^6;
    wm = N[wmExpr /. y -> yy, 30];
    phi = N[phiExpr /. y -> yy, 30];
    wmphi = N[wmphiExpr /. y -> yy, 30];
    rFactor = 4.0*4.0*Pi/(2.0*JA + 1.0);
    {q, er, wm, phi, wmphi,
      rFactor*wm/A^2, rFactor*phi/A^2, rFactor*wmphi/A^2}
  ], {i, Length[qGrid]}];
outDir = FileNameJoin[{scriptDir, "output", "native_mathematica"}];
If[!DirectoryQ[outDir], CreateDirectory[outDir, CreateIntermediateDirectories -> True]];
csvPath = FileNameJoin[{outDir, "afh_vv_phi_xe131_native.csv"}];
Export[csvPath,
  Prepend[rows, {"q_GeV", "ER_keV", "W_M00_AFH", "W_PhiPP_AFH", "W_MPhiPP_AFH",
    "R_M_raw_over_A2", "R_PhiPP_raw_over_A2", "R_MPhiPP_raw_over_A2"}], "CSV"];
metaPath = FileNameJoin[{outDir, "native_metadata.txt"}];
meta = {
  "AFH source = " <> packagePath,
  "AFH source SHA256 = " <> IntegerString[FileHash[packagePath, "SHA256"], 16, 64],
  "SetIsotope[54,131,default,default]",
  "ResponseNuclear index 1 = W_M",
  "ResponseNuclear index 4 = W_PhiPP = W_Phi double-prime",
  "ResponseNuclear index 7 = W_MPhiPP interference",
  "Isospin components = (0,0), equal physical proton/neutron coupling factor = 4",
  "q grid = 0 to 0.6 GeV, dq = 0.00025 GeV, exact spatial q",
  "b_A [fm] = " <> ToString[InputForm[N[bFM, 16]]],
  "Native Mathematica/Wolfram version = " <> ToString[$Version],
  "Rows = " <> ToString[Length[rows]]
};
Export[metaPath, StringRiffle[meta, "\n"] <> "\n", "Text"];
Print["Native AFH Xe-131 M/Phi''/M-Phi'' export completed."];
Print["CSV: ", csvPath];
Print["Metadata: ", metaPath];
