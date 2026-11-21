(* Native AFH v6.0 q=0 analytic limits for rank-resolved DeltaJ and SigmaPJ amplitudes. *)
ClearAll["Global`*"];

scriptDir = DirectoryName[$InputFileName];
repoRoot = DirectoryName[DirectoryName[scriptDir]];
packagePath = FileNameJoin[{repoRoot, "v6", "dmformfactor-V6.m"}];
If[!FileExistsQ[packagePath],
  Print["ERROR: AFH source not found: ", packagePath];
  Exit[2]
];
Get[packagePath];

isotopes = {129, 131};
outDir = FileNameJoin[{scriptDir, "output", "native-spatial-multipoles"}];
If[!DirectoryQ[outDir], CreateDirectory[outDir, CreateIntermediateDirectories -> True]];

allRows = {};
Do[
  A = isotope;
  Z = 54;
  Print["Computing q=0 limits for Xe-", A];
  SetIsotope[Z, A, "default", "default"];
  dmLength = dmformfactor`Private`DMmatrixLength;
  bFM = Sqrt[41.467/(45.0 A^(-1.0/3.0) - 25.0 A^(-2.0/3.0))];
  bGeVInv = bFM * 5.0677;
  isoFactor = Sqrt[2]/Sqrt[2 dmformfactor`Private`TIso + 1];

  rankList = Sort@DeleteDuplicates@Cases[
    Table[
      If[dmformfactor`Private`DensityMatrix[i][[3]] == 0 && dmformfactor`Private`DensityMatrix[i][[2]] >= 1,
        dmformfactor`Private`DensityMatrix[i][[2]], 0],
      {i, dmLength}
    ],
    n_Integer /; n > 0
  ];

  Do[
    ampDelta = Sum[
      If[dmformfactor`Private`DensityMatrix[i][[3]] == 0 && dmformfactor`Private`DensityMatrix[i][[2]] == J,
        dmformfactor`Private`DensityMatrix[i][[1]] * isoFactor *
          Limit[dmformfactor`Private`DeltaJ[y,
            {dmformfactor`Private`DensityMatrix[i][[4]], dmformfactor`Private`DensityMatrix[i][[5]]/2},
            {dmformfactor`Private`DensityMatrix[i][[6]], dmformfactor`Private`DensityMatrix[i][[7]]/2},
            J], y -> 0],
        0
      ],
      {i, dmLength}
    ];
    ampSigma = Sum[
      If[dmformfactor`Private`DensityMatrix[i][[3]] == 0 && dmformfactor`Private`DensityMatrix[i][[2]] == J,
        dmformfactor`Private`DensityMatrix[i][[1]] * isoFactor *
          Limit[dmformfactor`Private`SigmaPJ[y,
            {dmformfactor`Private`DensityMatrix[i][[4]], dmformfactor`Private`DensityMatrix[i][[5]]/2},
            {dmformfactor`Private`DensityMatrix[i][[6]], dmformfactor`Private`DensityMatrix[i][[7]]/2},
            J], y -> 0],
        0
      ],
      {i, dmLength}
    ];
    AppendTo[allRows, {A, 0, 0, J, Re[N[ampDelta, 30]], Re[N[ampSigma, 30]],
      Im[N[ampDelta, 30]], Im[N[ampSigma, 30]]}];
  , {J, rankList}];
, {isotope, isotopes}];

Export[
  FileNameJoin[{outDir, "afh_v6_spatial_multipoles_q0.csv"}],
  Prepend[allRows,
    {"A", "q_GeV", "y", "multipole_J",
      "M_Delta_J_native", "M_SigmaPrime_J_native",
      "Im_M_Delta_J_native", "Im_M_SigmaPrime_J_native"}],
  "CSV"
];
Print["q=0 limit rows: ", Length[allRows]];
