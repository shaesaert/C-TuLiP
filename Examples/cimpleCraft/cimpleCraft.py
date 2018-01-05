# Import modules
from __future__ import print_function

import sys

import numpy as np
from polytope import box2poly
from tulip import hybrid
from tulip.abstract import prop2part, discretize

import Interface.DSL as DSL
from Interface import Statechart
from Interface.Reduce import *
from Interface.Transform import *

print("----------------------------------\n Script options \n----------------------------------")
verbose = 1 # Decrease printed output = 0, increase= 1

print("""----------------------------------\n System Definition \n----------------------------------
         -- System Constants 
         -- System Label State Space & partition

         """)
# System constants
input_bound = 1.0
disturbance_bound = 0.1

# The system dynamics
A = np.array([[1., 0, 2., 0, 0], [0, 1., 0, 2, 0], [0, 0, 0.5, 0, 0], [0, 0, 0, 0.5, 0], [0, 0, 0, 0, 1]])
B = np.array([[0, 0, 0, 0], [0, 0, 0, 0], [5, -1, 0, 0], [0, 0, 5, -1], [1, 0, 1, 0]])
E = np.array([[1., 0, 0, 0, 0], [0, 1., 0, 0, 0], [0, 0, 1., 0, 0], [0, 0, 0, 1., 0], [0, 0, 0, 0, 1.]])
# $x^+=Ax+Bu+E W$

# Size of the sets
X = box2poly([[0, 100.], [0, 100.], [0, 5.], [0, 5.], [0, 100.]])
U = box2poly(input_bound*np.array([[0, 1], [0, 1], [0, 1], [0, 1]]))
W = box2poly(disturbance_bound*np.array([[0, 10], [0, 10], [0, 0.1], [0, 0.1], [0, 1]]))
#  ----------------------------------\n Define system\n----------------------------------
# Intermezzo polytope tutorial
#  https://github.com/tulip-control/polytope/blob/master/doc/tutorial.md
sys_dyn = hybrid.LtiSysDyn(A, B, E, None, U, W, X)

print(str(sys_dyn))

#----------------------------------\n Define labelling \n----------------------------------")

cprops ={}
cprops["inA"] = box2poly([[0, 10], [45, 55], [0, 0.1], [0, 0.1], [0, 100]])
cprops["inB"] = box2poly([[90, 100], [45, 55], [0, 0.1], [0, 0.1], [0, 100]])
cprops["inG"] = box2poly([[45, 55], [45, 55], [0, 0.1], [0, 0.1], [0, 100]])

cprops["inObj1"] = box2poly([[15, 35], [30, 70], [0, 5], [0, 5], [0, 100]])
cprops["inObj2"] = box2poly([[65, 85], [30, 70], [0, 5], [0, 5], [0, 100]])

cprops["noGas"] = box2poly([[0, 100], [0, 100], [0, 5], [0, 5], [0, 1]])


cpartition = prop2part(X, cprops)
if verbose == 1:
    print("partition before refinement")
    print(cpartition)

#  ----------------------------------\n System partition State Space \n----------------------------------

disc_dynamics = discretize(cpartition, sys_dyn,
                           closed_loop=True, conservative=True,
                           N=5, min_cell_volume=0.1)


states=[state for (state, label) in disc_dynamics.ts.states.find(with_attr_dict={'ap': {'init'}})]
disc_dynamics.ts.states.initial|=states