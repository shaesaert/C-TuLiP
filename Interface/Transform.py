""" Local routines
Written by S.Haesaert

CONTENT    
    helpfull functions for JPL project 
    Bridging Tulip with the Statechart autocoder
 DATE    2 June 


"""
from __future__ import absolute_import
from __future__ import print_function

import logging
from itertools import product
from itertools import product as it_product

import networkx as nx
from tulip import spec
from tulip import transys
from tulip.transys.transys import FiniteTransitionSystem

from Interface import synth2 as synth

logger = logging.getLogger(__name__)

def transform2control(trans_sys1, statevar='loc', fullmodel=False, noreach=True):
    """Transform a finite state transition system with labelled nodes to a Transition system whose nodes represent 
    the old edges. 
    Specifically the function translates TransSys1 to TransSys2: 
    TransSys1
        * Nodes =  represent locations or states, owned by environment
        * Edges = control actions by system ending in a new state

    TransSys2:
        * Nodes = Represents a move towards a specific state (owned by environment)
        * Edges = contains Arrival at state (dictated by environment) + decision to move to new state

    @param trans_sys1: FiniteTransitionSystem()
    @param statevar: string name of locations in trans_sys1
    @param fullmodel: give two models, the transformed and simplified and the full model

        """
    #  - - - - Check incoming arguments - - - - - - - -
    #   1 Check whether the given transition system is actually a transition system
    assert isinstance(trans_sys1, transys.FiniteTransitionSystem)
    from tulip.synth import _sprint_aps as print_aps

    # - - - - - Function Body - - - - - - - - - - - - -
    trans_sys2 = transys.FiniteTransitionSystem()  # Define empty transition system
    if trans_sys1.name is None:
        trans_sys2.name = "FTS*"
    else:
        trans_sys2.name = trans_sys1.name + "*"
    trans_sys2.atomic_propositions.add_from({'env_s'})
    # trans_sys2.atomic_propositions.add_from({'env_s', 'ctrl_m'})
    # tagging to who nodes in the graph belong

    try:  # state names are integers
        for s in trans_sys1.states:
            trans_sys2.states.add('%d' % s, ap={'env_s'})
            if s in trans_sys1.states.initial:
                trans_sys2.states.initial |= {'%d' % s}
    except TypeError:
        try:  # state names are strings
            for s in trans_sys1.states:
                trans_sys2.states.add('%s' % s, ap={'env_s'})
                if s in trans_sys1.states.initial:
                    trans_sys2.states.initial |= {'%s' % s}
        except Exception:
            raise logger.debug('State naming gave a failure.')

    # create nodes for the existing transitions in original FTS
    # and add transitions in the new FTS
    for (s1, s2) in trans_sys1.transitions():
        tr12 = 'm%s_%s' % (str(s1), str(s2))
        trans_sys2.states.add(tr12)
        trans_sys2.transitions.add('%s' % str(s1), tr12)
        trans_sys2.transitions.add(tr12, '%s' % str(s2))
        if s1 in trans_sys1.states.initial:
            trans_sys2.states.initial |= {tr12}

    # simplify the obtained two player game (sys= env_s; input =ctrl_m)
    for (s_state, label_) in trans_sys2.states.find(with_attr_dict={'ap': {'env_s'}}):
        if trans_sys2.states.post(trans_sys2.states.pre(s_state)) == {s_state}:
            # check whether all states with transitions that enter s_state have only transitions to s_state
            logger.info('Contracting incoming transitions of state %s ' % s_state)
            trans_sys2.states.add('m%s' % s_state)  # to replace all 'm%s_%s' states

            for node in trans_sys2.states.pre(s_state):
                # print('transition from %s to %s' % (str(trans_sys2.states.pre(node)), s_state))
                trans_sys2.transitions.add_comb(trans_sys2.states.pre(node), {'m%s' % s_state})
                if node in trans_sys2.states.initial:
                    trans_sys2.states.initial |= {'m%s' % s_state}
                trans_sys2.states.remove(node)
            # TODO : above block can be written more efficient

            trans_sys2.transitions.add('m%s' % s_state, s_state)

    # now the resulting FTS has
    # - states owned by the control system (ctrl_m)
    #    whose outgoing transitions are selected by the system in the environment
    # - states owned by the system(= environment system) (env_s)
    #    whose outgoing transitions are selected by the control system

    # ----------------------------------  Reduce  ----------------------------------
    # for reduced Transitions system create new copy (we do this to later on
    # have the option to use the original 2 play FTS)

    # This only works if the original transition were deterministic
    # We can check this as
    assert all([(len(trans_sys2.states.pre(str(s_state))) == 1) for s_state in trans_sys1.states()])

    if noreach:

        trans_red = trans_sys2.copy()
        sys_safe = list()  # list of transitions to be added to the GR(1) specification
        sys_init = list()

        for s_state in trans_sys1.states():
            logger.info('removing state :' + str(s_state))
            labels = trans_sys1.states[s_state]
            _tmp = print_aps(labels, trans_sys1.ap)

            for (tr_state1, tr_state2) in it_product(trans_red.states.pre(str(s_state)),
                                                     trans_red.states.post(str(s_state))):
                trans_red.transitions.add(tr_state1, tr_state2)
            for tr_state in trans_red.states.pre(str(s_state)):
                sys_safe += ['((' + statevar + ' = "' + tr_state + '") -> X (' + _tmp + '))']
            if s_state in trans_sys1.states.initial:
                _goto = ' || '.join(
                    ['(' + statevar + ' = "' + str(x) + '" )' for x in trans_red.states.post(str(s_state))])
                sys_init += [_tmp + ' && ' + ' ( ' + _goto + ' ) ']
            trans_red.states.remove(str(s_state))

        # Remove unneeded labels
        trans_red.ap.remove('env_s')

        # Create needed additional specifications
        # -   Environment variables and assumptions
        env_vars = list()
        env_init = list()
        env_safe = list()
        env_prog = list()  # ['(env_actions= "' + reach + '")']

        # -   System variables and requirements
        sys_vars = [x for x in trans_sys1.ap]  # we assign the labels
        #  to the control system (otherwise the GR1 synthesis will blow up the control synthesis)
        sys_prog = list()
        gr_sys = synth.sys_to_spec(trans_red, True, statevar)

        add_specs = gr_sys | spec.GRSpec(env_vars, sys_vars, env_init, sys_init,
                                         env_safe, sys_safe, env_prog, sys_prog)


    else:

        trans_red = trans_sys2.copy()
        reach = 'reach'
        stay = 'stay'
        sys_safe = list()  # list of transitions to be added to the GR(1) specification
        sys_init = list()

        trans_red.actions['env_actions'] |= {reach, stay}  # these are the action of the environment
        for s_state in trans_sys1.states():
            logger.info('removing state :' + str(s_state))
            labels = trans_sys1.states[s_state]
            _tmp = print_aps(labels, trans_sys1.ap)

            for (tr_state1, tr_state2) in it_product(trans_red.states.pre(str(s_state)),
                                                     trans_red.states.post(str(s_state))):
                trans_red.transitions.add(tr_state1, tr_state2, env_actions=reach)
            for tr_state in trans_red.states.pre(str(s_state)):
                trans_red.transitions.add(tr_state, tr_state, env_actions=stay)
                sys_safe += ['(((' + statevar + ' = "' + tr_state + '") && X ( env_actions = "' + reach + '")) -> X ('
                             + _tmp + '))']
            if s_state in trans_sys1.states.initial:
                _goto = ' || '.join(
                    ['(' + statevar + ' = "' + str(x) + '" )' for x in trans_red.states.post(str(s_state))])
                sys_init += [_tmp + ' && ' + ' ( ' + _goto + ' ) ']
            trans_red.states.remove(str(s_state))

        for x in trans_sys1.ap:
            sys_safe += ['( !' + str(x) + ' & X ( env_actions = "stay")) -> ( X !' + str(x) + ')']
            sys_safe += ['( ' + str(x) + ' & X ( env_actions = "stay")) -> ( X ' + str(x) + ')']

        # Remove unneeded labels
        trans_red.ap.remove('env_s')

        # Create needed additional specifications
        # -   Environment variables and assumptions
        env_vars = list()
        env_init = list()
        env_safe = list()
        env_prog = list()  # ['(env_actions= "' + reach + '")']

        # -   System variables and requirements
        sys_vars = [x for x in trans_sys1.ap]  # we assign the labels
        #  to the control system (otherwise the GR1 synthesis will blow up the control synthesis)
        sys_prog = list()

        add_specs = spec.GRSpec(env_vars, sys_vars, env_init, sys_init,
                                env_safe, sys_safe, env_prog, sys_prog)

    if fullmodel:
        return trans_red, add_specs, trans_sys2
    return trans_red, add_specs



