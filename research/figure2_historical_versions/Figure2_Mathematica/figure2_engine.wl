(* Figure 2 2->3 nuclear recoil rate. All energies/masses GeV, speed km/s. *)
(* Scope: Dirac benchmark, AFH nuclear charge response, zero-width/off-shell. *)
ClearAll["Fig2`*"];
BeginPackage["Fig2`"];
LoadResponses::usage="LoadResponses[path, isotopes] loads AFH and freezes a response for each isotope.";
I6::usage="I6[m,ms,dm,mA,er,v,{nw,nz,nphi}] computes coherent three-body integral.";
VMin::usage="VMin[m,ms,mA,er] is the threshold speed in km/s.";
SpeedPDF::usage="SpeedPDF[v,v0,ve,vesc] is the normalized truncated lab speed PDF.";
Rate::usage="Rate[erKeV,ms,dm,parameters] returns events/(tonne year keV).";
MakeCurves::usage="MakeCurves[energies,benchmarks,parameters] evaluates every curve.";
Begin["`Private`"];
cKm=299792.458; cCm=2.99792458*10^10; GeV2cm2=0.3893793721*10^-27;
(* GL weights from Jacobi matrix. The angular phi weights sum to one. *)
gl[n_Integer?Positive]:=gl[n]=Module[{b,vals,vec,order},
 b=Table[k/Sqrt[4. k^2-1.],{k,1,n-1}];
 {vals,vec}=Eigensystem[DiagonalMatrix[b,1]+DiagonalMatrix[b,-1]];
 order=Ordering[vals]; Transpose[{vals[[order]],2 (vec[[order,1]])^2}]];
mdot[a_,b_]:=a[[1]] b[[1]]-a[[2;;4]].b[[2;;4]];
boost[a_,beta_]:=Module[{b2=beta.beta,g,p},
 If[b2<10^-30,Return[a]]; If[b2>=1,Throw["Invalid boost"]];
 g=1/Sqrt[1-b2]; p=a[[2;;4]].beta;
 Join[{g(a[[1]]+p)},a[[2;;4]]+(((g-1)p/b2)+g a[[1]]) beta]];
i2=IdentityMatrix[2];z2=ConstantArray[0,{2,2}];
s1={{0,1},{1,0}};s2={{0,-I},{I,0}};s3={{1,0},{0,-1}};
g0=ArrayFlatten[{{i2,z2},{z2,-i2}}];
g1=ArrayFlatten[{{z2,s1},{-s1,z2}}];
g2=ArrayFlatten[{{z2,s2},{-s2,z2}}];
g3=ArrayFlatten[{{z2,s3},{-s3,z2}}]; id=IdentityMatrix[4];
slash[p_]:=g0 p[[1]]-g1 p[[2]]-g2 p[[3]]-g3 p[[4]];
trace[pin_,pp_,k_,m_,m2_,w2_]:=Module[{d1,d2,gb,ga,g,bar},
 d1=mdot[pin-k,pin-k]-m2^2;d2=w2-m2^2;
 If[Abs[d1]<10^-12 || Abs[d2]<10^-12,Throw["Propagator pole: zero-width approximation invalid"]];
 gb=g0.(slash[pin-k]+m2 id)/d1;
 ga=(slash[pp+k]+m2 id).g0/d2;
 g=gb+ga;bar=g0.ConjugateTranspose[g].g0;
 Re[Tr[(slash[pp]+m id).g.(slash[pin]+m id).bar]]/2];
I6[m_?NumericQ,ms_?NumericQ,dm_?NumericQ,mA_?NumericQ,er_?NumericQ,v_?NumericQ,order_List]:=Module[
 {beta,lor,ee,pz,qq,wlo,whi,pin,quadrW,quadrZ,quadrP,sum=0.,w2,weight,cq,q,K,bK,ps,e3,ref,e1,e2,lam,W,kabs,Ek,Ep,z,phi,n,k,pp,ang,pa,m2},
 If[er<=0 || v<=0,Return[0.]];
 beta=v/cKm;lor=1/Sqrt[1-beta^2];ee=m lor;pz=m lor beta;qq=Sqrt[2 mA er+er^2];
 wlo=(m+ms)^2;whi=m^2+2 pz qq-2(ee+mA)er;
 If[whi<=wlo,Return[0.]];
 m2=m+dm;
 If[whi>=m2^2,Throw["On-shell chi2 accessible: zero-width calculation aborted"]];
 pin={ee,0.,0.,pz};quadrW=gl[order[[1]]];quadrZ=gl[order[[2]]];quadrP=gl[order[[3]]];
 Do[
  w2=(whi+wlo)/2+(whi-wlo)node[[1]]/2;weight=node[[2]](whi-wlo)/2;
  cq=Clip[(w2-m^2+2(ee+mA)er)/(2 pz qq),{-1.,1.}];
  q={er,qq Sqrt[Max[0.,1-cq^2]],0.,qq cq};K=pin-q;bK=K[[2;;4]]/K[[1]];
  ps=boost[pin,-bK];e3=Normalize[ps[[2;;4]]];ref=If[Abs[e3[[1]]]>.9,{0.,1.,0.},{1.,0.,0.}];
  e1=Normalize[Cross[ref,e3]];e2=Cross[e3,e1];
  lam=Max[0.,(w2-(m+ms)^2)(w2-(m-ms)^2)]; W=Sqrt[w2];
  kabs=Sqrt[lam]/(2 W);Ek=(w2-m^2+ms^2)/(2 W);Ep=(w2+m^2-ms^2)/(2 W);
  ang=0.;Do[z=zn[[1]];pa=0.;Do[phi=Pi(pn[[1]]+1);
   n=z e3+Sqrt[Max[0.,1-z^2]](Cos[phi] e1+Sin[phi] e2);
   k=boost[Join[{Ek},kabs n],bK];pp=boost[Join[{Ep},-kabs n],bK];
   pa+=pn[[2]]/2 trace[pin,pp,k,m,m2,w2],{pn,quadrP}];
   ang+=zn[[2]] pa,{zn,quadrZ}];
  sum+=weight Sqrt[lam]/w2 ang,{node,quadrW}];sum];
