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

/**
 * Functions that help perform several mathematical operations
 * on the way to calculating the input.
 */
typedef struct auxiliary_matrices{

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


}auxiliary_matrices;

/**
 * Cost function to be minimized:
 *
 * |Rx|_{ord} + |Qu|_{ord} + r'x + mid_weight * |xc - x(N)|_{ord}
 *
 *      R: state cost matrix for:
 *      x = [x(1)' x(2)' .. x(N)']'
 *      If empty, zero matrix is used.
 *      dim[N*n x N*n] (n = x.size)
 *
 *      r: cost vector for state trajectory:
 *      x = [x(1)' x(2)' .. x(N)']'
 *      r: size (N*xdim x 1)
 *
 *      Q: input cost matrix for control input::
 *      u = [u(0)' u(1)' .. u(N-1)']'
 *      If empty, identity matrix is used.
 *      dim[N*m x N*m] m = u.size
 *
 *      distance_error_weight: cost weight for |x(N)-xc|_{ord}
 *
 *      ord: norm used for cost function: ord in {1, 2, INFINITY}
*/
typedef struct cost_function{

    gsl_matrix *R;
    gsl_matrix *Q;
    gsl_vector *r;
    double distance_error_weight;

}cost_function;

/**
 * Abstraction of the system
 * contains all the polytopes
 *
 * number_of_region = total number of possible states that can be reached
 * regions: array of region, each containing one or multiple polytopes
 *
 * closed_loop: if 'true' only first input of next N calculated inputs is applied.
 *              All others are discarded.
 * conservative: if 'true' x(0)...x(N-1) are in starting polytope, x(N) is in final polytope
 *               if false x(1)...x(N-1) can be anywhere
 *
 * ord: norm that is used for minimizing cost function in {1, 2, INFINITY}
 *
 * time_horizon: number of next steps that are taken into account in calculation of the path
 */
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

/**
 * Dynamics of the system
 *
 * x(t+1) = Ax(t) + Bu(t) + E
 *
 * A system dynamics
 * B input dynamics
 * E disturbance
 * U_set, W_set constraints on states and inputs
 * aux_matrices: auxiliary matrices to fasten calculation of next input
 */
typedef struct system_dynamics{

    gsl_matrix *A;
    gsl_matrix *B;
    gsl_matrix *E;
    gsl_vector *K;
    polytope *W_set;
    polytope *U_set;
    auxiliary_matrices *aux_matrices;

}system_dynamics;

/**
 * State plant is in at the beginning of the calculation
 *
 * current_cell starting region
 */
typedef struct current_state{

    int current_cell;
    gsl_vector *x;

} current_state;

/**
 * @brief "Constructor" Dynamically allocates the memory all auxiliary matrices need
 * @param n s_dyn.A.size2
 * @param p s_dyn.E.size2
 * @param m s_dyn.B.size2
 * @param u_set_size Uset.size1
 * @param N time horizon
 * @param d_ext_i number of rows of vertices disturbances matrix over N time steps
 * @param d_ext_j number of columns of vertices disturbances matrix over N time steps
 * @param d_one_i number of rows of vertices disturbances matrix over one time steps
 * @param d_one_j number of columns of vertices disturbances matrix over one time steps
 * @return
 */
struct auxiliary_matrices *aux_matrices_alloc(size_t n, size_t p, size_t m, size_t u_set_size, size_t N,size_t d_ext_i,size_t d_ext_j, size_t d_one_i, size_t d_one_j);

/**
 * @brief "Destructor" Deallocates the dynamically allocated memory of the auxiliary matrices
 * @param aux_matrices
 */
void aux_matrices_free(auxiliary_matrices *aux_matrices);

/**
 * @brief "Constructor" Dynamically allocates the memory the complete system dynamics need
 * @param n
 * @param m
 * @param p
 * @param w_set_size
 * @param u_set_size
 * @param N
 * @param d_ext_i
 * @param d_ext_j
 * @param d_one_i
 * @param d_one_j
 * @return
 */
struct system_dynamics *system_dynamics_alloc (size_t n, size_t m, size_t p, size_t w_set_size, size_t u_set_size, size_t N, size_t d_ext_i, size_t d_ext_j, size_t d_one_i, size_t d_one_j);

/**
 * @brief "Destructor" Deallocates the dynamically allocated memory of the system dynamics
 * @param system_dynamics
 */
void system_dynamics_free(system_dynamics * system_dynamics);

/**
 * @brief "Constructor" Dynamically allocates the memory for the state of the plant
 * @param n
 * @param cell
 * @return
 */
struct current_state *state_alloc(size_t n, int cell);

/**
 * @brief "Destructor" Deallocates the dynamically allocated memory of the state of the plant
 * @param state
 */
void state_free(current_state *state);

/**
 * @brief "Constructor" Dynamically allocates the memory for cost function matrices
 * @param n
 * @param m
 * @param N
 * @param distance_error_weight
 * @return
 */
struct cost_function *cost_function_alloc(size_t n,size_t m, size_t N, double distance_error_weight);

/**
 * @brief "Destructor" Deallocates the dynamically allocated memory of the cost function matrices
 * @param cost_function
 */
void cost_function_free(cost_function *cost_function);

/**
 * @brief "Constructor" Dynamically allocates the memory for the discrete abstraction of the system
 * @param polytopes_in_region
 * @param polytope_sizes
 * @param hull_sizes
 * @param orig_polytopes_in_region
 * @param orig_polytope_sizes
 * @param orig_hull_sizes
 * @param n
 * @param number_of_regions
 * @param number_of_original_regions
 * @param closed_loop
 * @param conservative
 * @param ord
 * @param time_horizon
 * @return
 */
struct discrete_dynamics *discrete_dynamics_alloc(int *polytopes_in_region, size_t *polytope_sizes, size_t *hull_sizes, int *orig_polytopes_in_region, size_t *orig_polytope_sizes, size_t *orig_hull_sizes, size_t n, int number_of_regions, int number_of_original_regions, int closed_loop, int conservative, int ord, size_t time_horizon);

/**
 * @brief "Destructor" Deallocates the dynamically allocated memory of the discrete dynamics
 * @param d_dyn
 */
void discrete_dynamics_free(discrete_dynamics *d_dyn);

#endif //CIMPLE_SYSTEM_H
