//
// Created by L.Jonathan Feldstein
//

#ifndef CIMPLE_SYSTEM_H
#define CIMPLE_SYSTEM_H

#include <gsl/gsl_blas.h>
#include <gsl/gsl_cblas.h>
typedef struct system_dynamics_helper_functions{

    //gsl_vector * K_hat;
    gsl_matrix * A_K_2;
    gsl_matrix * A_N_2;
    gsl_matrix * Ct;


    //gsl_matrix * L;
    //gsl_vector * M;
    gsl_matrix * L_default;
    gsl_matrix * E_default;
    gsl_matrix * D_vertices;
    gsl_matrix * D_one_step;


    //LUn = np.shape(PU.A)[0]

    //LU = np.zeros([LUn*N, n+N*m])

    gsl_matrix * LU;

    //MU = np.tile(PU.b.reshape(PU.b.size, 1), (N, 1))

    gsl_vector * MU;

    //GU = np.zeros([LUn*N, p*N])

    gsl_matrix * GU;

    //K_hat = np.tile(K, (N, 1))

    gsl_vector * K_hat;

    /*B_diag = B
    E_diag = E
    for i in range(N-1):
    B_diag = _block_diag2(B_diag, B)
    E_diag = _block_diag2(E_diag, E)

     */

    gsl_matrix * B_diag;
    gsl_matrix * E_diag;

    //A_n = np.eye(n)
    gsl_matrix * A_N;

    //A_k = np.zeros([n, n*N])
    gsl_matrix * A_K;


}system_dynamics_helper_functions;

typedef struct cost_function{

    gsl_matrix *R;
    gsl_matrix *Q;
    gsl_vector *r;
    double distance_error_weight;

}cost_function;
typedef struct polytope{

    gsl_matrix * H;
    gsl_vector * G;
    double *chebyshev_center;

}polytope;

typedef struct region_of_polytopes{

    int number_of_polytopes;
    polytope **polytopes;
    // convex hull of polytopes in that region: hull.A = NULL if only one polytope exists in that region
    polytope *hull_of_region;

}region_of_polytopes;

typedef struct discrete_dynamics{

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
struct polytope *polytope_alloc(size_t k, size_t n);
void polytope_free(polytope *polytope);
struct region_of_polytopes *region_of_polytopes_alloc(size_t k[],size_t k_hull, size_t n, int number_of_polytopes);
void region_of_polytopes_free(region_of_polytopes * region_of_polytopes);
struct system_dynamics_helper_functions *helper_functions_alloc(size_t n, size_t p, size_t m, size_t u_set_size, size_t N,size_t d_ext_i,size_t d_ext_j, size_t d_one_i, size_t d_one_j);
void helper_functions_free(system_dynamics_helper_functions *helper_functions);
struct system_dynamics *system_dynamics_alloc (size_t n, size_t m, size_t p, size_t w_set_size, size_t u_set_size, size_t N, size_t d_ext_i, size_t d_ext_j, size_t d_one_i, size_t d_one_j);
void system_dynamics_free(system_dynamics * system_dynamics);
struct current_state *state_alloc(size_t n, int cell);
void state_free(current_state *state);
struct cost_function *cost_function_alloc(size_t n,size_t m, size_t N, double distance_error_weight);
void cost_function_free(cost_function *cost_function);
struct discrete_dynamics *discrete_dynamics_alloc(int *polytopes_in_region, size_t *polytope_sizes, size_t *hull_sizes, int *orig_polytopes_in_region, size_t *orig_polytope_sizes, size_t *orig_hull_sizes, size_t n, int number_of_regions, int number_of_original_regions, int closed_loop, int conservative, int ord, size_t time_horizon);
void discrete_dynamics_free(discrete_dynamics *d_dyn, int number_of_regions, int number_of_orig_regions);

#endif //CIMPLE_SYSTEM_H
