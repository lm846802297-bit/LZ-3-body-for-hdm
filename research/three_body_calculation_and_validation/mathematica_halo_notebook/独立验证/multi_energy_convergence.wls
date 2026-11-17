base=DirectoryName[DirectoryName[$InputFileName]];Get[FileNameJoin[{base,"three_body_rate_engine.wl"}]];Get[FileNameJoin[{DirectoryName[base],"independent_nintegrate.wl"}]];
m=1000.;ms=.0003;dm=.001;ma=Fig2`XenonNuclearMassGeV[131];v=776.;g=Fig2`Chi2Width[m,ms,dm,1.];
ers={101.,109.16,110.,150.,200.,267.,300.,542.,654.94,700.};orders={{6,6,4},{12,12,8},{16,16,8},{24,24,12}};
rows=Table[With[{er=e 10^-6},
 Module[{vals,ni,beta,Ein,pin,qmag,wmax},vals=Table[Fig2`I6[m,ms,dm,ma,er,v,o,g],{o,orders}];beta=v/(299792458/1000);Ein=m/Sqrt[1-beta^2];pin=Ein beta;qmag=Sqrt[er(2ma+er)];wmax=m^2+2pin qmag-2(Ein+ma)er;If[wmax>=(m+dm)^2,Throw["On-shell chi2 accessible"]];ni=If[wmax<=(m+ms)^2,0.,NIntegrate[niIntegrand[m,ms,dm,ma,er,v,g,u,z,phi],{u,0,1},{z,-1,1},{phi,0,2Pi},Method->{"GlobalAdaptive","SymbolicProcessing"->0},AccuracyGoal->4,PrecisionGoal->4,MaxRecursion->7]];
 Print["ER=",e," Gauss=",vals," NI=",ni];{e,Sequence@@vals,ni}]],{e,ers}];

outputDirectory=FileNameJoin[{DirectoryName[DirectoryName[base]],"three_body_natural_xenon",FromCharacterCode[{29420,31435,39564,35777}]}];
If[!DirectoryQ[outputDirectory],CreateDirectory[outputDirectory,CreateIntermediateDirectories->True]];
Export[FileNameJoin[{outputDirectory,"mma_i6_convergence.csv"}],Prepend[rows,{"ER_keV","gauss6","gauss12","gauss16","gauss24","nintegrate"}],"CSV"];


