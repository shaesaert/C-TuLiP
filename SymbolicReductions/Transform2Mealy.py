
from omega.symbolic import fol as _fol
from omega.symbolic import symbolic
from omega.logic import syntax as stx
import networkx as nx
from tulip.interfaces import omega as omega_int
import tulip.synth as synth
import SymbolicReductions.Lift_Mealyred as comp
import random
import itertools
import operator


from omega.logic import bitvector

try:
    import omega
    from omega.logic import bitvector as bv
    from omega.games import gr1
    from omega.symbolic import symbolic as sym
    from omega.games import enumeration as enum
except ImportError:
    omega = None
import time
import dd


def strat2mealy(aut,bdd2,qinit='\A \E',keeporder=True):
    """Reordering of the BDD along levels"""
    t = [time.clock()]

    # isolate strategy env input -> sys input
    # & move to new BDD
    (u,) = aut.action['env']
    (v,) = aut.action['sys']

    visit = set()
    use_cudd = False
    bdd = aut.bdd


    fullstrath = bdd.apply('and', u, v)

    n1 = dd.bdd.copy_bdd(fullstrath, bdd, bdd2)
    bdd2.incref(n1)

    t += [time.clock()]
    print('combined strategies and copied BDD in {time} sec'.format(time=t[-1] - t[-2]))

    # collect groups
    control, primed_vars = enum._split_vars_per_quantifier(
        aut.vars, aut.players)
    vars = symbolic._prime_and_order_table(aut.vars)
    unprimed = unpack(control['sys'] | control['env'], vars)
    primed = unpack(primed_vars['env'] | primed_vars['sys'], vars)

    # sort on unprimed and primed groups
    strat2split(bdd2, unprimed, primed, keeporder=keeporder)
    t += [time.clock()]
    print('Sorted BDD in {time} sec'.format(time=t[-1] - t[-2]))
    if not keeporder: # keeporder is preferred!!!! It speeds up some of the later computations
        # find grouped levels and sort within those groups
        minlev, maxlev = set2levels(bdd2, unprimed)[0], set2levels(bdd2, unprimed)[-1]
        apply_sifting(bdd2, unprimed, minlev, maxlev)
        minlev, maxlev = set2levels(bdd2, primed)[0], set2levels(bdd2, primed)[-1]
        apply_sifting(bdd2, primed, minlev, maxlev)
        t += [time.clock()]

        print('Reordered BDD in {time} sec'.format(time=t[-1] - t[-2]))
    splitlevel = set2levels(bdd2, primed)[0]

    return  splitlevel,n1


def len_decision(bdd2, level):
    set_nodes = set()
    levels = bdd2._levels()

    for node in levels[level]:
        _,low,high = bdd2._succ[node]
        set_nodes |= {low,high}

    set_n = set_nodes.difference({1,-1})
    return len(set_n)


def complement(bdd3,node,newnode):
    if bdd3._succ[abs(node)][2] >0:
        print("no issue")
        return
    i, v, w = bdd3._succ[abs(node)]
    node_ = bdd3._pred.pop((i, v, w))
    # remove combination from table
    assert node == node_, (node, node_)
    # wrong fix:
    r = (i, -v, -w)
    bdd3._succ[abs(node)] = r
    assert r not in bdd3._pred, r
    bdd3._pred[r] = node


    # Todo: speed up implementation of complement

    levels = bdd3.levels()
    matches = (x for x in list(levels)[1::] if ((abs(x[2]) == node) or (abs(x[3]) == node)))
    for x in matches:
        parent_node = x[0]
        node_ = bdd3._pred.pop((x[1], x[2], x[3]))
        # remove combination from table
        if x[2] == node:
            r = (x[1], -x[2], x[3])
            bdd3._succ[abs(parent_node)] = r
            assert r not in bdd3._pred, r
            bdd3._pred[r] = parent_node
        if x[3] == node:
            r = (x[1], x[2], -x[3])
            bdd3._succ[abs(parent_node)] = r
            assert r not in bdd3._pred, r
            bdd3._pred[r] = parent_node
            complement(bdd3, parent_node,newnode)

    if abs(newnode) == abs(node):
        print("sign reference switched")
        return -newnode
    else:
        return newnode


