(* Evaluate the notebook's input cells in order, without requiring a front end. *)
base = DirectoryName[DirectoryName[$InputFileName]];
paths = FileNames["Elastic_Vector_AFH_vs_Direct.nb", base, Infinity];
If[Length[paths] != 1, Print["FAIL: notebook not found uniquely"]; Exit[1]];
folder = DirectoryName[First[paths]];
notebook = Get[First[paths]];
cells = Cases[notebook, Cell[s_String, "Input", ___] :> s, Infinity];
If[Length[cells] != 2, Print["FAIL: expected two input cells"]; Exit[1]];
Do[ToExpression[StringReplace[cell, "NotebookDirectory[]" -> ToString[InputForm[folder]]]], {cell, cells}];
If[!ValueQ[rows] || Max[Abs[rows[[All, 4]]]] > 10^-8, Exit[1]];
Print["PASS: notebook input cells ran in order."];
