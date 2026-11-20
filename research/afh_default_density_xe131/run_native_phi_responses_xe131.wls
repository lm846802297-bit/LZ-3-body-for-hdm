(* AME2020 xenon nuclear mass from atomic masses and CODATA-2022 constants. *)
Global`ame2020XenonAtomicMassU=<|124->123905885174/10^9,126->125904297422/10^9,128->12790353075341/10^11,129->12890478085742/10^11,130->129903509346/10^9,131->13090508412808/10^11,132->13190415508346/10^11,134->133905393030/10^9,136->135907214474/10^9|>;
Global`xenonZ=54; Global`xenonAtomicMassUnitGeV=93149410372/10^11; Global`electronMassU=5485799090441/10^16;
Global`xenonElectronBindingEnergyGeV=N[(144381/10^4 Global`xenonZ^(239/100)+155468/10^11 Global`xenonZ^(535/100))10^-9,30];
Global`xenonNuclearMassGeV[A_Integer]:=Module[{mAtom=Lookup[Global`ame2020XenonAtomicMassU,A,Null]},If[mAtom===Null,Return[$Failed]];N[(mAtom-Global`xenonZ Global`electronMassU)Global`xenonAtomicMassUnitGeV+Global`xenonElectronBindingEnergyGeV,20]];
(* Native AFH v6.0 Xe-131 Phi'' and M-Phi'' responses. *)
ClearAll["Global`*"];
scriptDir = DirectoryName[$InputFileName];
packagePath = FileNameJoin[{scriptDir, "..", "..", "v6", "dmformfactor-V6.m"}];
If[!FileExistsQ[packagePath], Print["ERROR: AFH v6 package not found: ", packagePath]; Exit[2]];
Get[packagePath];
A = 131; Z = 54; JA = 3/2; mA = Global`xenonNuclearMassGeV[A];
fmToGeVInv = 5.0677; qMax = 0.60; dq = 0.00025;
bFM = Sqrt[41.467/(45.0 A^(-1.0/3.0) - 25.0 A^(-2.0/3.0))];
bGeVInv = bFM*fmToGeVInv;
SetIsotope[Z, A, "default", "default"];
wmExpr = ResponseNuclear[y, 1, 0, 0];
phiExpr = ResponseNuclear[y, 4, 0, 0];
mPhiExpr = ResponseNuclear[y, 7, 0, 0];
If[!FreeQ[{phiExpr, mPhiExpr}, ResponseNuclear] || phiExpr === $Failed || mPhiExpr === $Failed,
  Print["ERROR: native AFH responses failed to evaluate."]; Exit[3]];
qGrid = N[Range[0, Round[qMax/dq]]*dq, 16];
rows = Table[Module[{q=qGrid[[i]], yy, wp, wmp, er, csResidual},
  yy=(q*bGeVInv/2.0)^2;
  wp=N[phiExpr /. y->yy, 30]; wmp=N[mPhiExpr /. y->yy, 30];
  er=(Sqrt[mA^2+q^2]-mA)*10^6;
  csResidual=If[wp >= 0, Max[0., Abs[wmp]^2 - N[wmExpr /. y->yy,30]*wp], Indeterminate];
  {q, yy, er, N[wmExpr /. y->yy, 20], wp, wmp, csResidual}
], {i,Length[qGrid]}];
outDir=FileNameJoin[{scriptDir,"output","native_phi_response"}];
If[!DirectoryQ[outDir],CreateDirectory[outDir,CreateIntermediateDirectories->True]];
csvPath=FileNameJoin[{outDir,"afh_xe131_phi_responses_native.csv"}];
Export[csvPath,Prepend[rows,{"q_GeV","y","ER_keV_A_times_0p93149410242","W_M00_AFH","W_PhiPP00_AFH","W_M_PhiPP00_AFH","CS_excess_if_WM_available"}],"CSV"];
meta={"source = official AFH DMFormFactor v6.0 source file", "isotope = Xe-131; A=131; Z=54; J=3/2",
"SetIsotope[54,131,\"default\",\"default\"]", "response index 4 = Phi''; index 7 = M Phi'' (AFH ResponseNuclear mapping)",
"isospin = (tau1,tau2)=(0,0); raw AFH package convention; no extra normalization applied",
"q = 0..0.600 GeV, step 0.00025 GeV, 2401 inclusive nodes", "y=(q*b_A/2)^2; b_A uses AFH default oscillator prescription and 5.0677 GeV^-1/fm",
"b_A_fm = "<>ToString[InputForm[N[bFM,16]]],"W_M00, W_PhiPP00, W_M_PhiPP00 are direct native ResponseNuclear outputs",
"W_M00 included to evaluate the response-matrix Cauchy-Schwarz bound pointwise"};
Export[FileNameJoin[{outDir,"metadata.txt"}],StringRiffle[meta,"\n"]<>"\n","Text"];
Print["Native AFH Xe-131 Phi'' and M-Phi'' calculation complete."];
Print["Grid points: ",Length[rows],"; q range: 0 to ",Last[qGrid]," GeV"];
Print["b_A = ",N[bFM,12]," fm"];
Print["CSV: ",csvPath];
