"""Among other routines, dump XMI UML Statecharts from MealyMachine of TuLiP.

Assumptions
===========

- There is only one initial state in the finite-state machine, and it
  is named "Sinit".

- This one handles multiple triggers, and reduced definitions of outputs

- This one is going to be able to send out events (instead of iniation control actions)
SCL; 29 Jul 2014
"""

# DONE
#  cStringIO ==>> StringIO
import networkx as nx

# import cStringIO
# TODO find replacement for  cStringIO; first try follows
# TODO unnecessary relabeling needed

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

from itertools import product as it_product
import itertools
import uuid
from Interface.Transform import *


def create_env_event(env_vars, valuation):
    """

    @type env_vars: list
    """

    return "_".join([str(v) + "_" + str(valuation[v]) for v in env_vars])


def tulip_to_xmi(strat, ctrl_sys):
    f = StringIO()

    name_model = 'Ctrl_modes'
    SignalEvent = ''
    diagram_id = str(hash((name_model, 'Diagram')))
    # -------- PIECE of XML ----------
    # PREFACE
    f.write(PREFACE_combi)  # start of model with name = DATA
    # ---end ----- PIECE of XML ----------
    ctrl = fts2SC(ctrl_sys, env_name='ctrl')
    outputs = {'act'}

    if not outputs <= set(ctrl.outputs.keys()):
        outputs = set(ctrl.outputs.keys())
        print('WARNING: Wrong output set. Taking into account all outputs')

    (state_names, state_ids) = _state_labeling(ctrl)
    # use new function for computing incoming events

    # Start uml:StateMachine --> the controller
    f.write("<packagedElement xmi:type='uml:StateMachine' xmi:id='" + str(hash(name_model)) + "' xmi:uuid='" + str(
        uuid.uuid1()) + "' name='" + name_model + "' isReentrant='false'> \n")

    # ------------------ Find Events --------------------------
    (events_input, list_in, labels) = _inputs2events(ctrl)
    (events_output) = _outputs2events(ctrl, outputs)

    # ----------------- Add Events  RTI + Inputs & outputs --------------------------
    events_str = "          <event xmi:idref='" + str(hash('RTI')) + "_1" + "'/>\n"
    SignalEvent += _signalevent('RTI')
    for event in events_input:
        events_str += " <event xmi:idref='" + str(hash(event)) + "_1" + "'/>\n"
        SignalEvent += _signalevent(event)
    for event in events_output:
        events_str += "          <event xmi:idref='" + str(hash(event)) + "_1" + "'/>\n"
        SignalEvent += _signalevent(event)
    f.write(extender(events_str))  # write model extension with all the events in it

    # ----------------- Add Signals for  RTI + Inputs & outputs --------------------------
    f.write(_signals('RTI', 'RTI'))  # Add RTI

    for event in events_input:  # add Inputs
        f.write(_signals(event, create_env_event(ctrl.inputs.keys(), dict(event))))
    for event in events_output:  # add outputs
        if event[0] == 'sys_actions':
            f.write(_signals(event, str(event[1])))
        else:
            f.write(_signals(event, event[0] + '_' + str(event[1])))

    # ---- Open up region where we write the states & transitions---
    f.write("<region xmi:type='uml:Region' xmi:id='" + str(hash(name_model)) + "_1' xmi:uuid='" + str(uuid.uuid1())
            + "' visibility='public'>")

    # -------------Start positioning -------------------------------
    binary1 = "BINARY-4a3fc940-2bdc-4a6f-8a1e-687138c112b5"
    mdOwnedViews1 = """			<xmi:Extension extender='MagicDraw UML 18.0'>
    		<filePart name='""" + str(binary1) + """' type='XML' header='&lt;?xml version=&#39;1.0&#39; encoding=&#39;UTF-8&#39;?&gt;'><mdOwnedViews>
    """
    mdOwnedViews1 += """ <mdElement elementClass="DiagramFrame" xmi:id="_18_0_6_12a303c1_1500791404771_200057_12333">
       			<elementID xmi:idref=""" + '"' + str(
        diagram_id) + '">' + """</elementID><geometry>5, 5, 977, 441</geometry><compartment compartmentID="TAGGED_VALUES"></compartment><mdOwnedViews></mdOwnedViews></mdElement>"""

    # ------------------ Add the states  --------------------------
    Sinit_id = None
    assert len(ctrl.states.initial) <= 1  # make sure there is no nondeterminism in the initialisation

    pseudostate_id = str(hash(name_model)) + '_0'
    f.write("  <subvertex xmi:type='uml:Pseudostate' xmi:id='" + pseudostate_id + "' xmi:uuid='" + str(
        uuid.uuid1()) + "' visibility='public'/>\n")
    Refs_text = _refs(pseudostate_id)

    mdOwnedViews1 += "<mdElement elementClass='PseudoState' xmi:id='" + pseudostate_id + "1" + "'><elementID xmi:idref='" + pseudostate_id + "' /><geometry>" + str(
        100) + ", " + str(
        100) + ", 18, 18</geometry><compartment compartmentID='TAGGED_VALUES'/><mdOwnedViews/></mdElement>\n"

    for i, state in enumerate(ctrl.states):
        if (state == "Sinit") | (state in ctrl.states.initial):
            Sinit_id = id(state)
        f.write(_states(state, state_names, entry='entry()'))  # add vertix for state
        Refs_text += _refs(state, type='id')
        mdOwnedViews1 += "<mdElement elementClass='State' xmi:id='" + str(
            id(state) + 1) + "'><elementID xmi:idref='" + str(
            id(state)) + "' /><geometry>" + str(140 + 45 * (i % int(len(ctrl) ** (1 / 2.0)))) + ", " + str(
            100 + 45 * (int(i / int(len(ctrl) ** (
                1 / 2.0))))) + ", 30, 20</geometry><compartment compartmentID='TAGGED_VALUES'/><mdOwnedViews/></mdElement>\n"

    # ------------------ Add the transitions  --------------------------
    # Add all the RTI transitions
    for state in ctrl.states:
        f.write(_rti(state, rti='at_RTI()'))

    # Add the transitions from the pseudos state
    f.write("  <transition xmi:type='uml:Transition' xmi:id='" + pseudostate_id + "_1" + "' xmi:uuid='" + str(
        uuid.uuid1()) + "' visibility='public' source='" + pseudostate_id + "' target='" + str(Sinit_id) + "'/>\n")
    Refs_text += _refs(pseudostate_id + "_1")

    mdOwnedViews1 += "<mdElement elementClass='Transition' xmi:id='" + pseudostate_id + "_2" + "'><elementID xmi:idref='" + pseudostate_id + "_1" + "'/><linkSecondEndID xmi:idref='" + pseudostate_id + "1" + "'/><linkFirstEndID xmi:idref='" + str(
        Sinit_id + 1) + "'/><geometry>65, 104; 65, 64; </geometry><compartment compartmentID='TAGGED_VALUES'/><nameVisible xmi:value='true'/></mdElement>\n"

    for trans_fro, trans_to, label in ctrl.transitions(data=True):
        f.write(_transition(trans_fro, trans_to, label, state_ids, events_input, list_in, events_output))
        Refs_text += _refs(str(hash((trans_fro, str(label.items())))))
        mdOwnedViews1 += _mdelement(trans_fro, trans_to, label, state_ids, events_input, ctrl, list_in, events_output,
                                    guard=None)

    mdOwnedViews1 += "</mdOwnedViews></filePart></xmi:Extension>"

    f.write("</region>")

    # ------- Add Diagram info -------
    Refs_text += _refs(diagram_id)

    f.write(_diag_info(Refs_text, binary1, diagram_id, name_model))

    # End uml:StateMachine --> the controller
    f.write("</packagedElement>")

    #
    #
    # -------------------------------------------------------------
    # -------------------------------------------------------------
    # -------------------------------------------------------------
    #
    #
    #

    # Start uml:StateMachine --> the strategy
    ctrl = strat
    # ctrl = fts2SC(ctrl_sys, env_name='ctrl')
    outputs = {'ctrl'}
    name_model = 'Alice'

    diagram_id = str(hash((name_model, 'Diagram')))
    f.write("<packagedElement xmi:type='uml:StateMachine' xmi:id='" + str(hash(name_model)) + "' xmi:uuid='" + str(
        uuid.uuid1()) + "' name='" + name_model + "' isReentrant='false'> \n")
    # ---end ----- PIECE of XML ----------
    if not outputs <= set(ctrl.outputs.keys()):
        outputs = set(ctrl.outputs.keys())
        print('WARNING: Wrong output set. Taking into account all outputs')

    (state_names, state_ids) = _state_labeling(ctrl)
    # use new function for computing incoming events

    # ------------------ Find Events --------------------------
    (events_input, list_in, labels) = _inputs2events(ctrl)
    (events_output) = _outputs2events(ctrl, outputs)

    # ----------------- Add Events  RTI + Inputs & outputs --------------------------
    for event in events_input:
        events_str += "          <event xmi:idref='" + str(hash(event)) + "_1" + "'/>\n"
        SignalEvent += _signalevent(event)

    for event in events_output:
        events_str += "          <event xmi:idref='" + str(hash(event)) + "_1" + "'/>\n"
        SignalEvent += _signalevent(event)

    f.write(extender(events_str))  # write model extension with all the events in it

    # ----------------- Add Signals for  RTI + Inputs & outputs --------------------------
    for event in events_input:  # add Inputs
        f.write(_signals(event, create_env_event(ctrl.inputs.keys(), dict(event))))
    for event in events_output:  # add outputs
        if event[0] == 'sys_actions':
            f.write(_signals(event, str(event[1])))
        else:
            f.write(_signals(event, event[0] + '_' + str(event[1])))

    # ---- Open up region where we write the states & transitions---
    f.write("<region xmi:type='uml:Region' xmi:id='" + str(hash(name_model)) + "_1' xmi:uuid='" + str(uuid.uuid1())
            + "' visibility='public'>")

    # -------------Start positioning -------------------------------
    binary2 = "BINARY-394d52bc-cf37-4c5e-8b2e-8dbd78a60e8d"
    mdOwnedViews2 = """			<xmi:Extension extender='MagicDraw UML 18.0'>
    		<filePart name='""" + str(binary2) + """' type='XML' header='&lt;?xml version=&#39;1.0&#39; encoding=&#39;UTF-8&#39;?&gt;'><mdOwnedViews>
    """

    # ------------------ Add the states  --------------------------
    Sinit_id = None
    assert len(ctrl.states.initial) <= 1  # make sure there is no nondeterminism in the initialisation

    pseudostate_id = str(hash(name_model)) + '_0'
    Refs_text = _refs(pseudostate_id)
    mdOwnedViews2 += "<mdElement elementClass='PseudoState' xmi:id='" + pseudostate_id + "1" + "'><elementID xmi:idref='" + pseudostate_id + "' /><geometry>" + str(
        100) + ", " + str(
        100) + ", 18, 18</geometry><compartment compartmentID='TAGGED_VALUES'/><mdOwnedViews/></mdElement>\n"

    f.write("  <subvertex xmi:type='uml:Pseudostate' xmi:id='" + pseudostate_id + "' xmi:uuid='" + str(
        uuid.uuid1()) + "' visibility='public'/>\n")

    for state in ctrl.states:
        if (state == "Sinit") | (state in ctrl.states.initial):
            Sinit_id = id(state)
        f.write(_states(state, state_names, entry='set_guard()'))  # add vertix for state
        Refs_text += _refs(state, type='id')
        mdOwnedViews2 += "<mdElement elementClass='State' xmi:id='" + str(id(state) + 1) + "'><elementID xmi:idref='" \
                         + str(id(state)) + "' /><geometry>" + str(140 + 45 * (i % int(len(ctrl) ** (1 / 2.0)))) + ", " \
                         + str(100 + 45 * (int(i / int(len(ctrl) ** (1 / 2.0))))) \
                         + ", 30, 20</geometry><compartment compartmentID='TAGGED_VALUES'/><mdOwnedViews/></mdElement>\n"

    # ------------------ Add the transitions  --------------------------

    # Add the transitions from the pseudos state
    f.write("  <transition xmi:type='uml:Transition' xmi:id='" + pseudostate_id + "_1" + "' xmi:uuid='" + str(
        uuid.uuid1()) + "' visibility='public' source='" + pseudostate_id + "' target='" + str(Sinit_id) + "'/>\n")
    Refs_text += _refs(pseudostate_id + "_1")

    mdOwnedViews2 += "<mdElement elementClass='Transition' xmi:id='" + pseudostate_id + "_2" + "'><elementID xmi:idref='" + pseudostate_id + "_1" + "'/><linkSecondEndID xmi:idref='" + pseudostate_id + "1" + "'/><linkFirstEndID xmi:idref='" + str(
        Sinit_id + 1) + "'/><geometry>65, 104; 65, 64; </geometry><compartment compartmentID='TAGGED_VALUES'/><nameVisible xmi:value='true'/></mdElement>\n"

    for trans_fro, trans_to, label in ctrl.transitions(data=True):
        f.write(_transition(trans_fro, trans_to, label, state_ids, events_input, list_in, events_output,
                            guard='read_guard()'))
        Refs_text += _refs(str(hash((trans_fro, str(label.items())))))
        mdOwnedViews2 += _mdelement(trans_fro, trans_to, label, state_ids, events_input, ctrl, list_in, events_output,
                                    guard=None)

    mdOwnedViews2 += """ <mdElement elementClass="DiagramFrame" xmi:id="_18_0_6_12a303c1_1500791404771_200057_12344">
    			<elementID xmi:idref=""" + '"' + str(
        diagram_id) + '">' + """</elementID><geometry>5, 5, 977, 441</geometry><compartment compartmentID="TAGGED_VALUES"></compartment><mdOwnedViews></mdOwnedViews></mdElement>"""
    mdOwnedViews2 += "</mdOwnedViews></filePart></xmi:Extension>"
    f.write("</region>\n")
    # ------- Add Diagram info -------
    Refs_text += _refs(diagram_id)

    f.write(_diag_info(Refs_text, binary2, diagram_id, name_model))

    # End uml:StateMachine --> the strategy
    f.write("</packagedElement>\n")

    # ADD signal event
    f.write(SignalEvent)
    # Model
    f.write("</uml:Model>\n")
    f.write("<MagicDraw_Profile:DiagramInfo xmi:id='" + str(id(
        diagram_id)) + "_12" + "' base_Diagram='" + diagram_id + "' Modification_date='7/22/17 11:30 PM' Author='TuLiP' Last_modified_by='TuLiP'/>")

    # write file part for mdOwnedViews
    f.write(mdOwnedViews1)

    f.write(mdOwnedViews2)

    f.write(END_combi)
    return f.getvalue()


def _signalevent(event):
    text = "<packagedElement xmi:type='uml:SignalEvent' xmi:id='" + str(
        hash(event)) + "_1" + "' xmi:uuid='" + str(uuid.uuid1()) + "' signal='" + str(
        hash(event)) + "_12" + "' visibility='public'/>\n"
    return text


def _diag_info(Refs_text, binary, diag_id, name):
    text = """<xmi:Extension extender='MagicDraw UML 18.0'><modelExtension>
    					<ownedDiagram xmi:type='uml:Diagram' xmi:id='""" + str(diag_id) + "' xmi:uuid='" + str(
        uuid.uuid1()) + "' name='" + str(name) + """' visibility='public' context='""" + str(
        hash(name)) + """' ownerOfDiagram='""" + str(hash(name)) + """'>
    						<xmi:Extension extender='MagicDraw UML 18.0'>
    							<diagramRepresentation><diagram:DiagramRepresentationObject ID='""" + str(
        hash(name + 'ID')) + """' diagramStyleID='""" + str(hash(name + 'IDstyle')) + """' initialFrameSizeSet='true' requiredFeature='com.nomagic.magicdraw.plugins.impl.sysml#SysML;MD_customization_for_SysML.mdzip;UML_Standard_Profile.mdzip' type='SysML State Machine Diagram' umlType='State Machine Diagram' xmi:id='_XRBQYG9wEeew-re8YLvkUg' xmi:version='2.0' xmlns:binary='http://www.nomagic.com/ns/cameo/client/binary/1.0' xmlns:diagram='http://www.nomagic.com/ns/magicdraw/core/diagram/1.0' xmlns:xmi='http://www.omg.org/XMI' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'>
    									<diagramContents contentHash='""" + str(uuid.uuid1()) + """' exporterName='MagicDraw UML' exporterVersion='18.0' xmi:id='_XRBQYW9wEeew-re8YLvkUg'>
    										"""
    text += "<binaryObject streamContentID='" + str(binary) + "' xmi:id='" + str(
        hash(binary)) + "' xsi:type='binary:StreamIdentityBinaryObject'/>"
    text += Refs_text
    text += """	</diagramContents></diagram:DiagramRepresentationObject></diagramRepresentation>
    					</xmi:Extension></ownedDiagram></modelExtension> </xmi:Extension>"""
    return text


def _mdelement(trans_fro, trans_to, label, state_ids, events_input, ctrl, list_in, events_output, guard=None):
    mdOwnedViews = ' '
    mdOwnedViews += "<mdElement elementClass='Transition' xmi:id='" + str(
        hash((trans_fro, trans_to)) + 1) + "'><elementID xmi:idref='" + str(
        hash((trans_fro, str(label.items())))) + "'/>"
    mdOwnedViews += "<linkFirstEndID xmi:idref='" + str(id(trans_fro) + 1) + "'/><linkSecondEndID xmi:idref='" + str(
        state_ids[
            trans_to] + 1) + "'/><geometry>65, 104; 65, 64; </geometry><compartment compartmentID='TAGGED_VALUES'/><nameVisible xmi:value='true'/>"
    mdOwnedViews += "<linkNameID xmi:idref='" + str(hash((trans_fro, str(label.items())))) + "_3" + "'/>"
    mdOwnedViews += "<mdOwnedViews><mdElement elementClass='TextBox' xmi:id='" + str(
        hash((trans_fro, str(label.items())))) + "_3" + "'>\n"
    mdOwnedViews += "<geometry>" + str(100) + ", " + str(100) + ", 24, 13</geometry>"
    event_str = ''
    for event in events_input:
        if (set.intersection(set(label.items()), list_in) <= set(event)):
            event_str += ', ' + create_env_event(ctrl.inputs.keys(), dict(event))
    mdOwnedViews += "<text>" + event_str + "</text></mdElement>"

    mdOwnedViews += "</mdOwnedViews></mdElement>\n"
    return mdOwnedViews


def _transition(source, target, label, state_ids, events_inputs, list_in, events_output, guard=None):
    # define transition
    if guard is not None:
        text = "  <transition xmi:type='uml:Transition' xmi:id='" + str(
            hash((source, str(label.items())))) + "' xmi:uuid='" + str(
            uuid.uuid1()) + "' visibility='public' source='" + str(id(source)) + "' guard='" + str(
            hash(guard + str((source, str(label.items()))))) + "' target='" + str(state_ids[target]) + "'>"
        text += "<ownedRule  xmi:type='uml:Constraint' xmi:id='" + str(
            hash(guard + str((source, str(label.items()))))) + "' xmi:uuid='" + str(
            uuid.uuid1()) + "'>\n"
        text += "<specification  xmi:type='uml:OpaqueExpression' xmi:id='" + str(
            hash(guard + str((source, str(label.items()))))) + "_12" + "' xmi:uuid='" + str(
            uuid.uuid1()) + "' >" + " <body>" + guard + "</body > <language>English</language>" + "  </specification > </ownedRule >"
    else:
        text = "  <transition xmi:type='uml:Transition' xmi:id='" + str(
            hash((source, str(label.items())))) + "' xmi:uuid='" + str(
            uuid.uuid1()) + "' visibility='public' source='" + str(id(source)) + "' target='" + str(
            state_ids[target]) + "'>"

    # Add trigger
    for event in events_inputs:
        if set.intersection(set(label.items()), list_in) <= set(event):
            text += "    <trigger xmi:type='uml:Trigger' xmi:id='" + str(hash((source, event))) + "_122" \
                    + "' xmi:uuid='" + str(uuid.uuid1()) + "' visibility='public' event='" \
                    + str(hash(event)) + "_1" + "'/>"

    # Add effect
    for event in events_output:
        if set([event]) <= set(label.items()):
            if event[0] == 'sys_actions':
                text += "  <effect xmi:type='uml:FunctionBehavior' xmi:id='" + str(
                    hash((source, str(label.items())))) + "_13" + "' visibility='public' name='" + str(event[1]) + "'/>"
            elif event[0] == 'act':
                text += "  <effect xmi:type='uml:FunctionBehavior' xmi:id='" + str(
                    hash((source, str(label.items())))) + "_13" + "' visibility='public' name='" + event[0] \
                        + '_' + str(event[1]) + "()" + "'/>"
            else:
                text += "  <effect xmi:type='uml:FunctionBehavior' xmi:id='" + str(
                    hash((source, str(label.items())))) + "_13" + "' visibility='public' name='" + event[0] \
                        + '_' + str(event[1]) + "'/>"
    text += "  </transition>\n"
    return text


def _outputs2events(ctrl, outputs):
    events_output = list(itertools.chain(*[list(it_product({key}, values)) for (key, values) in ctrl.outputs.items()
                                           if (not values == {0, 1}) and ({key} <= outputs)] + [
                                              list(it_product({key}, {True, False})) for (key, values) in
                                              ctrl.outputs.items()
                                              if (values == {0, 1}) and ({key} <= outputs)]))

    return events_output


def _rti(state, rti='at_RTI()'):
    text = " <transition xmi:type='uml:Transition' xmi:id='" + str(id(state)) + "_111" + "' xmi:uuid='" + str(
        uuid.uuid1()) + "' visibility='public' kind='internal' source='" + str(id(state)) + "' target='" + str(
        id(state)) + "'>"
    text += " <effect xmi:type='uml:FunctionBehavior' xmi:id='" + str(id(state)) + "_112" + "' xmi:uuid='" + str(
        uuid.uuid1()) + "' name='" + str(rti) + "' isReentrant='false'/>"
    text += "<trigger xmi:type='uml:Trigger' xmi:id='" + str(id(state)) + "_113" + "' xmi:uuid='" + str(
        uuid.uuid1()) + "' visibility='public' event='" + str(hash('RTI')) + "_1'/></transition> \n"
    return text


def _states(state, state_names, entry=None):
    text = "  <subvertex xmi:type='uml:State' xmi:id='" + str(id(state)) + "' xmi:uuid='" + str(
        uuid.uuid1()) + "' name='" + state_names[state] + "' visibility='public'>"
    if (entry is not None) & (isinstance(entry, str)):
        text += "    <entry xmi:type='uml:Activity' xmi:id='" + str(id(state)) + "_1" + "' xmi:uuid='" + str(
            uuid.uuid1()) + "' name='" + str(entry) + "' visibility='public'/>\n" + "  </subvertex>\n"

    return text


def _refs(state, type=None):
    if type == 'id':
        text = "<usedObjects href='#" + str(id(state)) + "'/>\n"
        text += "<usedElements>" + str(id(state)) + "</usedElements>\n"
    elif type == 'hash':
        text = "<usedObjects href='#" + str(hash(state)) + "'/>\n"
        text += "<usedElements>" + str(hash(state)) + "</usedElements>\n"
    else:
        text = "<usedObjects href='#" + str(state) + "'/>\n"
        text += "<usedElements>" + str(state) + "</usedElements>\n"
    return text


def _signals(event, name):
    text = "<nestedClassifier xmi:type='uml:Signal' xmi:id='" + str(hash(event)) + "_12" + "' xmi:uuid='" + str(
        uuid.uuid1()) + "' name='" + str(name) + "' visibility='public'/>\n"
    return text


def extender(inner):
    text = """	<xmi:Extension extender='MagicDraw UML 18.0'> <modelExtension>""" + "\n" \
           + inner + """	</modelExtension> </xmi:Extension>""" + "\n"
    return text


def _state_labeling(ctrl):
    relabel = not any([(isinstance(state, int) | (isinstance(state, str))) for state in ctrl.nodes()])
    state_names = dict()
    state_ids = dict()

    for i, state in enumerate(ctrl.states()):
        state_ids[state] = id(state)
        if (state == 'Sinit') | (state == 'Minit'):
            state_names[state] = str(state)
        elif relabel:
            state_names[state] = str(i)
        elif isinstance(state, int):
            state_names[state] = 's' + str(state)
        else:
            state_names[state] = str(state)

    return (state_names, state_ids)


def _inputs2events(ctrl):
    # ----------------- Find Events in ctrl -------------------------
    # Equal to incoming signals
    # Equal to signal events
    # the potential combinations of outside signals
    # TODO not all combinatorially generated events are possible. Better to first prune them

    events_list = list(it_product(*[set(it_product({key}, values)) for (key, values) in ctrl.inputs.items()
                                    if not values == {0, 1}] + [
                                       set(it_product({key}, {True, False})) for (key, values) in ctrl.inputs.items()
                                       if values == {0, 1}]))

    list_in = set.union(*[set(it_product({key}, values)) for (key, values) in ctrl.inputs.items()
                          if not values == {0, 1}] + [
                             set(it_product({key}, {True, False})) for (key, values) in ctrl.inputs.items()
                             if values == {0, 1}])

    labels = {frozenset(set.intersection(set(label.items()), list_in)) for (x, y, label) in ctrl.transitions(data=True)}

    events_list_minimal = []
    for event in events_list:
        if {frozenset(event)} <= labels:
            events_list_minimal += [event]

    return (events_list_minimal, list_in, labels)


