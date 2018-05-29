""" Tulip to ULM chart: Lift
CREDIT

    Scott1. Piterman, Nir et al.: Synthesis of Reactive(1) Designs. 2006
"""

from __future__ import print_function
import Interface.Statechart as dumpsmach

from itertools import combinations, cycle


from Interface.Reduce import *
import time
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


def lift_spec(n):
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
        sys_safe |= {f[i] + ' -> ' + 'X (' + f[i] + f_down + f_up + ')'}

    # the lift should not move up unless some button is pressed
    # equivalent to, if u are moving up, then a button should be on

    sys_vars |= {'bon'}  # some button is on (AUX)
    sys_vars |= {'fup'}  # moving up         (AUX)
    sys_init |= {'f1'}
    # \/i (f_i && f_i+1)
    # print(' || '.join([' ( ' + f[i] + ' ) ' for i in range(n)]))
    sys_safe |= {' || '.join([' ( ' + f[i] + ' ) ' for i in range(n)])}

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
    #print(psi.pretty())

    psi.qinit = '\A \E'
    psi.moore = False
    psi.plus_one = False
    return psi,f


def test_timing(range_floors, reduce=False):
    times = []
    nodes = []
    for n in range_floors:
        t =[]
        nodes_n =[]
        t0 = time.clock()

        # define boolean variables for the buttons & the floors


        t += [time.clock()-t0]
        psi,f = lift_spec(n)
        ctrl = synth.synthesize(psi, ignore_sys_init=False, solver='omega')

        t += [time.clock()-t0]
        # found a controller
        print('controller found, time = %d' %t[1])
        # ctrl_s = synth.determinize_machine_init(ctrl)
        Events_init = set(map(lambda fl: ('b%d'%fl , False), range(1,n+1)))
        #Events_init = {('b1', False), ('b2', False)}
        nodes_n += [len(ctrl.nodes())]
        if reduce:
            ctrl_red = reduce_mealy(ctrl, relabel=True, outputs=set(f),
                                    prune_set=Events_init, combine_trans=False)
            t += [time.clock()-t0]
            nodes_n += [len(ctrl_red.nodes())]
        times += [t]
        nodes += [nodes_n]

    return times, nodes


def test_gr1_timing(range_floors):
    times = []
    for n in range_floors:
        t =[]
        nodes_n =[]
        t0 = time.clock()

        # define boolean variables for the buttons & the floors


        t += [time.clock()-t0]
        psi,f = lift_spec(n)
    # ctrl=synth.synthesize(psi, ignore_sys_init=False, solver='gr1c')

        #strategy = omega_int.synthesize_enumerated_streett(psi)
        use_cudd = False

        spec = psi
        aut = omega_int._grspec_to_automaton(spec)

        sym.fill_blanks(aut)
        bdd = omega_int._init_bdd(use_cudd)
        aut.bdd = bdd
        a = aut.build()
        #
        # # what has been generated#
        # print(aut.init['env'])
        # print(aut.init['sys'])
        # print(aut.action['sys'])
        #
        # print(bdd.false)
        # # what has been build from it
        # print(a.init['env'])
        # print(a.init['sys'])
        # print(a.action['sys'])

        assert a.action['sys'][0] != bdd.false
        t0 = time.time()
        z, yij, xijk = gr1.solve_streett_game(a)
        t1 = time.time()
        #print(t1 - t0)
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

        times += [t1 - t0, t2 - t1, t3 - t2]
    return times



def test_gr1_enumerate(range_floors):
    times = []
    for n in range_floors:
        t =[]
        nodes_n =[]
        t0 = time.clock()

        # define boolean variables for the buttons & the floors


        t += [time.clock()-t0]
        psi,f = lift_spec(n)
        #strategy = omega_int.synthesize_enumerated_streett(psi)
        use_cudd = False

        spec = psi
        aut = omega_int._grspec_to_automaton(spec)

        sym.fill_blanks(aut)
        bdd = omega_int._init_bdd(use_cudd)
        aut.bdd = bdd
        a = aut.build()
        #
        # # what has been generated#
        # print(aut.init['env'])
        # print(aut.init['sys'])
        # print(aut.action['sys'])
        #
        # print(bdd.false)
        # # what has been build from it
        # print(a.init['env'])
        # print(a.init['sys'])
        # print(a.action['sys'])

        assert a.action['sys'][0] != bdd.false
        t0 = time.time()
        z, yij, xijk = gr1.solve_streett_game(a)
        t1 = time.time()
        #print(t1 - t0)
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



        ctrl = synth.strategy2mealy(h, spec)

        ctrl.remove_deadends()
        t4 = time.time()


        times += [t1 - t0, t2 - t1, t3 - t2, t4 - t3]
    return times

def test_shape(val =1):
    times = []
    t =[]
    nodes_n =[]
    t0 = time.clock()

    # define boolean variables for the buttons & the floors


    t += [time.clock()-t0]
    psi,f = lift_spec(n)
    #strategy = omega_int.synthesize_enumerated_streett(psi)
    use_cudd = False

    spec = psi
    aut = omega_int._grspec_to_automaton(spec)

    sym.fill_blanks(aut)
    bdd = omega_int._init_bdd(use_cudd)
    aut.bdd = bdd
    a = aut.build()
    #
    # # what has been generated#
    # print(aut.init['env'])
    # print(aut.init['sys'])
    # print(aut.action['sys'])
    #
    # print(bdd.false)
    # # what has been build from it
    # print(a.init['env'])
    # print(a.init['sys'])
    # print(a.action['sys'])

    assert a.action['sys'][0] != bdd.false
    t0 = time.time()
    z, yij, xijk = gr1.solve_streett_game(a)
    t1 = time.time()

    #print(t1 - t0)
    # unrealizable ?
    if not gr1.is_realizable(z, a):
        print('WARNING: unrealizable')

    t = gr1.make_streett_transducer(z, yij, xijk, a)
    t2 = time.time()
    (u,) = t.action['sys']
    assert u != bdd.false
    if val == 1:
        return t

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



    ctrl = synth.strategy2mealy(h, spec)

    ctrl.remove_deadends()
    t4 = time.time()


    times += [t1 - t0, t2 - t1, t3 - t2, t4 - t3]
    return times

def print_nodes(g):

    for node_n, d in g.nodes(data=True):
        c ="node %s = " %node_n.__str__()

        for var, value in d.items():
            if bool(value):
                c += var + ' '
            else:
                c +='! ' + var + ' '

        print(c)

def nodes_table(g):
    c = ' &'
    for key in g.nodes(data=True)[0][1].keys():
        c += key + ' &'
    print(c + '\\\\')
    for node_n, d in g.nodes(data=True):
        c ="node %s  " %node_n.__str__()

        for var, value in d.items():
            if bool(value):
                c += '& 1 '
            else:
                c +='& 0 '

        print(c + '\\\\')