def add_nodes(bdd,n1, splitlevel):
    # add dummy var
    level_n = bdd.add_var("_n_0")
    levels = bdd._levels()
    dd.bdd._shift(bdd, level_n, splitlevel, levels)
    # negate dummy var
    notn_node = bdd.add_expr("~ _n_0")
    notn_node = bdd.apply('and', n1, notn_node)

    # clean BDD
    bdd.incref(notn_node)
    bdd.decref(n1)
    bdd.collect_garbage()

    # shift up negate var to split level


    # count the number of nodes at split level
    levels = bdd._levels()
    nodenumb = len(levels[splitlevel])
    print('Number of nodes at splitlevel is %d' %nodenumb )

    # how many bits are needed?
    # introduce bits into bdd2
    nprev = bdd.vars['_n_0']
    nodenumb = len(levels[nprev])
    signed, width = bitvector.dom_to_width((0, nodenumb)) # actual domain is (0, nodenumb - 1) add one node for initial condition
    if width>1:
        c = ''
        for i in range(1, width):
            nprev += 1
            # add variables
            lev = bdd.add_var('_n_%d' % i)
            # shift variables up
            levels = bdd._levels()
            sizes = dd.bdd._shift(bdd, lev, nprev, levels)
            # create string of negated var
            c += "~ _n_%d /\ " % i

        # number to bit
        print(c[:-3:])
        u = bdd.add_expr(c[:-3:])
        newnode = bdd.apply('and', u, notn_node)
        bdd.decref(notn_node)
        bdd.incref(newnode)
    else:
        newnode = notn_node
    # clean to new node

    bdd.collect_garbage()


    levels = bdd._levels()

    # for each string of nodes starting at
    #  node in nodelist set node edge to bit value of the node count
    nodelist = levels[splitlevel]
    startlevel = splitlevel
    binary_nodes = list(itertools.product([0, 1], repeat=width))
    # initial node will be 1,1,..1,1, and should be unused
    visited = set() # todo: keeping visited set is safe but slows everything down
    for number, n_0 in enumerate(nodelist):
        node = n_0
        for bit_index in range(width):
            assert node not in visited, (n_0, node, visited)
            visited |= {node}
            if node is None:
                continue
            i, v, w = bdd._succ[abs(node)]
            # assert v is next node in BDD (and not the True node)
            assert (abs(v) ==1) | (abs(w) ==1)
            nextnode = abs(v*w)
            # assert you moved one level down
            assert i == startlevel + bit_index, (i, startlevel, bit_index)
            bit = binary_nodes[number][bit_index]
            if bit:
                node_ = bdd._pred.pop((i, v, w))
                # remove combination from table
                assert node == node_, (node, node_)
                r = (i, w, v)  # switch around else if to make it positive

                # add tuple
                bdd._succ[abs(node)] = r
                assert r not in bdd._pred, r
                # add node
                bdd._pred[r] = node

                if bdd._succ[abs(node)][2] < 0:
                    # fix canonicity
                    newnode = complement(bdd, abs(node), newnode)
            node = nextnode
    bdd._ite_table = dict()
    #bdd.incref(abs(newnode))
    #print("Practical number of nodes %d"  %len_decision(bdd, startlevel + width-1))
    #dd.bdd.reorder(bdd)

    return newnode, width, nodenumb


def exit_entry(aut,bdd,node,width):
    control, primed_vars = enum._split_vars_per_quantifier(
        aut.vars, aut.players)
    vars = symbolic._prime_and_order_table(aut.vars)

    unprimed = unpack(control['sys'] | control['env'], vars)
    primed = unpack(primed_vars['env'] | primed_vars['sys'], vars)

    return _exit_entry(bdd, node, width, primed, unprimed)


def _exit_entry(bdd, node, width, primed, unprimed):

    # there exists quantification
    pre_exit = bdd.quantify(node, set(unprimed), forall=False)


    pre_entry = bdd.quantify(node, set(primed), forall=False)


    bdd.incref(pre_entry)
    bdd.incref(pre_exit)
    bdd.decref(node)


    unprime_vars = {stx.prime(var): var for var in unprimed}

    #unprime_varsv2 = unprime_vars.copy()
    prime_n = dict()
    for i in range(0,width):
        bdd.add_var("_n_%d'" % i)
        assert "_n_%d" % i in bdd.vars, ("_n_%d" % i,(bdd.vars))
        # compute unprime vars with node included
        #unprime_varsv2["_n_%d'" % i] = '_n_%d' % i
        prime_n['_n_%d' % i] = "_n_%d'" % i

    # current order full bdd: vars-unprimed => nodes-unprimed => vars-primed=> nodes-primed
    # entry sub-bdd: vars-unprimed => nodes-unprimed
    # exit sub-bdd: nodes-unprimed => vars-primed

    # entry sub-bdd: vars-unprimed => nodes-unprimed to  vars-unprimed => nodes-primed
    entry = bdd.rename(pre_entry, prime_n)
    bdd.incref(entry)
    bdd.decref(pre_entry)

    # clean bdd
    bdd.collect_garbage()  # clean


    # make sure only entry and pre_exit are kept in the bdd
    # check that there is only 1 node on the first level
    dict_lev = bdd._levels()
    assert  dict_lev[0] == {abs(entry)}, (dict_lev[0],entry) # check first level. should only include node to entry



    # first reorder
    # current order full bdd: vars-unprimed => nodes-unprimed => vars-primed=> nodes-primed

    # primed levels
    levels_unprimed = set2levels(bdd, unprimed)

    for p_level in reversed(levels_unprimed):
        primed_var =  bdd._level_to_var[p_level] + "'"
        target = bdd.vars[primed_var]-1  # find unprimed var and add prime + find level primed var

        levels = bdd._levels()
        if p_level == target:
            pass
        else:
            _ = dd.bdd._shift(bdd, p_level, target, levels)


    exit_e = bdd.rename(pre_exit, unprime_vars)
    bdd.incref(exit_e)
    bdd.decref(pre_exit)
    bdd.collect_garbage()


    return exit_e,entry

