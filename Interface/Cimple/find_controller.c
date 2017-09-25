//
// Created by L.Jonathan Feldstein
//

#include <gsl/gsl_matrix.h>
#include <gsl/gsl_vector_double.h>
#include <gsl/gsl_cblas.h>
#include <gsl/gsl_blas.h>
#include "find_controller.h"

//void projection_fm(polytope poly, int new_dim, int del_dim);
//void projection_exthull(polytope poly, int new_dim);
//void projection_iterhull(polytope poly, int new_dim);

void gsl_vector_from_array(gsl_vector *vector, double *array){
    for(size_t j = 0; j<vector->size; j++){
        gsl_vector_set(vector, j, array[j]);
    }
};

void gsl_matrix_from_array(gsl_matrix *matrix, double *array){
    for(size_t i = 0; i < matrix->size1; i++){
        for(size_t j = 0; j<matrix->size2; j++){
            gsl_matrix_set(matrix, i, j, array[j+matrix->size2*i]);
        }
    }
};

void polytope_from_arrays(polytope *polytope, size_t k, size_t n, double *left_side, double *right_side){

    gsl_matrix_from_array(polytope->H, left_side);
    gsl_vector_from_array(polytope->G, right_side);
};
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
void apply_control(gsl_vector *x, gsl_matrix *u, gsl_matrix *A, gsl_matrix *B) {
    //TODO:printf("apply_control: begin at x[0] = %f\n", *x);
    //fflush(stdout);
    //Apply input to state of next N time steps
    // x[k+1] = A.x[k] + B.u[k+1]
    for (size_t k = 0; k < (u->size2); k++){
        gsl_vector *Btu = gsl_vector_alloc(x->size);
        gsl_vector_view u_col = gsl_matrix_column(u,k);

        //A.x[k-1]
        gsl_blas_dgemv(CblasNoTrans, 1, A, x, 0, x);
        //B.u[k]
        gsl_blas_dgemv(CblasNoTrans, 1, B, &u_col.vector, 0 , Btu);
        //update x[k-1] => x[k]
        gsl_vector_add(x, Btu);
        gsl_vector_free(Btu);
        //TODO:printf("apply_control: u[%d] = %d; x[%d] = %f", k, u[k], k++, *x);
        //fflush(stdout);
    }
};
void project_polytope(polytope *polytope, size_t new_dimension){
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
//TODO
void reduce_polytope(polytope *polytope){
//////////////////////////////////////////////////////////////////////
//    Removes redundant inequalities in the hyperplane representation
//    of the polytope with the algorithm described at
//    http://www.ifor.math.ethz.ch/~fukuda/polyfaq/node24.html
//    by solving one LP for each facet
//
//    Warning:
//    - nonEmptyBounded == 0 case is not tested much.
//
//    @type poly: L{Polytope} or L{Region}
//
//    @return: Reduced L{Polytope} or L{Region} object
//////////////////////////////////////////////////////////////////////

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

void solve_feasible_closed_loop(polytope *return_polytope, polytope *P1, polytope *P2, system_dynamics *s_dyn){
    /*Under-approximate N-step attractor of polytope P2, with N > 0.
     *
     *See docstring of function `_solve_closed_loop_fixed_horizon`
     *for details.
     **/
    //print_horizon_warning()
    // one step backwards in time

    size_t n = s_dyn->A->size2;  // State space dimension;
    size_t m = s_dyn->B->size2;  // Input space dimension;
    size_t p = s_dyn->E->size2;  // Disturbance space dimension;


    size_t sum_dim = P1->H->size1+P2->H->size1;

    polytope *precedent_polytope = polytope_alloc(sum_dim+s_dyn->U_set->H->size1, n+m);

    // FOR precedent_polytope G
    /*
     *     |   P1_G      |
     * G = |P2_G - P2_H.K|
     *     |     0       |
     */
    gsl_vector_set_zero(precedent_polytope->G);
    gsl_vector_view G_P1 = gsl_vector_subvector(precedent_polytope->G, 0, P1->G->size);
    gsl_vector_memcpy(&G_P1.vector, P1->G);
    gsl_vector_view G_P2 = gsl_vector_subvector(precedent_polytope->G, P1->G->size,P2->G->size);
    gsl_vector_memcpy(&G_P2.vector, P2->G);
    gsl_vector * P2_HdotK = gsl_vector_alloc(P2->G->size);
    gsl_blas_dgemv(CblasNoTrans,1.0, P2->H, s_dyn->K, 0.0, P2_HdotK);
    gsl_vector_sub(&G_P2.vector, P2_HdotK);
    //Clean up!
    gsl_vector_free(P2_HdotK);

    // FOR Dist
    /*
     *         |  0   |
     * Dist =  |P2_H.E|
     *         |  0   |
     */
    gsl_matrix *Dist = gsl_matrix_alloc(sum_dim+s_dyn->U_set->H->size1, p);
    gsl_matrix_set_zero(Dist);
    gsl_matrix_view Dist_P2 = gsl_matrix_submatrix(Dist, P1->H->size1, 0, P2->H->size1, Dist->size2);
    gsl_blas_dgemm(CblasNoTrans,CblasNoTrans, 1.0, P2->H, s_dyn->E, 0.0, &Dist_P2.matrix);

    // FOR precedent_polytope H
    /*
     *  H = |H1   0 |
     *      |H2A H2B|
     *      |  HU   |
     */
    gsl_matrix_set_zero(precedent_polytope->H);

    gsl_matrix_view H_P1 = gsl_matrix_submatrix(precedent_polytope->H, 0, 0, P1->H->size1, n);
    gsl_matrix_memcpy(&H_P1.matrix, P1->H);
    gsl_matrix_view H_P2_1 = gsl_matrix_submatrix(precedent_polytope->H, P1->H->size1, 0, P2->H->size1, n);
    gsl_blas_dgemm(CblasNoTrans,CblasNoTrans, 1.0, P2->H, s_dyn->A, 0.0, &H_P2_1.matrix);
    gsl_matrix_view H_P2_2 = gsl_matrix_submatrix(precedent_polytope->H, P1->H->size1, n, P2->H->size1, m);
    gsl_blas_dgemm(CblasNoTrans,CblasNoTrans, 1.0, P2->H, s_dyn->B, 0.0, &H_P2_2.matrix);

    if (s_dyn->U_set->H->size2 == m){
        gsl_matrix_view HU = gsl_matrix_submatrix(precedent_polytope->H,sum_dim, n, s_dyn->U_set->H->size1,m);
        gsl_matrix_memcpy(&HU.matrix,s_dyn->U_set->H);
    } else if (s_dyn->U_set->H->size2 == m+n){
        // transforms U_set.H from |constraints_ input constraints_state| to |constraints_state constraints_input|
        /*
         * |m m m m n n n|    |n n n m m m m|
         * |m m m m n n n| => |n n n m m m m|
         * |m m m m n n n|    |n n n m m m m|
         */
        gsl_matrix_view HU = gsl_matrix_submatrix(precedent_polytope->H,sum_dim, n, s_dyn->U_set->H->size1,m);
        gsl_matrix * exchange_matrix = gsl_matrix_alloc(n+m,n+m);
        gsl_matrix_set_zero(exchange_matrix);
        gsl_matrix_view eye_m = gsl_matrix_submatrix(exchange_matrix, 0, n, m, m);
        gsl_matrix_set_identity(&eye_m.matrix);
        gsl_matrix_view eye_n = gsl_matrix_submatrix(exchange_matrix, m, 0, n, n);
        gsl_matrix_set_identity(&eye_n.matrix);
        gsl_blas_dgemm(CblasNoTrans,CblasNoTrans,1.0, s_dyn->U_set->H,exchange_matrix, 0.0, &HU.matrix);
    }

    // Get disturbance sets
    gsl_vector * D_hat = gsl_vector_alloc(precedent_polytope->G->size);
    if (!(gsl_matrix_isnull(Dist))){
        gsl_matrix * maxima = gsl_matrix_alloc(Dist->size1, s_dyn->helper_functions->D_one_step->size2);
        //Calculate Dist.Dextremes (extremum of each dimension of each polytope)
        gsl_blas_dgemm(CblasNoTrans, CblasNoTrans, 1.0, Dist, s_dyn->helper_functions->D_one_step,0.0, maxima);
        //find the maximum for each dimension of each polytope
        for(size_t i = 0; i < sum_dim; i++){
            gsl_vector_view max_row = gsl_matrix_row(maxima, i);
            gsl_vector_set(D_hat, i, gsl_vector_max(&max_row.vector));
        }
        gsl_matrix_free(maxima);
    } else{
        gsl_vector_set_zero(D_hat);
    }
    gsl_matrix_free(Dist);
    gsl_vector_sub(precedent_polytope->G, D_hat);
    //Clean up!
    gsl_vector_free(D_hat);

    reduce_polytope(precedent_polytope);

    // Project precedent polytope onto lower dim
    project_polytope(precedent_polytope, n);

    reduce_polytope(precedent_polytope);

    gsl_matrix_view precedent_view = gsl_matrix_submatrix(precedent_polytope->H,0,0,precedent_polytope->H->size1, n);

    gsl_matrix_memcpy(return_polytope->H,&precedent_view.matrix);
    gsl_vector_memcpy(return_polytope->G,precedent_polytope->G);
    polytope_free(precedent_polytope);
};

void set_path_constraints(gsl_matrix *L_full,gsl_vector *M_full, system_dynamics * s_dyn, polytope *list_polytopes[], size_t N){
////////////////////////////////////////////////////////////////////////////////
//    Compute the components of the polytope::
//
//    L [x(0)' u(0)' ... u(N-1)']' <= M
//
//    which stacks the following constraints:
//
//    - x(t+1) = A x(t) + B u(t) + E d(t)
//    - [u(k); x(k)] \in ssys.Uset for all k
//
//    If list_P is a C{Polytope}:
//
//    - x(0) \in list_P if list_P
//    - x(k) \in Pk for k= 1,2, .. N-1
//    - x(N) \in PN
//
//    If list_P is a list of polytopes:
//
//    - x(k) \in list_P[k] for k= 0, 1 ... N
//
//    The returned polytope describes the intersection of the polytopes
//    for all possible
//
//    @param ssys: system dynamics
//    @type ssys: L{LtiSysDyn}
//
//    @param N: horizon length
//
//    @type list_P: list of Polytopes or C{Polytope}
//    @type Pk: C{Polytope}
//    @type PN: C{Polytope}
//
////////////////////////////////////////////////////////////////////////////////

    //Disturbance assumed at every step
    //Also ... NO DEFAULT IF E NOT FULL DIMENSION OF s_dyn.Wset >> Will lead to problems when multiplying Gk.D

    // Help variables
    size_t n = s_dyn->A->size2;  // State space dimension
    size_t p = s_dyn->E->size2;  // Disturbance space dimension
    size_t sum_polytope_dim = 0; // Sum of dimension n of all polytopes in the list
    for(size_t i = 0; i < N; i++){

        sum_polytope_dim += list_polytopes[i]->H->size1;

    }

/* INITIALIZE MATRICES: Lk, Mk, Gk, H_diag*/
    gsl_matrix_view Lk = gsl_matrix_submatrix(L_full, 0, 0, sum_polytope_dim, L_full->size2);
    gsl_vector_view Mk = gsl_vector_subvector(M_full, 0, sum_polytope_dim);

    /*
     *     |G_0|
     *     |G_1|
     *Mk = |G_2| dim[sum_polytope_dim x 1]
     *     |G_3|
     *     |G_4|
     *
     *   with M = |Mk|
     *            |Mu|
     * */
    //Reset Mk
    gsl_vector_set_zero(&Mk.vector);

    gsl_matrix *Gk = gsl_matrix_alloc(sum_polytope_dim, p*N);

    /*
     *                          |0            0          0        0      0|
     *                          |H_1.E        0          0        0      0|
     *Gk =  H_diag.E_default  = |H_2.A.E    H_2.E        0        0      0| dim[sum_polytope_dim x p*N]
     *                          |H_3.A^2.E  H_3.A.E    H_3.E      0      0|
     *                          |H_4.A^3.E  H_4.A^3.E  H_4.A.E  H_4.E    0|
     * */
    gsl_matrix_set_zero(Gk);
    gsl_matrix *H_diag= gsl_matrix_alloc(sum_polytope_dim, n*N);
    gsl_matrix_set_zero(H_diag);

    /*
     *          |H_0 0  0  0  0 |
     *          |0 H_1  0  0  0 |
     * H_diag=  |0  0  H_2 0  0 | dim[sum_polytope_dim x n*N]
     *          |0  0   0 H_3 0 |
     *          |0  0   0  0 H_4|
     * */

    //Loop over N and polytopes in parallel
    size_t polytope_count = 0;
    for(int i = 0; i<N; i++){

        polytope *polytope_step_i = list_polytopes[i];

        //Set diagonal block N of H_diag
        for(size_t j = 0; j<n; j++){

            for(size_t k = 0; k<polytope_step_i->H->size1; k++){
                gsl_matrix_set(H_diag,polytope_count+k, j+(i*n), gsl_matrix_get(polytope_step_i->H,k,j));
            }
        }

        // Build guarantee Matrix       M
        for(size_t j = 0; j<polytope_step_i->G->size; j++){
            // Set entries Mk[j+polytope_count] = G_i[j]
            gsl_vector_set(&Mk.vector,j+polytope_count,gsl_vector_get(polytope_step_i->G,j));
        }

        polytope_count += polytope_step_i->H->size1;

    }

/*Update L and M*/
    // Lk = H_diag.L_default
    gsl_blas_dgemm(CblasNoTrans,CblasNoTrans,1.0, H_diag, s_dyn->helper_functions->L_default,0.0,&Lk.matrix);

    // Gk = H_diag.E_default
    gsl_blas_dgemm(CblasNoTrans,CblasNoTrans,1.0, H_diag, s_dyn->helper_functions->E_default,0.0,Gk);

    /*Find maxima of Gk.Dextremes*/
    //TODO: if Gk non zero else...
    gsl_matrix * maxima = gsl_matrix_alloc(Gk->size1, s_dyn->helper_functions->D_vertices->size2);
    //Calculate Gk.Dextremes (extremum of each dimension of each polytope)
    gsl_blas_dgemm(CblasNoTrans, CblasNoTrans, 1.0, Gk, s_dyn->helper_functions->D_vertices,0.0, maxima);
    gsl_vector *D_hat = gsl_vector_alloc(sum_polytope_dim);
    //find the maximum for each dimension of each polytope
    for(size_t i = 0; i < sum_polytope_dim; i++){
        gsl_vector_view max_row = gsl_matrix_row(maxima, i);
        gsl_vector_set(D_hat, i, gsl_vector_max(&max_row.vector));
    }
    //Update M such that it includes the uncertainty of noise
    gsl_vector_sub(&Mk.vector, D_hat);

    //Clean up!
    gsl_matrix_free(Gk);
    gsl_matrix_free(H_diag);
    gsl_matrix_free(maxima);
    gsl_vector_free(D_hat);

};

void search_better_path(gsl_matrix *low_u, current_state *now, system_dynamics *s_dyn, polytope *P1, polytope *P3, int ord , int closed_loop, size_t time_horizon, cost_function * f_cost, double *low_cost){
////////////////////////////////////////////////////////////////////////////////
//    Calculate the sequence u_seq such that:
//
//    - x(t+1) = A x(t) + B u(t) + K
//    - x(k) \in P1 for k = 0,...N
//    - x(N) \in P3
//    - [u(k); x(k)] \in PU
//
//    and minimize:
//    |Rx|_{ord} + |Qu|_{ord} + r'x + mid_weight * |xc - x(N)|_{ord}
////////////////////////////////////////////////////////////////////////////////

    //Helper variables
    size_t N = time_horizon;
    size_t n = s_dyn->A->size2;
    size_t m = s_dyn->B->size2;


    //Build list of polytopes that the state is going to be in in the next N time steps
    polytope **polytope_list = malloc(sizeof(polytope)*(N+1));
    polytope_list[0] = polytope_alloc(P1->H->size1,P1->H->size2);
    gsl_matrix_memcpy(polytope_list[0]->H, P1->H);
    gsl_vector_memcpy(polytope_list[0]->G, P1->G);
    if (closed_loop == 1) {
        polytope_list[N] = polytope_alloc(P3->H->size1,P3->H->size2);
        gsl_matrix_memcpy(polytope_list[N]->H, P3->H);
        gsl_vector_memcpy(polytope_list[N]->G, P3->G);
        //check partition system is in after i time steps
        for (size_t i = N; i > 1; i--){
            //TODO: check if target polytope full dim
            polytope_list[i-1] = polytope_alloc((P1->H->size1+polytope_list[i]->H->size1+s_dyn->U_set->H->size1), n);
            solve_feasible_closed_loop(polytope_list[i-1], P1, polytope_list[i], s_dyn);
        }
    }else {
        for (int i = 1; i < N; i++) {
            polytope_list[i] = polytope_alloc(P1->H->size1,P1->H->size2);
            gsl_matrix_memcpy(polytope_list[i]->H, P1->H);
            gsl_vector_memcpy(polytope_list[i]->G, P1->G);
        }
        polytope_list[N] = polytope_alloc(P3->H->size1, P3->H->size2);
        gsl_matrix_memcpy(polytope_list[N]->H, P3->H);
        gsl_vector_memcpy(polytope_list[N]->G, P3->G);
    }

    size_t sum_polytope_sizes = 0;
    for(int i = 0; i<N+1; i++){
        sum_polytope_sizes += polytope_list[i]->H->size1;
    }
    gsl_matrix *L_full = gsl_matrix_alloc(sum_polytope_sizes+N*(s_dyn->U_set->H->size1), n+N*m);
    gsl_vector *M_full = gsl_vector_alloc(sum_polytope_sizes+N*(s_dyn->U_set->H->size1));
    gsl_matrix_set_zero(L_full);
    gsl_vector_set_zero(M_full);
    set_path_constraints(L_full, M_full, s_dyn, polytope_list, N);

    for(int i = 0; i< N+1; i++){
        polytope_free(polytope_list[i]);
    }
    free(polytope_list);
    // Remove first constraints on x(0) they are obviously already satisfied
    // L_x = L[{(polytope[0]+1),(dim_n(L))},{1,n}]
    gsl_matrix_view L_x = gsl_matrix_submatrix(L_full, P1->H->size1, 0, (L_full->size1)-(P1->H->size1), n);
    // L_u = L[{(polytope[0]+1),(dim_n(L))},{(n+1),(dim_m(L))}]
    gsl_matrix_view L_u = gsl_matrix_submatrix(L_full, P1->H->size1, n, (L_full->size1)-(P1->H->size1), L_full->size2 - n);
    // M_view = M[{(polytope[0]+1),(dim_n(M))}]
    gsl_vector_view M_view = gsl_vector_subvector(M_full, P1->H->size1, M_full->size-P1->H->size1);

    //M = M-(L_x.x)
    gsl_vector * L_x_dot_X0 = gsl_vector_alloc((L_full->size1)-(P1->H->size1));
    gsl_blas_dgemv(CblasNoTrans, 1.0, &L_x.matrix, now->x, 0.0, L_x_dot_X0);
    gsl_vector_sub(&M_view.vector, L_x_dot_X0);
    //Clean up!
    gsl_vector_free(L_x_dot_X0);


    if (ord == 2){

        /*Calculate P and q */
        //P = Q2 + Ct^T.R2.Ct
        //q = {([x^T.A_N^T + (A_K.K_hat)^T].[R2.Ct])+(0.5*r^T.Ct)}^T

        // symmetrize
        gsl_matrix * Q2 = gsl_matrix_alloc(N*m, N*m);
        gsl_blas_dgemm(CblasTrans, CblasNoTrans, 1.0, f_cost->Q,f_cost->Q, 0.0, Q2);
        gsl_matrix * R2 = gsl_matrix_alloc(N*n, N*n);
        gsl_blas_dgemm(CblasTrans, CblasNoTrans, 1.0, f_cost->R,f_cost->R, 0.0, R2);


        //Calculate P
        gsl_matrix * P = gsl_matrix_alloc(N*m, N*m);
        gsl_matrix * R2_dot_Ct = gsl_matrix_alloc(N*n, N*m);
        gsl_matrix_set_zero(R2_dot_Ct);
        gsl_blas_dgemm(CblasNoTrans, CblasNoTrans, 1.0, R2, s_dyn->helper_functions->Ct, 0.0, R2_dot_Ct);
        gsl_blas_dgemm(CblasTrans, CblasNoTrans, 1.0, s_dyn->helper_functions->Ct, R2_dot_Ct, 0.0, P);
        gsl_matrix_add(P, Q2);

        //Clean up!
        gsl_matrix_free(R2);
        gsl_matrix_free(Q2);

        //Calculate q
        gsl_vector * q = gsl_vector_alloc(N*m);
        gsl_vector_set_zero(q);
        gsl_vector * A_N_dot_x = gsl_vector_alloc(N*n);
        gsl_vector_set_zero(A_N_dot_x);
        gsl_blas_dgemv(CblasNoTrans, 1.0, s_dyn->helper_functions->A_N_2, now->x, 0.0, A_N_dot_x);
        gsl_vector * A_K_dot_K_hat = gsl_vector_alloc(N*n);
        gsl_vector_set_zero(A_K_dot_K_hat);
        gsl_blas_dgemv(CblasNoTrans, 1.0, s_dyn->helper_functions->A_K_2, s_dyn->helper_functions->K_hat, 0.0, A_K_dot_K_hat);

        //[x^T.A_N^T + (A_K.K_hat)^T]^T
        gsl_vector_add(A_N_dot_x, A_K_dot_K_hat);

        //{([x^T.A_N^T + (A_K.K_hat)^T].[R2.Ct])}^T
        //R2_dot_Ct was calculated earlier
        gsl_blas_dgemv(CblasTrans, 1.0, R2_dot_Ct, A_N_dot_x, 0.0, q);

        //(0.5*r^T.Ct)
        gsl_vector *Right_side = gsl_vector_alloc(N*m);
        gsl_blas_dgemv(CblasTrans, 0.5, s_dyn->helper_functions->Ct, f_cost->r, 0.0, Right_side);
        gsl_vector_add(q, Right_side);

        //Clean up!
        gsl_matrix_free(R2_dot_Ct);
        gsl_vector_free(A_N_dot_x);
        gsl_vector_free(A_K_dot_K_hat);
        gsl_vector_free(Right_side);


        /*CVXOPT solve quadratic problem*/

        Py_Initialize();

        //Check if CVXOPT is installed
        if (import_cvxopt() < 0) {
            fprintf(stderr, "error importing cvxopt");
            exit(EXIT_FAILURE);
        }

        //Import cvxopt.solvers
        PyObject *solvers = PyImport_ImportModule("cvxopt.solvers");
        if (!solvers) {
            fprintf(stderr, "error importing cvxopt.solvers");
            exit(EXIT_FAILURE);
        }

        //Get reference to solvers.qp
        PyObject *qp = PyObject_GetAttrString(solvers, "qp");
        if (!qp) {
            fprintf(stderr, "error referencing cvxopt.solvers.qp");
            Py_DECREF(solvers);
            exit(EXIT_FAILURE);
        }

        //Transform P to CVXOPT compatible matrix: P =>P_cvx
        PyObject *P_cvx = (PyObject *)Matrix_New(N*m, N*m, DOUBLE);
        for(size_t l = 0; l< N*m; l++){
            for(size_t k = 0; k < N*m; k++){
                MAT_BUFD(P_cvx)[l+k*(N*m)] = gsl_matrix_get(P,l,k);
            }
        }
        gsl_matrix_free(P);

        //Transform q to CVXOPT compatible vector: q => q_cvx
        PyObject *q_cvx = (PyObject *)Matrix_New(N*m,1 , DOUBLE);
        for(size_t k = 0; k< (N*m); k++){
            MAT_BUFD(q_cvx)[k] = gsl_vector_get(q, k);
        }
        gsl_vector_free(q);

        //Transform L_u to CVXOPT compatible matrix: L_u => L_u_cvx
        PyObject *L_u_cvx = (PyObject *)Matrix_New(L_u.matrix.size1 ,L_u.matrix.size2, DOUBLE);
        for(size_t l = 0; l< L_u.matrix.size1; l++){
            for(size_t k = 0; k < L_u.matrix.size2; k++){
                MAT_BUFD(L_u_cvx)[k+l*(L_u.matrix.size2)] = gsl_matrix_get(&L_u.matrix,l,k);
            }
        }

        PyObject *M_view_cvx = (PyObject *)Matrix_New(M_view.vector.size, 1, DOUBLE);
        for(size_t k = 0; k< M_view.vector.size; k++){
            MAT_BUFD(M_view_cvx)[k] = gsl_vector_get(&M_view.vector,k);
        }
        /* pack matrices into an argument tuple*/
        PyObject *pArgs = PyTuple_New(4);
        PyTuple_SetItem(pArgs, 0, P_cvx);
        PyTuple_SetItem(pArgs, 1, q_cvx);
        PyTuple_SetItem(pArgs, 2, L_u_cvx);
        PyTuple_SetItem(pArgs, 3, M_view_cvx);

        PyObject *solution = PyObject_CallObject(qp, pArgs);
        if (!solution) {
            PyErr_Print();
            Py_DECREF(solvers);
            Py_DECREF(qp);
            Py_DECREF(pArgs);
            exit(EXIT_FAILURE);
        }
        /*PyObject *status = PyDict_GetItemString(solution, "status");
        if (*status != "optimal"){
            fprintf(stderr, "getInputHelper: QP solver finished with status %s", solution.status);
            exit(EXIT_FAILURE);
        }*/

        //Get value from Python Dictionary
        PyObject *primal_objective = PyDict_GetItemString(solution, "primal objective");
        double cost = PyFloat_AS_DOUBLE(primal_objective);

        //ONLY interested if cost is lower than current optimal path!
        if(cost < *low_cost){
            PyObject *x_cvx = PyDict_GetItemString(solution, "x");
            // Transform x_cvx to GSL compatible matrix: x_cvx => low_u
            for(size_t i = 0; i<n; i++){
                for(size_t j = 0; j<N; j++){
                    gsl_matrix_set(low_u,i, j,MAT_BUFD(x_cvx)[j+(i*N)]);
                }
            }
            *low_cost = cost;
            //Clean up!
            Py_DECREF(x_cvx);

        }

        //Clean up!
        Py_DECREF(solvers);
        Py_DECREF(qp);
        Py_DECREF(pArgs);
        Py_DECREF(solution);
        Py_DECREF(primal_objective);

        Py_Finalize();

        gsl_matrix_free(L_full);
        gsl_vector_free(M_full);
    }

    //TODO: Once more than norm2 is needed
    /* else if( ord == 1){
     *
     * } else {
     *  //ord == INFINITY
     *
     * }
     * lp_solved_solution sol = pc.polytope.lpsolve(c_LP.flatten(), G_LP, h_LP);
     *
     * if (sol.status != 0){
     *     fprintf(stderr, "getInputHelper: LP solver finished with message %s", sol.message);
     *     exit(EXIT_FAILURE);
     * }
     * var = np.array(sol['x']).flatten();
     * u = var[-N * m:];
     * path.input = u.reshape(N, m);
     * path.cost = sol['fun'];
     * return path;
     * */
};

void get_input (gsl_matrix * low_u, current_state * now, discrete_dynamics * d_dyn, system_dynamics * s_dyn, int target_cell, cost_function * f_cost) {
////////////////////////////////////////////////////////////////////////////////
//    Compute continuous control input for discrete transition.
//
//    Computes a continuous control input sequence which takes the plant:
//
//    - from state C{start}
//    - to state C{end}
//
//    These are states of the partition C{abstraction}.
//    The computed control input is such that::
//
//    f(x, u) = |Rx|_{ord} + |Qu|_{ord} + r'x + distance_error_weight * |xc - x(N)|_{ord}
//
//    be minimal.
//
//    C{xc} is the chebyshev center of the final cell.
//    If no cost parameters are given, then the defaults are:
//
//          - Q = I
//          - distance_error_weight = 3
//
//==================================================================================
//    Notes
//    =====
//    1. The same horizon length as in reachability analysis
//    should be used in order to guarantee feasibility.
//
//    2. If the closed loop algorithm has been used
//    to compute reachability the input needs to be
//    recalculated for each time step
//    (with decreasing horizon length).
//
//    In this case only u(0) should be used as
//    a control signal and u(1) ... u(N-1) discarded.
//
//    3. The "conservative" calculation makes sure that
//    the plant remains inside the convex hull of the
//    starting region during execution, i.e.::
//
//    x(1), x(2) ...  x(N-1) are \in conv_hull(starting region).
//
//    If the original proposition preserving partition
//    is not convex, then safety cannot be guaranteed.
//
//    @param x0: initial continuous state
//    @type x0: numpy 1darray
//
//    @param ssys: system dynamics
//    @type ssys: L{LtiSysDyn}
//
//    @param abstraction: abstract system dynamics
//    @type abstraction: L{AbstractPwa}
//
//    @param start: index of the initial state in C{abstraction.ts}
//    @type start: int >= 0
//
//    @param end: index of the end state in C{abstraction.ts}
//    @type end: int >= 0
//
//    @param R: state cost matrix for::
//    x = [x(1)' x(2)' .. x(N)']'
//    If empty, zero matrix is used.
//    @type R: size (N*xdim x N*xdim)
//
//    @param r: cost vector for state trajectory:
//    x = [x(1)' x(2)' .. x(N)']'
//    @type r: size (N*xdim x 1)
//
//    @param Q: input cost matrix for control input::
//            u = [u(0)' u(1)' .. u(N-1)']'
//    If empty, identity matrix is used.
//    @type Q: size (N*udim x N*udim)
//
//    @param distance_error_weight: cost weight for |x(N)-xc|_{ord}
//
//    @param ord: norm used for cost function::
//            f(x, u) = |Rx|_{ord} + |Qu|_{ord} + r'x + distance_error_weight *|xc - x(N)|_{ord}
//    @type ord: ord \in {1, 2, np.inf}
//
//    @return: array A where row k contains the control input: u(k)
//    for k = 0, 1 ... N-1
//    @rtype: (N x m) numpy 2darray
////////////////////////////////////////////////////////////////////////////////

    //TODO Initialize all matrices in python
    //TODO: program solve_feasible

    /*Initialize*/

    //Set input back to zero (safety precaution)
    gsl_matrix_set_zero(low_u);


    //Help variables:
    size_t n = now->x->size;
    size_t N = d_dyn->time_horizon;

    double low_cost = INFINITY;
    double err_weight = f_cost->distance_error_weight;

    //Set start region (depends on conservative path or not)
    polytope *P1;

    int start = now->current_cell;

    if (d_dyn->conservative == 1){
        // Take convex hull or polytope as starting polytope P1

        region_of_polytopes *start_region = d_dyn->regions[start];
        // if hull_of_region != NULL => hull was computed => several polytopes in that region
        if (start_region->hull_of_region->H != NULL){
            P1 = start_region->hull_of_region;
        } else{
            P1 = start_region->polytopes[0];
        }
    } else{
        // Take original proposition preserving cell as constraint
        // must be single polytope (ensuring convex)

        if (d_dyn->original_regions[start]->number_of_polytopes == 1){
            P1 = d_dyn->original_regions[start]->polytopes[0];
        } else {
            fprintf(stderr, "In Region of polytopes(%d): `conservative = False` arg requires that original regions be convex", now->current_cell);
            exit(EXIT_FAILURE);
        }
    }


    //Find optimal path into target region
    //by finding polytope that is easiest to reach in target region

    // for each polytope in target region
    for (int i = 0; i < d_dyn->regions[target_cell]->number_of_polytopes; i++){
        polytope *P3 = d_dyn->regions[target_cell]->polytopes[i];

        //Finding a path to target region
        if (err_weight > 0){
            //Set r (=xc.R)(from default to polytope specific):
            double *xc = P3->chebyshev_center;

            //r[n*(N-1), n*N] += err_weight * xc;
            for (size_t j = n * (N - 1); j < n*N; j++){
                double * element_value = gsl_vector_ptr(f_cost->r, j);
                * element_value += err_weight * xc[i];
                gsl_vector_set(f_cost->r, j, *element_value);
            }

            search_better_path(low_u, now,s_dyn, P1, P3,d_dyn->ord, d_dyn->closed_loop, N, f_cost, &low_cost);
            //Reset r vector to default values
            for (size_t j = n * (N - 1); j < n*N; j++){
                double * element_value = gsl_vector_ptr(f_cost->r, j);
                * element_value -= err_weight * xc[i];
                gsl_vector_set(f_cost->r, j, * element_value);
            }

        } else{
            search_better_path(low_u, now,s_dyn, P1, P3,d_dyn->ord, d_dyn->closed_loop, N, f_cost, &low_cost);
        }
    }

    if (low_cost == INFINITY){
        //raise Exception
        fprintf(stderr, "get_input: Did not find any trajectory");
        exit(EXIT_FAILURE);
    }

}