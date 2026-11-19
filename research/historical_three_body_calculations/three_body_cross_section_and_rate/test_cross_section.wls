Get[FileNameJoin[{DirectoryName[$InputFileName],"three_body_rate_engine.wl"}]];
Fig2`LoadResponses[FileNameJoin[{DirectoryName[$InputFileName],"dmformfactor-V6.m"}],{131}];
failures=0;
check[name_,condition_]:=If[TrueQ[condition],Print["PASS: ",name],Print["FAIL: ",name];failures++];
p=<|"mchi"->1000.,"mV"->10.,"couplingSq"->1.*10^-8,"g2"->1.,
 "rho"->0.3,"v0"->220.,"vEarth"->232.,"vEsc"->544.,"molarMass"->131.,
 "isotopes"->{131},"abundance"-><|131->1.|>,"quad"->{16,16,8},"nv"->4,
 "widthMode"->"pole"|>;
mA=Global`xenonNuclearMassGeV[131];q=0.22;er=10^6 q^2/(Sqrt[mA^2+q^2]+mA);
r=Fig2`NuclearResponse[131,er];
check["nuclear response at exact q",NumericQ[r] && Abs[r/10.111501574504262-1]<10^-10];
check["nuclear response at zero",NumericQ[Fig2`NuclearResponse[131,0.]] && Abs[Fig2`NuclearResponse[131,0.]/131^2-1]<10^-12];
pole=Fig2`DifferentialCrossSection[131,er,776.,0.0003,0.001,p];
check["pole cross section matches AME2020 GeV^-3",NumericQ[pole] && Abs[pole/(1.9671732880157643*10^-8)-1]<10^-8];
closed=Fig2`DifferentialCrossSection[131,10.,776.,0.0003,0.001,p];
check["closed phase space returns zero",NumericQ[closed] && closed==0];
If[failures>0,Print["FAILED checks: ",failures];Exit[1],Print["PASS all fixed-speed checks"];Exit[0]];