def unpack(varnames, vars):
    varlist = list()
    for var in varnames:
        varlist += vars[var]['bitnames']
    return varlist

def set2levels(bdd, varnames):
    levels = list(map(lambda var: bdd.vars[var], varnames))
    return sorted(levels)


def strat2split(bdd2,unprimed, primed,keeporder=False):
    #"Re-organize BDD (no fancy reordering yet)"
    # control, primed_vars
    if keeporder is False:
        levels = bdd2._levels()
        unsorted = True
        while unsorted:
            unsorted = sortgroups(bdd2, unprimed, primed)
            bdd2.collect_garbage()

    if keeporder is True:
        levels = bdd2._levels()

        # primed levels
        levels_primed = set2levels(bdd2, primed)
        target = max(bdd2._levels().keys())

        for p_level in reversed(levels_primed):
            levels = bdd2._levels()
            if p_level == target:
                pass
            else:
                _ = dd.bdd._shift(bdd2, p_level, target, levels)
            target -= 1 # next target is plus one
        print(bdd2.vars)



def sortgroups(bdd2, gr1, gr2):
    # re-order bdd to levels in gr1 followed by levels in group2
    lev1 = set2levels(bdd2, gr1)
    lev2 = set2levels(bdd2, gr2)
    levels = bdd2._levels()
    max_level = max(bdd2._levels().keys())
    if lev2[0] > lev1[-1]:
        print('Nothing to be done')
        print(bdd2.vars)
        return False
    sizes = dd.bdd._shift(bdd2, lev2[0], max_level, levels)

    # compute minimum between lev1[-1] and max_level
    size_min = sizes[lev1[-1]]
    lev_min = lev1[-1]
    for le in range(lev1[-1], max_level + 1):
        if size_min > sizes[le]:
            size_min = sizes[le]
            lev_min = le
    dd.bdd._shift(bdd2, max_level, lev_min, levels)

    return True




def apply_sifting(bdd, names, minlev, maxlev, crit=None):
    """Apply Rudell's sifting algorithm but now in groups.
     (copied from dd/bdd package of ioannis)"""
    bdd.collect_garbage()
    n = len(bdd)
    random.shuffle(names)
    # using `set` injects some randomness
    levels = bdd._levels()
    for var in names:
        k = reorder_var_bounded(bdd, var, levels, minlev, maxlev, crit=crit)
        m = len(bdd)

    assert m <= n, (m, n)


def reorder_var_bounded(bdd, var, levels, minlev, maxlev, crit=None):
    """Reorder by sifting a variable `var` (copied from dd/bdd package).
     (copied from dd/bdd package of ioannis)

    @type bdd: `BDD`
    @type var: `str`
    """
    assert var in bdd.vars, (var, bdd.vars)
    m = len(bdd)
    n = len(bdd.vars) - 1
    assert n >= 0, n
    start = minlev
    end = maxlev
    level = bdd.level_of_var(var)
    # closer to top ?
    if (2 * (level - start)) >= (end - start):
        start, end = end, start
    dd.bdd._shift(bdd, level, start, levels)
    sizes = dd.bdd._shift(bdd, start, end, levels)
    k = min(sizes, key=sizes.get)
    shift(bdd, end, k, levels, crit=crit)
    m_ = len(bdd)
    assert sizes[k] == m_, (sizes[k], m_)
    assert m_ <= m, (m_, m)
    return k


def shift(bdd, start, end, levels, crit=None):
    """Shift level `start` to become `end`, by swapping.
    copied from Ioannis
    @type bdd: `BDD`
    @type start, end: `0 <= int < len(bdd.vars)`
    """
    m = len(bdd.vars)
    assert 0 <= start < m, (start, m)
    assert 0 <= end < m, (end, m)
    sizes = dict()
    d = 1 if start < end else -1
    for i in range(start, end, d):
        if crit is not None:
            sizes[i] = len(bdd._levels()[crit])
        j = i + d
        oldn, n = bdd.swap(i, j, levels)
        sizes[i] = oldn
        sizes[j] = n
        if crit is not None:
            sizes[j] = len(bdd._levels()[crit])

    return sizes


