base=DirectoryName[DirectoryName[$InputFileName]];Get[FileNameJoin[{base,"figure2_engine.wl"}]];Get[FileNameJoin[{base,"independent_nintegrate.wl"}]];
m=1000.;ms=.0003;dm=.001;ma=131*.93149410242;v=776.;g=Fig2`Chi2Width[m,ms,dm,1.];
ers={101.,109.16,110.,150.,200.,267.,300.,542.,654.94,700.};orders={{6,6,4},{12,12,8},{16,16,8},{24,24,12}};
rows=Table[With[{er=e 10^-6},
 Module[{vals,ni},vals=Table[Fig2`I6[m,ms,dm,ma,er,v,o,g],{o,orders}];ni=niI6[m,ms,dm,ma,er,v,g,AccuracyGoal->4,PrecisionGoal->4,MaxRecursion->7];
 Print["ER=",e," Gauss=",vals," NI=",ni];{e,Sequence@@vals,ni}]],{e,ers}];

Export[FileNameJoin[{base,"mma_i6_convergence.csv"}],Prepend[rows,{"ER_keV","gauss6","gauss12","gauss16","gauss24","nintegrate"}],"CSV"] ;


