(* Direct off-grid responses for the AME2020 recoil energies used in this fold. *)
study = DirectoryName[$InputFileName];
repo = DirectoryName[study, 3];
package = FileNameJoin[{repo, "v6", "dmformfactor-V6.m"}];
If[IntegerString[FileHash[package, "SHA256"], 16, 64] =!=
  "dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372", Exit[2]];
Get[package];
massFile = FileNameJoin[{repo, "research", "afh_default_density_xe131", "output",
    "ame2020_exact_spatial_xe131_partial", "xenon_isotope_ame2020_masses.csv"}];
massTable = Import[massFile, "CSV"];
massColumn = First@FirstPosition[First@massTable, "mA_AME2020_CODATA2022_GeV"];
isotopes = {128, 129, 130, 131, 132, 134, 136};
energies = Union[Range[0, 1000, 2], Range[241, 295, 2], {101}];
outDir = FileNameJoin[{study, "output"}];
If[!DirectoryQ[outDir], CreateDirectory[outDir, CreateIntermediateDirectories -> True]];
channels = {"M", "SigmaDoublePrime", "SigmaPrime", "PhiPP", "PhiTildePrime", "Delta",
   "MPhiPP", "SigmaPrimeDelta"};
header = Join[{"A", "ER_keV", "Q_A_GeV", "y_A", "max_abs_imaginary"}, channels];
records = Flatten[Table[
   SetIsotope[54, aa, "default", "default"];
   mass = SelectFirst[Rest[massTable], First[#] == aa &][[massColumn]];
   bInvGeV = 5.0677 Sqrt[41.467/(45. aa^(-1./3.) - 25. aa^(-2./3.))];
   expressions = Table[ResponseNuclear[yy, idx, 0, 0], {idx, 8}];
   Print["Xe-", aa, "  ", Length[energies], " recoil energies"];
   Table[Module[{er = en 10.^-6, q, yValue, w},
      q = Sqrt[er (2 mass + er)];
      yValue = (q bInvGeV/2)^2;
      w = N[expressions /. yy -> yValue];
      If[!VectorQ[w, NumericQ] || Max[Abs[Im[w]]] > 2 10^-12, Exit[3]];
      Join[{aa, en, q, yValue, Max[Abs[Im[w]]]}, Re[w]]
    ], {en, energies}], {aa, isotopes}], 1];
Export[FileNameJoin[{outDir, "native_recoil_responses.csv"}], Prepend[records, header], "CSV"];
Print[$Version, "  ", Length[records], " response rows."];
