(* Execute the notebook input cells as an end-to-end kernel check.
   Replace NotebookDirectory[] only for this command-line runner.
   This runs both full curves and may take several minutes. *)
Begin["notebookAudit`"];
notebookDir=DirectoryName[$InputFileName];
nb=Get[FileNameJoin[{notebookDir,"vector_vector_g2_1.nb"}]];
inputs=Cases[nb,Cell[t_String,"Input",___]:>t,Infinity];
Print["Input cells: ",Length[inputs]];
If[Length[inputs]!=15,Print["FAIL unexpected cell count"];Exit[1]];
Do[Print["CELL ",i];src=StringReplace[inputs[[i]],"NotebookDirectory[]"->"notebookAudit`notebookDir"];
 ok=CheckAbort[Check[ToExpression[src];True,False],False];If[!TrueQ[ok],Print["ABORT ",i];Exit[2]],{i,Length[inputs]}];
Print["Zero dimensions: ",Dimensions[curvesZero],"; pole dimensions: ",Dimensions[curvesPole]];
Print["Width table: ",widthTable];Print["Selected comparisons: ",compareRows];
Print["Convergence: zero coarse=",coarse0," fine=",fine0," ratio=",coarse0/fine0-1];
Print["Convergence: pole coarse=",coarse1," fine=",fine1," ratio=",coarse1/fine1-1];
If[Dimensions[curvesZero]=!={4,83,2} || Dimensions[curvesPole]=!={4,83,2} ||
 !And@@Flatten[Map[NumericQ,curvesPole,{3}]] || fine1<=0,Print["FAIL numeric shape"];Exit[3]];
Print["PASS: all notebook inputs executed"];End[];Exit[0];

