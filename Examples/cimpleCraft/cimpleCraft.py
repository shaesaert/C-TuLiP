# Import modules
from __future__ import print_function

import sys

import numpy as np
from polytope import box2poly
from tulip import hybrid
from tulip.abstract import prop2part, discretize

import Interface.DSL as DSL
from Interface import Statechart as dumpsmach
from Interface.Reduce import *
from Interface.Transform import *

print("----------------------------------\n Script options \n----------------------------------")
verbose = 1  # Decrease printed output = 0, increase= 1

print("""----------------------------------\n System Definition \n----------------------------------
         -- System Constants 
         -- System Label State Space & partition

         """)
# System constants
input_bound = 1.0
disturbance_bound = 1.0

# The system dynamics
A = np.array([[1., 0, 2., 0], [0, 1., 0, 2], [0, 0, 0.5, 0], [0, 0, 0, 0.5]])
B = np.array([[0, 0], [0, 0], [5, 0], [0, 5]])
E = np.array([[1., 0, 0, 0], [0, 1., 0, 0], [0, 0, 1., 0], [0, 0, 0, 1.]])
# $x^+=Ax+Bu+E W$

# Size of the sets
X = box2poly([[0, 100.], [0, 100.], [-5, 5.], [-5, 5.]])
U = box2poly(input_bound*np.array([[-1, 1.], [-1, 1.]]))
W = box2poly(disturbance_bound*np.array([[-2, 2], [-2, 2], [-0.1, 0.1], [-0.1, 0.1]]))
print("----------------------------------\n Define system\n----------------------------------")
# Intermezzo polytope tutorial
#  https://github.com/tulip-control/polytope/blob/master/doc/tutorial.md
sys_dyn = hybrid.LtiSysDyn(A, B, E, None, U, W, X)

print(str(sys_dyn))

print("----------------------------------\n Define labelling \n----------------------------------")

cprops = {}
cprops["inA"] = box2poly([[0, 10], [45, 55], [-1, 1], [-1, 1]])
cprops["inB"] = box2poly([[90, 100], [45, 55], [-1, 1], [-1, 1]])
cprops["inG"] = box2poly([[45, 55], [45, 55], [-1, 1], [-1, 1]])

cprops["inObj1"] = box2poly([[15, 35], [30, 70], [-5, 5], [-5, 5]])
cprops["inObj2"] = box2poly([[65, 85], [30, 70], [-5, 5], [-5, 5]])
#
# cprops["noGas"] = box2poly([[0, 100], [0, 100], [-5, 5], [-5, 5], [0, 10]])
# cprops["gasReserves"] = box2poly([[0, 100], [0, 100], [-5, 5], [-5, 5], [0, 40]])
# cprops["fullGas"] = box2poly([[0, 100], [0, 100], [-5, 5], [-5, 5], [90, 100]])


cpartition = prop2part(X, cprops)
if verbose == 1:
    print("partition before refinement")
    print(cpartition)

print("---------------------------------\n System partition State Space \n----------------------------------")

disc_dynamics = discretize(cpartition, sys_dyn, N=5, min_cell_volume=1, closed_loop=True, conservative=True)

states = [state for (state, label) in disc_dynamics.ts.states.find(with_attr_dict={'ap': {'inA'}})]
disc_dynamics.ts.states.initial |= states

print("----------------------------------\n Define specification \n----------------------------------")

