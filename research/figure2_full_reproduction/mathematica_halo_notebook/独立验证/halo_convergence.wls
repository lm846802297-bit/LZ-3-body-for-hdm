base=DirectoryName[DirectoryName[$InputFileName]];Get[FileNameJoin[{base,"figure2_engine.wl"}]];
iso={128,129,130,131,132,134,136};abu=<|128->.019102,129->.264006,130->.040710,131->.212324,132->.269086,134->.104357,136->.088573|>;
Fig2`LoadResponses[FileNameJoin[{base,"dmformfactor-V6.m"}],iso];
p=<|"mchi"->1000.,"mV"->10.,"g2"->1.,"couplingSq"->1.,"rho"->.3,"v0"->220.,"vEarth"->232.,"vEsc"->544.,"molarMass"->131.293,"isotopes"->iso,"abundance"->abu,"quad"->{6,6,4},"nv"->6,"widthMode"->"pole"|>;
orders={{{6,6,4},6},{{12,12,8},6},{{12,12,8},12},{{16,16,8},16}};
rows=Table[Module[{x=Table[Fig2`Rate[e,.0003,.001,Join[p,<|"quad"->o[[1]],"nv"->o[[2]]|>]],{o,orders}]},Print["ER=",e," rates=",x];{e,Sequence@@x}],{e,{110.,200.,267.,542.}}];
Export[FileNameJoin[{base,"convergence_halo.csv"}],Prepend[rows,{"ER_keV","quad6_v6","quad12_v6","quad12_v12","quad16_v16"}],"CSV"];
