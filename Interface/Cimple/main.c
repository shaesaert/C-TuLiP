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

//        dd_MatrixPtr constraintsA;
//    constraintsA = dd_CreateMatrix(4, 3);
//    dd_set_d(constraintsA->matrix[0][0],1);
//    dd_set_d(constraintsA->matrix[0][1],1);
//    dd_set_d(constraintsA->matrix[0][2],1);
//    dd_set_d(constraintsA->matrix[1][0],1);
//    dd_set_d(constraintsA->matrix[1][1],-1);
//    dd_set_d(constraintsA->matrix[1][2],1);
//    dd_set_d(constraintsA->matrix[2][0],1);
//    dd_set_d(constraintsA->matrix[2][1],1);
//    dd_set_d(constraintsA->matrix[2][2],-1);
//    dd_set_d(constraintsA->matrix[3][0],1);
//    dd_set_d(constraintsA->matrix[3][1],-1);
//    dd_set_d(constraintsA->matrix[3][2],-1);
//
//
//    constraintsA->representation=dd_Generator;
//    dd_ErrorType err =dd_NoError;
//
//    dd_PolyhedraPtr newPolyA = dd_DDMatrix2Poly(constraintsA, &err);
//
//    dd_PolyhedraPtr newPoly = dd_DDMatrix2Poly(constraintsA, &err);
//    dd_PolyhedraPtr B = polytope_minkowski(newPoly,newPolyA);
//    polytope * correct = cdd_to_polytope(&B);
//    dd_FreePolyhedra(B);
//    gsl_matrix_print(correct->H, "H");
//    gsl_vector_print(correct->G, "G");
//    polytope_free(correct);

//    double sec = 2;
//    ACT(3, now, d_dyn, s_dyn, f_cost, sec);

    system_dynamics_free(s_dyn);
    discrete_dynamics_free(d_dyn);
    cost_function_free(f_cost);
    state_free(now);

    dd_free_global_constants();
    return 0;
}