def mealy_to_xmi_uml(ctrl_sys, env_events=True, outputs={'loc'}, name="ThermostatCtrl", relabel=False, Type='default'):
    """
    @param ctrl: MealyMachine, as in TuLiP

    @param env_events: if False (not default), every edge of the state
        machine is used to create an event of the form MOV_i_j, where
        the transition is from state i to state j.  If True, then
        events are of the form ENV_e0_v0_e1_v1_..., where v0 is the
        value taken by environment variable e0.  v0 must be a
        nonnegative integer; e.g., for boolean variables it is 0 or 1.

    @param inputs: If None (default ctrl is asserted to be a Mealy 
    machine and inputs are recovered from there. Otherwise inputs are
     selected based on the values of the labels.  

    @param name : give name of the XML UML Statechart, default is name="ThermostatCtrl"

    @param  Type = 'default'  => Default translation the XMI. (mealy is expected)
            Type = 'control' => Translated as hybrid control modes (FTS is expected)
            Type = 'strat' => mealy machine strategy for synthesis problem (mealy is expected)


    @return: str of XMI UML Statechart
    """
    # states are named to complicated (due to gr1c) fix that first!

    # f = cStringIO.StringIO()
    # TODO check whether fix for above line works
    f = StringIO()

    pseudostate_id = "_1"
    print('Received a control system')
    if Type == 'control':
        print('Received a control system')
        ctrl = fts2SC(ctrl_sys, env_name='ctrl')
    elif (Type == 'default') | (Type == 'strat'):
        ctrl = ctrl_sys
    else:
        raise ValueError('Type should be either "control", "default", or "strat"')

    if not outputs <= set(ctrl.outputs.keys()):
        outputs = set(ctrl.outputs.keys())
        print('WARNING: Wrong output set. Taking into account all outputs')

    if relabel:
        mapping = dict((n, i) for (i, n) in enumerate(ctrl.nodes()))
        mapping['Sinit'] = 'Sinit'
        nx.relabel_nodes(ctrl, mapping, copy=False)

    if (Type == 'default') | (Type == 'strat'):
        # create dictionary of statenames this avoids errors
        state_names = dict()
        for i, state in enumerate(ctrl.states()):
            if isinstance(state, int):
                state_names[state] = "s" + str(state)
            elif state == 'Sinit':
                state_names[state] = str(state)
            else:
                state_names[state] = "s" + str(i)
    elif Type == 'control':
        state_names = dict()
        for i, state in enumerate(ctrl.states()):
            if state == 'Sinit':
                state_names[state] = str(state)
            else:
                state_names[state] = str(state)

    # ----------------- Find Events -------------------------
    # Equal to incoming signals
    # Equal to signal events
    # the potential combinations of outside signals
    # TODO not all combinatorially generated events are possible. Better to first prune them
    events_list = list(it_product(*[set(it_product({key}, values)) for (key, values) in ctrl.inputs.items()
                                    if not values == {0, 1}] + [
                                       set(it_product({key}, {True, False})) for (key, values) in ctrl.inputs.items()
                                       if values == {0, 1}]))

    events_output = list(itertools.chain(*[list(it_product({key}, values)) for (key, values) in ctrl.outputs.items()
                                           if (not values == {0, 1}) and ({key} <= outputs)] + [
                                              list(it_product({key}, {True, False})) for (key, values) in
                                              ctrl.outputs.items()
                                              if (values == {0, 1}) and ({key} <= outputs)]))
    # ----------------- Trigger transitions ---------
    list_in = set.union(*[set(it_product({key}, values)) for (key, values) in ctrl.inputs.items()
                          if not values == {0, 1}] + [
                             set(it_product({key}, {True, False})) for (key, values) in ctrl.inputs.items()
                             if values == {0, 1}])

    labels = {frozenset(set.intersection(set(label.items()), list_in)) for (x, y, label) in ctrl.transitions(data=True)}

    # ----------------- Begin preface -----------------------
    f.write(preface(name))

    # ------------------ Add inputs as Events --------------------------
    for event in events_list:
        if {frozenset(event)} <= labels:
            f.write("<event xmi:idref='" + str(hash(event)) + "_1" + "'/>\n")
    # Add RTI event in case system is for control
    if Type == 'control':
        f.write("<event xmi:idref='" + str(hash('RTI')) + "_1" + "'/>\n")
    # ----------------- Add outputs as Events --------------------------
    # add all outputs as EVENTS

    for event in events_output:
        f.write("<event xmi:idref='" + str(hash(event)) + "_1" + "'/>\n")

    # ------------------ Intermezzo  --------------------------
    # f.write(INTERMEZZO1) => removed for easy reading
    f.write("""</modelExtension> </xmi:Extension>""")

    # ------------------ Add signals nested in the state-machine package  --------------------------

    for event in events_list:
        if {frozenset(event)} <= labels:
            f.write(_signals(event, create_env_event(ctrl.inputs.keys(), dict(event))))

    for event in events_output:  # add outputs
        if event[0] == 'sys_actions':
            f.write(_signals(event, str(event[1])))
        else:
            f.write(_signals(event, event[0] + '_' + str(event[1])))
    # If the Type is control, also add the RTI as a signal
    if Type == 'control':
        f.write(_signals('RTI', 'RTI'))  # Add RTI

    # ------------------ Intermezzo  --------------------------
    f.write(INTERMEZZO2)
    f.write("  <subvertex xmi:type='uml:Pseudostate' xmi:id='" + pseudostate_id + "' xmi:uuid='" + str(
        uuid.uuid1()) + "' visibility='public'/>\n")

    # ------------------ Introduce the states  --------------------------
    Sinit_id = None
    assert len(ctrl.states.initial) <= 1  # make sure there is no nondeterminism in the initialisation

    for state in ctrl.states:
        if (state == "Sinit") | (state in ctrl.states.initial):
            Sinit_id = id(state)

        f.write("  <subvertex xmi:type='uml:State' xmi:id='" + str(id(state)) + "' xmi:uuid='" + str(
            uuid.uuid1()) + "' name='" + state_names[state] + "' visibility='public'>")
        if Type == 'strat':
            f.write("    <entry xmi:type='uml:Activity' xmi:id='" + str(id(state)) + "_1" + "' xmi:uuid='" + str(
                uuid.uuid1()) + "' name='set_guard()' visibility='public'/>\n")
        elif Type == 'control':
            f.write("    <entry xmi:type='uml:Activity' xmi:id='" + str(id(state)) + "_1" + "' xmi:uuid='" + str(
                uuid.uuid1()) + "' name='entry()' visibility='public'/>\n")

        f.write("  </subvertex>\n")

    # ------------------ Introduce the transitions  --------------------------
    f.write("  <transition xmi:type='uml:Transition' xmi:id='" + pseudostate_id + "_1" + "' xmi:uuid='" + str(
        uuid.uuid1()) + "' visibility='public' source='" + pseudostate_id + "' target='" + str(Sinit_id) + "'/>\n")
    for trans_fro, trans_to, label in ctrl.transitions(data=True):
        if Type == 'strat':
            f.write("  <transition xmi:type='uml:Transition' xmi:id='" + str(
                hash((trans_fro, str(label.items())))) + "' xmi:uuid='" + str(
                uuid.uuid1()) + "' visibility='public' source='" + str(
                id(trans_fro)) + "' guard='" + str(
                hash('set_guard()' + str((trans_fro, str(label.items()))))) + "' target='" + str(id(trans_to)) + "'>")
            f.write(" <ownedRule  xmi:type='uml:Constraint' xmi:id='" + str(
                hash('set_guard()' + str((trans_fro, str(label.items()))))) + "' xmi:uuid='" + str(
                uuid.uuid1()) + "'>\n")
            f.write("<specification  xmi:type='uml:OpaqueExpression' xmi:id='" + str(
                hash('read_guard()' + str((trans_fro, str(label.items()))))) + "_12" + "' xmi:uuid='" + str(
                uuid.uuid1()) + "' >" + " <body>read_guard()</body > <language>English</language>" + "  </specification > </ownedRule >")
        else:
            f.write("  <transition xmi:type='uml:Transition' xmi:id='" + str(
                hash((trans_fro, str(label.items())))) + "' xmi:uuid='" + str(
                uuid.uuid1()) + "' visibility='public' source='" + str(
                id(trans_fro)) + "' target='" + str(id(trans_to)) + "'>")
        # here we need multiple triggers!!
        # TODO check whether this is how it should be written
        for event in events_list:
            if {frozenset(event)} <= labels:
                if (set.intersection(set(label.items()), list_in) <= set(event)):
                    f.write("    <trigger xmi:type='uml:Trigger' xmi:id='" + str(hash((trans_fro, event))) + "_122"
                            + "' xmi:uuid='" + str(uuid.uuid1()) + "' visibility='public' event='"
                            + str(hash(event)) + "_1" + "'/>")

        for event in events_output:
            if set([event]) <= set(label.items()):
                if event[0] == 'sys_actions':
                    f.write("  <effect xmi:type='uml:FunctionBehavior' xmi:id='" + str(
                        hash((trans_fro, str(label.items())))) + "_13" + "' visibility='public' name='" + str(
                        event[1]) + "'/>")
                elif event[0] == 'act':
                    f.write("  <effect xmi:type='uml:FunctionBehavior' xmi:id='" + str(
                        hash((trans_fro, str(label.items())))) + "_13" + "' visibility='public' name='" + event[0]
                            + '_' + str(event[1]) + "()" + "'/>")
                else:
                    f.write("  <effect xmi:type='uml:FunctionBehavior' xmi:id='" + str(
                        hash((trans_fro, str(label.items())))) + "_13" + "' visibility='public' name='" + event[
                                0] + '_' + str(event[1]) + "'/>")
                    # TODO: the above should be changed to publish an Event
        f.write("  </transition>\n")
    # here we add the internal behaviours=> these are  kind of reentry transitions but they will skip the exit and entry actions
    if Type == 'control':
        for state in ctrl.states:
            f.write(" <transition xmi:type='uml:Transition' xmi:id='" + str(id(state)) + "_111" + "' xmi:uuid='" + str(
                uuid.uuid1()) + "' visibility='public' kind='internal' source='" + str(id(state)) + "' target='" + str(
                id(state)) + "'>")
            f.write(
                " <effect xmi:type='uml:FunctionBehavior' xmi:id='" + str(id(state)) + "_112" + "' xmi:uuid='" + str(
                    uuid.uuid1()) + "' name='at_RTI()' isReentrant='false'/>")
            f.write("<trigger xmi:type='uml:Trigger' xmi:id='" + str(id(state)) + "_113" + "' xmi:uuid='" + str(
                uuid.uuid1()) + "' visibility='public' event='" + str(hash('RTI')) + "_1'/></transition>")

    # ---------------------Intermezzo 3 -------------------------------------
    f.write(INTERMEZZO3)

    # ---------------------Signal events as packaged elements -----------------
    for event in events_list:
        if {frozenset(event)} <= labels:
            f.write("<packagedElement xmi:type='uml:SignalEvent' xmi:id='" + str(
                hash(event)) + "_1" + "' xmi:uuid='" + str(uuid.uuid1()) + "' signal='" + str(
                hash(event)) + "_12" + "' visibility='public'/>\n")

    for event in events_output:
        f.write("<packagedElement xmi:type='uml:SignalEvent' xmi:id='" + str(
            hash(event)) + "_1" + "' xmi:uuid='" + str(uuid.uuid1()) + "' signal='" + str(
            hash(event)) + "_12" + "' visibility='public'/>\n")

    # Add signal event for control=> reflects sampling instances
    if Type == 'control':
        f.write("<packagedElement xmi:type='uml:SignalEvent' xmi:id='" + str(
            hash('RTI')) + "_1" + "' xmi:uuid='" + str(uuid.uuid1()) + "' signal='" + str(
            hash('RTI')) + "_12" + "' visibility='public'/>\n")
    # ---------------------Intermezzo 4 -------------------------------------
    f.write(intermezzo4(name))

    # ---------------------Position the states -------------------------------------
    # position and shape states

    f.write(
        "<mdElement elementClass='PseudoState' xmi:id='" + pseudostate_id + "1" + "'><elementID xmi:idref='" + pseudostate_id + "' /><geometry>" + str(
            100) + ", " + str(
            100) + ", 18, 18</geometry><compartment compartmentID='TAGGED_VALUES'/><mdOwnedViews/></mdElement>\n")
    for i, state in enumerate(ctrl.states):
        f.write("<mdElement elementClass='State' xmi:id='" + str(id(state) + 1) + "'><elementID xmi:idref='" + str(
            id(state)) + "' /><geometry>" + str(140 + 45 * (i % int(len(ctrl) ** (1 / 2.0)))) + ", " + str(
            100 + 45 * (int(i / int(len(ctrl) ** (
                1 / 2.0))))) + ", 30, 20</geometry><compartment compartmentID='TAGGED_VALUES'/><mdOwnedViews/></mdElement>\n")
    # --------------------- Position the transitions ------------------------------
    # position

    f.write(
        "<mdElement elementClass='Transition' xmi:id='" + pseudostate_id + "_2" + "'><elementID xmi:idref='" + pseudostate_id + "_1" + "'/><linkSecondEndID xmi:idref='" + pseudostate_id + "1" + "'/><linkFirstEndID xmi:idref='" + str(
            Sinit_id + 1) + "'/><geometry>65, 104; 65, 64; </geometry><compartment compartmentID='TAGGED_VALUES'/><nameVisible xmi:value='true'/></mdElement>\n")
    for trans_fro, trans_to, d in ctrl.transitions(data=True):
        f.write("<mdElement elementClass='Transition' xmi:id='" + str(
            hash((trans_fro, trans_to)) + 1) + "'><elementID xmi:idref='" + str(
            hash((trans_fro, str(d.items())))) + "'/>")
        f.write("<linkFirstEndID xmi:idref='" + str(id(trans_fro) + 1) + "'/><linkSecondEndID xmi:idref='" + str(id(
            trans_to) + 1) + "'/><geometry>65, 104; 65, 64; </geometry><compartment compartmentID='TAGGED_VALUES'/><nameVisible xmi:value='true'/>")
        f.write("<linkNameID xmi:idref='" + str(hash((trans_fro, str(d.items())))) + "_3" + "'/>")
        f.write("<mdOwnedViews><mdElement elementClass='TextBox' xmi:id='" + str(
            hash((trans_fro, str(d.items())))) + "_3" + "'>\n")
        f.write("<geometry>" + str(100) + ", " + str(100) + ", 24, 13</geometry>")
        if env_events:
            event_str = ''
            for event in events_list:
                if {frozenset(event)} <= labels:
                    if (set.intersection(set(d.items()), list_in) <= set(event)):
                        event_str += ', ' + create_env_event(ctrl.inputs.keys(), dict(event))
            f.write("<text>" + event_str + "</text></mdElement>")
        else:
            f.write("<text>" + "MOV_" + str(trans_fro) + "_" + str(trans_to) + "</text></mdElement>")
        f.write("</mdOwnedViews></mdElement>\n")

    # -----------------------Finish --------------------------------------------------
    f.write(POSTFACE)

    return f.getvalue()


def implement_actions(ctrl, sys_dyn, disc_dynamics, name="tst"):
    # TODO: this needs to be fully rewritten to c code
    """Create implementations that can be copy-and-pasted into Impl.py file

    The outgoing transitions from Sinit are considered special because
    no trajectory of the physical (or real-valued, or underlying)
    system is necessary.
    """
    # f = cStringIO.StringIO()
    # TODO check whether fix for above line works
    f = StringIO()
    tab = "    "

    for trans_fro, trans_to, d in ctrl.transitions(data=True):

        f.write(tab + "def ACT_" + str(trans_fro) + "_" + str(trans_to) + "(self, e):\n")
        #   f.write(tab*2+"\"\"\"\n"+tab*2+"WARNING: This method was automatically generated by dumpsmach.py.\n"+tab*2+"\"\"\"\n")
        if trans_fro == "Sinit":
            f.write(tab * 2 + "self.x = e['x']\n")
            f.write(
                tab * 2 + "self.current_cell = find_controller.find_discrete_state(self.x, self.disc_dynamics.ppp)\n")
            f.write(
                tab * 2 + "LOGGER.info('Initializing at x0 = '+str(self.x)+', discrete cell '+str(self.current_cell))\n")
        else:
            f.write(tab * 2 + "target_cell = " + str(d["loc"]) + "\n")
            f.write(
                tab * 2 + "LOGGER.info('Computing control sequence to go from cell '+str(self.current_cell)+' to cell '+str(target_cell)+'...')\n")
            f.write(
                tab * 2 + "u = find_controller.get_input(self.x, self.sys_dyn, self.disc_dynamics, self.current_cell, target_cell)\n")
            f.write(tab * 2 + "LOGGER.info('Applying it...')\n")
            f.write(tab * 2 + "self.x = self.apply_control(self.x, u)\n")
            f.write(
                tab * 2 + "self.current_cell = find_controller.find_discrete_state(self.x, self.disc_dynamics.ppp)\n")
            f.write(tab * 2 + "LOGGER.info('Result is '+str(self.x)+', discrete cell '+str(self.current_cell))\n")

        f.write("\n")

    aux_methods_str = """
    def apply_control(self, x0, u, log_moves=True):
        x = x0.copy()
        LOGGER.info('apply_control: begin at x[0] = '+str(x))
        for k in xrange(u.shape[0]):
            x = np.dot(self.sys_dyn.A, x) + np.dot(self.sys_dyn.B, u[k])
            LOGGER.info('apply_control: u['+str(k)+'] = '+str(u[k])+'; x['+str(k+1)+'] = '+str(x))
        return x

    def sample_in_region(self, P):
        # Currently only (polytopes or singleton regions) and 1-D polytopes supported.
        if isinstance(P, pc.Region):
            assert len(P) == 1
            P = P[0]
        assert isinstance(P, pc.Polytope)
        V = pc.extreme(P)
        assert V.shape == (2,1) or V.shape == (1,2)
        return np.random.random((1,))*(V[1]-V[0]) + V[0]
    """

    f.write(aux_methods_str)

    f.write("""
    with open('""" + name + """.pickle', "rb") as f:
            sys_dyn, disc_dynamics = cPickle.load(f)

        self.sys_dyn = sys_dyn
        self.disc_dynamics = disc_dynamics
    """)

    f.write("""
import cPickle
import numpy as np
import polytope as pc
from tulip.abstract import find_controller
    """)

    return f.getvalue()


# The state machine name is fixed to be "ThermostatCtrl".
def preface(name="ThermostatCtrl"):
    """   @param name : give name of the XML UML Statechart """
    return """<?xml version='1.0' encoding='UTF-8'?>
<xmi:XMI xmi:version='2.1' xmlns:uml='http://schema.omg.org/spec/UML/2.2' xmlns:xmi='http://schema.omg.org/spec/XMI/2.1' xmlns:Non_Normative_Extensions='http://www.magicdraw.com/schemas/Non_Normative_Extensions.xmi' xmlns:ConstraintBlocks='http://www.magicdraw.com/schemas/ConstraintBlocks.xmi' xmlns:ModelElements='http://www.magicdraw.com/schemas/ModelElements.xmi' xmlns:Matrix_Templates_Profile='http://www.magicdraw.com/schemas/Matrix_Templates_Profile.xmi' xmlns:Allocations='http://www.magicdraw.com/schemas/Allocations.xmi' xmlns:UML_Standard_Profile='http://www.magicdraw.com/schemas/UML_Standard_Profile.xmi' xmlns:Activities='http://www.magicdraw.com/schemas/Activities.xmi' xmlns:MagicDraw_Profile='http://www.magicdraw.com/schemas/MagicDraw_Profile.xmi' xmlns:Ports_Flows='http://www.magicdraw.com/schemas/Ports_Flows.xmi' xmlns:SysML_Profile='http://www.magicdraw.com/schemas/SysML_Profile.xmi' xmlns:Requirements='http://www.magicdraw.com/schemas/Requirements.xmi' xmlns:Blocks='http://www.magicdraw.com/schemas/Blocks.xmi' xmlns:DSL_Customization='http://www.magicdraw.com/schemas/DSL_Customization.xmi' xmlns:Validation_Profile='http://www.magicdraw.com/schemas/Validation_Profile.xmi' xmlns:additional_stereotypes='http://www.magicdraw.com/schemas/additional_stereotypes.xmi'>
	<xmi:Documentation exporter='MagicDraw UML' exporterVersion='16.5'/>
	<xmi:Extension extender='MagicDraw UML 16.5'>
		<shareTable/>
		<mountTable>
			<module resource='file:/Applications/MagicDraw%2016.5%20SP3/MagicDraw%20UML/profiles/UML_Standard_Profile.xml' autoloadType='ALWAYS_LOAD' readOnly='true' loadIndex='false' requiredVersion='-1'>
				<mount mountPoint='magicdraw_uml_standard_profile_v_0001' mountedOn='eee_1045467100313_135436_1'/>
			</module>
			<module resource='file:/Applications/MagicDraw%2016.5%20SP3/MagicDraw%20UML/profiles/MD_customization_for_SysML.mdzip' autoloadType='ALWAYS_LOAD' readOnly='true' loadIndex='true' requiredVersion='-1'>
				<mount mountPoint='_12_0EAPbeta_be00301_1156851270584_552173_1' mountedOn='eee_1045467100313_135436_1'/>
			</module>
		</mountTable>
	</xmi:Extension>
	<uml:Model xmi:id='eee_1045467100313_135436_1' name='Data' visibility='public'>
		<xmi:Extension extender='MagicDraw UML 16.5'>
			<moduleExtension ignoredInModule='true'/>
		</xmi:Extension>
		<ownedComment xmi:type='uml:Comment' xmi:id='_16_5_3_63b0213_1256144971024_733598_327' body='Author:TuLiP.&#10;Created:(automatically generated)'>
			<annotatedElement xmi:idref='eee_1045467100313_135436_1'/>
		</ownedComment>
		<packagedElement xmi:type='uml:StateMachine' xmi:id='_16_5_3_63b0213_1256144996170_788400_3798' name='""" + str(
        name) + """' visibility='public'>
			<xmi:Extension extender='MagicDraw UML 16.5'>
				<modelExtension>
"""


def intermezzo4(name="ThermostatCtrl"):
    """ @param name: the name of the statechart, default is "ThermostaCtrl" """
    return """	</uml:Model>
	<xmi:Extension extender='MagicDraw UML 16.5'>
		<mdOwnedDiagrams>
			<mdElement elementClass='Diagram' xmi:id='_16_5_3_63b0213_1256144996145_937853_3796' name='""" + str(name) + """' visibility='public' context='_16_5_3_63b0213_1256144996170_788400_3798' ownerOfDiagram='_16_5_3_63b0213_1256144996170_788400_3798'>
				<mdElement elementClass='DiagramPresentationElement' xmi:id='_16_5_3_63b0213_1256144996148_220255_3797'>
					<elementID xmi:idref='_16_5_3_63b0213_1256144996145_937853_3796'/>
					<type>SysML State Machine Diagram</type>
					<umlType>State Machine Diagram</umlType>
					<zoomFactor xmi:value='1.0226951'/>
					<diagramOpened xmi:value='true'/>
					<diagramFrameInitialSizeSet xmi:value='true'/>
					<requiredFeature>com.nomagic.magicdraw.plugins.impl.sysml#SysML</requiredFeature>
					<diagramWindowBounds>2, 24, 1055, 770</diagramWindowBounds>
					<diagramScrollPositionX xmi:value='0'/>
					<diagramScrollPositionY xmi:value='0'/>
					<maximized xmi:value='false'/>
					<active xmi:value='false'/>
					<mdOwnedViews>
						<mdElement elementClass='DiagramFrame' xmi:id='_16_5_3_63b0213_1256144996195_302646_3811'>
							<elementID xmi:idref='_16_5_3_63b0213_1256144996145_937853_3796'/>
							<geometry>5, 5, 621, 688</geometry>
						</mdElement>
"""


INTERMEZZO1 = """				</modelExtension>
			</xmi:Extension>
"""

INTERMEZZO2 = """			<region xmi:type='uml:Region' xmi:id='_16_5_3_63b0213_1256144996175_697518_3799' visibility='public'>
"""

INTERMEZZO3 = """			</region>
		</packagedElement>
"""

