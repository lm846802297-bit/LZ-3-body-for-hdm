(* Independent kernel: patched FeynArts is kept inside this project. *)
workDir=DirectoryName[$InputFileName];projectDir=DirectoryName[workDir];
FeynCalc`$FeynArtsDirectory=FileNameJoin[{workDir,"FeynArtsPatched"}];
sourceModel=FileNameJoin[{workDir,"ThreeBodyVV.fr"}];
hashFile=FileNameJoin[{workDir,"generated_model_source_sha256.txt"}];
If[!FileExistsQ[sourceModel]||!FileExistsQ[hashFile]||ToLowerCase[FileHash[sourceModel,"SHA256","HexString"]]=!=StringTrim[Import[hashFile,"Text"]],
 Print["FeynRules source changed since FeynArts model generation; regenerate and patch the model first."];Exit[2]];
$LoadAddOns={"FeynArts"};$FeynCalcStartupMessages=False;Get["FeynCalc`"];
$PrePrint=.;$FAVerbose=0;
top=CreateTopologies[0,2->3,ExcludeTopologies->{Tadpoles,SelfEnergies}];
ins=InsertFields[top,{F[1],F[3]}->{F[1],F[3],S[1]},Model->"ThreeBodyVV_FA",GenericModel->"ThreeBodyVV_FA",InsertionLevel->{Classes}];
Print["graphs=",Length[ins]];
faamp=CreateFeynAmp[ins,PreFactor->1];
fcamp=FCFAConvert[faamp,IncomingMomenta->{p,P},OutgoingMomenta->{r,R,k},ChangeDimension->4,List->False,DropSumOver->True];
Print["FCAMP=",ToString[InputForm[fcamp],PageWidth->Infinity]];
Print["Starting spin sum..."];
sq=FermionSpinSum[fcamp ComplexConjugate[fcamp]]/4;
Print["Spin sum generated; bytecount=",ByteCount[sq]];
result=Contract[DiracSimplify[sq,DiracTraceEvaluate->True]];
Print["Dirac trace evaluated; bytecount=",ByteCount[result]];
Print["Expanding denominators..."];
expr=FeynAmpDenominatorExplicit[result];
Print["Denominators expanded bytes=",ByteCount[expr]," remaining=",Length[Cases[expr,_FeynAmpDenominator,Infinity]]];
Get[FileNameJoin[{projectDir,"three_body_rate_engine.wl"}]];
(* Exact speed conversion avoids loss of precision in TeV minus keV differences. *)
ToExpression[StringReplace[Import[FileNameJoin[{projectDir,"independent_nintegrate.wl"}],"Text"],"299792.458"->"(299792458/1000)"]];
prec=50;
args=Rest[$ScriptCommandLine];
If[Length[args]==10,
 {m,ms,dm,ma,er,v,mv,cX,cS,cN}=N[Rationalize[ToExpression[#],0],prec]& /@ args,
 {m,ms,dm,ma,er,v,mv,cX,cS,cN}=N[#,prec]& /@ {1000,3/10000,1/1000,12190992244721734/10^14,1/5000,776,10,1,1,1}
];
If[!TrueQ[m>0&&ms>=0&&dm>=0&&ma>0&&er>0&&0<v<299792458/1000&&mv>0&&cX!=0&&cS!=0&&cN!=0],Print["Invalid input or zero coupling; comparison aborted."];Exit[2]];
Print["Inputs m,ms,dm,mA,ER,v,mV,g1,g2,gN: ",N[{m,ms,dm,ma,er,v,mv,cX,cS,cN},10]];
Print["Width mode: zero for both propagators; pointlike Dirac target; no AFH response."];
kin=niKinematics[m,ms,ma,er,v,N[2/5,prec],N[1/4,prec],N[6/5,prec]];
If[kin===$Failed,Print["Phase space closed."];Exit[2]];
If[!TrueQ[(m+ms)^2+kin["delta"]<(m+dm)^2],Print["On-shell pole accessible: zero-width comparison is invalid."];Exit[2]];
pin=kin["pin"];pout=kin["pout"];kvec=kin["k"];Ptar={ma,0,0,0};Rtar=Ptar+Join[{er},kin["qvec"]];
vecs={p->pin,r->pout,k->kvec,P->Ptar,R->Rtar};
muDot[a_,b_]:=a[[1]]b[[1]]-a[[2;;4]].b[[2;;4]];
momentumValue[a_]:=a/.vecs;
num=expr/.{HoldPattern[Pair[Momentum[a_],Momentum[b_]]]:>muDot[momentumValue[a],momentumValue[b]],MChiOne->m,MChiTwo->m+dm,MNuc->ma,MMed->mv,gc1->cS,gc2->cS,gc3->cX,gc4->cX,gc5->cN};
Print["Unresolved FeynCalc objects: ",Length[Cases[num,_Pair|_FeynAmpDenominator|_DiracTrace,Infinity]]];
Print["FeynCalc amplitude squared: ",N[num,18]];
mat=Fig2`Private`id;gam={Fig2`Private`g0,Fig2`Private`g1,Fig2`Private`g2,Fig2`Private`g3};g0=First[gam];et={1,-1,-1,-1};sl=Fig2`Private`slash;
d1=muDot[pin-kvec,pin-kvec]-(m+dm)^2;d2=kin["w2"]-(m+dm)^2;
ch=Table[gam[[i]].(sl[pin-kvec]+(m+dm)mat)/d1+(sl[pout+kvec]+(m+dm)mat).gam[[i]]/d2,{i,4}];
L=Table[Tr[(sl[pout]+m mat).ch[[i]].(sl[pin]+m mat).g0.ConjugateTranspose[ch[[j]]].g0]/2,{i,4},{j,4}];
H=Table[Tr[(sl[Rtar]+ma mat).gam[[i]].(sl[Ptar]+ma mat).gam[[j]]]/2,{i,4},{j,4}];
man=Re[Sum[et[[i]]et[[j]] L[[i,j]]H[[i,j]],{i,4},{j,4}]]*(cX*cS*cN)^2/(mv^2+2ma er)^2;
Print["Independent gamma-matrix amplitude squared: ",N[man,18]];
Print["relative difference: ",N[num/man-1,8]];
If[!NumericQ[num]||Abs[N[num/man-1]]>10^-8,Exit[3]];Print["FULL POINT PASS"];Clear[fcFullME2,fcFullWeight];
fcFullME2[u_?NumericQ,z_?NumericQ,phi_?NumericQ]:=Module[{x,pIn,pOut,kOut,pT,rT,vs,momf},
 x=niKinematics[m,ms,ma,er,v,u,z,phi];If[x===$Failed,Return[0]];
 pIn=x["pin"];pOut=x["pout"];kOut=x["k"];pT={ma,0,0,0};rT=pT+Join[{er},x["qvec"]];
 vs={p->pIn,r->pOut,k->kOut,P->pT,R->rT};momf[a_]:=a/.vs;
 expr/.{HoldPattern[Pair[Momentum[a_],Momentum[b_]]]:>muDot[momf[a],momf[b]],MChiOne->m,MChiTwo->m+dm,MNuc->ma,MMed->mv,gc1->cS,gc2->cS,gc3->cX,gc4->cX,gc5->cN}
];
fcFullWeight[u_?NumericQ,z_?NumericQ,phi_?NumericQ]:=Module[{x},
 x=niKinematics[m,ms,ma,er,v,u,z,phi];If[x===$Failed,Return[0]];
 x["jac"] x["phase"] fcFullME2[u,z,phi]/(2 Pi)
];
incomingMomentum=m*(v/(299792458/1000))/Sqrt[1-(v/(299792458/1000))^2];
Print["Integrating full FeynCalc point-fermion target..."];
fullSigma=NIntegrate[fcFullWeight[u,z,phi],{u,0,1},{z,-1,1},{phi,0,2Pi},WorkingPrecision->35,AccuracyGoal->6,PrecisionGoal->6,MaxRecursion->7,Method->{"GlobalAdaptive","SymbolicProcessing"->0}]/(1024 Pi^3 ma incomingMomentum^2);
staticI6=niI6[m,ms,dm,ma,er,v,0,AccuracyGoal->6,PrecisionGoal->6,MaxRecursion->8];
staticSigma=ma*staticI6*(cX*cS*cN)^2/(256 Pi^3 incomingMomentum^2*(mv^2+2ma er)^2);
Print["FULL FEYNCALC dsigma GeV^-3=",N[fullSigma,15]];
Print["FULL FEYNCALC dsigma cm2/keV=",N[fullSigma*3893793721/10^43,15]];
Print["STATIC NOTEBOOK R=1 dsigma GeV^-3=",N[staticSigma,15]];
Print["full/static - 1=",N[fullSigma/staticSigma-1,10]];
If[!NumericQ[fullSigma]||!NumericQ[staticSigma]||!TrueQ[fullSigma>0],Exit[5]];
Exit[0];



