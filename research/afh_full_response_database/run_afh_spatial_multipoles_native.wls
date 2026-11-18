(* Native AFH v6.0 rank-resolved DeltaJ and SigmaPJ amplitudes for Xe-129/131. *)
ClearAll["Global\`*"];

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

isotopes = {129, 131};
qGrid = N[Range[0, 2400] * 0.00025, 18];

envOut = Environment["AFH_SPATIAL_NATIVE_OUTDIR"];
outDir = If[StringQ[envOut] && envOut =!= "",
  envOut,
  FileNameJoin[{scriptDir, "output", "native-spatial-multipoles"}]
];
If[!DirectoryQ[outDir],
  CreateDirectory[outDir, CreateIntermediateDirectories -> True]
];

allRows = {};
maxImaginaryResidual = 0.0;
rankMap = {};

Do[
  A = isotope;
  Z = 54;
  Print["Starting native AFH rank-resolved multipoles for Xe-", A];
  SetIsotope[Z, A, "default", "default"];

  bFM = Sqrt[41.467/(45.0 A^(-1.0/3.0) - 25.0 A^(-2.0/3.0))];
  bGeVInv = bFM * 5.0677;
  isoFactor = Sqrt[2]/Sqrt[2 TIso + 1];

  (* Use exactly the isoscalar (T=0) OBDME rows that enter ResponseNuclear[...,0,0]. *)
  rankList = Sort@DeleteDuplicates@Cases[
    Table[
      If[DensityMatrix[i][[3]] == 0 && DensityMatrix[i][[2]] >= 1,
        DensityMatrix[i][[2]], 0],
      {i, DMmatrixLength}
    ],
    n_Integer /; n > 0
  ];
  AppendTo[rankMap, ToString[A] <> "=" <> StringRiffle[ToString /@ rankList, ","]];

  isotopeRows = Table[
    Module[{q = qGrid[[k]], yy, rankRows},
      yy = (q bGeVInv/2.0)^2;
      rankRows = Table[
        Module[{ampDelta, ampSigma, deltaComplex, sigmaComplex},
          ampDelta = Sum[
            If[DensityMatrix[i][[3]] == 0 && DensityMatrix[i][[2]] == J,
              DensityMatrix[i][[1]] * isoFactor *
                DeltaJ[
                  yy,
                  {DensityMatrix[i][[4]], DensityMatrix[i][[5]]/2},
                  {DensityMatrix[i][[6]], DensityMatrix[i][[7]]/2},
                  J
                ],
              0
            ],
            {i, DMmatrixLength}
          ];
          ampSigma = Sum[
            If[DensityMatrix[i][[3]] == 0 && DensityMatrix[i][[2]] == J,
              DensityMatrix[i][[1]] * isoFactor *
                SigmaPJ[
                  yy,
                  {DensityMatrix[i][[4]], DensityMatrix[i][[5]]/2},
                  {DensityMatrix[i][[6]], DensityMatrix[i][[7]]/2},
                  J
                ],
              0
            ],
            {i, DMmatrixLength}
          ];
          deltaComplex = N[ampDelta, 30];
          sigmaComplex = N[ampSigma, 30];
          maxImaginaryResidual = Max[
            maxImaginaryResidual, Abs[Im[deltaComplex]], Abs[Im[sigmaComplex]]
          ];
          {A, q, yy, J, Re[deltaComplex], Re[sigmaComplex],
            Im[deltaComplex], Im[sigmaComplex]}
        ],
        {J, rankList}
      ];
      rankRows
    ],
    {k, Length[qGrid]}
  ];

  flatRows = Flatten[isotopeRows, 1];
  allRows = Join[allRows, flatRows];
  Print["Xe-", A, ": ", Length[flatRows], " native rank/q rows."];
,
  {isotope, isotopes}
];

csvPath = FileNameJoin[{
  outDir, "afh_v6_xe129_xe131_spatial_multipoles_native.csv"
}];
Export[
  csvPath,
  Prepend[
    allRows,
    {"A", "q_GeV", "y", "multipole_J",
      "M_Delta_J_native", "M_SigmaPrime_J_native",
      "Im_M_Delta_J_native", "Im_M_SigmaPrime_J_native"}
  ],
  "CSV"
];

sourceCommit = Environment["AFH_SOURCE_COMMIT"];
If[!StringQ[sourceCommit] || sourceCommit === "", sourceCommit = "unspecified"];
metadata = StringRiffle[{
  "source=AFH DMFormFactor v6.0 native Wolfram execution",
  "source_commit=" <> sourceCommit,
  "AFH_source_path=" <> packagePath,
  "AFH_source_sha256=" <> IntegerString[FileHash[packagePath, "SHA256"], 16, 64],
  "wolfram_version=" <> $Version,
  "isotopes=129,131",
  "q_grid=2401 uniform nodes from 0 to 0.6 GeV, step 0.00025 GeV",
  "multipole_amplitudes=direct native DeltaJ and SigmaPJ OBDME sums",
  "isospin=only T=0 OBDME rows; isoscalar factor Sqrt[2/(2 TIso+1)]",
  "normalization=raw AFH package amplitudes; no equal-p/n factor-four conversion",
  "imaginary_parts=exported separately for both amplitude channels",
  "max_imaginary_residual=" <> ToString[N[maxImaginaryResidual, 16]],
  "rank_map=" <> StringRiffle[rankMap, ";"],
  "rows=" <> ToString[Length[allRows]]
}, "\n"];

Export[FileNameJoin[{outDir, "native_spatial_multipole_metadata.txt"}], metadata, "Text"];
Print["Native AFH spatial multipole export complete: ", Length[allRows], " rows."];
