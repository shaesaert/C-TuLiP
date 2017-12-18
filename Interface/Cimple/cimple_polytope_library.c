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

}

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
    gsl_vector * result = gsl_vector_alloc(x->size);
    gsl_blas_dgemv(CblasNoTrans, 1.0, polytope->H, x, 0.0, result);
    for(size_t i = 1; i<= x->size; i++){
        if(gsl_vector_get(result, i) <= gsl_vector_get(polytope->G, i)){
            return 0;
        }
    }
    return 1;
};

void polytope_to_constraints(matrix_t *new, polytope *original){
    for(size_t i = 0; i<original->H->size1; i++){
        pkint_set_si(new->p[i][0], 1);
        double g_i_d = gsl_vector_get(original->G, i);
        g_i_d = g_i_d*1000;
        g_i_d = round(g_i_d);
        int g_i = (int) g_i_d;
        pkint_set_si(new->p[i][1], g_i);
        for (size_t j = 0; j < original->H->size2; j++) {
            double h_i_j_d = gsl_matrix_get(original->H, i, j);
            h_i_j_d = h_i_j_d*(-1000);
            h_i_j_d = round(h_i_j_d);
            int h_i_j = (int) h_i_j_d;
            pkint_set_si(new->p[i][j+2], h_i_j);
        }
    }
}

void polytope_from_constraints(polytope *new, matrix_t *original){
    for(size_t i = 0; i<original->nbrows; i++){
        long g_i = original->p[i][1].rep;
        double g_i_d = g_i/1000;
        gsl_vector_set(new->G,i, g_i_d);
        for (size_t j = 0; j < new->H->size2; ++j) {
            long h_i_j = original->p[i][j+2].rep;
            double h_i_j_d = h_i_j/1000;
            gsl_matrix_set(new->H,i,j, h_i_j_d);
        }
    }
}
//TODO project on array of dimensions instead of first n dimensions
/**
 * Projects polytope on lower dimensions (e.g. new_dimension = n => projects polytope on first n columns)
 */
void polytope_project(polytope *polytope, size_t new_dimension){
//    /*Projects a polytope onto lower dimensions.
//
//    Available solvers are:
//
//    - "esp": Equality Set Projection;
//    - "exthull": vertex projection;
//    - "fm": Fourier-Motzkin projection;
//    - "iterhull": iterative hull method.
//
//            Example:
//    To project the polytope `P` onto the first three dimensions, use
//                                                                         >>> P_proj = projection(P, [1,2,3])
//
//    @param poly1: Polytope to project
//    @param dim: Dimensions on which to project
//    @param solver: A solver can be specified, if left blank an attempt
//    is made to choose the most suitable solver.
//    @param verbose: if positive, print solver used in case of
//        guessing; default is 0 (be silent).
//
//    @rtype: L{Polytope}
//    @return: Projected polytope in lower dimension
//     */
//    // already flat?
//    if (polytope->H->size1 <= new_dimension){
//        return ;
//    }
//    // `poly1` isn't flat
//    poly_dim = poly1.dim;
//    org_dim = xrange(poly_dim);
//    new_dim = dim.flatten() - 1;
//    del_dim = np.setdiff1d(org_dim, new_dim); // Index of dimensions to remove
//    // enlarge A, b with zeros
//    A = poly1.A.copy();
//    poly1.A = np.zeros((poly_dim, poly_dim));
//    poly1.A[0:mA, 0:nA] = A;
//    // stack
//    poly1.b = np.hstack([poly1.b, np.zeros(poly_dim - mA)]);
//    // Compute cheby ball in lower dim to see if projection exists
//    norm = np.sum(poly1.A*poly1.A, axis=1).flatten();
//    norm[del_dim] = 0;
//    c = np.zeros(len(org_dim)+1, dtype=float);
//    c[len(org_dim)] = -1;
//    G = np.hstack([poly1.A, norm.reshape(norm.size, 1)]);
//    h = poly1.b;
//    sol = lpsolve(c, G, h)
//    if (sol['status'] != 0){
//    // Projection not fulldim
//        return ;
//        }
//    if (sol['x'][-1] < abs_tol){
//        return ;
//        }
//    // select solver method based on dimension criteria
//    if (len(del_dim) <= 2){
//        projection_fm(poly1, new_dim, del_dim);
//        return;
//    }else if(len(org_dim) <= 4){
//        projection_exthull(poly1, new_dim);
//        return;
//    }else{
//        projection_iterhull(poly1, new_dim);
//        return;
//    }
};

/**
 * Reduces redundant number of rows of polytope
 */
