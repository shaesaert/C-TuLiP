//
// Created by be107admin on 3/22/18.
//

#ifndef CIMPLE_CIMPLE_SAFE_MODE_H
#define CIMPLE_CIMPLE_SAFE_MODE_H

#include "cimple_controller.h"


int check_backup(gsl_vector *x_real,
                 gsl_vector *u,
                 gsl_matrix *A,
                 gsl_matrix *B,
                 polytope *check_polytope);

polytope* previous_polytope(polytope *P1,
                            polytope *P2,
                            system_dynamics *s_dyn);

void safe_mode_polytopes(system_dynamics *s_dyn,
                         polytope *current_polytope,
                         polytope *safe_polytope,
                         size_t time_horizon,
                         polytope **polytope_list_safemode);

void next_safemode_input(gsl_matrix *u,
                         current_state *now,
                         polytope *current,
                         polytope *next,
                         system_dynamics *s_dyn,
                         cost_function *f_cost);

void *next_safemode_computation(void *arg);

void * total_safe_mode_computation(void *arg);

poly_t * solve_feasible_closed_loop(poly_t *p_universe,
                                    polytope *P1,
                                    polytope *P2,
                                    system_dynamics *s_dyn);
#endif //CIMPLE_CIMPLE_SAFE_MODE_H
