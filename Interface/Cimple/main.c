#include "cimple_c_from_py.h"
#include "setoper.h"
#include "cimple_safe_mode.h"
#include <cdd.h>
#include <gsl/gsl_matrix.h>

int main(){

    dd_set_global_constants();
    // Initialize state:
    system_dynamics *s_dyn;
    cost_function *f_cost;
    discrete_dynamics *d_dyn;
    current_state *now;

    system_alloc(&now, &s_dyn, &f_cost, &d_dyn);
    system_init(now, s_dyn, f_cost, d_dyn);

gsl_matrix *A = gsl_matrix_alloc(2,2);
gsl_matrix_set_zero(A);
gsl_matrix_set(A,0,1,1);
gsl_matrix_set(A,1,0,1);
gsl_matrix_set(A,1,1,1);
gsl_matrix *B = gsl_matrix_alloc(2,1);
gsl_matrix_set_zero(B);
gsl_matrix_set(B,1,0,1);
polytope *U_set = polytope_alloc(2,1);
gsl_matrix_set_zero(U_set->H);
gsl_matrix_set(U_set->H,0,0,1);
gsl_matrix_set(U_set->H,1,0,-1);
gsl_vector_set_zero(U_set->G);
gsl_vector_set(U_set->G,0,100);
gsl_vector_set(U_set->G,1,100);
polytope *W_set = polytope_alloc(4,2);
gsl_matrix_set_zero(W_set->H);
gsl_matrix_set(W_set->H,0,0,1);
gsl_matrix_set(W_set->H,1,0,1);
gsl_matrix_set(W_set->H,2,1,-1);
gsl_matrix_set(W_set->H,3,1,-1);
gsl_vector_set_zero(W_set->G);
gsl_vector_set(W_set->G,0,1);
gsl_vector_set(W_set->G,1,1);
gsl_vector_set(W_set->G,2,1);
gsl_vector_set(W_set->G,3,1);
polytope *X = polytope_alloc(3,2);
gsl_matrix_set_zero(X->H);
gsl_matrix_set(X->H,0,0,1);
gsl_matrix_set(X->H,0,1,1);
gsl_matrix_set(X->H,1,0,-3);
gsl_matrix_set(X->H,1,1,1);
gsl_matrix_set(X->H,2,1,-1);
gsl_vector_set_zero(X->G);
gsl_vector_set(X->G,0,100);
gsl_vector_set(X->G,1,-50);
gsl_vector_set(X->G,2,-26);
double alpha = 1;
polytope *invariant_set = compute_invariant_set(X,A,B,W_set,U_set, alpha);

gsl_matrix_print(invariant_set->H, "Hinv");
gsl_vector_print(invariant_set->G, "Ginv");

gsl_matrix_free(A);
gsl_matrix_free(B);
dd_ErrorType err = dd_NoError;
dd_PolyhedraPtr origX = polytope_to_cdd(X,&err);
polytope_free(U_set);
polytope_free(W_set);
polytope_free(X);
dd_PolyhedraPtr result = polytope_to_cdd(invariant_set, &err);
dd_MatrixPtr vert = dd_CopyGenerators(result);
dd_WriteMatrix(stdout, vert);
dd_MatrixPtr vertorig = dd_CopyGenerators(origX);
dd_WriteMatrix(stdout, vertorig);
dd_FreeMatrix(vertorig);
dd_FreePolyhedra(origX);
dd_FreePolyhedra(result);
dd_FreeMatrix(vert);
polytope_free(invariant_set);


//    double sec = 2;
//    ACT(3, now, d_dyn, s_dyn, f_cost, sec);

    system_dynamics_free(s_dyn);
    discrete_dynamics_free(d_dyn);
    cost_function_free(f_cost);
    state_free(now);

    dd_free_global_constants();
    return 0;
}
