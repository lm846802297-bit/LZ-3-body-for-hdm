(* Native Wolfram Language evaluation of the complete Xe-131 Eq. (6) dSigma/dER.
   AFH response is read from the already archived native 2401-node table; I6 is recomputed here.
   Natural units, metric (+---), all masses and energies in GeV. *)
$HistoryLength = 0;
scriptArgs = $ScriptCommandLine;
getArg[name_, default_] := Module[{pos = FirstPosition[scriptArgs, name]},
  If[Head[pos] === Missing, default, scriptArgs[[First[pos] + 1]]]
];
nw = ToExpression[getArg["--nw", "16"]];
nz = ToExpression[getArg["--nz", "16"]];
nphi = ToExpression[getArg["--nphi", "8"]];
widthScheme = getArg["--width-scheme", "pole"];
w2Mapping = getArg["--w2-mapping", "threshold_u2"];
erStart = ToExpression[getArg["--er-start-kev", "5"]];
erStop = ToExpression[getArg["--er-stop-kev", "800"]];
erStep = ToExpression[getArg["--er-step-kev", "5"]];
erListString = getArg["--er-list-kev", ""];
benchmarkArg = getArg["--benchmark", "all"];
If[!(And @@ (IntegerQ /@ {nw, nz, nphi})) || Min[nw, nz, nphi] < 1, Exit[2]];
If[!MemberQ[{"pole", "zero"}, widthScheme] || !MemberQ[{"threshold_u2", "linear_w2"}, w2Mapping] || erStep <= 0 || erStop < erStart, Exit[2]];

here = DirectoryName[$InputFileName];
responsePath = FileNameJoin[{here, "afh_default_xe131_WM00_mathematica.csv"}];
outDir = FileNameJoin[{here, "output", "full_dsigma_mathematica"}];
outPath = getArg["--out-csv", FileNameJoin[{outDir, "mathematica_full_dsigma_xe131.csv"}]];
metaPath = getArg["--metadata", FileNameJoin[{outDir, "mathematica_full_dsigma_xe131_metadata.json"}]];
If[!FileExistsQ[responsePath], Print["Missing native AFH response CSV: ", responsePath]; Exit[3]];

A = 131; Z = 54; JA = 3/2.;
mA = 131.*0.93149410242; (* A*u convention retained for direct comparison to archived benchmarks *)
mchi = 1000.; mV = 10.; g2 = 1.; gProductSquared = 1.*10^-8;
speedKms = 800.; cKms = 299792.458;
betaChi = speedKms/cKms; gammaChi = 1./Sqrt[1. - betaChi^2];
pChi = mchi*gammaChi*betaChi; eChi = mchi*gammaChi;

