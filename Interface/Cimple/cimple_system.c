//
// Created by L. Jonathan Feldstein

#include "cimple_system.h"

struct system_dynamics_helper_functions *helper_functions_alloc(size_t n, size_t p, size_t m, size_t u_set_size, size_t N,size_t d_ext_i,size_t d_ext_j, size_t d_one_i, size_t d_one_j){

    struct system_dynamics_helper_functions *return_helper_functions = malloc (sizeof (struct system_dynamics_helper_functions));

    return_helper_functions->A_N = gsl_matrix_alloc(n*N, n);
    if (return_helper_functions->A_N == NULL) {
        free (return_helper_functions);
        return NULL;
    }

    return_helper_functions->A_K = gsl_matrix_alloc(n*N, n*N);
    if (return_helper_functions->A_K == NULL) {
        free (return_helper_functions);
        return NULL;
    }

    return_helper_functions->Ct = gsl_matrix_alloc(n*N, m*N);
    if (return_helper_functions->Ct == NULL) {
        free (return_helper_functions);
        return NULL;
    }

    return_helper_functions->B_diag = gsl_matrix_alloc(n*N, m*N);
    if (return_helper_functions->B_diag == NULL) {
        free (return_helper_functions);
        return NULL;
    }

    return_helper_functions->E_diag = gsl_matrix_alloc(n*N, p*N);
    if (return_helper_functions->E_diag == NULL) {
        free (return_helper_functions);
        return NULL;
    }

    return_helper_functions->D_vertices = gsl_matrix_alloc(d_ext_i, d_ext_j);
    if (return_helper_functions->D_vertices == NULL) {
        free (return_helper_functions);
        return NULL;
    }

    return_helper_functions->D_one_step = gsl_matrix_alloc(d_one_i, d_one_j);
    if (return_helper_functions->D_one_step == NULL) {
        free (return_helper_functions);
        return NULL;
    }

    return_helper_functions->E_default = gsl_matrix_alloc(n* N, p* N);
    if (return_helper_functions->E_default == NULL) {
        free (return_helper_functions);
        return NULL;
    }

    return_helper_functions->L_default = gsl_matrix_alloc(n*N, (n+m*N));
    if (return_helper_functions->L_default == NULL) {
        free (return_helper_functions);
        return NULL;
    }

    return_helper_functions->LU = gsl_matrix_alloc(u_set_size*N, n+N*m);
    if (return_helper_functions->LU == NULL) {
        free (return_helper_functions);
        return NULL;
    }

    return_helper_functions->MU = gsl_vector_alloc(u_set_size*N);
    if (return_helper_functions->MU == NULL) {
        free (return_helper_functions);
        return NULL;
    }

    return_helper_functions->GU = gsl_matrix_alloc(u_set_size*N, p*N);
    if (return_helper_functions->GU == NULL) {
        free (return_helper_functions);
        return NULL;
    }

    return_helper_functions->K_hat = gsl_vector_alloc(n*N);
    if (return_helper_functions->K_hat == NULL) {
        free (return_helper_functions);
        return NULL;
    }

    return return_helper_functions;
}
void helper_functions_free(system_dynamics_helper_functions *helper_functions){
    gsl_matrix_free(helper_functions->D_vertices);
    gsl_matrix_free(helper_functions->D_one_step);
    gsl_matrix_free(helper_functions->L_default);
    gsl_matrix_free(helper_functions->E_default);
    gsl_vector_free(helper_functions->MU);
    gsl_matrix_free(helper_functions->LU);
    gsl_matrix_free(helper_functions->GU);
    gsl_matrix_free(helper_functions->Ct);
    gsl_vector_free(helper_functions->K_hat);
    gsl_matrix_free(helper_functions->B_diag);
    gsl_matrix_free(helper_functions->E_diag);
    gsl_matrix_free(helper_functions->A_N);
    gsl_matrix_free(helper_functions->A_K);
    free(helper_functions);
}
struct system_dynamics *system_dynamics_alloc (size_t n, size_t m, size_t p, size_t w_set_size, size_t u_set_size, size_t N, size_t d_ext_i, size_t d_ext_j, size_t d_one_i, size_t d_one_j) {

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
    return_dynamics->helper_functions = helper_functions_alloc(n, p, m, u_set_size, N, d_ext_i, d_ext_j, d_one_i, d_one_j);
    if (return_dynamics->helper_functions == NULL) {
        free(return_dynamics);
        return NULL;
    }

