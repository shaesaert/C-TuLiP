""" Tulip to ULM chart: Lift 
CREDIT
    
    Scott1. Piterman, Nir et al.: Synthesis of Reactive(1) Designs. 2006
"""

from __future__ import print_function
from __future__ import absolute_import

import logging
import time
from itertools import combinations, cycle

from tulip import spec
from tulip.interfaces import omega as omega_int
try:
    import dd.bdd as _bdd
except ImportError:
    _bdd = None
try:
    from dd import cudd
except ImportError:
    cudd = None
try:
    import omega
    from omega.logic import bitvector as bv
    from omega.games import gr1
    from omega.symbolic import symbolic as sym
    from omega.games import enumeration as enum
except ImportError:
    omega = None
import networkx as nx
log = logging.getLogger(__name__)


from Interface.Reduce import *

# the specification of the lift (sec 5.2)
n = 2  # number of floors (minimum =2)


# define boolean variables for the buttons & the floors
b = []
f = []
for i in range(n):
    b += ['b' + str(i + 1)] # button at i-th floor is enabled or disables
    f += ['f' + str(i + 1)] # lift is at i-th floor


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
sys_safe |= {' && '.join(['!( ' + f[i] + ' && ' + f[j] + ' ) ' for (i,j) in combinations(range(n),2)]) }

for i in range(n):
    sys_vars |= {f[i]}
    f_down = ' || ' +  f[i-1] if i > 0 else ''
    f_up = ' || ' + f[i+1] if i < n-1 else ''
    sys_safe |= {f[i] + ' -> ' + '(' + f[i] + f_down + f_up + ')'}

# the lift should not move up unless some button is pressed
# equivalent to, if u are moving up, then a button should be on

sys_vars |= {'bon'} # some button is on (AUX)
sys_vars |= {'fup'} # moving up         (AUX)

# \/i (f_i && f_i+1)
sys_safe |= {'fup' + ' <-> (' + ' || '.join([' ( ' + f[i] + ' && X ' + f[i+1]+' ) ' for i in range(n-1)]) + ' ) '}
sys_safe |= {'bon' + ' <-> (' + ' || '.join([b[i] for i in range(n)]) + ' ) '}

sys_safe |= {'fup -> bon'}

sys_prog |= { f[0] + ' || bon'}
# either button keeps being used (buttons are pressed)
#  or the lift moves to the first floor infinitly many times
for i in range(n):
    sys_prog |= {'!' + b[i]}

# we require that the lift eventually satisfies every request
#  (i.e. button being turned on)
psi = spec.GRSpec(env_vars, sys_vars, env_init, sys_init,
                  env_safe, sys_safe, env_prog, sys_prog)
#for i in range(n):
#    psi |= DSL.response(trig=b[i], react=f[i], owner='sys', aux='aux' + str(i+1))
#print(psi.pretty())


psi.qinit = '\A \E'
psi.moore = False
psi.plus_one = False

#ctrl=synth.synthesize(psi, ignore_sys_init=False, solver='gr1c')

strategy = omega_int.synthesize_enumerated_streett(psi)
use_cudd=False

spec=psi
aut = omega_int._grspec_to_automaton(spec)
sym.fill_blanks(aut)
bdd = omega_int._init_bdd(use_cudd)
aut.bdd = bdd
a = aut.build()
bdd.dump("file_a.pdf")

# what has been generated#
print(aut.init['env'])
print(aut.init['sys'])
print(aut.action['sys'])

print(bdd.false)
# what has been build from it
print(a.init['env'])
print(a.init['sys'])
print(a.action['sys'])

assert a.action['sys'][0] != bdd.false
t0 = time.time()
z, yij, xijk = gr1.solve_streett_game(a)
t1 = time.time()
print(t1-t0)
# unrealizable ?
if not gr1.is_realizable(z, a):
    print('WARNING: unrealizable')

t = gr1.make_streett_transducer(z, yij, xijk, a)
t2 = time.time()
(u,) = t.action['sys']
assert u != bdd.false

g = enum.action_to_steps(t, qinit=spec.qinit)
h = omega_int._strategy_to_state_annotated(g, a)
del u, yij, xijk
t3 = time.time()
print((
    'Winning set computed in {win} sec.\n'
    'Symbolic strategy computed in {sym} sec.\n'
    'Strategy enumerated in {enu} sec.').format(
    win=t1 - t0,
    sym=t2 - t1,
    enu=t3 - t2))
bdd.dump('manager.p')
bdd2 = omega_int._init_bdd(use_cudd)
_bdd.copy_vars(t.bdd,bdd2)
n1=bdd.copy(z,bdd2)