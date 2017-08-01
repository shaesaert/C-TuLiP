""" Tulip to ULM chart: Alice 2
CREDIT
    Based on code of Sumant Dathathri & 
    Scott C. Livingston &
    Leonard J. Reder  & Richard M. Murray 
CONTENT    
    This file contains an re-implementation of their Alice 2 speed control example
 DATE    May 1st -- 22 June
"""

from __future__ import print_function

import numpy as np
import sys
from tulip import spec, hybrid
import synth2 as synth
from tulip.abstract import prop2part, discretize
from polytope import box2poly
from Reduce import *
import Interface.Statechart as dumpsmach
from Interface.Transform import *

# TODO  1. Low-level control actions are missing
print("----------------------------------\n Script options \n----------------------------------")

verbose = 1  # 1 = print and save all intermediate automatons,
#              0 = don't print and save.


Case = '1 Sensor' # in { '1 Sensor',  '2 Sensors', '3 Sensors'}
Case = '2 Sensors'
Case = '3 Sensors'
 # or 'Paper simple'
 # or 'Complex'

print("----------------------------------\n System Constants \n----------------------------------")

epsilon = 1.
input_bound = 2
disturbance_bound = 0.01

A = np.array([[1.]])
B = np.array([[1.]])
E = np.array([[1.]])

X = box2poly([[0., 20]])
U = box2poly(input_bound * np.array([[-1., 1]]))
W = box2poly(disturbance_bound * np.array([[-1., 1]]))



if Case == '1 Sensor' :
    # -------------Simple specification
    #  example with only 4 labels
    cprops = dict()
    cprops["init"] = box2poly([[0., 5.]])
    cprops["slow"] = box2poly([[5.0, 10]])
    cprops["moderate"] = box2poly([[10.0, 15]])
    cprops["fast"] = box2poly([[15.0, 20]])

    env_vars = {'lidon'}
    env_init = {'!lidon'}
    env_safe =set()#{'(env_actions = "reach")'}# ['lidon &&(env_actions = "reach")']
    env_prog = set()

    sys_vars = set() #{'A','B','C'}
    sys_init = {'init'}
    sys_safe = {' lidon->(X(moderate))', '(!lidon)->(X(!(moderate)))','!fast'}
    sys_prog = set()


    Events_init = {('lidon', False)}

    sys.stdout.flush()

elif Case == '2 Sensors':
    # -------------Simple specification
    #  example with only 4 labels
    cprops = dict()
    cprops["init"] = box2poly([[0., 5.]])
    cprops["slow"] = box2poly([[5.0, 10]])
    cprops["moderate"] = box2poly([[10.0, 15]])
    cprops["fast"] = box2poly([[15.0, 20]])




    env_vars = {'lidon','steron'}
    env_init = {'!lidon && !steron'}
    env_safe = {'(lidon -> X(lidon))||(steron -> X(steron))'}
    env_safe |= {'(!lidon -> X(!lidon)) || (!steron -> X(!steron))'}
    env_safe |={'lidon -> steron'}

    env_prog = set()

    sys_vars = {'Xfast','Xslow','Xinit'} #{'A','B','C'}
    sys_init = {'init'}
    sys_safe = {'((lidon & steron)& (X(lidon) & X(steron)) -> X (Xfast)) '}
    sys_safe |= {'X(fast) <-> (Xfast)'}
    #sys_safe |= {'X(slow) <-> (Xslow)'}
    sys_safe |= {'X(init) <-> (Xinit)'}

    sys_safe |= {'(!steron && X(!steron)) -> (X(Xinit))'}
    sys_safe |= {'((!lidon & steron) -> X(!fast & !init))'}

    sys_prog = set()

    Events_init = {('lidon', False),('steron',False)}

    sys.stdout.flush()


elif Case == '3 Sensors':
    print("----------------------------------\n Describe Labeling and Specification \n----------------------------------")
    print("complex")

    #  example with only 4 labels
    cprops = dict()
    cprops["init"] = box2poly([[0., 5.]])
    cprops["slow"] = box2poly([[5.0, 10]])
    cprops["moderate"] = box2poly([[10.0, 15]])
    cprops["fast"] = box2poly([[15.0, 20]])



    env_vars = {'lidon', 'radon', 'stereo', 'freeway'}
    env_init = {'!lidon', '!radon', '!stereo', '!freeway'}
    env_safe = {'(lidon->X(lidon))|| (radon->X(radon))', '(stereo->X(stereo))|| (radon->X(radon))',
                '(stereo->X(stereo))|| (lidon->X(lidon))'}
    env_prog = set()

    sys_vars = {'Aux', 'Aux2', 'Aux3', 'Aux4'}
    sys_init = {'init', 'Aux', 'Aux2', 'Aux3', 'Aux4'}
    sys_safe = set()
    #sys_safe |= {'(X(Aux) <-> (init || stereo)) || (Aux && (stereo))'} # Infinitely often the stereo should be on or a reboot should be performed
    # TODO rewrite as:
    sys_safe |= {'((Aux) <-> (init || stereo))'}
    sys_safe |= {'init->(((X init)||stereo))'} # ok => remark if you try a reboot
    # you are staying there until the stereo turns on

    #sys_safe |= {'(X(Aux2) <-> (moderate || init || fast || (!(freeway)))) || (Aux2 && !(freeway))'}
                # dont keep driving slow on the highway
    #sys_safe |= {'(X(Aux3) <-> (moderate || fast || !((lidon||radon) & stereo))) || (Aux3 && !((lidon || radon) & stereo))'}
    sys_safe |= {'((Aux3) <-> (moderate || fast || !((lidon||radon) & stereo))) '}

    #sys_safe |= {'((Aux2) <-> (moderate || init || fast || (!(freeway)))) '}
    sys_safe |= {'((Aux2) <-> (!(slow & freeway))) '}

    sys_safe |= {'(X(Aux4) <-> ((X(slow) & !freeway) || (freeway & X(init)))) || (Aux4 && !(stereo & !(lidon || radon)))'}
    sys_safe |= {'(init & freeway & (!((lidon || radon) & stereo)))->(X(init || !(freeway)))'}


    sys_safe |= {'(moderate || fast)->((X(moderate||fast))||(!((lidon || radon) & stereo)))'}

    sys_safe |= {'(slow & (!((lidon || radon) & stereo)))->(X(slow || init))'}



    sys_prog = {'Aux', 'Aux2', 'Aux3', 'Aux4'}
    Events_init = {('lidon', False),('stereo', False),('radon', False),('freeway', False)}


