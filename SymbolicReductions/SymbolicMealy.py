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
        # assert aux is owned by environment
        if aux == set():
            pass
        else:
            assert set({vars[key]['owner'] == 'sys' for key in self.aux.keys()}) == {True}, set(
                {vars[key]['owner'] == 'sys' for key in self.aux.keys()})


        for a in aux:
            if a in self.Y:
                self.Y.pop(a)


        splitlevel, n1 = trMealy.strat2mealy(aut, bdd3)
        t += [time.clock()]
        #print('initialised symbolic Mealy in {time} sec'.format(time=t[-1]-t[-2]))

        node, width, nodenumb = trMealy.add_nodes(bdd3, n1, splitlevel)
        t += [time.clock()]
        print('added nodes  symbolic Mealy in {time} sec'.format(time=t[-1]-t[-2]))
        self.Nmax = nodenumb


        exi, entry = trMealy.exit_entry(aut, bdd3, node, width)
        trans_part = bdd3.apply('and', entry, exi)
        t += [time.clock()]
        print('computed part one of transition in {time} sec'.format(time=t[-1] - t[-2]))

        ## add initial condition
        # initial node will be 1,1,..1,1, and should be unused
        c = ''
        self.n0 = dict({"n":int(2**width-1)})

        node_pairs = dict()
        bitnames =[]
        for i in range(0, width):
            # create string of  var
            c += " _n_%d /\ " % i
            bitnames += ["_n_%d" % i]
            node_pairs["_n_%d'" % i ] = "_n_%d" % i
        init_state = bdd3.add_expr(c[:-3:])

        # check that initial doesn't exist yet
        u = bdd3.apply('and', init_state, exi)
        assert u == bdd3.false

        # get initial input/output
        (init_aut,) = aut.init['env']
        expr = aut.bdd.to_expr(init_aut)


        #init_trans = dd.bdd.copy_bdd(init_aut, aut.bdd, bdd3)
        init_trans = bdd3.add_expr(expr)
        init_aux = bdd3.apply('and', init_trans, init_state)
        init = bdd3.apply('and', init_aux, entry)
        t += [time.clock()]
        print('computed part two of transition in {time} sec'.format(time=t[-1] - t[-2]))

        self.N["n"] = dict({'owner': 'sys', 'type': 'int', 'signed' :False, 'dom':(0, 2**width-1),'width' :width, 'len': 2**width, 'bitnames': bitnames})
        self.Next = symbolic._prime_and_order_table(self.N)
        self.vars.update(self.Next.copy())
        self.Next.__delitem__("n")





        trans_full = bdd3.apply('or', init, trans_part)
        t += [time.clock()]
        print('computed full transition in {time} sec'.format(time=t[-1] - t[-2]))

        if remove_aux == True:
            trans = self.exist(set(self.aux), trans_full)
        else:
            trans= trans_full
        t += [time.clock()]
        print('removed superfluous aux in {time} sec'.format(time=t[-1] - t[-2]))
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
