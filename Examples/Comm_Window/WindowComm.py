""" Tulip to ULM chart:  Communication window example
Written by S.Haesaert

CREDIT 
    Leonard J. Reder  & Richard M. Murray 
CONTENT    
    This file contains the communication window manager example for Tulip 1.4
 DATE    5th of June
"""
from __future__ import print_function

import Interface.Statechart as dumpsmach
from Interface.Reduce import *
from Interface.Transform import *

print("----------------------------------\n Script options \n----------------------------------")
verbose = 1

print("----------------------------------\n Finite State Transition System: radio ELT \n----------------------------------")

print("\n 1. Describe state of list with a FTS:")
 # Define
ts_elt = transys.FiniteTransitionSystem()  # Define empty transition system
#  its atomic propositions
ts_elt.atomic_propositions.add_from({'ELT_ON'}) # 'ELT_Off',
ts_elt.owner='env'
ts_elt.name='ELT'

# its states
ts_elt.states.add(0)#, ap={'ELT_Off'})
ts_elt.states.add(1, ap={'ELT_ON'})
# its initial states
ts_elt.states.initial |= {0}

# Add Transitions
ts_elt.actions['sys_actions'] |= {'ELCTRA_RADIO_OFF', 'ELCTRA_RADIO_ON'}  # these are the action of the environment

ts_elt.transitions.add(0, 1, sys_actions='ELCTRA_RADIO_ON')
ts_elt.transitions.add(1, 0, sys_actions='ELCTRA_RADIO_OFF')


## layout of graph

ts_elt.states.paint(0, 'red')
ts_elt.states.paint(1, 'green')

ts_elt.transitions.graph._transition_dot_label_format['env_actions']='env'
ts_elt.transitions.graph._transition_dot_label_format['separator']= r"\n"

ts_elt.save('comm_ex_elt.eps')



print("----------------------------------\n Finite State Transition System: radio SDST \n----------------------------------")

print("\n 1. Describe state of list with a FTS:")
 # Define
ts_sdst = transys.FiniteTransitionSystem()  # Define empty transition system
#  its atomic propositions
ts_sdst.atomic_propositions.add_from({'SDST_ON'}) #'SDST_Off',
ts_sdst.owner='env'
ts_sdst.name='SDST'

# its states
ts_sdst.states.add(0)#, ap={'SDST_Off'})
ts_sdst.states.add(1, ap={'SDST_ON'})
# its initial states
ts_sdst.states.initial |= {1}

# Add Transitions
ts_sdst.actions['sys_actions'] |= {'SDST_RADIO_OFF', 'SDST_RADIO_ON'}  # these are the action of the environment

ts_sdst.transitions.add(0, 1, sys_actions='SDST_RADIO_ON')
ts_sdst.transitions.add(1, 0, sys_actions='SDST_RADIO_OFF')


## layout of graph

ts_sdst.states.paint(0, 'red')
ts_sdst.states.paint(1, 'green')

ts_sdst.transitions.graph._transition_dot_label_format['env_actions']='env'
ts_sdst.transitions.graph._transition_dot_label_format['separator']=r"\n"

ts_sdst.save('comm_ex_sdst.eps')




print("----------------------------------\n Finite State Transition System :  Combine systems\n----------------------------------")
new_ts=async_prod(ts_sdst,ts_elt)
new_ts.save('combine_radios.png')
ts_env_complete=trans_complete(new_ts)
ts_env_complete.save('ts_env_complete.png')

gr_env00= synth.env_to_spec(ts_elt, False,'env')#,'ap_list':ts_window.ap})

gr_env= synth.env_to_spec(ts_env_complete, False,'env', aps={'ap_ELT':ts_elt.ap,'ap_SDST':ts_sdst.ap})#,'ap_list':ts_window.ap})
print(gr_env00.pretty())


print("----------------------------------\n Finite State Transition System: list\n----------------------------------")
print("\n 1. Describe state of list with a FTS:")
 # Define
cfg_time = 2

ts_window = transys.FiniteTransitionSystem()  # Define empty transition system
#  its atomic propositions
ts_window.atomic_propositions.add_from({'idle', 'cfg','transmit','cln'})
ts_window.owner='env'
ts_window.name='window'

# its states
st=0
ts_window.states.add(st, ap={'idle'})
ts_window.transitions.add(st, st)

for i in range(cfg_time):
    st += 1
    ts_window.states.add(st, ap={'cfg'})
    ts_window.states.paint(st, 'yellow')


st += 1
ts_window.states.add(st, ap={'transmit'})
ts_window.states.paint(st, 'green')

ts_window.transitions.add(st, st)

for i in range(cfg_time):
    st += 1
    ts_window.states.add(st, ap={'cln'})
    ts_window.states.paint(st, 'yellow')


ts_window.transitions.add(st, 0)

for i in range(st):
    ts_window.transitions.add(i, i+1)

# its initial states
ts_window.states.initial |= {0}

print(" \n 2. system actions as additions and removals of the list")

ts_window.save('comm_ex_window.png')

gr_window = synth.env_to_spec(ts_window, False,'window')
print(gr_window.pretty())


print("---------------------\n Can the radios be controlled? \n------------")

env_vars = list()
env_init = list()
env_safe = list()
env_prog = list()

# System variables and requirements
sys_vars = list()
sys_init = list()
sys_safe = ['ELT_ON || SDST_ON']
sys_safe += ['(transmit && (!SDST_ON && ELT_ON)) || !transmit']
sys_safe += ['(idle && (SDST_ON && !ELT_ON)) || !idle']
sys_prog = list()


specs = spec.GRSpec(env_vars, sys_vars, env_init,sys_init,
                    env_safe, sys_safe, env_prog,sys_prog)

specs |= gr_env
specs |= gr_window

print("----------------------------------\n Synthesize control \n----------------------------------")

specs.qinit = '\A \E'
specs.moore = False
specs.plus_one = False

ctrl=synth.synthesize(specs, ignore_sys_init=False, solver='gr1c')

print("----------------------------------\n Remove auxiliary inputs \n----------------------------------")
inputs = {'idle', 'cfg','transmit','cln'}
ctrl_rem = remove_aux_inputs(ctrl, inputs)

print("----------------------------------\n Reduce states \n----------------------------------")

Events_init = {('idle', 1),('cfg', 0), ('transmit', 0), ('cln', 0)}

ctrl_red = reduce_mealy(ctrl_rem, outputs={'sys_actions'},
                        relabel=True, prune_set=Events_init, full=False, combine_trans=False)


print("---------------------\n Communication window controller \n------------")

try:
    filename = str(__file__)
except NameError:
    filename = "test"

filename = filename[0:-3] + "_gen"

with open(filename+".xml", "w") as f:
    f.write(dumpsmach.mealy_to_xmi_uml(ctrl_red, outputs={'sys_actions'}, name="CommWindow", relabel=False))


print("---------------\n Pictures \n-------------")
save_png(ctrl_red, name='ctrl_red')
save_png(ctrl_rem, name='ctrl_rem')

if not ctrl.save("Window_simple.eps"):
    print(ctrl)
