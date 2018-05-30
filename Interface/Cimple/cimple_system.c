//
// Created by L. Jonathan Feldstein

#include "cimple_system.h"


/**
 * "Constructor" Dynamically allocates the space for the get_input thread
 */
struct control_computation_arguments *cc_arguments_alloc(current_state *now, gsl_matrix* u, system_dynamics *s_dyn, discrete_dynamics *d_dyn, cost_function *f_cost, size_t current_time_horizon, int target_abs_state, polytope **polytope_list){

    struct control_computation_arguments *return_control_computation_arguments = malloc (sizeof (struct control_computation_arguments));

    return_control_computation_arguments->current_time_horizon =current_time_horizon;

    return_control_computation_arguments->target_abs_state = target_abs_state;

    return_control_computation_arguments->d_dyn = d_dyn;

    return_control_computation_arguments->f_cost = f_cost;

    return_control_computation_arguments->s_dyn = s_dyn;

    return_control_computation_arguments->now = now;

    return_control_computation_arguments->u = u;

    return_control_computation_arguments->polytope_list_backup = polytope_list;

    return return_control_computation_arguments;
};
/**
 * "Constructor" Dynamically allocates the space for the arguments of the safemode computation thread
 */
struct total_safemode_computation_arguments *sm_arguments_alloc(current_state *now, gsl_matrix * u, polytope *current, polytope *safe, system_dynamics * s_dyn, size_t time_horizon,cost_function *f_cost, polytope **polytope_list_safemode){

    struct total_safemode_computation_arguments *return_sm_arguments = malloc (sizeof (struct total_safemode_computation_arguments));

    return_sm_arguments->now = now;
    return_sm_arguments->u = u;
    return_sm_arguments->time_horizon = time_horizon;
    return_sm_arguments->current = current;
    return_sm_arguments->safe = safe;
    return_sm_arguments->s_dyn = s_dyn;
    return_sm_arguments->f_cost = f_cost;
    return_sm_arguments->polytope_list_backup = polytope_list_safemode;

    return return_sm_arguments;
};

/**
 * "Constructor" Dynamically allocates the space for the arguments of the next step towards safemode computation thread
 */
struct next_safemode_computation_arguments *next_sm_arguments_alloc(current_state *now, gsl_matrix * u, system_dynamics * s_dyn, size_t time_horizon,cost_function *f_cost, polytope **polytope_list_safemode){

    struct next_safemode_computation_arguments *return_sm_arguments = malloc (sizeof (struct next_safemode_computation_arguments));

    return_sm_arguments->now = now;
    return_sm_arguments->u = u;
    return_sm_arguments->time_horizon = time_horizon;
    return_sm_arguments->s_dyn = s_dyn;
    return_sm_arguments->f_cost = f_cost;
    return_sm_arguments->polytope_list_backup = polytope_list_safemode;

    return return_sm_arguments;
};
/**
 * "Constructor" Dynamically allocates the memory all auxiliary matrices need
 */
struct auxiliary_matrices *aux_matrices_alloc(size_t n,
                                              size_t p,
                                              size_t m,
                                              size_t u_set_size,
                                              size_t N){

    struct auxiliary_matrices *return_aux_matrices = malloc (sizeof (struct auxiliary_matrices));

    return_aux_matrices->A_N = gsl_matrix_alloc(n*N, n);
    if (return_aux_matrices->A_N == NULL) {
        free (return_aux_matrices);
        return NULL;
    }

    return_aux_matrices->A_K = gsl_matrix_alloc(n*N, n*N);
    if (return_aux_matrices->A_K == NULL) {
        free (return_aux_matrices);
        return NULL;
    }

    return_aux_matrices->Ct = gsl_matrix_alloc(n*N, m*N);
    if (return_aux_matrices->Ct == NULL) {
        free (return_aux_matrices);
        return NULL;
    }

    return_aux_matrices->B_diag = gsl_matrix_alloc(n*N, m*N);
    if (return_aux_matrices->B_diag == NULL) {
        free (return_aux_matrices);
        return NULL;
    }

    return_aux_matrices->E_diag = gsl_matrix_alloc(n*N, p*N);
    if (return_aux_matrices->E_diag == NULL) {
        free (return_aux_matrices);
        return NULL;
    }

    return_aux_matrices->E_default = gsl_matrix_alloc(n* (N+1), p* (N+1));
    if (return_aux_matrices->E_default == NULL) {
        free (return_aux_matrices);
        return NULL;
    }

    return_aux_matrices->L_default = gsl_matrix_alloc(n*(N+1), (n+m*N));
    if (return_aux_matrices->L_default == NULL) {
        free (return_aux_matrices);
        return NULL;
    }

    return_aux_matrices->LU = gsl_matrix_alloc(u_set_size*N, n+N*m);
    if (return_aux_matrices->LU == NULL) {
        free (return_aux_matrices);
        return NULL;
    }

    return_aux_matrices->MU = gsl_vector_alloc(u_set_size*N);
    if (return_aux_matrices->MU == NULL) {
        free (return_aux_matrices);
        return NULL;
    }

    return_aux_matrices->GU = gsl_matrix_alloc(u_set_size*N, p*N);
    if (return_aux_matrices->GU == NULL) {
        free (return_aux_matrices);
        return NULL;
    }

    return_aux_matrices->K_hat = gsl_vector_alloc(n*N);
    if (return_aux_matrices->K_hat == NULL) {
        free (return_aux_matrices);
        return NULL;
    }

    return return_aux_matrices;
}

