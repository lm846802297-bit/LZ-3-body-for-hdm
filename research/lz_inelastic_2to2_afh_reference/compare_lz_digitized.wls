(* Load the AFH total spectrum and digitized points from the paper figure. *)
directory=DirectoryName[$InputFileName];
afhRows=Rest[Import[FileNameJoin[{directory,"lz_inelastic_o1_spectra.csv"}],"CSV"]];
lzRows=Rest[Import[FileNameJoin[{directory,"lz_fig1_digitized_long.csv"}],"CSV"]];

(* Match AFH CSV columns to delta = 0, 200, and 300 keV. *)
afCurves=Table[With[{column=Switch[delta,0,2,200,3,300,4]},Select[({#[[1]],#[[column]]}&/@afhRows),Last[#]>0&]],{delta,{0,200,300}}];

(* Read each LZ curve as {ER, rate}; these values were digitized from the PDF plot. *)
lzCurves=Table[Select[({#[[2]],#[[3]]}&/@Select[lzRows,#[[1]]==delta&]),Last[#]>0&],{delta,{0,200,300}}];

(* Interleave the LZ solid curve and AFH dashed curve for each splitting. *)
comparisonCurves=Flatten[Table[{lzCurves[[i]],afCurves[[i]]},{i,3}],1];
comparisonStyles={Directive[Blue,Thick],Directive[Blue,Dashed,Thick],Directive[Orange,Thick],Directive[Orange,Dashed,Thick],Directive[Darker[Green],Thick],Directive[Darker[Green],Dashed,Thick]};
comparisonLabels={"LZ digitized delta=0 keV","AFH delta=0 keV","LZ digitized delta=200 keV","AFH delta=200 keV","LZ digitized delta=300 keV","AFH delta=300 keV"};

(* Overlay the independently computed AFH rates and digitized LZ curves on identical log axes. *)
lzAfhOverlay=ListLogPlot[comparisonCurves,Joined->True,PlotStyle->comparisonStyles,PlotRange->{{0,350},{10^-1,10^9}},Frame->True,FrameLabel->{"True recoil energy ER (keV)","dR/dER [events/(tonne year keV)]"},PlotLegends->Placed[comparisonLabels,Below],GridLines->Automatic,ImageSize->1100,PlotLabel->"LZ Figure 1 top: paper digitization (solid) and AFH v6 (dashed)",Epilog->{Directive[Gray,Opacity[0.20]],Rectangle[{0,10^-1},{5.4,10^9}],Rectangle[{269.9,10^-1},{350,10^9}]}];
Export[FileNameJoin[{directory,"lz_fig1_vs_afh_overlay.png"}],lzAfhOverlay,ImageResolution->180];
comparisonTableRows=Rest[Import[FileNameJoin[{directory,"lz_overlay_benchmark_comparison.csv"}],"CSV"]];
comparisonTable=Grid[Prepend[comparisonTableRows,{"delta keV","ER keV","LZ digitized rate","AFH rate","LZ/AFH"}],Frame->All];
Print[comparisonTable];
