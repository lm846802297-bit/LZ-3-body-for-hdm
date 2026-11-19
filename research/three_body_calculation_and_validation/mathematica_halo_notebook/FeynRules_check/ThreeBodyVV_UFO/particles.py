# This file was automatically created by FeynRules 2.3.49
# Mathematica version: 14.2.0 for Microsoft Windows (64-bit) (December 26, 2024)
# Date: Mon 16 Nov 2026 20:29:27


from __future__ import division
from object_library import all_particles, Particle
import parameters as Param

import propagators as Prop

chiOne = Particle(pdg_code = 9000001,
                  name = 'chiOne',
                  antiname = 'chiOne~',
                  spin = 2,
                  color = 1,
                  mass = Param.MChiOne,
                  width = Param.ZERO,
                  texname = 'chiOne',
                  antitexname = 'chiOne~',
                  charge = 0)

chiOne__tilde__ = chiOne.anti()

chiTwo = Particle(pdg_code = 9000002,
                  name = 'chiTwo',
                  antiname = 'chiTwo~',
                  spin = 2,
                  color = 1,
                  mass = Param.MChiTwo,
                  width = Param.WChiTwo,
                  texname = 'chiTwo',
                  antitexname = 'chiTwo~',
                  charge = 0)

chiTwo__tilde__ = chiTwo.anti()

nuc = Particle(pdg_code = 9000003,
               name = 'nuc',
               antiname = 'nuc~',
               spin = 2,
               color = 1,
               mass = Param.MNuc,
               width = Param.ZERO,
               texname = 'nuc',
               antitexname = 'nuc~',
               charge = 0)

nuc__tilde__ = nuc.anti()

med = Particle(pdg_code = 9000004,
               name = 'med',
               antiname = 'med',
               spin = 3,
               color = 1,
               mass = Param.MMed,
               width = Param.ZERO,
               texname = 'med',
               antitexname = 'med',
               charge = 0)

scal = Particle(pdg_code = 9000005,
                name = 'scal',
                antiname = 'scal',
                spin = 1,
                color = 1,
                mass = Param.MScal,
                width = Param.ZERO,
                texname = 'scal',
                antitexname = 'scal',
                charge = 0)

