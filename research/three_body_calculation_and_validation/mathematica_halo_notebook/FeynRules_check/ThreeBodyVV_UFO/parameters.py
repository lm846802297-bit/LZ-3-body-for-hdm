# This file was automatically created by FeynRules 2.3.49
# Mathematica version: 14.2.0 for Microsoft Windows (64-bit) (December 26, 2024)
# Date: Mon 16 Nov 2026 20:29:27



from object_library import all_parameters, Parameter


from function_library import complexconjugate, re, im, csc, sec, acsc, asec, cot

# This is a default parameter object representing 0.
ZERO = Parameter(name = 'ZERO',
                 nature = 'internal',
                 type = 'real',
                 value = '0.0',
                 texname = '0')

# User-defined parameters.
gX = Parameter(name = 'gX',
               nature = 'external',
               type = 'real',
               value = 1.,
               texname = '\\text{gX}',
               lhablock = 'FRBlock',
               lhacode = [ 1 ])

gS = Parameter(name = 'gS',
               nature = 'external',
               type = 'real',
               value = 1.,
               texname = '\\text{gS}',
               lhablock = 'FRBlock',
               lhacode = [ 2 ])

gN = Parameter(name = 'gN',
               nature = 'external',
               type = 'real',
               value = 1.,
               texname = '\\text{gN}',
               lhablock = 'FRBlock',
               lhacode = [ 3 ])

MChiOne = Parameter(name = 'MChiOne',
                    nature = 'external',
                    type = 'real',
                    value = 1000.,
                    texname = '\\text{MChiOne}',
                    lhablock = 'MASS',
                    lhacode = [ 9000001 ])

MChiTwo = Parameter(name = 'MChiTwo',
                    nature = 'external',
                    type = 'real',
                    value = 1000.001,
                    texname = '\\text{MChiTwo}',
                    lhablock = 'MASS',
                    lhacode = [ 9000002 ])

MNuc = Parameter(name = 'MNuc',
                 nature = 'external',
                 type = 'real',
                 value = 0.938272,
                 texname = '\\text{MNuc}',
                 lhablock = 'MASS',
                 lhacode = [ 9000003 ])

MMed = Parameter(name = 'MMed',
                 nature = 'external',
                 type = 'real',
                 value = 10.,
                 texname = '\\text{MMed}',
                 lhablock = 'MASS',
                 lhacode = [ 9000004 ])

MScal = Parameter(name = 'MScal',
                  nature = 'external',
                  type = 'real',
                  value = 0.0003,
                  texname = '\\text{MScal}',
                  lhablock = 'MASS',
                  lhacode = [ 9000005 ])

WChiTwo = Parameter(name = 'WChiTwo',
                    nature = 'external',
                    type = 'real',
                    value = 0.0001518239116,
                    texname = '\\text{WChiTwo}',
                    lhablock = 'DECAY',
                    lhacode = [ 9000002 ])

