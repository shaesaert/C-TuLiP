//
// Created by be107admin on 9/25/17.
//

#include "cimple_polytope_library.h"

/**
 * "Constructor" Dynamically allocates the space a polytope needs
 */
struct polytope *polytope_alloc(size_t k,
                                size_t n){

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
};

/**
 * "Destructor" Deallocates the dynamically allocated memory of the polytope
 */
void polytope_free(polytope *polytope){
    gsl_matrix_free(polytope->H);
    gsl_vector_free(polytope->G);
    free(polytope->chebyshev_center);
    free(polytope);
};
/**
 * "Constructor" Dynamically allocates the space a polytope needs
 */
struct cell *cell_alloc(size_t k,
                        size_t n,
                        int time_horizon){

    struct cell *return_cell = malloc (sizeof (struct cell));

    return_cell->safe_mode = malloc(sizeof(polytope)*time_horizon);
    if (return_cell->safe_mode == NULL) {
        free (return_cell);
        return NULL;
    }

    return_cell->polytope_description = polytope_alloc(k,n);
    if (return_cell->polytope_description == NULL) {
        free (return_cell);
        return NULL;
    }
    return return_cell;
};

/**
 * "Destructor" Deallocates the dynamically allocated memory of the region of polytopes
 */
void cell_free(cell *cell){
    polytope_free(cell->polytope_description);
    free(cell->safe_mode);
    free(cell);

};
/**
 * "Constructor" Dynamically allocates the space a region of polytope needs
 */
struct abstract_state *abstract_state_alloc(size_t *k,
                                            size_t k_hull,
                                            size_t n,
                                            int transitions_in_count,
                                            int transitions_out_count,
                                            int cells_count,
                                            int time_horizon){

    struct abstract_state *return_abstract_state = malloc (sizeof (struct abstract_state));

    /*
     * Default values: at initialization safe mode is not yet computed.
     * Thus it is assumed that the state does not contain an invariant set => invariant_set = NULL
     * next_state (next state the system has to transition to reach an invariant set) is unknown at initialization.
     */

    return_abstract_state->next_state = NULL;
    return_abstract_state->invariant_set = NULL;
    return_abstract_state->distance_invariant_set = NULL;

    return_abstract_state->cells = malloc(sizeof(cell)*cells_count);
    if (return_abstract_state->cells == NULL) {
        free (return_abstract_state);
        return NULL;
    }

    for(int i = 0; i < cells_count; i++){
        return_abstract_state->cells[i] = cell_alloc(*(k+i), n, time_horizon);
        if (return_abstract_state->cells[i] == NULL) {
            free (return_abstract_state);
            return NULL;
        }
    }

    return_abstract_state->cells_count = cells_count;

    return_abstract_state->transitions_in = malloc(sizeof(struct abstract_state) * transitions_in_count);
    if (return_abstract_state->transitions_in == NULL) {
        free (return_abstract_state);
        return NULL;
    }

    return_abstract_state->transitions_in_count = transitions_in_count;

    return_abstract_state->transitions_out = malloc(sizeof(struct abstract_state) * transitions_out_count);
    if (return_abstract_state->transitions_out == NULL) {
        free (return_abstract_state);
        return NULL;
    }

    return_abstract_state->transitions_out_count = transitions_out_count;

    return_abstract_state->hull_over_polytopes = polytope_alloc(k_hull, n);
    if (return_abstract_state->hull_over_polytopes == NULL) {
        free (return_abstract_state);
        return NULL;
    }

    return return_abstract_state;
};

/**
 * "Destructor" Deallocates the dynamically allocated memory of the region of polytopes
 */
void abstract_state_free(abstract_state * abstract_state){
    polytope_free(abstract_state->hull_over_polytopes);
    for(int i = 0; i< abstract_state->cells_count; i++){
        cell_free(abstract_state->cells[i]);
    }
    free(abstract_state->transitions_out);
    free(abstract_state->transitions_in);
    free(abstract_state->cells);
    free(abstract_state);

};

/**
 * Converts two C arrays to a polytope consistent of a left side matrix (i.e. H) and right side vector (i.e. G)
 */
void polytope_from_arrays(polytope *polytope,
                          double *left_side,
                          double *right_side,
                          double *cheby,
                          char*name){

    gsl_matrix_from_array(polytope->H, left_side, name);
    gsl_vector_from_array(polytope->G, right_side, name);
    for(int i = 0; i < polytope->H->size2; i++){
        polytope->chebyshev_center[i] = cheby[i];
    }
};

/**
 * Checks whether a state is in a certain polytope
 */
int polytope_check_state(polytope *polytope,
                         gsl_vector *x){
    gsl_vector * result = gsl_vector_alloc(polytope->G->size);
    gsl_blas_dgemv(CblasNoTrans, 1.0, polytope->H, x, 0.0, result);
    for(size_t i = 0; i< polytope->G->size; i++){
        if(gsl_vector_get(result, i) > gsl_vector_get(polytope->G, i)){
            gsl_vector_free(result);
            return 0;
        }
    }
    gsl_vector_free(result);
    return 1;
};

/*
 * Converts a polytope in gsl form to cdd constraint form
 */
