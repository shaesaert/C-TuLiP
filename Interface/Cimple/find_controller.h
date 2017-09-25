//
// Created by L. Jonathan Feldstein
//

#ifndef CIMPLE_FIND_CONTROLLER_H
#define CIMPLE_FIND_CONTROLLER_H

#include <stddef.h>
#include <math.h>
#include "system.h"
#include "cvxopt/cvxopt.h"
////////////////////////////////////////////////////////////////////////////////
// @fn apply_control()
// @brief Updates current state x by applying control over N time steps
// @param gsl_vector *x
// @param gsl_matrix *u
// @param gsl_matrix *A
// @param gsl_matrix *B
////////////////////////////////////////////////////////////////////////////////
void apply_control(gsl_vector *x, gsl_matrix *u, gsl_matrix *A, gsl_matrix *B);
////////////////////////////////////////////////////////////////////////////////
// @fn search_better_path()
// @brief Calculates possible path and its cost, for further evaluation (in get_input)
// @param current_state *now
// @param system_dynamics *s_dyn
// @param polytope P1
// @param polytope P3
// @param int closed_loop
// @param int time_horizon
// @param int ord
// @param cost_function * f_cost
////////////////////////////////////////////////////////////////////////////////
void search_better_path(gsl_matrix *low_u, current_state *now, system_dynamics *s_dyn, polytope *P1, polytope *P3, int ord, int closed_loop, size_t time_horizon, cost_function * f_cost,
                        double* low_cost);
////////////////////////////////////////////////////////////////////////////////
// @fn gsl_input()
// @brief Calculates optimal next N inputs
// @param current_state * now
// @param discrete_dynamics *d_dyn
// @param system_dynamics *s_dyn
// @param int target_cell
// @param cost_function * f_cost
////////////////////////////////////////////////////////////////////////////////
void get_input (gsl_matrix *u, current_state * now, discrete_dynamics *d_dyn, system_dynamics *s_dyn, int target_cell, cost_function * f_cost);
////////////////////////////////////////////////////////////////////////////////
void gsl_vector_from_array(gsl_vector *vector, double *array);
void gsl_matrix_from_array(gsl_matrix *matrix,double *array);
void polytope_from_arrays(polytope *polytope, size_t k, size_t n, double *left_side, double *right_side);
int state_in_polytope(polytope *polytope, gsl_vector *x);
void project_polytope(polytope *polytope, size_t new_dimension);
void reduce_polytope(polytope *polytope);
void solve_feasible_closed_loop(polytope *return_polytope, polytope *P1, polytope *P2, system_dynamics *s_dyn);
void set_path_constraints(gsl_matrix* L_full, gsl_vector *M_full, system_dynamics * s_dyn, polytope *list_polytopes[], size_t N);

#endif //CIMPLE_FIND_CONTROLLER_H