benchmarks = {
  {"red_ms200_dm1", 200.*10^-6, 1.*10^-3},
  {"green_ms300_dm1", 300.*10^-6, 1.*10^-3},
  {"black_ms360_dm1", 360.*10^-6, 1.*10^-3},
  {"blue_ms300_dm10", 300.*10^-6, 10.*10^-3}
};
selectedBenchmarks = If[benchmarkArg === "all", benchmarks,
  Select[benchmarks, First[#] === benchmarkArg &]];
If[selectedBenchmarks === {}, Print["Unknown benchmark: ", benchmarkArg]; Exit[2]];
erGrid = If[StringLength[erListString] > 0,
  ToExpression /@ StringSplit[erListString, ","], N[Range[erStart, erStop, erStep]]];

(* AFH response table: columns 1, 4, 7 are q, raw package response, physical response. *)
rawCSV = Import[responsePath, "CSV"];
responseRows = Rest[rawCSV];
qGrid = N[responseRows[[All, 1]]];
rPackageGrid = N[responseRows[[All, 4]]];
rPhysicalGrid = N[responseRows[[All, 7]]];
If[Length[qGrid] =!= 2401 || !(And @@ Thread[Differences[qGrid] > 0]), Exit[4]];
If[Abs[rPhysicalGrid[[1]] - A^2] > 1.*10^-7, Exit[4]];
c0 = A^2/(4.*rPackageGrid[[1]]);
responseNodeResidual = Max[MapThread[
  Abs[#1 - 4.*c0*#2]/Max[1., Abs[#1]] &, {rPhysicalGrid, rPackageGrid}]];
If[responseNodeResidual > 2.*10^-12, Print["AFH factor-four mapping failed"]; Exit[4]];

(* Shape-preserving cubic Hermite slopes/evaluation, matching SciPy PCHIP. *)
pchipSlopes[x_List, y_List] := Module[{n = Length[x], h, d, m, w1, w2, d0, dn},
  h = Differences[x]; d = Differences[y]; d = d/h; m = ConstantArray[0., n];
  If[n == 2, Return[{d[[1]], d[[1]]}]];
  Do[
    If[d[[i - 1]]*d[[i]] > 0.,
      w1 = 2.*h[[i]] + h[[i - 1]]; w2 = h[[i]] + 2.*h[[i - 1]];
      m[[i]] = (w1 + w2)/(w1/d[[i - 1]] + w2/d[[i]]),
      m[[i]] = 0.],
    {i, 2, n - 1}];
  d0 = ((2.*h[[1]] + h[[2]])*d[[1]] - h[[1]]*d[[2]])/(h[[1]] + h[[2]]);
  If[Sign[d0] != Sign[d[[1]]], d0 = 0.,
    If[Sign[d[[1]]] != Sign[d[[2]]] && Abs[d0] > 3.*Abs[d[[1]]], d0 = 3.*d[[1]]]];
  dn = ((2.*h[[-1]] + h[[-2]])*d[[-1]] - h[[-1]]*d[[-2]])/(h[[-1]] + h[[-2]]);
  If[Sign[dn] != Sign[d[[-1]]], dn = 0.,
    If[Sign[d[[-1]]] != Sign[d[[-2]]] && Abs[dn] > 3.*Abs[d[[-1]]], dn = 3.*d[[-1]]]];
  m[[1]] = d0; m[[-1]] = dn; m
];
pchipValue[x_List, y_List, m_List, x0_?NumericQ] := Module[{n = Length[x], i, h, t},
  If[x0 < x[[1]] || x0 > x[[-1]], Return[Indeterminate]];
  i = LengthWhile[x, # <= x0 &]; i = Min[n - 1, Max[1, i]];
  h = x[[i + 1]] - x[[i]]; t = (x0 - x[[i]])/h;
  (2.*t^3 - 3.*t^2 + 1.)*y[[i]] +
  (t^3 - 2.*t^2 + t)*h*m[[i]] +
  (-2.*t^3 + 3.*t^2)*y[[i + 1]] + (t^3 - t^2)*h*m[[i + 1]]
];
rPackageSlope = pchipSlopes[qGrid, rPackageGrid];
rPhysicalSlope = pchipSlopes[qGrid, rPhysicalGrid];
responseAt[ER_?NumericQ] := Module[{q = Sqrt[2.*mA*ER + ER^2]},
  {pchipValue[qGrid, rPackageGrid, rPackageSlope, q],
   pchipValue[qGrid, rPhysicalGrid, rPhysicalSlope, q], q}
];

(* Gauss-Legendre rule from the symmetric Jacobi matrix. *)
gaussLegendreRule[n_Integer?Positive, a_?NumericQ, b_?NumericQ] := Module[
  {jac = ConstantArray[0., {n, n}], vals, vecs, order, scale},
  Do[jac[[i, i + 1]] = i/Sqrt[4.*i^2 - 1.]; jac[[i + 1, i]] = jac[[i, i + 1]], {i, 1, n - 1}];
  {vals, vecs} = Eigensystem[jac]; order = Ordering[vals]; scale = (b - a)/2.;
  Transpose[{(a + b)/2. + scale*vals[[order]], scale*2.*(Re[vecs[[order, 1]]]^2)}]
];

(* Dirac representation and (+---) slash. *)
id2 = IdentityMatrix[2]; z2 = ConstantArray[0., {2, 2}];
sigma1 = {{0., 1.}, {1., 0.}}; sigma2 = {{0., -I}, {I, 0.}}; sigma3 = {{1., 0.}, {0., -1.}};
gammaMatrices = {
  ArrayFlatten[{{id2, z2}, {z2, -id2}}],
  ArrayFlatten[{{z2, sigma1}, {-sigma1, z2}}],
  ArrayFlatten[{{z2, sigma2}, {-sigma2, z2}}],
  ArrayFlatten[{{z2, sigma3}, {-sigma3, z2}}]
};
gamma0 = gammaMatrices[[1]]; id4 = IdentityMatrix[4];
slash4[v_List] := gammaMatrices[[1]]*v[[1]] - gammaMatrices[[2]]*v[[2]] -
  gammaMatrices[[3]]*v[[3]] - gammaMatrices[[4]]*v[[4]];
minkowskiDot[a_List, b_List] := a[[1]]*b[[1]] - a[[2 ;; 4]].b[[2 ;; 4]];

boost4[v_List, betaVec_List] := Module[{b2, b, gam, bh, par},
  b2 = betaVec.betaVec; If[b2 < 1.*10^-30, Return[v]];
  If[b2 >= 1., Abort[]];
  b = Sqrt[b2]; gam = 1./Sqrt[1. - b2]; bh = betaVec/b; par = v[[2 ;; 4]].bh;
  Join[{gam*(v[[1]] + b*par)}, v[[2 ;; 4]] + (((gam - 1.)*par + gam*b*v[[1]])*bh)]
];

buildPoint[mchi_, ms_, mA_, ER_, speed_, w2_, deltaW2_, z_, phi_] := Module[
  {beta0, gamma0c, energy, pz, p, qmag, cq, sq, q, kTotal, betaK,
   pStar, e3, ref, e1, e2, lam, w, kAbs, eK, eP, nvec, k, pPrime},
  beta0 = speed/cKms; gamma0c = 1./Sqrt[1. - beta0^2];
  energy = mchi*gamma0c; pz = mchi*gamma0c*beta0; p = {energy, 0., 0., pz};
  qmag = Sqrt[2.*mA*ER + ER^2];
  cq = (w2 - mchi^2 + 2.*(energy + mA)*ER)/(2.*pz*qmag);
  If[Abs[cq] > 1. + 2.*10^-8, Print["Unphysical cos(theta_q) = ", cq]; Abort[]];
  cq = Min[1., Max[-1., cq]]; sq = Sqrt[Max[0., 1. - cq^2]];
  q = {ER, qmag*sq, 0., qmag*cq}; kTotal = p - q;
  If[Abs[minkowskiDot[kTotal, kTotal] - w2] > 2.*10^-7*Max[1., w2], Abort[]];
  w = Sqrt[w2]; betaK = kTotal[[2 ;; 4]]/kTotal[[1]];
  pStar = boost4[p, -betaK]; e3 = pStar[[2 ;; 4]]/Norm[pStar[[2 ;; 4]]];
  ref = If[Abs[{1., 0., 0.}.e3] > 0.9, {0., 1., 0.}, {1., 0., 0.}];
  e1 = Cross[ref, e3]; e1 = e1/Norm[e1]; e2 = Cross[e3, e1];
  lam = deltaW2*(4.*mchi*ms + deltaW2);
  If[lam < -1.*10^-12, Abort[]];
  kAbs = Sqrt[Max[0., lam]]/(2.*w);
  eK = (2.*ms*(mchi + ms) + deltaW2)/(2.*w);
  eP = (2.*mchi*(mchi + ms) + deltaW2)/(2.*w);
  nvec = z*e3 + Sqrt[Max[0., 1. - z^2]]*(Cos[phi]*e1 + Sin[phi]*e2);
  k = boost4[Join[{eK}, kAbs*nvec], betaK];
  pPrime = boost4[Join[{eP}, -kAbs*nvec], betaK];
  {p, pPrime, k}
];

spinTrace[point_List, mchi_, mchi2_, width_] := Module[
  {p = point[[1]], pPrime = point[[2]], k = point[[3]], d1, d2, before, after, vertex, vertexBar},
  d1 = minkowskiDot[p - k, p - k] - mchi2^2;
  d2 = minkowskiDot[pPrime + k, pPrime + k] - mchi2^2 + I*mchi2*width;
  If[Abs[d1] < 1.*10^-30 || Abs[d2] < 1.*10^-30, Abort[]];
  before = gamma0 . (slash4[p - k] + mchi2*id4)/d1;
  after = (slash4[pPrime + k] + mchi2*id4) . gamma0/d2;
  vertex = before + after;
  vertexBar = gamma0 . ConjugateTranspose[vertex] . gamma0;
  Re[Tr[(slash4[pPrime] + mchi*id4) . vertex . (slash4[p] + mchi*id4) . vertexBar]/2.]
];

chi2Width[mchi_, ms_, deltaM_, g2_] := Module[
  {m2 = mchi + deltaM, excess, lam},
  excess = m2 - mchi - ms;
  If[excess <= 0., Return[0.]];
  (* Factorized threshold form avoids subtracting nearly equal squared masses. *)
  lam = excess*(excess + 2.*ms)*(2.*mchi + excess)*
    (2.*mchi + excess + 2.*ms);
  g2^2/(16.*Pi*m2^3)*Sqrt[lam]*((m2 + mchi)^2 - ms^2)
];

reducedKernel[mchi_, ms_, deltaM_, mA_, ER_, speed_, width_, nW_, nZ_, nPhi_, mapping_] := Module[
  {wMin2, wMax2, wRule, zRule, phiRule, total = 0., wPair, zPair, phiPair,
   w2, deltaW2, deltaW2Max, u, weightW, z, weightZ, phi, weightPhi,
   lambdaDim, angular, azimuth, point, beta0, gamma0c},
  wMin2 = (mchi + ms)^2; beta0 = speed/cKms; gamma0c = 1./Sqrt[1. - beta0^2];
  wMax2 = mchi^2 + 2.*mchi*gamma0c*beta0*Sqrt[2.*mA*ER + ER^2] -
    2.*(mchi*gamma0c + mA)*ER;
  If[wMax2 <= wMin2, Return[0.]];
  deltaW2Max = wMax2 - wMin2;
  wRule = If[mapping === "threshold_u2",
    gaussLegendreRule[nW, -1., 1.],
    gaussLegendreRule[nW, wMin2, wMax2]];
  zRule = gaussLegendreRule[nZ, -1., 1.];
  phiRule = gaussLegendreRule[nPhi, 0., 2.*Pi];
  Do[
    If[mapping === "threshold_u2",
      u = 0.5*(wPair[[1]] + 1.);
      deltaW2 = deltaW2Max*u^2;
      w2 = wMin2 + deltaW2;
      weightW = 0.5*wPair[[2]]*(2.*deltaW2Max*u),
      w2 = wPair[[1]];
      deltaW2 = w2 - wMin2;
      weightW = wPair[[2]]
    ];
    lambdaDim = deltaW2*(4.*mchi*ms + deltaW2)/w2^2;
    angular = 0.;
    Do[
      z = zPair[[1]]; weightZ = zPair[[2]]; azimuth = 0.;
      Do[
        phi = phiPair[[1]]; weightPhi = phiPair[[2]];
        point = buildPoint[mchi, ms, mA, ER, speed, w2, deltaW2, z, phi];
        azimuth += (weightPhi/(2.*Pi))*spinTrace[point, mchi, mchi + deltaM, width],
        {phiPair, phiRule}];
      angular += weightZ*azimuth,
      {zPair, zRule}];
    total += weightW*Sqrt[Max[0., lambdaDim]]*angular,
    {wPair, wRule}];
  total
];

rows = {}; minPoleClearance = Infinity; maxFactor4GridResidual = 0.;
Do[
  benchmark = bench[[1]]; ms = bench[[2]]; deltaM = bench[[3]];
  mchi2 = mchi + deltaM; gammaPole = chi2Width[mchi, ms, deltaM, g2];
  width = If[widthScheme === "pole", gammaPole, 0.];
  Print["Starting ", benchmark, " ; Gamma_pole = ", ScientificForm[gammaPole, 6], " GeV"];
  Do[
    ER = erKev*10^-6; wMin2 = (mchi + ms)^2;
    wMax2 = mchi^2 + 2.*pChi*Sqrt[2.*mA*ER + ER^2] - 2.*(eChi + mA)*ER;
    open = wMax2 > wMin2;
    If[open && wMax2 >= mchi2^2, Print["On-shell chi2 region: ", benchmark, " ER=", erKev]; Exit[8]];
    clearanceGeV = If[wMax2 > 0., mchi2 - Sqrt[wMax2], Infinity];
    If[open, minPoleClearance = Min[minPoleClearance, clearanceGeV]];
    {rPackage, rPhysical, qValue} = responseAt[ER];
    If[!NumericQ[rPackage] || !NumericQ[rPhysical] || !NumericQ[qValue], Exit[9]];
    i6Value = If[open, reducedKernel[mchi, ms, deltaM, mA, ER, speedKms, width, nw, nz, nphi, w2Mapping], 0.];
    denominator = (mV^2 + 2.*mA*ER)^2;
    prefactor = mA*gProductSquared/(256.*Pi^3*pChi^2*denominator);
    dsigma = If[open, prefactor*rPhysical*i6Value, 0.];
    dsigmaNo4 = If[open, prefactor*(rPhysical/4.)*i6Value, 0.];
    factor4Ratio = If[open && dsigmaNo4 != 0., dsigma/dsigmaNo4, 0.];
    factor4Residual = If[open, Abs[factor4Ratio - 4.]/4., 0.];
    maxFactor4GridResidual = Max[maxFactor4GridResidual, factor4Residual];
    AppendTo[rows, {benchmark, erKev, qValue, rPackage, rPhysical, rPhysical/4., c0,
      i6Value, widthScheme, w2Mapping, g2, gammaPole, wMin2, wMax2, clearanceGeV*10^6,
      If[open, 1, 0], nw, nz, nphi, pChi, denominator, dsigma, dsigmaNo4,
      factor4Ratio, dsigma*0.3893793721*10^-33}],
    {erKev, erGrid}];
  Print["Completed ", benchmark, " ; recoil points = ", Length[erGrid]],
  {bench, selectedBenchmarks}];

header = {"benchmark", "ER_keV", "q_GeV", "R_A_AFH_package", "R_A_physical_normalized",
  "R_A_physical_without_factor4", "C0", "I6_GeV2", "width_scheme", "W2_mapping", "g2",
  "Gamma_chi2_pole_GeV", "Wmin2_GeV2", "Wmax2_GeV2", "chi2_pole_clearance_keV",
  "phase_space_open", "nW", "nz", "nphi", "pchi_GeV", "mediator_denominator_GeV4",
  "dsigma_dER_GeVminus3", "dsigma_without_factor4_GeVminus3", "dsigma_factor4_ratio",
  "dsigma_cm2_per_keV"};
If[Length[rows] === 0, Exit[10]];
CreateDirectory[DirectoryName[outPath], CreateIntermediateDirectories -> True];
CreateDirectory[DirectoryName[metaPath], CreateIntermediateDirectories -> True];
Export[outPath, Prepend[rows, header], "CSV"];
benchmarkMeta = Association @@ Map[
  (#1[[1]] -> <|"m_s_keV" -> #1[[2]]*10^6, "Delta_m_MeV" -> #1[[3]]*10^3,
    "Gamma_chi2_pole_GeV" -> chi2Width[mchi, #1[[2]], #1[[3]], g2]|>) &,
  selectedBenchmarks];
meta = <|
  "calculation" -> "Native Wolfram Language full Eq. (6) Xe-131 differential cross section",
  "target" -> <|"A" -> A, "Z" -> Z, "J_A" -> JA, "mA_GeV" -> mA,
    "mass_scheme" -> "A*u approximation, retained to match archived four-benchmark diagnostic"|>,
  "particle_inputs" -> <|"m_chi1_GeV" -> mchi, "m_V_GeV" -> mV, "g2" -> g2,
    "coupling_product_squared" -> gProductSquared, "speed_km_s" -> speedKms, "pchi_GeV" -> pChi|>,
  "benchmarks" -> benchmarkMeta,
  "integration" -> <|"I6_recomputed_in_Wolfram_Language" -> True,
    "quadrature" -> <|"nW" -> nw, "nz" -> nz, "nphi" -> nphi|>,
    "definition" -> "Integral dW2 sqrt(lambda_dim) dz (1/(2 Pi)) dphi L00",
    "width_scheme" -> widthScheme, "W2_mapping" -> w2Mapping|>,
  "AFH" -> <|"source_table" -> "afh_default_xe131_WM00_mathematica.csv",
    "native_AFH_package_rerun" -> False, "q_nodes" -> Length[qGrid],
    "raw_package_R0" -> rPackageGrid[[1]], "C0" -> c0, "physical_R0" -> rPhysicalGrid[[1]],
    "physical_response" -> "R_A = 4 C0 R_A_AFH_package",
    "factor_four_applied_in_response_once" -> True,
    "max_native_table_mapping_relative_residual" -> responseNodeResidual,
    "max_full_grid_factor_four_relative_residual" -> maxFactor4GridResidual,
    "minimum_chi2_pole_clearance_keV" -> minPoleClearance*10^6|>,
  "output" -> <|"rows" -> Length[rows], "csv" -> outPath|>,
  "scope" -> {"Xe-131 only; fixed v=800 km/s; no halo fold or detector response",
    "g2=1 is a chosen factorization of the caption coupling product",
    "pole width is conditional on Dirac chi states, real scalar, pure scalar Yukawa and chi2 -> chi1 s only",
    "not the complete vector-plus-scalar chi2 self-energy"}|>;
Export[metaPath, meta, "JSON"];
Print["PASS: Mathematica Eq. (6) run completed. Rows = ", Length[rows]];
Print["AFH table mapping residual = ", ScientificForm[responseNodeResidual, 5]];
Print["Factor-four residual = ", ScientificForm[maxFactor4GridResidual, 5]];
Print["Output: ", outPath]; Print["Metadata: ", metaPath];
Exit[0];
