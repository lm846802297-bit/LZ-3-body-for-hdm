Get[FileNameJoin[{DirectoryName[DirectoryName[$InputFileName]],"three_body_rate_engine.wl"}]];Fig2`LoadResponses[FileNameJoin[{DirectoryName[DirectoryName[$InputFileName]],"dmformfactor-V6.m"}],{131}];
p=<|"mchi"->1000.,"mV"->10.,"g2"->1.,"couplingSq"->1.,"quad"->{10,10,6},"widthMode"->"pole"|>;
f[c_,v_,ms_]:=Fig2`DifferentialCrossSection[131,200.,v,ms,.001,Join[p,<|"couplingSq"->c|>]];
a=f[1.,776.,.0003];b=f[4.,776.,.0003];c=f[1.,400.,.0003];
Print["base=",a," coupling x4=",b," ratio=",b/a," closed v400=",c];