/**
 * "Destructor" Deallocates the dynamically allocated memory of the auxiliary matrices
 */
void aux_matrices_free(auxiliary_matrices *aux_matrices){
    gsl_matrix_free(aux_matrices->L_default);
    gsl_matrix_free(aux_matrices->E_default);
    gsl_vector_free(aux_matrices->MU);
    gsl_matrix_free(aux_matrices->LU);
    gsl_matrix_free(aux_matrices->GU);
    gsl_matrix_free(aux_matrices->Ct);
    gsl_vector_free(aux_matrices->K_hat);
    gsl_matrix_free(aux_matrices->B_diag);
    gsl_matrix_free(aux_matrices->E_diag);
    gsl_matrix_free(aux_matrices->A_N);
    gsl_matrix_free(aux_matrices->A_K);
    free(aux_matrices);
}

/**
 * "Constructor" Dynamically allocates the memory the complete system dynamics need
 */
struct system_dynamics *system_dynamics_alloc (size_t n,
                                               size_t m,
                                               size_t p,
                                               size_t w_set_size,
                                               size_t u_set_size,
                                               size_t N) {

    struct system_dynamics *return_dynamics = malloc (sizeof (struct system_dynamics));
    if (return_dynamics == NULL){
        return NULL;
    }

    return_dynamics->A = gsl_matrix_alloc(n, n);
    if (return_dynamics->A == NULL) {
        free (return_dynamics);
        return NULL;
    }

    return_dynamics->B = gsl_matrix_alloc(n, m);
    if (return_dynamics->B == NULL) {
        free (return_dynamics);
        return NULL;
    }

    return_dynamics->E = gsl_matrix_alloc(n, p);
    if (return_dynamics->E == NULL) {
        free (return_dynamics);
        return NULL;
    }
    return_dynamics->K = gsl_vector_alloc(n);
    if (return_dynamics->K == NULL) {
        free (return_dynamics);
        return NULL;
    }
    return_dynamics->W_set = polytope_alloc(w_set_size, n);
    if (return_dynamics->W_set == NULL) {
        free (return_dynamics);
        return NULL;
    }
    return_dynamics->U_set = polytope_alloc(u_set_size, n);
    if (return_dynamics->U_set == NULL) {
        free (return_dynamics);
        return NULL;
    }
    return_dynamics->aux_matrices = aux_matrices_alloc(n,
                                                       p,
                                                       m,
                                                       u_set_size,
                                                       N);
    if (return_dynamics->aux_matrices == NULL) {
        free(return_dynamics);
        return NULL;
    }

    return return_dynamics;
}

/**
 * "Destructor" Deallocates the dynamically allocated memory of the system dynamics
 */
void system_dynamics_free(system_dynamics * system_dynamics){
    aux_matrices_free(system_dynamics->aux_matrices);
    polytope_free(system_dynamics->U_set);
    polytope_free(system_dynamics->W_set);
    gsl_matrix_free(system_dynamics->A);
    gsl_matrix_free(system_dynamics->B);
    gsl_matrix_free(system_dynamics->E);
    gsl_vector_free(system_dynamics->K);
    free(system_dynamics);
}

/**
 * "Constructor" Dynamically allocates the memory for the state of the plant
 */
struct current_state *state_alloc(size_t n, int abstract_state){

    struct current_state *return_state = malloc (sizeof (struct current_state));

    return_state->x = gsl_vector_alloc(n);
    if (return_state->x == NULL) {
        free (return_state);
        return NULL;
    }

    return_state->current_abs_state = abstract_state;

    return return_state;
}

/**
 * "Destructor" Deallocates the dynamically allocated memory of the state of the plant
 */
