base=DirectoryName[$InputFileName];
Get[FileNameJoin[{base,"three_body_rate_engine.wl"}]];
iso={128,129,130,131,132,134,136};
Fig2`LoadResponses[FileNameJoin[{base,"dmformfactor-V6.m"}],iso];
ab=<|128->0.019102,129->0.264006,130->0.040710,131->0.212324,132->0.269086,134->0.104357,136->0.088573|>;
p=<|"mchi"->1000.,"mV"->10.,"couplingSq"->1.*10^-8,"rho"->0.3,"v0"->220.,"vEarth"->232.,"vEsc"->544.,"molarMass"->131.293,"isotopes"->iso,"abundance"->ab,"g2"->1.|>;
bench={{200.,1.,300.},{300.,1.,200.},{360.,1.,300.},{300.,10.,300.}};
rows=Flatten[Table[
 ms=b[[1]] 10^-6; dm=b[[2]] 10^-3; er=b[[3]];
 Print["Convergence ",i," / 4 ",mode];
 pc=Join[p,<|"quad"->{6,6,4},"nv"->6,"widthMode"->mode|>];
 pf=Join[p,<|"quad"->{12,12,8},"nv"->12,"widthMode"->mode|>];
 c=Fig2`Rate[er,ms,dm,pc];f=Fig2`Rate[er,ms,dm,pf];
 {i,b[[1]],b[[2]],er,mode,c,f,If[f>0,c/f-1,"closed"]},
 {i,Length[bench]},{b,{bench[[i]]}},{mode,{"zero","pole"}}],2];
Export[FileNameJoin[{base,"g2_output","four_benchmark_convergence.csv"}],
 Prepend[rows,{"benchmark","ms_keV","delta_m_MeV","ER_keV","width_mode","coarse","fine","relative_coarse_vs_fine"}],"CSV"];
Print["Results:"];Scan[Print,rows];
If[Length[rows]!=8||!And@@(NumberQ[#[[6]]]&&NumberQ[#[[7]]]&/@rows),Print["FAIL"];Exit[1]];
Print["PASS all convergence points evaluated"];Exit[0];
