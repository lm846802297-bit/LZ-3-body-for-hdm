Get[FileNameJoin[{DirectoryName[$InputFileName],"three_body_rate_engine.wl"}]];
iso={128,129,130,131,132,134,136};Fig2`LoadResponses[FileNameJoin[{DirectoryName[$InputFileName],"dmformfactor-V6.m"}],iso];
p=<|"mchi"->1000.,"mV"->10.,"couplingSq"->1.*10^-8,"g2"->1.,
 "rho"->0.3,"v0"->220.,"vEarth"->232.,"vEsc"->544.,"molarMass"->131.293,
 "isotopes"->iso,"abundance"-><|128->.019102,129->.264006,130->.040710,131->.212324,132->.269086,134->.104357,136->.088573|>,
 "quad"->{6,6,4},"nv"->6,"widthMode"->"pole"|>;
cases={{200.,.0003,.001,6.71123654356748*10^-6},{300.,.0002,.001,3.819054268857729*10^-5},{300.,.00036,.001,1.3920925267733454*10^-9},{300.,.0003,.01,9.076712549855385*10^-9}};
Do[value=Fig2`Rate[c[[1]],c[[2]],c[[3]],p];
 Print["Rate ",c[[1;;3]]," = ",value," relative to previous = ",value/c[[4]]-1];
 If[!TrueQ[Abs[value/c[[4]]-1]<10^-10],Exit[1]],{c,cases}];
Print["PASS: halo rates preserve prior results at four physical points."];Exit[0];
