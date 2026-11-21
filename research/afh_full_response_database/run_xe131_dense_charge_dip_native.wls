(* Dense native AFH v6.0 Xe-131 charge-response export around the W_M diffraction minimum. *)
ClearAll["Global`*"];

scriptDir = DirectoryName[$InputFileName];
repoRoot = DirectoryName[DirectoryName[scriptDir]];
envPath = Environment["DMFormFactorPath"];
packagePath = If[StringQ[envPath] && envPath =!= "",
  envPath,
  FileNameJoin[{repoRoot, "v6", "dmformfactor-V6.m"}]
];
If[!FileExistsQ[packagePath],
  Print["ERROR: AFH source not found: ", packagePath];
  Exit[2]
];

(* Keep the committed provenance path repository-relative. The SHA-256 below
   still pins the exact package bytes used for this export. *)
sourceRel = If[StringQ[envPath] && envPath =!= "",
  packagePath,
  "v6/dmformfactor-V6.m"
];

Get[packagePath];

A = 131;
Z = 54;
SetIsotope[Z, A, "default", "default"];

bFM = Sqrt[41.467/(45.0 A^(-1.0/3.0) - 25.0 A^(-2.0/3.0))];
bGeVInv = bFM * 5.0677;

(* 121 nodes: 0.2545--0.2575 GeV, with 0.025 MeV spacing. *)
qGrid = N[0.2545 + Range[0, 120] * 0.000025, 18];
responseIndices = {1, 4, 7};
responseNames = {"W_M00_AFH", "W_PhiPP00_AFH", "W_MPhiPP00_AFH"};
imagNames = ("Im_" <> #) & /@ responseNames;

envOut = Environment["AFH_XE131_DENSE_CHARGE_OUTDIR"];
outDir = If[StringQ[envOut] && envOut =!= "",
  envOut,
  FileNameJoin[{scriptDir, "output", "xe131-dense-charge-dip"}]
];
If[!DirectoryQ[outDir],
  CreateDirectory[outDir, CreateIntermediateDirectories -> True]
];

exprs = Table[ResponseNuclear[y, i, 0, 0], {i, responseIndices}];
rows = Table[
  Module[{q = qGrid[[k]], yy, vals, reVals, imVals},
    yy = (q bGeVInv/2.0)^2;
    vals = N[exprs /. y -> yy, 30];
    reVals = Re /@ vals;
    imVals = Im /@ vals;
    {A, q, yy, Sequence @@ reVals, Sequence @@ imVals}
  ],
  {k, Length[qGrid]}
];

maxImaginaryResidual = Max[Abs[Flatten[rows[[All, 7 ;; 9]]]]];
If[!NumericQ[maxImaginaryResidual] || maxImaginaryResidual > 2.0*10^-12,
  Print["ERROR: native imaginary residual exceeds tolerance: ", maxImaginaryResidual];
  Exit[3]
];

csvPath = FileNameJoin[{outDir, "xe131_dense_charge_response_dip_native.csv"}];
Export[
  csvPath,
  Prepend[rows, Join[{"A", "q_GeV", "y"}, responseNames, imagNames]],
  "CSV"
];

metadata = StringRiffle[{
  "source=AFH DMFormFactor v6.0 native Wolfram execution",
  "isotope=Xe-131",
  "Z=54",
  "responses=ResponseNuclear[y,index,0,0], indices=1,4,7",
  "response_map=M=1;PhiPP=4;MPhiPP=7",
  "q_grid=121 uniform nodes from 0.2545 to 0.2575 GeV, step 0.000025 GeV",
  "isospin=tau1=tau2=0; raw AFH isoscalar package convention",
  "normalization=raw AFH package response; no physical equal-p/n factor-four rescaling",
  "imaginary_parts=exported separately for all three response functions",
  "max_imaginary_residual=" <> ToString[InputForm[maxImaginaryResidual]],
  "AFH_source_path=" <> sourceRel,
  "AFH_source_sha256=" <> IntegerString[FileHash[packagePath, "SHA256"], 16, 64],
  "source_commit=" <> ToString[Environment["AFH_SOURCE_COMMIT"]],
  "wolfram_version=" <> $Version,
  "rows=" <> ToString[Length[rows]]
}, "\n"];

Export[
  FileNameJoin[{outDir, "xe131_dense_charge_response_dip_metadata.txt"}],
  metadata,
  "Text"
];

Print["Dense native Xe-131 charge export complete: ", Length[rows], " rows."];
Print["q range: ", First[qGrid], " -- ", Last[qGrid], " GeV"];
Print["max imaginary residual: ", maxImaginaryResidual];
