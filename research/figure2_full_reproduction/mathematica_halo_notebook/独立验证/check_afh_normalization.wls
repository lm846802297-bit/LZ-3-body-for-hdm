Get[FileNameJoin[{DirectoryName[DirectoryName[$InputFileName]],"figure2_engine.wl"}]];Fig2`LoadResponses[FileNameJoin[{DirectoryName[DirectoryName[$InputFileName]],"dmformfactor-V6.m"}],{131}];
raw=dmformfactor`ResponseNuclear[0,1,0,0];rawNormalized=N[4 Pi raw/(2 (3/2)+1)];
engineZero=Fig2`NuclearResponse[131,0.];engine200=Fig2`NuclearResponse[131,200.];
Print["raw W00(0)=",N[raw]," 4Pi/(2J+1) W00=",rawNormalized];
Print["4*raw normalized=",4rawNormalized," A?=",131^2," ratio=",4rawNormalized/131^2];
Print["engine R0=",engineZero," R200=",engine200];
