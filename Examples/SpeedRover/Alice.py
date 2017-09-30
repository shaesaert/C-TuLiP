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

import sys

import numpy as np
from polytope import box2poly
from tulip import hybrid
from tulip.abstract import prop2part, discretize

import Interface.DSL as DSL
from Interface import Statechart
from Interface.Reduce import *
from Interface.Transform import *

# TODO  1. Low-level control actions are missing
print("----------------------------------\n Script options \n----------------------------------")

verbose = 1  # 1 = print and save all intermediate automatons,
#              0 = don't print and save.



Cases = ['1 Sensor', '2 Sensors', '3 Sensors']
Orig_len = ()
Orig_trans = ()
Red_len = ()
Red_trans = ()
for Case in Cases:

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

        env_vars = {'lidon'}    # one new environment variable
        env_init = {'!lidon'}
        env_safe, env_prog = set(), set()

        sys_vars = set()  # no new system variables
        sys_init = {'init'}
        sys_safe = {'lidon->(X(moderate))', '(!lidon)->(X(!(moderate)))','!fast'}
        sys_prog = set()
        psi = spec.GRSpec(env_vars, sys_vars, env_init, sys_init,
                    env_safe, sys_safe, env_prog, sys_prog)
        Events_init = {('lidon', False)}

    elif Case == '2 Sensors':
        # -------------Simple specification
        #  example with only 4 labels
        cprops = dict()
        cprops["init"] = box2poly([[0., 5.]])
        cprops["slow"] = box2poly([[5.0, 10]])
        cprops["moderate"] = box2poly([[10.0, 15]])
        cprops["fast"] = box2poly([[15.0, 20]])

        psi =DSL.Xtimes('fast', owner='sys') | DSL.Xtimes('init', owner='sys')  # introduce X1fast and X1init

        env_vars = {'lidon','steron'}
        env_init = {'!lidon && !steron'}
        env_safety = ['(lidon -> X(lidon))||(steron -> X(steron))']
        env_safety += ['(!lidon -> X(!lidon)) || (!steron -> X(!steron))']
        env_safety += ['lidon -> steron']


        sys_init = {'init'}
        sys_safety = {'((lidon && steron)&& (X(lidon) & X(steron)) -> X (X1fast)) '}
        sys_safety |= {'(!steron && X(!steron)) -> (X(X1init))'}
        sys_safety |= {'((!lidon && steron) -> X(!fast && !init))'}
        psi |= spec.GRSpec(env_vars=env_vars, env_init=env_init, env_safety=env_safety,
                           sys_init=sys_init, sys_safety=sys_safety)
        Events_init = {('lidon', False),('steron',False)}

        print(psi.pretty())
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

        sys_vars ={}# {'Aux'} # new progress variables
        sys_init = {'init'}#,'Aux'}
        sys_safe = set()
        sys_safe |= {'init->(((X init)||stereo))'}  # if you try a reboot
                        # you are staying there until the stereo turns on
        sys_safe |= {'(moderate || fast)->((X(moderate||fast))||(!((lidon || radon) & stereo)))'}
                        # Constant speed
        sys_safe |= {'(init & freeway & (!((lidon || radon) & stereo)))->(X(init || !(freeway)))'}
        sys_safe |= {'(slow & (!((lidon || radon) & stereo)))->(X(slow || init))'}

        # [] <> '(init || stereo)',[] <> '(!(slow & freeway))', [] <> '(moderate || fast || !((lidon||radon) & stereo))'
        sys_prog = {'(init || stereo)', '(!(slow & freeway))', '(moderate || fast || !((lidon||radon) & stereo))'}
        psi = spec.GRSpec(env_vars, sys_vars, env_init, sys_init,
                          env_safe, sys_safe, env_prog, sys_prog)\
              | DSL.response(trig='(stereo & !(lidon || radon))',
                             react='((X(slow) & !freeway) || (freeway & X(init)))', owner='sys')

        Events_init = {('lidon', False),('stereo', False),('radon', False),('freeway', False)}


    else:
        print("WRONG name for 'Case'")
        raise Exception(NameError)

    print("----------------------------------\n System partition State Space \n----------------------------------")


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
    disc_dynamics.ts.states.initial |= states


    print("----------------------------------\n  Make GR(1) specification \n----------------------------------")
    (ctrl_modes, grspec) = transform2control(disc_dynamics.ts,  statevar='ctrl')

    phi = grspec | psi
    print(phi.pretty())
    phi.qinit = '\A \E'
    phi.moore = False
    phi.plus_one = False
    print("----------------------------------\n Make Controller \n----------------------------------")
    ctrl = synth.synthesize(phi, ignore_sys_init=True,solver='gr1c')
    ctrl_red = reduce_mealy(ctrl, relabel=True, outputs={'ctrl'},
                           prune_set=Events_init, combine_trans=False)


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
       f.write(Statechart.tulip_to_xmi(ctrl_red, ctrl_modes))
    # Alternatively, they can be programmed one by one:
    # -- the discrete strategy:
    #   with open(filename+".xml", "w") as f:
    #       f.write(dumpsmach.mealy_to_xmi_uml(ctrl_red, env_events=True, name="Alice", outputs={'ctrl'}, relabel=True,Type='strat'))

    # -- the control modes
    # with open("low_ctrl"+".xml", "w") as f:
    #    f.write(dumpsmach.mealy_to_xmi_uml(ctrl_modes,name="Ctrl_modes",outputs={'act'},relabel=True, Type='control'))

    # write strategy plus control modes at the same time to a statechart

    print('Original model:')
    Orig_len += (str(len(ctrl.nodes())),)
    print(Orig_len[-1])
    Orig_trans += (str(len(ctrl.transitions())),)
    print(Orig_trans[-1])
    print('\n')

    print('Reduced model:')
    Red_len += (str(len(ctrl_red.nodes())),)
    print(Red_len[-1])
    Red_trans += (str(len(ctrl_red.transitions())),)
    print(Red_trans[-1])
    print('\n')

    print('\n')
    with open("Tabular.txt", "w") as f:
        f.write("Original & " + str(len(ctrl.nodes())) + " & " + str(len(ctrl.transitions())) + "& "
                + str(len(ctrl.nodes())) + " & " + str(len(ctrl.transitions())) + "\n")

print("----------------------------------\n Output results  \n----------------------------------")

with open("Tabular.txt", "w") as f:
    f.write(" & " +Cases[0] + " & " + Cases[1] + " & " + Cases[2] + "\\\\ \n")
    f.write("Orig. nodes & " + Orig_len[0] + " & " + Orig_len[1] + " & " + Orig_len[2] + "\\\\ \n ")
    f.write("Orig. trans. & " + Orig_trans[0] + " & " + Orig_trans[1] + " & " + Orig_trans[2] + "\\\\ \n")
    f.write("Red. nodes & " + Red_len[0] + " & " + Red_len[1] + " & " + Red_len[2] + "\\\\ \n")
    f.write("Red. trans. & " + Red_trans[0] + " & " + Red_trans[1] + " & " + Red_trans[2] + "\\\\ \n")



if verbose == 1 and Case is not '3 Sensors':
    print(" (Verbose) ")
    try:
        save_png(disc_dynamics.ts, name=filename[0:-3]+"dyn")
        save_png(ctrl_modes,filename[0:-3]+"ctrl_modes")
        #
        print(len(list(ctrl.nodes())))
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

