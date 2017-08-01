""" Tulip to ULM chart:  Thermostat Examples
Written by S.Haesaert

CREDIT
    Based on code of Sumanth Dathathri & 
    Scott C. Livingston &
    Leonard J. Reder  & Richard M. Murray 
CONTENT    
    This file contains an re-implementation of their Thermostat example for Tulip 3.6
 DATE    22 May 
"""

# Import modules
from __future__ import print_function

import numpy as np
import sys
import sys
#sys.path.append("..")

from tulip import spec, hybrid
import synth2 as synth
from tulip.abstract import prop2part, discretize
from polytope import box2poly
from Reduce import *
import Interface.Statechart as dumpsmach
from Interface.Transform import *


print("----------------------------------\n Script options \n----------------------------------")
verbose = 0 # Decrease printed output = 0, increase= 1

print("""----------------------------------\n System Definition \n----------------------------------
         -- System Constants 
         -- System Label State Space & partition

         """)
# Define the to be used system constants
epsilon = 1.
input_bound = 1.0
disturbance_bound = 0.1
goal = 73.  # deg F

# The system dynamics
A = np.array([[1.]])
B = np.array([[1.]])
E = np.array([[1.]])
# $x^+=Ax+Bu+E W$

# Size of the sets
X = box2poly([[60., 85]])
U = box2poly(input_bound*np.array([[-1., 1]]))
W = box2poly(disturbance_bound*np.array([[-1., 1]]))
#  ----------------------------------\n Define system\n----------------------------------
# Intermezzo polytope tutorial
#  https://github.com/tulip-control/polytope/blob/master/doc/tutorial.md
sys_dyn = hybrid.LtiSysDyn(A, B, E, None, U, W, X)

print(A)
print(str(sys_dyn))

#----------------------------------\n Define labelling \n----------------------------------")

cprops ={}
cprops["l"] = box2poly([[60., 65]])
cprops["g"] = box2poly([[goal-epsilon, goal+epsilon]])
cprops["init"] = box2poly([[76., 78.]])
cprops["h"] = box2poly([[80., 85]])

cpartition = prop2part(X, cprops)
if verbose == 1:
    print("part before refinement")
    print(cpartition)
#  ----------------------------------\n System partition State Space \n----------------------------------

disc_dynamics = discretize(cpartition, sys_dyn,
                           closed_loop=True, conservative=True,
                           N=5, min_cell_volume=0.1)

states=[state for (state, label) in disc_dynamics.ts.states.find(with_attr_dict={'ap': {'init'}})]
disc_dynamics.ts.states.initial|=states

# part, ssys, N=10, min_cell_volume=0.1,
#   closed_loop=True, conservative=False,
#   max_numpoly=5, use_all_horizon=False,
#   trans_length=1, remove_trans=False,
#   abs_tol=1e-7,
#   plotit=False, save_img=False, cont_props=None,
#   plot_every=1

states = [state for (state, label) in disc_dynamics.ts.states.find(with_attr_dict={'ap': {'init'}})]
disc_dynamics.ts.states.initial |= states



print("----------------------------------\n Define specification \n----------------------------------")

# Specifications
# Environment variables and assumptions
env_vars=["bump"]
env_init=["!bump"]
env_safe=['bump -> (X !bump)']
env_prog=list()

# System variables and requirements
sys_vars=list()
sys_init=list()
sys_safe=['!l', '!h', '(( (bump) ) -> X!g )']
sys_prog=['g']

(ctrl_modes, grspec) = transform2control(disc_dynamics.ts,  statevar='ctrl')

phi = grspec | spec.GRSpec(env_vars, sys_vars, env_init,sys_init,
                           env_safe, sys_safe, env_prog,sys_prog)

print("----------  ------------------------\n Combine sys and spec \n----------------------------------")


phi.qinit = '\A \E'
phi.moore = False
phi.plus_one=False

ctrl = synth.synthesize(phi,ignore_sys_init=True)



print("----------------------------------\n Reduce sys  \n----------------------------------")
ctrl_s = prune_init(ctrl, init_event={('bump', False)})
ctrl_red=reduce_mealy(ctrl,relabel=False,outputs={'ctrl'})
ctrl_red2 = ctrl_red.copy()
ctrl_red2 = combine_transitions(ctrl_red2)

print("----------------------------------\n Output results  \n----------------------------------")

if verbose == 1:
    print(" (Verbose) ")
    try:
        disc_dynamics.ts.save("Images/Thermo_orig.png")
        ctrl_modes.save("Images/Thermo_modes.png")
        ctrl_red2.save('Images/Thermo_ctrl_tr.png')
        ctrl_red.save('Images/Thermo_ctrl_red.png')
        ctrl.save("Images/Thermo_ctrl_orig.png")

        print(" (Verbose): saved all Finite State Transition Systems ")

    except Exception:
        pass

    print('nodes in ctrl:')
    print(len(ctrl.nodes()))
    print(len(ctrl.transitions()))
    print('\n')

    print('nodes in ctrl_red:')
    print(len(ctrl_red.nodes()))
    print(len(ctrl_red.transitions()))
    print('\n')

    print('nodes in ctrl_red2:')
    print(len(ctrl_red2.nodes()))
    print(len(ctrl_red2.transitions()))
    print('\n')



print("----------------------------------\n Convert controller to Xmi \n----------------------------------")
sys.stdout.flush()

# --------------- Writing the statechart -----------
try:
    filename = str(__file__)
    filename = filename[0:-3] + "_gen"
except NameError:
    filename = "test_gen"

# write strategy plus control modes at the same time to a statechart
with open(filename+".xml", "w") as f:
   f.write(dumpsmach.tulip_to_xmi(ctrl_red2,ctrl_modes))