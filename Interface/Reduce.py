""" Local routines
Written by S.Haesaert

CONTENT    
    helpfull functions for JPL project 
    Bridging Tulip with the Statechart autocoder
 DATE    2 June 


"""
# TODO : Check whether output set of reduced mealy machines (i,e.,ctrl.outputs) is too big?

from __future__ import absolute_import
from __future__ import print_function

import logging
from itertools import product as it_product

from networkx.algorithms.minors import equivalence_classes
from tulip import transys

from Interface import synth2 as synth

logger = logging.getLogger(__name__)

def remove_aux_inputs(ctrl, inputs):

    #1. check whether you are allowed to remove the aux inputs. <= not done
    #2. remove aux. inputs.

    ctrl_new = transys.MealyMachine()
    ctrl_new.add_outputs(ctrl.outputs)

    # this needs to be changed to be a limited set
    inputs_dict = dict()
    for i in inputs:
        inputs_dict[i] = ctrl.inputs[i]
    ctrl_new.add_inputs(inputs_dict)

    # add nodes from original mealy
    ctrl_new.add_nodes_from(ctrl.nodes())
    block_pairs = it_product(ctrl, ctrl)
    for (b, c) in block_pairs:
        labels = {frozenset([(key, label[key]) for key in ctrl_new.inputs.keys()]
                            + [(output, label[output]) for output in ctrl_new.outputs.keys()])
                  for (x, y, label) in ctrl.transitions.find(b, c)}
        for q in labels:
            ctrl_new.transitions.add(b, c, **dict(q))

    ctrl_new.states.initial.add_from(ctrl.states.initial)

    return ctrl_new

def reduce_mealy(ctrl, outputs={'ctrl'}, relabel=False, prune_set=None,
                 full=True, combine_trans=True, verbose=True):
    """ reduce mealy machines by computing the quotient system of the maximal equivalence class
    Parameters
    ----------
    ctrl:  mealy machine
    outputs :  Tells which outputs are critical and should be kept. Given as a set of strings.
    relabel :  True/False = Relabels nodes (especially needed when ctrl comes with hash like names)
    prune_init :  if set => try 'prune' => remove all transitions that do not belong to the set of allowed initialisations
                    Else determinize

    """

    assert isinstance(prune_set, set) or prune_set is None, 'prune_set is not a set'

    ctrl_s = prune_init(ctrl, init_event=prune_set)
    if verbose: print('Original number of states = ' + str(len(ctrl)) + '\n'
                      + '    number of transitions = ' + str(len(ctrl.transitions.find())))
    it_beh = True
    len_last = len(ctrl_s)
    while it_beh:

        equiv_classes = equiv_alpha(ctrl_s, outputs)

        if verbose: print('Start iterating for maximally coarse bisimulation')
        it = True
        # now you should iterate for maximally coarse
        while it:
            if verbose: print('Number of states = ' + str(len(equiv_classes)))
            equiv_classes_new = iterate_equiv(equiv_classes, ctrl_s, outputs=outputs)
            it = (len(equiv_classes_new) != len(equiv_classes))
            equiv_classes = equiv_classes_new

        if verbose: print('Found equivalence classes')

        # now compute quotient system
        equiv_dict = dict(sum([list(it_product(block, {i})) for (i, block) in enumerate(equiv_classes)], []))
        node_rel = lambda u, v: equiv_dict[u] == equiv_dict[v]  # the initial relation
        ctrl_s = quotient_mealy(ctrl_s, node_relation=node_rel, relabel=relabel, outputs=outputs)

        if full:
            equiv_classes = reduce_guar_beh(ctrl_s, outputs=outputs)
            equiv_dict = dict(sum([list(it_product(block, {i})) for (i, block) in enumerate(equiv_classes)], []))
            node_rel = lambda u, v: equiv_dict[u] == equiv_dict[v]  # the initial relation => groups of nodes that can
            # have equal next nodes
            ctrl_s = quotient_mealy(ctrl_s, node_relation=node_rel, relabel=relabel, outputs=outputs)

            if verbose: print('Behavioural equivalence reductions \n' +
                              '-  number of states = ' + str(len(ctrl_s)) + '\n'
                              + '-  number of transitions = ' + str(len(ctrl_s.transitions.find())))

        it_beh = ((len(ctrl_s) != len_last) and full)
        len_last = len(ctrl_s)

    if combine_trans:
        ctrl_s = combine_transitions(ctrl_s)
        if verbose: print('Combine transitions \n' +
                          '-  number of states = ' + str(len(ctrl_s)) + '\n'
                          + '-  number of transitions = ' + str(len(ctrl_s.transitions.find())))

    return ctrl_s



