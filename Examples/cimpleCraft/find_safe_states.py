import numpy as np
import polytope
from Interface import Statechart as dumpsmach
def unit_ball(rho, n):
    return rho
def pontryagin_difference(R,W):
    return R
def prev_step_invariant_set(R,X,W, rho_B):
    R = pontryagin_difference(R,W)
    #new polytope
    #R.HA R.HB \leq R.g
    #HUset \leq GUset
    #project on x dimensions
    return R
def find_safe_states(disc_dynamics, sys_dinamics):
    """
    We compute the inner approximation of the invariant set, based on the algorithm proposed in:
    https://arxiv.org/pdf/1601.00416.pdf
    :param disc_dynamics:
    :return:
    """
    drop_polytopes = []
    for region in disc_dynamics.ppp.regions:
        rho = 1
        rho_B = unit_ball(rho, n)
        for polytope in region:
            X  = polytope.union(X,polytope)
            R = X
            preR = prev_step_invariant_set(R, X, W, rho_B)
            while polytope.is_subset(R,):
                R = preR
                preR = prev_step_invariant_set(R, X, W, rho_B)
            if R == None:
                disc_dynamics.ppp.regions.remove(polytope)
            else:
                polytope_safe.append(R)