def async_prod(self, ts,ap = False,relabel=True):
    """Asynchronous product TS1 x TS2 between FT Systems.

    See Also
    ========
    __or__, sync_prod, cartesian_product
    Def. 2.18, p.38 U{[BK08]
    <https://tulip-control.sourceforge.io/doc/bibliography.html#bk08>}
    """

    if not isinstance(ts, FiniteTransitionSystem):
        raise TypeError('ts must be a FiniteTransitionSystem.')

    prod_ts = transys.FiniteTransitionSystem()

    # Add all atomic propositions
    prod_ts.owner=self.owner
    prod_ts.name=self.name + '_' + ts.name
    # for parallel product: union of action sets
    prod_ts.actions['sys_actions'] |= self.actions['sys_actions'] | ts.actions['sys_actions']
    prod_ts.actions['env_actions'] |= self.actions['env_actions'] | ts.actions['env_actions']
    prod_aux = nx.product.cartesian_product(self, ts)
    state_to_i = dict((n, i) for (i, n) in enumerate(prod_aux.nodes()))

    i_to_state = dict((i,i) for (i, n) in enumerate(prod_aux.nodes()))

    for state,i in state_to_i.items():
        if ap == True:
            prod_ts.atomic_propositions |= {str(self.node[state[0]]['ap'] | ts.node[state[1]]['ap'])}
            prod_ts.add_node(i, ap={str(self.node[state[0]]['ap'] | ts.node[state[1]]['ap'])})
        else :

            prod_ts.add_node(i)
            # Assume for a moment that each of the system has atomic proposition
            for key in ts.node[state[1]].keys():
                if ('ap' == key) and (ts.node[state[1]]['ap']!= set()):
                    prod_ts.node[i]['ap_' + ts.name] = ts.node[state[1]]['ap']
                elif 'ap_' in key:
                    prod_ts.node[i][key] = ts.node[state[1]][key]

            for key in self.node[state[0]].keys():
                if ('ap' == key) and (self.node[state[0]]['ap'] != set()):
                    prod_ts.node[i]['ap_' + self.name] = self.node[state[0]]['ap']
                else:
                    prod_ts.node[i][key] = self.node[state[0]][key]


    for edge in prod_aux.edges():
        #print(edge)
        for _x, _y, label in self.transitions.find({edge[0][0]}, {edge[1][0]}):
            #print([_x, _y, label])
            prod_ts.transitions.add(state_to_i[edge[0]], state_to_i[edge[1]], **label)
        for _x, _y, label in ts.transitions.find({edge[0][1]}, {edge[1][1]}):
            #print([_x, _y, label])
            prod_ts.transitions.add(state_to_i[edge[0]], state_to_i[edge[1]], **label)

        for (initx, inity) in product(self.states.initial, ts.states.initial):
            prod_ts.states.initial |= {state_to_i[(initx, inity)]}


    return prod_ts