    return return_dynamics;
}
void system_dynamics_free(system_dynamics * system_dynamics){
    helper_functions_free(system_dynamics->helper_functions);
    polytope_free(system_dynamics->U_set);
    polytope_free(system_dynamics->W_set);
    gsl_matrix_free(system_dynamics->A);
    gsl_matrix_free(system_dynamics->B);
    gsl_matrix_free(system_dynamics->E);
    gsl_vector_free(system_dynamics->K);
    free(system_dynamics);
}
struct current_state *state_alloc(size_t n, int cell){

    struct current_state *return_state = malloc (sizeof (struct current_state));

    return_state->x = gsl_vector_alloc(n);
    if (return_state->x == NULL) {
        free (return_state);
        return NULL;
    }

    return_state->current_cell = cell;

    return return_state;
}
void state_free(current_state *state){

    gsl_vector_free(state->x);
    free(state);
}
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
void cost_function_free(cost_function *cost_function){
    gsl_matrix_free(cost_function->R);
    gsl_vector_free(cost_function->r);
    gsl_matrix_free(cost_function->Q);
    free(cost_function);
}
struct discrete_dynamics *discrete_dynamics_alloc(int *polytopes_in_region, size_t *polytope_sizes, size_t *hull_sizes, int *orig_polytopes_in_region, size_t *orig_polytope_sizes, size_t *orig_hull_sizes, size_t n, int number_of_regions, int number_of_original_regions, int closed_loop, int conservative, int ord, size_t time_horizon){

    struct discrete_dynamics *return_discrete_dynamics = malloc (sizeof (struct discrete_dynamics));

    return_discrete_dynamics->regions = malloc(sizeof(region_of_polytopes)*number_of_regions);
    int polytope_count = 0;
    for(int i =0; i < number_of_regions; i++){

        return_discrete_dynamics->regions[i] = region_of_polytopes_alloc(polytope_sizes+polytope_count, hull_sizes[i],n,polytopes_in_region[i]);
        polytope_count += polytopes_in_region[i];
    }
    if (return_discrete_dynamics->regions == NULL) {
        free (return_discrete_dynamics);
        return NULL;
    }
    return_discrete_dynamics->original_regions = malloc(sizeof(region_of_polytopes)*number_of_original_regions);
    int orig_polytope_count = 0;
    for(int j =0; j < number_of_original_regions; j++){
        return_discrete_dynamics->original_regions[j] = region_of_polytopes_alloc(orig_polytope_sizes+orig_polytope_count, orig_hull_sizes[j],n,orig_polytopes_in_region[j]);
        orig_polytope_count += orig_polytopes_in_region[j];
    }
    if (return_discrete_dynamics->original_regions == NULL) {
        free (return_discrete_dynamics);
        return NULL;
    }
    return_discrete_dynamics->number_of_regions = number_of_regions;
    return_discrete_dynamics->number_of_original_regions = number_of_original_regions;
    return_discrete_dynamics->closed_loop = closed_loop;
    return_discrete_dynamics->conservative = conservative;
    return_discrete_dynamics->ord = ord;
    return_discrete_dynamics->time_horizon = time_horizon;

    return return_discrete_dynamics;
}

void discrete_dynamics_free(discrete_dynamics *d_dyn){

    for(int i = 0; i<d_dyn->number_of_regions; i++){
        region_of_polytopes_free(d_dyn->regions[i]);
    }
    for(int j = 0; j<d_dyn->number_of_original_regions; j++){
        region_of_polytopes_free(d_dyn->original_regions[j]);
    }
    free(d_dyn->regions);
    free(d_dyn->original_regions);
    free(d_dyn);
}