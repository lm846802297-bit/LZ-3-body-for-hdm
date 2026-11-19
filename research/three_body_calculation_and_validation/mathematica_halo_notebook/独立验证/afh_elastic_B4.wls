Get[FileNameJoin[{DirectoryName[DirectoryName[$InputFileName]],"dmformfactor-V6.m"}]];
dmformfactor`ZeroCoeffs[];dmformfactor`SetJChi[1/2];dmformfactor`SetMChi[50 dmformfactor`GeV];dmformfactor`SetIsotope[54,131,"default","default"];dmformfactor`SetCoeffsNonrel[1,1.,"p"];
v=300 dmformfactor`KilometerPerSecond; er=5.;q=Sqrt[2*131*.938272*er*10^-6];
p=dmformfactor`TransitionProbability[v,q];ds=dmformfactor`DiffCrossSection[er,v];
ind=131*.938272 dmformfactor`GeV/(2 Pi v^2) p;
Print["q GeV=",q," probability=",InputForm[p]," direct ds=",InputForm[ds]," B4 ds=",InputForm[ind]," relative=",N[ds/ind-1]];