POSTFACE = """</mdOwnedViews></mdElement></mdElement></mdOwnedDiagrams>
		<proxies/>
		<privateProxies>
			<proxy xmi:type='uml:Package' xmi:id='magicdraw_uml_standard_profile_v_0001' name='UML Standard Profile' visibility='public'>
				<xmi:Extension extender='MagicDraw UML 16.5'>
					<moduleExtension moduleRoot='::UML Standard Profile' moduleName='UML_Standard_Profile.xml' remoteProjectID='' remoteModuleVersion='1247746750000' moduleUsedByProject='true'/>
				</xmi:Extension>
				<packagedElement xmi:type='uml:Model' xmi:id='_9_0_be00301_1108053761194_467635_11463' name='UML2 Metamodel' visibility='public'>
					<packagedElement xmi:type='uml:Package' xmi:id='_9_0_62a020a_1105705080802_729520_11402' name='AuxiliaryConstructs' visibility='public'>
						<packagedElement xmi:type='uml:Package' xmi:id='_9_0_62a020a_1105705084263_818134_11536' name='Models' visibility='public'>
							<packagedElement xmi:type='uml:Class' xmi:id='_9_0_62a020a_1105704920340_825592_9329' name='Model' visibility='public'/>
						</packagedElement>
					</packagedElement>
					<packagedElement xmi:type='uml:Package' xmi:id='_9_0_62a020a_1105705064233_676383_11042' name='Classes' visibility='public'>
						<packagedElement xmi:type='uml:Package' xmi:id='_9_0_62a020a_1105705064323_957155_11049' name='Kernel' visibility='public'>
							<packagedElement xmi:type='uml:Class' xmi:id='_9_0_62a020a_1106296071977_61607_0' name='Diagram' visibility='public'>
								<xmi:Extension extender='MagicDraw UML 16.5'>
									<modelExtension/>
								</xmi:Extension>
							</packagedElement>
							<packagedElement xmi:type='uml:Class' xmi:id='_9_0_62a020a_1105704884807_371561_7741' name='Element' visibility='public'>
								<xmi:Extension extender='MagicDraw UML 16.5'>
									<modelExtension/>
								</xmi:Extension>
							</packagedElement>
							<packagedElement xmi:type='uml:Class' xmi:id='_9_0_62a020a_1105704885298_713292_7913' name='Package' visibility='public'/>
						</packagedElement>
					</packagedElement>
				</packagedElement>
				<packagedElement xmi:type='uml:Profile' xmi:id='_9_0_be00301_1108050582343_527400_10847' name='UML Standard Profile' visibility='public'>
					<packagedElement xmi:type='uml:Extension' xmi:id='_10_0EAPbeta_be00301_1123081771136_824883_97' visibility='public'>
						<memberEnd xmi:idref='_10_0EAPbeta_be00301_1123081771136_580423_99'/>
						<memberEnd xmi:idref='_10_0EAPbeta_be00301_1123081771136_271406_98'/>
						<ownedEnd xmi:type='uml:ExtensionEnd' xmi:id='_10_0EAPbeta_be00301_1123081771136_580423_99' name='extension_metamodel' visibility='private' aggregation='composite' type='magicdraw_1046861421236_601240_36'>
							<xmi:Extension extender='MagicDraw UML 16.5'>
								<modelExtension/>
							</xmi:Extension>
						</ownedEnd>
					</packagedElement>
					<packagedElement xmi:type='uml:Stereotype' xmi:id='magicdraw_1046861421236_601240_36' name='metamodel' visibility='public'>
						<ownedAttribute xmi:type='uml:Property' xmi:id='_10_0EAPbeta_be00301_1123081771136_271406_98' name='base_Model' visibility='private' type='_9_0_62a020a_1105704920340_825592_9329'/>
					</packagedElement>
				</packagedElement>
				<packagedElement xmi:type='uml:Profile' xmi:id='_be00301_1073394351331_445580_2' name='MagicDraw Profile' visibility='public'>
					<packagedElement xmi:type='uml:Extension' xmi:id='_10_0EAPbeta_be00301_1123081772498_531863_355' visibility='public'>
						<memberEnd xmi:idref='_10_0EAPbeta_be00301_1123081772498_435993_357'/>
						<memberEnd xmi:idref='_10_0EAPbeta_be00301_1123081772498_901864_356'/>
						<ownedEnd xmi:type='uml:ExtensionEnd' xmi:id='_10_0EAPbeta_be00301_1123081772498_435993_357' name='extension_DiagramInfo' visibility='private' aggregation='composite' type='_9_0_be00301_1108044380615_150487_0'>
							<xmi:Extension extender='MagicDraw UML 16.5'>
								<modelExtension/>
							</xmi:Extension>
						</ownedEnd>
					</packagedElement>
					<packagedElement xmi:type='uml:Extension' xmi:id='_10_0EAPbeta_be00301_1123081772098_323897_274' visibility='public'>
						<memberEnd xmi:idref='_10_0EAPbeta_be00301_1123081772108_624594_276'/>
						<memberEnd xmi:idref='_10_0EAPbeta_be00301_1123081772098_411862_275'/>
						<ownedEnd xmi:type='uml:ExtensionEnd' xmi:id='_10_0EAPbeta_be00301_1123081772108_624594_276' name='extension_InvisibleStereotype' visibility='private' aggregation='composite' type='_9_0_be00301_1108044721245_236588_411'>
							<xmi:Extension extender='MagicDraw UML 16.5'>
								<modelExtension/>
							</xmi:Extension>
						</ownedEnd>
					</packagedElement>
					<packagedElement xmi:type='uml:Extension' xmi:id='_12_1_8f90291_1173963939937_323574_98' visibility='public'>
						<memberEnd xmi:idref='_12_1_8f90291_1173963939937_399630_100'/>
						<memberEnd xmi:idref='_12_1_8f90291_1173963939937_52316_99'/>
						<ownedEnd xmi:type='uml:ExtensionEnd' xmi:id='_12_1_8f90291_1173963939937_399630_100' name='extension_auxiliaryResource' visibility='private' aggregation='composite' type='_12_1_8f90291_1173963323875_662612_98'>
							<xmi:Extension extender='MagicDraw UML 16.5'>
								<modelExtension/>
							</xmi:Extension>
						</ownedEnd>
					</packagedElement>
					<packagedElement xmi:type='uml:Stereotype' xmi:id='_9_0_be00301_1108044380615_150487_0' name='DiagramInfo' visibility='public'>
						<generalization xmi:type='uml:Generalization' xmi:id='_9_0_be00301_1108044989070_469307_436' general='_9_0_be00301_1108044721245_236588_411'/>
						<ownedAttribute xmi:type='uml:Property' xmi:id='_be00301_1073306188629_537791_2' name='Creation date' visibility='private'>
							<xmi:Extension extender='MagicDraw UML 16.5'>
								<modelExtension/>
							</xmi:Extension>
							<xmi:Extension extender='MagicDraw UML 16.5'>
								<modelExtension/>
							</xmi:Extension>
						</ownedAttribute>
						<ownedAttribute xmi:type='uml:Property' xmi:id='_be00301_1077726770128_871366_1' name='Author' visibility='private'>
							<xmi:Extension extender='MagicDraw UML 16.5'>
								<modelExtension/>
							</xmi:Extension>
							<xmi:Extension extender='MagicDraw UML 16.5'>
								<modelExtension/>
							</xmi:Extension>
						</ownedAttribute>
						<ownedAttribute xmi:type='uml:Property' xmi:id='_be00301_1073394345322_922552_1' name='Modification date' visibility='private'>
							<xmi:Extension extender='MagicDraw UML 16.5'>
								<modelExtension/>
							</xmi:Extension>
							<xmi:Extension extender='MagicDraw UML 16.5'>
								<modelExtension/>
							</xmi:Extension>
						</ownedAttribute>
						<ownedAttribute xmi:type='uml:Property' xmi:id='_10_0EAPbeta_be00301_1123081772498_901864_356' name='base_Diagram' visibility='private' type='_9_0_62a020a_1106296071977_61607_0'/>
					</packagedElement>
					<packagedElement xmi:type='uml:Stereotype' xmi:id='_9_0_be00301_1108044721245_236588_411' name='InvisibleStereotype' visibility='public'>
						<ownedAttribute xmi:type='uml:Property' xmi:id='_10_0EAPbeta_be00301_1123081772098_411862_275' name='base_Element' visibility='private' type='_9_0_62a020a_1105704884807_371561_7741'/>
					</packagedElement>
					<packagedElement xmi:type='uml:Stereotype' xmi:id='_12_1_8f90291_1173963323875_662612_98' name='auxiliaryResource' visibility='public'>
						<generalization xmi:type='uml:Generalization' xmi:id='_15_0_8f90291_1196866634537_680603_98' general='_9_0_be00301_1108044721245_236588_411'/>
						<ownedAttribute xmi:type='uml:Property' xmi:id='_12_1_8f90291_1173963939937_52316_99' name='base_Package' visibility='private' type='_9_0_62a020a_1105704885298_713292_7913'/>
					</packagedElement>
				</packagedElement>
			</proxy>
			<proxy xmi:type='uml:Package' xmi:id='_12_0EAPbeta_be00301_1156851270584_552173_1' name='MD Customization for SysML' visibility='public'>
				<xmi:Extension extender='MagicDraw UML 16.5'>
					<moduleExtension moduleRoot='::MD Customization for SysML' moduleName='MD_customization_for_SysML.mdzip' remoteProjectID='' remoteModuleVersion='1249931134000' moduleUsedByProject='true'/>
				</xmi:Extension>
			</proxy>
		</privateProxies>
		<stereotypeApplicationForProxies>
			<MagicDraw_Profile:auxiliaryResource xmi:id='_12_5EAPbeta2_be00301_1177500976392_281866_2496' base_Package='_12_0EAPbeta_be00301_1156851270584_552173_1'/>
			<UML_Standard_Profile:metamodel xmi:id='_10_0EAPbeta_be00301_1123081771126_233373_95' base_Model='_9_0_be00301_1108053761194_467635_11463'/>
			<MagicDraw_Profile:auxiliaryResource xmi:id='_12_1_8f90291_1174411598625_504587_98' base_Package='magicdraw_uml_standard_profile_v_0001'/>
		</stereotypeApplicationForProxies>
		<stereotypesIDS>
			<stereotype name='MagicDraw_Profile:DiagramInfo' stereotypeID='_9_0_be00301_1108044380615_150487_0'/>
			<tag name='MagicDraw_Profile:DiagramInfo:Creation_date' tagID='_be00301_1073306188629_537791_2'/>
			<tag name='MagicDraw_Profile:DiagramInfo:Author' tagID='_be00301_1077726770128_871366_1'/>
			<tag name='MagicDraw_Profile:DiagramInfo:Modification_date' tagID='_be00301_1073394345322_922552_1'/>
			<stereotype name='MagicDraw_Profile:auxiliaryResource' stereotypeID='_12_1_8f90291_1173963323875_662612_98'/>
			<stereotype name='UML_Standard_Profile:metamodel' stereotypeID='magicdraw_1046861421236_601240_36'/>
		</stereotypesIDS>
		<index/>
		<options>
			<mdElement elementClass='StyleManager'>
				<mdElement elementClass='SimpleStyle'>
					<name>STYLE_MODEL_ELEMENT_DEFAULTS</name>
					<default xmi:value='false'/>
				</mdElement>
				<mdElement elementClass='SimpleStyle'>
					<name>STYLE_USER_PROPERTIES</name>
					<default xmi:value='false'/>
					<mdElement elementClass='PropertyManager'>
						<name>PROJECT_GENERAL_PROPERTIES</name>
						<propertyManagerID>_16_5_3_63b0213_1269298986258_751344_3925</propertyManagerID>
						<mdElement elementClass='ClassPathListProperty'>
							<propertyID>MODULES_DIRS</propertyID>
							<propertyDescriptionID>MODULES_DIRS_DESCRIPTION</propertyDescriptionID>
							<mdElement elementClass='FileProperty'>
								<value>&lt;project.dir&gt;</value>
								<selectionMode xmi:value='0'/>
								<displayFullPath xmi:value='true'/>
								<useFilePreviewer xmi:value='false'/>
								<displayAllFiles xmi:value='true'/>
								<fileType>FILE_TYPE_ANY</fileType>
							</mdElement>
							<mdElement elementClass='FileProperty'>
								<value>&lt;install.root&gt;/profiles</value>
								<selectionMode xmi:value='0'/>
								<displayFullPath xmi:value='true'/>
								<useFilePreviewer xmi:value='false'/>
								<displayAllFiles xmi:value='true'/>
								<fileType>FILE_TYPE_ANY</fileType>
							</mdElement>
							<mdElement elementClass='FileProperty'>
								<value>&lt;install.root&gt;/modelLibraries</value>
								<selectionMode xmi:value='0'/>
								<displayFullPath xmi:value='true'/>
								<useFilePreviewer xmi:value='false'/>
								<displayAllFiles xmi:value='true'/>
								<fileType>FILE_TYPE_ANY</fileType>
							</mdElement>
							<allowFiles xmi:value='false'/>
						</mdElement>
						<mdElement elementClass='BooleanProperty'>
							<propertyID>SHOW_DOT_NOTATION_FOR_ASSOCIATIONS</propertyID>
							<propertyDescriptionID>SHOW_DOT_NOTATION_FOR_ASSOCIATIONS_DESCRIPTION</propertyDescriptionID>
						</mdElement>
						<mdElement elementClass='BooleanProperty'>
							<propertyID>CHANGE_OWNERSHIP_FOR_NAVIGABILITY</propertyID>
							<propertyDescriptionID>CHANGE_OWNERSHIP_FOR_NAVIGABILITY_DESCRIPTION</propertyDescriptionID>
							<value xmi:value='true'/>
						</mdElement>
						<mdElement elementClass='ChoiceProperty'>
							<propertyID>QNAME_DISPLAY_STYLE</propertyID>
							<propertyDescriptionID>QNAME_DISPLAY_STYLE_DESCRIPTION</propertyDescriptionID>
							<value>QNAME_DISPLAY_STYLE_RELATIVE</value>
							<choice xmi:value='QNAME_DISPLAY_STYLE_ABSOLUTE^QNAME_DISPLAY_STYLE_MODEL_RELATIVE^QNAME_DISPLAY_STYLE_RELATIVE^QNAME_DISPLAY_STYLE_MODEL_OR_LIBRARY_RELATIVE'/>
							<index xmi:value='2'/>
						</mdElement>
						<mdElement elementClass='BooleanProperty'>
							<propertyID>AUTO_SYNCHRONIZE_PARAMETERS_AND_ARGUMENTS</propertyID>
							<propertyDescriptionID>AUTO_SYNCHRONIZE_PARAMETERS_AND_ARGUMENTS_DESCRIPTION</propertyDescriptionID>
							<value xmi:value='true'/>
						</mdElement>
						<mdElement elementClass='ElementListProperty'>
							<propertyID>ACTIVE_VALIDATION_SCOPE</propertyID>
							<propertyGroup>ACTIVE_VALIDATION</propertyGroup>
							<displayableTypes xmi:value='Property^InteractionConstraint^Class^SendObjectAction^Relationship^SequenceNode^LiteralSpecification^ReclassifyObjectAction^TimeEvent^ClearVariableAction^BehavioralFeature^DataStoreNode^Region^FlowFinalNode^Realization^RemoveStructuralFeatureValueAction^Diagram^UnmarshallAction^ClearStructuralFeatureAction^ConditionalNode^ProtocolTransition^Feature^ConnectionPointReference^AssociationClass^ReadLinkAction^ActionExecutionSpecification^ProtocolStateMachine^BehavioredClassifier^ExceptionHandler^ActivityGroup^TimeInterval^Deployment^Variable^StateInvariant^Message^LiteralNull^LinkEndDestructionData^ReduceAction^OutputPin^Reception^TemplateParameter^CollaborationUse^ParameterSet^TemplateParameterSubstitution^AddVariableValueAction^InteractionOperand^InputPin^StartObjectBehaviorAction^RedefinableTemplateSignature^LiteralBoolean^SendSignalEvent^OpaqueExpression^Parameter^StructuralFeature^ReadExtentAction^InformationFlow^DataType^EnumerationLiteral^ComponentRealization^LinkAction^PackageImport^ChangeEvent^Abstraction^Node^NamedElement^Behavior^StructuredClassifier^LiteralInteger^ExecutionOccurrenceSpecification^ControlFlow^AcceptEventAction^SignalEvent^DecisionNode^Dependency^PartDecomposition^Generalization^CombinedFragment^TemplateSignature^Classifier^CentralBufferNode^Operation^FinalState^Interaction^Interval^Stereotype^LinkEndData^Duration^OccurrenceSpecification^IntervalConstraint^StructuredActivityNode^ExecutableNode^Include^Collaboration^OpaqueAction^CallEvent^InitialNode^OperationTemplateParameter^Component^MessageEnd^FunctionBehavior^ObjectNode^UseCase^CreateObjectAction^MergeNode^SendOperationEvent^Enumeration^Image^Constraint^AddStructuralFeatureValueAction^Vertex^ElementImport^DirectedRelationship^Expression^AcceptCallAction^WriteVariableAction^MessageEvent^InterfaceRealization^RaiseExceptionAction^TemplateableElement^Trigger^ValueSpecificationAction^Comment^RemoveVariableValueAction^ClassifierTemplateParameter^SendSignalAction^Connector^Actor^ExtensionPoint^ParameterableElement^LoopNode^ConnectableElement^CallBehaviorAction^StateMachine^Event^BehaviorExecutionSpecification^Transition^State^Slot^Usage^ValueSpecification^ActivityFinalNode^TestIdentityAction^OpaqueBehavior^Profile^InvocationAction^Model^ForkNode^ActivityPartition^ConsiderIgnoreFragment^MessageOccurrenceSpecification^TimeExpression^LinkEndCreationData^ActionInputPin^ProtocolConformance^LiteralString^DestroyLinkAction^ReadIsClassifiedObjectAction^Type^Action^ExecutionEnvironment^Artifact^DurationConstraint^Observation^WriteStructuralFeatureAction^ReadVariableAction^ExpansionRegion^Signal^AnyReceiveEvent^Extension^LiteralUnlimitedNatural^EncapsulatedClassifier^MultiplicityElement^StringExpression^PackageableElement^Substitution^ClearAssociationAction^Extend^GeneralizationSet^CreateLinkAction^JoinNode^Lifeline^InterruptibleActivityRegion^DeploymentTarget^InformationItem^TypedElement^CreateLinkObjectAction^ObjectFlow^TemplateBinding^GeneralOrdering^Package^ConnectableElementTemplateParameter^ReadStructuralFeatureAction^PackageMerge^ReceiveSignalEvent^InstanceValue^Continuation^Interface^ExecutionSpecification^PrimitiveType^StructuralFeatureAction^BroadcastSignalAction^CallAction^InstanceSpecification^Clause^FinalNode^ExtensionEnd^QualifierValue^Activity^Pin^InteractionUse^Gate^ValuePin^CallOperationAction^InteractionFragment^ReceiveOperationEvent^TimeObservation^ReadSelfAction^ElementValue^ControlNode^CommunicationPath^Port^DeploymentSpecification^DestructionEvent^ProfileApplication^ReadLinkObjectEndQualifierAction^Device^WriteLinkAction^DurationObservation^DeployedArtifact^ActivityEdge^DestroyObjectAction^RedefinableElement^CreationEvent^ActivityNode^ReplyAction^Namespace^Association^Manifestation^ConnectorEnd^VariableAction^DurationInterval^Pseudostate^ExpansionNode^StartClassifierBehaviorAction^ActivityParameterNode^TimeConstraint^ExecutionEvent^Element^ReadLinkObjectEndAction'/>
							<selectableTypes xmi:value='Property^InteractionConstraint^Class^SendObjectAction^Relationship^SequenceNode^LiteralSpecification^ReclassifyObjectAction^TimeEvent^ClearVariableAction^BehavioralFeature^DataStoreNode^Region^FlowFinalNode^Realization^RemoveStructuralFeatureValueAction^Diagram^UnmarshallAction^ClearStructuralFeatureAction^ConditionalNode^ProtocolTransition^Feature^ConnectionPointReference^AssociationClass^ReadLinkAction^ActionExecutionSpecification^ProtocolStateMachine^BehavioredClassifier^ExceptionHandler^ActivityGroup^TimeInterval^Deployment^Variable^StateInvariant^Message^LiteralNull^LinkEndDestructionData^ReduceAction^OutputPin^Reception^TemplateParameter^CollaborationUse^ParameterSet^TemplateParameterSubstitution^AddVariableValueAction^InteractionOperand^InputPin^StartObjectBehaviorAction^RedefinableTemplateSignature^LiteralBoolean^SendSignalEvent^OpaqueExpression^Parameter^StructuralFeature^ReadExtentAction^InformationFlow^DataType^EnumerationLiteral^ComponentRealization^LinkAction^PackageImport^ChangeEvent^Abstraction^Node^NamedElement^Behavior^StructuredClassifier^LiteralInteger^ExecutionOccurrenceSpecification^ControlFlow^AcceptEventAction^SignalEvent^DecisionNode^Dependency^PartDecomposition^Generalization^CombinedFragment^TemplateSignature^Classifier^CentralBufferNode^Operation^FinalState^Interaction^Interval^Stereotype^LinkEndData^Duration^OccurrenceSpecification^IntervalConstraint^StructuredActivityNode^ExecutableNode^Include^Collaboration^OpaqueAction^CallEvent^InitialNode^OperationTemplateParameter^Component^MessageEnd^FunctionBehavior^ObjectNode^UseCase^CreateObjectAction^MergeNode^SendOperationEvent^Enumeration^Image^Constraint^AddStructuralFeatureValueAction^Vertex^ElementImport^DirectedRelationship^Expression^AcceptCallAction^WriteVariableAction^MessageEvent^InterfaceRealization^RaiseExceptionAction^TemplateableElement^Trigger^ValueSpecificationAction^Comment^RemoveVariableValueAction^ClassifierTemplateParameter^SendSignalAction^Connector^Actor^ExtensionPoint^ParameterableElement^LoopNode^ConnectableElement^CallBehaviorAction^StateMachine^Event^BehaviorExecutionSpecification^Transition^State^Slot^Usage^ValueSpecification^ActivityFinalNode^TestIdentityAction^OpaqueBehavior^Profile^InvocationAction^Model^ForkNode^ActivityPartition^ConsiderIgnoreFragment^MessageOccurrenceSpecification^TimeExpression^LinkEndCreationData^ActionInputPin^ProtocolConformance^LiteralString^DestroyLinkAction^ReadIsClassifiedObjectAction^Type^Action^ExecutionEnvironment^Artifact^DurationConstraint^Observation^WriteStructuralFeatureAction^ReadVariableAction^ExpansionRegion^Signal^AnyReceiveEvent^Extension^LiteralUnlimitedNatural^EncapsulatedClassifier^MultiplicityElement^StringExpression^PackageableElement^Substitution^ClearAssociationAction^Extend^GeneralizationSet^CreateLinkAction^JoinNode^Lifeline^InterruptibleActivityRegion^DeploymentTarget^InformationItem^TypedElement^CreateLinkObjectAction^ObjectFlow^TemplateBinding^GeneralOrdering^Package^ConnectableElementTemplateParameter^ReadStructuralFeatureAction^PackageMerge^ReceiveSignalEvent^InstanceValue^Continuation^Interface^ExecutionSpecification^PrimitiveType^StructuralFeatureAction^BroadcastSignalAction^CallAction^InstanceSpecification^Clause^FinalNode^ExtensionEnd^QualifierValue^Activity^Pin^InteractionUse^Gate^ValuePin^CallOperationAction^InteractionFragment^ReceiveOperationEvent^TimeObservation^ReadSelfAction^ElementValue^ControlNode^CommunicationPath^Port^DeploymentSpecification^DestructionEvent^ProfileApplication^ReadLinkObjectEndQualifierAction^Device^WriteLinkAction^DurationObservation^DeployedArtifact^ActivityEdge^DestroyObjectAction^RedefinableElement^CreationEvent^ActivityNode^ReplyAction^Namespace^Association^Manifestation^ConnectorEnd^VariableAction^DurationInterval^Pseudostate^ExpansionNode^StartClassifierBehaviorAction^ActivityParameterNode^TimeConstraint^ExecutionEvent^Element^ReadLinkObjectEndAction'/>
							<containment xmi:value='true'/>
							<ordered xmi:value='false'/>
							<value>eee_1045467100313_135436_1</value>
						</mdElement>
						<mdElement elementClass='BooleanProperty'>
							<propertyID>ACTIVE_VALIDATION_EXCLUDE_ELEMENTS_FROM_READONLY_MODULES</propertyID>
							<propertyGroup>ACTIVE_VALIDATION</propertyGroup>
							<value xmi:value='true'/>
						</mdElement>
						<mdElement elementClass='BooleanProperty'>
							<propertyID>ACTIVE_VALIDATION_MARK_IN_MODEL</propertyID>
							<propertyGroup>ACTIVE_VALIDATION</propertyGroup>
							<value xmi:value='true'/>
						</mdElement>
						<mdElement elementClass='FileProperty'>
							<propertyID>EMF_UML2_OUTPUT_LOCATION</propertyID>
							<propertyGroup>General</propertyGroup>
							<propertyDescriptionID>EMF_UML2_OUTPUT_LOCATION_DESCRIPTION</propertyDescriptionID>
							<selectionMode xmi:value='1'/>
							<displayFullPath xmi:value='true'/>
							<useFilePreviewer xmi:value='false'/>
							<displayAllFiles xmi:value='true'/>
							<fileType>FILE_TYPE_ANY</fileType>
						</mdElement>
						<mdElement elementClass='BooleanProperty'>
							<propertyID>PROPAGATE_SYSML_VALUES</propertyID>
							<propertyGroup>SysML</propertyGroup>
							<propertyDescriptionID>PROPAGATE_SYSML_VALUES_DESCRIPTION</propertyDescriptionID>
							<value xmi:value='true'/>
						</mdElement>
						<mdElement elementClass='BooleanProperty'>
							<propertyID>ENABLE_SYSML_AUTO_REQUIREMENT_ID</propertyID>
							<propertyGroup>SysML</propertyGroup>
							<propertyDescriptionID>ENABLE_SYSML_AUTO_REQUIREMENT_ID_DESCRIPTION</propertyDescriptionID>
							<value xmi:value='true'/>
						</mdElement>
						<mdElement elementClass='ElementListProperty'>
							<propertyID>IGNORED_ACTIVE_VALIDATION_SUITES</propertyID>
							<propertyGroup>ACTIVE_VALIDATION</propertyGroup>
							<containment xmi:value='false'/>
							<ordered xmi:value='false'/>
						</mdElement>
						<mdElement elementClass='ElementProperty'>
							<propertyID>ACTIVE_VALIDATION_SEVERITY</propertyID>
							<propertyGroup>ACTIVE_VALIDATION</propertyGroup>
							<useUnspecified xmi:value='false'/>
							<containment xmi:value='false'/>
							<typeElement xmi:value='false'/>
							<parentApplicant xmi:value='false'/>
							<value>_11_5_f720368_1159529789933_567569_120</value>
						</mdElement>
					</mdElement>
					<mdElement elementClass='PropertyManager'>
						<name>PROJECT_INVISIBLE_PROPERTIES</name>
						<propertyManagerID>_16_5_3_63b0213_1269298986260_228972_3926</propertyManagerID>
						<mdElement elementClass='NumberProperty'>
							<propertyID>TOOL_TIP_STYLE</propertyID>
							<propertyDescriptionID>TOOL_TIP_STYLE_DESCRIPTION</propertyDescriptionID>
							<value xmi:value='0.0'/>
							<highRange xmi:value='2.0'/>
						</mdElement>
						<mdElement elementClass='NumberProperty'>
							<propertyID>LAST_INTERFACE_STYLE</propertyID>
							<propertyDescriptionID>LAST_INTERFACE_STYLE_DESCRIPTION</propertyDescriptionID>
							<value xmi:value='2.0'/>
							<highRange xmi:value='1.0'/>
						</mdElement>
						<mdElement elementClass='BooleanProperty'>
							<propertyID>IS_BROWSER_VISIBLE</propertyID>
							<propertyDescriptionID>IS_BROWSER_VISIBLE_DESCRIPTION</propertyDescriptionID>
							<value xmi:value='true'/>
						</mdElement>
						<mdElement elementClass='ChoiceProperty'>
							<propertyID>BROWSER_ITEM_TYPES</propertyID>
							<propertyDescriptionID>BROWSER_ITEM_TYPES_DESCRIPTION</propertyDescriptionID>
							<value></value>
							<choice xmi:value='LiteralString^LiteralBoolean^LiteralNull^LiteralInteger^LiteralUnlimitedNatural^Expression^OpaqueExpression^InstanceValue^StringExpression^ElementValue^Duration^DurationInterval^TimeInterval^TimeExpression^MessageOccurrenceSpecification^Gate^Image'/>
							<index xmi:value='-1'/>
						</mdElement>
						<mdElement elementClass='NumberProperty'>
							<propertyID>BROWSER_DIVIDER_LOCATION</propertyID>
							<propertyDescriptionID>BROWSER_DIVIDER_LOCATION_DESCRIPTION</propertyDescriptionID>
							<value xmi:value='-1.0'/>
							<lowRange xmi:value='-1.0'/>
						</mdElement>
						<mdElement elementClass='ChoiceProperty'>
							<propertyID>BROWSER_BOUNDS</propertyID>
							<propertyDescriptionID>BROWSER_BOUNDS_DESCRIPTION</propertyDescriptionID>
							<value></value>
							<choice xmi:value=''/>
							<index xmi:value='-1'/>
						</mdElement>
						<mdElement elementClass='BooleanProperty'>
							<propertyID>IS_DOCS_TAB_VISIBLE</propertyID>
							<propertyDescriptionID>IS_DOCS_TAB_VISIBLE_DESCRIPTION</propertyDescriptionID>
							<value xmi:value='true'/>
						</mdElement>
						<mdElement elementClass='StringProperty'>
							<propertyID>BROWSER_LAYOUT</propertyID>
							<propertyDescriptionID>BROWSER_LAYOUT_DESCRIPTION</propertyDescriptionID>
							<value>0 14 0 0 0 0 0 0 0 0 0 0 4 0 0 0 3 0 0 0 0 0 0 0 0 8 0 0 0 d 0 44 0 4f 0 43 0 55 0 4d 0 45 0 4e 0 54 0 41 0 54 0 49 0 4f 0 4e 0 0 34 4f 0 0 0 8 0 0 0 1 0 0 0 1 0 0 0 f 0 0 0 4 0 0 0 4 0 0 0 8 0 0 0 bb 0 0 0 0 0 0 0 c8 0 0 0 c8 ff ff ff ff ff ff ff ff 0 0 1 2c 0 0 1 11 0 0 0 0 0 0 0 1 0 0 0 4 0 0 34 4f 0 0 0 2 0 0 0 0 0 0 0 0 0 0 4 e5 0 0 3 20 0 0 0 8 0 0 0 0 0 0 1e 2c 0 0 0 3 0 0 74 bd 0 0 34 4f 0 0 3f fa 0 0 0 2 0 0 78 c1 0 0 1e 2c 0 0 0 0 0 0 0 2 0 0 70 cb 0 0 1e 2c 0 0 2c f1 0 0 78 c1 0 0 0 1 0 0 0 2 0 0 78 c1 0 0 d1 5e 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 d 0 44 0 49 0 41 0 47 0 52 0 41 0 4d 0 53 0 5f 0 54 0 52 0 45 0 45 0 0 73 66 0 0 0 8 0 0 0 0 0 0 0 1 0 0 0 f 0 0 0 4 0 0 0 4 0 0 0 8 0 0 0 bb 0 0 0 0 0 0 0 c8 0 0 0 c8 ff ff ff ff ff ff ff ff 0 0 1 2c 0 0 1 11 0 0 0 0 0 0 0 1 0 0 0 4 0 0 73 66 0 0 0 2 0 0 0 0 0 0 0 0 0 0 4 e5 0 0 3 20 0 0 0 8 0 0 0 0 0 0 70 cb 0 0 0 4 0 0 d2 8c 0 0 f0 7b 0 0 73 66 0 0 e 4a 0 0 0 2 0 0 78 c1 0 0 70 cb 0 0 0 0 0 0 0 2 0 0 70 cb 0 0 1e 2c 0 0 2c f1 0 0 78 c1 0 0 0 1 0 0 0 2 0 0 78 c1 0 0 d1 5e 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 c 0 5a 0 4f 0 4f 0 4d 0 5f 0 43 0 4f 0 4e 0 54 0 52 0 4f 0 4c 0 0 74 bd 0 0 0 8 0 0 0 1 0 0 0 1 0 0 0 f 0 0 0 4 0 0 0 4 0 0 0 8 0 0 0 bb 0 0 0 0 0 0 0 c8 0 0 0 c8 ff ff ff ff ff ff ff ff 0 0 1 2c 0 0 1 11 0 0 0 0 0 0 0 1 0 0 0 4 0 0 74 bd 0 0 0 2 0 0 0 0 0 0 0 0 0 0 4 e5 0 0 3 20 0 0 0 8 0 0 0 0 0 0 1e 2c 0 0 0 3 0 0 74 bd 0 0 34 4f 0 0 3f fa 0 0 0 2 0 0 78 c1 0 0 1e 2c 0 0 0 0 0 0 0 2 0 0 70 cb 0 0 1e 2c 0 0 2c f1 0 0 78 c1 0 0 0 1 0 0 0 2 0 0 78 c1 0 0 d1 5e 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 f 0 45 0 58 0 54 0 45 0 4e 0 53 0 49 0 4f 0 4e 0 53 0 5f 0 54 0 52 0 45 0 45 0 0 e 4a 0 0 0 8 0 0 0 0 0 0 0 1 0 0 0 f 0 0 0 4 0 0 0 4 0 0 0 8 0 0 0 bb 0 0 0 0 0 0 0 c8 0 0 0 c8 ff ff ff ff ff ff ff ff 0 0 1 2c 0 0 1 11 0 0 0 0 0 0 0 1 0 0 0 4 0 0 e 4a 0 0 0 2 0 0 0 0 0 0 0 0 0 0 4 e5 0 0 3 20 0 0 0 8 0 0 0 0 0 0 70 cb 0 0 0 4 0 0 d2 8c 0 0 f0 7b 0 0 73 66 0 0 e 4a 0 0 0 2 0 0 78 c1 0 0 70 cb 0 0 0 0 0 0 0 2 0 0 70 cb 0 0 1e 2c 0 0 2c f1 0 0 78 c1 0 0 0 1 0 0 0 2 0 0 78 c1 0 0 d1 5e 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 10 0 49 0 4e 0 48 0 45 0 52 0 49 0 54 0 41 0 4e 0 43 0 45 0 5f 0 54 0 52 0 45 0 45 0 0 f0 7b 0 0 0 8 0 0 0 0 0 0 0 1 0 0 0 f 0 0 0 4 0 0 0 4 0 0 0 8 0 0 0 bb 0 0 0 0 0 0 0 c8 0 0 0 c8 ff ff ff ff ff ff ff ff 0 0 1 2c 0 0 1 11 0 0 0 0 0 0 0 1 0 0 0 4 0 0 f0 7b 0 0 0 2 0 0 0 0 0 0 0 0 0 0 4 e5 0 0 3 20 0 0 0 8 0 0 0 0 0 0 70 cb 0 0 0 4 0 0 d2 8c 0 0 f0 7b 0 0 73 66 0 0 e 4a 0 0 0 2 0 0 78 c1 0 0 70 cb 0 0 0 0 0 0 0 2 0 0 70 cb 0 0 1e 2c 0 0 2c f1 0 0 78 c1 0 0 0 1 0 0 0 2 0 0 78 c1 0 0 d1 5e 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 f 0 4d 0 45 0 53 0 53 0 41 0 47 0 45 0 53 0 5f 0 57 0 49 0 4e 0 44 0 4f 0 57 0 0 f9 df 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 f 0 0 0 0 0 0 0 0 0 0 0 2 0 0 0 0 0 0 0 0 0 0 0 c8 0 0 0 c8 ff ff ff ff ff ff ff ff 0 0 1 2c 0 0 1 23 0 0 0 0 0 0 0 1 0 0 0 0 0 0 f9 df 0 0 0 0 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 a 0 50 0 52 0 4f 0 50 0 45 0 52 0 54 0 49 0 45 0 53 0 0 3f fa 0 0 0 8 0 0 0 1 0 0 0 1 0 0 0 f 0 0 0 4 0 0 0 4 0 0 0 8 0 0 0 bb 0 0 0 0 0 0 0 c8 0 0 0 c8 ff ff ff ff ff ff ff ff 0 0 1 2c 0 0 1 11 0 0 0 0 0 0 0 1 0 0 0 4 0 0 3f fa 0 0 0 2 0 0 0 0 0 0 0 0 0 0 4 e5 0 0 3 20 0 0 0 8 0 0 0 0 0 0 1e 2c 0 0 0 3 0 0 74 bd 0 0 34 4f 0 0 3f fa 0 0 0 2 0 0 78 c1 0 0 1e 2c 0 0 0 0 0 0 0 2 0 0 70 cb 0 0 1e 2c 0 0 2c f1 0 0 78 c1 0 0 0 1 0 0 0 2 0 0 78 c1 0 0 d1 5e 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 10 0 43 0 4f 0 4e 0 54 0 41 0 49 0 4e 0 4d 0 45 0 4e 0 54 0 5f 0 54 0 52 0 45 0 45 0 0 d2 8c 0 0 0 8 0 0 0 0 0 0 0 1 0 0 0 f 0 0 0 4 0 0 0 4 0 0 0 8 0 0 0 bb 0 0 0 0 0 0 0 c8 0 0 0 c8 ff ff ff ff ff ff ff ff 0 0 1 2c 0 0 1 11 0 0 0 0 0 0 0 1 0 0 0 4 0 0 d2 8c 0 0 0 2 0 0 0 0 0 0 0 0 0 0 4 e5 0 0 3 20 0 0 0 8 0 0 0 0 0 0 70 cb 0 0 0 4 0 0 d2 8c 0 0 f0 7b 0 0 73 66 0 0 e 4a 0 0 0 2 0 0 78 c1 0 0 70 cb 0 0 0 0 0 0 0 2 0 0 70 cb 0 0 1e 2c 0 0 2c f1 0 0 78 c1 0 0 0 1 0 0 0 2 0 0 78 c1 0 0 d1 5e 0 0 0 0 0 0 0 0 0 0 0 0 0 0 4 63 0 0 0 1 0 0 2c f1 0 0 0 0 2 0 0 4 63 0 0 0 0 0 0 78 c1 0 0 0 0 2 0 0 4 64 0 0 70 cb 0 0 0 4 0 0 4 65 0 0 0 10 0 43 0 4f 0 4e 0 54 0 41 0 49 0 4e 0 4d 0 45 0 4e 0 54 0 5f 0 54 0 52 0 45 0 45 0 0 4 65 0 0 0 10 0 49 0 4e 0 48 0 45 0 52 0 49 0 54 0 41 0 4e 0 43 0 45 0 5f 0 54 0 52 0 45 0 45 0 0 4 65 0 0 0 d 0 44 0 49 0 41 0 47 0 52 0 41 0 4d 0 53 0 5f 0 54 0 52 0 45 0 45 0 0 4 65 0 0 0 f 0 45 0 58 0 54 0 45 0 4e 0 53 0 49 0 4f 0 4e 0 53 0 5f 0 54 0 52 0 45 0 45 ff ff ff ff ff ff ff ff 0 0 0 0 0 0 4 64 0 0 1e 2c 0 0 0 3 0 0 4 65 0 0 0 c 0 5a 0 4f 0 4f 0 4d 0 5f 0 43 0 4f 0 4e 0 54 0 52 0 4f 0 4c 0 0 4 65 0 0 0 d 0 44 0 4f 0 43 0 55 0 4d 0 45 0 4e 0 54 0 41 0 54 0 49 0 4f 0 4e 0 0 4 65 0 0 0 a 0 50 0 52 0 4f 0 50 0 45 0 52 0 54 0 49 0 45 0 53 ff ff ff ff ff ff ff ff 0 0 0 0 0 0 0 bb 0 0 2 51 0 0 4 63 0 0 0 0 0 0 d1 5e 0 0 0 0 1 0 0 4 66 ff ff ff ff ff ff ff ff 0 0 0 0 0 0 4 27 0 0 0 e6 ff ff ff ff ff ff ff ff 0 0 0 3 0 0 0 0 0 0 0 7 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 5 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 f 0 4d 0 45 0 53 0 53 0 41 0 47 0 45 0 53 0 5f 0 57 0 49 0 4e 0 44 0 4f 0 57 0 0 0 0 </value>
						</mdElement>
						<mdElement elementClass='StringProperty'>
							<propertyID>LAYOUT_BEFORE_FULL_SCREEN</propertyID>
							<propertyDescriptionID>LAYOUT_BEFORE_FULL_SCREEN_DESCRIPTION</propertyDescriptionID>
						</mdElement>
						<mdElement elementClass='StringProperty'>
							<propertyID>LAYOUT_BEFORE_EXIT_FULL_SCREEN</propertyID>
							<propertyDescriptionID>LAYOUT_BEFORE_EXIT_FULL_SCREEN_DESCRIPTION</propertyDescriptionID>
							<value>0 14 0 0 0 0 0 0 0 0 0 0 4 0 0 0 3 0 0 0 0 0 0 0 0 1b 0 0 0 11 0 44 0 6f 0 44 0 41 0 46 0 20 0 54 0 56 0 20 0 44 0 69 0 61 0 67 0 72 0 61 0 6d 0 73 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 1 0 0 0 2 0 0 0 2 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 2 15 0 0 0 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 3 8d 0 0 0 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 11 0 44 0 6f 0 44 0 41 0 46 0 20 0 4f 0 56 0 20 0 44 0 69 0 61 0 67 0 72 0 61 0 6d 0 73 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 1 0 0 0 2 0 0 0 2 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 0 0 0 0 0 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 1 34 0 0 0 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 f 0 52 0 45 0 43 0 45 0 4e 0 54 0 5f 0 50 0 52 0 4f 0 4a 0 45 0 43 0 54 0 53 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 11 0 55 0 50 0 44 0 4d 0 20 0 53 0 4f 0 56 0 20 0 44 0 69 0 61 0 67 0 72 0 61 0 6d 0 73 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 1 0 0 0 2 0 0 0 2 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 2 bc 0 0 0 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 10 0 55 0 50 0 44 0 4d 0 20 0 4f 0 56 0 20 0 44 0 69 0 61 0 67 0 72 0 61 0 6d 0 73 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 1 0 0 0 2 0 0 0 2 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 1 b7 0 0 0 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 4 0 53 0 50 0 45 0 4d 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 1 0 0 0 2 0 0 0 2 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 0 0 0 0 0 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 18 0 43 0 55 0 53 0 54 0 4f 0 4d 0 5f 0 44 0 49 0 41 0 47 0 52 0 41 0 4d 0 53 0 5f 0 43 0 41 0 54 0 45 0 47 0 4f 0 52 0 59 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 2 ca 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1b 0 45 0 58 0 54 0 45 0 52 0 4e 0 41 0 4c 0 5f 0 54 0 4f 0 4f 0 4c 0 5f 0 41 0 43 0 54 0 49 0 4f 0 4e 0 53 0 5f 0 47 0 52 0 4f 0 55 0 50 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 1 0 0 0 2 0 0 0 2 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 0 0 0 0 0 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 8 0 44 0 49 0 41 0 47 0 52 0 41 0 4d 0 53 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 0 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 ff ff fe 66 0 0 0 94 0 0 6 1d 0 0 0 35 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 1 90 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 10 0 50 0 61 0 72 0 61 0 4d 0 61 0 67 0 69 0 63 0 54 0 6f 0 6f 0 6c 0 42 0 61 0 72 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 0 0 0 0 0 2 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 a 0 43 0 61 0 6d 0 65 0 6f 0 20 0 53 0 4f 0 41 0 2b 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 1 0 0 0 2 0 0 0 2 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 0 0 0 0 0 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 18 0 44 0 49 0 41 0 47 0 52 0 41 0 4d 0 5f 0 4e 0 41 0 56 0 49 0 47 0 41 0 54 0 49 0 4f 0 4e 0 5f 0 47 0 52 0 4f 0 55 0 50 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 4 9b 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1c 0 21 0 40 0 23 0 67 0 65 0 6e 0 65 0 72 0 61 0 74 0 65 0 64 0 49 0 44 0 49 0 44 0 30 0 30 0 30 0 30 0 30 0 30 0 30 0 30 0 30 0 37 0 38 0 31 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 0 0 0 0 2 0 0 0 2 0 0 0 1 0 0 0 0 0 0 0 0 0 0 1 b7 0 0 0 4f 0 0 0 95 0 0 0 30 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 1 7d 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 0 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 0 0 0 0 0 0 0 1 e7 0 0 0 e6 0 0 0 95 0 0 0 30 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 10 0 55 0 50 0 44 0 4d 0 20 0 53 0 56 0 20 0 44 0 69 0 61 0 67 0 72 0 61 0 6d 0 73 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 1 0 0 0 2 0 0 0 2 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 3 d5 0 0 0 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 10 0 55 0 50 0 44 0 4d 0 20 0 54 0 56 0 20 0 44 0 69 0 61 0 67 0 72 0 61 0 6d 0 73 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 1 0 0 0 2 0 0 0 2 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 1 e7 0 0 0 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 11 0 44 0 6f 0 44 0 41 0 46 0 20 0 53 0 56 0 20 0 44 0 69 0 61 0 67 0 72 0 61 0 6d 0 73 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 1 0 0 0 2 0 0 0 2 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 0 b9 0 0 0 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 1 f1 0 0 0 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 11 0 55 0 50 0 44 0 4d 0 20 0 41 0 63 0 56 0 20 0 44 0 69 0 61 0 67 0 72 0 61 0 6d 0 73 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 1 0 0 0 2 0 0 0 2 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 1 8a 0 0 0 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 18 0 46 0 55 0 4c 0 4c 0 5f 0 53 0 43 0 52 0 45 0 45 0 4e 0 5f 0 4d 0 4f 0 44 0 45 0 5f 0 54 0 4f 0 4f 0 4c 0 42 0 41 0 52 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 1 0 0 0 0 0 0 0 0 0 0 3 39 0 0 2 a1 0 0 0 75 0 0 0 2d 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 0 0 0 0 0 0 0 3 39 0 0 2 a1 0 0 0 75 0 0 0 2d 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 4 0 46 0 49 0 4c 0 45 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1c 0 21 0 40 0 23 0 67 0 65 0 6e 0 65 0 72 0 61 0 74 0 65 0 64 0 49 0 44 0 49 0 44 0 30 0 30 0 30 0 30 0 30 0 30 0 30 0 30 0 30 0 34 0 66 0 35 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 0 0 0 0 2 0 0 0 2 0 0 0 1 0 0 0 0 0 0 0 0 0 0 1 bb 0 0 0 38 0 0 0 be 0 0 0 30 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 1 ba 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 8 0 4d 0 65 0 6e 0 75 0 20 0 42 0 61 0 72 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 15 0 45 0 58 0 54 0 45 0 52 0 4e 0 41 0 4c 0 5f 0 54 0 4f 0 4f 0 4c 0 5f 0 41 0 43 0 54 0 49 0 4f 0 4e 0 53 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 8 0 54 0 45 0 41 0 4d 0 57 0 4f 0 52 0 4b 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 0 0 0 0 2 0 0 0 2 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 e5 0 0 0 5d 0 0 0 8a 0 0 0 2f 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 0 0 0 0 0 2 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 0 ed 0 0 0 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 f 0 53 0 59 0 53 0 4d 0 4f 0 44 0 20 0 44 0 69 0 61 0 67 0 72 0 61 0 6d 0 73 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 1 0 0 0 2 0 0 0 2 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 4 1b 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 11 0 55 0 50 0 44 0 4d 0 20 0 53 0 74 0 56 0 20 0 44 0 69 0 61 0 67 0 72 0 61 0 6d 0 73 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 1 0 0 0 2 0 0 0 2 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 0 a2 0 0 0 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 e 0 53 0 79 0 73 0 4d 0 4c 0 20 0 44 0 69 0 61 0 67 0 72 0 61 0 6d 0 73 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 4 8 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 e 0 44 0 6f 0 44 0 41 0 46 0 20 0 44 0 69 0 61 0 67 0 72 0 61 0 6d 0 73 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 1 0 0 0 2 0 0 0 2 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 2 0 0 0 0 0 0 0 1 0 0 0 3c 0 0 0 3c 0 0 0 c8 0 0 0 c8 0 0 0 f2 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 4 6a 0 0 0 3 0 0 0 0 0 0 4 6a 0 0 0 5 0 0 0 0 0 0 4 6a 0 0 0 7 0 0 0 0 0 0 4 6a 0 0 0 1 0 0 0 0 0 0 0 1 0 0 4 6c 0 0 3 39 0 0 2 a1 0 0 0 75 0 0 0 2d 0 0 0 1 0 0 4 6b 0 0 0 18 0 46 0 55 0 4c 0 4c 0 5f 0 53 0 43 0 52 0 45 0 45 0 4e 0 5f 0 4d 0 4f 0 44 0 45 0 5f 0 54 0 4f 0 4f 0 4c 0 42 0 41 0 52 0 0 0 0 </value>
						</mdElement>
						<mdElement elementClass='StringProperty'>
							<propertyID>DIAGRAMS_LAYOUT</propertyID>
							<propertyDescriptionID>DIAGRAMS_LAYOUT_DESCRIPTION</propertyDescriptionID>
							<value>0 0 0 14 0 0 0 1 0 0 0 29 0 5f 0 31 0 36 0 5f 0 35 0 5f 0 33 0 5f 0 36 0 33 0 62 0 30 0 32 0 31 0 33 0 5f 0 31 0 32 0 35 0 36 0 31 0 34 0 36 0 35 0 36 0 30 0 33 0 33 0 30 0 5f 0 39 0 30 0 30 0 33 0 30 0 30 0 5f 0 34 0 31 0 34 0 37 0 0 0 1 0 0 0 cc 0 0 0 e2 0 0 0 1 0 0 0 2 0 0 0 29 0 5f 0 31 0 36 0 5f 0 35 0 5f 0 33 0 5f 0 36 0 33 0 62 0 30 0 32 0 31 0 33 0 5f 0 31 0 32 0 35 0 36 0 31 0 34 0 34 0 39 0 39 0 36 0 31 0 34 0 35 0 5f 0 39 0 33 0 37 0 38 0 35 0 33 0 5f 0 33 0 37 0 39 0 36 0 0 0 29 0 5f 0 31 0 36 0 5f 0 35 0 5f 0 33 0 5f 0 36 0 33 0 62 0 30 0 32 0 31 0 33 0 5f 0 31 0 32 0 35 0 36 0 31 0 34 0 36 0 35 0 36 0 30 0 33 0 33 0 30 0 5f 0 39 0 30 0 30 0 33 0 30 0 30 0 5f 0 34 0 31 0 34 0 37 0 0 0 0 </value>
						</mdElement>
						<mdElement elementClass='StringProperty'>
							<propertyID>MT_LAST_SELECTED_TRANSFORMATION</propertyID>
							<propertyDescriptionID>MT_LAST_SELECTED_TRANSFORMATION_DESCRIPTION</propertyDescriptionID>
						</mdElement>
						<mdElement elementClass='BooleanProperty'>
							<propertyID>MT_TRANSFORMATION_IN_PLACE</propertyID>
							<propertyDescriptionID>MT_TRANSFORMATION_IN_PLACE_DESCRIPTION</propertyDescriptionID>
						</mdElement>
						<mdElement elementClass='ElementProperty'>
							<propertyID>MT_DESTINATION_PACKAGE</propertyID>
							<selectableTypes xmi:value=''/>
							<useUnspecified xmi:value='false'/>
							<containment xmi:value='false'/>
							<typeElement xmi:value='false'/>
							<parentApplicant xmi:value='false'/>
						</mdElement>
						<mdElement elementClass='StringProperty'>
							<propertyID>MT_LAST_SELECTED_TYPE_MAP_PROFILE</propertyID>
							<propertyDescriptionID>MT_LAST_SELECTED_TYPE_MAP_PROFILE_DESCRIPTION</propertyDescriptionID>
						</mdElement>
						<mdElement elementClass='BooleanProperty'>
							<propertyID>MT_LAST_SELECTED_TYPE_MAP_PROFILE_DIRECTION</propertyID>
							<propertyDescriptionID>MT_LAST_SELECTED_TYPE_MAP_PROFILE_DIRECTION_DESCRIPTION</propertyDescriptionID>
							<value xmi:value='true'/>
						</mdElement>
						<mdElement elementClass='NumberProperty'>
							<propertyID>INDEX_MODE</propertyID>
							<propertyDescriptionID>INDEX_MODE_DESCRIPTION</propertyDescriptionID>
							<value xmi:value='0.0'/>
						</mdElement>
						<mdElement elementClass='BooleanProperty'>
							<propertyID>INDEX_SCOPE_ALL</propertyID>
							<propertyDescriptionID>INDEX_SCOPE_ALL_DESCRIPTION</propertyDescriptionID>
						</mdElement>
						<mdElement elementClass='ElementListProperty'>
							<propertyID>INDEX_SCOPE</propertyID>
							<displayableTypes xmi:value=''/>
							<selectableTypes xmi:value=''/>
							<containment xmi:value='false'/>
							<ordered xmi:value='false'/>
						</mdElement>
						<mdElement elementClass='ElementProperty'>
							<propertyID>INDEX_TYPES</propertyID>
							<selectableTypes xmi:value=''/>
							<useUnspecified xmi:value='false'/>
							<containment xmi:value='false'/>
							<typeElement xmi:value='false'/>
							<parentApplicant xmi:value='false'/>
						</mdElement>
						<mdElement elementClass='StringProperty'>
							<propertyID>LAST_SELECTED_MODULE_PATH</propertyID>
							<propertyDescriptionID>LAST_SELECTED_MODULE_PATH_DESCRIPTION</propertyDescriptionID>
						</mdElement>
						<mdElement elementClass='BooleanProperty'>
							<propertyID>DIAGRAM_INFO_CUSTOM_MODE</propertyID>
							<propertyDescriptionID>DIAGRAM_INFO_CUSTOM_MODE_DESCRIPTION</propertyDescriptionID>
						</mdElement>
						<mdElement elementClass='LIST_PROPERTY'>
							<propertyID>DIAGRAM_INFO_SELECTED_KEYWORDS</propertyID>
							<propertyDescriptionID>DIAGRAM_INFO_SELECTED_KEYWORDS_DESCRIPTION</propertyDescriptionID>
							<value>Diagram name</value>
							<value>Author</value>
							<value>Creation date</value>
							<value>Modification date</value>
						</mdElement>
						<mdElement elementClass='StringProperty'>
							<propertyID>DIAGRAM_INFO_CUSTOM_HTML</propertyID>
							<propertyDescriptionID>DIAGRAM_INFO_CUSTOM_HTML_DESCRIPTION</propertyDescriptionID>
							<value></value>
						</mdElement>
						<mdElement elementClass='StringProperty'>
							<propertyID>INFO_PROPERTY</propertyID>
							<propertyDescriptionID>INFO_PROPERTY_DESCRIPTION</propertyDescriptionID>
							<value>21 69 5f 4 1f 67 2 3 11 60 2f 1d 32 b3 6 ea ea 5f 9d 48 fd 38 88 c0 7c dd 42 9b d1 e3 49 4a ec 6b 1c 22 e1 c6 9b db 9a 94 2c ef 53 d3 4f 8a 88 f8 f7 8f ac e9 54 b7 61 a7 a6 6e 33 c7 a7 47 cd 87 ee 51 c2 </value>
						</mdElement>
						<mdElement elementClass='LIST_PROPERTY'>
							<propertyID>ADDITIONAL_CONTAINMENT_TREES</propertyID>
							<propertyDescriptionID>ADDITIONAL_CONTAINMENT_TREES_DESCRIPTION</propertyDescriptionID>
						</mdElement>
						<mdElement elementClass='StringProperty'>
							<propertyID>LAST_DIRECTORY</propertyID>
							<propertyDescriptionID>LAST_DIRECTORY_DESCRIPTION</propertyDescriptionID>
							<value></value>
						</mdElement>
						<mdElement elementClass='NumberProperty'>
							<propertyID>OutputTypeSelectionPanel.value</propertyID>
							<propertyDescriptionID>OutputTypeSelectionPanel.value_DESCRIPTION</propertyDescriptionID>
							<value xmi:value='0.0'/>
							<highRange xmi:value='10.0'/>
						</mdElement>
						<mdElement elementClass='LIST_PROPERTY'>
							<propertyID>IGNORED_CONSTRAINT_PROPERTY</propertyID>
						</mdElement>
						<mdElement elementClass='StringProperty'>
							<propertyID>ACTIVE_VALIDATION_IGNORED_OPTION</propertyID>
							<propertyGroup>ACTIVE_VALIDATION</propertyGroup>
							<propertyDescriptionID>ACTIVE_VALIDATION_IGNORED_OPTION_DESCRIPTION</propertyDescriptionID>
						</mdElement>
						<mdElement elementClass='LIST_PROPERTY'>
							<propertyID>SPELL_IGNORE_LIST</propertyID>
							<propertyDescriptionID>SPELL_IGNORE_LIST_DESCRIPTION</propertyDescriptionID>
							<value>MagicDrawUML</value>
						</mdElement>
						<mdElement elementClass='ChoiceProperty'>
							<propertyID>RECENT_DIAGRAMS</propertyID>
							<propertyDescriptionID>RECENT_DIAGRAMS_DESCRIPTION</propertyDescriptionID>
							<choice xmi:value=''/>
							<index xmi:value='-1'/>
						</mdElement>
					</mdElement>
				</mdElement>
			</mdElement>
		</options>
		<favoriteElements xmi:value=''/>
		<dataTypes xmi:idref='_9_0_2_be00301_1111670217596_336168_627'/>
		<moduleID>Project Simple1</moduleID>
		<mdElement elementClass='StyleManager'>
			<mdElement elementClass='SimpleStyle'>
				<name>Default</name>
				<default xmi:value='true'/>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Abstraction</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986264_201903_3927</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_A</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_A_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_B</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_B_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>AcceptEventAction</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986264_763130_3929</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-1973821'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-6710948'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>DIRECTION</propertyID>
						<propertyDescriptionID>DIRECTION_DESCRIPTION</propertyDescriptionID>
						<value>LEFT</value>
						<choice xmi:value='RIGHT^LEFT'/>
						<index xmi:value='1'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Action</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986264_987335_3931</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-1973821'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-6710948'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>ActivityParameterNode</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986265_602518_3932</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-1973821'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-6710948'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OBJECT_CLASS</propertyID>
						<propertyDescriptionID>SHOW_OBJECT_CLASS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_FULL_TYPE</propertyID>
						<propertyDescriptionID>SHOW_FULL_TYPE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_STATE</propertyID>
						<propertyDescriptionID>SHOW_STATE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_PROPERTIES</propertyID>
						<propertyDescriptionID>SHOW_PROPERTIES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SHOW_ACTIVITY_PARAMETER_NODE_NAME_PROPERTY</propertyID>
						<propertyDescriptionID>SHOW_ACTIVITY_PARAMETER_NODE_NAME_PROPERTY_DESCRIPTION</propertyDescriptionID>
						<value>SHOW_PARAMETER_NAME</value>
						<choice xmi:value='SHOW_PARAMETER_NAME^SHOW_NAME'/>
						<index xmi:value='0'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Actor</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986265_62570_3933</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-10066361'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>TAGGED_VALUES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>TAGGED_VALUES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>ON_SHAPE</value>
						<choice xmi:value='ON_SHAPE^IN_COMPARTMENT^DO_NOT_DISPLAY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='3'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES_STEREOTYPES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_STEREOTYPES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_QUALIFIED_NAME_IN_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_QUALIFIED_NAME_IN_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Artifact</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986265_384633_3934</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-13159'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-6719140'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='3'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SHOW_MEMBERS_MODE</propertyID>
						<propertyDescriptionID>SHOW_MEMBERS_MODE_DESCRIPTION</propertyDescriptionID>
						<value>ALL</value>
						<choice xmi:value='ALL^ONLY_PUBLIC^NOT_PRIVATE'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_CLASS_ATTRIBUTES</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SUPPRESS_CLASS_ATTRIBUTES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>ATTRIBUTE_COLOR</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>ATTRIBUTE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-14155776'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>ATTRIBUTE_FONT</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>ATTRIBUTE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_MORE_SIGN_FOR_ATTRIBUTES</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_MORE_SIGN_FOR_ATTRIBUTES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SORT_CLASS_ATTRIBUTES_MODE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SORT_CLASS_ATTRIBUTES_MODE_DESCRIPTION</propertyDescriptionID>
						<value>NO_SORT</value>
						<choice xmi:value='NO_SORT^BY_NAME^BY_STEREOTYPE^BY_VISIBILITY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SHOW_ASSOCIATION_ENDS_MODE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ASSOCIATION_ENDS_MODE_DESCRIPTION</propertyDescriptionID>
						<value>DO_NOT_DISPLAY</value>
						<choice xmi:value='ALL^WITHOUT_ASSOCIATION^DO_NOT_DISPLAY'/>
						<index xmi:value='2'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_VISIBILITY</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_VISIBILITY_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_TYPE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_TYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_STEREOTYPE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_STEREOTYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_PROPERTIES</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_PROPERTIES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_CONSTRAINTS</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>ATTRIBUTES_CONSTRAINT_TEXT_MODE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>ATTRIBUTES_CONSTRAINT_TEXT_MODE_DESCRIPTION</propertyDescriptionID>
						<value>EXPRESSION_MODE</value>
						<choice xmi:value='NAME_MODE^EXPRESSION_MODE^NAME_EXPRESSION_MODE'/>
						<index xmi:value='1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_INIT_VALUE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_INIT_VALUE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_CLASS_OPERATIONS</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SUPPRESS_CLASS_OPERATIONS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>OPERATION_COLOR</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>OPERATION_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777176'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>OPERATION_FONT</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>OPERATION_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_SIGNATURE</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_SIGNATURE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_MORE_SIGN_FOR_OPERATIONS</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_MORE_SIGN_FOR_OPERATIONS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SORT_CLASS_OPERATIONS_MODE</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SORT_CLASS_OPERATIONS_MODE_DESCRIPTION</propertyDescriptionID>
						<value>NO_SORT</value>
						<choice xmi:value='NO_SORT^BY_NAME^BY_STEREOTYPE^BY_VISIBILITY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_VISIBILITY</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_VISIBILITY_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_STEREOTYPE</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_STEREOTYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_PROPERTIES</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_PROPERTIES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_CONSTRAINTS</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>OPERATIONS_CONSTRAINT_TEXT_MODE</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>OPERATIONS_CONSTRAINT_TEXT_MODE_DESCRIPTION</propertyDescriptionID>
						<value>EXPRESSION_MODE</value>
						<choice xmi:value='NAME_MODE^EXPRESSION_MODE^NAME_EXPRESSION_MODE'/>
						<index xmi:value='1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_FULL_TYPE</propertyID>
						<propertyDescriptionID>SHOW_FULL_TYPE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_PARAMETERS_DIRECTION_KIND</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_PARAMETERS_DIRECTION_KIND_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>TAGGED_VALUES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>TAGGED_VALUES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>ON_SHAPE</value>
						<choice xmi:value='ON_SHAPE^IN_COMPARTMENT^DO_NOT_DISPLAY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES_STEREOTYPES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_STEREOTYPES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_QUALIFIED_NAME_IN_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_QUALIFIED_NAME_IN_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>MEMBERS_WORD_WRAP</propertyID>
						<propertyDescriptionID>MEMBERS_WORD_WRAP_DESCRIPTION</propertyDescriptionID>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Association</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986267_647387_3935</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_A</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_A_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_B</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_B_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ASSOCIATION_DIRECTION_ICON</propertyID>
						<propertyDescriptionID>SHOW_ASSOCIATION_DIRECTION_ICON_DESCRIPTION</propertyDescriptionID>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>AssociationClass</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986267_1045_3936</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_A</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_A_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_B</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_B_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ASSOCIATION_DIRECTION_ICON</propertyID>
						<propertyDescriptionID>SHOW_ASSOCIATION_DIRECTION_ICON_DESCRIPTION</propertyDescriptionID>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>CallBehaviorAction</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986267_420239_3937</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-1973821'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-6710948'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>CALL_BEHAVIOR_ACTION_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>CALL_BEHAVIOR_ACTION_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>SHOW_BOTH</value>
						<choice xmi:value='SHOW_ACTION_NAME^SHOW_BEHAVIOR_NAME^SHOW_BOTH'/>
						<index xmi:value='2'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>CallOperationAction</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986272_457318_3938</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-1973821'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-6710948'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_QUALIFIED_NAME_FOR_OPERATIONS</propertyID>
						<propertyDescriptionID>SHOW_QUALIFIED_NAME_FOR_OPERATIONS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>CentralBufferNode</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986272_307472_3939</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-1973821'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-6710948'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OBJECT_CLASS</propertyID>
						<propertyDescriptionID>SHOW_OBJECT_CLASS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_FULL_TYPE</propertyID>
						<propertyDescriptionID>SHOW_FULL_TYPE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='5'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_STATE</propertyID>
						<propertyDescriptionID>SHOW_STATE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Class</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986272_20961_3940</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-13159'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-6719140'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='3'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SHOW_MEMBERS_MODE</propertyID>
						<propertyDescriptionID>SHOW_MEMBERS_MODE_DESCRIPTION</propertyDescriptionID>
						<value>ALL</value>
						<choice xmi:value='ALL^ONLY_PUBLIC^NOT_PRIVATE'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_CLASS_ATTRIBUTES</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SUPPRESS_CLASS_ATTRIBUTES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>ATTRIBUTE_COLOR</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>ATTRIBUTE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-14155776'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>ATTRIBUTE_FONT</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>ATTRIBUTE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_MORE_SIGN_FOR_ATTRIBUTES</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_MORE_SIGN_FOR_ATTRIBUTES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SORT_CLASS_ATTRIBUTES_MODE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SORT_CLASS_ATTRIBUTES_MODE_DESCRIPTION</propertyDescriptionID>
						<value>NO_SORT</value>
						<choice xmi:value='NO_SORT^BY_NAME^BY_STEREOTYPE^BY_VISIBILITY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SHOW_ASSOCIATION_ENDS_MODE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ASSOCIATION_ENDS_MODE_DESCRIPTION</propertyDescriptionID>
						<value>DO_NOT_DISPLAY</value>
						<choice xmi:value='ALL^WITHOUT_ASSOCIATION^DO_NOT_DISPLAY'/>
						<index xmi:value='2'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_VISIBILITY</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_VISIBILITY_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_TYPE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_TYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_STEREOTYPE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_STEREOTYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_PROPERTIES</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_PROPERTIES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_CONSTRAINTS</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>ATTRIBUTES_CONSTRAINT_TEXT_MODE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>ATTRIBUTES_CONSTRAINT_TEXT_MODE_DESCRIPTION</propertyDescriptionID>
						<value>EXPRESSION_MODE</value>
						<choice xmi:value='NAME_MODE^EXPRESSION_MODE^NAME_EXPRESSION_MODE'/>
						<index xmi:value='1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_INIT_VALUE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_INIT_VALUE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_CLASS_OPERATIONS</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SUPPRESS_CLASS_OPERATIONS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>OPERATION_COLOR</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>OPERATION_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777176'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>OPERATION_FONT</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>OPERATION_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_SIGNATURE</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_SIGNATURE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_MORE_SIGN_FOR_OPERATIONS</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_MORE_SIGN_FOR_OPERATIONS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SORT_CLASS_OPERATIONS_MODE</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SORT_CLASS_OPERATIONS_MODE_DESCRIPTION</propertyDescriptionID>
						<value>NO_SORT</value>
						<choice xmi:value='NO_SORT^BY_NAME^BY_STEREOTYPE^BY_VISIBILITY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_VISIBILITY</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_VISIBILITY_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_STEREOTYPE</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_STEREOTYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_PROPERTIES</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_PROPERTIES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_CONSTRAINTS</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>OPERATIONS_CONSTRAINT_TEXT_MODE</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>OPERATIONS_CONSTRAINT_TEXT_MODE_DESCRIPTION</propertyDescriptionID>
						<value>EXPRESSION_MODE</value>
						<choice xmi:value='NAME_MODE^EXPRESSION_MODE^NAME_EXPRESSION_MODE'/>
						<index xmi:value='1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_FULL_TYPE</propertyID>
						<propertyDescriptionID>SHOW_FULL_TYPE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_PARAMETERS_DIRECTION_KIND</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_PARAMETERS_DIRECTION_KIND_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>TAGGED_VALUES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>TAGGED_VALUES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>ON_SHAPE</value>
						<choice xmi:value='ON_SHAPE^IN_COMPARTMENT^DO_NOT_DISPLAY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES_STEREOTYPES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_STEREOTYPES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_QUALIFIED_NAME_IN_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_QUALIFIED_NAME_IN_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>MEMBERS_WORD_WRAP</propertyID>
						<propertyDescriptionID>MEMBERS_WORD_WRAP_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_CLASS_PORTS</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>SUPPRESS_CLASS_PORTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PORTS_COLOR</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>PORTS_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-14155776'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>PORTS_FONT</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>PORTS_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_MORE_SIGN_FOR_PORTS</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>SHOW_MORE_SIGN_FOR_PORTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SORT_CLASS_PORT_MODE</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>SORT_CLASS_PORT_MODE_DESCRIPTION</propertyDescriptionID>
						<value>NO_SORT</value>
						<choice xmi:value='NO_SORT^BY_NAME^BY_STEREOTYPE^BY_VISIBILITY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_PORTS_VISIBILITY</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>SHOW_PORTS_VISIBILITY_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_PORTS_TYPE</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>SHOW_PORTS_TYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_PORTS_STEREOTYPE</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>SHOW_PORTS_STEREOTYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_PORTS_PROPERTIES</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>SHOW_PORTS_PROPERTIES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_PORTS_CONSTRAINTS</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>SHOW_PORTS_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>PORTS_CONSTRAINTS_TEXT_MODE</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>PORTS_CONSTRAINTS_TEXT_MODE_DESCRIPTION</propertyDescriptionID>
						<value>EXPRESSION_MODE</value>
						<choice xmi:value='NAME_MODE^EXPRESSION_MODE^NAME_EXPRESSION_MODE'/>
						<index xmi:value='1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_INIT_PORTS_VALUE</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>SHOW_INIT_PORTS_VALUE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_SIGNAL_RECEPTIONS</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SUPPRESS_SIGNAL_RECEPTIONS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>RECEPTION_COLOR</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>RECEPTION_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777176'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>RECEPTION_FONT</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>RECEPTION_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_SIGNAL_RECEPTIONS_SIGNATURE</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SHOW_SIGNAL_RECEPTIONS_SIGNATURE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_MORE_SIGN_FOR_RECEPTIONS</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SHOW_MORE_SIGN_FOR_RECEPTIONS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SORT_CLASS_RECEPTIONS_MODE</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SORT_CLASS_RECEPTIONS_MODE_DESCRIPTION</propertyDescriptionID>
						<value>NO_SORT</value>
						<choice xmi:value='NO_SORT^BY_SIGNAL_NAME^BY_STEREOTYPE^BY_VISIBILITY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_SIGNAL_RECEPTIONS_VISIBILITY</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SHOW_SIGNAL_RECEPTIONS_VISIBILITY_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_RECEPTIONS_STEREOTYPES</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SHOW_RECEPTIONS_STEREOTYPES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_RECEPTIONS_PROPERTIES</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SHOW_RECEPTIONS_PROPERTIES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_RECEPTIONS_CONSTRAINTS</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SHOW_RECEPTIONS_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>RECEPTIONS_CONSTRAINTS_TEXT_MODE</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>RECEPTIONS_CONSTRAINTS_TEXT_MODE_DESCRIPTION</propertyDescriptionID>
						<value>EXPRESSION_MODE</value>
						<choice xmi:value='NAME_MODE^EXPRESSION_MODE^NAME_EXPRESSION_MODE'/>
						<index xmi:value='1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_RECEPTIONS_PARAMETERS_DIRECTION_KIND</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SHOW_RECEPTIONS_PARAMETERS_DIRECTION_KIND_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_STRUCTURE</propertyID>
						<propertyDescriptionID>SUPPRESS_STRUCTURE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SORT_SYSML_STYLE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SORT_SYSML_STYLE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Collaboration</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986274_307820_3941</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-11712978'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_STRUCTURE</propertyID>
						<propertyDescriptionID>SUPPRESS_STRUCTURE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-3916'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>CollaborationUse</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986274_647428_3942</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-11712978'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OBJECT_CLASS</propertyID>
						<propertyDescriptionID>SHOW_OBJECT_CLASS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_FULL_TYPE</propertyID>
						<propertyDescriptionID>SHOW_FULL_TYPE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-3916'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>CombinedFragment</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986274_180343_3943</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>USE_FILL_COLOR</propertyID>
						<propertyDescriptionID>USE_FILL_COLOR_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='3'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>OWNER_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>OWNER_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>QNAME_DISPLAY_MODE_DO_NOT_DISPLAY</value>
						<choice xmi:value='QNAME_DISPLAY_MODE_DO_NOT_DISPLAY^OWNER_DISPLAY_MODE_STD^OWNER_DISPLAY_MODE_OLD'/>
						<index xmi:value='0'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Comment</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986274_317934_3944</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>OWNER_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>OWNER_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>QNAME_DISPLAY_MODE_DO_NOT_DISPLAY</value>
						<choice xmi:value='QNAME_DISPLAY_MODE_DO_NOT_DISPLAY^OWNER_DISPLAY_MODE_STD^OWNER_DISPLAY_MODE_OLD'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>HTML_TEXT</propertyID>
						<propertyDescriptionID>HTML_TEXT_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-723724'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>CommunicationPath</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986275_687519_3945</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_A</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_A_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_B</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_B_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ASSOCIATION_DIRECTION_ICON</propertyID>
						<propertyDescriptionID>SHOW_ASSOCIATION_DIRECTION_ICON_DESCRIPTION</propertyDescriptionID>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Component</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986276_215905_3946</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-6710948'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='3'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SHOW_MEMBERS_MODE</propertyID>
						<propertyDescriptionID>SHOW_MEMBERS_MODE_DESCRIPTION</propertyDescriptionID>
						<value>ALL</value>
						<choice xmi:value='ALL^ONLY_PUBLIC^NOT_PRIVATE'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_CLASS_ATTRIBUTES</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SUPPRESS_CLASS_ATTRIBUTES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>ATTRIBUTE_COLOR</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>ATTRIBUTE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-14155776'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>ATTRIBUTE_FONT</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>ATTRIBUTE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_MORE_SIGN_FOR_ATTRIBUTES</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_MORE_SIGN_FOR_ATTRIBUTES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SORT_CLASS_ATTRIBUTES_MODE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SORT_CLASS_ATTRIBUTES_MODE_DESCRIPTION</propertyDescriptionID>
						<value>NO_SORT</value>
						<choice xmi:value='NO_SORT^BY_NAME^BY_STEREOTYPE^BY_VISIBILITY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SHOW_ASSOCIATION_ENDS_MODE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ASSOCIATION_ENDS_MODE_DESCRIPTION</propertyDescriptionID>
						<value>DO_NOT_DISPLAY</value>
						<choice xmi:value='ALL^WITHOUT_ASSOCIATION^DO_NOT_DISPLAY'/>
						<index xmi:value='2'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_VISIBILITY</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_VISIBILITY_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_TYPE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_TYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_STEREOTYPE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_STEREOTYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_PROPERTIES</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_PROPERTIES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_CONSTRAINTS</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>ATTRIBUTES_CONSTRAINT_TEXT_MODE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>ATTRIBUTES_CONSTRAINT_TEXT_MODE_DESCRIPTION</propertyDescriptionID>
						<value>EXPRESSION_MODE</value>
						<choice xmi:value='NAME_MODE^EXPRESSION_MODE^NAME_EXPRESSION_MODE'/>
						<index xmi:value='1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_INIT_VALUE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_INIT_VALUE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_CLASS_OPERATIONS</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SUPPRESS_CLASS_OPERATIONS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>OPERATION_COLOR</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>OPERATION_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777176'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>OPERATION_FONT</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>OPERATION_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_SIGNATURE</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_SIGNATURE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_MORE_SIGN_FOR_OPERATIONS</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_MORE_SIGN_FOR_OPERATIONS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SORT_CLASS_OPERATIONS_MODE</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SORT_CLASS_OPERATIONS_MODE_DESCRIPTION</propertyDescriptionID>
						<value>NO_SORT</value>
						<choice xmi:value='NO_SORT^BY_NAME^BY_STEREOTYPE^BY_VISIBILITY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_VISIBILITY</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_VISIBILITY_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_STEREOTYPE</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_STEREOTYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_PROPERTIES</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_PROPERTIES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_CONSTRAINTS</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>OPERATIONS_CONSTRAINT_TEXT_MODE</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>OPERATIONS_CONSTRAINT_TEXT_MODE_DESCRIPTION</propertyDescriptionID>
						<value>EXPRESSION_MODE</value>
						<choice xmi:value='NAME_MODE^EXPRESSION_MODE^NAME_EXPRESSION_MODE'/>
						<index xmi:value='1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_FULL_TYPE</propertyID>
						<propertyDescriptionID>SHOW_FULL_TYPE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_PARAMETERS_DIRECTION_KIND</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_PARAMETERS_DIRECTION_KIND_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>TAGGED_VALUES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>TAGGED_VALUES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>ON_SHAPE</value>
						<choice xmi:value='ON_SHAPE^IN_COMPARTMENT^DO_NOT_DISPLAY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES_STEREOTYPES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_STEREOTYPES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_QUALIFIED_NAME_IN_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_QUALIFIED_NAME_IN_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>MEMBERS_WORD_WRAP</propertyID>
						<propertyDescriptionID>MEMBERS_WORD_WRAP_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_CLASS_PORTS</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>SUPPRESS_CLASS_PORTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PORTS_COLOR</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>PORTS_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-14155776'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>PORTS_FONT</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>PORTS_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_MORE_SIGN_FOR_PORTS</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>SHOW_MORE_SIGN_FOR_PORTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SORT_CLASS_PORT_MODE</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>SORT_CLASS_PORT_MODE_DESCRIPTION</propertyDescriptionID>
						<value>NO_SORT</value>
						<choice xmi:value='NO_SORT^BY_NAME^BY_STEREOTYPE^BY_VISIBILITY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_PORTS_VISIBILITY</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>SHOW_PORTS_VISIBILITY_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_PORTS_TYPE</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>SHOW_PORTS_TYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_PORTS_STEREOTYPE</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>SHOW_PORTS_STEREOTYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_PORTS_PROPERTIES</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>SHOW_PORTS_PROPERTIES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_PORTS_CONSTRAINTS</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>SHOW_PORTS_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>PORTS_CONSTRAINTS_TEXT_MODE</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>PORTS_CONSTRAINTS_TEXT_MODE_DESCRIPTION</propertyDescriptionID>
						<value>EXPRESSION_MODE</value>
						<choice xmi:value='NAME_MODE^EXPRESSION_MODE^NAME_EXPRESSION_MODE'/>
						<index xmi:value='1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_INIT_PORTS_VALUE</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>SHOW_INIT_PORTS_VALUE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_SIGNAL_RECEPTIONS</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SUPPRESS_SIGNAL_RECEPTIONS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>RECEPTION_COLOR</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>RECEPTION_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777176'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>RECEPTION_FONT</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>RECEPTION_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_SIGNAL_RECEPTIONS_SIGNATURE</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SHOW_SIGNAL_RECEPTIONS_SIGNATURE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_MORE_SIGN_FOR_RECEPTIONS</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SHOW_MORE_SIGN_FOR_RECEPTIONS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SORT_CLASS_RECEPTIONS_MODE</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SORT_CLASS_RECEPTIONS_MODE_DESCRIPTION</propertyDescriptionID>
						<value>NO_SORT</value>
						<choice xmi:value='NO_SORT^BY_SIGNAL_NAME^BY_STEREOTYPE^BY_VISIBILITY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_SIGNAL_RECEPTIONS_VISIBILITY</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SHOW_SIGNAL_RECEPTIONS_VISIBILITY_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_RECEPTIONS_STEREOTYPES</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SHOW_RECEPTIONS_STEREOTYPES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_RECEPTIONS_PROPERTIES</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SHOW_RECEPTIONS_PROPERTIES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_RECEPTIONS_CONSTRAINTS</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SHOW_RECEPTIONS_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>RECEPTIONS_CONSTRAINTS_TEXT_MODE</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>RECEPTIONS_CONSTRAINTS_TEXT_MODE_DESCRIPTION</propertyDescriptionID>
						<value>EXPRESSION_MODE</value>
						<choice xmi:value='NAME_MODE^EXPRESSION_MODE^NAME_EXPRESSION_MODE'/>
						<index xmi:value='1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_RECEPTIONS_PARAMETERS_DIRECTION_KIND</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SHOW_RECEPTIONS_PARAMETERS_DIRECTION_KIND_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_STRUCTURE</propertyID>
						<propertyDescriptionID>SUPPRESS_STRUCTURE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_INTERFACES</propertyID>
						<propertyDescriptionID>SUPPRESS_INTERFACES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_REALIZATIONS</propertyID>
						<propertyDescriptionID>SUPPRESS_REALIZATIONS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_ARTIFACTS</propertyID>
						<propertyDescriptionID>SUPPRESS_ARTIFACTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='PropertyManagerByDiagram'>
					<diagramType>Composite Structure Diagram</diagramType>
					<removable xmi:value='true'/>
					<extendableByDiagram xmi:value='false'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Composite Structure Diagram</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986277_907020_3947</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986272_20961_3940</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_CLASS_OPERATIONS</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SUPPRESS_CLASS_OPERATIONS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_CLASS_ATTRIBUTES</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SUPPRESS_CLASS_ATTRIBUTES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_STRUCTURE</propertyID>
						<propertyDescriptionID>SUPPRESS_STRUCTURE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
				</mdElement>
				<mdElement elementClass='PropertyManagerByDiagram'>
					<diagramType>Composite Structure Diagram</diagramType>
					<removable xmi:value='true'/>
					<extendableByDiagram xmi:value='false'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Composite Structure Diagram</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986277_797019_3948</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986265_62570_3933</parentPropertyManager>
				</mdElement>
				<mdElement elementClass='PropertyManagerByDiagram'>
					<diagramType>Composite Structure Diagram</diagramType>
					<removable xmi:value='true'/>
					<extendableByDiagram xmi:value='false'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Composite Structure Diagram</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986277_556472_3949</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986277_781675_3950</parentPropertyManager>
				</mdElement>
				<mdElement elementClass='PropertyManagerByDiagram'>
					<diagramType>Composite Structure Diagram</diagramType>
					<removable xmi:value='true'/>
					<extendableByDiagram xmi:value='false'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Composite Structure Diagram</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986277_667717_3951</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986277_434954_3952</parentPropertyManager>
				</mdElement>
				<mdElement elementClass='PropertyManagerByDiagram'>
					<diagramType>Composite Structure Diagram</diagramType>
					<removable xmi:value='true'/>
					<extendableByDiagram xmi:value='false'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Composite Structure Diagram</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986277_44016_3953</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986265_384633_3934</parentPropertyManager>
				</mdElement>
				<mdElement elementClass='PropertyManagerByDiagram'>
					<diagramType>Composite Structure Diagram</diagramType>
					<removable xmi:value='true'/>
					<extendableByDiagram xmi:value='false'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Composite Structure Diagram</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986277_730003_3954</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986277_118971_3955</parentPropertyManager>
				</mdElement>
				<mdElement elementClass='PropertyManagerByDiagram'>
					<diagramType>Composite Structure Diagram</diagramType>
					<removable xmi:value='true'/>
					<extendableByDiagram xmi:value='false'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Composite Structure Diagram</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986277_914036_3956</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986276_215905_3946</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_STRUCTURE</propertyID>
						<propertyDescriptionID>SUPPRESS_STRUCTURE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
				</mdElement>
				<mdElement elementClass='PropertyManagerByDiagram'>
					<diagramType>Composite Structure Diagram</diagramType>
					<removable xmi:value='true'/>
					<extendableByDiagram xmi:value='false'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Composite Structure Diagram</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986277_384110_3957</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986277_925354_3958</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_STRUCTURE</propertyID>
						<propertyDescriptionID>SUPPRESS_STRUCTURE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
				</mdElement>
				<mdElement elementClass='PropertyManagerByDiagram'>
					<diagramType>Composite Structure Diagram</diagramType>
					<removable xmi:value='true'/>
					<extendableByDiagram xmi:value='false'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Composite Structure Diagram</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986277_878190_3959</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986274_307820_3941</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_STRUCTURE</propertyID>
						<propertyDescriptionID>SUPPRESS_STRUCTURE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>ConditionalNode</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986277_124013_3960</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-1973821'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-6710948'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>ConnectionPointReference</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986277_140897_3961</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>USE_FIXED_CONNECTION_POINTS</propertyID>
						<propertyDescriptionID>USE_FIXED_CONNECTION_POINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='3'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Connector</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986278_992738_3962</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_A</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_A_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_B</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_B_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONNECTOR_END_A</propertyID>
						<propertyDescriptionID>SHOW_CONNECTOR_END_A_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONNECTOR_END_B</propertyID>
						<propertyDescriptionID>SHOW_CONNECTOR_END_B_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>ConnectorEnd</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986278_973125_3963</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ROLE_MULTIPLICITY</propertyID>
						<propertyDescriptionID>SHOW_ROLE_MULTIPLICITY_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_DEFINING_END</propertyID>
						<propertyDescriptionID>SHOW_DEFINING_END_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Constraint</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986278_198766_3964</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ARROW</propertyID>
						<propertyDescriptionID>SHOW_ARROW_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>LINK_LINE_STYLE</propertyID>
						<propertyDescriptionID>LINK_LINE_STYLE_DESCRIPTION</propertyDescriptionID>
						<value>OBLIQUE</value>
						<choice xmi:value='RECTILINEAR^OBLIQUE^BEZIER'/>
						<index xmi:value='1'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Containment</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986278_652242_3965</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>LINK_LINE_STYLE</propertyID>
						<propertyDescriptionID>LINK_LINE_STYLE_DESCRIPTION</propertyDescriptionID>
						<value>OBLIQUE</value>
						<choice xmi:value='RECTILINEAR^OBLIQUE^BEZIER'/>
						<index xmi:value='1'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>ContentShape</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986278_557431_3966</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>USE_FILL_COLOR</propertyID>
						<propertyDescriptionID>USE_FILL_COLOR_DESCRIPTION</propertyDescriptionID>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>ControlFlow</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986278_401324_3967</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_A</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_A_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_B</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_B_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>IS_ROUNDED</propertyID>
						<propertyDescriptionID>IS_ROUNDED_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>DataStoreNode</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986278_646158_3968</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-1973821'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-6710948'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OBJECT_CLASS</propertyID>
						<propertyDescriptionID>SHOW_OBJECT_CLASS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_FULL_TYPE</propertyID>
						<propertyDescriptionID>SHOW_FULL_TYPE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_STATE</propertyID>
						<propertyDescriptionID>SHOW_STATE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>DataType</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986278_774319_3969</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-6719140'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-13159'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SHOW_MEMBERS_MODE</propertyID>
						<propertyDescriptionID>SHOW_MEMBERS_MODE_DESCRIPTION</propertyDescriptionID>
						<value>ALL</value>
						<choice xmi:value='ALL^ONLY_PUBLIC^NOT_PRIVATE'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_CLASS_ATTRIBUTES</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SUPPRESS_CLASS_ATTRIBUTES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>ATTRIBUTE_COLOR</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>ATTRIBUTE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-14155776'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>ATTRIBUTE_FONT</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>ATTRIBUTE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_MORE_SIGN_FOR_ATTRIBUTES</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_MORE_SIGN_FOR_ATTRIBUTES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SORT_CLASS_ATTRIBUTES_MODE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SORT_CLASS_ATTRIBUTES_MODE_DESCRIPTION</propertyDescriptionID>
						<value>NO_SORT</value>
						<choice xmi:value='NO_SORT^BY_NAME^BY_STEREOTYPE^BY_VISIBILITY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SHOW_ASSOCIATION_ENDS_MODE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ASSOCIATION_ENDS_MODE_DESCRIPTION</propertyDescriptionID>
						<value>DO_NOT_DISPLAY</value>
						<choice xmi:value='ALL^WITHOUT_ASSOCIATION^DO_NOT_DISPLAY'/>
						<index xmi:value='2'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_VISIBILITY</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_VISIBILITY_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_TYPE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_TYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_STEREOTYPE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_STEREOTYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_PROPERTIES</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_PROPERTIES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_CONSTRAINTS</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>ATTRIBUTES_CONSTRAINT_TEXT_MODE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>ATTRIBUTES_CONSTRAINT_TEXT_MODE_DESCRIPTION</propertyDescriptionID>
						<value>EXPRESSION_MODE</value>
						<choice xmi:value='NAME_MODE^EXPRESSION_MODE^NAME_EXPRESSION_MODE'/>
						<index xmi:value='1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_INIT_VALUE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_INIT_VALUE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_CLASS_OPERATIONS</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SUPPRESS_CLASS_OPERATIONS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>OPERATION_COLOR</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>OPERATION_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777176'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>OPERATION_FONT</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>OPERATION_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_SIGNATURE</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_SIGNATURE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_MORE_SIGN_FOR_OPERATIONS</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_MORE_SIGN_FOR_OPERATIONS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SORT_CLASS_OPERATIONS_MODE</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SORT_CLASS_OPERATIONS_MODE_DESCRIPTION</propertyDescriptionID>
						<value>NO_SORT</value>
						<choice xmi:value='NO_SORT^BY_NAME^BY_STEREOTYPE^BY_VISIBILITY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_VISIBILITY</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_VISIBILITY_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_STEREOTYPE</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_STEREOTYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_PROPERTIES</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_PROPERTIES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_CONSTRAINTS</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>OPERATIONS_CONSTRAINT_TEXT_MODE</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>OPERATIONS_CONSTRAINT_TEXT_MODE_DESCRIPTION</propertyDescriptionID>
						<value>EXPRESSION_MODE</value>
						<choice xmi:value='NAME_MODE^EXPRESSION_MODE^NAME_EXPRESSION_MODE'/>
						<index xmi:value='1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_FULL_TYPE</propertyID>
						<propertyDescriptionID>SHOW_FULL_TYPE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_PARAMETERS_DIRECTION_KIND</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_PARAMETERS_DIRECTION_KIND_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>TAGGED_VALUES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>TAGGED_VALUES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>ON_SHAPE</value>
						<choice xmi:value='ON_SHAPE^IN_COMPARTMENT^DO_NOT_DISPLAY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES_STEREOTYPES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_STEREOTYPES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_QUALIFIED_NAME_IN_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_QUALIFIED_NAME_IN_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>MEMBERS_WORD_WRAP</propertyID>
						<propertyDescriptionID>MEMBERS_WORD_WRAP_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='3'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>DecisionNode</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986279_740243_3970</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-2763307'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>USE_FIXED_CONNECTION_POINTS</propertyID>
						<propertyDescriptionID>USE_FIXED_CONNECTION_POINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='3'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-8617619'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Dependency</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986279_703403_3971</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_A</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_A_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_B</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_B_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>LINK_LINE_STYLE</propertyID>
						<propertyDescriptionID>LINK_LINE_STYLE_DESCRIPTION</propertyDescriptionID>
						<value>OBLIQUE</value>
						<choice xmi:value='RECTILINEAR^OBLIQUE^BEZIER'/>
						<index xmi:value='1'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Deployment</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986280_302295_3972</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_A</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_A_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_B</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_B_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Diagram</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986280_659674_3973</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986280_893953_3974</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>DIAGRAM_BACKGROUND_COLOR</propertyID>
						<propertyDescriptionID>DIAGRAM_BACKGROUND_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>USE_GRADIENT_FOR_FILL</propertyID>
						<propertyDescriptionID>USE_GRADIENT_FOR_FILL_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>USE_SHADOW_FOR_SHAPES</propertyID>
						<propertyDescriptionID>USE_SHADOW_FOR_SHAPES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_GRID</propertyID>
						<propertyDescriptionID>SHOW_GRID_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='NumberProperty'>
						<propertyID>GRID_SIZE</propertyID>
						<propertyDescriptionID>GRID_SIZE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='7.0'/>
						<lowRange xmi:value='2.0'/>
						<highRange xmi:value='30.0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>USE_GRID_FOR_PATHS</propertyID>
						<propertyDescriptionID>USE_GRID_FOR_PATHS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>USE_GRID_FOR_SHAPES</propertyID>
						<propertyDescriptionID>USE_GRID_FOR_SHAPES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_MESSAGE_NUMBERS</propertyID>
						<propertyDescriptionID>SHOW_MESSAGE_NUMBERS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>USE_ADVANCED_NUMBERING</propertyID>
						<propertyDescriptionID>USE_ADVANCED_NUMBERING_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ACTIVATIONS</propertyID>
						<propertyDescriptionID>SHOW_ACTIVATIONS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_DIAGRAM_INFO</propertyID>
						<propertyDescriptionID>SHOW_DIAGRAM_INFO_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_DIAGRAM_OWNER</propertyID>
						<propertyDescriptionID>SHOW_DIAGRAM_OWNER_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_DIAGRAM_FRAME</propertyID>
						<propertyGroup>DIAGRAM_FRAME</propertyGroup>
						<propertyDescriptionID>SHOW_DIAGRAM_FRAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ABBREVIATED_DIAGRAM_TYPE</propertyID>
						<propertyGroup>DIAGRAM_FRAME</propertyGroup>
						<propertyDescriptionID>SHOW_ABBREVIATED_DIAGRAM_TYPE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_DIAGRAM_NAME</propertyID>
						<propertyGroup>DIAGRAM_FRAME</propertyGroup>
						<propertyDescriptionID>SHOW_DIAGRAM_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_DIAGRAM_TYPE</propertyID>
						<propertyGroup>DIAGRAM_FRAME</propertyGroup>
						<propertyDescriptionID>SHOW_DIAGRAM_TYPE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_PARAMETERS</propertyID>
						<propertyGroup>DIAGRAM_FRAME</propertyGroup>
						<propertyDescriptionID>SHOW_PARAMETERS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONTEXT_NAME</propertyID>
						<propertyGroup>DIAGRAM_FRAME</propertyGroup>
						<propertyDescriptionID>SHOW_CONTEXT_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONTEXT_TYPE</propertyID>
						<propertyGroup>DIAGRAM_FRAME</propertyGroup>
						<propertyDescriptionID>SHOW_CONTEXT_TYPE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_FRAME_OWNER</propertyID>
						<propertyGroup>DIAGRAM_FRAME</propertyGroup>
						<propertyDescriptionID>SHOW_FRAME_OWNER_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>AUTOSIZE</propertyID>
						<propertyGroup>DIAGRAM_FRAME</propertyGroup>
						<propertyDescriptionID>AUTOSIZE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>USE_ROUNDED_CORNERS</propertyID>
						<propertyGroup>DIAGRAM_FRAME</propertyGroup>
						<propertyDescriptionID>USE_ROUNDED_CORNERS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>USE_STEREOTYPE</propertyID>
						<propertyDescriptionID>USE_STEREOTYPE_DESCRIPTION</propertyDescriptionID>
						<value>USE_STEREOTYPE_DIAGRAM</value>
						<choice xmi:value='USE_STEREOTYPE_CONTEXT^USE_STEREOTYPE_DIAGRAM'/>
						<index xmi:value='1'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>DIAGRAM_ORIENTATION</propertyID>
						<propertyDescriptionID>DIAGRAM_ORIENTATION_DESCRIPTION</propertyDescriptionID>
						<value>DIAGRAM_ORIENTATION_VERTICAL</value>
						<choice xmi:value='DIAGRAM_ORIENTATION_VERTICAL^DIAGRAM_ORIENTATION_HORIZONTAL'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>LINE_JUMP_PLACE</propertyID>
						<propertyDescriptionID>LINE_JUMP_PLACE_DESCRIPTION</propertyDescriptionID>
						<value>LINE_JUMP_PLACE_HORIZONTAL</value>
						<choice xmi:value='LINE_JUMP_PLACE_NONE^LINE_JUMP_PLACE_HORIZONTAL^LINE_JUMP_PLACE_VERTICAL'/>
						<index xmi:value='1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_SYSML_INTERNAL_PROPERTIES_COMPARTMENTS</propertyID>
						<propertyDescriptionID>SHOW_SYSML_INTERNAL_PROPERTIES_COMPARTMENTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Diagram Shape</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986280_244012_3975</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='3'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>USE_STEREOTYPE</propertyID>
						<propertyDescriptionID>USE_STEREOTYPE_DESCRIPTION</propertyDescriptionID>
						<value>USE_STEREOTYPE_DIAGRAM</value>
						<choice xmi:value='USE_STEREOTYPE_CONTEXT^USE_STEREOTYPE_DIAGRAM'/>
						<index xmi:value='1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ABBREVIATED_TYPE</propertyID>
						<propertyDescriptionID>SHOW_ABBREVIATED_TYPE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_DIAGRAM_NAME</propertyID>
						<propertyDescriptionID>SHOW_DIAGRAM_NAME_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_PARAMETERS</propertyID>
						<propertyDescriptionID>SHOW_PARAMETERS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONTEXT_NAME</propertyID>
						<propertyDescriptionID>SHOW_CONTEXT_NAME_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONTEXT_TYPE</propertyID>
						<propertyDescriptionID>SHOW_CONTEXT_TYPE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_DIAGRAM_TYPE</propertyID>
						<propertyDescriptionID>SHOW_DIAGRAM_TYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_FRAME_OWNER</propertyID>
						<propertyDescriptionID>SHOW_FRAME_OWNER_DESCRIPTION</propertyDescriptionID>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>DiagramInfo</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986280_295512_3976</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>USE_FILL_COLOR</propertyID>
						<propertyDescriptionID>USE_FILL_COLOR_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>AUTOSIZE</propertyID>
						<propertyDescriptionID>AUTOSIZE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>DurationConstraint</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986283_481896_3977</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>ElementImport</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986283_36258_3978</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_A</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_A_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_B</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_B_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Enumeration</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986277_118971_3955</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-13159'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-6719140'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='3'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SHOW_MEMBERS_MODE</propertyID>
						<propertyDescriptionID>SHOW_MEMBERS_MODE_DESCRIPTION</propertyDescriptionID>
						<value>ALL</value>
						<choice xmi:value='ALL^ONLY_PUBLIC^NOT_PRIVATE'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_CLASS_ATTRIBUTES</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SUPPRESS_CLASS_ATTRIBUTES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>ATTRIBUTE_COLOR</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>ATTRIBUTE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-14155776'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>ATTRIBUTE_FONT</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>ATTRIBUTE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_MORE_SIGN_FOR_ATTRIBUTES</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_MORE_SIGN_FOR_ATTRIBUTES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SORT_CLASS_ATTRIBUTES_MODE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SORT_CLASS_ATTRIBUTES_MODE_DESCRIPTION</propertyDescriptionID>
						<value>NO_SORT</value>
						<choice xmi:value='NO_SORT^BY_NAME^BY_STEREOTYPE^BY_VISIBILITY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SHOW_ASSOCIATION_ENDS_MODE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ASSOCIATION_ENDS_MODE_DESCRIPTION</propertyDescriptionID>
						<value>DO_NOT_DISPLAY</value>
						<choice xmi:value='ALL^WITHOUT_ASSOCIATION^DO_NOT_DISPLAY'/>
						<index xmi:value='2'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_VISIBILITY</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_VISIBILITY_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_TYPE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_TYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_STEREOTYPE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_STEREOTYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_PROPERTIES</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_PROPERTIES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_CONSTRAINTS</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>ATTRIBUTES_CONSTRAINT_TEXT_MODE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>ATTRIBUTES_CONSTRAINT_TEXT_MODE_DESCRIPTION</propertyDescriptionID>
						<value>EXPRESSION_MODE</value>
						<choice xmi:value='NAME_MODE^EXPRESSION_MODE^NAME_EXPRESSION_MODE'/>
						<index xmi:value='1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_INIT_VALUE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_INIT_VALUE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_CLASS_OPERATIONS</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SUPPRESS_CLASS_OPERATIONS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>OPERATION_COLOR</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>OPERATION_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777176'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>OPERATION_FONT</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>OPERATION_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_SIGNATURE</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_SIGNATURE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_MORE_SIGN_FOR_OPERATIONS</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_MORE_SIGN_FOR_OPERATIONS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SORT_CLASS_OPERATIONS_MODE</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SORT_CLASS_OPERATIONS_MODE_DESCRIPTION</propertyDescriptionID>
						<value>NO_SORT</value>
						<choice xmi:value='NO_SORT^BY_NAME^BY_STEREOTYPE^BY_VISIBILITY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_VISIBILITY</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_VISIBILITY_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_STEREOTYPE</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_STEREOTYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_PROPERTIES</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_PROPERTIES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_CONSTRAINTS</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>OPERATIONS_CONSTRAINT_TEXT_MODE</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>OPERATIONS_CONSTRAINT_TEXT_MODE_DESCRIPTION</propertyDescriptionID>
						<value>EXPRESSION_MODE</value>
						<choice xmi:value='NAME_MODE^EXPRESSION_MODE^NAME_EXPRESSION_MODE'/>
						<index xmi:value='1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_FULL_TYPE</propertyID>
						<propertyDescriptionID>SHOW_FULL_TYPE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_PARAMETERS_DIRECTION_KIND</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_PARAMETERS_DIRECTION_KIND_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>TAGGED_VALUES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>TAGGED_VALUES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>ON_SHAPE</value>
						<choice xmi:value='ON_SHAPE^IN_COMPARTMENT^DO_NOT_DISPLAY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES_STEREOTYPES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_STEREOTYPES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_QUALIFIED_NAME_IN_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_QUALIFIED_NAME_IN_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>MEMBERS_WORD_WRAP</propertyID>
						<propertyDescriptionID>MEMBERS_WORD_WRAP_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_ENUMERATION_LITERALS</propertyID>
						<propertyGroup>ENUMERATION_LITERALS</propertyGroup>
						<propertyDescriptionID>SUPPRESS_ENUMERATION_LITERALS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>ENUMERATION_LITERAL_COLOR</propertyID>
						<propertyGroup>ENUMERATION_LITERALS</propertyGroup>
						<propertyDescriptionID>ENUMERATION_LITERAL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-14155776'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ENUMERATION_LITERAL_CONSTRAINTS</propertyID>
						<propertyGroup>ENUMERATION_LITERALS</propertyGroup>
						<propertyDescriptionID>SHOW_ENUMERATION_LITERAL_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>ENUMERATION_LITERAL_CONSTRAINTS_TEXT_MODE</propertyID>
						<propertyGroup>ENUMERATION_LITERALS</propertyGroup>
						<propertyDescriptionID>ENUMERATION_LITERAL_CONSTRAINTS_TEXT_MODE_DESCRIPTION</propertyDescriptionID>
						<value>EXPRESSION_MODE</value>
						<choice xmi:value='NAME_MODE^EXPRESSION_MODE^NAME_EXPRESSION_MODE'/>
						<index xmi:value='1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ENUMERATION_LITERAL_PROPERTIES</propertyID>
						<propertyGroup>ENUMERATION_LITERALS</propertyGroup>
						<propertyDescriptionID>SHOW_ENUMERATION_LITERAL_PROPERTIES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ENUMERATION_LITERAL_STEREOTYPE</propertyID>
						<propertyGroup>ENUMERATION_LITERALS</propertyGroup>
						<propertyDescriptionID>SHOW_ENUMERATION_LITERAL_STEREOTYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>ENUMERATION_LITERAL_FONT</propertyID>
						<propertyGroup>ENUMERATION_LITERALS</propertyGroup>
						<propertyDescriptionID>ENUMERATION_LITERAL_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SORT_ENUMERATION_LITERALS_MODE</propertyID>
						<propertyGroup>ENUMERATION_LITERALS</propertyGroup>
						<propertyDescriptionID>SORT_ENUMERATION_LITERALS_MODE_DESCRIPTION</propertyDescriptionID>
						<value>NO_SORT</value>
						<choice xmi:value='NO_SORT^BY_NAME^BY_STEREOTYPE'/>
						<index xmi:value='0'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>ExceptionHandler</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986285_715666_3979</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='2'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_A</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_A_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_B</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_B_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>IS_ROUNDED</propertyID>
						<propertyDescriptionID>IS_ROUNDED_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>ExpansionNode</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986285_940789_3980</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>AUTOSIZE</propertyID>
						<propertyDescriptionID>AUTOSIZE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-1973821'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-6710948'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='5'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>ExpansionRegion</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986285_731924_3981</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-1973821'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-6710948'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Extend</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986285_685574_3982</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_A</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_A_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_B</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_B_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>LINK_LINE_STYLE</propertyID>
						<propertyDescriptionID>LINK_LINE_STYLE_DESCRIPTION</propertyDescriptionID>
						<value>OBLIQUE</value>
						<choice xmi:value='RECTILINEAR^OBLIQUE^BEZIER'/>
						<index xmi:value='1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_EXTENSION_POINT</propertyID>
						<propertyDescriptionID>SHOW_EXTENSION_POINT_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Extension</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986286_233144_3983</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_A</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_A_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_B</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_B_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ASSOCIATION_DIRECTION_ICON</propertyID>
						<propertyDescriptionID>SHOW_ASSOCIATION_DIRECTION_ICON_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_IS_REQUIRED</propertyID>
						<propertyDescriptionID>SHOW_IS_REQUIRED_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>ExtensionRole</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986286_501867_3984</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ROLE_NAME</propertyID>
						<propertyDescriptionID>SHOW_ROLE_NAME_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ROLE_VISIBILITY</propertyID>
						<propertyDescriptionID>SHOW_ROLE_VISIBILITY_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ROLE_MULTIPLICITY</propertyID>
						<propertyDescriptionID>SHOW_ROLE_MULTIPLICITY_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ROLE_PROPERTY_STRING</propertyID>
						<propertyDescriptionID>SHOW_ROLE_PROPERTY_STRING_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Final State</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986286_954170_3985</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>USE_FIXED_CONNECTION_POINTS</propertyID>
						<propertyDescriptionID>USE_FIXED_CONNECTION_POINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='3'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>FinalNode</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986286_838242_3986</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>USE_FIXED_CONNECTION_POINTS</propertyID>
						<propertyDescriptionID>USE_FIXED_CONNECTION_POINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='3'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>FlowConnector</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986286_269954_3987</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-1973821'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>USE_FIXED_CONNECTION_POINTS</propertyID>
						<propertyDescriptionID>USE_FIXED_CONNECTION_POINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>AUTOSIZE</propertyID>
						<propertyDescriptionID>AUTOSIZE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>FlowFinalNode</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986286_56218_3988</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-1'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='3'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>ForkJoinPseudostate</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986286_565096_3989</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-1'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='5'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SYNCH_BAR_ORIENTATION</propertyID>
						<propertyDescriptionID>SYNCH_BAR_ORIENTATION_DESCRIPTION</propertyDescriptionID>
						<value>HORIZONTAL</value>
						<choice xmi:value='HORIZONTAL^VERTICAL'/>
						<index xmi:value='0'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>ForkNode</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986286_639165_3990</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SYNCH_BAR_ORIENTATION</propertyID>
						<propertyDescriptionID>SYNCH_BAR_ORIENTATION_DESCRIPTION</propertyDescriptionID>
						<value>HORIZONTAL</value>
						<choice xmi:value='HORIZONTAL^VERTICAL'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='3'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Generalization</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986286_603394_3991</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_A</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_A_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_B</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_B_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_GENERALIZATION_SET</propertyID>
						<propertyDescriptionID>SHOW_GENERALIZATION_SET_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>GeneralizationSet</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986287_277089_3992</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>USE_FILL_COLOR</propertyID>
						<propertyDescriptionID>USE_FILL_COLOR_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_POWERTYPE</propertyID>
						<propertyDescriptionID>SHOW_POWERTYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_COMPLETE_DISJOINT</propertyID>
						<propertyDescriptionID>SHOW_COMPLETE_DISJOINT_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='3'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>ImageShape</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986287_702486_3993</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='FileProperty'>
						<propertyID>IMAGE</propertyID>
						<propertyDescriptionID>IMAGE_DESCRIPTION</propertyDescriptionID>
						<selectionMode xmi:value='0'/>
						<displayFullPath xmi:value='true'/>
						<useFilePreviewer xmi:value='false'/>
						<displayAllFiles xmi:value='true'/>
						<fileType>FILE_TYPE_ANY</fileType>
					</mdElement>
				</mdElement>
				<mdElement elementClass='PropertyManagerByDiagram'>
					<diagramType>Implementation Diagram</diagramType>
					<removable xmi:value='true'/>
					<extendableByDiagram xmi:value='false'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Implementation Diagram</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986287_892646_3994</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986277_434954_3952</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_CLASS_OPERATIONS</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SUPPRESS_CLASS_OPERATIONS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Include</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986287_381041_3995</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_A</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_A_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_B</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_B_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>LINK_LINE_STYLE</propertyID>
						<propertyDescriptionID>LINK_LINE_STYLE_DESCRIPTION</propertyDescriptionID>
						<value>OBLIQUE</value>
						<choice xmi:value='RECTILINEAR^OBLIQUE^BEZIER'/>
						<index xmi:value='1'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>InformationFlow</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986287_807230_3996</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>InformationItem</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986287_890618_3997</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-13159'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-6719140'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_FULL_TYPE</propertyID>
						<propertyDescriptionID>SHOW_FULL_TYPE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>TAGGED_VALUES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>TAGGED_VALUES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>ON_SHAPE</value>
						<choice xmi:value='ON_SHAPE^IN_COMPARTMENT^DO_NOT_DISPLAY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES_STEREOTYPES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_STEREOTYPES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_QUALIFIED_NAME_IN_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_QUALIFIED_NAME_IN_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='3'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>InitialNode</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986287_936159_3998</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>USE_FIXED_CONNECTION_POINTS</propertyID>
						<propertyDescriptionID>USE_FIXED_CONNECTION_POINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='3'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>InputPin</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986287_399024_3999</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>AUTOSIZE</propertyID>
						<propertyDescriptionID>AUTOSIZE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TYPE</propertyID>
						<propertyDescriptionID>SHOW_TYPE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_FULL_TYPE</propertyID>
						<propertyDescriptionID>SHOW_FULL_TYPE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>USE_FIXED_CONNECTION_POINTS</propertyID>
						<propertyDescriptionID>USE_FIXED_CONNECTION_POINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-1973821'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-6710948'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_PROPERTIES</propertyID>
						<propertyDescriptionID>SHOW_PROPERTIES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='5'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>InstanceSpecification</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986287_40489_4000</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-3916'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-6714020'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OBJECT_CLASS</propertyID>
						<propertyDescriptionID>SHOW_OBJECT_CLASS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_FULL_TYPE</propertyID>
						<propertyDescriptionID>SHOW_FULL_TYPE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_SPECIFICATION_VALUE</propertyID>
						<propertyDescriptionID>SHOW_SPECIFICATION_VALUE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_OBJECT_ATTRIBUTES</propertyID>
						<propertyDescriptionID>SUPPRESS_OBJECT_ATTRIBUTES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SHOW_SLOT_TYPE_ON_INSTANCE</propertyID>
						<propertyDescriptionID>SHOW_SLOT_TYPE_ON_INSTANCE_DESCRIPTION</propertyDescriptionID>
						<value>SHOW_TYPE_MODE_NONE</value>
						<choice xmi:value='SHOW_TYPE_MODE_NONE^SHOW_TYPE_MODE_NAME^SHOW_TYPE_MODE_QUALIFIED_NAME'/>
						<index xmi:value='0'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>InteractionUse</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986287_674689_4001</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-6710948'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='3'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>OWNER_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>OWNER_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>QNAME_DISPLAY_MODE_DO_NOT_DISPLAY</value>
						<choice xmi:value='QNAME_DISPLAY_MODE_DO_NOT_DISPLAY^OWNER_DISPLAY_MODE_STD^OWNER_DISPLAY_MODE_OLD'/>
						<index xmi:value='0'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Interface</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986277_434954_3952</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-4336959'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-10708633'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='3'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SHOW_MEMBERS_MODE</propertyID>
						<propertyDescriptionID>SHOW_MEMBERS_MODE_DESCRIPTION</propertyDescriptionID>
						<value>ALL</value>
						<choice xmi:value='ALL^ONLY_PUBLIC^NOT_PRIVATE'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_CLASS_ATTRIBUTES</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SUPPRESS_CLASS_ATTRIBUTES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>ATTRIBUTE_COLOR</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>ATTRIBUTE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-14155776'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>ATTRIBUTE_FONT</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>ATTRIBUTE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_MORE_SIGN_FOR_ATTRIBUTES</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_MORE_SIGN_FOR_ATTRIBUTES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SORT_CLASS_ATTRIBUTES_MODE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SORT_CLASS_ATTRIBUTES_MODE_DESCRIPTION</propertyDescriptionID>
						<value>NO_SORT</value>
						<choice xmi:value='NO_SORT^BY_NAME^BY_STEREOTYPE^BY_VISIBILITY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SHOW_ASSOCIATION_ENDS_MODE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ASSOCIATION_ENDS_MODE_DESCRIPTION</propertyDescriptionID>
						<value>DO_NOT_DISPLAY</value>
						<choice xmi:value='ALL^WITHOUT_ASSOCIATION^DO_NOT_DISPLAY'/>
						<index xmi:value='2'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_VISIBILITY</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_VISIBILITY_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_TYPE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_TYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_STEREOTYPE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_STEREOTYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_PROPERTIES</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_PROPERTIES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_CONSTRAINTS</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>ATTRIBUTES_CONSTRAINT_TEXT_MODE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>ATTRIBUTES_CONSTRAINT_TEXT_MODE_DESCRIPTION</propertyDescriptionID>
						<value>EXPRESSION_MODE</value>
						<choice xmi:value='NAME_MODE^EXPRESSION_MODE^NAME_EXPRESSION_MODE'/>
						<index xmi:value='1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_INIT_VALUE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_INIT_VALUE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_CLASS_OPERATIONS</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SUPPRESS_CLASS_OPERATIONS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>OPERATION_COLOR</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>OPERATION_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777176'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>OPERATION_FONT</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>OPERATION_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_SIGNATURE</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_SIGNATURE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_MORE_SIGN_FOR_OPERATIONS</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_MORE_SIGN_FOR_OPERATIONS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SORT_CLASS_OPERATIONS_MODE</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SORT_CLASS_OPERATIONS_MODE_DESCRIPTION</propertyDescriptionID>
						<value>NO_SORT</value>
						<choice xmi:value='NO_SORT^BY_NAME^BY_STEREOTYPE^BY_VISIBILITY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_VISIBILITY</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_VISIBILITY_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_STEREOTYPE</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_STEREOTYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_PROPERTIES</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_PROPERTIES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_CONSTRAINTS</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>OPERATIONS_CONSTRAINT_TEXT_MODE</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>OPERATIONS_CONSTRAINT_TEXT_MODE_DESCRIPTION</propertyDescriptionID>
						<value>EXPRESSION_MODE</value>
						<choice xmi:value='NAME_MODE^EXPRESSION_MODE^NAME_EXPRESSION_MODE'/>
						<index xmi:value='1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_FULL_TYPE</propertyID>
						<propertyDescriptionID>SHOW_FULL_TYPE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_PARAMETERS_DIRECTION_KIND</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_PARAMETERS_DIRECTION_KIND_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>TAGGED_VALUES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>TAGGED_VALUES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>ON_SHAPE</value>
						<choice xmi:value='ON_SHAPE^IN_COMPARTMENT^DO_NOT_DISPLAY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES_STEREOTYPES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_STEREOTYPES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_QUALIFIED_NAME_IN_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_QUALIFIED_NAME_IN_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>MEMBERS_WORD_WRAP</propertyID>
						<propertyDescriptionID>MEMBERS_WORD_WRAP_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_SIGNAL_RECEPTIONS</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SUPPRESS_SIGNAL_RECEPTIONS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>RECEPTION_COLOR</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>RECEPTION_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777176'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>RECEPTION_FONT</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>RECEPTION_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_SIGNAL_RECEPTIONS_SIGNATURE</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SHOW_SIGNAL_RECEPTIONS_SIGNATURE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_MORE_SIGN_FOR_RECEPTIONS</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SHOW_MORE_SIGN_FOR_RECEPTIONS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SORT_CLASS_RECEPTIONS_MODE</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SORT_CLASS_RECEPTIONS_MODE_DESCRIPTION</propertyDescriptionID>
						<value>NO_SORT</value>
						<choice xmi:value='NO_SORT^BY_SIGNAL_NAME^BY_STEREOTYPE^BY_VISIBILITY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_SIGNAL_RECEPTIONS_VISIBILITY</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SHOW_SIGNAL_RECEPTIONS_VISIBILITY_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_RECEPTIONS_STEREOTYPES</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SHOW_RECEPTIONS_STEREOTYPES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_RECEPTIONS_PROPERTIES</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SHOW_RECEPTIONS_PROPERTIES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_RECEPTIONS_CONSTRAINTS</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SHOW_RECEPTIONS_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>RECEPTIONS_CONSTRAINTS_TEXT_MODE</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>RECEPTIONS_CONSTRAINTS_TEXT_MODE_DESCRIPTION</propertyDescriptionID>
						<value>EXPRESSION_MODE</value>
						<choice xmi:value='NAME_MODE^EXPRESSION_MODE^NAME_EXPRESSION_MODE'/>
						<index xmi:value='1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_RECEPTIONS_PARAMETERS_DIRECTION_KIND</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SHOW_RECEPTIONS_PARAMETERS_DIRECTION_KIND_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>ENABLE_UML_2_0_NOTATION</propertyID>
						<propertyDescriptionID>ENABLE_UML_2_0_NOTATION_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>InterfaceRealization</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986288_557003_4002</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_A</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_A_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_B</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_B_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>LINK_LINE_STYLE</propertyID>
						<propertyDescriptionID>LINK_LINE_STYLE_DESCRIPTION</propertyDescriptionID>
						<value>OBLIQUE</value>
						<choice xmi:value='RECTILINEAR^OBLIQUE^BEZIER'/>
						<index xmi:value='1'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>InterruptibleActivityRegion</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986288_691228_4003</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>OWNER_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>OWNER_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>QNAME_DISPLAY_MODE_DO_NOT_DISPLAY</value>
						<choice xmi:value='QNAME_DISPLAY_MODE_DO_NOT_DISPLAY^OWNER_DISPLAY_MODE_STD^OWNER_DISPLAY_MODE_OLD'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-1973821'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-6710948'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>JoinNode</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986288_550314_4004</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SYNCH_BAR_ORIENTATION</propertyID>
						<propertyDescriptionID>SYNCH_BAR_ORIENTATION_DESCRIPTION</propertyDescriptionID>
						<value>HORIZONTAL</value>
						<choice xmi:value='HORIZONTAL^VERTICAL'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='3'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Lifeline</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986288_277240_4005</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>OWNER_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>OWNER_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>QNAME_DISPLAY_MODE_DO_NOT_DISPLAY</value>
						<choice xmi:value='QNAME_DISPLAY_MODE_DO_NOT_DISPLAY^OWNER_DISPLAY_MODE_STD^OWNER_DISPLAY_MODE_OLD'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-4004909'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-12753326'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_FULL_TYPE</propertyID>
						<propertyDescriptionID>SHOW_FULL_TYPE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OBJECT_CLASS</propertyID>
						<propertyDescriptionID>SHOW_OBJECT_CLASS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Lifeline(in Sequence Diagram)</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986288_570303_4006</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-4004909'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-12753326'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>OWNER_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>OWNER_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>QNAME_DISPLAY_MODE_DO_NOT_DISPLAY</value>
						<choice xmi:value='QNAME_DISPLAY_MODE_DO_NOT_DISPLAY^OWNER_DISPLAY_MODE_STD^OWNER_DISPLAY_MODE_OLD'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_FULL_TYPE</propertyID>
						<propertyDescriptionID>SHOW_FULL_TYPE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OBJECT_CLASS</propertyID>
						<propertyDescriptionID>SHOW_OBJECT_CLASS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ENTIRE_ACTIVATION</propertyID>
						<propertyDescriptionID>SHOW_ENTIRE_ACTIVATION_DESCRIPTION</propertyDescriptionID>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Link</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986288_568635_4007</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_A</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_A_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_B</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_B_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ROLE_A</propertyID>
						<propertyDescriptionID>SHOW_ROLE_A_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ROLE_B</propertyID>
						<propertyDescriptionID>SHOW_ROLE_B_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAVIGABILITY</propertyID>
						<propertyDescriptionID>SHOW_NAVIGABILITY_DESCRIPTION</propertyDescriptionID>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Link Attribute</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986289_108321_4008</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>LoopNode</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986289_760034_4009</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-1973821'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-6710948'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Manifestation</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986289_396494_4010</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_A</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_A_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_B</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_B_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>MergeNode</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986289_319264_4011</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-2763307'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>USE_FIXED_CONNECTION_POINTS</propertyID>
						<propertyDescriptionID>USE_FIXED_CONNECTION_POINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='3'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-8617619'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Message</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986292_221412_4012</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>USE_FILL_COLOR</propertyID>
						<propertyDescriptionID>USE_FILL_COLOR_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='NumberProperty'>
						<propertyID>LINE_WIDTH</propertyID>
						<propertyDescriptionID>LINE_WIDTH_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='1.0'/>
						<lowRange xmi:value='1.0'/>
						<highRange xmi:value='100.0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='3'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_PREDECESSORS</propertyID>
						<propertyDescriptionID>SHOW_PREDECESSORS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_PARAMETERS_NAMES</propertyID>
						<propertyDescriptionID>SHOW_PARAMETERS_NAMES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Message(in Sequence Diagram)</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986292_136711_4013</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>USE_FILL_COLOR</propertyID>
						<propertyDescriptionID>USE_FILL_COLOR_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='NumberProperty'>
						<propertyID>LINE_WIDTH</propertyID>
						<propertyDescriptionID>LINE_WIDTH_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='1.0'/>
						<lowRange xmi:value='1.0'/>
						<highRange xmi:value='100.0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>IS_ROUNDED</propertyID>
						<propertyDescriptionID>IS_ROUNDED_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_A</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_A_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_B</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_B_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_PARAMETERS_NAMES</propertyID>
						<propertyDescriptionID>SHOW_PARAMETERS_NAMES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Model</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986292_477455_4014</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-2826753'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-9734759'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>FONT</propertyID>
						<propertyDescriptionID>FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='13'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>PACKAGE_HEADER_POSITION</propertyID>
						<propertyDescriptionID>PACKAGE_HEADER_POSITION_DESCRIPTION</propertyDescriptionID>
						<value>TOP</value>
						<choice xmi:value='TOP^IN_TAB'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ELEMENTS_LIST</propertyID>
						<propertyDescriptionID>SHOW_ELEMENTS_LIST_DESCRIPTION</propertyDescriptionID>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>N-ary Association</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986292_881742_4015</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>USE_FIXED_CONNECTION_POINTS</propertyID>
						<propertyDescriptionID>USE_FIXED_CONNECTION_POINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Node</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986277_925354_3958</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-4336959'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-10708633'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='3'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SHOW_MEMBERS_MODE</propertyID>
						<propertyDescriptionID>SHOW_MEMBERS_MODE_DESCRIPTION</propertyDescriptionID>
						<value>ALL</value>
						<choice xmi:value='ALL^ONLY_PUBLIC^NOT_PRIVATE'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_CLASS_ATTRIBUTES</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SUPPRESS_CLASS_ATTRIBUTES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>ATTRIBUTE_COLOR</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>ATTRIBUTE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-14155776'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>ATTRIBUTE_FONT</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>ATTRIBUTE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_MORE_SIGN_FOR_ATTRIBUTES</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_MORE_SIGN_FOR_ATTRIBUTES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SORT_CLASS_ATTRIBUTES_MODE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SORT_CLASS_ATTRIBUTES_MODE_DESCRIPTION</propertyDescriptionID>
						<value>NO_SORT</value>
						<choice xmi:value='NO_SORT^BY_NAME^BY_STEREOTYPE^BY_VISIBILITY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SHOW_ASSOCIATION_ENDS_MODE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ASSOCIATION_ENDS_MODE_DESCRIPTION</propertyDescriptionID>
						<value>DO_NOT_DISPLAY</value>
						<choice xmi:value='ALL^WITHOUT_ASSOCIATION^DO_NOT_DISPLAY'/>
						<index xmi:value='2'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_VISIBILITY</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_VISIBILITY_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_TYPE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_TYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_STEREOTYPE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_STEREOTYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_PROPERTIES</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_PROPERTIES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_CONSTRAINTS</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>ATTRIBUTES_CONSTRAINT_TEXT_MODE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>ATTRIBUTES_CONSTRAINT_TEXT_MODE_DESCRIPTION</propertyDescriptionID>
						<value>EXPRESSION_MODE</value>
						<choice xmi:value='NAME_MODE^EXPRESSION_MODE^NAME_EXPRESSION_MODE'/>
						<index xmi:value='1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_INIT_VALUE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_INIT_VALUE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_CLASS_OPERATIONS</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SUPPRESS_CLASS_OPERATIONS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>OPERATION_COLOR</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>OPERATION_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777176'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>OPERATION_FONT</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>OPERATION_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_SIGNATURE</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_SIGNATURE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_MORE_SIGN_FOR_OPERATIONS</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_MORE_SIGN_FOR_OPERATIONS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SORT_CLASS_OPERATIONS_MODE</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SORT_CLASS_OPERATIONS_MODE_DESCRIPTION</propertyDescriptionID>
						<value>NO_SORT</value>
						<choice xmi:value='NO_SORT^BY_NAME^BY_STEREOTYPE^BY_VISIBILITY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_VISIBILITY</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_VISIBILITY_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_STEREOTYPE</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_STEREOTYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_PROPERTIES</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_PROPERTIES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_CONSTRAINTS</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>OPERATIONS_CONSTRAINT_TEXT_MODE</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>OPERATIONS_CONSTRAINT_TEXT_MODE_DESCRIPTION</propertyDescriptionID>
						<value>EXPRESSION_MODE</value>
						<choice xmi:value='NAME_MODE^EXPRESSION_MODE^NAME_EXPRESSION_MODE'/>
						<index xmi:value='1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_FULL_TYPE</propertyID>
						<propertyDescriptionID>SHOW_FULL_TYPE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_PARAMETERS_DIRECTION_KIND</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_PARAMETERS_DIRECTION_KIND_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>TAGGED_VALUES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>TAGGED_VALUES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>ON_SHAPE</value>
						<choice xmi:value='ON_SHAPE^IN_COMPARTMENT^DO_NOT_DISPLAY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES_STEREOTYPES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_STEREOTYPES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_QUALIFIED_NAME_IN_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_QUALIFIED_NAME_IN_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>MEMBERS_WORD_WRAP</propertyID>
						<propertyDescriptionID>MEMBERS_WORD_WRAP_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_CLASS_PORTS</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>SUPPRESS_CLASS_PORTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PORTS_COLOR</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>PORTS_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-14155776'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>PORTS_FONT</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>PORTS_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_MORE_SIGN_FOR_PORTS</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>SHOW_MORE_SIGN_FOR_PORTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SORT_CLASS_PORT_MODE</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>SORT_CLASS_PORT_MODE_DESCRIPTION</propertyDescriptionID>
						<value>NO_SORT</value>
						<choice xmi:value='NO_SORT^BY_NAME^BY_STEREOTYPE^BY_VISIBILITY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_PORTS_VISIBILITY</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>SHOW_PORTS_VISIBILITY_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_PORTS_TYPE</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>SHOW_PORTS_TYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_PORTS_STEREOTYPE</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>SHOW_PORTS_STEREOTYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_PORTS_PROPERTIES</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>SHOW_PORTS_PROPERTIES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_PORTS_CONSTRAINTS</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>SHOW_PORTS_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>PORTS_CONSTRAINTS_TEXT_MODE</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>PORTS_CONSTRAINTS_TEXT_MODE_DESCRIPTION</propertyDescriptionID>
						<value>EXPRESSION_MODE</value>
						<choice xmi:value='NAME_MODE^EXPRESSION_MODE^NAME_EXPRESSION_MODE'/>
						<index xmi:value='1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_INIT_PORTS_VALUE</propertyID>
						<propertyGroup>PORTS</propertyGroup>
						<propertyDescriptionID>SHOW_INIT_PORTS_VALUE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_SIGNAL_RECEPTIONS</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SUPPRESS_SIGNAL_RECEPTIONS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>RECEPTION_COLOR</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>RECEPTION_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777176'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>RECEPTION_FONT</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>RECEPTION_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_SIGNAL_RECEPTIONS_SIGNATURE</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SHOW_SIGNAL_RECEPTIONS_SIGNATURE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_MORE_SIGN_FOR_RECEPTIONS</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SHOW_MORE_SIGN_FOR_RECEPTIONS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SORT_CLASS_RECEPTIONS_MODE</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SORT_CLASS_RECEPTIONS_MODE_DESCRIPTION</propertyDescriptionID>
						<value>NO_SORT</value>
						<choice xmi:value='NO_SORT^BY_SIGNAL_NAME^BY_STEREOTYPE^BY_VISIBILITY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_SIGNAL_RECEPTIONS_VISIBILITY</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SHOW_SIGNAL_RECEPTIONS_VISIBILITY_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_RECEPTIONS_STEREOTYPES</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SHOW_RECEPTIONS_STEREOTYPES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_RECEPTIONS_PROPERTIES</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SHOW_RECEPTIONS_PROPERTIES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_RECEPTIONS_CONSTRAINTS</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SHOW_RECEPTIONS_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>RECEPTIONS_CONSTRAINTS_TEXT_MODE</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>RECEPTIONS_CONSTRAINTS_TEXT_MODE_DESCRIPTION</propertyDescriptionID>
						<value>EXPRESSION_MODE</value>
						<choice xmi:value='NAME_MODE^EXPRESSION_MODE^NAME_EXPRESSION_MODE'/>
						<index xmi:value='1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_RECEPTIONS_PARAMETERS_DIRECTION_KIND</propertyID>
						<propertyGroup>RECEPTIONS</propertyGroup>
						<propertyDescriptionID>SHOW_RECEPTIONS_PARAMETERS_DIRECTION_KIND_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_STRUCTURE</propertyID>
						<propertyDescriptionID>SUPPRESS_STRUCTURE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>FONT</propertyID>
						<propertyDescriptionID>FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='13'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_DEPLOYED_ELEMENTS</propertyID>
						<propertyDescriptionID>SUPPRESS_DEPLOYED_ELEMENTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>NodeInstance</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986293_382553_4016</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-3916'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-6714020'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>FONT</propertyID>
						<propertyDescriptionID>FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='13'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OBJECT_CLASS</propertyID>
						<propertyDescriptionID>SHOW_OBJECT_CLASS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_FULL_TYPE</propertyID>
						<propertyDescriptionID>SHOW_FULL_TYPE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_SPECIFICATION_VALUE</propertyID>
						<propertyDescriptionID>SHOW_SPECIFICATION_VALUE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_OBJECT_ATTRIBUTES</propertyID>
						<propertyDescriptionID>SUPPRESS_OBJECT_ATTRIBUTES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_DEPLOYED_ELEMENTS</propertyID>
						<propertyDescriptionID>SUPPRESS_DEPLOYED_ELEMENTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Note</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986293_374733_4017</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>HTML_TEXT</propertyID>
						<propertyDescriptionID>HTML_TEXT_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>TEXT_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>TEXT_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>SHOW_COMMENT</value>
						<choice xmi:value='SHOW_COMMENT^SHOW_DOCUMENTATION^NONE'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_LINE_BETWEEN_COMPARTMENTS</propertyID>
						<propertyDescriptionID>SHOW_LINE_BETWEEN_COMPARTMENTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_DOCUMENTATION_STEREOTYPES</propertyID>
						<propertyDescriptionID>SHOW_DOCUMENTATION_STEREOTYPES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES_STEREOTYPES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_STEREOTYPES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_QUALIFIED_NAME_IN_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_QUALIFIED_NAME_IN_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ELEMENT_PROPERTIES</propertyID>
						<propertyDescriptionID>SHOW_ELEMENT_PROPERTIES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-3916'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-6714020'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='3'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Note Anchor</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986294_652645_4018</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>LINK_LINE_STYLE</propertyID>
						<propertyDescriptionID>LINK_LINE_STYLE_DESCRIPTION</propertyDescriptionID>
						<value>OBLIQUE</value>
						<choice xmi:value='RECTILINEAR^OBLIQUE^BEZIER'/>
						<index xmi:value='1'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>ObjectFlow</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986294_939310_4019</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_A</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_A_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_B</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_B_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>IS_ROUNDED</propertyID>
						<propertyDescriptionID>IS_ROUNDED_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>OpaqueAction</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986294_778148_4020</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-1973821'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-6710948'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>OPAQUE_ACTION_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>OPAQUE_ACTION_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>SHOW_BODY</value>
						<choice xmi:value='SHOW_ACTION_NAME^SHOW_BODY'/>
						<index xmi:value='1'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>OutputPin</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986294_249543_4021</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>AUTOSIZE</propertyID>
						<propertyDescriptionID>AUTOSIZE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TYPE</propertyID>
						<propertyDescriptionID>SHOW_TYPE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_FULL_TYPE</propertyID>
						<propertyDescriptionID>SHOW_FULL_TYPE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>USE_FIXED_CONNECTION_POINTS</propertyID>
						<propertyDescriptionID>USE_FIXED_CONNECTION_POINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-1973821'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-6710948'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_PROPERTIES</propertyID>
						<propertyDescriptionID>SHOW_PROPERTIES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='5'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Package</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986294_680093_4022</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-2826753'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-9734759'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>FONT</propertyID>
						<propertyDescriptionID>FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='13'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>PACKAGE_HEADER_POSITION</propertyID>
						<propertyDescriptionID>PACKAGE_HEADER_POSITION_DESCRIPTION</propertyDescriptionID>
						<value>TOP</value>
						<choice xmi:value='TOP^IN_TAB'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ELEMENTS_LIST</propertyID>
						<propertyDescriptionID>SHOW_ELEMENTS_LIST_DESCRIPTION</propertyDescriptionID>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>PackageImport</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986294_46104_4023</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_A</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_A_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_B</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_B_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>PackageMerge</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986294_24081_4024</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_A</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_A_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_B</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_B_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Part</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986294_569525_4025</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-6714020'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OBJECT_CLASS</propertyID>
						<propertyDescriptionID>SHOW_OBJECT_CLASS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_FULL_TYPE</propertyID>
						<propertyDescriptionID>SHOW_FULL_TYPE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>TAGGED_VALUES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>TAGGED_VALUES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>ON_SHAPE</value>
						<choice xmi:value='ON_SHAPE^IN_COMPARTMENT^DO_NOT_DISPLAY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES_STEREOTYPES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_STEREOTYPES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_QUALIFIED_NAME_IN_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_QUALIFIED_NAME_IN_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_DEFAULT_PART_VALUE</propertyID>
						<propertyDescriptionID>SHOW_DEFAULT_PART_VALUE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_STRUCTURE</propertyID>
						<propertyDescriptionID>SUPPRESS_STRUCTURE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SHOW_SLOT_TYPE_ON_PART</propertyID>
						<propertyDescriptionID>SHOW_SLOT_TYPE_ON_PART_DESCRIPTION</propertyDescriptionID>
						<value>SHOW_TYPE_MODE_NONE</value>
						<choice xmi:value='SHOW_TYPE_MODE_NONE^SHOW_TYPE_MODE_NAME^SHOW_TYPE_MODE_QUALIFIED_NAME'/>
						<index xmi:value='0'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='false'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Paths</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986264_681073_3928</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986280_893953_3974</parentPropertyManager>
					<mdElement elementClass='NumberProperty'>
						<propertyID>LINE_WIDTH</propertyID>
						<propertyDescriptionID>LINE_WIDTH_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='1.0'/>
						<lowRange xmi:value='1.0'/>
						<highRange xmi:value='100.0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>USE_FILL_COLOR</propertyID>
						<propertyDescriptionID>USE_FILL_COLOR_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>LINK_LINE_STYLE</propertyID>
						<propertyDescriptionID>LINK_LINE_STYLE_DESCRIPTION</propertyDescriptionID>
						<value>RECTILINEAR</value>
						<choice xmi:value='RECTILINEAR^OBLIQUE^BEZIER'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>IS_ROUNDED</propertyID>
						<propertyDescriptionID>IS_ROUNDED_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>CONSTRAINT_TEXT_MODE</propertyID>
						<propertyDescriptionID>CONSTRAINT_TEXT_MODE_DESCRIPTION</propertyDescriptionID>
						<value>EXPRESSION_MODE</value>
						<choice xmi:value='NAME_MODE^EXPRESSION_MODE^NAME_EXPRESSION_MODE'/>
						<index xmi:value='1'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Port</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986295_931814_4026</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-10708633'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TYPE</propertyID>
						<propertyDescriptionID>SHOW_TYPE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_FULL_TYPE</propertyID>
						<propertyDescriptionID>SHOW_FULL_TYPE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-4336959'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='5'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_PROVIDED_INTERFACES</propertyID>
						<propertyDescriptionID>SHOW_PROVIDED_INTERFACES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_REQUIRED_INTERFACES</propertyID>
						<propertyDescriptionID>SHOW_REQUIRED_INTERFACES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>PrimitiveType</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986295_593858_4027</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-13159'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-6719140'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='3'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SHOW_MEMBERS_MODE</propertyID>
						<propertyDescriptionID>SHOW_MEMBERS_MODE_DESCRIPTION</propertyDescriptionID>
						<value>ALL</value>
						<choice xmi:value='ALL^ONLY_PUBLIC^NOT_PRIVATE'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_CLASS_ATTRIBUTES</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SUPPRESS_CLASS_ATTRIBUTES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>ATTRIBUTE_COLOR</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>ATTRIBUTE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-14155776'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>ATTRIBUTE_FONT</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>ATTRIBUTE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_MORE_SIGN_FOR_ATTRIBUTES</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_MORE_SIGN_FOR_ATTRIBUTES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SORT_CLASS_ATTRIBUTES_MODE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SORT_CLASS_ATTRIBUTES_MODE_DESCRIPTION</propertyDescriptionID>
						<value>NO_SORT</value>
						<choice xmi:value='NO_SORT^BY_NAME^BY_STEREOTYPE^BY_VISIBILITY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SHOW_ASSOCIATION_ENDS_MODE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ASSOCIATION_ENDS_MODE_DESCRIPTION</propertyDescriptionID>
						<value>DO_NOT_DISPLAY</value>
						<choice xmi:value='ALL^WITHOUT_ASSOCIATION^DO_NOT_DISPLAY'/>
						<index xmi:value='2'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_VISIBILITY</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_VISIBILITY_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_TYPE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_TYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_STEREOTYPE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_STEREOTYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_PROPERTIES</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_PROPERTIES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_CONSTRAINTS</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>ATTRIBUTES_CONSTRAINT_TEXT_MODE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>ATTRIBUTES_CONSTRAINT_TEXT_MODE_DESCRIPTION</propertyDescriptionID>
						<value>EXPRESSION_MODE</value>
						<choice xmi:value='NAME_MODE^EXPRESSION_MODE^NAME_EXPRESSION_MODE'/>
						<index xmi:value='1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_INIT_VALUE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_INIT_VALUE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_CLASS_OPERATIONS</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SUPPRESS_CLASS_OPERATIONS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>OPERATION_COLOR</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>OPERATION_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777176'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>OPERATION_FONT</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>OPERATION_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_SIGNATURE</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_SIGNATURE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_MORE_SIGN_FOR_OPERATIONS</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_MORE_SIGN_FOR_OPERATIONS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SORT_CLASS_OPERATIONS_MODE</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SORT_CLASS_OPERATIONS_MODE_DESCRIPTION</propertyDescriptionID>
						<value>NO_SORT</value>
						<choice xmi:value='NO_SORT^BY_NAME^BY_STEREOTYPE^BY_VISIBILITY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_VISIBILITY</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_VISIBILITY_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_STEREOTYPE</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_STEREOTYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_PROPERTIES</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_PROPERTIES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_CONSTRAINTS</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>OPERATIONS_CONSTRAINT_TEXT_MODE</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>OPERATIONS_CONSTRAINT_TEXT_MODE_DESCRIPTION</propertyDescriptionID>
						<value>EXPRESSION_MODE</value>
						<choice xmi:value='NAME_MODE^EXPRESSION_MODE^NAME_EXPRESSION_MODE'/>
						<index xmi:value='1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_FULL_TYPE</propertyID>
						<propertyDescriptionID>SHOW_FULL_TYPE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_OPERATIONS_PARAMETERS_DIRECTION_KIND</propertyID>
						<propertyGroup>OPERATIONS</propertyGroup>
						<propertyDescriptionID>SHOW_OPERATIONS_PARAMETERS_DIRECTION_KIND_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>TAGGED_VALUES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>TAGGED_VALUES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>ON_SHAPE</value>
						<choice xmi:value='ON_SHAPE^IN_COMPARTMENT^DO_NOT_DISPLAY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES_STEREOTYPES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_STEREOTYPES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_QUALIFIED_NAME_IN_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_QUALIFIED_NAME_IN_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>MEMBERS_WORD_WRAP</propertyID>
						<propertyDescriptionID>MEMBERS_WORD_WRAP_DESCRIPTION</propertyDescriptionID>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>ProfileApplication</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986295_612811_4028</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_A</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_A_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_B</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_B_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Protocol Transition</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986296_377250_4029</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_A</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_A_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_B</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_B_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Protocol TransitionToSelf</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986296_919192_4030</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_A</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_A_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_B</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_B_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>AUTOSIZE</propertyID>
						<propertyDescriptionID>AUTOSIZE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>USE_FIXED_CONNECTION_POINTS</propertyID>
						<propertyDescriptionID>USE_FIXED_CONNECTION_POINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Pseudostate</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986296_654697_4031</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>USE_FIXED_CONNECTION_POINTS</propertyID>
						<propertyDescriptionID>USE_FIXED_CONNECTION_POINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='3'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Realization</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986296_145532_4032</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_A</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_A_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_B</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_B_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>LINK_LINE_STYLE</propertyID>
						<propertyDescriptionID>LINK_LINE_STYLE_DESCRIPTION</propertyDescriptionID>
						<value>OBLIQUE</value>
						<choice xmi:value='RECTILINEAR^OBLIQUE^BEZIER'/>
						<index xmi:value='1'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>RectangularShape</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986296_350695_4033</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>USE_FILL_COLOR</propertyID>
						<propertyDescriptionID>USE_FILL_COLOR_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>HTML_TEXT</propertyID>
						<propertyDescriptionID>HTML_TEXT_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>TEXT_POSITION</propertyID>
						<propertyDescriptionID>TEXT_POSITION_DESCRIPTION</propertyDescriptionID>
						<value>LEFT</value>
						<choice xmi:value='CENTER^LEFT^RIGHT'/>
						<index xmi:value='1'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>LINE_STYLE</propertyID>
						<propertyDescriptionID>LINE_STYLE_DESCRIPTION</propertyDescriptionID>
						<value>DASHED</value>
						<choice xmi:value='DASHED^SOLID^DOTTED'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>ROUNDED</propertyID>
						<propertyDescriptionID>ROUNDED_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Role</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986296_711119_4034</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ROLE_NAME</propertyID>
						<propertyDescriptionID>SHOW_ROLE_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ROLE_NAVIGABILITY</propertyID>
						<propertyDescriptionID>SHOW_ROLE_NAVIGABILITY_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ROLE_VISIBILITY</propertyID>
						<propertyDescriptionID>SHOW_ROLE_VISIBILITY_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ROLE_MULTIPLICITY</propertyID>
						<propertyDescriptionID>SHOW_ROLE_MULTIPLICITY_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ROLE_PROPERTY_STRING</propertyID>
						<propertyDescriptionID>SHOW_ROLE_PROPERTY_STRING_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>RoleBinding</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986296_994489_4035</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_A</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_A_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_B</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_B_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>SendSignalAction</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986296_96264_4036</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-1973821'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-6710948'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>DIRECTION</propertyID>
						<propertyDescriptionID>DIRECTION_DESCRIPTION</propertyDescriptionID>
						<value>RIGHT</value>
						<choice xmi:value='RIGHT^LEFT'/>
						<index xmi:value='0'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Separator</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986297_777488_4037</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>USE_FILL_COLOR</propertyID>
						<propertyDescriptionID>USE_FILL_COLOR_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>HTML_TEXT</propertyID>
						<propertyDescriptionID>HTML_TEXT_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>TEXT_POSITION</propertyID>
						<propertyDescriptionID>TEXT_POSITION_DESCRIPTION</propertyDescriptionID>
						<value>LEFT</value>
						<choice xmi:value='CENTER^LEFT^RIGHT'/>
						<index xmi:value='1'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>LINE_STYLE</propertyID>
						<propertyDescriptionID>LINE_STYLE_DESCRIPTION</propertyDescriptionID>
						<value>DASHED</value>
						<choice xmi:value='DASHED^SOLID^DOTTED'/>
						<index xmi:value='0'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>SequenceNode</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986297_496119_4038</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-1973821'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-6710948'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='false'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Shapes</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986264_503370_3930</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986280_893953_3974</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>AUTOSIZE</propertyID>
						<propertyDescriptionID>AUTOSIZE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>USE_FIXED_CONNECTION_POINTS</propertyID>
						<propertyDescriptionID>USE_FIXED_CONNECTION_POINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_HEADER_IN_BOLD</propertyID>
						<propertyDescriptionID>SHOW_HEADER_IN_BOLD_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>QNAME_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>QNAME_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>QNAME_DISPLAY_MODE_DO_NOT_DISPLAY</value>
						<choice xmi:value='QNAME_DISPLAY_MODE_DO_NOT_DISPLAY^QNAME_DISPLAY_MODE_BELOW_NAME^QNAME_DISPLAY_MODE_MERGE_WITH_NAME^QNAME_DISPLAY_MODE_ABOVE_NAME'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>CONSTRAINT_TEXT_MODE</propertyID>
						<propertyDescriptionID>CONSTRAINT_TEXT_MODE_DESCRIPTION</propertyDescriptionID>
						<value>EXPRESSION_MODE</value>
						<choice xmi:value='NAME_MODE^EXPRESSION_MODE^NAME_EXPRESSION_MODE'/>
						<index xmi:value='1'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Signal</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986277_781675_3950</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-6719140'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_FULL_TYPE</propertyID>
						<propertyDescriptionID>SHOW_FULL_TYPE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SHOW_MEMBERS_MODE</propertyID>
						<propertyDescriptionID>SHOW_MEMBERS_MODE_DESCRIPTION</propertyDescriptionID>
						<value>ALL</value>
						<choice xmi:value='ALL^ONLY_PUBLIC^NOT_PRIVATE'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_CLASS_ATTRIBUTES</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SUPPRESS_CLASS_ATTRIBUTES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>ATTRIBUTE_COLOR</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>ATTRIBUTE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-14155776'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>ATTRIBUTE_FONT</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>ATTRIBUTE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_MORE_SIGN_FOR_ATTRIBUTES</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_MORE_SIGN_FOR_ATTRIBUTES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SORT_CLASS_ATTRIBUTES_MODE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SORT_CLASS_ATTRIBUTES_MODE_DESCRIPTION</propertyDescriptionID>
						<value>NO_SORT</value>
						<choice xmi:value='NO_SORT^BY_NAME^BY_STEREOTYPE^BY_VISIBILITY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SHOW_ASSOCIATION_ENDS_MODE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ASSOCIATION_ENDS_MODE_DESCRIPTION</propertyDescriptionID>
						<value>DO_NOT_DISPLAY</value>
						<choice xmi:value='ALL^WITHOUT_ASSOCIATION^DO_NOT_DISPLAY'/>
						<index xmi:value='2'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_VISIBILITY</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_VISIBILITY_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_TYPE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_TYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_STEREOTYPE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_STEREOTYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_PROPERTIES</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_PROPERTIES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_CONSTRAINTS</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>ATTRIBUTES_CONSTRAINT_TEXT_MODE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>ATTRIBUTES_CONSTRAINT_TEXT_MODE_DESCRIPTION</propertyDescriptionID>
						<value>EXPRESSION_MODE</value>
						<choice xmi:value='NAME_MODE^EXPRESSION_MODE^NAME_EXPRESSION_MODE'/>
						<index xmi:value='1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_INIT_VALUE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_INIT_VALUE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-13159'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>TAGGED_VALUES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>TAGGED_VALUES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>ON_SHAPE</value>
						<choice xmi:value='ON_SHAPE^IN_COMPARTMENT^DO_NOT_DISPLAY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='3'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES_STEREOTYPES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_STEREOTYPES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_QUALIFIED_NAME_IN_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_QUALIFIED_NAME_IN_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>MEMBERS_WORD_WRAP</propertyID>
						<propertyDescriptionID>MEMBERS_WORD_WRAP_DESCRIPTION</propertyDescriptionID>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>State</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986297_841251_4039</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_STATE_ACTIONS</propertyID>
						<propertyDescriptionID>SUPPRESS_STATE_ACTIONS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-6710948'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_REGION_NAME</propertyID>
						<propertyDescriptionID>SHOW_REGION_NAME_DESCRIPTION</propertyDescriptionID>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>StateInvariant</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986301_808814_4040</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='3'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Stereotype</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986302_155935_4041</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_FULL_TYPE</propertyID>
						<propertyDescriptionID>SHOW_FULL_TYPE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-6710948'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SHOW_MEMBERS_MODE</propertyID>
						<propertyDescriptionID>SHOW_MEMBERS_MODE_DESCRIPTION</propertyDescriptionID>
						<value>ALL</value>
						<choice xmi:value='ALL^ONLY_PUBLIC^NOT_PRIVATE'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_CLASS_ATTRIBUTES</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SUPPRESS_CLASS_ATTRIBUTES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>ATTRIBUTE_COLOR</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>ATTRIBUTE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-14155776'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>ATTRIBUTE_FONT</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>ATTRIBUTE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_MORE_SIGN_FOR_ATTRIBUTES</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_MORE_SIGN_FOR_ATTRIBUTES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SORT_CLASS_ATTRIBUTES_MODE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SORT_CLASS_ATTRIBUTES_MODE_DESCRIPTION</propertyDescriptionID>
						<value>NO_SORT</value>
						<choice xmi:value='NO_SORT^BY_NAME^BY_STEREOTYPE^BY_VISIBILITY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>SHOW_ASSOCIATION_ENDS_MODE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ASSOCIATION_ENDS_MODE_DESCRIPTION</propertyDescriptionID>
						<value>DO_NOT_DISPLAY</value>
						<choice xmi:value='ALL^WITHOUT_ASSOCIATION^DO_NOT_DISPLAY'/>
						<index xmi:value='2'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_VISIBILITY</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_VISIBILITY_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_TYPE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_TYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_STEREOTYPE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_STEREOTYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_PROPERTIES</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_PROPERTIES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ATTRIBUTES_CONSTRAINTS</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_ATTRIBUTES_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>ATTRIBUTES_CONSTRAINT_TEXT_MODE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>ATTRIBUTES_CONSTRAINT_TEXT_MODE_DESCRIPTION</propertyDescriptionID>
						<value>EXPRESSION_MODE</value>
						<choice xmi:value='NAME_MODE^EXPRESSION_MODE^NAME_EXPRESSION_MODE'/>
						<index xmi:value='1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_INIT_VALUE</propertyID>
						<propertyGroup>ATTRIBUTES</propertyGroup>
						<propertyDescriptionID>SHOW_INIT_VALUE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_BASE_CLASSES</propertyID>
						<propertyDescriptionID>SHOW_BASE_CLASSES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>TAGGED_VALUES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>TAGGED_VALUES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>ON_SHAPE</value>
						<choice xmi:value='ON_SHAPE^IN_COMPARTMENT^DO_NOT_DISPLAY'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='3'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES_STEREOTYPES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_STEREOTYPES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_QUALIFIED_NAME_IN_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_QUALIFIED_NAME_IN_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>MEMBERS_WORD_WRAP</propertyID>
						<propertyDescriptionID>MEMBERS_WORD_WRAP_DESCRIPTION</propertyDescriptionID>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='false'/>
					<extendableByStereotype xmi:value='true'/>
					<name>Stereotypes</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986302_509466_4042</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986280_893953_3974</parentPropertyManager>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>StructuredActivityNode</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986302_314409_4043</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-1973821'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-6710948'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Substitution</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986302_662934_4044</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_A</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_A_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_B</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_B_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Swimlane</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986302_688488_4045</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-1973821'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>USE_FILL_COLOR</propertyID>
						<propertyDescriptionID>USE_FILL_COLOR_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>PARTITION_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>PARTITION_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>SHOW_REPRESENTED_IF_EXISTS</value>
						<choice xmi:value='SHOW_REPRESENTED^SHOW_REPRESENTED_IF_EXISTS^SHOW_PARTITION_NAME^SHOW_BOTH'/>
						<index xmi:value='1'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>PARTITION_FULL_REPRESENTED_ELEMENT_SIGNATURE</propertyID>
						<propertyDescriptionID>PARTITION_FULL_REPRESENTED_ELEMENT_SIGNATURE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='false'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Symbol</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986280_893953_3974</propertyManagerID>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-52'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>USE_FILL_COLOR</propertyID>
						<propertyDescriptionID>USE_FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-12434878'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>TEXT_COLOR</propertyID>
						<propertyDescriptionID>TEXT_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>FONT</propertyID>
						<propertyDescriptionID>FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='PropertyManagerByDiagram'>
					<diagramType>SysML State Machine Diagram</diagramType>
					<removable xmi:value='true'/>
					<extendableByDiagram xmi:value='false'/>
					<extendableByStereotype xmi:value='false'/>
					<name>SysML State Machine Diagram</name>
					<propertyManagerID>_16_5_3_63b0213_1256146117962_512912_4146</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986280_659674_3973</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_ABBREVIATED_DIAGRAM_TYPE</propertyID>
						<propertyGroup>DIAGRAM_FRAME</propertyGroup>
						<propertyDescriptionID>SHOW_ABBREVIATED_DIAGRAM_TYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_DIAGRAM_TYPE</propertyID>
						<propertyGroup>DIAGRAM_FRAME</propertyGroup>
						<propertyDescriptionID>SHOW_DIAGRAM_TYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_PARAMETERS</propertyID>
						<propertyGroup>DIAGRAM_FRAME</propertyGroup>
						<propertyDescriptionID>SHOW_PARAMETERS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONTEXT_TYPE</propertyID>
						<propertyGroup>DIAGRAM_FRAME</propertyGroup>
						<propertyDescriptionID>SHOW_CONTEXT_TYPE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_FRAME_OWNER</propertyID>
						<propertyGroup>DIAGRAM_FRAME</propertyGroup>
						<propertyDescriptionID>SHOW_FRAME_OWNER_DESCRIPTION</propertyDescriptionID>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>TemplateBinding</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986302_297211_4046</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_A</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_A_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_B</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_B_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>TextBox</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986302_773244_4047</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>USE_FILL_COLOR</propertyID>
						<propertyDescriptionID>USE_FILL_COLOR_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>HTML_TEXT</propertyID>
						<propertyDescriptionID>HTML_TEXT_DESCRIPTION</propertyDescriptionID>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>TimeConstraint</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986302_862576_4048</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-1'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Transition</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986303_676456_4049</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_A</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_A_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_B</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_B_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>IS_ROUNDED</propertyID>
						<propertyDescriptionID>IS_ROUNDED_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>TransitionToSelf</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986303_821337_4050</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_A</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_A_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_B</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_B_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>AUTOSIZE</propertyID>
						<propertyDescriptionID>AUTOSIZE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>USE_FIXED_CONNECTION_POINTS</propertyID>
						<propertyDescriptionID>USE_FIXED_CONNECTION_POINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Tree</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986303_726636_4051</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='NumberProperty'>
						<propertyID>LINE_WIDTH</propertyID>
						<propertyDescriptionID>LINE_WIDTH_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='1.0'/>
						<lowRange xmi:value='1.0'/>
						<highRange xmi:value='100.0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_GENERALIZATION_SET</propertyID>
						<propertyDescriptionID>SHOW_GENERALIZATION_SET_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Usage</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986303_97020_4052</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_681073_3928</parentPropertyManager>
					<mdElement elementClass='ColorProperty'>
						<propertyID>STEREOTYPE_COLOR</propertyID>
						<propertyDescriptionID>STEREOTYPE_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-16777216'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>STEREOTYPE_FONT</propertyID>
						<propertyDescriptionID>STEREOTYPE_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='0'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_A</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_A_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONVEYED_B</propertyID>
						<propertyDescriptionID>SHOW_CONVEYED_B_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>LINK_LINE_STYLE</propertyID>
						<propertyDescriptionID>LINK_LINE_STYLE_DESCRIPTION</propertyDescriptionID>
						<value>OBLIQUE</value>
						<choice xmi:value='RECTILINEAR^OBLIQUE^BEZIER'/>
						<index xmi:value='1'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='PropertyManagerByDiagram'>
					<diagramType>Use Case Diagram</diagramType>
					<removable xmi:value='true'/>
					<extendableByDiagram xmi:value='false'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Use Case Diagram</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986303_99208_4053</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986286_233144_3983</parentPropertyManager>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>LINK_LINE_STYLE</propertyID>
						<propertyDescriptionID>LINK_LINE_STYLE_DESCRIPTION</propertyDescriptionID>
						<value>OBLIQUE</value>
						<choice xmi:value='RECTILINEAR^OBLIQUE^BEZIER'/>
						<index xmi:value='1'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='PropertyManagerByDiagram'>
					<diagramType>Use Case Diagram</diagramType>
					<removable xmi:value='true'/>
					<extendableByDiagram xmi:value='false'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Use Case Diagram</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986303_223678_4054</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986286_603394_3991</parentPropertyManager>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>LINK_LINE_STYLE</propertyID>
						<propertyDescriptionID>LINK_LINE_STYLE_DESCRIPTION</propertyDescriptionID>
						<value>OBLIQUE</value>
						<choice xmi:value='RECTILINEAR^OBLIQUE^BEZIER'/>
						<index xmi:value='1'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='PropertyManagerByDiagram'>
					<diagramType>Use Case Diagram</diagramType>
					<removable xmi:value='true'/>
					<extendableByDiagram xmi:value='false'/>
					<extendableByStereotype xmi:value='false'/>
					<name>Use Case Diagram</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986303_361273_4055</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986280_302295_3972</parentPropertyManager>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>LINK_LINE_STYLE</propertyID>
						<propertyDescriptionID>LINK_LINE_STYLE_DESCRIPTION</propertyDescriptionID>
						<value>OBLIQUE</value>
						<choice xmi:value='RECTILINEAR^OBLIQUE^BEZIER'/>
						<index xmi:value='1'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>UseCase</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986303_404721_4056</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>WRAP_WORDS</propertyID>
						<propertyDescriptionID>WRAP_WORDS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-10066361'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SUPPRESS_EXTENSIONS</propertyID>
						<propertyGroup>EXTENSION_POINTS</propertyGroup>
						<propertyDescriptionID>SUPPRESS_EXTENSIONS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>EXT_POINT_COLOR</propertyID>
						<propertyGroup>EXTENSION_POINTS</propertyGroup>
						<propertyDescriptionID>EXT_POINT_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-14155776'/>
					</mdElement>
					<mdElement elementClass='FontProperty'>
						<propertyID>EXT_POINT_FONT</propertyID>
						<propertyGroup>EXTENSION_POINTS</propertyGroup>
						<propertyDescriptionID>EXT_POINT_FONT_DESCRIPTION</propertyDescriptionID>
						<fontName>Arial</fontName>
						<size xmi:value='11'/>
						<style xmi:value='0'/>
					</mdElement>
				</mdElement>
				<mdElement elementClass='ExtendableManager'>
					<removable xmi:value='false'/>
					<extendableByDiagram xmi:value='true'/>
					<extendableByStereotype xmi:value='false'/>
					<name>ValuePin</name>
					<propertyManagerID>_16_5_3_63b0213_1269298986303_466762_4057</propertyManagerID>
					<parentPropertyManager>_16_5_3_63b0213_1269298986264_503370_3930</parentPropertyManager>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>AUTOSIZE</propertyID>
						<propertyDescriptionID>AUTOSIZE_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_NAME</propertyID>
						<propertyDescriptionID>SHOW_NAME_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TYPE</propertyID>
						<propertyDescriptionID>SHOW_TYPE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_FULL_TYPE</propertyID>
						<propertyDescriptionID>SHOW_FULL_TYPE_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>USE_FIXED_CONNECTION_POINTS</propertyID>
						<propertyDescriptionID>USE_FIXED_CONNECTION_POINTS_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>FILL_COLOR</propertyID>
						<propertyDescriptionID>FILL_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-1973821'/>
					</mdElement>
					<mdElement elementClass='ColorProperty'>
						<propertyID>PEN_COLOR</propertyID>
						<propertyDescriptionID>PEN_COLOR_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='-6710948'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_PROPERTIES</propertyID>
						<propertyDescriptionID>SHOW_PROPERTIES_DESCRIPTION</propertyDescriptionID>
						<value xmi:value='true'/>
					</mdElement>
					<mdElement elementClass='ChoiceProperty'>
						<propertyID>STEREOTYPES_DISPLAY_MODE</propertyID>
						<propertyDescriptionID>STEREOTYPES_DISPLAY_MODE_DESCRIPTION</propertyDescriptionID>
						<value>STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES</value>
						<choice xmi:value='STEREOTYPE_DISPLAY_MODE_TEXT_AND_ICON^STEREOTYPE_DISPLAY_MODE_TEXT^STEREOTYPE_DISPLAY_MODE_ICON^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE_AND_TEXT^STEREOTYPE_DISPLAY_MODE_SHAPE_IMAGE^STEREOTYPE_DISPLAY_MODE_DO_NOT_DISPLAY_STEREOTYPES'/>
						<index xmi:value='5'/>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_TAGGED_VALUES</propertyID>
						<propertyDescriptionID>SHOW_TAGGED_VALUES_DESCRIPTION</propertyDescriptionID>
					</mdElement>
					<mdElement elementClass='BooleanProperty'>
						<propertyID>SHOW_CONSTRAINTS</propertyID>
						<propertyDescriptionID>SHOW_CONSTRAINTS_DESCRIPTION</propertyDescriptionID>
					</mdElement>
				</mdElement>
			</mdElement>
		</mdElement>
</xmi:Extension>
</xmi:XMI>
"""

