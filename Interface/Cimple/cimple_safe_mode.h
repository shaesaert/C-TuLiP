//
// Created by be107admin on 3/22/18.
//

#ifndef CIMPLE_CIMPLE_SAFE_MODE_H
#define CIMPLE_CIMPLE_SAFE_MODE_H

#include "cimple_controller.h"
#include "cimple_auxiliary_functions.h"

/**
 * List node:
 * Needed to build up the graph for the burning method
 */
typedef struct burn_graph_node {
    abstract_state *state;
    struct burn_graph_node * next;
} burn_graph_node;

/**
 * @brief Adds a node to the beginning of the list
 * @param head Current head of the list
 * @param state New item to be added
 */
void push_burn_node(burn_graph_node ** head,
                    abstract_state *state);

/**
 * @brief Remove a node from the beginning of the list
 * @param head Current head of the list
 */
void pop_burn_node(burn_graph_node ** head);

/**
 * @brief Delete and free memory of all nodes of a list
 * @param head
 */
void clear_burn_list(burn_graph_node **head);

/**
 * @brief Computes one step backwards from second polytope towards first polytope
 * @param P1 Polytope of origin
 * @param P2 Target polytope
 * @param s_dyn
 * @return Intermediate polytope system has to be in to reach P2 in one time step
 */
polytope* previous_polytope(polytope *P1,
                            polytope *P2,
                            system_dynamics *s_dyn);

/**
 * @brief Computes N-1 polytopes the system has to transition to go from origin to target in N time steps
 * @param origin
 * @param target
 * @param s_dyn
 * @param N time horizon within which target needs to be reached
 * @return Array of polytopes
 */
polytope ** compute_path(polytope *origin,
                         polytope *target,
                         system_dynamics *s_dyn,
                         int N);

abstract_state* fastest_burn(abstract_state **transitions,
                             int transitions_count);
int check_backup(gsl_vector *x_real,
                 gsl_vector *u,
                 gsl_matrix *A,
                 gsl_matrix *B,
                 polytope *check_polytope);

polytope * compute_invariant_set(polytope* X,
                                 gsl_matrix *A,
                                 gsl_matrix *B,
                                 polytope *W_set,
                                 polytope *U_set,
                                 double alpha);

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

#endif //CIMPLE_CIMPLE_SAFE_MODE_H
