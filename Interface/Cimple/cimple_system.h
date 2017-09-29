//
// Created by L.Jonathan Feldstein
//

#ifndef CIMPLE_SYSTEM_H
#define CIMPLE_SYSTEM_H

#include <gsl/gsl_cblas.h>
#include <gsl/gsl_blas.h>
#include "cimple_polytope_library.h"

// EXAMPLE ALLOCATION FOR STRUCT
// Try to allocate structure.
// struct struct_name *return_**** = malloc(sizeof(struct));
// Try to allocate data, free structure if fail.
// return_****->**** = malloc(***);
// Free structure if fail, return NULL
// if (return_****->**** == NULL){
//    return NULL;
//}


typedef struct system_dynamics_helper_functions{

    gsl_matrix * A_K;
    gsl_matrix * A_N;
    gsl_matrix * Ct;

    /*
    B_diag = B
    E_diag = E
    for i in range(N-1):
    B_diag = _block_diag2(B_diag, B)
    E_diag = _block_diag2(E_diag, E)
     */
    gsl_matrix * B_diag;
    gsl_matrix * E_diag;

    gsl_matrix * L_default;
    gsl_matrix * E_default;
    gsl_matrix * D_vertices;
    gsl_matrix * D_one_step;


    //LU = ([Uset->size1*N, n+N*m])

    gsl_matrix * LU;

    //MU = tile(Uset->G, N)

    gsl_vector * MU;

    //GU = ([Uset->size1*N, p*N])

    gsl_matrix * GU;

    //K_hat = tile(K, N)

    gsl_vector * K_hat;


}system_dynamics_helper_functions;

/**
@param R: state cost matrix for::
x = [x(1)' x(2)' .. x(N)']'
If empty, zero matrix is used.
@type R: size (N*xdim x N*xdim)

@param r: cost vector for state trajectory:
x = [x(1)' x(2)' .. x(N)']'
@type r: size (N*xdim x 1)

@param Q: input cost matrix for control input::
        u = [u(0)' u(1)' .. u(N-1)']'
If empty, identity matrix is used.
@type Q: size (N*udim x N*udim)

@param distance_error_weight: cost weight for |x(N)-xc|_{ord}

@param ord: norm used for cost function: ord in {1, 2, INFINITY}
*/
typedef struct cost_function{

    gsl_matrix *R;
    gsl_matrix *Q;
    gsl_vector *r;
    double distance_error_weight;

}cost_function;

typedef struct discrete_dynamics{

    int number_of_regions;
    int number_of_original_regions;
    region_of_polytopes **regions;
    region_of_polytopes **original_regions;
    int closed_loop;
    int conservative;
    int ord;
    size_t time_horizon;

}discrete_dynamics;

typedef struct system_dynamics{

    gsl_matrix *A;
    gsl_matrix *B;
    gsl_matrix *E;
    gsl_vector *K;
    polytope *W_set;
    polytope *U_set;
    system_dynamics_helper_functions *helper_functions;

}system_dynamics;
typedef struct current_state{

    int current_cell;
    gsl_vector *x;

} current_state;
struct system_dynamics_helper_functions *helper_functions_alloc(size_t n, size_t p, size_t m, size_t u_set_size, size_t N,size_t d_ext_i,size_t d_ext_j, size_t d_one_i, size_t d_one_j);
void helper_functions_free(system_dynamics_helper_functions *helper_functions);
struct system_dynamics *system_dynamics_alloc (size_t n, size_t m, size_t p, size_t w_set_size, size_t u_set_size, size_t N, size_t d_ext_i, size_t d_ext_j, size_t d_one_i, size_t d_one_j);
void system_dynamics_free(system_dynamics * system_dynamics);
struct current_state *state_alloc(size_t n, int cell);
void state_free(current_state *state);
struct cost_function *cost_function_alloc(size_t n,size_t m, size_t N, double distance_error_weight);
void cost_function_free(cost_function *cost_function);
struct discrete_dynamics *discrete_dynamics_alloc(int *polytopes_in_region, size_t *polytope_sizes, size_t *hull_sizes, int *orig_polytopes_in_region, size_t *orig_polytope_sizes, size_t *orig_hull_sizes, size_t n, int number_of_regions, int number_of_original_regions, int closed_loop, int conservative, int ord, size_t time_horizon);
void discrete_dynamics_free(discrete_dynamics *d_dyn);

#endif //CIMPLE_SYSTEM_H
