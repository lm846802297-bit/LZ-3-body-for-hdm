(* Independent construction: axes aligned with the chi1+s system momentum.
   Uses the existing trace only; no private momentum or quadrature functions. *)
ClearAll[niDot,niKinematics,niIntegrand,niI6];
niDot[a_,b_]:=a[[1]] b[[1]]-a[[2;;4]].b[[2;;4]];
niKinematics[m_?NumericQ,ms_?NumericQ,mA_?NumericQ,er_?NumericQ,v_?NumericQ,u_?NumericQ,z_?NumericQ,phi_?NumericQ]:=Module[
 {beta,e,p,q,wmin,wmax,w2,angle,qvec,pin,Q,W,Qvec,Qmag,ez,ex,ey,rad,est,kstar,ks,ks4,pp,threshold,delta},
 beta=v/299792.458;e=m/Sqrt[1-beta^2];p=e beta;q=Sqrt[er (2 mA+er)];
 wmin=(m+ms)^2;wmax=m^2+2 p q-2(e+mA)er;delta=wmax-wmin;
 If[delta<=0,Return[$Failed]];
 w2=wmin+delta u^2;
 angle=(w2-m^2+2(e+mA)er)/(2 p q);
 If[Abs[angle]>1+10^-8,Return[$Failed]];
 qvec=q {Sqrt[Max[0,1-angle^2]],0,angle};
 pin={e,0,0,p};Q=Join[{e-er},{0,0,p}-qvec];
 W=Sqrt[w2];Qvec=Q[[2;;4]];Qmag=Norm[Qvec];
 ez=If[Qmag>0,Qvec/Qmag,{0,0,1}];
 ex=Normalize[Cross[If[Abs[ez[[3]]]<0.9,{0,0,1},{0,1,0}],ez]];ey=Cross[ez,ex];
 rad=Sqrt[Max[0,(w2-(m+ms)^2)(w2-(m-ms)^2)]];
 est=(w2-m^2+ms^2)/(2 W);kstar=rad/(2 W);
 ks=kstar (z ez+Sqrt[Max[0,1-z^2]](Cos[phi] ex+Sin[phi] ey));
 ks4=Join[{(Q[[1]] est+Qvec.ks)/W},ks+Qvec (est/W+(Qvec.ks)/(W (Q[[1]]+W)))];
 pp=Q-ks4;
 <|"pin"->pin,"pout"->pp,"k"->ks4,"Q"->Q,"w2"->w2,"qvec"->qvec,
   "jac"->2 delta u,"phase"->rad/w2,"delta"->delta|>
];
niIntegrand[m_?NumericQ,ms_?NumericQ,dm_?NumericQ,mA_?NumericQ,er_?NumericQ,v_?NumericQ,width_?NumericQ,u_?NumericQ,z_?NumericQ,phi_?NumericQ]:=Module[{kin},
 kin=niKinematics[m,ms,mA,er,v,u,z,phi];
 If[kin===$Failed,Return[0.]];
 kin["jac"] kin["phase"] Fig2`Private`trace[kin["pin"],kin["pout"],kin["k"],m,m+dm,kin["w2"],width]/(2 Pi)
];
Options[niI6]={AccuracyGoal->3,PrecisionGoal->3,MaxRecursion->6};
niI6[m_?NumericQ,ms_?NumericQ,dm_?NumericQ,mA_?NumericQ,er_?NumericQ,v_?NumericQ,width_?NumericQ,OptionsPattern[]]:=Module[{b,e,p,q,wmax},
 If[!TrueQ[m>0&&ms>=0&&dm>=0&&mA>0&&er>0&&0<v<299792.458&&width>=0],Print["Invalid inputs"];Return[$Failed]];
 b=v/299792.458;e=m/Sqrt[1-b^2];p=e b;q=Sqrt[er(2mA+er)];wmax=m^2+2p q-2(e+mA)er;
 If[wmax<=(m+ms)^2,Return[0.]];
 If[wmax>=(m+dm)^2,Print["On-shell chi2 accessible; off-shell calculation aborted."];Return[$Failed]];
 NIntegrate[niIntegrand[m,ms,dm,mA,er,v,width,u,z,phi],{u,0,1},{z,-1,1},{phi,0,2Pi},
   Method->{"GlobalAdaptive","SymbolicProcessing"->0},AccuracyGoal->OptionValue[AccuracyGoal],
   PrecisionGoal->OptionValue[PrecisionGoal],MaxRecursion->OptionValue[MaxRecursion]]
];
