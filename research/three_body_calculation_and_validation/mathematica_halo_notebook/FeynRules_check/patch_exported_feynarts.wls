root=DirectoryName[$InputFileName];modelDir=FileNameJoin[{root,"ThreeBodyVV_FA"}];
patched=FileNameJoin[{root,"FeynArtsPatched"}];custom=FileNameJoin[{patched,"CustomModel"}];
exportHash=FileNameJoin[{root,"feynarts_export_source_sha256.txt"}];
If[!FileExistsQ[exportHash]||ToLowerCase[FileHash[FileNameJoin[{root,"ThreeBodyVV.fr"}],"SHA256","HexString"]]=!=StringTrim[Import[exportHash,"Text"]],
 Print["FeynRules source differs from export; run export_feynarts.wls first."];Exit[2]];
If[!DirectoryQ[custom],CreateDirectory[custom]];
Do[CopyFile[FileNameJoin[{modelDir,"ThreeBodyVV_FA."<>ext}],FileNameJoin[{custom,"ThreeBodyVV_FA."<>ext}],OverwriteTarget->True],{ext,{"gen","mod"}}];
$LoadFeynArts=False;Get["FeynCalc`"];
FeynCalc`$FeynArtsDirectory=patched;
FAPatch[Quiet->True,PatchModelsOnly->True,FAModelsDirectory->custom];
Do[CopyFile[FileNameJoin[{custom,"ThreeBodyVV_FA."<>ext}],FileNameJoin[{patched,"Models","ThreeBodyVV_FA."<>ext}],OverwriteTarget->True],{ext,{"gen","mod"}}];
Export[FileNameJoin[{root,"generated_model_source_sha256.txt"}],FileHash[FileNameJoin[{root,"ThreeBodyVV.fr"}],"SHA256","HexString"],"Text"];
Print["Custom FeynArts model patched and source hash recorded."];Exit[0];
