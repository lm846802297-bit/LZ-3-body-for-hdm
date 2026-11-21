(* Native AFH v6.0 export: seven xenon isotopes, all eight ResponseNuclear channels. *)
ClearAll["Global" <> FromCharacterCode[96] <> "*"];

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

Get[packagePath];

isotopes = {128, 129, 130, 131, 132, 134, 136};
qGrid = N[Range[0, 2400] * 0.00025, 18];
responseNames = {
  "W_M00_AFH",
  "W_SigmaDoublePrime00_AFH",
  "W_SigmaPrime00_AFH",
  "W_PhiPP00_AFH",
  "W_PhiTildePrime00_AFH",
  "W_Delta00_AFH",
  "W_MPhiPP00_AFH",
  "W_SigmaPrimeDelta00_AFH"
};
imagNames = ("Im_" <> #) & /@ responseNames;

envOut = Environment["AFH_FULL_RESPONSE_OUTDIR"];
outDir = If[StringQ[envOut] && envOut =!= "",
  envOut,
  FileNameJoin[{scriptDir, "output", "native"}]
];
If[!DirectoryQ[outDir],
  CreateDirectory[outDir, CreateIntermediateDirectories -> True]
];

nativeRows = {};
Do[
  A = isotope;
  Z = 54;
  Print["Starting native AFH export for Xe-", A];
  SetIsotope[Z, A, "default", "default"];

  bFM = Sqrt[41.467/(45.0 A^(-1.0/3.0) - 25.0 A^(-2.0/3.0))];
  bGeVInv = bFM * 5.0677;

  (* ResponseNuclear indices 1..8 are the authoritative AFH v6.0 definitions. *)
  exprs = Table[ResponseNuclear[y, i, 0, 0], {i, 1, 8}];

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

  path = FileNameJoin[{
    outDir, "afh_v6_xe" <> ToString[A] <> "_eight_response_native.csv"
  }];
  Export[
    path,
    Prepend[
      rows,
      Join[{"A", "q_GeV", "y"}, responseNames, imagNames]
    ],
    "CSV"
  ];
  nativeRows = Join[nativeRows, rows];
  Print["Wrote ", path, " (", Length[rows], " q nodes)"];
,
  {isotope, isotopes}
];

metadata = StringRiffle[{
  "source=AFH DMFormFactor v6.0 native Wolfram execution",
  "responses=ResponseNuclear[y,index,0,0], index=1..8",
  "isotopes=128,129,130,131,132,134,136",
  "q_grid=2401 uniform nodes from 0 to 0.6 GeV, step 0.00025 GeV",
  "isospin=tau1=tau2=0; raw AFH isoscalar package convention",
  "normalization=no physical equal-p/n factor-four rescaling in native W columns",
  "imaginary_parts=exported separately for all eight response functions",
  "AFH_source_path=" <> packagePath,
  "AFH_source_sha256=" <> IntegerString[FileHash[packagePath, "SHA256"], 16, 64],
  "wolfram_version=" <> $Version,
  "rows=" <> ToString[Length[nativeRows]]
}, "\n"];

Export[FileNameJoin[{outDir, "native_metadata.txt"}], metadata, "Text"];
Print["Native AFH eight-response export complete: ", Length[nativeRows], " rows."];
