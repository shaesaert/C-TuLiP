""" Symbolic Mealy machine class and methods:
Based on first order wrapper of Omega (https://github.com/johnyf/omega)
"""


import logging
import pprint

try:
    from dd import cudd as _bdd
except ImportError:
    from dd import bdd as _bdd
from omega.symbolic.fol import Context
from omega.logic import bitvector as bv
from omega.logic import syntax as stx
from omega.symbolic import bdd as sym_bdd
from omega.symbolic import enumeration as enum


log = logging.getLogger(__name__)


class SMealy(Context):
    """ Mealy machine with set-valued expression for transitions.

    Set are expressed with bdd and a first-order interface to tje binary decision diagram is used

    """
    def __init__(self):
        """Instantiate first-order context."""
        Context.__init__(self)

        self.N  = dict() # the variable name of the state variable of the Mealy  machine
        self.X  = dict() # the variable name of the inputs
        self.Y  = dict() # the variable name of the outputs

        self.T = None    # the node of the bdd representing the transition relation
        self.n0 = None   # the initial state of the Mealy machine
