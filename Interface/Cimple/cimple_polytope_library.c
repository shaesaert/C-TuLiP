#include <gsl/gsl_matrix.h>
#include <gsl/gsl_vector.h>
#include "cimple_polytope_library.h"

/**
 * "Constructor" Dynamically allocates the space a polytope needs
 */
struct polytope *polytope_alloc(size_t k,
                                size_t n)
{

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
void polytope_free(polytope *polytope)
{
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
                        int time_horizon)
{

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
void cell_free(cell *cell)
{
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
                                            int time_horizon)
{

    struct abstract_state *return_abstract_state = malloc (sizeof (struct abstract_state));

    /*
     * Default values: at initialization safe mode is not yet computed.
     * Thus it is assumed that the state does not contain an invariant set => invariant_set = NULL
     * next_state (next state the system has to transition to reach an invariant set) is unknown at initialization.
     */

    return_abstract_state->next_state = NULL;
    return_abstract_state->invariant_set = NULL;
//    return_abstract_state->distance_invariant_set = INFINITY;

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

    return_abstract_state->convex_hull = polytope_alloc(k_hull, n);
    if (return_abstract_state->convex_hull == NULL) {
        free (return_abstract_state);
        return NULL;
    }

    return return_abstract_state;
};

/**
 * "Destructor" Deallocates the dynamically allocated memory of the region of polytopes
 */
void abstract_state_free(abstract_state * abstract_state){
    polytope_free(abstract_state->convex_hull);
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
                          char*name)
{

    gsl_matrix_from_array(polytope->H, left_side, name);
    gsl_vector_from_array(polytope->G, right_side, name);
    for(int i = 0; i < polytope->H->size2; i++){
        polytope->chebyshev_center[i] = cheby[i];
    }
};

/**
 * Converts a polytope in gsl form to cdd constraint form
 */
dd_PolyhedraPtr polytope_to_cdd(polytope *original,
                                dd_ErrorType *err)
{
    dd_PolyhedraPtr new;
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
    new = dd_DDMatrix2Poly(constraints, err);
    dd_FreeMatrix(constraints);
    return new;
};

/**
 * Converts a polytope in cdd constraint form to gsl form
 */
polytope * cdd_to_polytope(dd_PolyhedraPtr *original)
{

    dd_MatrixPtr constraints;
    constraints = dd_CopyInequalities(*original);
    polytope *new = polytope_alloc(constraints->rowsize, constraints->colsize-1);
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
    return new;

};

/**
 * Generate a polytope representing a scaled unit cube
 */
polytope * polytope_scaled_unit_cube(double scale,
                                     int dimensions)
{

    dd_PolyhedraPtr cube = cdd_scaled_unit_cube(scale, dimensions);
    polytope * return_cube = cdd_to_polytope(&cube);
    dd_FreePolyhedra(cube);

    return return_cube;
};

/**
 * Checks whether a state is in a certain polytope
 */
bool polytope_check_state(polytope *polytope,
                         gsl_vector *x)
{
    gsl_vector * result = gsl_vector_alloc(polytope->G->size);
    gsl_blas_dgemv(CblasNoTrans, 1.0, polytope->H, x, 0.0, result);
    for(size_t i = 0; i< polytope->G->size; i++){
        if(gsl_vector_get(result, i) > gsl_vector_get(polytope->G, i)){
            gsl_vector_free(result);
            return false;
        }
    }
    gsl_vector_free(result);
    return true;
};

/**
 * Checks whether polytope P1 \ issubset P2
 */
bool polytope_is_subset(polytope *P1,
                        polytope *P2)
{
    dd_ErrorType err = dd_NoError;
    dd_PolyhedraPtr first = polytope_to_cdd(P1, &err);
    dd_MatrixPtr verticesFirst = dd_CopyGenerators(first);
    gsl_vector *vertex = gsl_vector_alloc(P1->H->size2);
    gsl_vector_set_zero(vertex);
    int is_included;
    bool is_subset = true;
    for(int i = 0; i<verticesFirst->rowsize;i++){
        double valueFirst0 = dd_get_d(verticesFirst->matrix[i][0]);
        if(valueFirst0 == 1){
            for(int j = 0; j<vertex->size; j++){
                double valueFirstj = dd_get_d(verticesFirst->matrix[i][j+1]);
                gsl_vector_set(vertex,(size_t)j, valueFirstj);
            }
            is_included = polytope_check_state(P2,vertex);
            if(!is_included){
                is_subset = false;
                break;
            }
        }
    }
    gsl_vector_free(vertex);
    dd_FreePolyhedra(first);
    dd_FreeMatrix(verticesFirst);
    return is_subset;
};

/**
 * Unite inequalities of P1 and P2 in new polytope and remove redundancies
 */
polytope * polytope_unite_inequalities(polytope *P1,
                                       polytope *P2)
{
    polytope *united = polytope_alloc(P1->H->size1+P2->H->size1,P1->H->size2);
    //Unite H
    gsl_matrix_set_zero(united->H);
    gsl_matrix_view H_P1 = gsl_matrix_submatrix(united->H, 0, 0, P1->H->size1, P1->H->size2);
    gsl_matrix_memcpy(&H_P1.matrix, P1->H);
    gsl_matrix_view H_P2 = gsl_matrix_submatrix(united->H, P1->H->size1, 0, P2->H->size1, P2->H->size2);
    gsl_matrix_memcpy(&H_P2.matrix, P2->H);

    //Unite G
    gsl_vector_set_zero(united->G);
    gsl_vector_view G_P1 = gsl_vector_subvector(united->G, 0, P1->G->size);
    gsl_vector_memcpy(&G_P1.vector, P1->G);
    gsl_vector_view G_P2 = gsl_vector_subvector(united->G, P1->G->size,P2->G->size);
    gsl_vector_memcpy(&G_P2.vector, P2->G);
    polytope * return_polytope = polytope_minimize(united);

    polytope_free(united);

    return return_polytope;

};

/**
 * Project original polytope (in cdd format) to the first n dimensions
 */
polytope * polytope_projection(polytope * original,
                               size_t n)
{

    dd_ErrorType err;
    dd_PolyhedraPtr orig_cdd = polytope_to_cdd(original, &err);
    dd_PolyhedraPtr new_cdd = NULL;

    cdd_projection(&orig_cdd, &new_cdd, n, &err);
    polytope * new = cdd_to_polytope(&new_cdd);
    dd_FreePolyhedra(orig_cdd);
    dd_FreePolyhedra(new_cdd);

    return new;

};

polytope * polytope_linear_transform(polytope *original,
                                     gsl_matrix *scale){

    dd_ErrorType err = dd_NoError;
    dd_PolyhedraPtr orig_cdd = polytope_to_cdd(original, &err);

    dd_MatrixPtr vertices = dd_CopyGenerators(orig_cdd);

    dd_MatrixPtr transformed_vertices = dd_CreateMatrix(1, scale->size1+1);
    dd_MatrixPtr transformed_vertex = dd_CreateMatrix(1, scale->size1+1);
    bool new_matrix_started = false;
    gsl_vector *vertex = gsl_vector_alloc((vertices->colsize - 1));
    gsl_vector *scaled_vertex = gsl_vector_alloc(scale->size1);
    gsl_vector_set_zero(vertex);
    gsl_vector_set_zero(scaled_vertex);

    for(int i = 0; i<vertices->rowsize; i++) {
        //Check whether row represents ray or vertex
        double is_vertex = dd_get_d(vertices->matrix[i][0]);
        if (is_vertex == 1) {
            for (size_t j = 1; j < vertices->colsize; j++) {
                double value = dd_get_d(vertices->matrix[i][j]);
                gsl_vector_set(vertex, j-1, value);
            }
            gsl_blas_dgemv(CblasNoTrans, 1.0, scale, vertex, 0.0, scaled_vertex);

            if (new_matrix_started) {
                dd_set_d(transformed_vertex->matrix[0][0], 1);
                for (size_t j = 0; j < scaled_vertex->size; j++) {
                    dd_set_d(transformed_vertex->matrix[0][j + 1], gsl_vector_get(scaled_vertex, j));
                }
                dd_MatrixAppendTo(&transformed_vertices, transformed_vertex);
            } else {
                dd_set_d(transformed_vertices->matrix[0][0], 1);
                for (size_t j = 0; j < scaled_vertex->size; j++) {
                    dd_set_d(transformed_vertices->matrix[0][j + 1], gsl_vector_get(scaled_vertex, j));
                }
                new_matrix_started = true;
            }

        }
    }

    transformed_vertices->representation = dd_Generator;
    dd_PolyhedraPtr transformed_cdd = dd_DDMatrix2Poly(transformed_vertices, &err);
    polytope *transformed = cdd_to_polytope(&transformed_cdd);

    //Clean up
    dd_FreeMatrix(transformed_vertex);
    dd_FreeMatrix(transformed_vertices);
    dd_FreePolyhedra(orig_cdd);
    dd_FreePolyhedra(transformed_cdd);
    dd_FreeMatrix(vertices);
    gsl_vector_free(vertex);
    gsl_vector_free(scaled_vertex);

    return transformed;

};
/**
 * Remove redundancies from gsl polytope inequalities
 */
polytope * polytope_minimize(polytope *original)
{


    dd_ErrorType err = dd_NoError;
    dd_MatrixPtr min_matrix;

    dd_PolyhedraPtr cdd_original = polytope_to_cdd(original, &err);

    dd_PolyhedraPtr cdd_minimized = cdd_minimize(&cdd_original, &err);
    min_matrix = dd_CopyInequalities(cdd_minimized);

    polytope * minimized = cdd_to_polytope(&cdd_minimized);
    dd_FreeMatrix(min_matrix);
    dd_FreePolyhedra(cdd_original);
    dd_FreePolyhedra(cdd_minimized);

    return minimized;

};

/**
 * Compute Minkowski sum of two polytopes
 */
polytope * polytope_minkowski(polytope *P1,
                              polytope *P2)
{
    dd_ErrorType err = dd_NoError;
    dd_PolyhedraPtr A = polytope_to_cdd(P1, &err);
    dd_PolyhedraPtr B = polytope_to_cdd(P2, &err);
    dd_PolyhedraPtr C = cdd_minkowski(A,B);
    polytope * returnPolytope = cdd_to_polytope(&C);
    dd_FreePolyhedra(A);
    dd_FreePolyhedra(B);
    dd_FreePolyhedra(C);
    return returnPolytope;
};

/**
 * Compute Pontryagin difference C = A-B s.t.:
 * A-B = {c \in A-B| c+b \in A, \forall b \in B}
 */
polytope * polytope_pontryagin(polytope* A,
                               polytope* B)
{

    dd_ErrorType err;
    dd_MatrixPtr verticesA, verticesB;
    //create cddPoly A,B
    dd_PolyhedraPtr cddA = polytope_to_cdd(A, &err);

    dd_PolyhedraPtr cddB = polytope_to_cdd(B, &err);

    polytope *C = NULL;

    verticesA = dd_CopyGenerators(cddA);
    verticesB = dd_CopyGenerators(cddB);
    for(int i = 0; i<verticesB->rowsize; i++){
        //Check whether row represents ray or vertex
        double value_B0 = dd_get_d(verticesB->matrix[i][0]);
        if(value_B0 == 1){
            dd_MatrixPtr tempA;
            //A-b (where b is the vertex)
            tempA = dd_CreateMatrix(verticesA->rowsize,verticesA->colsize);
            //each vertex of A displaced by b
            for(int j = 0; j<verticesA->rowsize; j++){
                double value_A0 = dd_get_d(verticesA->matrix[j][0]);
                if(value_A0 == 1){
                    dd_set_d(tempA->matrix[j][0], 1);
                    for(int k = 1; k<verticesA->colsize; k++){
                        double value_Ak = dd_get_d(verticesA->matrix[j][k]);
                        double value_Bk = dd_get_d(verticesB->matrix[i][k]);
                        dd_set_d(tempA->matrix[j][k],(value_Ak-value_Bk));
                    }
                }else{
                    dd_set_d(tempA->matrix[j][0], 0);
                    for(int k = 1; k<verticesA->colsize; k++){
                        double value_Ak = dd_get_d(verticesA->matrix[j][k]);
                        dd_set_d(tempA->matrix[j][k],(value_Ak));
                    }
                }
            }
            dd_PolyhedraPtr cdd_temp;
            tempA->representation = dd_Generator;
            cdd_temp = dd_DDMatrix2Poly(tempA, &err);
            polytope *tempC = cdd_to_polytope(&cdd_temp);
            dd_FreePolyhedra(cdd_temp);
            if(C == NULL){
                C = polytope_alloc(tempC->H->size1,tempC->H->size2);
                gsl_matrix_memcpy(C->H,tempC->H);
                gsl_vector_memcpy(C->G,tempC->G);
                polytope_free(tempC);
            }else{
                polytope *copyC = C;
                C = polytope_unite_inequalities(copyC, tempC);
                polytope_free(tempC);
                polytope_free(copyC);
            }
            dd_FreeMatrix(tempA);
        }
    }

    dd_FreeMatrix(verticesA);
    dd_FreeMatrix(verticesB);
    dd_FreePolyhedra(cddA);
    dd_FreePolyhedra(cddB);
    return C;
};

/**
 * Set up constraints in quadratic problem for GUROBI
 */
int polytope_to_constraints_gurobi(polytope *constraints,
                                   GRBmodel *model,
                                   size_t N)
{

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

/**
 * Generate a polytope representing a scaled unit cube
 */
dd_PolyhedraPtr cdd_scaled_unit_cube(double scale,
                                     int dimensions)
{

    dd_MatrixPtr constraints;
    dd_PolyhedraPtr cube = NULL;
    dd_ErrorType err = dd_NoError;
    constraints = dd_CreateMatrix(dimensions*2,dimensions+1);
    for(int i = 0; i<(dimensions); i++){

            dd_set_d(constraints->matrix[2*i][0],(scale*0.5));
            dd_set_d(constraints->matrix[2*i][i+1],-1);
            dd_set_d(constraints->matrix[2*i+1][0],(scale*0.5));
            dd_set_d(constraints->matrix[2*i+1][i+1],1);
    }
    constraints->representation=dd_Inequality;
    cube = dd_DDMatrix2Poly(constraints, &err);
    dd_FreeMatrix(constraints);

    return cube;
};


/**
 * Project original polytope (in cdd format) to the first n dimensions
 */
void cdd_projection(dd_PolyhedraPtr *original,
                    dd_PolyhedraPtr *new,
                    size_t n,
                    dd_ErrorType *err)
{
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

/**
 * Remove redundancies from cdd polytope inequalities
 */
dd_PolyhedraPtr cdd_minimize(dd_PolyhedraPtr *original,
                             dd_ErrorType *err)
{

    dd_rowset redset,impl_linset;
    dd_rowindex newpos;
    dd_MatrixPtr full=NULL;
    full = dd_CopyInequalities(*original);
    dd_MatrixCanonicalize(&full,&impl_linset,&redset,&newpos,err);

    full->representation = dd_Inequality;
    dd_PolyhedraPtr new = dd_DDMatrix2Poly(full, err);
    dd_FreeMatrix(full);
    set_free(redset);
    set_free(impl_linset);
    free(newpos);
    return new;

};