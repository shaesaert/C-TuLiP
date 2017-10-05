//
// Created by L.Jonathan Feldstein
//

#include <gsl/gsl_vector_double.h>
#include "cimple_controller.h"


/**
 * Action to get plant from current cell to target cell.
 */
void ACT(int target, current_state * now, discrete_dynamics * d_dyn, system_dynamics * s_dyn, cost_function * f_cost){
    printf("Computing control sequence to go from cell %d to cell %d...", (*now).current_cell, target);
    fflush(stdout);

    gsl_matrix * u = gsl_matrix_alloc(now->x->size, d_dyn->time_horizon);
    get_input(u, now, d_dyn, s_dyn, target, f_cost);
    printf("Applying it...");
    fflush(stdout);
    apply_control(now->x, u, s_dyn->A, s_dyn->B);
    printf("New state:");
    gsl_vector_print(now->x, "now->");
    fflush(stdout);
    // Clean up!
    gsl_matrix_free(u);
}

/**
 * Apply the calculated control to the current state using system dynamics
 */
void apply_control(gsl_vector *x, gsl_matrix *u, gsl_matrix *A, gsl_matrix *B) {
    printf("apply_control: begin at");
    gsl_vector_print(x, "x[0]");
    fflush(stdout);
    gsl_vector *x_temp = gsl_vector_alloc(x->size);
    //Apply input to state of next N time steps
    // x[k+1] = A.x[k] + B.u[k+1]
    int time = 0;
    for (size_t k = 0; k < (u->size2); k++){
        gsl_vector_set_zero(x_temp);
        printf("apply_control: u[%d] = ", time);
        gsl_vector_view u_view = gsl_matrix_column(u, k);
        gsl_vector_print(&u_view.vector,"u[]");
        fflush(stdout);
        gsl_vector *Btu = gsl_vector_alloc(x->size);
        gsl_vector_view u_col = gsl_matrix_column(u,k);

        //A.x[k-1]
        gsl_blas_dgemv(CblasNoTrans, 1, A, x, 0, x_temp);
        //B.u[k]
        gsl_blas_dgemv(CblasNoTrans, 1, B, &u_col.vector, 0 , Btu);
        //update x[k-1] => x[k]
        gsl_vector_set_zero(x);
        gsl_vector_add(x, x_temp);
        gsl_vector_add(x, Btu);
        printf("Temporary state: x[%d] = ", time+1);
        gsl_vector_print(x,"x[]");
        fflush(stdout);
        gsl_vector_free(Btu);
    }
};

/**
 * Calculate recursively polytope (return_polytope) system needs to be in, to reach P2 in one time step
 */
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
        gsl_matrix * maxima = gsl_matrix_alloc(Dist->size1, s_dyn->aux_matrices->D_one_step->size2);
        //Calculate Dist.Dextremes (extremum of each dimension of each polytope)
        gsl_blas_dgemm(CblasNoTrans, CblasNoTrans, 1.0, Dist, s_dyn->aux_matrices->D_one_step,0.0, maxima);
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

    polytope_reduce(precedent_polytope);

    // Project precedent polytope onto lower dim
    polytope_project(precedent_polytope, n);

    polytope_reduce(precedent_polytope);

    gsl_matrix_view precedent_view = gsl_matrix_submatrix(precedent_polytope->H,0,0,precedent_polytope->H->size1, n);

    gsl_matrix_memcpy(return_polytope->H,&precedent_view.matrix);
    gsl_vector_memcpy(return_polytope->G,precedent_polytope->G);
    polytope_free(precedent_polytope);
};

/**
 * Compute a polytope that constraints the system over the next N time steps to fullfill the GR(1) specifications
 */
