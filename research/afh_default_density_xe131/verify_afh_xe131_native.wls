(* Independent AFH v6 / archived Python comparison for Xe-131.
   Run: wolframscript -file verify_afh_xe131_native.wls
   Set environment variables DMFormFactorPath, AFHPythonCSV, AFHAuditDir.
   The official AFH package and the archived Python CSV are required. *)
ClearAll["Global`*"];
fail[msg_, code_: 1] := (Print["ERROR: ", msg]; Exit[code]);
env[name_] := Module[{s = Environment[name]}, If[StringQ[s] && StringLength[s] > 0, s, ""]];
packagePath = env["DMFormFactorPath"];
pythonPath = env["AFHPythonCSV"];
outDir = env["AFHAuditDir"];
If[packagePath === "" || !FileExistsQ[packagePath], fail["Set DMFormFactorPath to dmformfactor-V6.m", 2]];
If[pythonPath === "" || !FileExistsQ[pythonPath], fail["Set AFHPythonCSV to output/afh_default_xe131_WM00.csv", 2]];
If[outDir === "", outDir = DirectoryName[$InputFileName]];
If[!DirectoryQ[outDir], fail["AFHAuditDir does not exist", 2]];
Print["Wolfram version: ", $Version];
Print["AFH source SHA256: ", FileHash[packagePath, "SHA256", "HexString"]];
Print["Python CSV SHA256: ", FileHash[pythonPath, "SHA256", "HexString"]];
Get[packagePath];
SetIsotope[54, 131, "default", "default"];
response = ResponseNuclear[y, 1, 0, 0];
If[!NumericQ[N[response /. y -> 0]], fail["ResponseNuclear did not produce a numeric response at y=0", 3]];
A = 131; jA = 3/2;
bFM = Sqrt[41.467/(45. A^(-1./3.) - 25. A^(-2./3.))];
bGeV = 5.0677 bFM;
mA = A 0.93149410242; (* same recoil-coordinate convention as Python *)
wm[q_?NumericQ] := N[response /. y -> (q bGeV/2)^2];
rRaw[q_?NumericQ] := 16 Pi/(2 jA + 1) wm[q];
r0 = rRaw[0.];
If[!NumericQ[r0] || r0 <= 0, fail["Invalid raw zero-momentum response", 3]];
rNorm[q_?NumericQ] := A^2 rRaw[q]/r0;
relativeZeroOffset = r0/A^2 - 1;
If[Abs[relativeZeroOffset] > 2.*10^-4, fail["Raw zero-momentum response outside density-rounding tolerance", 4]];
py = Import[pythonPath, "CSV"];
If[!ListQ[py] || Length[py] < 2, fail["Cannot read Python CSV", 5]];
header = First[py]; data = Rest[py];
required = {"q_GeV", "W_M00_AFH_package", "R_equal_pn_raw", "R_equal_pn_normalized"};
positions = (FirstPosition[header, #, Missing["NotFound"]] &) /@ required;
If[!FreeQ[positions, _Missing], fail["Missing required Python CSV column", 5]];
indices = First /@ positions;
If[!MatrixQ[data[[All, indices]], NumericQ], fail["Non-numeric Python CSV input", 5]];
qGrid = data[[All, indices[[1]]]];
If[Length[qGrid] != 2401 || Abs[First[qGrid]] > 10^-14 || Abs[Last[qGrid] - 0.6] > 10^-12 || Max[Abs[Differences[qGrid] - 0.00025]] > 10^-12, fail["Unexpected q grid", 5]];
(* Compare raw W and raw physical response before any q=0 normalization. *)
native = Table[{q, wm[q], rRaw[q], rNorm[q]}, {q, qGrid}];
python = data[[All, indices]];
rtol = 2.*10^-8; atol = 2.*10^-10;
columns = {"W_M00_AFH_package", "R_equal_pn_raw", "R_equal_pn_normalized"};
stats = Table[
  Module[{delta, allowed, worst},
    delta = Abs[native[[All, k]] - python[[All, k]]];
    allowed = atol + rtol Abs[python[[All, k]]];
    worst = First[Ordering[delta/allowed, -1]];
    {columns[[k-1]], Max[delta], Max[delta/allowed], qGrid[[worst]], Count[MapThread[Greater, {delta, allowed}], True]}
  ], {k, 2, 4}];
(* Find the three minima independently in finite intervals, not by fitting b. *)
intervals = {{0.14, 0.18}, {0.24, 0.28}, {0.34, 0.39}};
minima = Table[
  Module[{sol, qq, er, lo = interval[[1]], hi = interval[[2]]},
    sol = Quiet[NMinimize[{rNorm[x]/A^2, lo <= x <= hi}, x]];
    If[!MatchQ[sol, {_?NumericQ, {x -> _?NumericQ}}], fail["Minimization failed", 6]];
    qq = x /. sol[[2]];
    er = 10^6 qq^2/(Sqrt[mA^2 + qq^2] + mA);
    {qq, 1000 qq, er, sol[[1]]}
  ], {interval, intervals}];
nativeGridPath = FileNameJoin[{outDir, "afh_native_audit_grid.csv"}];
nativeComparisonPath = FileNameJoin[{outDir, "afh_native_audit_comparison.csv"}];
nativeMinimaPath = FileNameJoin[{outDir, "afh_native_audit_minima.csv"}];
nativeMetadataPath = FileNameJoin[{outDir, "afh_native_audit_metadata.txt"}];
Export[nativeGridPath,
  Prepend[native, {"q_GeV", "W_M00_AFH_package", "R_equal_pn_raw", "R_equal_pn_normalized"}], "CSV"];
Export[nativeComparisonPath,
  Prepend[stats, {"quantity", "max_absolute_difference", "max_tolerance_ratio", "worst_q_GeV", "failed_points"}], "CSV"];
Export[nativeMinimaPath,
  Prepend[minima, {"q_GeV", "q_MeV", "ER_keV", "R_over_A2"}], "CSV"];
auditMetadata = {
  "WolframVersion = " <> $Version,
  "AFHSourcePath = " <> packagePath,
  "AFHSourceSHA256 = " <> FileHash[packagePath, "SHA256", "HexString"],
  "PythonCSVPath = " <> pythonPath,
  "PythonCSV_SHA256 = " <> FileHash[pythonPath, "SHA256", "HexString"],
  "NativeGridCSV_SHA256 = " <> FileHash[nativeGridPath, "SHA256", "HexString"],
  "NativeComparisonCSV_SHA256 = " <> FileHash[nativeComparisonPath, "SHA256", "HexString"],
  "NativeMinimaCSV_SHA256 = " <> FileHash[nativeMinimaPath, "SHA256", "HexString"],
  "q_nodes = " <> ToString[Length[qGrid]],
  "q_min_GeV = " <> ToString[InputForm[First[qGrid]]],
  "q_max_GeV = " <> ToString[InputForm[Last[qGrid]]],
  "q_step_GeV = 0.00025",
  "response_rtol = " <> ToString[InputForm[rtol]],
  "response_atol = " <> ToString[InputForm[atol]],
  "raw_R_A_zero = " <> ToString[InputForm[r0]],
  "raw_R_A_zero_relative_offset = " <> ToString[InputForm[relativeZeroOffset]],
  "zero_normalization_factor = " <> ToString[InputForm[A^2/r0]]
};
Export[nativeMetadataPath, StringRiffle[auditMetadata, "\n"] <> "\n", "Text"];
Print["b_A [fm] = ", InputForm[bFM]];
Print["raw physical R(0) = ", InputForm[r0], "; A^2 = ", A^2];
Print["raw relative offset R(0)/A^2 - 1 = ", InputForm[relativeZeroOffset]];
Print["explicit zero-normalization factor = ", InputForm[A^2/r0]];
Print["Comparison {quantity, max abs diff, max tolerance ratio, worst q, failed count}:"];
Scan[Print, stats];
Print["Minima {q [GeV], q [MeV], ER [keV], normalized response/A^2}:"];
Scan[Print, minima];
If[Total[stats[[All, 5]]] > 0, fail["Mathematica/Python comparison failed; output files retained", 7]];
Print["PASS: raw and normalized responses agree with Python at all grid points."];
Print["Native audit metadata: ", nativeMetadataPath];
Exit[0];