VMin[m_,ms_,mA_,er_]:=Module[{q,a},If[er<=0,Return[Infinity]];
 q=Sqrt[2 mA er+er^2];a=ms+(mA er+ms^2/2)/m;
 cKm (q er+a Sqrt[q^2-er^2+a^2])/(q^2+a^2)];
SpeedPDF[v_,v0_,ve_,vesc_]:=Module[{z,n,b},
 If[v<0 || v>=vesc+ve,Return[0.]];
 z=vesc/v0;n=Erf[z]-2 z Exp[-z^2]/Sqrt[Pi];
 b=If[v<vesc-ve,Exp[-((v-ve)/v0)^2]-Exp[-((v+ve)/v0)^2],Exp[-((v-ve)/v0)^2]-Exp[-z^2]];
 v b/(Sqrt[Pi] v0 ve n)];
(* Normalization R(0)=A^2 removes finite-precision density table offset. *)
LoadResponses[path_String,isotopes_List]:=Module[{expr,aa,b},
 If[!FileExistsQ[path],Throw["AFH package missing"]];Get[path];
 Do[aa=iso;dmformfactor`SetIsotope[54,aa,"default","default"];
 expr=dmformfactor`ResponseNuclear[Global`y,1,0,0];
 If[!NumericQ[N[expr/.Global`y->0]],Throw["AFH response failed"]];
 b=5.0677 Sqrt[41.467/(45. aa^(-1./3.)-25. aa^(-2./3.))];
 responseExpr[aa]=expr;responseZero[aa]=N[expr/.Global`y->0];bInv[aa]=b,
 {iso,isotopes}];isotopes];
response[a_,er_,mA_]:=a^2 N[responseExpr[a]/.Global`y->((Sqrt[2 mA er+er^2] bInv[a]/2)^2)]/responseZero[a];
Rate[erKeV_?NumericQ,ms_?NumericQ,dm_?NumericQ,p_Association]:=Module[
 {er=erKeV 10^-6,m=p["mchi"],v0=p["v0"],ve=p["vEarth"],vesc=p["vEsc"],coupling=p["couplingSq"],mv=p["mV"],order=p["quad"],isotopes=p["isotopes"],weights=p["abundance"],nv=p["nv"],rho=p["rho"],sum=0.,mA,vmin,vmax,acc,v,w,pchi,conv},
 vmax=ve+vesc;
 Do[mA=a 0.93149410242;vmin=VMin[m,ms,mA,er];
 If[vmin<vmax,acc=0.;Do[v=(vmax+vmin)/2+(vmax-vmin)node[[1]]/2;w=node[[2]](vmax-vmin)/2;
 pchi=m(v/cKm)/Sqrt[1-(v/cKm)^2];
 acc+=w SpeedPDF[v,v0,ve,vesc] (v/cKm) mA coupling/(256 Pi^3 pchi^2) I6[m,ms,dm,mA,er,v,order],{node,gl[nv]}];
 sum+=weights[a] acc response[a,er,mA]/(mv^2+2 mA er)^2],{a,isotopes}];
 (* isotope weights are number fractions; average target molar mass is explicit *)
 conv=(rho/m) cCm (6.02214076 10^23 1000/p["molarMass"]) GeV2cm2 10^-6 86400 365250;
 conv sum];
MakeCurves[energies_List,bench_List,p_Association]:=Table[
 Print["Computing benchmark ",i," / ",Length[bench],"; ms,dm = ",bench[[i]]];
 Table[{er,Rate[er,bench[[i,1]] 10^-6,bench[[i,2]] 10^-3,p]}, {er,energies}],{i,Length[bench]}];
End[];EndPackage[];

