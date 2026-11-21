(* Native AFH v6.0 export for spatial nuclear responses. *)
ClearAll["Global`*"];
scriptDir = DirectoryName[$InputFileName];
repoRoot = DirectoryName[DirectoryName[scriptDir]];
envPath = Environment["DMFormFactorPath"];
packagePath = If[StringQ[envPath] && envPath =!= "", envPath, FileNameJoin[{repoRoot,"v6","dmformfactor-V6.m"}]];
If[!FileExistsQ[packagePath], Print["ERROR: AFH source not found: ",packagePath]; Exit[2]];
Get[packagePath];
qGrid={0.,0.05,0.10,0.158,0.20,0.25625,0.30,0.365,0.45,0.49925,0.60};
outDir=FileNameJoin[{scriptDir,"output","spatial_native"}];
If[!DirectoryQ[outDir],CreateDirectory[outDir,CreateIntermediateDirectories->True]];
Do[
 A=isotope; Z=54; SetIsotope[Z,A,"default","default"];
 bFM=Sqrt[41.467/(45.0 A^(-1.0/3.0)-25.0 A^(-2.0/3.0))]; bGeVInv=bFM*5.0677;
 exprs=Table[ResponseNuclear[y,i,0,0],{i,{1,3,6,8}}];
 rows=Table[Module[{q=qGrid[[k]],yy,vals},yy=(q bGeVInv/2.0)^2;vals=N[exprs/.y->yy,30];{A,q,yy,Sequence@@vals}],{k,Length[qGrid]}];
 path=FileNameJoin[{outDir,"afh_xe"<>ToString[A]<>"_spatial_native.csv"}];
 Export[path,Prepend[rows,{"A","q_GeV","y","W_M00_AFH","W_SigmaPrime00_AFH","W_Delta00_AFH","W_SigmaPrimeDelta00_AFH"}],"CSV"];
 Print["Wrote ",path],{isotope,{129,131}}];
Export[FileNameJoin[{outDir,"metadata.txt"}],"AFH v6.0 native ResponseNuclear indices 1,3,6,8; isoscalar tau=0; no factor-four rescaling; nuclear response only.","Text"];
Print["Native AFH spatial response export completed."];
