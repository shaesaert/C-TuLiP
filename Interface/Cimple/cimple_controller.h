//
// Created by L. Jonathan Feldstein
//

#ifndef CIMPLE_CIMPLE_CONTROLLER_H
#define CIMPLE_CIMPLE_CONTROLLER_H

#include <stddef.h>
#include <math.h>
#include "cimple_system.h"
#include <gsl/gsl_matrix.h>
#include <gsl/gsl_blas.h>
#include "cimple_polytope_library.h"
#include <pthread.h>

/**
 * @brief Action to get plant from current cell to target cell.
 *
 * @param target target region the plant is supposed to reach
 * @param now current state of the plant
 * @param d_dyn discrete abstraction of the system
 * @param s_dyn system dynamics including auxiliary matrices
 * @param f_cost cost function to be minimized on the path
 */
void ACT(int target,
         current_state * now,
         discrete_dynamics * d_dyn,
         system_dynamics * s_dyn,
         cost_function * f_cost,
         double sec);
/**
 * @brief Apply the calculated control to the current state using system dynamics
 * @param x current state at time [0]
 * @param u matrix with next N inputs calculated by the MPC controller
 * @param A system dynamics
 * @param B input dynamics
 */
void apply_control(gsl_vector *x,
                   gsl_matrix *u,
                   gsl_matrix *A,
                   gsl_matrix *B,
                   gsl_matrix *E,
                   gsl_vector *w,
                   size_t current_time);

/**
 * @brief Generates random numbers with normal distribution
 * @param mu
 * @param sigma
 * @return
 */
double randn (double mu,
              double sigma);

/**
 * Fill a vector with gaussian distributed noise
 * @param w
 */
void get_disturbance(gsl_vector *w,
                     double mu,
                     double sigma);
/**
 * @brief Calculate (optimal) input that will be applied to take plant from current state (now) to target_cell.
 *
 * Global function to compute continuous control input for discrete transition.
 *
 * Computes continuous control input sequence which takes the plant:
 *
 *      - from now
 *      - to (chebyshev center of) target_cell
 *      => partitions given by discrete dynamics (d_dyn)
 *
 * Control input is calculated such that it minimizes:
 *
 *      f(x, u) = |Rx|_{ord} + |Qu|_{ord} + r'x + distance_error_weight * |xc - x(N)|_{ord}
 *      with xc == chebyshev center of target_cell
 *
 *    Notes
 *    =====
 *    1. The same horizon length as in reachability analysis
 *    should be used in order to guarantee feasibility.
 *
 *    2. If the closed loop algorithm has been used
 *    to compute reachability the input needs to be
 *    recalculated for each time step
 *    (with decreasing horizon length).
 *
 *    In this case only u(0) should be used as
 *    a control signal and u(1) ... u(N-1) discarded.
 *
 *    3. The "conservative" calculation makes sure that
 *    the plant remains inside the convex hull of the
 *    starting region during execution, i.e.::
 *
 *    x(1), x(2) ...  x(N-1) are in starting region.
 *
 *    If the original proposition preserving partition
 *    is not convex, then safety cannot be guaranteed.
 *
 * @param low_u row k contains the control input: u(k) dim[N x m]
 * @param now initial continuous state
 * @param d_dyn discrete abstraction of system
 * @param s_dyn system dynamics (including auxiliary matrices)
 * @param target_cell index of target region in discrete dynamics (d_dyn)
 * @param f_cost cost func matrices: f(x, u) = |Rx|_{ord} + |Qu|_{ord} + r'x + distance_error_weight *|xc - x(N)|_{ord}
 */
void get_input (gsl_matrix *u,
                current_state * now,
                discrete_dynamics *d_dyn,
                system_dynamics *s_dyn,
                int target_cell,
                cost_function * f_cost,
                size_t current_time_horizon);


/**
 * @brief Calculates (optimal) input to reach desired state (P3) from current state (now) through convex optimization
 *
 * Calculate the sequence low_u such that:
 *
 *      - x(t+1) = A x(t) + B u(t) + K
 *      - x(k) in P1 for k = 0,...,N-1 (if closed loop == 'true')
 *      - x(N) in P3
 *      - [u(k); x(k)] always obey s_dyn.Uset
 *
 * Actual optimality is compared in get_input()
 *
 *
 * @param low_u currently optimal calculated input to target region (input to beat)
 * @param now current state
 * @param s_dyn system dynamics (including auxiliary matrices)
 * @param P1 current polytope (or hull of region) the system is in
 * @param P3 a polytope from the target region
 * @param ord ordinance of the norm that should be minimized ord in {1, 2, INFINITY} (currently only '2' is possible)
 * @param closed_loop if 'true' only u[0] will actually be applied all other inputs will be discarded
 * @param time_horizon
 * @param f_cost predefined cost functions |Rx|_{ord} + |Qu|_{ord} + r'x + mid_weight * |xc - x(N)|_{ord}
 * @param low_cost cost associate to low_u
 */
void search_better_path(gsl_matrix *low_u,
                        current_state *now,
                        system_dynamics *s_dyn,
                        polytope *P1,
                        polytope *P3,
                        int ord,
                        int closed_loop,
                        size_t time_horizon,
                        cost_function * f_cost,
                        double* low_cost);

/**
 * @brief Calculate recursively polytope (return_polytope) system needs to be in, to reach P2 in one time step
 * @param return_polytope empty polytope
 * @param P1 polytope in which the system is currently (at time [0]) might be several time steps away from P2
 * @param P2 last recursively calculated polytope
 * @param s_dyn system dynamics (including auxiliary matrices)
 */
poly_t * solve_feasible_closed_loop(poly_t *p_universe,
                                    polytope *P1,
                                    polytope *P2,
                                    system_dynamics *s_dyn,
                                    matrix_t * constraints);


/**
 * @brief Compute a polytope that constraints the system over the next N time steps to fullfill the GR(1) specifications
 *
 * @param L_full empty matrix when passed in, left side of constraint polytope at the end
 * @param M_full empty vector when passed in, right side of constraint polytope at the end
 * @param s_dyn system dynamics (including auxiliary matrices)
 * @param list_polytopes list of N+1 polytopes in which the systems needs to be in to reach new desired state at time N
 * @param N time horizon
 *
 * Compute the components of the polytope:
 *
 *      L [x(0)' u(0)' ... u(N-1)']' <= M
 *
 * which stacks the following constraints:
 *
 *      - x(t+1) = A x(t) + B u(t) + E d(t)
 *      - [u(k); x(k)] in s_dyn.Uset for all k => system obeys predefined constraints on how inputs may behave
 *
 * [L_full; M_full] polytope intersection of required and allowed polytopes
 *
 */
void set_path_constraints(gsl_matrix* L_full,
                          gsl_vector *M_full,
                          system_dynamics * s_dyn,
                          polytope *list_polytopes[],
                          size_t N);

#endif //CIMPLE_CIMPLE_CONTROLLER_H
