root=DirectoryName[$InputFileName];base=FileNameJoin[{root,"feynrules-current"}];
$FeynRulesPath=base;FR$Parallel=False;FeynRules`MatrixSymbol;
Get[FileNameJoin[{base,"FeynRules.m"}]];SetDirectory[root];
LoadModel[FileNameJoin[{root,"ThreeBodyVV.fr"}]];
WriteFeynArtsOutput[LInteraction,Output->"ThreeBodyVV_FA"];
Export[FileNameJoin[{root,"feynarts_export_source_sha256.txt"}],FileHash[FileNameJoin[{root,"ThreeBodyVV.fr"}],"SHA256","HexString"],"Text"];
Print["FeynArts output exported; source hash saved."];
