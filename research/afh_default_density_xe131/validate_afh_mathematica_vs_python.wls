ClearAll["Global" <> FromCharacterCode[96] <> "*"];
scriptDir = DirectoryName[$InputFileName];
packageEnv = Environment["DMFormFactorPath"];
referenceEnv = Environment["AFHPythonReferenceCSV"];
outEnv = Environment["AFHMathematicaOutDir"];
packagePath = If[StringQ[packageEnv] && packageEnv =!= "", packageEnv, ExpandFileName[FileNameJoin[{scriptDir, "..", "..", "v6", "dmformfactor-V6.m"}]]];
referencePath = If[StringQ[referenceEnv] && referenceEnv =!= "", referenceEnv, FileNameJoin[{scriptDir, "output", "afh_default_xe131_WM00.csv"}]];
outDir = If[StringQ[outEnv] && outEnv =!= "", outEnv, FileNameJoin[{scriptDir, "output", "mathematica_native"}]];
If[!FileExistsQ[packagePath], Print["ERROR: AFH package not found: ", packagePath]; Exit[2]];
If[!FileExistsQ[referencePath], Print["ERROR: Python reference CSV not found: ", referencePath]; Exit[3]];
CreateDirectory[outDir, CreateIntermediateDirectories -> True];
packageText = Import[packagePath, "Text"];
If[!StringContainsQ[packageText, "Welcome to DMFormFactor version 1.1."], Print["ERROR: unexpected AFH package/version marker"]; Exit[8]];
Get[packagePath];
A = 131; Z = 54; JA = 3/2; mA = A*0.93149410242; fmToGeVInv = 5.0677;
bFM = Sqrt[41.467/(45.0 A^(-1.0/3.0) - 25.0 A^(-2.0/3.0))];
bGeVInv = bFM*fmToGeVInv;
SetIsotope[Z, A, "default", "default"];
(* Build the native AFH symbolic response once; evaluate it at every y node. *)
wmExpr = ResponseNuclear[y, 1, 0, 0];
qGrid = N[Range[0, 2400]/4000, 16];
If[Length[qGrid] =!= 2401, Print["ERROR: q grid length mismatch"]; Exit[4]];
nativeRows = Table[
 Module[{q = qGrid[[i]], yy, wm, rPackage, er},
  yy = (q*bGeVInv/2.0)^2;
  wm = N[wmExpr /. y -> yy, 16];
  If[!NumericQ[wm], Print["ERROR: nonnumeric AFH response at q=", q]; Exit[5]];
  rPackage = 4.0 Pi/(2.0 JA + 1.0)*wm;
  er = (Sqrt[mA^2 + q^2] - mA)*10^6;
  {q, yy, wm, rPackage, 4.0*rPackage, er}
 ],
 {i, Length[qGrid]}
];
pythonData = Import[referencePath, "CSV"];
If[Length[pythonData] =!= 2402, Print["ERROR: Python reference must have 2401 data rows"]; Exit[6]];
pythonRows = Rest[pythonData];
If[Length[First[pythonRows]] < 13, Print["ERROR: unexpected Python CSV columns"]; Exit[7]];
requiredColumns = {"q_GeV", "W_M00_AFH_package", "R_AFH_package_4pi_over_2Jplus1", "R_equal_pn_normalized", "A0_normalization_factor"};
If[!And @@ (MemberQ[First[pythonData], #] & /@ requiredColumns), Print["ERROR: Python CSV header does not match the expected AFH schema"]; Exit[9]];
asNumber[x_] := If[NumberQ[x], N[x], ToExpression[StringTrim[ToString[x]]]];
pythonQ = asNumber /@ pythonRows[[All, 1]];
pythonW = asNumber /@ pythonRows[[All, 4]];
pythonRPackage = asNumber /@ pythonRows[[All, 5]];
pythonRPhysical = asNumber /@ pythonRows[[All, 9]];
pythonCA = asNumber /@ pythonRows[[All, 13]];
nativeQ = nativeRows[[All, 1]];
nativeW = nativeRows[[All, 3]];
nativeRPackage = nativeRows[[All, 4]];
nativeRPhysicalRaw = nativeRows[[All, 5]];
r0AFH = First[nativeRPackage];
packageNormRelErr = Abs[r0AFH/(A^2/4.0) - 1.0];
normalizationFactor = A^2/First[nativeRPhysicalRaw];
nativeRPhysical = normalizationFactor*nativeRPhysicalRaw;
maxQDifference = Max[Abs[nativeQ - pythonQ]];
maxWAbsDifferenceOverA2 = Max[Abs[nativeW - pythonW]]/A^2;
maxPackageRAbsDifferenceOverA2 = Max[Abs[nativeRPackage - pythonRPackage]]/A^2;
maxPhysicalRAbsDifferenceOverA2 = Max[Abs[nativeRPhysical - pythonRPhysical]]/A^2;
maxNormalizationFactorDifference = Max[Abs[ConstantArray[normalizationFactor, 2401] - pythonCA]];
physicalR0RelErr = Abs[First[nativeRPhysical]/A^2 - 1.0];
comparisonRows = MapThread[
 {#1, #2, #3, #4, #5, #6, #7, #8, #9} &,
 {nativeQ, nativeW, pythonW, Abs[nativeW - pythonW], nativeRPhysical, pythonRPhysical, Abs[nativeRPhysical - pythonRPhysical], nativeRPackage, pythonRPackage}
];
comparisonPath = FileNameJoin[{outDir, "afh_xe131_mathematica_vs_python_2401.csv"}];
Export[comparisonPath, Prepend[comparisonRows, {"q_GeV", "W_M00_Mathematica", "W_M00_Python", "W_M00_abs_difference", "R_equal_pn_Mathematica", "R_equal_pn_Python", "R_equal_pn_abs_difference", "R_AFH_package_Mathematica", "R_AFH_package_Python"}], "CSV"];
status = If[maxQDifference <= 1.0*10^-12 && packageNormRelErr <= 2.0*10^-4 && physicalR0RelErr <= 1.0*10^-12 && maxWAbsDifferenceOverA2 <= 1.0*10^-10 && maxPackageRAbsDifferenceOverA2 <= 1.0*10^-10 && maxPhysicalRAbsDifferenceOverA2 <= 1.0*10^-10 && maxNormalizationFactorDifference <= 1.0*10^-10, "PASS", "FAIL"];
metadata = <|"status" -> status, "kernel" -> "native Wolfram Language / wolframscript", "official_package" -> packagePath, "python_reference_csv" -> referencePath, "isotope" -> "Xe-131", "source_selection" -> "SetIsotope[54,131,default,default]", "response_call" -> "ResponseNuclear[y,1,0,0]", "q_grid_points" -> Length[qGrid], "b_A_fm" -> N[bFM, 16], "b_A_GeV_inverse" -> N[bGeVInv, 16], "AFH_package_R0" -> N[r0AFH, 16], "expected_AFH_package_R0_A2_over_4" -> A^2/4.0, "AFH_package_R0_relative_error" -> N[packageNormRelErr, 12], "physical_equal_pn_R0" -> N[First[nativeRPhysical], 16], "A_squared" -> A^2, "normalization_factor_C_A" -> N[normalizationFactor, 16], "max_q_absolute_difference_GeV" -> N[maxQDifference, 12], "max_W_M00_absolute_difference_over_A2" -> N[maxWAbsDifferenceOverA2, 12], "max_AFH_package_response_absolute_difference_over_A2" -> N[maxPackageRAbsDifferenceOverA2, 12], "max_physical_response_absolute_difference_over_A2" -> N[maxPhysicalRAbsDifferenceOverA2, 12], "max_C_A_absolute_difference" -> N[maxNormalizationFactorDifference, 12], "acceptance_tolerances" -> <|"q_absolute_difference_GeV" -> 1.0*10^-12, "AFH_package_R0_relative_error" -> 2.0*10^-4, "physical_R0_relative_error" -> 1.0*10^-12, "W_M00_absolute_difference_over_A2" -> 1.0*10^-10, "AFH_package_response_absolute_difference_over_A2" -> 1.0*10^-10, "physical_response_absolute_difference_over_A2" -> 1.0*10^-10, "C_A_absolute_difference" -> 1.0*10^-10|>, "scope" -> "Native AFH v6.0 package evaluation at all 2401 Xe-131 q nodes compared with the archived Python finite-sum translation; no three-body or halo integral is evaluated."|>;
metadataPath = FileNameJoin[{outDir, "afh_xe131_mathematica_vs_python_metadata.json"}];
Export[metadataPath, metadata, "JSON"];
Print[ExportString[metadata, "JSON", "Compact" -> False]];
Print["Comparison CSV: ", comparisonPath];
Print["Metadata JSON: ", metadataPath];
If[status =!= "PASS", Exit[1]];
