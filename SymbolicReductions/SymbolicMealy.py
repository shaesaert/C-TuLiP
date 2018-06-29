""" Symbolic Mealy machine class and methods:
Based on first order wrapper of Omega (https://github.com/johnyf/omega)
"""


import logging
from tulip.transys import MealyMachine
try:
    from dd import cudd as _bdd
except ImportError:
    from dd import bdd as _bdd
from omega.symbolic.fol import Context
from omega.logic import syntax as stx
from omega.symbolic import symbolic
import time
import dd
import SymbolicReductions.Transform2Mealy as trMealy
from tulip.interfaces import omega as omega_int
from omega.logic import bitvector
import itertools

from omega.games import enumeration as enum

log = logging.getLogger(__name__)


class SMealy(Context):
    """ Mealy machine with set-valued expression for transitions.

    Set are expressed with bdd and a first-order interface to tje binary decision diagram is used

    """
    def __init__(self):
        """Instantiate first-order context."""
        Context.__init__(self)

        self.N = dict()  # the variable name of the state variable of the Mealy  machine
        self.Next = dict()  # the variable name of the state variable of the Mealy  machine

        self.Nmax = None # max node count (excluding initial)
        self.X = dict()  # the variable name of the inputs
        self.Y = dict()  # the variable name of the outputs
        self.YN = dict()  # the variable name of the outputs
        self.n0 = dict()   # the initial state of the Mealy machine

        self.aux = dict()  # the variable name of the inputs

        self.T = None  # BDD the node of the bdd representing the transition relation
        self.N_s = None  # BDD symbolic set of nodes
        self.N_init = None  # BDD the initial state of the Mealy machine

    def strat2mealy(self,aut,control,aux,remove_aux = True):
        t = [time.clock()]
        assert isinstance(aux,set)
        use_cudd = False # todo : implement in CUDD

        # initialize the BDD
        bdd3 = omega_int._init_bdd(use_cudd)  # create clean BDD
        bdd_node = dd.bdd.copy_vars(aut.bdd, bdd3)  # fill with vars
        self.bdd = bdd3
        vars = symbolic._prime_and_order_table(aut.vars)
        self.Y = {key: vars[key] for key in vars.keys() & control['sys']}
        self.X = {key: vars[key] for key in vars.keys() & control['env']}
        self.vars.update(self.Y)
        self.vars.update(self.X)
        self.aux = {key: vars[key] for key in vars.keys() & aux}
        self.vars.update(self.aux)

        # assert aux is owned by environment and remove
        if aux == set():
            pass
        else:
            assert set({vars[key]['owner'] == 'sys' for key in self.aux.keys()}) == {True}, set(
                {vars[key]['owner'] == 'sys' for key in self.aux.keys()})
        for a in aux:
            if a in self.Y:
                self.Y.pop(a)

        # 1. re-order the variables in the BDD unprimed to primed
        splitlevel, n1 = trMealy.strat2mealy(aut, bdd3)
        t += [time.clock()]

        # 2. Add nodes to this split level
        # (This implementation could be replaced by one similar to the one used for symbolic bisimulations -- SIGREF)

        node, width, nodenumb = trMealy.add_nodes(bdd3, n1, splitlevel)
        t += [time.clock()]
        log.debug('added nodes  symbolic Mealy in {time} sec'.format(time=t[-1]-t[-2]))

        self.Nmax = nodenumb

        # 3. Existential quantification to compute upper and lower part
        exi, entry = trMealy.exit_entry(aut, bdd3, node, width)
        trans_part = bdd3.apply('and', entry, exi)
        t += [time.clock()]
        log.debug('computed part one of transition in {time} sec'.format(time=t[-1] - t[-2]))

        # 4. add initial condition
        # initial node will be 1,1,..1,1, and should be unused
        c = ''
        self.n0 = dict({"n":int(2**width-1)})
        node_pairs = dict()
        bitnames =[]
        # create the corresponding expression
        for i in range(0, width):
            # create string of  var
            c += " _n_%d /\ " % i
            bitnames += ["_n_%d" % i]
            node_pairs["_n_%d'" % i ] = "_n_%d" % i
        init_state = bdd3.add_expr(c[:-3:])

        #   check that initial doesn't exist yet
        u = bdd3.apply('and', init_state, exi)
        assert u == bdd3.false

        #   get initial input/output
        (init_aut,) = aut.init['env']
        expr = aut.bdd.to_expr(init_aut)


        #    finally add the initial state with transition combi to the BDD
        init_trans = bdd3.add_expr(expr)
        init_aux = bdd3.apply('and', init_trans, init_state)
        init = bdd3.apply('and', init_aux, entry)
        t += [time.clock()]
        log.debug('computed part two of transition in {time} sec'.format(time=t[-1] - t[-2]))

        # filling up the rest of the information
        self.N["n"] = dict({'owner': 'sys', 'type': 'int', 'signed' :False, 'dom':(0, 2**width-1),'width' :width, 'len': 2**width, 'bitnames': bitnames})
        self.N["n"] = dict({'owner': 'sys', 'type': 'int', 'signed' :False, 'dom':(0, 2**width-1),'width' :width, 'len': 2**width, 'bitnames': bitnames})
        self.Next = symbolic._prime_and_order_table(self.N)
        self.vars.update(self.Next.copy())
        self.Next.__delitem__("n")


        trans_full = bdd3.apply('or', init, trans_part)
        t += [time.clock()]
        log.debug('computed full transition in {time} sec'.format(time=t[-1] - t[-2]))

        if remove_aux == True:
            trans = self.exist(set(self.aux), trans_full)
        else:
            trans= trans_full
        t += [time.clock()]
        log.debug('removed superfluous aux in {time} sec'.format(time=t[-1] - t[-2]))

        bdd3.incref(trans)
        bdd3.incref(init_state)
        bdd3.decref(exi)
        bdd3.decref(entry)
        bdd3.collect_garbage()

        # introduce transition set, set of states, initial state
        self.T = trans
        self.N_init = init_state



        # add state space bdd
        binary_nodes = list(itertools.product([0, 1], repeat=width))

        bitindex = 0
        bit = binary_nodes[self.Nmax - 1]
        suffix = ''
        bdd = self.bdd
        Nnodes = self.N_init  # start with initial node
        for bitindex in range(0, width):
            # assert self.bdd.false != Nnodes
            # verif_bdd = bdd.apply('and', self.T, Nnodes)
            #
            # assert self.bdd.false != verif_bdd

            if bit[bitindex] == 1:
                # create string of negated var
                prefix = " ~ _n_%d " % bitindex
                expression = suffix + prefix
                new_node_set = self.bdd.add_expr(expression)
                Nnodes = bdd.apply('or', new_node_set, Nnodes)

                suffix += " _n_%d /\ " % bitindex
            else:
                suffix += " ~ _n_%d /\ " % bitindex
                if bitindex == width - 1:
                    expression = suffix[:-3:]
                    new_node_set = self.bdd.add_expr(expression)
                    Nnodes = bdd.apply('or', new_node_set, Nnodes)

        # verif_bdd = bdd.apply('and', self.T, Nnodes)
        # <= check whether any node is removed
        # assert verif_bdd == self.T
        bdd3.incref(Nnodes)
        bdd3.collect_garbage()

        self.N_s = Nnodes

    def strat2comp(self,aut,control,aux,remove_aux = True):
        t = [time.clock()]
        assert isinstance(aux,set)
        use_cudd = False # todo : implement in CUDD

        # initialize the BDD
        bdd3 = omega_int._init_bdd(use_cudd)  # create clean BDD
        bdd_node = dd.bdd.copy_vars(aut.bdd, bdd3)  # fill with vars
        self.bdd = bdd3
        vars = symbolic._prime_and_order_table(aut.vars)
        self.Y = {key: vars[key] for key in vars.keys() & control['sys']}
        self.X = {key: vars[key] for key in vars.keys() & control['env']}
        self.vars.update(self.Y)
        self.vars.update(self.X)
        self.aux = {key: vars[key] for key in vars.keys() & aux}
        self.vars.update(self.aux)

        # assert aux is owned by environment and remove
        if aux == set():
            pass
        else:
            assert set({vars[key]['owner'] == 'sys' for key in self.aux.keys()}) == {True}, set(
                {vars[key]['owner'] == 'sys' for key in self.aux.keys()})
        for a in aux:
            if a in self.Y:
                self.Y.pop(a)

        # 1. re-order the variables in the BDD unprimed to primed
        splitlevel, n1 = trMealy.strat2mealy(aut, bdd3)
        t += [time.clock()]

        # 2. Add nodes to this split level
        # (This implementation could be replaced by one similar to the one used for symbolic bisimulations -- SIGREF)



        entry,count,new_nodes = trMealy.add_sets(self, n1, splitlevel)
        t += [time.clock()]
        log.debug('added nodesets for symbolic Mealy in {time} sec'.format(time=t[-1]-t[-2]))
        control, primed_vars = enum._split_vars_per_quantifier(
            aut.vars, aut.players)
        vars = symbolic._prime_and_order_table(aut.vars)

        unprimed = trMealy.unpack(control['sys'] | control['env'], vars)
        primed = trMealy.unpack(primed_vars['env'] | primed_vars['sys'], vars)
        unprime_vars = {stx.prime(var): var for var in unprimed}
        unprimed_in = trMealy.unpack(control['env'], vars)
        unprimed_out = trMealy.unpack(control['sys'], vars)

        self.Nmax = count+1
        for k in new_nodes:
            new = bdd3.rename(new_nodes[k], unprime_vars)
            new_nodes[k] = bdd3.apply('and', entry, new)
            new_nodes[k] = self.exist(set(self.aux), new_nodes[k])
            bdd3.incref(new_nodes[k])

        bdd3.decref(n1)

        self.bdd.collect_garbage()

        print(self.bdd.vars)


        print(self.bdd.prune())
        print(set(self.Y.keys())|set(self.X.keys()))
        minlev, maxlev = trMealy.set2levels(bdd3, set(self.Y.keys())|set(self.X.keys()))[0], trMealy.set2levels(bdd3, set(self.Y.keys())|set(self.X.keys()))[-1]
        trMealy.apply_sifting(bdd3, list(set(self.Y.keys())|set(self.X.keys())), minlev, maxlev)
        # minlev, maxlev = trMealy.set2levels(bdd3, k_set)[0], set2levels(bdd2, primed)[-1]
        # apply_sifting(bdd2, primed, minlev, maxlev)
        minlev, maxlev = trMealy.set2levels(bdd3, set(new_nodes.keys()))[0], \
                         trMealy.set2levels(bdd3, set(new_nodes.keys()))[-1]
        trMealy.apply_sifting(bdd3, list(set(new_nodes.keys())), minlev, maxlev)

        # create compatibility classes
        imp_set = bdd3.true
        c_set = set()
        k_set = set()
        c2k = dict()
        added_count =-1
        index_max = 0
        for k in range(count,-1,-1):
            print(k,)
            lev = self.bdd.add_var("c_%d" % k)
            added_count +=1
            K = dict()
            K["c_%d" % k] = dict({'owner': 'sys', 'type': 'bool', 'bitnames': ["c%d" % k]})
            c_set |= {"c_%d" % k}
            k_set |= {"k_%d" % k}
            c2k["c_%d" % k] = "k_%d" % k
            self.vars.update(K)
            levels = self.bdd._levels()
            dd.bdd._shift(self.bdd, lev, 0, levels)
            #print('compute high',imp_set, new_nodes["k_%d" % k])
            high = bdd3.apply('and', imp_set, new_nodes["k_%d" % k])
            low = imp_set
            bdd3.decref(imp_set)
            # find / add node at level i with high and with low
            imp_set = self.bdd.find_or_add(0, low, high)
            bdd3.incref(imp_set)

            t += [time.clock()]
            print('Compute {time}'.format(time=t[-1]-t[-2]),)
            print('   before sifting', len(bdd3),)
            levels = self.bdd._levels()
            minlev = 0
            maxlev = added_count
            indexing  = [ (len(levels[level]),level)  for level in levels.keys() if ((level<= maxlev) and (level != index_max))]
            sorted(indexing, reverse = True)

            # if minlev < maxlev:
            #    maxlev = min(20,added_count)
            #
            #    l = trMealy.reorder_var_bounded(bdd3, "c_%d" % k, levels, minlev, maxlev, crit=None)
            #    # sort max ten up and down
            #    minlev = max(indexing[0][-1]-10,0)
            #    maxlev = min(indexing[0][-1]+10,added_count)
            #    l = trMealy.reorder_var_bounded(bdd3,bdd3.var_at_level(indexing[0][-1]), levels, minlev, maxlev, crit=None)
            #
            # t += [time.clock()]
            # print('   after sifting', len(bdd3))
            # print('Compute {time1}, {time2}'.format(time1=t[-2]-t[-3], time2=t[-1]-t[-2]),)




        # 3. Existential quantification to compute upper and lower part
        t += [time.clock()]

        #imp_set = self.exist(set(self.aux), imp_set)
        log.debug('computed part one of transition in {time} sec'.format(time=t[-1] - t[-2]))
        comp_sets1 = self.exist(set(self.Y.keys()) | k_set,imp_set) # this should not be done for all var,
        #  only existence for uotput and state, then uniform quantification over all input var.
        # keep only c variables
        comp_sets2 = bdd3.quantify(comp_sets1, set(unprimed_in), forall=True) # this should not be done for all var,

        comp_sets = bdd3.rename(comp_sets2, c2k)
        # rename them to k
        comp_set_old = None
        t += [time.clock()]

        while (comp_set_old != comp_sets):
            comp_set_old = comp_sets
            imp_setnew = bdd3.apply('and', imp_set, comp_sets)
            print('Support compatibility set ', bdd3.support(imp_setnew))

            print('change imp_sets',imp_set,imp_setnew)
            # remove all implied sets that are impossible
            comp_sets1 = self.exist(set(self.Y.keys()) | k_set, imp_setnew)  # this should not be done for all var,
            #  only existence for uotput and state, then uniform quantification over all input var.
            # keep only c variables
            comp_sets2 = self.forall(set(self.X.keys()), comp_sets1)

            print('1',bdd3.support(comp_sets1), bdd3.support(comp_sets1).symmetric_difference(c_set))
            print('2',bdd3.support(comp_sets2), bdd3.support(comp_sets2).symmetric_difference(c_set))

            comp_sets = bdd3.rename(comp_sets2, c2k)
            print('change compsets',comp_sets,comp_sets2)




            print('compat',comp_sets,comp_set_old)
            t += [time.clock()]
            print('{time}'.format(time=t[-2] - t[-1]),)

        print('Support compatibility set ',bdd3.support(imp_set))

    def enum(self):

        # >> > m = MealyMachine()
        # >> > pure_signal = {'present', 'absent'}
        # >> > m.add_inputs([('tick', pure_signal)])
        # >> > m.add_outputs([('go', pure_signal), ('stop', pure_signal)])
        # >> > m.states.add_from(['red', 'green', 'yellow'])
        # >> > m.states.initial.add('red')
        # get strategy
        # initiate Mealy machine
        m = MealyMachine()
        m.add_inputs({x: {False,True} for x in self.X.keys()})
        m.add_outputs({y: {False,True} for y in self.Y.keys()})

        # add initial node
        m.states.add_from(['Sinit'])
        m.states.initial.add('Sinit')
        bdd = self.bdd
        env_init = self.replace(self.T, self.n0)
        self.YN=self.Y.copy()
        self.YN.update(self.Next)
        env_init2 = self.exist(self.YN, env_init)
        assert env_init2  != bdd.false
        env_iter = self.pick_iter(
            env_init2, full=True, care_vars=self.X)
        log.debug("initial choice env {env}".format(env = env_iter))
        self.N_s = bdd.false
        queue = list()
        node = 0


        for env_0 in env_iter:
            u = self.replace(env_init, env_0)
            sys_0 = self.pick(u, full=True,
                             care_vars=self.YN)
            d = dict(env_0)

            d.update({y: sys_0[y] for y in sys_0 if y in self.Y})
            n = dict({n: sys_0[n] for n in sys_0 if n in self.Next})
            n_number = n["n'"]
            # confirm `sys_0` picked properly

            u = self.replace(u, sys_0)
            assert u == bdd.true, u
            m.states.add_from([n_number])
            self._add_to_nodes(n)
            queue +=[n_number]
            m.transitions.add('Sinit', n_number, d)

        while queue:
            log.debug(('----'))
            node = queue.pop()
            from_node = dict({"n": node})
            edge_to_nodes = self.replace(self.T, from_node)

            env_act_to_node = self.exist(self.YN, edge_to_nodes)

            assert env_act_to_node != bdd.false
            env_iter = self.pick_iter(env_act_to_node, full=True, care_vars=self.X)
            for env_to_node in env_iter:
                u = self.replace(edge_to_nodes, env_to_node)
                #print(self.support(u))

                # ioanis implementation
                # prefer already visited nodes
                v = bdd.apply('and', u, self.N_s)
                if v == bdd.false:
                    log.info('cannot remain in visited nodes')
                    v = u
                    remain = False
                else:
                    remain = True
                assert v != bdd.false
                sys_values = self.pick(v, full=True, care_vars=self.YN)


                d = dict(env_to_node)
                d.update({y: sys_values[y] for y in sys_values if y in self.Y})
                n = dict({n: sys_values[n] for n in sys_values if n in self.Next})
                n_number = n["n'"]
                # confirm `sys_0` picked properly
                u = self.replace(u , sys_values)
                assert u == bdd.true, u

                if remain:
                    m.transitions.add(node, n_number, d)
                else:
                    m.states.add_from([n_number])
                    self._add_to_nodes(n)
                    queue += [n_number]
                    m.transitions.add(node, n_number, d)







        # add next transitions/= new nodes
        # pick transitions based on similarity with previous
        # otherwise pick not new node
        return m

    def _add_to_nodes(self, values):
        """Return BDD `visited` updated with assignment `values`. Adaptation from _add_to_visited in Omega/games/enumeration"""
        bdd = self.bdd
        c = list()
        for var, value in values.items():
            t = self.Next[var]['type']
            if t == 'bool':
                assert value in (True, False), value
                if bool(value):
                    c.append(var)
                else:
                    c.append('! ' + var)
                continue
            # integer
            assert t in ('int', 'saturating', 'modwrap'), t
            s = '{var} = {value}'.format(var=var, value=value)
            c.append(s)
        s = stx.conj(c)
        u = self.add_expr(s)
        self.N_s = bdd.apply('or', self.N_s, u)
