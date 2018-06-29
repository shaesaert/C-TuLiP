""" Implementation of sigref in python.

Algorithms based on symbolic bisimulation toolbox sigref for CUDD
Wimmer, R., Herbstritt, M., Hermanns, H., Strampp, K., & Becker, B. (2006, October).
     Sigref–a symbolic bisimulation toolbox. In International Symposium on Automated Technology f
     or Verification and Analysis (pp. 477-492). Springer, Berlin, Heidelberg.

     and based on the multi-core toolbox sigref for sylvan:
van Dijk, T., & van de Pol, J. (2016, April).
      Multi-core symbolic bisimulation minimisation.
      In International Conference on Tools and Algorithms
      for the Construction and Analysis of Systems (pp. 332-348).
      Springer, Berlin, Heidelberg.
"""

 # Algorithm  build up
from omega.symbolic import symbolic

import itertools
from omega.logic import bitvector
import dd

global count



def opt_Prune(mealy,sys_prog,lazy=False):


    #1. Compute set of goals
    # based on sys_prog = (boolean variables? or do these also include next operators?)

    bdd = mealy.bdd

    S = mealy.N_s  # state space
    T = mealy.T  # transitions relation


    # go for option 1 add variable up to width N
    signed, width = bitvector.dom_to_width((0, mealy.Nmax)) # actual domain is (0, nodenumb - 1) add one node for initial condition

    prime_n = dict()
    unprime_n = dict()

    for i in range(0, width):
        # add variables
        prime_n['_n_%d' % i] = "_n_%d'" % i
        unprime_n["_n_%d'" % i] =  '_n_%d' % i


    if lazy == True:
        eq_n = bdd.true
        equalnodes = []

        # for i in range(0, mealy.Nmax+1):
        #     n = '({var} = {value})'.format(var="n", value=i)
        #     nnext = '({var} = {value})'.format(var="n'", value=i)
        #     equalnodes += ['(' + n + '/\\' + nnext +')' ]
        for i in range(0, width):
            neqnext = bdd.add_expr('({n} <-> {nnext})'.format(n='_n_%d' % i, nnext="_n_%d'" % i))
            eq_n = bdd.apply('and',eq_n,neqnext)
        #equalnodes_str = '\\/'.join(equalnodes)

        # mealy.add_expr('f1')

        #eq_n = mealy.add_expr(equalnodes_str)

    # for el in sys_prog:
    #     goal = mealy.add_expr(el) #mealy.add_expr('f1')
    #     goals = bdd.apply('or',goals,goal) #mealy.add_expr('f1')
    # #
    #
    # goals =  mealy.add_expr('f1')

    goals =  mealy.add_expr('{var} = {value}'.format(var="_goal",value=0)) # value=mealy.vars['_goal']['dom'][-1]

    target = bdd.apply('and',goals,mealy.T) # all states get labeled with k=0

    targetv1 = mealy.exist(mealy.aux, target)

    target = bdd.quantify(targetv1,set(mealy.Y.keys())|set(mealy.X.keys())|set(mealy.N["n"]["bitnames"]), forall=False)
    T = mealy.exist(mealy.aux, mealy.T)

    mealy.T = T

    # initialize
    visited = bdd.rename(target, unprime_n)
    #print(list(mealy.pick_iter(visited, full = True, care_vars = mealy.N)))
    T_part = bdd.apply('and',target,T) # all states get labeled with k=0

    if lazy == True:
        T_part_eq_nodes = bdd.apply('and',T_part,eq_n) # self loops
        NX_self =  bdd.quantify(T_part_eq_nodes,  set(mealy.Y.keys())|set(mealy.Next["n'"]["bitnames"]), forall=False)
        NX_self_c = bdd.apply('not', NX_self)
        T_part_neq_nodes = bdd.apply('and',T_part,NX_self_c)


        T_new =  bdd.apply('or',T_part_eq_nodes,T_part_neq_nodes)
    else:
        T_new = T_part
    NX = bdd.quantify(T_part , set(mealy.Next["n'"]["bitnames"])|set(mealy.Y.keys()), forall=False)

    NX_c = bdd.apply('not', NX)
    T = bdd.apply('and', T, NX_c)  # all states get labeled with k=0

    global count
    it = 1
    target = bdd.quantify(NX, set(mealy.Y.keys()) | set(mealy.X.keys()), forall=False)
    visited = bdd.apply('or', visited, target)

    while (S is not visited) :

        # compute target

        # compute NX

        #=> only keep unprimed var... now we need a way to prime these..
        target_p = bdd.rename(target, prime_n)

        T_part = bdd.apply('and', target_p, T)  # all states get labeled with k=0
        if lazy == True:
            print("lazy")
            T_part_eq_nodes = bdd.apply('and', T_part, eq_n)  # self loops
            NX_self = bdd.quantify(T_part_eq_nodes, set(mealy.Y.keys()) | set(mealy.Next["n'"]["bitnames"]), forall=False)
            NX_self_c = bdd.apply('not', NX_self)
            T_part_neq_nodes = bdd.apply('and', T_part, NX_self_c)

            T_part_pruned = bdd.apply('or', T_part_eq_nodes, T_part_neq_nodes)


            T_new = bdd.apply('or', T_part_pruned, T_new)

        else:
            T_new = bdd.apply('or', T_part, T_new)

        NX = bdd.quantify(T_part, set(mealy.Next["n'"]["bitnames"]) | set(mealy.Y.keys()), forall=False)

        if NX == bdd.false:
            print("end via NX = false")
            break
        NX_c = bdd.apply('not', NX)
        T = bdd.apply('and', T, NX_c)  # all states get labeled with k=0
        target = bdd.quantify(NX, set(mealy.Y.keys()) | set(mealy.X.keys()) ,forall=False)

        visited = bdd.apply('or', visited, target)


        it += 1
        print('iteration = ',)
        print(it,)

        # initialize Partition
    T = bdd.apply('or', T, T_new)
    if T == mealy.T:
        print('NO TRANSITION PRUNING')

    T_test = bdd.apply('and', T, mealy.T)  # all states get labeled with k=0
    if T_test == T:
        bdd.decref(mealy.T)
        mealy.T = T
        bdd.incref(mealy.T)

        print(T)
    else:
        print("Failure")
    return mealy

    # new_count = 1
    # old_count = 0
    # while old_count < new_count:
    #     old_count = new_count
    #     visited = dict()
    #     count = -1
    #     # initialize sig
    #     Pp = bdd.rename(P, prime_n)
    #
    #     pre_sig = bdd.apply('and', Pp, mealy.T)  # sig(P(n',k) ^ T(n,a,n'))
    #
    #     sig = bdd.quantify(pre_sig, set(mealy.Next["n'"]["bitnames"]), forall=False)
    #
    #     P = refine(sig,mealy,visited)
    #     new_count = count
    #     print(("Partitions", count))