def reduce_guar_beh(ctrl,outputs={'loc'}):
    ctrl_n=ctrl.copy()
    """ 
        compute equivalence classes.
            Parameters
            ----------
        ctrl :  mealy machine
        outputs :  Tells which outputs are critical and should be kept. Given as a set of strings.

        Code is adapted from networkx.algorithms.minors.equivalenceclasses by Jeffry Finkelstein.

        """
    # 1. Find R_0 =  equivalence class of elements with the same labels on their outgoing transitions.

    blocks = []
    # Determine the equivalence class for each element of the iterable.
    # TODO Order first :
    # => Dont go directly over ctrl.states(), first order them on the number of transitions they have.
    stat_len = [(y, len(ctrl_n.transitions.find(y))) for y in ctrl_n.states()]
    sorted_nodes = sorted(stat_len, key=lambda stat_len: -stat_len[1])
    for (y,_t) in sorted_nodes:
        # Each element y must be in *exactly one* equivalence class.
        #
        # Each block is guaranteed to be non-empty
        if y == 'Sinit': # the initial state gets its own block
            blocks.append([y])
            continue

        for block in blocks:
            x = next(iter(block))

            if len(ctrl[x]) < len(ctrl[y]):
                #print('unequal number')
                continue
            if x == 'Sinit':  # the initial state gets its own block
                continue

            # compute set of labels:
            labels_x = {frozenset([(key, label[key]) for key in ctrl_n.inputs.keys()]
                                  + [(output, label[output]) for output in outputs]+[('node',_y)])
                        for (_x, _y, label) in ctrl_n.transitions.find({x})}
            labels_y = {frozenset([(key, label[key]) for key in ctrl_n.inputs.keys()]
                                  + [(output, label[output]) for output in outputs]+[('node',_y)])
                        for (_x, _y, label) in ctrl_n.transitions.find({y})}

            if labels_y <= labels_x:
                block.append(y)
                break

            labelin_x = {frozenset([(key, label[key]) for key in ctrl_n.inputs.keys()])
                        for (_x, _y, label) in ctrl_n.transitions.find({x})}
            labelin_y = {frozenset([(key, label[key]) for key in ctrl_n.inputs.keys()])
                        for (_x, _y, label) in ctrl_n.transitions.find({y})}



            if len(labels_y | labels_x) == len(labelin_y | labelin_x):
                block.append(y) #TODO (THIS is WRONG, the labels are now no longer correct!!!
                # after adding a new state to a block, the first state of the block needs to get
                # additional outgoing transitions)
                # you need to also immediatly add the additional outgoing transition. Otherwise you are creating errors )
                # find the missing input labels
                for label in labels_y.difference(labels_x):
                    ldict=dict(label)
                    ctrl_n.transitions.add(x, ldict.pop('node'), **ldict)
                    ctrl_n.transitions.find(x, **ldict)

                # labels = {frozenset([(key, label[key]) for key in mealy.inputs.keys()]
                #                     + [(output, label[output]) for output in outputs])
                #           for (x, y, label) in mealy.transitions.find(b, c)}
                # for q in labels:
                #     q_mealy.transitions.add(mapping[b], mapping[c], **dict(q))
                break
        else:
            # If the element y is not part of any known equivalence class, it
            # must be in its own, so we create a new singleton equivalence
            # class for it.
            blocks.append([y])
    return {frozenset(block) for block in blocks}



