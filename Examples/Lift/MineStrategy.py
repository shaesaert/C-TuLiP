""" Tulip to ULM chart: Lift 
CREDIT

    Scott1. Piterman, Nir et al.: Synthesis of Reactive(1) Designs. 2006
"""

from __future__ import print_function
from dd import cudd
#from tulip import spec, hybrid
import synth2 as synth
import Interface.Statechart as dumpsmach
from Reduce import *
import Interface.DSL as DSL
from itertools import combinations, cycle

# the specification of the lift (sec 5.2)
n=2
# define boolean variables for the buttons & the floors
b = []
f = []
for i in range(n):
    b += ['b' + str(i + 1)]  # button at i-th floor is enabled or disables
    f += ['f' + str(i + 1)]  # lift is at i-th floor

env_vars, sys_vars, env_init, sys_init = set(), set(), set(), set()
env_safe, sys_safe, env_prog, sys_prog = set(), set(), set(), set()
# How the button behaves
for i in range(n):
    env_vars |= {b[i]}
    env_init |= {'!' + b[i]}
    env_safe |= {'( ' + b[i] + ' && ' + f[i] + ') -> ( X (!' + b[i] + ') )'}
    env_safe |= {'( ' + b[i] + ' && !' + f[i] + ') -> ( X (' + b[i] + ') )'}

# how the lift behaves
# 1. it cannot be at more than 1 floor at a time
# 2. at any state lift can go 1 up, 1 down or stay
sys_safe |= {' && '.join(['!( ' + f[i] + ' && ' + f[j] + ' ) ' for (i, j) in combinations(range(n), 2)])}

for i in range(n):
    sys_vars |= {f[i]}
    f_down = ' || ' + f[i - 1] if i > 0 else ''
    f_up = ' || ' + f[i + 1] if i < n - 1 else ''
    sys_safe |= {f[i] + ' -> ' + '(' + f[i] + f_down + f_up + ')'}

# the lift should not move up unless some button is pressed
# equivalent to, if u are moving up, then a button should be on

sys_vars |= {'bon'}  # some button is on (AUX)
sys_vars |= {'fup'}  # moving up         (AUX)

# \/i (f_i && f_i+1)
sys_safe |= {
'fup' + ' <-> (' + ' || '.join([' ( ' + f[i] + ' && X ' + f[i + 1] + ' ) ' for i in range(n - 1)]) + ' ) '}
sys_safe |= {'bon' + ' <-> (' + ' || '.join([b[i] for i in range(n)]) + ' ) '}

sys_safe |= {'fup -> bon'}

sys_prog |= {f[0] + ' || bon'}
# either button keeps being used (buttons are pressed)
#  or the lift moves to the first floor infinitly many times
for i in range(n):
    sys_prog |= {'!' + b[i]}

# we require that the lift eventually satisfies every request
#  (i.e. button being turned on)
psi = spec.GRSpec(env_vars, sys_vars, env_init, sys_init,
                  env_safe, sys_safe, env_prog, sys_prog)
# for i in range(n):
#    psi |= DSL.response(trig=b[i], react=f[i], owner='sys', aux='aux' + str(i+1))
print(psi.pretty())

psi.qinit = '\A \E'
psi.moore = False
psi.plus_one = False

ctrl = synth.synthesize(psi, ignore_sys_init=False, solver='gr1c')
# found a controller
print('controller found')
ctrl_s = synth.determinize_machine_init(ctrl)

ctrl_red = reduce_mealy(ctrl_s, relabel=True, outputs=set(f),
                        prune_set=None, combine_trans=False)
