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



def Bisim(mealy):
    bdd = mealy.bdd

    S = mealy.N_s  # state space
    T = mealy.T  # transitions relation

    # to be created
    P = None # partition bdd (i.e. nodenum)
    # P(n,k) k = partition number

    sig = None  # signature bdd (i.e. nodenum)
    # sig(s,a,k) = 1 if (a,B_k) in sig(s)


    # option 1 : add vars up to width of N
    # option 2 : reuse Nprime => this


    signed, width = bitvector.dom_to_width((0, mealy.Nmax)) # actual domain is (0, nodenumb - 1) add one node for initial condition
    binary_nodes = list(itertools.product([0, 1], repeat=width))


    # go for option 1 add variable up to width N
    bitnames = []
    prime_n = dict()
    for i in range(0, width):
        # add variables
        lev = bdd.add_var('_k_%d' % i)
        bitnames += ["_k_%d" % i]
        prime_n['_n_%d' % i] = "_n_%d'" % i

    K = dict()
    K["k"] = dict({'owner': 'sys', 'type': 'int', 'signed': False,
                   'dom': (0, 2**width-1),'width': width, 'len': 2**width, 'bitnames': bitnames})
    # Knext = symbolic._prime_and_order_table(K)
    # print(Knext)
    mealy.vars.update(K)

    global count

    # initialize Partition

    k_0 = mealy.add_expr('{var} = {value}'.format(var="k", value=0))

    P = bdd.apply('and',k_0,mealy.N_s) # all states get labeled with k=0
    new_count =1
    old_count = 0
    while old_count < new_count:
        old_count = new_count
        visited = dict()
        count = -1
        # initialize sig
        Pp = bdd.rename(P, prime_n)

        pre_sig = bdd.apply('and', Pp, mealy.T)  # sig(P(n',k) ^ T(n,a,n'))

        sig = bdd.quantify(pre_sig, set(mealy.Next["n'"]["bitnames"]), forall=False)

        P = refine(sig,mealy,visited)
        new_count = count
        print(("Partitions", count))


def refine(sig, mealy,visited):
    # visited  = table of visited nodes
    # count = count for next node
    if sig in visited:
        return  visited[sig]
    if abs(sig) == 1:
        return sig


    # which var
    i, _, _ = mealy.bdd._succ[abs(sig)]
    ni = mealy.bdd.var_at_level(i)

    if ni in set(mealy.vars["n"]["bitnames"]): # var = n then
        # still in level of the nodes levels

        ni_high = mealy.bdd.cofactor(sig, {ni:1}) # this could be positive or negative
        ni_low = mealy.bdd.cofactor(sig, {ni:0})

        high = refine(ni_high, mealy, visited)
        low = refine(ni_low, mealy, visited)

        #find / add node at level i with high and with low
        result = mealy.bdd.find_or_add(i, low, high)
    else:
        result = newcount_k(mealy)
    visited[sig] = result

    return result


def newcount_k(mealy):
    global count
    count += 1

    k_0 = mealy.add_expr('{var} = {value}'.format(var="k", value=count))

    return k_0