else:
    print("WRONG name for 'Case'")
    raise Exception(NameError)

print("----------------------------------\n System partition State Space \n----------------------------------")


print("------  System Definition")


print("------ System Label State Space & partition")
sys_dyn = hybrid.LtiSysDyn(A, B, E, None, U, W, X)

cpartition = prop2part(X, cprops)
if verbose == 1:
    sys.stdout.flush()
    print(" (Verbose) ")
    print(cpartition)
    sys.stdout.flush()


disc_dynamics = discretize(cpartition, sys_dyn,
                           closed_loop=True, conservative=False,
                           N=5, min_cell_volume=0.1,  remove_trans=True)

save_png(disc_dynamics.ts, name="dynamics")
states = [state for (state, label) in disc_dynamics.ts.states.find(with_attr_dict={'ap': {'init'}})]
disc_dynamics.ts.states.initial|=states


print("----------------------------------\n  Make GR(1) specification \n----------------------------------")
(ctrl_modes, grspec) = transform2control(disc_dynamics.ts,  statevar='ctrl')
#gr_sys=synth.sys_to_spec(ctrl_modes, True, 'ctrl')

phi=grspec|spec.GRSpec(env_vars, sys_vars, env_init,sys_init,
                           env_safe, sys_safe, env_prog,sys_prog)
print(phi.pretty())
phi.qinit = '\A \E'
phi.moore = False
phi.plus_one=False

#ctrl = synth.synthesize(phi, sys=disc_dynamics.ts, ignore_sys_init=True, solver='gr1c')
#ctrl = synth.synthesize(phi, ignore_sys_init=True, solver='gr1c')

print("----------------------------------\n Make Controller \n----------------------------------")
ctrl = synth.synthesize(phi, ignore_sys_init=True,solver='gr1c')
ctrl_red= reduce_mealy(ctrl, relabel=True, outputs={'ctrl'},
                       prune_set=Events_init, combine_trans=True)


print("----------------------------------\n Convert controller to Xmi \n----------------------------------")

# --------------- Writing the statechart -----------
try:
    filename = str(__file__)
    filename = filename[0:-3]
    if Case == '1 Sensor':
        filename += '1'+ "_gen"
    elif Case == '2 Sensors':
        filename += '2'+ "_gen"
    elif Case == '3 Sensors':
        filename += '3' + "_gen"
    else:
        filename += "_gen"
except NameError:
    filename = "test_gen"

# write strategy plus control modes at the same time to a statechart
with open(filename+".xml", "w") as f:
   f.write(dumpsmach.tulip_to_xmi(ctrl_red,ctrl_modes))
# Alternatively, they can be programmed one by one:
# -- the discrete strategy:
#   with open(filename+".xml", "w") as f:
#       f.write(dumpsmach.mealy_to_xmi_uml(ctrl_red, env_events=True, name="Alice", outputs={'ctrl'}, relabel=True,Type='strat'))

# -- the control modes
# with open("low_ctrl"+".xml", "w") as f:
#    f.write(dumpsmach.mealy_to_xmi_uml(ctrl_modes,name="Ctrl_modes",outputs={'act'},relabel=True, Type='control'))



print("----------------------------------\n Output results  \n----------------------------------")

if verbose == 1 and Case is not '3 Sensors':
    print(" (Verbose) ")
    try:
        save_png(disc_dynamics.ts, name=filename[0:-3]+"dyn")
        save_png(ctrl_modes,filename[0:-3]+"ctrl_modes")
        #
        print( len(list(ctrl.nodes())))
        if len(list(ctrl_red.nodes()))<100:
            save_png(ctrl_red, filename[0:-3] + "red")



        print(" (Verbose): saved all Finite State Transition Systems ")
    except Exception:
        pass

if Case is '3 Sensors':
    try:
        save_png(disc_dynamics.ts, name=filename[0:-3]+"dyn")
        save_png(ctrl_modes,filename[0:-3]+"ctrl_modes")
        print('Start saving control')
        save_png(ctrl_red, filename[0:-3] + "trn")
    except Exception:
        pass

sys.stdout.flush()

print('nodes in ctrl:')
print(len(ctrl.nodes()))
print(len(ctrl.transitions()))
print('\n')
#
# print('nodes in ctrl_red:')
# print(len(ctrl_red.nodes()))
# print(len(ctrl_red.transitions()))
# print('\n')
#
# print('nodes in ctrl_redb:')
# print(len(ctrl_redb.nodes()))
# print(len(ctrl_redb.transitions()))
# print('\n')
#
# print('nodes in ctrl_red2:')
# print(len(ctrl_red2.nodes()))
# print(len(ctrl_red2.transitions()))
# print('\n')

print('nodes in ctrl_red3:')
print(len(ctrl_red.nodes()))
print(len(ctrl_red.transitions()))
print('\n')

#print('nodes in ctrl_red4:')
#print(len(ctrl_red4.nodes()))
#print(len(ctrl_red4.transitions()))
print('\n')