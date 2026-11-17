(* Load the single canonical AFH v6 source stored at the repository root. *)
studyDirectory=DirectoryName[$InputFileName];
afhProgramPath=ExpandFileName[FileNameJoin[{studyDirectory,"..","..","v6","dmformfactor-V6.m"}]];
Get[afhProgramPath];

(* LZ paper inputs: WIMP mass, halo parameters, recoil grid, and inelastic splittings. *)
mChiGeV=1000.; mNucleonGeV=0.938272; mNuGeV=246.2;
rhoGeVPerCm3=0.3; v0KmPerS=238.; vEarthKmPerS=250.24; vEscapeKmPerS=544.;
recoilGridKeV=Sort[Union[Range[5,350,5],Range[28,45,1]]]; deltaListKeV={0.,200.,300.};

(* Natural xenon isotope number fractions; normalize their rounded sum to one. *)
isotopeFractionsRaw=<|128->0.019102,129->0.264006,130->0.040710,131->0.212324,132->0.269086,134->0.104357,136->0.088573|>;
isotopeFractionTotal=Total[Values[isotopeFractionsRaw]];
isotopeFractions=Map[#/isotopeFractionTotal&,isotopeFractionsRaw];
averageMassNumber=Total[KeyValueMap[#1 #2&,isotopeFractions]];

(* AFH splits its isoscalar input equally between proton and neutron; input 2 gives cp=cn=1/mNu^2. *)
SetJChi[1/2]; SetMChi[mChiGeV GeV]; SetHALO["MBcutoff"];
ZeroCoeffs[]; SetCoeffsNonrel[1,2,0]; SetHelm[False];
veAFH=vEarthKmPerS KilometerPerSecond; v0AFH=v0KmPerS KilometerPerSecond; vescAFH=vEscapeKmPerS KilometerPerSecond;
cmAFH=10^13 Femtometer; rhoAFH=rhoGeVPerCm3 GeV/cmAFH^3;

(* AFH v6 did not export EventRateInelastic as a public symbol; this wrapper calls its internal AFH implementation. *)
AFHInelasticRate[nt_,deltaGeV_,qGeV_]:=dmformfactor`Private`EventRateInelastic[nt,rhoAFH,deltaGeV,qGeV,veAFH,v0AFH,vescAFH];

(* Convert isotope number fractions to target counts per detector mass: NT_i=f_i/(average A times nucleon mass). *)
numberPerMassByIsotope=AssociationMap[(isotopeFractions[#]/(averageMassNumber*mNucleonGeV GeV))&,Keys[isotopeFractions]];
rateConversion=KilogramDay*365.25*10^-3;

(* O1 only: replace AFH smooth-cutoff velocity integral by the conventional sharply truncated Maxwellian integral. *)
etaSharp[v_?NumericQ]:=Module[{z=vescAFH/v0AFH,n,x=v/v0AFH,e=veAFH/v0AFH}, n=Erf[z]-2 z Exp[-z^2]/Sqrt[Pi]; Which[x>=z+e,0.,x<z-e,((Erf[x+e]-Erf[x-e])-4 e Exp[-z^2]/Sqrt[Pi])/(2 n veAFH),True,(Erf[z]-Erf[x-e]-2 (z-x+e) Exp[-z^2]/Sqrt[Pi])/(2 n veAFH)]];
etaSmooth[v_?NumericQ]:=dmformfactor`Private`Fv0MBcutoff[veAFH/v0AFH,v/v0AFH,vescAFH/v0AFH]/v0AFH;
haloCorrection[v_?NumericQ]:=If[v>=vescAFH+veAFH,0.,etaSharp[v]/etaSmooth[v]];
(* Build one AFH velocity-averaged expression per isotope and splitting, then substitute q=sqrt(2 mA ER). *)
qSymbol=Unique["qGeV"];
rateCurve[deltaKeV_]:=Module[{isotopeExpressions,curveByIsotope},
  isotopeExpressions=Association@Table[
    SetIsotope[54,a,"default","default"];
    a->AFHInelasticRate[numberPerMassByIsotope[a],deltaKeV*10^-6 GeV,qSymbol],
    {a,Keys[isotopeFractions]}];
  curveByIsotope=AssociationMap[Function[a,Table[
    With[{qValue=Sqrt[2. a mNucleonGeV er 10^-6]},
      {er, N[rateConversion (isotopeExpressions[a]/.qSymbol->qValue/.GeV->1) haloCorrection[(qValue/(2 (mChiGeV a mNucleonGeV/(mChiGeV+a mNucleonGeV)))+deltaKeV 10^-6/qValue)],10]}],
    {er,recoilGridKeV}]],Keys[isotopeFractions]];
  <|"IsotopeCurves"->curveByIsotope,"Total"->Transpose[{recoilGridKeV,Total[(#[[All,2]]&/@Values[curveByIsotope])]}]|>
];

(* Calculate the three LZ Figure 1 top-panel benchmarks: delta=0, 200, 300 keV. *)
curveResults=Association@Table[delta->rateCurve[delta],{delta,deltaListKeV}];
plotCurves=Table[curveResults[delta]["Total"],{delta,deltaListKeV}];

(* Export natural-xenon spectra in CSV for independent inspection or plotting. *)
header=Join[{"ER_keV"},("rate_delta_"<>ToString[Round[#]]<>"keV_events_per_tonne_year_keV"&/@deltaListKeV)];
exportRows=Transpose[Join[{recoilGridKeV},(#[[All,2]]&/@plotCurves)]];
Export[FileNameJoin[{DirectoryName[$InputFileName],"lz_inelastic_o1_spectra.csv"}],Prepend[exportRows,header],"CSV"];

(* Plot the spectra; gray bands mark LZ regions with efficiency below 50 percent. *)
plotData=Map[Select[#,Last[#]>0&]&,plotCurves];
ratePlot=ListLogPlot[plotData,Joined->True,PlotMarkers->None,PlotRange->{{0,350},{10^-8,10^8}},
  Frame->True,FrameLabel->{"True nuclear recoil energy ER (keV)","dR/dER [events/(tonne year keV)]"},
  PlotLegends->Placed[("Inelastic O1, delta = "<>ToString[Round[#]]<>" keV"&/@deltaListKeV),Below],
  PlotStyle->{Directive[Blue,Thick],Directive[Red,Thick],Directive[Darker[Green],Thick]},
  GridLines->Automatic,ImageSize->900,PlotLabel->"Natural xenon; mChi = 1000 GeV; isoscalar O1",
  Epilog->{Directive[Gray,Opacity[0.22]],Rectangle[{0,10^-8},{5.4,10^8}],Rectangle[{269.9,10^-8},{350,10^8}]}];
Export[FileNameJoin[{DirectoryName[$InputFileName],"lz_inelastic_o1_spectra.png"}],ratePlot,ImageResolution->180];

(* Print rates at six representative recoil energies for comparison with the paper curves. *)
benchmarkRows=Flatten[Table[{delta,er,curveResults[delta]["Total"][[First@FirstPosition[recoilGridKeV,er],2]]},{delta,deltaListKeV},{er,{50,100,150,200,250,300}}],1];
Print["Fraction sum before normalization = ",N[isotopeFractionTotal,8]];
Print["Number-weighted mean xenon mass = ",N[averageMassNumber,8]," u"];
Print["Output convention: events/(tonne year keV); unit conversion factor = ",N[rateConversion,8]];
Print[Grid[Prepend[benchmarkRows,{"delta [keV]","ER [keV]","dR/dER [events/(tonne year keV)]"}],Frame->All]];
ratePlot