# Specifications
# Environment variables and assumptions
env_vars = ['tens', 'ones', 'gasEmpty']
env_init = {'tens = "4"', 'ones = "9"', '!gasEmpty'}
env_safe = set()
env_safe |= {'(ones = "9")->(X(ones = "8"))'}
env_safe |= {'(ones = "8")->(X(ones = "7"))'}
env_safe |= {'(ones = "7")->(X(ones = "6"))'}
env_safe |= {'(ones = "6")->(X(ones = "5"))'}
env_safe |= {'(ones = "5")->(X(ones = "4"))'}
env_safe |= {'(ones = "4")->(X(ones = "3"))'}
env_safe |= {'(ones = "3")->(X(ones = "2"))'}
env_safe |= {'(ones = "2")->(X(ones = "1"))'}
env_safe |= {'(ones = "1")->(X(ones = "0"))'}
env_safe |= {'((ones = "0") && !(tens = "0"))->(X(ones = "9"))'}
env_safe |= {'(tens = "4") && !(ones = "0")->(X(tens = "3"))'}
env_safe |= {'(tens = "3") && !(ones = "0")->(X(tens = "2"))'}
env_safe |= {'(tens = "2") && !(ones = "0")->(X(tens = "1"))'}
env_safe |= {'(tens = "1") && !(ones = "0")->(X(tens = "0"))'}
env_safe |= {'((tens = "0") && (ones = "3")) -> (X(gasEmpty))'}
env_safe |= {'inG -> (X(ones = "9") && X(tens = "4") && X(!gasEmpty))'}
env_prog = list()

# System variables and requirements
sys_vars = ['goToA', 'goToB']
sys_init = ['inA', 'goToA', 'goToB']
sys_safe = set()
sys_safe |= {'(X(goToB)<->(inB ||(!(inA)))) || (goToB && !(inA))'}
sys_safe |= {'(X(goToA)<->(inA ||(!(inB)))) || (goToA && !(inB))'}
sys_safe |= {'!(gasEmpty && !inG)'}
sys_safe |= {'!inObj1'}
sys_safe |= {'!inObj2'}
sys_prog = ['goToA', 'goToB']

# (ctrl_modes, grspec) = transform2control(disc_dynamics.ts,  statevar='ctrl')

print("----------------------------------\n Combine sys and spec \n----------------------------------")

# phi = grspec | spec.GRSpec(env_vars, sys_vars, env_init, sys_init,
#                            env_safe, sys_safe, env_prog, sys_prog)

phi = spec.GRSpec(env_vars, sys_vars,
                  env_init, sys_init,
                  env_safe, sys_safe,
                  env_prog, sys_prog)

phi.qinit = '\A \E'
phi.moore = False
phi.plus_one = False

ctrl = synth.synthesize(phi, ignore_sys_init=True)

with open("cimple_c_from_py.c", "w") as f:
    f.write(dumpsmach.write_init_file(ctrl, sys_dyn, disc_dynamics, 5, 2, 0.0, name="DroneV2"))
#
# print("----------------------------------\n Reduce states \n----------------------------------")
#
# Events_init = {('inA', True)}
#
#
# ctrl_red = reduce_mealy(ctrl, relabel=False, outputs={'ctrl'}, prune_set=Events_init, combine_trans=False)

print("----------------------------------\n Output results  \n----------------------------------")

if verbose == 1:
    print(" (Verbose) ")
    try:
        disc_dynamics.ts.save("cimple_aircraft_orig.png")
        # ctrl_modes.save("cimple_aircraft_modes.png")
        # ctrl_red.save('cimple_aircraft_ctrl_red.png')
        ctrl.save("cimple_aircraft_ctrl_orig.png")

        print(" (Verbose): saved all Finite State Transition Systems ")

    except Exception:
        pass

    print('nodes in ctrl:')
    print(len(ctrl.nodes()))
    print(len(ctrl.transitions()))
    print('\n')

    # print('nodes in ctrl_red:')
    # print(len(ctrl_red.nodes()))
    # print(len(ctrl_red.transitions()))
    # print('\n')


print("----------------------------------\n Convert controller to Xmi \n----------------------------------")
sys.stdout.flush()

# --------------- Writing the statechart -----------
try:
    filename = str(__file__)
    filename = filename[0:-3] + "_gen"
except NameError:
    filename = "test_gen"
#
# # write strategy plus control modes at the same time to a statechart
# with open(filename+".xml", "w") as f:
#     f.write(dumpsmach.tulip_to_xmi(ctrl_red, ctrl_modes))

# with open("cimple_c_from_py.c", "w") as f:
#     f.write(dumpsmach.write_init_file(ctrl_red, sys_dyn, disc_dynamics, 5, 2, 0.0, name="DroneV2"))