def fts2mealy(ts, env_name='move', reach_name='reach'):
    """ 
    Get a mealy machine with reach +  move state on all transitions 
        Parameters
        ----------
    ts :  FTS 
    env_name='move' :  label for on transitions environment action
    reach='reach' : ouput of each transition

    """
    h = transys.MealyMachine()

    mlist = list()
    for node in ts.nodes():
        mlist += [node]

    inputs = transys.machines.create_machine_ports(dict({env_name: mlist}))
    h.add_inputs(inputs)
    outputs = transys.machines.create_machine_ports(dict({reach_name: 'boolean'}))
    h.add_outputs(outputs)

    h.add_nodes_from(ts.nodes())
    for (st1, st2) in ts.transitions():
        q = {reach_name: 1, env_name: st2}
        h.transitions.add(st1, st2, **dict(q))

    for init in ts.states.initial:
        h.states.initial |= {init}

    return h



def fts2SC(ts, env_name='ctrl', act='act'):
    """ 
    Get a mealy machine with reach +  move state on all transitions 
        Parameters
        ----------
    ts :  FTS 
    env_name='move' :  label for on transitions environment action
    reach='reach' : ouput of each transition

    """
    h = transys.MealyMachine()

    mlist = list()
    for node in ts.nodes():
        mlist += [node]

    inputs = transys.machines.create_machine_ports(dict({env_name: mlist}))
    h.add_inputs(inputs)
    outputs = transys.machines.create_machine_ports(dict({act: mlist}))
    h.add_outputs(outputs)

    h.add_nodes_from(ts.nodes())
    for (st1, st2) in ts.transitions():
        q = {env_name: st2, act:st2}
        h.transitions.add(st1, st2, **dict(q))
    h.add_node('Minit')
    h.states.initial|={'Minit'}
    for init in ts.states.initial:
        q = {env_name: init, act: init}
        h.transitions.add('Minit', init, **dict(q))
    return h


def trans_complete(ts):
    """Complete FTS with selfloops for all alternative system actions
        Specifically go from a TransSys1 to TransSys2: 
        TransSys1
            * Nodes = represent locations or states, owned by environment
            * Edges = control actions by system ending in a new state


        TransSys2:
            * Nodes = Represents a move towards a specific state (owned by environment)
            * Edges = contains Arrival at state (dictated by environment) + decision to move to new state

        @param trans_sys1: FiniteTransitionSystem()
        @param statevar: string name of locations in trans_sys1


            """
    #  - - - - Check incoming arguments - - - - - - - -
    #   1 Check whether the given transition system is actually a transition system


    assert ts.owner == "env"
    ts_new = ts.copy()

    for state in ts_new.states:
        for act in ts_new.actions['sys_actions']:
            logger.info(' action %s ' % act)
            if ts_new.transitions.find(from_states=state,with_attr_dict={'sys_actions':act}) == []:
                ts_new.transitions.add(state,state,sys_actions = act)
    return ts_new