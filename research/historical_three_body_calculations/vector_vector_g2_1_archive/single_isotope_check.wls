Get[FileNameJoin[{DirectoryName[$InputFileName],"three_body_rate_engine.wl"}]];
Fig2`LoadResponses[FileNameJoin[{DirectoryName[$InputFileName],"dmformfactor-V6.m"}],{131}];
mA=Global`xenonNuclearMassGeV[131];q=0.22;er=10^6 q^2/(Sqrt[mA^2+q^2]+mA);
p=<|"mchi"->1000.,"v0"->220.,"vEarth"->232.,"vEsc"->544.,"couplingSq"->10^-8,"mV"->10.,"quad"->{4,4,4},"isotopes"->{131},"abundance"-><|131->1.|>,"nv"->4,"rho"->0.3,"molarMass"->131.,"widthMode"->"pole","g2"->1.|>;
Print["q=",q," ERkeV=",er," RATE=",Fig2`Rate[er,0.0003,0.001,p]];