void set_path_constraints(gsl_matrix *L_full,gsl_vector *M_full, system_dynamics * s_dyn, polytope *list_polytopes[], size_t N){
    //Disturbance assumed at every step
    //Also ... TODO: NO DEFAULT IF E NOT FULL DIMENSION OF s_dyn.Wset >> Will lead to problems when multiplying Gk.D

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
    gsl_blas_dgemm(CblasNoTrans,CblasNoTrans,1.0, H_diag, s_dyn->aux_matrices->L_default,0.0,&Lk.matrix);

    // Gk = H_diag.E_default
    gsl_blas_dgemm(CblasNoTrans,CblasNoTrans,1.0, H_diag, s_dyn->aux_matrices->E_default,0.0,Gk);

    /*Find maxima of Gk.Dextremes*/
    //TODO: if Gk non zero else...
    gsl_matrix * maxima = gsl_matrix_alloc(Gk->size1, s_dyn->aux_matrices->D_vertices->size2);
    //Calculate Gk.Dextremes (extremum of each dimension of each polytope)
    gsl_blas_dgemm(CblasNoTrans, CblasNoTrans, 1.0, Gk, s_dyn->aux_matrices->D_vertices,0.0, maxima);
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

/**
 * Calculates (optimal) input to reach desired state (P3) from current state (now) through convex optimization
 */
void search_better_path(gsl_matrix *low_u, current_state *now, system_dynamics *s_dyn, polytope *P1, polytope *P3, int ord , int closed_loop, size_t time_horizon, cost_function * f_cost, double *low_cost){

    //Auxiliary variables
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
        gsl_blas_dgemm(CblasNoTrans, CblasNoTrans, 1.0, R2, s_dyn->aux_matrices->Ct, 0.0, R2_dot_Ct);
        gsl_blas_dgemm(CblasTrans, CblasNoTrans, 1.0, s_dyn->aux_matrices->Ct, R2_dot_Ct, 0.0, P);
        gsl_matrix_add(P, Q2);

        //Clean up!
        gsl_matrix_free(R2);
        gsl_matrix_free(Q2);

        //Calculate q
        gsl_vector * q = gsl_vector_alloc(N*m);
        gsl_vector_set_zero(q);
        gsl_vector * A_N_dot_x = gsl_vector_alloc(N*n);
        gsl_vector_set_zero(A_N_dot_x);
        gsl_blas_dgemv(CblasNoTrans, 1.0, s_dyn->aux_matrices->A_N, now->x, 0.0, A_N_dot_x);
        gsl_vector * A_K_dot_K_hat = gsl_vector_alloc(N*n);
        gsl_vector_set_zero(A_K_dot_K_hat);
        gsl_blas_dgemv(CblasNoTrans, 1.0, s_dyn->aux_matrices->A_K, s_dyn->aux_matrices->K_hat, 0.0, A_K_dot_K_hat);

        //[x^T.A_N^T + (A_K.K_hat)^T]^T
        gsl_vector_add(A_N_dot_x, A_K_dot_K_hat);

        //{([x^T.A_N^T + (A_K.K_hat)^T].[R2.Ct])}^T
        //R2_dot_Ct was calculated earlier
        gsl_blas_dgemv(CblasTrans, 1.0, R2_dot_Ct, A_N_dot_x, 0.0, q);

        //(0.5*r^T.Ct)
        gsl_vector *Right_side = gsl_vector_alloc(N*m);
        gsl_blas_dgemv(CblasTrans, 0.5, s_dyn->aux_matrices->Ct, f_cost->r, 0.0, Right_side);
        gsl_vector_add(q, Right_side);

        //Clean up!
        gsl_matrix_free(R2_dot_Ct);
        gsl_vector_free(A_N_dot_x);
        gsl_vector_free(A_K_dot_K_hat);
        gsl_vector_free(Right_side);


        /*CVXOPT solve quadratic problem*/

        gsl_matrix_print(P, "P");
        gsl_vector_print(q, "q");
        gsl_matrix_print(&L_u.matrix, "L_u");
        gsl_vector_print(&M_view.vector, "M_view");
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
        printf("Cost: %.3f", cost);
        //ONLY interested if cost is lower than current optimal path!
        if(cost < *low_cost){
            printf(">> Better solution x: found");
            PyObject *x_cvx = PyDict_GetItemString(solution, "x");
            // Transform x_cvx to GSL compatible matrix: x_cvx => low_u
            for(size_t i = 0; i<n; i++){
                for(size_t j = 0; j<N; j++){
                    gsl_matrix_set(low_u,i, j,MAT_BUFD(x_cvx)[j+(i*N)]);
                }
            }
            gsl_matrix_print(low_u, "u");
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

/**
 * Calculate (optimal) input that will be applied to take plant from current state (now) to target_cell.
 */
void get_input (gsl_matrix * low_u, current_state * now, discrete_dynamics * d_dyn, system_dynamics * s_dyn, int target_cell, cost_function * f_cost) {

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