def combine_transitions(ctrl):
    """ Combine parallell transitions when they are independent of environment actions
    Parameters
    ----------
        ctrl:  mealy machine

    """
    ctrl_copy = ctrl.copy()

    for c_state in ctrl_copy.nodes():
        for post_s in ctrl_copy.states.post(c_state):
            logger.info('(' + str(c_state) + ')' + '(' + str(post_s) + ')')
            labels = [set(label.items()) for (x, y, label) in ctrl_copy.transitions.find({c_state}, {post_s})]
            min_set = set.intersection(*labels)
            labels_mins = [lab - min_set for lab in labels]
            if set.union(*labels_mins) == set():
                continue

            list_in = [set(it_product({key}, values)) for (key, values) in ctrl_copy.inputs.items()
                       if (not values == {0, 1}) & (set(it_product({key}, values)) <= set.union(*labels_mins))] + [
                          set(it_product({key}, {True, False})) for (key, values) in ctrl_copy.inputs.items()
                          if ((values == {0, 1}) & (set(it_product({key}, values)) <= set.union(*labels_mins)))]

            labels_updated = labels.copy()
            for list_el in list_in:
                for label in labels_updated:
                    label_gen = [(label - list_el) | {el_set} for el_set in list_el]
                    if all([any([label_gen_el == labels_el for labels_el in labels_updated]) for label_gen_el in
                            label_gen]):
                        labels_updated = set(frozenset(labels_el) for labels_el in labels_updated if
                                             not any([label_gen_el == labels_el for label_gen_el in label_gen]))
                        labels_updated |= {frozenset((label - list_el))}
            ctrl_copy.transitions.remove_from(ctrl_copy.transitions.find({c_state}, {post_s}))
            for labels_updated_el in labels_updated:
                ctrl_copy.transitions.add(c_state, post_s, dict(set(labels_updated_el)))
    return ctrl_copy


def equiv_alpha(ctrl, outputs={'loc'}):
    """ 
    compute equivalence classes.
        Parameters
        ----------
    ctrl :  mealy machine
    outputs :  Tells which outputs are critical and should be kept. Given as a set of strings.

    Code is adapted from networkx.algorithms.minors.equivalenceclasses by Jeffry Finkelstein.

    """
    # 1. Find R_0 =  equivalence class of elements with the same labels on their outgoing transitions.

    blocks = []
    # Determine the equivalence class for each element of the iterable.
    for y in ctrl.states():
        # Each element y must be in *exactly one* equivalence class.
        #
        # Each block is guaranteed to be non-empty
        for block in blocks:
            x = next(iter(block))

            if len(ctrl[x]) != len(ctrl[y]):
                # print('unequal number')
                continue

            # compute set of labels:
            labels_x = {frozenset([(key, label[key]) for key in ctrl.inputs.keys()]
                                  + [(output, label[output]) for output in outputs])
                        for (_x, _y, label) in ctrl.transitions.find({x})}
            labels_y = {frozenset([(key, label[key]) for key in ctrl.inputs.keys()]
                                  + [(output, label[output]) for output in outputs])
                        for (_x, _y, label) in ctrl.transitions.find({y})}

            if labels_x == labels_y:
                block.append(y)
                break
        else:
            # If the element y is not part of any known equivalence class, it
            # must be in its own, so we create a new singleton equivalence
            # class for it.
            blocks.append([y])
    return {frozenset(block) for block in blocks}



def iterate_equiv(q_blocks, ctrl, outputs={'loc'}):
    """ Iterate the equivalence classes
    Parameters
    ----------
    q_blocks : equivalence classes
    ctrl :  mealy machine
    outputs :  Tells which outputs are critical and should be kept. Given as a set of strings.
    """
    dict__r = dict(sum([list(it_product(block, {i})) for (i, block) in enumerate(q_blocks)], []))

    blocks = []
    # Determine the equivalence class for each element of the iterable.
    for y in ctrl.states():
        #  Each element y must be in *exactly one* equivalence class.
        #
        # Each block is guaranteed to be non-empty
        for block in blocks:
            x = next(iter(block))

            if len(ctrl[x]) != len(ctrl[y]):
                #  print('unequal number')
                continue

            # compute set of labels:
            labels_x = {frozenset([(key, label[key]) for key in ctrl.inputs.keys()] +
                                  [(output, label[output]) for output in outputs] +
                                  [('Relx', dict__r[_x])]+[('Rely', dict__r[_y])])
                        for (_x, _y, label) in ctrl.transitions.find({x})}
            labels_y = {frozenset([(key, label[key]) for key in ctrl.inputs.keys()] +
                                  [(output, label[output]) for output in outputs] +
                                  [('Relx', dict__r[_x])]+[('Rely', dict__r[_y])])
                        for (_x, _y, label) in ctrl.transitions.find({y})}

            if labels_x == labels_y:
                block.append(y)
                break
        else:
            # If the element y is not part of any known equivalence class, it
            # must be in its own, so we create a new singleton equivalence
            # class for it.
            blocks.append([y])
    return {frozenset(block) for block in blocks}