void polytope_to_cdd_constraints(polytope *original, dd_PolyhedraPtr *new, dd_ErrorType *err){
    dd_MatrixPtr constraints;
    constraints = dd_CreateMatrix(original->H->size1, (original->H->size2+1));
    for (size_t k = 0; k < (original->H->size1); k++) {
        double value = gsl_vector_get(original->G, k);
        dd_set_d(constraints->matrix[k][0],value);
    }
    for(size_t i = 0; i<original->H->size1; i++){
        for (size_t j = 1; j < (original->H->size2+1); j++) {
            double value = gsl_matrix_get(original->H, i, j-1);
            dd_set_d(constraints->matrix[i][j],-1*value);
        }
    }
    constraints->representation=dd_Inequality;
    *new = dd_DDMatrix2Poly(constraints, err);
    dd_FreeMatrix(constraints);
};

/*
 * Converts a polytope in cdd constraint form to gsl form
 */
void cdd_constraints_to_polytope(dd_PolyhedraPtr *original, polytope * new){

    dd_MatrixPtr constraints;
    constraints = dd_CopyInequalities(*original);
    for (size_t k = 0; k < (constraints->rowsize); k++) {
        double value = dd_get_d(constraints->matrix[k][0]);
        gsl_vector_set(new->G, k, value);
    }
    for(size_t i = 0; i<constraints->rowsize; i++){
        for (size_t j = 0; j < (constraints->colsize-1); j++) {
            double value = dd_get_d(constraints->matrix[i][j+1]);
            gsl_matrix_set(new->H,i,j,-value);
        }
    }
    dd_FreeMatrix(constraints);

};

int polytope_to_constraints_gurobi(polytope *constraints,
                                   GRBmodel *model,
                                   size_t N){

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

/*
 * Project original polytope (in cdd format) to the first n dimensions
 */
void cdd_projection(dd_PolyhedraPtr *original,
                    dd_PolyhedraPtr *new,
                    size_t n,
                    dd_ErrorType *err){
    dd_MatrixPtr full=NULL,projected=NULL;
    full = dd_CopyInequalities(*original);
    dd_colrange j,d;
    dd_rowset redset,impl_linset;
    dd_colset delset;
    dd_rowindex newpos;

    d=full->colsize;
    set_initialize(&delset, d);
    for (j=n+1; j<d; j++){
        set_addelem(delset, j+1);
    }

    projected=dd_BlockElimination(full, delset, err);

    dd_MatrixCanonicalize(&projected,&impl_linset,&redset,&newpos,err);

    dd_FreeMatrix(full);
    projected->representation = dd_Inequality;
    *new = dd_DDMatrix2Poly(projected, err);
    dd_FreeMatrix(projected);
    set_free(delset);
    set_free(redset);
    set_free(impl_linset);
    free(newpos);

};
/*
 * Project original polytope (in cdd format) to the first n dimensions
 */
void polytope_projection(polytope * original,
                         polytope * new,
                         size_t n){
    dd_PolyhedraPtr orig_cdd,new_cdd = NULL;
    dd_ErrorType err;
    polytope_to_cdd_constraints(original, &orig_cdd, &err);
    cdd_projection(&orig_cdd, &new_cdd, n, &err);
    cdd_constraints_to_polytope(&new_cdd, new);

};

void cdd_minimize(dd_PolyhedraPtr *original, dd_PolyhedraPtr *minimized){

    dd_MatrixPtr orig_matrix = dd_CopyInequalities(*original);
    dd_MatrixPtr min_matrix=NULL;
    dd_ErrorType err=dd_NoError;
    dd_rowset redrows,linrows;

    redrows=dd_RedundantRows(orig_matrix, &err);

    min_matrix=dd_MatrixSubmatrix(orig_matrix, redrows);

    set_free(redrows);
    linrows=dd_ImplicitLinearityRows(min_matrix, &err);

    set_card(linrows);
    set_uni(min_matrix->linset, min_matrix->linset, linrows);
    set_free(linrows);
    /* add the implicit linrows to the given linearity rows */

    dd_WriteMatrix(stdout, min_matrix);

    *minimized = dd_DDMatrix2Poly(min_matrix, &err);
    dd_FreeMatrix(orig_matrix);
    dd_FreeMatrix(min_matrix);

};

polytope * polytope_minimize(polytope *original){


    dd_ErrorType err = dd_NoError;
    dd_PolyhedraPtr cdd_original = NULL, cdd_minimized = NULL;
    dd_MatrixPtr min_matrix;

    polytope_to_cdd_constraints(original, &cdd_original, &err);

    cdd_minimize(&cdd_original, &cdd_minimized);
    min_matrix = dd_CopyInequalities(cdd_minimized);

    polytope * minimized = polytope_alloc((size_t)min_matrix->rowsize,((size_t)min_matrix->colsize-1));
    cdd_constraints_to_polytope(&cdd_minimized, minimized);
    dd_FreeMatrix(min_matrix);
    dd_FreePolyhedra(cdd_original);
    dd_FreePolyhedra(cdd_minimized);

    return minimized;

};
///*
// * Compute Pontryagin difference C = A-B s.t.:
// * A-B = {c \in A-B| c+b \in A, \forall b \in B}
// */
//polytope * pontryagin_difference(polytope* A, polytope* B){
//
//    dd_ErrorType err;
//    dd_PolyhedraPtr cddA, cddB;
//    //create cddPoly A,B
//    polytope_to_cdd_constraints(A, cddA, err);

//    polytope_to_cdd_constraints(B, cddB, err);
//    //create cddPoly C
//    dd_PolyhedraPtr cddC;
//    //foreach vertice \in B: A-b
//    //add inequalities to C

//    //remove redundancies C

//    //cdd C to polytope C

//    //free cdd parts
//    return C;
//}