PREFACE_combi = """<?xml version='1.0' encoding='UTF-8'?>

<xmi:XMI xmlns:uml='http://www.omg.org/spec/UML/20131001' xmlns:xmi='http://www.omg.org/spec/XMI/20131001' xmlns:Validation_Profile='http://www.magicdraw.com/schemas/Validation_Profile.xmi' xmlns:MagicDraw_Profile='http://www.omg.org/spec/UML/20131001/MagicDrawProfile' xmlns:sysml='http://www.omg.org/spec/SysML/20131201/SysML' xmlns:StandardProfile='http://www.omg.org/spec/UML/20131001/StandardProfile' xmlns:DSL_Customization='http://www.magicdraw.com/schemas/DSL_Customization.xmi'>
	<xmi:Documentation>
		<xmi:exporter>MagicDraw UML</xmi:exporter>
		<xmi:exporterVersion>18.0</xmi:exporterVersion>
	</xmi:Documentation>
	<xmi:Extension extender='MagicDraw UML 18.0'>
		<plugin pluginName='SysML' pluginVersion='18.0'/>
		<plugin pluginName='Cameo Requirements Modeler' pluginVersion='18.0'/>
		<req_resource resourceID='1440' resourceName='SysML' resourceValueName='MD_customization_for_SysML.mdzip'/>
		<req_resource resourceID='1440' resourceName='SysML' resourceValueName='SysML State Machine Diagram'/>
		<req_resource resourceID='1480' resourceName='Cameo Requirements Modeler' resourceValueName='Cameo Requirements Modeler'/>
		<req_resource resourceID='1440' resourceName='SysML' resourceValueName='SysML'/>
		<stereotypesHREFS>
			<stereotype name='MagicDraw_Profile:DiagramInfo' stereotypeHREF='local:/PROJECT-877558e9224f114d50dea1f39a1c119?resource=com.nomagic.magicdraw.uml_umodel.shared_umodel#_9_0_be00301_1108044380615_150487_0'/>
			<tag name='MagicDraw_Profile:DiagramInfo:base_Element' tagID='_10_0EAPbeta_be00301_1123081772098_411862_275' tagURI='local:/PROJECT-877558e9224f114d50dea1f39a1c119?resource=com.nomagic.magicdraw.uml_umodel.shared_umodel#_10_0EAPbeta_be00301_1123081772098_411862_275'/>
			<tag name='MagicDraw_Profile:DiagramInfo:Creation_date' tagID='_be00301_1073306188629_537791_2' tagURI='local:/PROJECT-877558e9224f114d50dea1f39a1c119?resource=com.nomagic.magicdraw.uml_umodel.shared_umodel#_be00301_1073306188629_537791_2'/>
			<tag name='MagicDraw_Profile:DiagramInfo:Author' tagID='_be00301_1077726770128_871366_1' tagURI='local:/PROJECT-877558e9224f114d50dea1f39a1c119?resource=com.nomagic.magicdraw.uml_umodel.shared_umodel#_be00301_1077726770128_871366_1'/>
			<tag name='MagicDraw_Profile:DiagramInfo:Modification_date' tagID='_be00301_1073394345322_922552_1' tagURI='local:/PROJECT-877558e9224f114d50dea1f39a1c119?resource=com.nomagic.magicdraw.uml_umodel.shared_umodel#_be00301_1073394345322_922552_1'/>
			<tag name='MagicDraw_Profile:DiagramInfo:Last_modified_by' tagID='_16_8beta_8ca0285_1257244649124_794756_344' tagURI='local:/PROJECT-877558e9224f114d50dea1f39a1c119?resource=com.nomagic.magicdraw.uml_umodel.shared_umodel#_16_8beta_8ca0285_1257244649124_794756_344'/>
		</stereotypesHREFS>
	</xmi:Extension>
	<uml:Model xmi:type='uml:Model' xmi:id='eee_1045467100313_135436_1' name='Data'>
		<ownedComment xmi:type='uml:Comment' xmi:id='_16_5_3_63b0213_1256144971024_733598_327' xmi:uuid='3f55dbc9-1db3-401b-bdb0-302ea236a193' body='Author:TuLiP.&#10;Created:(automatically generated)'>
			<annotatedElement xmi:idref='eee_1045467100313_135436_1'/>
		</ownedComment>"""

