(* Native AFH v6.0 Xe-131 export for M, Phi'', and M-Phi'' responses. *)
ClearAll["Global`*"];
scriptDir = DirectoryName[$InputFileName];
repoRoot = DirectoryName[DirectoryName[scriptDir]];
envPath = Environment["DMFormFactorPath"];
packagePath = If[StringQ[envPath] && envPath =!= "", envPath, FileNameJoin[{repoRoot, "v6", "dmformfactor-V6.m"}]];
matrixPath = FileNameJoin[{scriptDir, "input", "afh_default_xe131_density_matrix.csv"}];
If[!FileExistsQ[packagePath], Print["ERROR: AFH source not found: ", packagePath]; Exit[2]];
If[!FileExistsQ[matrixPath], Print["ERROR: Xe-131 density matrix not found: ", matrixPath]; Exit[2]];
sha256[path_] := IntegerString[FileHash[path, "SHA256"], 16, 64];
expectedSourceSha = "dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372";
expectedMatrixSha = "f656145ba2fb9da741b77faed4c01d0dc457c955fa340928b5dbf9cee9bc5d45";
sourceSha = ToLowerCase[sha256[packagePath]];
matrixSha = ToLowerCase[sha256[matrixPath]];
If[sourceSha =!= expectedSourceSha, Print["ERROR: AFH source SHA-256 mismatch: ", sourceSha]; Exit[3]];
If[matrixSha =!= expectedMatrixSha, Print["ERROR: density-matrix SHA-256 mismatch: ", matrixSha]; Exit[3]];
Get[packagePath];
A = 131; Z = 54; JA = 3/2;
SetIsotope[Z, A, "default", "default"];
fmToGeVInv = 5.0677;
bFM = Sqrt[41.467/(45.0 A^(-1.0/3.0) - 25.0 A^(-2.0/3.0))];
bGeVInv = bFM*fmToGeVInv;
qMin = 0.0; qMax = 0.60; dq = 0.00025;
qGrid = N[Range[0, Round[(qMax - qMin)/dq]]*dq + qMin, 16];
responseExpressions = (ResponseNuclear[y, #, 0, 0] &) /@ {1, 4, 7};
If[Length[responseExpressions] != 3 || MemberQ[responseExpressions, Null], Print["ERROR: AFH response export failed."]; Exit[4]];
rFactor = N[4 Pi/(2 JA + 1), 30];
rows = Table[
  Module[{q = qGrid[[i]], yy, vals, raw, physical, imag},
    yy = (q*bGeVInv/2.0)^2;
    vals = N[responseExpressions /. y -> yy, 30];
    If[!VectorQ[vals, NumericQ], Print["ERROR: non-numeric response at q = ", q]; Exit[5]];
    raw = rFactor*Re[vals]; physical = 4.0*raw; imag = Im[vals];
    {q, yy, Re[vals[[1]]], Re[vals[[2]]], Re[vals[[3]]],
     raw[[1]], raw[[2]], raw[[3]], physical[[1]], physical[[2]], physical[[3]],
     imag[[1]], imag[[2]], imag[[3]]}
  ], {i, Length[qGrid]}];
rM0Raw = rows[[1, 6]];
expectedM0Raw = A^2/4.0;
m0RelativeError = Abs[rM0Raw/expectedM0Raw - 1.0];
If[!NumericQ[rM0Raw] || m0RelativeError > 2.0*10^-4, Print["ERROR: W_M q=0 normalization failed."]; Exit[6]];
outDir = FileNameJoin[{scriptDir, "output", "phi_response_native"}];
If[!DirectoryQ[outDir], CreateDirectory[outDir, CreateIntermediateDirectories -> True]];
csvPath = FileNameJoin[{outDir, "afh_default_xe131_M_PhiPP_native.csv"}];
headers = {"q_GeV", "y", "W_M00_AFH", "W_PhiPP00_AFH", "W_MPhiPP00_AFH",
 "R_M_raw", "R_PhiPP_raw", "R_MPhiPP_raw", "R_M_physical_equal_pn",
 "R_PhiPP_physical_equal_pn", "R_MPhiPP_physical_equal_pn",
 "Im_W_M00", "Im_W_PhiPP00", "Im_W_MPhiPP00"};
Export[csvPath, Prepend[rows, headers], "CSV"];
metaPath = FileNameJoin[{outDir, "afh_default_xe131_M_PhiPP_metadata.json"}];
metadata = <|"status" -> "COMPLETED", "source" -> "AFH DMFormFactor v6.0 native Wolfram execution",
 "afh_source_sha256" -> sourceSha, "density_matrix_csv_sha256" -> matrixSha,
 "isotope_A" -> A, "Z" -> Z, "J_A" -> JA,
 "density_matrix" -> "built-in sdgXe131, 67 entries",
 "response_indices" -> <|"M" -> 1, "PhiPP" -> 4, "M_PhiPP" -> 7|>,
 "isospin" -> "tau1=tau2=0; raw AFH isoscalar package convention",
 "q_definition" -> "q_A = |P_A' - P_A|, spatial nuclear momentum in GeV",
 "q_min_GeV" -> qMin, "q_max_GeV" -> qMax, "dq_GeV" -> dq,
 "grid_points" -> Length[qGrid], "b_A_fm" -> N[bFM, 16], "b_A_GeV_inverse" -> N[bGeVInv, 16],
 "response_normalization" -> "R_raw = 4 Pi W_AFH/(2 J_A+1)",
 "physical_equal_pn_mapping" -> "R_physical = 4 R_raw, applied once to M, Phi'', and M-Phi''",
 "factor_four_applied_once" -> True, "shape_renormalization_applied" -> False,
 "expected_R_M_raw_q0_A2_over_4" -> expectedM0Raw,
 "measured_R_M_raw_q0" -> N[rM0Raw, 16],
 "R_M_raw_q0_relative_error" -> N[m0RelativeError, 12],
 "wolfram_version" -> $Version, "system_id" -> $SystemID|>;
metadata["csv_sha256"] = ToLowerCase[sha256[csvPath]];
Export[metaPath, metadata, "JSON"];
Print["Native AFH Xe-131 M/Phi'' export completed. Rows = ", Length[rows]];
Print["R_M_raw(0) = ", N[rM0Raw, 16], "; A^2/4 = ", expectedM0Raw];
Print["CSV: ", csvPath]; Print["Metadata: ", metaPath];
