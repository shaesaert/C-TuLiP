//
// Created by be107admin on 9/25/17.
//

#include <math.h>
#include <gsl/gsl_vector_double.h>
#include <gsl/gsl_matrix.h>
#include "cimple_polytope_library.h"


//TODO
//void projection_fm(polytope poly, int new_dim, int del_dim);
//void projection_exthull(polytope poly, int new_dim);
//void projection_iterhull(polytope poly, int new_dim);

/**
 * "Constructor" Dynamically allocates the space a polytope needs
 */
struct polytope *polytope_alloc(size_t k, size_t n){

    struct polytope *return_polytope = malloc (sizeof (struct polytope));

    return_polytope->H = gsl_matrix_alloc(k, n);
    if (return_polytope->H == NULL) {
        free (return_polytope);
        return NULL;
    }

    return_polytope->G = gsl_vector_alloc(k);
    if (return_polytope->H == NULL) {
        free (return_polytope);
        return NULL;
    }

    return_polytope->chebyshev_center = malloc(n* sizeof (double));
    if (return_polytope->chebyshev_center == NULL) {
        free (return_polytope);
        return NULL;
    }

    return return_polytope;
}

/**
 * "Destructor" Deallocates the dynamically allocated memory of the polytope
 */
void polytope_free(polytope *polytope){
    gsl_matrix_free(polytope->H);
    gsl_vector_free(polytope->G);
    free(polytope->chebyshev_center);
    free(polytope);
}

/**
 * "Constructor" Dynamically allocates the space a region of polytope needs
 */
struct region_of_polytopes *region_of_polytopes_alloc(size_t *k,size_t k_hull, size_t n, int number_of_polytopes){

    struct region_of_polytopes *return_region_of_polytopes = malloc (sizeof (struct region_of_polytopes));

    return_region_of_polytopes->polytopes = malloc(sizeof(polytope)*number_of_polytopes);
    for(int i = 0; i < number_of_polytopes; i++){
        return_region_of_polytopes->polytopes[i] = polytope_alloc(*(k+i), n);
    }
    if (return_region_of_polytopes->polytopes == NULL) {
        free (return_region_of_polytopes);
        return NULL;
    }

    return_region_of_polytopes->hull_of_region = polytope_alloc(k_hull, n);
    if (return_region_of_polytopes->polytopes == NULL) {
        free (return_region_of_polytopes);
        return NULL;
    }

    return_region_of_polytopes->number_of_polytopes = number_of_polytopes;

    return return_region_of_polytopes;
}

/**
 * "Destructor" Deallocates the dynamically allocated memory of the region of polytopes
 */
void region_of_polytopes_free(region_of_polytopes * region_of_polytopes){
    polytope_free(region_of_polytopes->hull_of_region);
    for(int i = 0; i< region_of_polytopes->number_of_polytopes; i++){
        polytope_free(region_of_polytopes->polytopes[i]);
    }
    free(region_of_polytopes->polytopes);
    free(region_of_polytopes);

};

/**
 * Converts two C arrays to a polytope consistent of a left side matrix (i.e. H) and right side vector (i.e. G)
 */
void polytope_from_arrays(polytope *polytope, double *left_side, double *right_side, double *cheby, char*name){

    gsl_matrix_from_array(polytope->H, left_side, name);
    gsl_vector_from_array(polytope->G, right_side, name);
    for(int i = 0; i < polytope->H->size2; i++){
        polytope->chebyshev_center[i] = cheby[i];
    }
};

/**
 * Checks whether a state is in a certain polytope
 */
int polytope_check_state(polytope *polytope, gsl_vector *x){
    gsl_vector * result = gsl_vector_alloc(polytope->G->size);
    gsl_blas_dgemv(CblasNoTrans, 1.0, polytope->H, x, 0.0, result);
    for(size_t i = 0; i< polytope->G->size; i++){
        if(gsl_vector_get(result, i) >= gsl_vector_get(polytope->G, i)){
            return 0;
        }
    }
    return 1;
};

void polytope_to_constraints(matrix_t *new, polytope *original){
    for(size_t i = 0; i<original->H->size1; i++){
        pkint_set_si(new->p[i][0], 1);
        double g_i_d = gsl_vector_get(original->G, i);
//        int roundup =0;
//        if(g_i_d != round(g_i_d)){
            g_i_d = g_i_d*1000;
            g_i_d = round(g_i_d);
//            roundup = 1;
//        }
        int g_i = (int) g_i_d;
        pkint_set_si(new->p[i][1], g_i);
        for (size_t j = 0; j < original->H->size2; j++) {
            double h_i_j_d = gsl_matrix_get(original->H, i, j);
//            if(roundup == 1){
                h_i_j_d = h_i_j_d*(-1000);
                h_i_j_d = round(h_i_j_d);
//            }
            int h_i_j = (int) h_i_j_d;
            pkint_set_si(new->p[i][j+2], h_i_j);
        }
    }
};

void polytope_from_constraints(polytope *new, matrix_t *original){
    for(size_t i = 0; i<original->nbrows; i++){
        double g_i = (double)(original->p[i][1].rep);
        gsl_vector_set(new->G,i, g_i);
        for (size_t j = 0; j < new->H->size2; ++j) {
            double h_i_j = (double)(original->p[i][j+2].rep)*(-1);
            gsl_matrix_set(new->H,i,j, h_i_j);
        }
    }
};

int polytope_to_constraints_gurobi(polytope *constraints, GRBmodel *model, size_t N){

    int error = 0;
    double constraint_val[N];
    int ind[N];
    for(size_t i = 0; i < constraints->H->size1;i++){
        char constraint_name[5];
        sprintf(constraint_name, "c_%d", (int)i);
        for(size_t j = 0; j < N;j++){
            ind[j] = (int)j;
            constraint_val[j] = gsl_matrix_get(constraints->H,i,j);
        }

        error = GRBaddconstr(model, (int)N, ind, constraint_val, GRB_LESS_EQUAL, gsl_vector_get(constraints->G,i), constraint_name);

        if(error){
            return error;
        }
    }
    return error;
};