END_combi = """	<xmi:Extension extender='MagicDraw UML 18.0'>
		<filePart name='proxy.local__PROJECT$h9b4d2b1641e6203934d95e7bde5fe08_resource_com$dnomagic$dmagicdraw$duml_umodel$dshared_umodel$dsnapshot' type='XML' header='&lt;?xml version=&quot;1.0&quot; encoding=&quot;ASCII&quot;?&gt;'>
<xmi:XMI xmi:version="2.0" xmlns:xmi="http://www.omg.org/XMI" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:uml="http://www.nomagic.com/magicdraw/UML/2.5">
  <uml:Package xmi:id="_12_0EAPbeta_be00301_1156851270584_552173_1" ID="_12_0EAPbeta_be00301_1156851270584_552173_1" name="MD Customization for SysML">
    <appliedStereotypeInstance xmi:id="_12_5EAPbeta2_be00301_1177500976392_281866_2496" ID="_12_5EAPbeta2_be00301_1177500976392_281866_2496">
      <classifier xsi:type="uml:Stereotype" href="#_12_1_8f90291_1173963323875_662612_98"/>
    </appliedStereotypeInstance>
  </uml:Package>
  <uml:Package xmi:id="magicdraw_uml_standard_profile_v_0001" ID="magicdraw_uml_standard_profile_v_0001" name="UML Standard Profile">
    <appliedStereotypeInstance xmi:id="_12_1_8f90291_1174411598625_504587_98" ID="_12_1_8f90291_1174411598625_504587_98">
      <classifier xsi:type="uml:Stereotype" href="#_12_1_8f90291_1173963323875_662612_98"/>
    </appliedStereotypeInstance>
    <packagedElement xsi:type="uml:Profile" xmi:id="_be00301_1073394351331_445580_2" ID="_be00301_1073394351331_445580_2" name="MagicDraw Profile">
      <packagedElement xsi:type="uml:Stereotype" xmi:id="_12_1_8f90291_1173963323875_662612_98" ID="_12_1_8f90291_1173963323875_662612_98" name="auxiliaryResource">
        <generalization xmi:id="_15_0_8f90291_1196866634537_680603_98" ID="_15_0_8f90291_1196866634537_680603_98">
          <general xsi:type="uml:Stereotype" href="#_9_0_be00301_1108044721245_236588_411"/>
        </generalization>
        <ownedAttribute xmi:id="_12_1_8f90291_1173963939937_52316_99" ID="_12_1_8f90291_1173963939937_52316_99" name="base_Package" visibility="private">
          <type xsi:type="uml:Class" href="#_9_0_62a020a_1105704885298_713292_7913"/>
        </ownedAttribute>
      </packagedElement>
      <packagedElement xsi:type="uml:Extension" xmi:id="_10_0EAPbeta_be00301_1123081772098_323897_274" ID="_10_0EAPbeta_be00301_1123081772098_323897_274">
        <memberEnd href="#_10_0EAPbeta_be00301_1123081772108_624594_276"/>
        <memberEnd href="#_10_0EAPbeta_be00301_1123081772098_411862_275"/>
        <ownedEnd xsi:type="uml:ExtensionEnd" xmi:id="_10_0EAPbeta_be00301_1123081772108_624594_276" ID="_10_0EAPbeta_be00301_1123081772108_624594_276" name="extension_InvisibleStereotype" visibility="private" aggregation="composite">
          <type xsi:type="uml:Stereotype" href="#_9_0_be00301_1108044721245_236588_411"/>
        </ownedEnd>
      </packagedElement>
      <packagedElement xsi:type="uml:Extension" xmi:id="_12_1_8f90291_1173963939937_323574_98" ID="_12_1_8f90291_1173963939937_323574_98">
        <memberEnd href="#_12_1_8f90291_1173963939937_399630_100"/>
        <memberEnd href="#_12_1_8f90291_1173963939937_52316_99"/>
        <ownedEnd xsi:type="uml:ExtensionEnd" xmi:id="_12_1_8f90291_1173963939937_399630_100" ID="_12_1_8f90291_1173963939937_399630_100" name="extension_auxiliaryResource" visibility="private" aggregation="composite">
          <type xsi:type="uml:Stereotype" href="#_12_1_8f90291_1173963323875_662612_98"/>
        </ownedEnd>
      </packagedElement>
      <packagedElement xsi:type="uml:Stereotype" xmi:id="_9_0_be00301_1108044721245_236588_411" ID="_9_0_be00301_1108044721245_236588_411" name="InvisibleStereotype">
        <ownedAttribute xmi:id="_10_0EAPbeta_be00301_1123081772098_411862_275" ID="_10_0EAPbeta_be00301_1123081772098_411862_275" name="base_Element" visibility="private">
          <type xsi:type="uml:Class" href="#_9_0_62a020a_1105704884807_371561_7741"/>
        </ownedAttribute>
      </packagedElement>
    </packagedElement>
    <packagedElement xsi:type="uml:Model" xmi:id="_9_0_be00301_1108053761194_467635_11463" ID="_9_0_be00301_1108053761194_467635_11463" name="UML2 Metamodel">
      <appliedStereotypeInstance xmi:id="_10_0EAPbeta_be00301_1123081771126_233373_95" ID="_10_0EAPbeta_be00301_1123081771126_233373_95">
        <classifier xsi:type="uml:Stereotype" href="#magicdraw_1046861421236_601240_36"/>
      </appliedStereotypeInstance>
      <packagedElement xsi:type="uml:Class" xmi:id="_9_0_62a020a_1105704885298_713292_7913" ID="_9_0_62a020a_1105704885298_713292_7913" name="Package"/>
      <packagedElement xsi:type="uml:Class" xmi:id="_9_0_62a020a_1105704884807_371561_7741" ID="_9_0_62a020a_1105704884807_371561_7741" name="Element"/>
      <packagedElement xsi:type="uml:Class" xmi:id="_9_0_62a020a_1105704920340_825592_9329" ID="_9_0_62a020a_1105704920340_825592_9329" name="Model"/>
    </packagedElement>
    <packagedElement xsi:type="uml:Profile" xmi:id="_9_0_be00301_1108050582343_527400_10847" ID="_9_0_be00301_1108050582343_527400_10847" name="StandardProfile">
      <packagedElement xsi:type="uml:Stereotype" xmi:id="magicdraw_1046861421236_601240_36" ID="magicdraw_1046861421236_601240_36" name="Metamodel">
        <ownedAttribute xmi:id="_10_0EAPbeta_be00301_1123081771136_271406_98" ID="_10_0EAPbeta_be00301_1123081771136_271406_98" name="base_Model" visibility="private">
          <type xsi:type="uml:Class" href="#_9_0_62a020a_1105704920340_825592_9329"/>
        </ownedAttribute>
      </packagedElement>
      <packagedElement xsi:type="uml:Extension" xmi:id="_10_0EAPbeta_be00301_1123081771136_824883_97" ID="_10_0EAPbeta_be00301_1123081771136_824883_97">
        <memberEnd href="#_10_0EAPbeta_be00301_1123081771136_580423_99"/>
        <memberEnd href="#_10_0EAPbeta_be00301_1123081771136_271406_98"/>
        <ownedEnd xsi:type="uml:ExtensionEnd" xmi:id="_10_0EAPbeta_be00301_1123081771136_580423_99" ID="_10_0EAPbeta_be00301_1123081771136_580423_99" name="extension_metamodel" visibility="private" aggregation="composite">
          <type xsi:type="uml:Stereotype" href="#magicdraw_1046861421236_601240_36"/>
        </ownedEnd>
      </packagedElement>
    </packagedElement>
  </uml:Package>
</xmi:XMI>
</filePart>
	</xmi:Extension>
	<xmi:Extension extender='MagicDraw UML 18.0'>
		<filePart name='com.nomagic.ci.metamodel.project' type='XML' header='&lt;?xml version=&quot;1.0&quot; encoding=&quot;ASCII&quot;?&gt;'>
<project:Project xmi:version="2.0" xmlns:xmi="http://www.omg.org/XMI" xmlns:project="http://www.nomagic.com/ns/cameo/client/project/1.0" xmi:id="_BYp6IG9pEeew-re8YLvkUg" description="" id="PROJECT-1d2013a62ce8e144232cbe10552e73">
  <ownedSections xmi:id="_BYrIQG9pEeew-re8YLvkUg" name="model" featuredBy="_BYqhMG9pEeew-re8YLvkUg"/>
  <ownedSections xmi:id="_BY4joG9pEeew-re8YLvkUg" name="commonprojectoptions" shared="true" featuredBy="_BY38kG9pEeew-re8YLvkUg"/>
  <ownedSections xmi:id="_BY4jpG9pEeew-re8YLvkUg" name="personalprojectoptions" shared="true" belongsTo="_BY4jo29pEeew-re8YLvkUg" featuredBy="_BY38kG9pEeew-re8YLvkUg"/>
  <userParts xmi:id="_BY4jo29pEeew-re8YLvkUg" user="_BY4jom9pEeew-re8YLvkUg" sections="_BY4jpG9pEeew-re8YLvkUg"/>
  <projectUsages xmi:id="_BZXEwm9pEeew-re8YLvkUg" usedProjectURI="file:/Applications/MagicDraw/profiles/UML_Standard_Profile.mdzip" readonly="true" preferredProjectRepositoryType="" loadedAutomatically="true" withPrivateDependencies="true">
    <usedProject href="PROJECT-877558e9224f114d50dea1f39a1c119?resource=com.nomagic.ci.metamodel.project#_VWTUgU_TEeCNOP_jel_PNg"/>
    <mountPoints xmi:id="_BvUtsG9pEeew-re8YLvkUg" sharePointID="magicdraw_uml_standard_profile_v_0001" containmentFeatureID="59" featureName="UML Model" containmentIndex="-1" containmentFeatureName="packagedElement">
      <mountedPoint href="PROJECT-877558e9224f114d50dea1f39a1c119?resource=com.nomagic.magicdraw.uml_umodel.shared_umodel#magicdraw_uml_standard_profile_v_0001"/>
      <mountedOn href="PROJECT-1d2013a62ce8e144232cbe10552e73?resource=com.nomagic.magicdraw.uml_umodel.model#eee_1045467100313_135436_1"/>
      <options xmi:id="_GJbYsG_xEeew-re8YLvkUg" key="preferredPath" value="::"/>
      <mountedSharePoint href="PROJECT-877558e9224f114d50dea1f39a1c119?resource=com.nomagic.ci.metamodel.project#_VbhywE_TEeCNOP_jel_PNg"/>
    </mountPoints>
    <properties xmi:id="_BZXEw29pEeew-re8YLvkUg" key="LOCAL_PROJECT_ID" value="PROJECT-877558e9224f114d50dea1f39a1c119"/>
    <properties xmi:id="_BpwRMm9pEeew-re8YLvkUg" key="usedVersion" value="18.0"/>
  </projectUsages>
  <projectUsages xmi:id="_BZZhAm9pEeew-re8YLvkUg" usedProjectURI="file:/Applications/MagicDraw/profiles/MD_customization_for_SysML.mdzip" readonly="true" preferredProjectRepositoryType="" loadedAutomatically="true" withPrivateDependencies="true">
    <usedProject href="PROJECT-9b4d2b1641e6203934d95e7bde5fe08?resource=com.nomagic.ci.metamodel.project#_obuDIG5dEeG47bdgtH4bfg"/>
    <mountPoints xmi:id="_BvUtsm9pEeew-re8YLvkUg" sharePointID="_12_0EAPbeta_be00301_1156851270584_552173_1" containmentFeatureID="59" featureName="UML Model" containmentIndex="-1" containmentFeatureName="packagedElement">
      <mountedPoint href="PROJECT-9b4d2b1641e6203934d95e7bde5fe08?resource=com.nomagic.magicdraw.uml_umodel.shared_umodel#_12_0EAPbeta_be00301_1156851270584_552173_1"/>
      <mountedOn href="PROJECT-1d2013a62ce8e144232cbe10552e73?resource=com.nomagic.magicdraw.uml_umodel.model#eee_1045467100313_135436_1"/>
      <options xmi:id="_GJbYsW_xEeew-re8YLvkUg" key="preferredPath" value="::"/>
      <mountedSharePoint href="PROJECT-9b4d2b1641e6203934d95e7bde5fe08?resource=com.nomagic.ci.metamodel.project#_oe2PoG5dEeG47bdgtH4bfg"/>
    </mountPoints>
    <properties xmi:id="_BZZhA29pEeew-re8YLvkUg" key="LOCAL_PROJECT_ID" value="PROJECT-9b4d2b1641e6203934d95e7bde5fe08"/>
    <properties xmi:id="_BpwRMG9pEeew-re8YLvkUg" key="loadIndex" value="true"/>
    <properties xmi:id="_BpwRMW9pEeew-re8YLvkUg" key="usedVersion" value="18.0"/>
  </projectUsages>
  <features xmi:id="_BYqhMG9pEeew-re8YLvkUg" name="UML Model" namespace="com.nomagic.magicdraw.uml_model" version="17.0" sections="_BYrIQG9pEeew-re8YLvkUg" internalVersion="1"/>
  <features xmi:id="_BY38kG9pEeew-re8YLvkUg" name="Project Options" namespace="com.nomagic.magicdraw.core.project.options" version="1.0" sections="_BY4joG9pEeew-re8YLvkUg _BY4jpG9pEeew-re8YLvkUg" internalVersion="1"/>
  <features xmi:id="_BpyGYG9pEeew-re8YLvkUg" name="Language Properties" namespace="com.nomagic.magicdraw.ce.languageproperties" version="1.0" internalVersion="1"/>
  <features xmi:id="_BpyGYW9pEeew-re8YLvkUg" name="Code Engineering" namespace="com.nomagic.magicdraw.ce" version="1.0" internalVersion="1"/>
  <properties xmi:id="_BZGmEG9pEeew-re8YLvkUg" key="standardProfile" value="false"/>
  <properties xmi:id="_BZGmEW9pEeew-re8YLvkUg" key="internalVersion" value="-1"/>
  <properties xmi:id="_zpNSIG9pEeew-re8YLvkUg" key="exporterDescription" value="ac ed 0 5 73 72 0 2e 63 6f 6d 2e 6e 6f 6d 61 67 69 63 2e 70 65 72 73 69 73 74 65 6e 63 65 2e 58 6d 69 45 78 70 6f 72 74 65 72 44 65 73 63 72 69 70 74 69 6f 6e f5 3e fd c8 e7 3c 3b d7 2 0 5 4c 0 5 6d 4e 61 6d 65 74 0 12 4c 6a 61 76 61 2f 6c 61 6e 67 2f 53 74 72 69 6e 67 3b 4c 0 12 6d 52 65 71 75 69 72 65 64 50 6c 75 67 69 6e 4d 61 70 74 0 f 4c 6a 61 76 61 2f 75 74 69 6c 2f 4d 61 70 3b 4c 0 12 6d 52 65 71 75 69 72 65 64 52 65 73 6f 75 72 63 65 73 74 0 10 4c 6a 61 76 61 2f 75 74 69 6c 2f 4c 69 73 74 3b 4c 0 10 6d 55 4d 4c 4e 61 6d 65 73 70 61 63 65 55 52 49 71 0 7e 0 1 4c 0 8 6d 56 65 72 73 69 6f 6e 71 0 7e 0 1 78 70 74 0 d 4d 61 67 69 63 44 72 61 77 20 55 4d 4c 73 72 0 11 6a 61 76 61 2e 75 74 69 6c 2e 48 61 73 68 4d 61 70 5 7 da c1 c3 16 60 d1 3 0 2 46 0 a 6c 6f 61 64 46 61 63 74 6f 72 49 0 9 74 68 72 65 73 68 6f 6c 64 78 70 3f 40 0 0 0 0 0 3 77 8 0 0 0 4 0 0 0 2 74 0 5 53 79 73 4d 4c 74 0 4 31 38 2e 30 74 0 1a 43 61 6d 65 6f 20 52 65 71 75 69 72 65 6d 65 6e 74 73 20 4d 6f 64 65 6c 65 72 74 0 4 31 38 2e 30 78 73 72 0 13 6a 61 76 61 2e 75 74 69 6c 2e 41 72 72 61 79 4c 69 73 74 78 81 d2 1d 99 c7 61 9d 3 0 1 49 0 4 73 69 7a 65 78 70 0 0 0 4 77 4 0 0 0 4 73 72 0 32 63 6f 6d 2e 6e 6f 6d 61 67 69 63 2e 70 65 72 73 69 73 74 65 6e 63 65 2e 52 65 71 75 69 72 65 64 52 65 73 6f 75 72 63 65 44 65 73 63 72 69 70 74 6f 72 da cf 46 1f 32 8 f0 c5 2 0 3 49 0 3 6d 49 64 4c 0 5 6d 4e 61 6d 65 71 0 7e 0 1 4c 0 6 6d 56 61 6c 75 65 71 0 7e 0 1 78 70 0 0 5 a0 74 0 5 53 79 73 4d 4c 74 0 20 4d 44 5f 63 75 73 74 6f 6d 69 7a 61 74 69 6f 6e 5f 66 6f 72 5f 53 79 73 4d 4c 2e 6d 64 7a 69 70 73 71 0 7e 0 e 0 0 5 a0 71 0 7e 0 10 74 0 1b 53 79 73 4d 4c 20 53 74 61 74 65 20 4d 61 63 68 69 6e 65 20 44 69 61 67 72 61 6d 73 71 0 7e 0 e 0 0 5 c8 74 0 1a 43 61 6d 65 6f 20 52 65 71 75 69 72 65 6d 65 6e 74 73 20 4d 6f 64 65 6c 65 72 71 0 7e 0 a 73 71 0 7e 0 e 0 0 5 a0 71 0 7e 0 10 71 0 7e 0 8 78 70 74 0 4 31 38 2e 30 "/>
  <properties xmi:id="_zpOgQG9pEeew-re8YLvkUg" key="fileVersion" value="5"/>
  <properties xmi:id="_zpUm4G9pEeew-re8YLvkUg" key="MODEL_ROOT_HREF" value="local:/PROJECT-1d2013a62ce8e144232cbe10552e73?resource=com.nomagic.magicdraw.uml_umodel.model#eee_1045467100313_135436_1"/>
  <properties xmi:id="_zprMMG9pEeew-re8YLvkUg" key="MODULES_DIRS" value="&lt;project.dir>&lt;>&lt;install.root>/profiles&lt;>&lt;install.root>/modelLibraries"/>
  <properties xmi:id="_zqGC8G9pEeew-re8YLvkUg" key="CI_VERSION" value="V1702_SP1"/>
  <projectUsers xmi:id="_BY4jom9pEeew-re8YLvkUg" userId="default"/>
</project:Project>
</filePart>
	</xmi:Extension>
	<xmi:Extension extender='MagicDraw UML 18.0'>
		<filePart name='proxy.local__PROJECT$h877558e9224f114d50dea1f39a1c119_resource_com$dnomagic$dmagicdraw$duml_umodel$dshared_umodel$dsnapshot' type='XML' header='&lt;?xml version=&quot;1.0&quot; encoding=&quot;ASCII&quot;?&gt;'>
<uml:Package xmi:version="2.0" xmlns:xmi="http://www.omg.org/XMI" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:uml="http://www.nomagic.com/magicdraw/UML/2.5" xmi:id="magicdraw_uml_standard_profile_v_0001" ID="magicdraw_uml_standard_profile_v_0001" name="UML Standard Profile">
  <appliedStereotypeInstance xmi:id="_12_1_8f90291_1174411598625_504587_98" ID="_12_1_8f90291_1174411598625_504587_98" classifier="_12_1_8f90291_1173963323875_662612_98"/>
  <packagedElement xsi:type="uml:Profile" xmi:id="_be00301_1073394351331_445580_2" ID="_be00301_1073394351331_445580_2" name="MagicDraw Profile">
    <packagedElement xsi:type="uml:Stereotype" xmi:id="_12_1_8f90291_1173963323875_662612_98" ID="_12_1_8f90291_1173963323875_662612_98" name="auxiliaryResource">
      <generalization xmi:id="_15_0_8f90291_1196866634537_680603_98" ID="_15_0_8f90291_1196866634537_680603_98" general="_9_0_be00301_1108044721245_236588_411"/>
      <ownedAttribute xmi:id="_12_1_8f90291_1173963939937_52316_99" ID="_12_1_8f90291_1173963939937_52316_99" name="base_Package" visibility="private" type="_9_0_62a020a_1105704885298_713292_7913"/>
    </packagedElement>
    <packagedElement xsi:type="uml:Extension" xmi:id="_10_0EAPbeta_be00301_1123081772098_323897_274" ID="_10_0EAPbeta_be00301_1123081772098_323897_274" memberEnd="_10_0EAPbeta_be00301_1123081772108_624594_276 _10_0EAPbeta_be00301_1123081772098_411862_275">
      <ownedEnd xsi:type="uml:ExtensionEnd" xmi:id="_10_0EAPbeta_be00301_1123081772108_624594_276" ID="_10_0EAPbeta_be00301_1123081772108_624594_276" name="extension_InvisibleStereotype" visibility="private" type="_9_0_be00301_1108044721245_236588_411" aggregation="composite"/>
    </packagedElement>
    <packagedElement xsi:type="uml:Extension" xmi:id="_12_1_8f90291_1173963939937_323574_98" ID="_12_1_8f90291_1173963939937_323574_98" memberEnd="_12_1_8f90291_1173963939937_399630_100 _12_1_8f90291_1173963939937_52316_99">
      <ownedEnd xsi:type="uml:ExtensionEnd" xmi:id="_12_1_8f90291_1173963939937_399630_100" ID="_12_1_8f90291_1173963939937_399630_100" name="extension_auxiliaryResource" visibility="private" type="_12_1_8f90291_1173963323875_662612_98" aggregation="composite"/>
    </packagedElement>
    <packagedElement xsi:type="uml:Stereotype" xmi:id="_9_0_be00301_1108044721245_236588_411" ID="_9_0_be00301_1108044721245_236588_411" name="InvisibleStereotype">
      <ownedAttribute xmi:id="_10_0EAPbeta_be00301_1123081772098_411862_275" ID="_10_0EAPbeta_be00301_1123081772098_411862_275" name="base_Element" visibility="private" type="_9_0_62a020a_1105704884807_371561_7741"/>
    </packagedElement>
    <packagedElement xsi:type="uml:Stereotype" xmi:id="_9_0_be00301_1108044380615_150487_0" ID="_9_0_be00301_1108044380615_150487_0" name="DiagramInfo">
      <generalization xmi:id="_9_0_be00301_1108044989070_469307_436" ID="_9_0_be00301_1108044989070_469307_436" general="_9_0_be00301_1108044721245_236588_411"/>
      <ownedAttribute xmi:id="_be00301_1073306188629_537791_2" ID="_be00301_1073306188629_537791_2" name="Creation date" visibility="private" type="_be00301_1073305590699_364818_1"/>
      <ownedAttribute xmi:id="_be00301_1077726770128_871366_1" ID="_be00301_1077726770128_871366_1" name="Author" visibility="private" type="_9_0_2_91a0295_1110274713995_297054_0"/>
      <ownedAttribute xmi:id="_be00301_1073394345322_922552_1" ID="_be00301_1073394345322_922552_1" name="Modification date" visibility="private" type="_be00301_1073305590699_364818_1"/>
      <ownedAttribute xmi:id="_10_0EAPbeta_be00301_1123081772498_901864_356" ID="_10_0EAPbeta_be00301_1123081772498_901864_356" name="base_Diagram" visibility="private" type="_9_0_62a020a_1106296071977_61607_0"/>
      <ownedAttribute xmi:id="_16_8beta_8ca0285_1257244649124_794756_344" ID="_16_8beta_8ca0285_1257244649124_794756_344" name="Last modified by" visibility="private" type="_9_0_2_91a0295_1110274713995_297054_0"/>
    </packagedElement>
    <packagedElement xsi:type="uml:Package" xmi:id="_9_0_2_be00301_1111670217596_336168_627" ID="_9_0_2_be00301_1111670217596_336168_627" name="datatypes">
      <packagedElement xsi:type="uml:DataType" xmi:id="_be00301_1073305590699_364818_1" ID="_be00301_1073305590699_364818_1" name="date"/>
    </packagedElement>
    <packagedElement xsi:type="uml:Extension" xmi:id="_10_0EAPbeta_be00301_1123081772498_531863_355" ID="_10_0EAPbeta_be00301_1123081772498_531863_355" memberEnd="_10_0EAPbeta_be00301_1123081772498_435993_357 _10_0EAPbeta_be00301_1123081772498_901864_356">
      <ownedEnd xsi:type="uml:ExtensionEnd" xmi:id="_10_0EAPbeta_be00301_1123081772498_435993_357" ID="_10_0EAPbeta_be00301_1123081772498_435993_357" name="extension_DiagramInfo" visibility="private" type="_9_0_be00301_1108044380615_150487_0" aggregation="composite"/>
    </packagedElement>
  </packagedElement>
  <packagedElement xsi:type="uml:Model" xmi:id="_9_0_be00301_1108053761194_467635_11463" ID="_9_0_be00301_1108053761194_467635_11463" name="UML2 Metamodel">
    <appliedStereotypeInstance xmi:id="_10_0EAPbeta_be00301_1123081771126_233373_95" ID="_10_0EAPbeta_be00301_1123081771126_233373_95" classifier="magicdraw_1046861421236_601240_36"/>
    <packagedElement xsi:type="uml:Class" xmi:id="_9_0_62a020a_1105704885298_713292_7913" ID="_9_0_62a020a_1105704885298_713292_7913" name="Package"/>
    <packagedElement xsi:type="uml:Class" xmi:id="_9_0_62a020a_1105704884807_371561_7741" ID="_9_0_62a020a_1105704884807_371561_7741" name="Element"/>
    <packagedElement xsi:type="uml:Class" xmi:id="_9_0_62a020a_1105704920340_825592_9329" ID="_9_0_62a020a_1105704920340_825592_9329" name="Model"/>
    <packagedElement xsi:type="uml:Package" xmi:id="_12_0EAPbeta_be00301_1157529392394_202602_1" ID="_12_0EAPbeta_be00301_1157529392394_202602_1" name="PrimitiveTypes">
      <packagedElement xsi:type="uml:PrimitiveType" xmi:id="_9_0_2_91a0295_1110274713995_297054_0" ID="_9_0_2_91a0295_1110274713995_297054_0" name="String"/>
    </packagedElement>
    <packagedElement xsi:type="uml:Class" xmi:id="_9_0_62a020a_1106296071977_61607_0" ID="_9_0_62a020a_1106296071977_61607_0" name="Diagram"/>
  </packagedElement>
  <packagedElement xsi:type="uml:Profile" xmi:id="_9_0_be00301_1108050582343_527400_10847" ID="_9_0_be00301_1108050582343_527400_10847" name="StandardProfile">
    <packagedElement xsi:type="uml:Stereotype" xmi:id="magicdraw_1046861421236_601240_36" ID="magicdraw_1046861421236_601240_36" name="Metamodel">
      <ownedAttribute xmi:id="_10_0EAPbeta_be00301_1123081771136_271406_98" ID="_10_0EAPbeta_be00301_1123081771136_271406_98" name="base_Model" visibility="private" type="_9_0_62a020a_1105704920340_825592_9329"/>
    </packagedElement>
    <packagedElement xsi:type="uml:Extension" xmi:id="_10_0EAPbeta_be00301_1123081771136_824883_97" ID="_10_0EAPbeta_be00301_1123081771136_824883_97" memberEnd="_10_0EAPbeta_be00301_1123081771136_580423_99 _10_0EAPbeta_be00301_1123081771136_271406_98">
      <ownedEnd xsi:type="uml:ExtensionEnd" xmi:id="_10_0EAPbeta_be00301_1123081771136_580423_99" ID="_10_0EAPbeta_be00301_1123081771136_580423_99" name="extension_metamodel" visibility="private" type="magicdraw_1046861421236_601240_36" aggregation="composite"/>
    </packagedElement>
  </packagedElement>
</uml:Package>
</filePart>
	</xmi:Extension>
	<xmi:Extension extender='MagicDraw UML 18.0'>
		<filePart name='Binaries.properties' type='BINARY'>H4sIAAAAAAAAAC3KvQrCMBRA4b1PEejqDb35adKCg+Kig4i6OElybypC04BQfH1LcfngwKmr+jZP4jSPQmmBprfYaysuh7tQDbqKSpZTyeH1JrnKn/CVcx6fuXAa5ep2fzzvrg/QnWGrIgEN2oEhm8BHtcCRnQ9tkzxv/q8JeqDONKAi01LtAD5ggtY71J4QVbTVDz3KOFqeAAAA</filePart>
	</xmi:Extension>
	<xmi:Extension extender='MagicDraw UML 18.0'>
		<filePart name='com.nomagic.magicdraw.core.project.options.commonprojectoptions' type='XML' header='&lt;?xml version=&quot;1.0&quot; encoding=&quot;ASCII&quot;?&gt;'>
<project.options:CommonProjectOptions xmi:version="2.0" xmlns:xmi="http://www.omg.org/XMI" xmlns:project.options="http://www.nomagic.com/ns/magicdraw/core/project/options/1.0" xmi:id="_BY4joW9pEeew-re8YLvkUg" optionsString="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" modelElementStyleString="UEsDBBQACAgIAHF290oAAAAAAAAAAAAAAAAAAAAAdY5BC4IwGEDP+iu87VTWLWJTJOdJK3AGnWToZwy2KdsU/fdpQbdO7/LgPRzPSgYTGCt6TdBxf0AB6KZvhX4RVLFsd0Jx5Pv4bvoBjFsewgrXm6RpYFgZ+R5WLZWgQLsAvrxIbi1BpVCDhNItEtDqeVhzBVHJnjmti1tK85rmtKBXVqc0S6qclTj8KJvbQsdH6YJZifPE5QgEdVxaQOGWDH/NyMfhv7c3UEsHCKB+0BCoAAAA3QAAAFBLAQIUABQACAgIAHF290qgftAQqAAAAN0AAAAAAAAAAAAAAAAAAAAAAAAAAABQSwUGAAAAAAEAAQAuAAAA1gAAAAAA" symbolStylesString="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"/>
</filePart>
	</xmi:Extension>
	<xmi:Extension extender='MagicDraw UML 18.0'>
		<filePart name='Records.properties' type='BINARY'>H4sIAAAAAAAAAL1VS0/cMBC+51dEItdE8SsPpByA9lAOLaJcOEWOZ9J1lcSR4227/76GzQJalpaIhcvIHn8z4/lmPD65MP0onW50p90mxMHZTXDyfT2El+supCwk/FSQUybCq083IU1JHoxoJzPILlamTwbTyx9aJfcSrPydKGMxGa35icolZnTaDFOys5n1s7o6nqvg/MvXs+vbmEvWqpKnMW1A+V3WxoUkGGdFTlihCKGNqBZgg6vrb5efL25iAj55JjOqsEDCOWVUNUhSISjmrHodLHiap9JJj072BrDbZVn9D7Dvwav/bJJpkOO0Mi4BnJTVozP2yXLa9/oqo2CL6oySXV3P+UWrIs+FKLCklLeEcBApoCQtKyXxjJW1xcmsrcLax4xgDhqB0hE8JBPBnE0Eu0tUHxrtsYfP9SCtxumOE690fln96/AZ/x6rJ4eDwu3lZ3JHq39Jh4AjDuBPN51HPavDEuPj1uPhkUWw7rt6PTM1raRFeNy+S3WWxQ4WzAYP7c2wN2TeaB8capFDnXGYo7LhQBuScYIZTVnJOJQC8wZQtJgWR34v7xTthRrcVW87ne7lC0zvoY7L01H6+ENi734oVvqHQhsVq5blMVcC46KhXkADeSGzFAuoFmCDvzjXxCnDBwAA</filePart>
	</xmi:Extension>
</xmi:XMI>"""



