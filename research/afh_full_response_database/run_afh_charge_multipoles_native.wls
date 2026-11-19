(* Native AFH v6.0 rank-resolved M_J and PhiPP_J charge multipoles for Xe-129/131. *)
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
Get[packagePath];

isotopes = {129, 131};
qGrid = N[Range[0, 2400] * 0.00025, 18];
envOut = Environment["AFH_CHARGE_NATIVE_OUTDIR"];
outDir = If[StringQ[envOut] && envOut =!= "",
  envOut,
  FileNameJoin[{scriptDir, "output", "native-charge-multipoles"}]
];
If[!DirectoryQ[outDir],
  CreateDirectory[outDir, CreateIntermediateDirectories -> True]
];

multipoleRows = {};
validationRows = {};
rankMap = {};
maxImaginaryResidual = 0.0;
maxAbsoluteResidual = 0.0;
maxRelativeResidual = 0.0;

closeQ[a_, b_] := Abs[a - b] <= 2.0*10^-12 +
  5.0*10^-7*Max[Abs[a], Abs[b], 10^-300];
relativeResidual[a_, b_] := Abs[a - b]/Max[Abs[a], Abs[b], 10^-8];

Do[
  A = isotope;
  Z = 54;
  Print["Starting native AFH charge multipoles for Xe-", A];
  SetIsotope[Z, A, "default", "default"];

  bFM = Sqrt[41.467/(45.0 A^(-1.0/3.0) - 25.0 A^(-2.0/3.0))];
  bGeVInv = bFM * 5.0677;
  isoFactor = Sqrt[2]/Sqrt[2 TIso + 1];

  (* Normal-parity charge multipoles include J=0. Obtain allowed ranks
     from the actual isoscalar OBDME instead of assuming a truncation. *)
  chargeRankList = Sort@DeleteDuplicates@Cases[
    Table[
      If[DensityMatrix[i][[3]] == 0 && DensityMatrix[i][[2]] >= 0,
        DensityMatrix[i][[2]], -1],
      {i, DMmatrixLength}
    ],
    n_Integer /; n >= 0
  ];
  expectedChargeRanks = If[A == 129, {0, 1}, {0, 1, 2, 3}];
  If[chargeRankList =!= expectedChargeRanks,
    Print["ERROR: unexpected AFH isoscalar charge ranks for Xe-", A,
      ": ", chargeRankList];
    Exit[4]
  ];
  AppendTo[rankMap, ToString[A] <> "=" <>
    StringRiffle[ToString /@ chargeRankList, ","]];

  isotopeMultipoles = {};
  isotopeValidation = Table[
    Module[{q = qGrid[[k]], yy, rankRows, ampM, ampPhi,
      mNative, phiNative, mPhiNative, mRank, phiRank, mPhiRank, residuals},
      yy = (q bGeVInv/2.0)^2;
      rankRows = Table[
        Module[{aM, aPhi, mComplex, phiComplex},
          aM = Sum[
            If[DensityMatrix[i][[3]] == 0 && DensityMatrix[i][[2]] == J,
              DensityMatrix[i][[1]] * isoFactor *
                MJ[
                  yy,
                  {DensityMatrix[i][[4]], DensityMatrix[i][[5]]/2},
                  {DensityMatrix[i][[6]], DensityMatrix[i][[7]]/2},
                  J
                ],
              0
            ],
            {i, DMmatrixLength}
          ];
          aPhi = Sum[
            If[DensityMatrix[i][[3]] == 0 && DensityMatrix[i][[2]] == J,
              DensityMatrix[i][[1]] * isoFactor *
                PhiPPJ[
                  yy,
                  {DensityMatrix[i][[4]], DensityMatrix[i][[5]]/2},
                  {DensityMatrix[i][[6]], DensityMatrix[i][[7]]/2},
                  J
                ],
              0
            ],
            {i, DMmatrixLength}
          ];
          mComplex = N[aM, 30];
          phiComplex = N[aPhi, 30];
          maxImaginaryResidual = Max[
            maxImaginaryResidual,
            Abs[Im[mComplex]], Abs[Im[phiComplex]]
          ];
          {A, q, yy, J, Re[mComplex], Im[mComplex],
            Re[phiComplex], Im[phiComplex]}
        ],
        {J, chargeRankList}
      ];

      ampM = (#[[5]] + I #[[6]]) & /@ rankRows;
      ampPhi = (#[[7]] + I #[[8]]) & /@ rankRows;
      mRank = 0.25 Total[Abs[ampM]^2];
      phiRank = 0.25 Total[Abs[ampPhi]^2];
      mPhiRank = 0.25 Total[Re[ampM Conjugate[ampPhi]]];

      (* Independent native AFH response evaluation at the same q node. *)
      mNative = N[ResponseNuclear[yy, 1, 0, 0], 30];
      phiNative = N[ResponseNuclear[yy, 4, 0, 0], 30];
      mPhiNative = N[ResponseNuclear[yy, 7, 0, 0], 30];

      residuals = {
        Abs[mRank - Re[mNative]],
        Abs[phiRank - Re[phiNative]],
        Abs[mPhiRank - Re[mPhiNative]]
      };
      maxAbsoluteResidual = Max[maxAbsoluteResidual, Sequence @@ residuals];
      maxRelativeResidual = Max[
        maxRelativeResidual,
        relativeResidual[mRank, Re[mNative]],
        relativeResidual[phiRank, Re[phiNative]],
        relativeResidual[mPhiRank, Re[mPhiNative]]
      ];
      maxImaginaryResidual = Max[
        maxImaginaryResidual, Abs[Im[mNative]],
        Abs[Im[phiNative]], Abs[Im[mPhiNative]]
      ];
      If[!And @@ MapThread[closeQ, {
          {mRank, phiRank, mPhiRank},
          {Re[mNative], Re[phiNative], Re[mPhiNative]}
        }],
        Print["ERROR: native charge rank-sum mismatch at Xe-", A,
          ", q=", q];
        Exit[5]
      ];

      isotopeMultipoles = Join[isotopeMultipoles, rankRows];
      {A, q, yy, mRank, Re[mNative], phiRank, Re[phiNative],
        mPhiRank, Re[mPhiNative], Sequence @@ residuals}
    ],
    {k, Length[qGrid]}
  ];

  multipoleRows = Join[multipoleRows, isotopeMultipoles];
  validationRows = Join[validationRows, isotopeValidation];
  Print["Finished Xe-", A, ": ", Length[isotopeMultipoles],
    " charge multipole rows; rank-sum residual max=",
    ScientificForm[maxRelativeResidual, 5]];
  ,
  {isotope, isotopes}
];

multipolePath = FileNameJoin[{outDir, "afh_v6_xe129_xe131_charge_multipoles_native.csv"}];
validationPath = FileNameJoin[{outDir, "afh_v6_xe129_xe131_charge_rank_sum_validation.csv"}];
metadataPath = FileNameJoin[{outDir, "charge_multipole_metadata.json"}];

Export[multipolePath,
  Prepend[multipoleRows, {
    "A", "q_GeV", "y", "multipole_J",
    "M_J_native", "Im_M_J_native",
    "PhiPP_J_native", "Im_PhiPP_J_native"
  }],
  "CSV"
];
Export[validationPath,
  Prepend[validationRows, {
    "A", "q_GeV", "y",
    "W_M_rank_sum", "W_M_native",
    "W_PhiPP_rank_sum", "W_PhiPP_native",
    "W_MPhiPP_rank_sum", "W_MPhiPP_native",
    "abs_residual_M", "abs_residual_PhiPP", "abs_residual_MPhiPP"
  }],
  "CSV"
];

metadata = <|
  "status" -> "PASS_NATIVE_AFH_CHARGE_MULTIPOLE_RANK_SUM",
  "AFH_source_sha256" -> FileHash[packagePath, "SHA256", "HexString"],
  "source_file" -> packagePath,
  "isotopes" -> isotopes,
  "rank_map" -> rankMap,
  "q_grid_points" -> Length[qGrid],
  "q_min_GeV" -> First[qGrid],
  "q_max_GeV" -> Last[qGrid],
  "q_step_GeV" -> 0.00025,
  "charge_multipole_rows" -> Length[multipoleRows],
  "rank_sum_validation_rows" -> Length[validationRows],
  "multipole_file" -> FileNameTake[multipolePath],
  "validation_file" -> FileNameTake[validationPath],
  "multipole_file_sha256" -> FileHash[multipolePath, "SHA256", "HexString"],
  "validation_file_sha256" -> FileHash[validationPath, "SHA256", "HexString"],
  "max_native_imaginary_residual" -> maxImaginaryResidual,
  "max_rank_sum_absolute_residual" -> maxAbsoluteResidual,
  "max_rank_sum_relative_residual" -> maxRelativeResidual,
  "acceptance_rtol" -> 5.0*10^-7,
  "acceptance_atol" -> 2.0*10^-12,
  "response_channels" -> {"M", "PhiPP", "M_PhiPP"},
  "rank_sum_convention" -> "one quarter times coherent rank-amplitude products",
  "native_afh_charge_multipoles_validated" -> True
|>;
Export[metadataPath, metadata, "JSON"];

If[maxImaginaryResidual > 2.0*10^-12,
  Print["ERROR: native AFH charge multipole imaginary residual failed."];
  Exit[6]
];

Print["PASS_NATIVE_AFH_CHARGE_MULTIPOLE_RANK_SUM"];
Print["Charge multipole rows: ", Length[multipoleRows]];
Print["Rank-sum validation rows: ", Length[validationRows]];
Print["Maximum imaginary residual: ", ScientificForm[maxImaginaryResidual, 8]];
Print["Maximum absolute rank-sum residual: ", ScientificForm[maxAbsoluteResidual, 8]];
Print["Maximum relative rank-sum residual: ", ScientificForm[maxRelativeResidual, 8]];
Print["Output directory: ", outDir];
