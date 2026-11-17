root=DirectoryName[$InputFileName];base=FileNameJoin[{root,"feynrules-current"}];
$FeynRulesPath=base;FR$Parallel=False;FeynRules`MatrixSymbol;
Get[FileNameJoin[{base,"FeynRules.m"}]];SetDirectory[root];
LoadModel[FileNameJoin[{root,"ThreeBodyVV.fr"}]];
WriteUFO[LInteraction,Output->"ThreeBodyVV_UFO",AddDecays->False];
(* FeynRules 2.3.49 ships two Python-2 raise statements; make them Python 3 compatible. *)
lib=FileNameJoin[{root,"ThreeBodyVV_UFO","object_library.py"}];
If[FileExistsQ[lib],
 source=Import[lib,"Text"];
 source=StringReplace[source,"raise UFOError, \"UFO does not support yet more than one occurence of CTParameters in the couplings values.\"" -> "raise UFOError(\"UFO does not support yet more than one occurence of CTParameters in the couplings values.\")"];
 Export[lib,source,"Text"];Print["Patched Python 3 raise syntax."]];
Print["UFO exists=",DirectoryQ[FileNameJoin[{root,"ThreeBodyVV_UFO"}]]];