def prune_init(ctrl,init_event=None):
    ctrl_s = synth.determinize_machine_init(ctrl)

    if init_event is not None:
        try:
            keys = list(set(key for (key,val) in list(init_event)))

            inputsb = {env_var: ctrl.inputs[env_var] for env_var in keys}
            # this allows you to give a subset of the inputs

            set_in = set.union(*[set(it_product({key}, values)) for (key, values) in inputsb.items()
                                  if not values == {0, 1}] + [
                                     set(it_product({key}, {True, False})) for (key, values) in inputsb.items()
                                     if values == {0, 1}])
            if not init_event <= set_in:
                raise ValueError('The set of initial environment values does not'
                                 ' belong to the set of inputs of the mealy machine')
            for s, to, label in ctrl_s.transitions.find({'Sinit'}):
                if not (set.intersection(set(label.items()), set_in)) <= init_event:
                    ctrl_s.transitions.remove(s, to, attr_dict=label)
            if ctrl_s['Sinit'] is None:
                raise ValueError('The set of initial environment values does not'
                                 ' belong to the set of inputs of the mealy machine.\n'
                                 ' All initial transitions were removed.')

        except ValueError as inst:
            print(inst.args)
            print('Determinized Mealy machine,'
                  ' initial transitions have not been pruned.(WARNING)')
            return synth.determinize_machine_init(ctrl)

    return ctrl_s


def quotient_mealy(mealy, node_relation=None, relabel=False, outputs={'loc'}):
    """Returns the quotient graph of ``G`` under the specified equivalence
    relation on nodes.

    Parameters
    ----------
    mealy : NetworkX graph
       The graph for which to return the quotient graph with the specified node
       relation.

    node_relation : Boolean function with two arguments
       This function must represent an equivalence relation on the nodes of
       ``G``. It must take two arguments *u* and *v* and return ``True``
       exactly when *u* and *v* are in the same equivalence class. The
       equivalence classes form the nodes in the returned graph.


        unlike the original networkx.quotient_graph selfloops are maintained  

    relabel : Boolean
        if true relabel nodes in the graph 

    outputs :  Tells which outputs are critical and should be kept. Given as a set of strings.

    """
    if node_relation is None:
        node_relation = lambda u, v: mealy.states.post(u) == mealy.states.post(v)

    q_mealy = transys.MealyMachine()
    q_mealy.add_inputs(mealy.inputs)
    q_mealy.add_outputs(mealy.outputs)
    # Compute the blocks of the partition on the nodes of G induced by the
    # equivalence relation R.
    if relabel:
        mapping = dict((n, i) for (i, n) in enumerate(equivalence_classes(mealy, node_relation)))
        for (n, i) in mapping.items():
            if {'Sinit'} <= set(n):
                mapping[n] = 'Sinit'
        q_mealy.add_nodes_from({n for (i, n) in mapping.items()})
    else:
        q_mealy.add_nodes_from(equivalence_classes(mealy, node_relation))

    if relabel:
        block_pairs = it_product(mapping.keys(), mapping.keys())
        for (b, c) in block_pairs:
            labels = {frozenset([(key, label[key]) for key in mealy.inputs.keys()]
                                + [(output, label[output]) for output in outputs])
                      for (x, y, label) in mealy.transitions.find(b, c)}
            for q in labels:
                q_mealy.transitions.add(mapping[b], mapping[c], **dict(q))
    else:
        block_pairs = it_product(q_mealy, q_mealy)
        for (b, c) in block_pairs:
            labels = {frozenset([(key, label[key]) for key in mealy.inputs.keys()]
                                + [(output, label[output]) for output in outputs])
                      for (x, y, label) in mealy.transitions.find(b, c)}
            for q in labels:
                q_mealy.transitions.add(b, c, **dict(q))

    if relabel:
        for node_eq in mapping.keys():
            if any(init in node_eq for init in mealy.states.initial):
                q_mealy.states.initial.add(mapping[node_eq])
    else:  # only initializing  after relabel
        for node_eq in q_mealy.nodes():
            if any(init in node_eq for init in mealy.states.initial):
                q_mealy.states.initial.add(node_eq)

    return q_mealy

def save_png(ctrl,name='untitled'):
    from tulip.transys.export import graph2dot
    pydot_ctrl = graph2dot._graph2pydot(ctrl)
    pydot_ctrl.set_rankdir('TB')
    # pydot_ctrl.set_splines('polyline')
    pydot_ctrl.set_bgcolor('white')
    pydot_ctrl.set_nodesep(.4)
    pydot_ctrl.set_ranksep(.4)

    pydot_ctrl.set_size('"40,30"')
    pydot_ctrl.set_concentrate('False')

    #png_str = pydot_ctrl.create_jpeg(prog='dot')
    pydot_ctrl.write_png(name+'.png',prog='dot')
    return

