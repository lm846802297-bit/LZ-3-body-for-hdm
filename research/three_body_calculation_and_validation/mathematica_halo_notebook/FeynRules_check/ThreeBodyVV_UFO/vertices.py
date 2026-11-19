# This file was automatically created by FeynRules 2.3.49
# Mathematica version: 14.2.0 for Microsoft Windows (64-bit) (December 26, 2024)
# Date: Mon 16 Nov 2026 20:29:27


from object_library import all_vertices, Vertex
import particles as P
import couplings as C
import lorentz as L


V_1 = Vertex(name = 'V_1',
             particles = [ P.chiTwo__tilde__, P.chiOne, P.scal ],
             color = [ '1' ],
             lorentz = [ L.FFS1 ],
             couplings = {(0,0):C.GC_2})

V_2 = Vertex(name = 'V_2',
             particles = [ P.chiOne__tilde__, P.chiTwo, P.scal ],
             color = [ '1' ],
             lorentz = [ L.FFS1 ],
             couplings = {(0,0):C.GC_2})

V_3 = Vertex(name = 'V_3',
             particles = [ P.chiTwo__tilde__, P.chiOne, P.med ],
             color = [ '1' ],
             lorentz = [ L.FFV1 ],
             couplings = {(0,0):C.GC_3})

V_4 = Vertex(name = 'V_4',
             particles = [ P.chiOne__tilde__, P.chiTwo, P.med ],
             color = [ '1' ],
             lorentz = [ L.FFV1 ],
             couplings = {(0,0):C.GC_3})

V_5 = Vertex(name = 'V_5',
             particles = [ P.nuc__tilde__, P.nuc, P.med ],
             color = [ '1' ],
             lorentz = [ L.FFV1 ],
             couplings = {(0,0):C.GC_1})

