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

(* Static nucleus charge current: project nuclear line to 2 m_A delta^mu_0. *)
projected=fcamp /. HoldPattern[Dot[Spinor[Momentum[R],___],middle__,Spinor[Momentum[P],___]]] :> 2 MNuc;
If[!FreeQ[projected,Spinor[Momentum[P|R],___]],Print["Nuclear projection failed."];Exit[3]];
projected=projected /. {HoldPattern[Pair[LorentzIndex[_],LorentzIndex[_]]]->1,HoldPattern[DiracGamma[LorentzIndex[_]]]:>FeynCalc`GA[0]};
(* Add the pole width only to the p-prime + k internal line, as in the paper. *)
projected=projected /. HoldPattern[FeynAmpDenominator[PropagatorDenominator[Momentum[-k-r],MChiTwo]]] :>
 1/(Pair[Momentum[k+r],Momentum[k+r]]-MChiTwo^2+I MChiTwo gammaWidth);
Print["Width inserted in radiating propagator: ",!FreeQ[projected,gammaWidth]];
If[FreeQ[projected,gammaWidth],Print["Width insertion failed."];Exit[3]];
conj=ComplexConjugate[projected] /. Conjugate[gammaWidth]->gammaWidth;
squared=FermionSpinSum[projected conj]/2;
expr=FeynAmpDenominatorExplicit[Contract[DiracSimplify[squared,DiracTraceEvaluate->True]]];
Print["static projected spin trace bytes=",ByteCount[expr]," remaining propagators=",Length[Cases[expr,_FeynAmpDenominator,Infinity]]];
Get[FileNameJoin[{projectDir,"three_body_rate_engine.wl"}]];
ToExpression[StringReplace[Import[FileNameJoin[{projectDir,"independent_nintegrate.wl"}],"Text"],"299792.458"->"(299792458/1000)"]];
prec=50;args=Rest[$ScriptCommandLine];
If[!MemberQ[{0,12},Length[args]],Print["Expected no arguments or exactly 12: m,ms,dm,mA,ER,v,mV,g1,g2,gN,A,widthMode."];Exit[2]];
If[Length[args]==12,
 {m,ms,dm,ma,er,v,mv,cX,cS,cN}=N[Rationalize[ToExpression[#],0],prec]& /@ Take[args,10];iso=ToExpression[args[[11]]];widthMode=Last[args],
 {m,ms,dm,ma,er,v,mv,cX,cS,cN}=N[#,prec]& /@ {1000,3/10000,1/1000,Fig2`XenonNuclearMassGeV[131],1/5000,776,10,1,1,1};iso=131;widthMode="pole"
];
If[!MemberQ[{128,129,130,131,132,134,136},iso]||!TrueQ[Abs[ma-Fig2`XenonNuclearMassGeV[iso]]<10^-8]||!MemberQ[{"pole","zero"},widthMode]||!TrueQ[m>0&&ms>=0&&dm>=0&&ma>0&&er>0&&0<v<299792458/1000&&mv>0&&cX!=0&&cS!=0&&cN!=0],Print["Invalid physical inputs."];Exit[2]];
widthGeV=If[widthMode==="pole",Fig2`Chi2Width[m,ms,dm,cS],0];
kin=niKinematics[m,ms,ma,er,v,N[2/5,prec],N[1/4,prec],N[6/5,prec]];
If[kin===$Failed,Print["Phase space closed."];Exit[2]];
If[!TrueQ[(m+ms)^2+kin["delta"]<(m+dm)^2],Print["On-shell pole accessible; off-shell assumption invalid."];Exit[2]];
muDot[a_,b_]:=a[[1]]b[[1]]-a[[2;;4]].b[[2;;4]];
Clear[fcStaticME2,fcStaticWeight];
fcStaticME2[u_?NumericQ,z_?NumericQ,phi_?NumericQ]:=Module[{x,pIn,pOut,kOut,pT,rT,vs,momf},
 x=niKinematics[m,ms,ma,er,v,u,z,phi];If[x===$Failed,Return[0]];
 pIn=x["pin"];pOut=x["pout"];kOut=x["k"];pT={ma,0,0,0};rT=pT+Join[{er},x["qvec"]];
 vs={p->pIn,r->pOut,k->kOut,P->pT,R->rT};momf[a_]:=a/.vs;
 expr/.{HoldPattern[Pair[Momentum[a_],Momentum[b_]]]:>muDot[momf[a],momf[b]],HoldPattern[TemporalPair[ExplicitLorentzIndex[0],TemporalMomentum[a_]]]:>momf[a][[1]],MChiOne->m,MChiTwo->m+dm,MNuc->ma,MMed->mv,gammaWidth->widthGeV,gc1->cS,gc2->cS,gc3->cX,gc4->cX,gc5->cN}
];
fcStaticWeight[u_?NumericQ,z_?NumericQ,phi_?NumericQ]:=Module[{x},
 x=niKinematics[m,ms,ma,er,v,u,z,phi];If[x===$Failed,Return[0]];
 x["jac"] x["phase"] Re[fcStaticME2[u,z,phi]]/(2 Pi)
];
point=fcStaticME2[N[2/5,prec],N[1/4,prec],N[6/5,prec]];
pointReference=4ma^2*(cX*cS*cN)^2 Fig2`Private`trace[kin["pin"],kin["pout"],kin["k"],m,m+dm,kin["w2"],widthGeV]/(mv^2+2ma er)^2;
Print["Static projected amplitude squared=",N[Re[point],15]," reference=",N[pointReference,15]," relative=",N[point/pointReference-1,8]];
If[!NumericQ[point]||Abs[N[Im[point]/pointReference]]>10^-8||Abs[N[point/pointReference-1]]>10^-8,Print["Point check failed."];Exit[4]];
incomingMomentum=m*(v/(299792458/1000))/Sqrt[1-(v/(299792458/1000))^2];
Print["Integrating FeynCalc static-current amplitude; width mode=",widthMode];
sigmaPoint=NIntegrate[fcStaticWeight[u,z,phi],{u,0,1},{z,-1,1},{phi,0,2Pi},WorkingPrecision->35,AccuracyGoal->5,PrecisionGoal->5,MaxRecursion->7,Method->{"GlobalAdaptive","SymbolicProcessing"->0}]/(1024 Pi^3 ma incomingMomentum^2);
Fig2`LoadResponses[FileNameJoin[{projectDir,"dmformfactor-V6.m"}],{iso}];
(* Use the same AFH isotope and AME2020 nuclear mass as the main calculation. *)
response=Fig2`NuclearResponse[iso,N[er*10^6]];
sigmaXe=sigmaPoint*response;
Print["AFH isotope and response=",iso," ",response];
Print["Three-body dsigma GeV^-3=",N[sigmaXe,15]];
Print["Three-body dsigma cm2/keV=",N[sigmaXe*3893793721/10^43,15]];
Print["Pointlike R=1 dsigma GeV^-3=",N[sigmaPoint,15]];
Print["Width GeV=",N[widthGeV,12]];
originalParams=<|"mchi"->N[m],"mV"->N[mv],"g2"->N[cS],"couplingSq"->N[(cX*cS*cN)^2],"quad"->{24,24,12},"widthMode"->widthMode|>;
originalSigma=Fig2`DifferentialCrossSection[iso,N[er*10^6],N[v],N[ms],N[dm],originalParams];
Print["Original Gauss (24,24,12) dsigma GeV^-3=",originalSigma];
Print["FeynCalc/original - 1=",N[sigmaXe/originalSigma-1,8]];
If[!NumericQ[sigmaXe]||!TrueQ[sigmaXe>0],Exit[5]];
Exit[0];


