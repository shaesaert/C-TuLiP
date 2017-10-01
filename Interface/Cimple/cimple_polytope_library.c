//
// Created by be107admin on 9/25/17.
//

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
void polytope_from_arrays(polytope *polytope, size_t k, size_t n, double *left_side, double *right_side, char*name){

    gsl_matrix_from_array(polytope->H, left_side, name);
    gsl_vector_from_array(polytope->G, right_side, name);
};

/**
 * Checks whether a state is in a certain polytope
 */
int state_in_polytope(polytope *polytope, gsl_vector *x){
    gsl_vector * result = gsl_vector_alloc(x->size);
    gsl_blas_dgemv(CblasNoTrans, 1.0, polytope->H, x, 0.0, result);
    for(size_t i = 1; i<= x->size; i++){
        if(gsl_vector_get(result, i) <= gsl_vector_get(polytope->G, i)){
            return 0;
        }
    }
    return 1;
};

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
//    // create list h, g
//    int num_eq = 0;
//    for(int i = 0; i < polytope->G->size; i++){
//        if(gsl_vector_get(polytope->G, i) != INFINITY){
//            // add gsl_matrix_row(polytope->H, i); to list h
//            // add gsl_vector_get(polytope->G, i); to list g
//            num_eq++;
//        }
//    }
//// first eliminate the linearly dependent rows corresponding to the same hyperplane
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
