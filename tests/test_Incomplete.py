
from tulip.interfaces import omega as omega_int
import dd
# print table a of paper
from tabulate import tabulate
from tulip.transys import MealyMachine
from itertools import *
from omega.symbolic import fol as _fol
from omega.symbolic import symbolic

from tulip.interfaces import omega as omega_int
import tulip.synth as synth
import SymbolicReductions.Lift_Mealyred as comp
from SymbolicReductions.SymbolicMealy import *
import itertools
from omega.logic import bitvector
import cvxpy
from SymbolicReductions.OptimistPrune import opt_Prune
from SymbolicReductions.Bisimulation  import *
import numpy as np
import time
try:
    import omega
    from omega.logic import bitvector as bv
    from omega.games import gr1
    from omega.symbolic import symbolic as sym
    from omega.games import enumeration as enum
except ImportError:
    omega = None

def test_pulse():
    # in this test, we duplicate the case study in the paper:  Implementation of Minimizing the Number of internal States in Incomplete specified sequential NEtworks
    # By A. Grasselli and F. Luccio
    #

    # 1. Define incomplete Mealy machine

    # >> > m = MealyMachine()
    # >> > pure_signal = {'present', 'absent'}
    # >> > m.add_inputs([('tick', pure_signal)])
    # >> > m.add_outputs([('go', pure_signal), ('stop', pure_signal)])
    # >> > m.states.add_from(['red', 'green', 'yellow'])
    # >> > m.states.initial.add('red')
    # get strategy
    # initiate Mealy machine

    m = MealyMachine()
    m.add_inputs({'X': {1, 2, 3, 4, 5, 6, 7}})
    m.add_outputs({'Y': {0, 1, -1}})
    m.states.add_from(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'x'])
    d = dict()

    d['X'] = 1
    states = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    tostates = ['a', 'b', 'b', 'x', 'b', 'b', 'x', 'a']
    toout = [0, 0, 0, -1, -1, 0, -1, 1]

    for (state,to,out) in zip(states,tostates,toout):
        d['Y'] = out
        m.transitions.add(state, to, d)

    d['X'] = 2
    tostates = ['x', 'd', 'd', 'e', 'e', 'c', 'c', 'e']
    toout = [-1, 1, 1, -1, -1, -1, 1, 0]
    for (state,to,out) in zip(states,tostates,toout):
        d['Y'] = out
        m.transitions.add(state, to, d)

    d['X'] = 3
    tostates = ['d', 'a', 'a', 'x', 'a', 'x', 'x', 'd']
    toout = [0, -1, 1, -1, -1, 1, -1, 1]
    for (state, to, out) in zip(states, tostates, toout):
        d['Y'] = out
        m.transitions.add(state, to, d)

    d['X'] = 4
    tostates = ['e', 'x', 'x', 'b', 'x', 'h', 'e', 'b']
    toout = [1, -1, -1, -1, -1, 1, 1, 0]
    for (state, to, out) in zip(states, tostates, toout):
        d['Y'] = out
        m.transitions.add(state, to, d)

    d['X'] = 5
    tostates = ['b', 'a', 'x', 'b', 'b', 'f', 'x', 'b']
    toout = [0, -1, -1, 0, -1, 1, -1, -1]
    for (state, to, out) in zip(states, tostates, toout):
        d['Y'] = out
        m.transitions.add(state, to, d)

    d['X'] = 6
    tostates = ['a', 'a', 'x', 'x', 'e', 'g', 'g', 'e']
    toout = [-1, 1, -1, -1, -1, 0, 0, -1]
    for (state, to, out) in zip(states, tostates, toout):
        d['Y'] = out
        m.transitions.add(state, to, d)

    d['X'] = 7
    tostates = ['x', 'x', 'g', 'a', 'a', 'x', 'f', 'a']
    toout = [-1, -1, 0, -1, 1, -1, 0, 1]
    for (state, to, out) in zip(states, tostates, toout):
        d['Y'] = out
        m.transitions.add(state, to, d)


    header_str = ['state'] + ['X'+str(i) for i in m.inputs['X']]
    print(header_str)

    def takeinput(elem):
        return elem[2]['X']
    Next = [[]]
    Out = [[]]

    for state in states:
        atr = m.transitions.find(state)
        atr.sort(key = takeinput)
        Next += [[state]+ [el[1] if el[1] is not 'x' else '-' for el in atr]]
        Out += [[state]+ [el[2]['Y'] if el[2]['Y'] is not -1 else '-' for el in atr]]

    print(Next)
    print(tabulate(Next, headers=header_str))
    print('\n\n')
    print(tabulate(Out, headers=header_str))
    Table = dict()

    for i in range(0, 8):
        for j in range(0, 8):
            Table[frozenset({states[i], states[j]})] = {'S'}

    # 2. Compute compability classes
    # for (i,j) in product(range(0,8), range(0,8)):
    #     Table[(i, j)] = '0'
    for (i,j) in combinations(range(0,8), 2):
        i_next = m.transitions.find(states[i])
        j_next = m.transitions.find(states[j])
        i_next.sort(key=takeinput)
        j_next.sort(key=takeinput)
        cond = set()
        for x in range(0,7):
            # find conditions
            # first check outputs
            yi = i_next[x][2]['Y']
            yj = j_next[x][2]['Y']

            if yi+yj == 1:
                # => this implies the outputs are not the same
                cond = {'X'}
                break

            # no issue yet in the output

            ni = i_next[x][1] # next state for i
            nj = j_next[x][1] # next state for j

            if ni == 'x' or nj == 'x' or ni == nj:
                pass
            elif {ni,nj} == {states[i],states[j]}:
                pass
            else:
                cond|={ frozenset({ni,nj}) }
        if cond == {'X'}:
            Table[frozenset({states[i], states[j]})] = cond
        elif len(cond) == 0:
            Table[frozenset({states[i], states[j]})] = set('S')
        else:
            Table[frozenset({states[i], states[j]})] = set([frozenset({eli[0],eli[1]}) for el in cond for eli in [list(set(el))] ])
            #','.join(['('+eli[0]+','+eli[1]+')' for el in cond for eli in [list(set(el))] ])


    print(Table)

    Table_old = []
    while Table_old is not Table:
        Table_old = Table
        for pairs in Table.keys():
            for req_pairs in Table[pairs]:
                if req_pairs == 'X' or req_pairs == 'S':
                    pass
                elif Table[req_pairs] == {'X'}:
                    Table[pairs] = {'X'}

    compt_n = dict()
    for pairs in Table.keys():
        if   {'X'}.issubset(Table[pairs]):
            pass
        else:
            if len(list(set(pairs))) == 2:
                (nj,ni) = list(set(pairs))
                compt_n[nj] = compt_n.pop(nj, frozenset()) | frozenset({ni})
                compt_n[ni] = compt_n.pop(ni, frozenset()) | frozenset({nj})
    print(compt_n)
    # convert a set of frozen sets to a single string
    def frozenset_2_str(set_froz):
        str_out =[]

        for frset in set_froz:
            if frset == 'X' or frset == 'S':
                str_out += [frset]
            else:
                str_out += ['('+','.join(list(set(frset)))+')']
        return ','.join(str_out)


    # create table
    tabulate_table = [[frozenset_2_str(Table[frozenset({states[i], states[j]})]) for i in range(0,8)]for j in range(0,8)]
    print(tabulate(tabulate_table))
    #print(tabulate([[Table[frozenset({states[i], states[j]})] for i in range(0,8)]for j in range(0,8)]))

    com_classes = [ frozenset()]
    com_new = []
    # 3. Compute compatibility classes
    for ni in reversed(states) :
        # first step:
        # find classes to which you can belong
        # make set of compatible states
        com_new = []
        while len(com_classes)>0:
            class1 = com_classes.pop(0)
            # this is a set consisting of several states.
            # check compatibility
            if class1.issubset(compt_n[ni]):
                com_new += [{ni}|class1]
            elif class1.intersection(compt_n[ni]) is not set()  :
                com_new += [class1]
                int_sec = class1.intersection(compt_n[ni])
                # now check whether it is a subset of any of the remaining classes,
                # if so, we can add it later. If not we add it now.
                if any([int_sec.issubset(class2) for class2 in com_classes]) or any([(int_sec|{ni}).issubset(class2) for class2 in com_new]):
                    pass
                else:
                    com_new += [{ni} | int_sec ]
            else:
                com_new += [class1]
                com_new += [{ni}]

        print(com_new)
        com_classes = com_new
    P_imp = dict()

    def getImplied(m,class1):
        Pre = dict()
        for state in list(class1):
            atr = m.transitions.find(state)
            atr.sort(key=takeinput)
            for index in range(7):
                Pre[index] = Pre.pop(index, frozenset()) | frozenset(atr[index][1])
        P = set()
        for key in Pre.keys():
            implied_set = Pre[key] -  {'x'} # subtract for undetermined sets
            if len(implied_set) == 1:
                pass
            elif implied_set.issubset(class1):
                pass
            elif any([implied_set.issubset(sets) for sets in P]):
                pass
            else: #now we make the list but exclude sets that are subsets of us
                P = set([sets if not sets.issubset(implied_set) else None for sets in P] + [implied_set])

        return P

    for class1 in com_classes:
        #compute the class set P implied by class1
        P = set()

        P = getImplied(m,class1)

        print('P:', P)
        P_imp[frozenset(class1)] = P

        # 4. Create prime classes from maximal classes
    com_classes.sort(key=len, reverse=True)

    classestable = com_classes.copy()
    print(classestable)
    while len(classestable)>0:
        class1 = classestable.pop(0)  #  take and remove the first element of the list
        # if no implied classes then pass by, else try removing elements:
        print('----------------------\n-------', class1, '\n------------------------')
        if len(P_imp[frozenset(class1)])>0:
             for el in class1:
                subclass1 = class1 - {el}
                if any([subclass1.issubset(class2) for class2 in classestable]):
                    break
                Psub = getImplied(m, subclass1)
                print('  subclass,Psub', subclass1, Psub)
                print('   com_classes',com_classes)
                print('   com_classes implied',[ P_imp[frozenset(class2)]  for class2 in com_classes])
                if any([Psub.issuperset(P_imp[frozenset(class2)]) if subclass1.issubset(class2) else False for class2 in com_classes]):
                    print('-----BREAK for subset superset condition')
                else:
                    print('++++++++ ADD subclass:', subclass1)
                    classestable += [subclass1] # add as new class set
                    P_imp[frozenset(subclass1)] = Psub
                    com_classes += [subclass1]
                    print(classestable)



    print('PRIME compatibility classes ',  com_classes)


    # now it is time to start soving the integer program.
    # For this we first rewrite the requirements into inequalities

    # 1. all states must be covered.

    Coverstates = []
    P = []
    for state in states:
        Coverstates += [[1 if state in class1 else 0 for class1 in com_classes]]
        P += [1]
    P = np.array(P)

    cv_states = np.array(Coverstates)
    print(cv_states)
    Coverclasses = []

    # 2. for every class if used also
    # the implied classes should be subsets of other classes
    for key in com_classes:
        if len(P_imp[frozenset(key)]) > 0:
            for sets in P_imp[frozenset(key)]:

                for_class1 = np.array([[1 if sets.issubset(class1) else 0 for class1 in com_classes]])
                if for_class1[0][com_classes.index(key)] == 1:
                    break
                for_class1[0][com_classes.index(key)] = -1
                if len(Coverclasses)<1:
                    Coverclasses = for_class1
                    # init
                    P = np.concatenate((P, np.array([0])), axis=0)

                    print('init')
                else:
                    Coverclasses = np.concatenate((Coverclasses, for_class1), axis=0)
                    P = np.concatenate((P, np.array([0])), axis=0)


    print(Coverclasses)


    selection = cvxpy.Variable(len(com_classes), boolean=True)
    print('primes classes', len(com_classes))
    print('P', len(P))


    weights = np.concatenate((cv_states,Coverclasses), axis=0)
    print('weights', len(weights))
    print('P',P)
    print('weights',weights)

    constraints = weights * selection >= P

    utilities = np.array([[-1]*len(com_classes)])
    total_utility = utilities * selection
    knapsack_problem = cvxpy.Problem(cvxpy.Maximize(total_utility.T), [constraints])

    # Solving the problem
    knapsack_problem.solve(solver=cvxpy.GLPK_MI)
    print("status:", knapsack_problem.status)
    print("optimal value", knapsack_problem.value)
    print("result: primeclasses:", selection.value)
    assert True

def test_cvx_py():


    # The data for the Knapsack problem
    # P is total weight capacity of sack
    # weights and utilities are also specified
    P = 165
    weights = np.array([23, 31, 29, 44, 53, 38, 63, 85, 89, 82])
    utilities = np.array([92, 57, 49, 68, 60, 43, 67, 84, 87, 72])

    # The variable we are solving for
    selection = cvxpy.Variable(len(weights), boolean=True)

    # The sum of the weights should be less than or equal to P
    weight_constraint = weights * selection <= P

    # Our total utility is the sum of the item utilities
    total_utility = utilities * selection

    # We tell cvxpy that we want to maximize total utility
    # subject to weight_constraint. All constraints in
    # cvxpy must be passed as a list
    knapsack_problem = cvxpy.Problem(cvxpy.Maximize(total_utility), [weight_constraint])

    # Solving the problem
    knapsack_problem.solve(solver=cvxpy.GLPK_MI)

    # last step add yourself