void state_free(current_state *state){

    gsl_vector_free(state->x);
    free(state);
}

/**
 * "Constructor" Dynamically allocates the memory for cost function matrices
 */
struct cost_function *cost_function_alloc(size_t n,size_t m, size_t N, double distance_error_weight){

    struct cost_function *return_cost_function = malloc (sizeof (struct cost_function));

    return_cost_function->R = gsl_matrix_alloc(n*N, n*N);
    if (return_cost_function->R == NULL) {
        free (return_cost_function);
        return NULL;
    }

    return_cost_function->Q = gsl_matrix_alloc(m*N, m*N);
    if (return_cost_function->Q == NULL) {
        free (return_cost_function);
        return NULL;
    }

    return_cost_function->r = gsl_vector_alloc(n*N);
    if (return_cost_function->r == NULL) {
        free (return_cost_function);
        return NULL;
    }

    return_cost_function->distance_error_weight = distance_error_weight;

    return return_cost_function;
}


/**
 * "Destructor" Deallocates the dynamically allocated memory of the cost function matrices
 */
void cost_function_free(cost_function *cost_function){
    gsl_matrix_free(cost_function->R);
    gsl_vector_free(cost_function->r);
    gsl_matrix_free(cost_function->Q);
    free(cost_function);
}

/**
 * "Constructor" Dynamically allocates the memory for the discrete abstraction of the system
 */
struct discrete_dynamics *discrete_dynamics_alloc(int *polytopes_in_region,
                                                  size_t *polytope_sizes,
                                                  size_t *hull_sizes,
                                                  int *orig_polytopes_in_region,
                                                  size_t *orig_polytope_sizes,
                                                  size_t *orig_hull_sizes,
                                                  int *transitions_in_sizes,
                                                  int *transitions_out_sizes,
                                                  size_t n,
                                                  int abstract_states_count,
                                                  int number_of_original_regions,
                                                  int closed_loop,
                                                  int conservative,
                                                  int ord,
                                                  size_t time_horizon){

    struct discrete_dynamics *return_discrete_dynamics = malloc (sizeof (struct discrete_dynamics));

    return_discrete_dynamics->abstract_states_set = malloc(sizeof(abstract_state)*abstract_states_count);
    int polytope_count = 0;
    for(int i =0; i < abstract_states_count; i++){

        return_discrete_dynamics->abstract_states_set[i] = abstract_state_alloc(polytope_sizes+polytope_count,
                                                                                hull_sizes[i],
                                                                                n,
                                                                                transitions_in_sizes[i],
                                                                                transitions_out_sizes[i],
                                                                                polytopes_in_region[i],
                                                                                (int) time_horizon);
        polytope_count += polytopes_in_region[i];
    }
    if (return_discrete_dynamics->abstract_states_set == NULL) {
        free (return_discrete_dynamics);
        return NULL;
    }
    return_discrete_dynamics->original_regions = malloc(sizeof(abstract_state)*number_of_original_regions);
    int orig_polytope_count = 0;
    for(int j =0; j < number_of_original_regions; j++){
        return_discrete_dynamics->original_regions[j] = abstract_state_alloc(orig_polytope_sizes+orig_polytope_count,
                                                                             orig_hull_sizes[j],
                                                                             n,
                                                                             number_of_original_regions,
                                                                             number_of_original_regions,
                                                                             orig_polytopes_in_region[j],
                                                                             (int) time_horizon);
        orig_polytope_count += orig_polytopes_in_region[j];
    }
    if (return_discrete_dynamics->original_regions == NULL) {
        free (return_discrete_dynamics);
        return NULL;
    }
    return_discrete_dynamics->abstract_states_count = abstract_states_count;
    return_discrete_dynamics->number_of_original_regions = number_of_original_regions;
    return_discrete_dynamics->closed_loop = closed_loop;
    return_discrete_dynamics->conservative = conservative;
    return_discrete_dynamics->ord = ord;
    return_discrete_dynamics->time_horizon = time_horizon;

    return return_discrete_dynamics;
}

/**
 * "Destructor" Deallocates the dynamically allocated memory of the discrete dynamics
 */
void discrete_dynamics_free(discrete_dynamics *d_dyn){

    for(int i = 0; i<d_dyn->abstract_states_count; i++){
        abstract_state_free(d_dyn->abstract_states_set[i]);
    }
    for(int j = 0; j<d_dyn->number_of_original_regions; j++){
        abstract_state_free(d_dyn->original_regions[j]);
    }
    free(d_dyn->abstract_states_set);
    free(d_dyn->original_regions);
    free(d_dyn);
}