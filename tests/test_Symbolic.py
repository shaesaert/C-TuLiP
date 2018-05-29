
from tulip.interfaces import omega as omega_int
import dd
from omega.symbolic import fol as _fol
from omega.symbolic import symbolic

from tulip.interfaces import omega as omega_int
import tulip.synth as synth
import SymbolicReductions.Lift_Mealyred as comp
from SymbolicReductions.SymbolicMealy import *
import itertools
from omega.logic import bitvector


from SymbolicReductions.Bisimulation  import *
import time
try:
    import omega
    from omega.logic import bitvector as bv
    from omega.games import gr1
    from omega.symbolic import symbolic as sym
    from omega.games import enumeration as enum
except ImportError:
    omega = None

def test_add_nodes(n=10):


    # create transition relation
    # x =1 2 3 4 5
    # y = 1 2 3 4 5

    # x=1 -> y=1
    from dd import autoref as _bdd
    unprimed = []
    primed = []
    bdd = omega_int._init_bdd(False)  # create clean BDD
    newnode = 0
    for i in range(n):
        bdd.add_var("x_%d" % i)
        bdd.add_var("x_%d'" % i)
        unprimed += ["x_%d" % i]
        primed += ["x_%d'" % i]
    for x in range(n):
        uprime = "x_%d /\ " % x
        prime = "x_%d' /\ " % x
        for y in range(n):
            if x != y:
                uprime += "~ x_%d /\ " % y
                prime += "~ x_%d' /\ " % y
        if x != 0:
            u = bdd.add_expr('(' + uprime[:-3:] + ') /\ ' + '(' + prime[:-3:] + ')')
            newnode = bdd.apply('or', u, newnode)
        else:
            print('(' + uprime[:-3:] + ') /\ ' + '(' + prime[:-3:] + ')')
            newnode = bdd.add_expr('(' + uprime[:-3:] + ') /\ ' + '(' + prime[:-3:] + ')')

    bdd.incref(newnode)
    bdd.collect_garbage()
    import SymbolicReductions.Transform2Mealy as trMealy
    use_cudd = False
    bdd2 = omega_int._init_bdd(use_cudd)  # create clean BDD
    bdd_node = dd.bdd.copy_vars(bdd, bdd2)  # fill with vars
    n1 = dd.bdd.copy_bdd(newnode, bdd, bdd2)
    bdd2.incref(n1)

    trMealy.strat2split(bdd2, unprimed, primed)

    minlev, maxlev = trMealy.set2levels(bdd2, unprimed)[0], trMealy.set2levels(bdd2, unprimed)[-1]
    trMealy.apply_sifting(bdd2, unprimed, minlev, maxlev, crit=None)
    minlev, maxlev = trMealy.set2levels(bdd2, primed)[0], trMealy.set2levels(bdd2, primed)[-1]
    splitlevel = trMealy.set2levels(bdd2, primed)[0]
    trMealy.apply_sifting(bdd2, primed, minlev, maxlev, crit=None)
    levels = bdd2._levels()

    node, width, nodenumb = trMealy.add_nodes(bdd2, n1, splitlevel)
    len(bdd2)
    exit, entry = trMealy._exit_entry(bdd2, node, width, primed, unprimed)
    trans = bdd2.apply('and', entry, exit)
    bdd2.incref(trans)
    bdd2.collect_garbage()

    trans_nodes = bdd2.quantify(trans, set(unprimed), forall=False)


    table = dict()
    for i in range(width):
        # table["_n_%d'" % i] = {'owner': 'sys', 'type': 'bool'}
        table["_n_%d" % i] = {'owner': 'sys', 'type': 'bool'}

    fol = _fol.Context()
    fol.vars = symbolic._prime_and_order_table(table)

    # Context
    """First-order interface to a binary decision diagram.

        All operations assume that integer-valued variables
        take only values that correspond to the Boolean-valued
        variables that refine them.

        Quantification is implicitly bounded.
        In the future, the bound will be made explicit
        in the syntax.
        """
    fol.bdd = bdd2

    for sol in fol.pick_iter(trans_nodes, full=True, care_vars=bdd2.support(trans_nodes)):
        for i in range(width):

            assert sol['_n_%d' %i] ==sol["_n_%d'" %i]


def test_elevator(n=4):
    t = [time.clock()]

    # define boolean variables for the buttons & the floors

    psi, f = comp.lift_spec(n)
    # strategy = omega_int.synthesize_enumerated_streett(psi)
    use_cudd = False

    spec = psi
    aut = omega_int._grspec_to_automaton(spec)

    sym.fill_blanks(aut)
    bdd = omega_int._init_bdd(use_cudd)
    aut.bdd = bdd
    a = aut.build()


    assert a.action['sys'][0] != bdd.false

    z, yij, xijk = gr1.solve_streett_game(a)
    # solved game

    if not gr1.is_realizable(z, a):
        print('WARNING: unrealizable')
    control, primed_vars = enum._split_vars_per_quantifier(
        aut.vars, aut.players)
    print("aut_control")
    aut.control = control
    t += [time.clock()]
    aut = gr1.make_streett_transducer(z, yij, xijk, a)
    t += [time.clock()]
    print('made symbolic strategy in {time} sec'.format(time=t[-1]-t[0]))

    mealy = SMealy()
    mealy.strat2mealy(aut,control, {'bon', '_goal', "fup"})
    t += [time.clock()]
    print('made symbolic Mealy in {time} sec'.format(time=t[-1]-t[-2]))

    print(mealy.bdd.prune())
    Bisim(mealy)
    t += [time.clock()]
    print('made pruned and bisimulated Mealy in {time} sec'.format(time=t[-1]-t[-2]))

    assert abs(mealy.T) != 1
    m = mealy.enum()
    t += [time.clock()]
    print('made enumerated Mealy in {time} sec'.format(time=t[-1]-t[-2]))

    print(len(m))
    print(len(m.edges(data=True)))
    assert True


def test_bisim(n=4):
    t = [time.clock()]

    # define boolean variables for the buttons & the floors

    psi, f = comp.lift_spec(n)
    # strategy = omega_int.synthesize_enumerated_streett(psi)
    use_cudd = False

    spec = psi
    aut = omega_int._grspec_to_automaton(spec)

    sym.fill_blanks(aut)
    bdd = omega_int._init_bdd(use_cudd)
    aut.bdd = bdd
    a = aut.build()


    assert a.action['sys'][0] != bdd.false

    z, yij, xijk = gr1.solve_streett_game(a)
    # solved game

    if not gr1.is_realizable(z, a):
        print('WARNING: unrealizable')
    control, primed_vars = enum._split_vars_per_quantifier(
        aut.vars, aut.players)
    print("aut_control")
    aut.control = control
    t += [time.clock()]
    aut = gr1.make_streett_transducer(z, yij, xijk, a)
    t += [time.clock()]
    print('made symbolic strategy in {time} sec'.format(time=t[-1]-t[0]))

    mealy = SMealy()
    mealy.strat2mealy(aut,control, {'bon', '_goal', "fup"})
    t += [time.clock()]
    print('made symbolic Mealy in {time} sec'.format(time=t[-1]-t[-2]))

    print(mealy.bdd.prune())

    print(mealy.Nmax)
    print(mealy.N_s)

    Bisim(mealy)
