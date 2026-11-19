(* Finite-Q^2 Dirac-Pauli charge-sector response ratio for Xe-131. *)
(* Run from any directory with: wolframscript -file this-file.wls *)
ClearAll["Global`*"];
scriptDirectory = DirectoryName[$InputFileName];
responseFile = FileNameJoin[{scriptDirectory, "output", "phi_response_native", "afh_default_xe131_M_PhiPP_native.csv"}];
raw = Import[responseFile, "CSV"];
header = First[raw]; dataRows = Rest[raw];
col[name_] := First@FirstPosition[header, name];
responseData[name_] := N[({#[[col["q_GeV"]]], #[[col[name]]]} & /@ dataRows)];

(* Shape-preserving cubic Hermite interpolation (PCHIP), Fritsch-Butland slopes. *)
pchipSlopes[d_] := Module[{x, y, h, delta, n, m, endpoint},
  x = d[[All, 1]]; y = d[[All, 2]]; n = Length[x]; h = Differences[x]; delta = Differences[y]/h; m = ConstantArray[0., n];
  endpoint[h1_, h2_, d1_, d2_] := Module[{s = ((2 h1 + h2) d1 - h1 d2)/(h1 + h2)}, If[Sign[s] != Sign[d1], 0., If[Sign[d1] != Sign[d2] && Abs[s] > Abs[3 d1], 3 d1, s]]];
  If[n == 2, Return[{delta[[1]], delta[[1]]}]];
  m[[1]] = endpoint[h[[1]], h[[2]], delta[[1]], delta[[2]]];
  m[[-1]] = endpoint[h[[-1]], h[[-2]], delta[[-1]], delta[[-2]]];
  Do[If[delta[[i - 1]] delta[[i]] > 0, With[{w1 = 2 h[[i]] + h[[i - 1]], w2 = h[[i]] + 2 h[[i - 1]]}, m[[i]] = (w1 + w2)/(w1/delta[[i - 1]] + w2/delta[[i]])], m[[i]] = 0.], {i, 2, n - 1}]; m];
pchipValue[d_, x0_] := Module[{x = d[[All, 1]], y = d[[All, 2]], m, i, h, t}, m = pchipSlopes[d]; i = Clip[LengthWhile[x, # <= x0 &], {1, Length[x] - 1}]; h = x[[i + 1]] - x[[i]]; t = (x0 - x[[i]])/h; (2 t^3 - 3 t^2 + 1) y[[i]] + (t^3 - 2 t^2 + t) h m[[i]] + (-2 t^3 + 3 t^2) y[[i + 1]] + (t^3 - t^2) h m[[i + 1]]];

(* Input masses are in GeV; F1 and F2 are supplied center-diagnostic values. *)
mA = 121.9097198354; mN = 0.938918;
benchmarks = {<|"ERkeV" -> 200., "DeltaMkeV" -> 450., "F1" -> 2.663163406, "F2" -> -0.468053440|>, <|"ERkeV" -> 267., "DeltaMkeV" -> 362., "F1" -> 2.563886256, "F2" -> -0.449774513|>};
wmData = responseData["R_M_physical_equal_pn"];
wphiData = responseData["R_PhiPP_physical_equal_pn"];
wmphiData = responseData["R_MPhiPP_physical_equal_pn"];
results = Map[Function[b, Module[{er, q, f1, f2, fs, cm, cp, eta, wm, wp, wmp, interf, diag, ratio},
  er = b["ERkeV"] 10^-6; q = Sqrt[er (er + 2 mA)]; f1 = b["F1"]; f2 = b["F2"]; fs = f1 + 2 f2;
  cm = f1 - q^2/(8 mN^2) fs; cp = q^2/(4 mN^2) fs; eta = cp/cm;
  wm = pchipValue[wmData, q]; wp = pchipValue[wphiData, q]; wmp = pchipValue[wmphiData, q];
  interf = 2 eta wmp/wm; diag = eta^2 wp/wm; ratio = 1 + interf + diag;
  Join[b, <|"QA_GeV" -> q, "F1plus2F2" -> fs, "cM" -> cm, "cPhiPP" -> cp, "eta" -> eta, "WM" -> wm, "WPhiPP" -> wp, "WMPhiPP" -> wmp, "WPhiPP_over_WM" -> wp/wm, "WMPhiPP_over_WM" -> wmp/wm, "InterferenceFraction" -> interf, "PhiDiagonalFraction" -> diag, "ChargeRatio" -> ratio, "ChangePercent" -> 100 (ratio - 1)|>]]], benchmarks];

(* The shared three-body phase-space/current factor cancels exactly in this ratio. *)
l = Unique["L00threeBody"];
ratioCancellation = FullSimplify[(l (cm^2 wm + 2 cm cp wmp + cp^2 wp)/(l cm^2 wm)), Assumptions -> l != 0 && cm != 0 && wm != 0];
Print["Mathematica version: ", $Version];
Print["AFH input: ", responseFile];
Print["PCHIP interpolation of native physical equal-p/n response columns."];
Print["Shared three-body kernel cancellation simplifies to: ", ratioCancellation];
headers = {"ER (keV)", "Delta m (keV)", "QA (GeV)", "F1", "F2", "cM", "cPhi''", "eta", "WM", "WPhi''", "WM-Phi''", "interference frac", "Phi'' diagonal frac", "ratio", "change (%)"};
view = ({# ["ERkeV"], # ["DeltaMkeV"], # ["QA_GeV"], # ["F1"], # ["F2"], # ["cM"], # ["cPhiPP"], # ["eta"], # ["WM"], # ["WPhiPP"], # ["WMPhiPP"], # ["InterferenceFraction"], # ["PhiDiagonalFraction"], # ["ChargeRatio"], # ["ChangePercent"]} & /@ results);
Print[Grid[Prepend[view, headers], Frame -> All, Alignment -> Right]];
outDir = FileNameJoin[{scriptDirectory, "output", "finite_q2_charge_response_ratio"}]; If[!DirectoryQ[outDir], CreateDirectory[outDir, CreateIntermediateDirectories -> True]];
csvHeaders = {"ER_keV", "DeltaM_keV", "QA_GeV", "F1V", "F2V", "F1plus2F2", "cM", "cPhiPP", "cPhi_over_cM", "WM", "WPhiPP", "WMPhiPP", "WPhiPP_over_WM", "WMPhiPP_over_WM", "interference_fraction", "PhiPP_diagonal_fraction", "charge_ratio", "change_percent"};
csvRows = ({#["ERkeV"], #["DeltaMkeV"], #["QA_GeV"], #["F1"], #["F2"], #["F1plus2F2"], #["cM"], #["cPhiPP"], #["eta"], #["WM"], #["WPhiPP"], #["WMPhiPP"], #["WPhiPP_over_WM"], #["WMPhiPP_over_WM"], #["InterferenceFraction"], #["PhiDiagonalFraction"], #["ChargeRatio"], #["ChangePercent"]} & /@ results);
Export[FileNameJoin[{outDir, "finite_q2_charge_response_ratio.csv"}], Prepend[csvRows, csvHeaders], "CSV"];
Export[FileNameJoin[{outDir, "run_manifest.json"}], <|"calculation" -> "Xe-131 finite-Q^2 Dirac-Pauli charge-sector ratio", "mathematica_version" -> $Version, "response_source" -> responseFile, "response_columns" -> {"R_M_physical_equal_pn", "R_PhiPP_physical_equal_pn", "R_MPhiPP_physical_equal_pn"}, "interpolation" -> "shape-preserving cubic Hermite (PCHIP)", "mA_GeV" -> mA, "mN_GeV" -> mN, "form_factor_note" -> "F1V and F2V are supplied isoscalar_zexp center diagnostic inputs, not independently recomputed here", "scope" -> {"Xe-131 only", "fixed-speed three-body kernel cancels in the ratio", "spatial nuclear current omitted", "width prescription cancels from the ratio"}, "results" -> (AssociationThread[csvHeaders, #] & /@ csvRows)|>, "JSON"];
Print["CSV saved: ", FileNameJoin[{outDir, "finite_q2_charge_response_ratio.csv"}]];
Print["Manifest saved: ", FileNameJoin[{outDir, "run_manifest.json"}]];