void polytope_reduce(polytope *polytope){
//    polytope_list *polytopeHead = NULL;
// poly, nonEmptyBounded=1, abs_tol=ABS_TOL

// Does not check if it is a region
//    if isinstance(poly, Region):
//    lst = []
//    for poly2 in poly.list_poly:
//    red = reduce(poly2)
//    if is_fulldim(red):
//    lst.append(red)
//    if len(lst) > 0:
//    return Region(lst, poly.props)
//    else:
//    return Polytope()

// is `poly` already in minimal representation ?
//    if poly.minrep:
//    return poly
//    if not is_fulldim(poly):
//        return Polytope()

// `poly` isn't flat
//    A_arr = poly.A
//    b_arr = poly.b

// Remove rows with b = inf
//
//    // create list h, g and diagonal norm matrix
//    int num_eq = 0;
//    gsl_vector * norm_vector = gsl_vector_alloc(polytope->H->size2 + 1);
//    gsl_vector_set_zero(norm_vector);
//    for(size_t i = polytope->G->size; i < 0; i--){
//        if(gsl_vector_get(polytope->G, i-1) != INFINITY){
//            for(size_t j = 0; j < polytope->H->size2; j++){
//                double current_value = gsl_vector_get(norm_vector,j);
//                double value = gsl_matrix_get(polytope->H, i, j);
//                current_value += value * value;
//                gsl_vector_set(norm_vector, j, current_value);
//            }
//            double current_g_value = gsl_vector_get(norm_vector, polytope->H->size2);
//            double g_value = gsl_vector_get(polytope->G,i);
//            current_g_value += g_value*g_value;
//            gsl_vector_set(norm_vector, polytope->H->size2, current_g_value);
//            gsl_vector_view current_view = gsl_matrix_row(polytope->H, i);
//            polytope_list_push(&polytopeHead, &current_view.vector ,gsl_vector_get(polytope->G, i));
//            num_eq++;
//        }
//    }
//    for(size_t k = 0; k < norm_vector->size; k++){
//        double norm_squared = gsl_vector_get(norm_vector , k);
//        norm_squared = 1/sqrt(norm_squared);
//        gsl_vector_set(norm_vector, k, norm_squared);
//    }
//    gsl_matrix_diag_from_vector(norm_vector);
//    gsl_vector_free(norm_vector);
//
// first eliminate the linearly dependent rows corresponding to the same hyperplane
//    M1 = np.hstack([A_arr, np.array([b_arr]).T]).T
//            M1row = 1/sqrt(np.sum(M1**2, 0))
//    M1n = np.dot(M1, np.diag(M1row))
//    M1n = M1n.T
//    keep_row = []
//    for i in xrange(neq):
//    keep_i = 1
//    for j in xrange(i+1, neq):
//    if np.dot(M1n[i].T, M1n[j]) > 1-abs_tol:
//    keep_i = 0
//    if keep_i:
//        keep_row.append(i)
//    A_arr = A_arr[keep_row]
//    b_arr = b_arr[keep_row]
//    neq, nx = A_arr.shape
//    if nonEmptyBounded:
//        if neq <= nx+1:
//    return Polytope(A_arr, b_arr)
//// Now eliminate hyperplanes outside the bounding box
//    if neq > 3*nx:
//    lb, ub = Polytope(A_arr, b_arr).bounding_box
////cand = -(np.dot((A_arr>0)*A_arr,ub-lb)
////-(b_arr-np.dot(A_arr,lb).T).T<-1e-4)
//    cand = ~ (np.dot((A_arr > 0)*A_arr, ub-lb) -
//              (np.array([b_arr]).T-np.dot(A_arr, lb)) < -1e-4)
//    A_arr = A_arr[cand.squeeze()]
//    b_arr = b_arr[cand.squeeze()]
//    neq, nx = A_arr.shape
//    if nonEmptyBounded:
//        if neq <= nx+1:
//    return Polytope(A_arr, b_arr)
//    del keep_row[:]
//    for k in xrange(A_arr.shape[0]):
//    f = -A_arr[k, :]
//    G = A_arr
//    h = b_arr
//    h[k] += 0.1
//    sol = lpsolve(f, G, h)
//    h[k] -= 0.1
//    if sol['status'] == 0:
//    obj = -sol['fun'] - h[k]
//    if obj > abs_tol:
//    keep_row.append(k)
//    elif sol['status'] == 3:
//    keep_row.append(k)
//    polyOut = Polytope(A_arr[keep_row], b_arr[keep_row])
//    polyOut.minrep = True
//    return polyOut

};

void polytope_list_push(polytope_list **list_head, gsl_vector * newVector, double newValue){

    polytope_list *newNode = NULL;

    /* Allocate memory for new node (with its payload). */
    newNode=malloc(sizeof(*newNode));
    if(NULL == newNode) {
        fprintf(stderr, "Error: malloc() failed.\n");
        exit(EXIT_FAILURE);
    }

    /* Initialize the new node's content. */
    newNode->vector = newVector;
    newNode->value = newValue;

    /* Link this node into the list as the new head node. */
    newNode->node = *list_head;
    *list_head = newNode;
}