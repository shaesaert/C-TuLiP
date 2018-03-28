//
// Created by jonathan on 1/5/18.
//

#include <gsl/gsl_matrix.h>
#include <gsl/gsl_vector_double.h>
#include "cimple_mpc_computation.h"

/**
 * Set up weight matrices for the quadratic problem
 */
polytope * set_cost_function(gsl_matrix *P,
                             gsl_vector *q,
                             gsl_matrix *L,
                             gsl_vector *M,
                             current_state *now,
                             system_dynamics *s_dyn,
                             cost_function *f_cost,
                             size_t time_horizon){

    size_t N = time_horizon;
    size_t n = s_dyn->A->size1;
    size_t m = s_dyn->B->size2;


    /*Calculate P and q */
    //           |B     0     0     0   0|
    //           |AB    B     0     0   0|
    //      Ct = |A^2B  AB    B     0   0|
    //           |A^3B  A^2B  AB    B   0|
    //           |A^4B  A^3B  A^2B  AB  B|

    //            |I    0    0    0  0|
    //            |A    I    0    0  0|
    //      A_K = |A^2  A    I    0  0|
    //            |A^3  A^2  A    I  0|
    //            |A^4  A^3  A^2  A  I|

    //            |A  |
    //            |A^2|
    //      A_N = |A^3|
    //            |A^4|
    //            |A^5|

    //P = Q2 + Ct^T.R2.Ct
    //q = {([x^T.A_N^T + (A_K.K_hat)^T].[R2.Ct])+(0.5*r^T.Ct)}^T

    // symmetrize
    gsl_matrix * Q2 = gsl_matrix_alloc(N*m, N*m);
    gsl_matrix_view Q_view = gsl_matrix_submatrix(f_cost->Q,(f_cost->Q->size1-N),(f_cost->Q->size2-N),(N),(N));
    gsl_blas_dgemm(CblasTrans, CblasNoTrans, 1.0, &Q_view.matrix,&Q_view.matrix, 0.0, Q2);
    gsl_matrix * R2 = gsl_matrix_alloc(N*n, N*n);
    gsl_matrix_view R_view = gsl_matrix_submatrix(f_cost->R,(f_cost->R->size1-N),(f_cost->R->size2-N),(N),(N));
    gsl_blas_dgemm(CblasTrans, CblasNoTrans, 1.0, &R_view.matrix,&R_view.matrix, 0.0, R2);


    //Calculate P
    gsl_matrix * R2_dot_Ct = gsl_matrix_alloc(N*n, N*m);
    gsl_matrix_set_zero(R2_dot_Ct);
    gsl_matrix_view Ct_view = gsl_matrix_submatrix(s_dyn->aux_matrices->Ct,0,0,N,N);
    gsl_blas_dgemm(CblasNoTrans, CblasNoTrans, 1.0, R2, &Ct_view.matrix, 0.0, R2_dot_Ct);
    gsl_blas_dgemm(CblasTrans, CblasNoTrans, 1.0, &Ct_view.matrix, R2_dot_Ct, 0.0, P);
    gsl_matrix_add(P, Q2);

    //Clean up!
    gsl_matrix_free(R2);
    gsl_matrix_free(Q2);

    //Calculate q
    gsl_vector_set_zero(q);
    gsl_vector * A_N_dot_x = gsl_vector_alloc(N*n);
    gsl_vector_set_zero(A_N_dot_x);
    gsl_matrix_view A_N_view = gsl_matrix_submatrix(s_dyn->aux_matrices->A_N,0,0,N,1);
    gsl_blas_dgemv(CblasNoTrans, 1.0, &A_N_view.matrix, now->x, 0.0, A_N_dot_x);
    gsl_vector * A_K_dot_K_hat = gsl_vector_alloc(N*n);
    gsl_vector_set_zero(A_K_dot_K_hat);
    gsl_matrix_view A_K_view = gsl_matrix_submatrix(s_dyn->aux_matrices->A_K,0,0,N,N);
    gsl_vector_view K_hat_view = gsl_vector_subvector(s_dyn->aux_matrices->K_hat,0,N);
    gsl_blas_dgemv(CblasNoTrans, 1.0, &A_K_view.matrix, &K_hat_view.vector, 0.0, A_K_dot_K_hat);

    //[x^T.A_N^T + (A_K.K_hat)^T]^T
    gsl_vector_add(A_N_dot_x, A_K_dot_K_hat);

    //{([x^T.A_N^T + (A_K.K_hat)^T].[R2.Ct])}^T
    //R2_dot_Ct was calculated earlier
    gsl_blas_dgemv(CblasTrans, 1.0, R2_dot_Ct, A_N_dot_x, 0.0, q);

    //(0.5*r^T.Ct)
    gsl_vector *Right_side = gsl_vector_alloc(N*m);
    gsl_vector_view r_view = gsl_vector_subvector(f_cost->r,(f_cost->r->size-N),N);
    gsl_blas_dgemv(CblasTrans, 0.5, &Ct_view.matrix, &r_view.vector, 0.0, Right_side);
    gsl_vector_add(q, Right_side);

    //Clean up!
    gsl_matrix_free(R2_dot_Ct);
    gsl_vector_free(A_N_dot_x);
    gsl_vector_free(A_K_dot_K_hat);
    gsl_vector_free(Right_side);


    /*GUROBI Convex Optimization: solve quadratic problem*/

    //Minimizing
    polytope * constraints_polytope = polytope_alloc(L->size1, L->size2);
    gsl_matrix_memcpy(constraints_polytope->H,L);
    gsl_vector_memcpy(constraints_polytope->G,M);

    //back to gsl polytope
    polytope *opt_constraints = polytope_minimize(constraints_polytope);
    polytope_free(constraints_polytope);

//    //Minimizing
//    polytope * constraints_polytope = polytope_alloc(L->size1, L->size2);
//    gsl_matrix_memcpy(constraints_polytope->H,L);
//    gsl_vector_memcpy(constraints_polytope->G,M);
//
//    printf("\n\n\n\nHALT\n\n\n\n\n");
//    gsl_matrix_print(constraints_polytope->H,"H");
//    gsl_vector_print(constraints_polytope->G,"G");
//
//    polytope *opt_constraints = polytope_minimize(constraints_polytope);
//    polytope_free(constraints_polytope);
//
//
//    printf("\n\n\n\nNOOOOO\n\n\n\n\n");
//    gsl_matrix_print(opt_constraints->H,"H");
//    gsl_vector_print(opt_constraints->G,"G");
//
//        polytope *opt_constraints = polytope_alloc(10,N);
//        gsl_vector_set(opt_constraints->G,0,1);
//        gsl_vector_set(opt_constraints->G,1,-1);
//        gsl_vector_set(opt_constraints->G,2,1);
//        gsl_vector_set(opt_constraints->G,3,-1);
//        gsl_vector_set(opt_constraints->G,4,1);
//        gsl_vector_set(opt_constraints->G,5,-1);
//        gsl_vector_set(opt_constraints->G,6,1);
//        gsl_vector_set(opt_constraints->G,7,-1);
//        gsl_vector_set(opt_constraints->G,8,1);
//        gsl_vector_set(opt_constraints->G,9,-1);
//        gsl_matrix_set(opt_constraints->H,0,0,0.2);
//        gsl_matrix_set(opt_constraints->H,0,1,0);
//        gsl_matrix_set(opt_constraints->H,0,2,0);
//        gsl_matrix_set(opt_constraints->H,0,3,0);
//        gsl_matrix_set(opt_constraints->H,0,4,0);
//
//        gsl_matrix_set(opt_constraints->H,1,0,-20);
//        gsl_matrix_set(opt_constraints->H,1,1,0);
//        gsl_matrix_set(opt_constraints->H,1,2,0);
//        gsl_matrix_set(opt_constraints->H,1,3,0);
//        gsl_matrix_set(opt_constraints->H,1,4,0);
//        gsl_matrix_set(opt_constraints->H,2,0,0.2);
//        gsl_matrix_set(opt_constraints->H,2,1,0.2);
//        gsl_matrix_set(opt_constraints->H,2,2,0);
//        gsl_matrix_set(opt_constraints->H,2,3,0);
//        gsl_matrix_set(opt_constraints->H,2,4,0);
//
//        gsl_matrix_set(opt_constraints->H,3,0,-20);
//        gsl_matrix_set(opt_constraints->H,3,1,-20);
//        gsl_matrix_set(opt_constraints->H,3,2,0);
//        gsl_matrix_set(opt_constraints->H,3,3,0);
//        gsl_matrix_set(opt_constraints->H,3,4,0);
//        gsl_matrix_set(opt_constraints->H,4,0,0.2);
//        gsl_matrix_set(opt_constraints->H,4,1,0.2);
//        gsl_matrix_set(opt_constraints->H,4,2,0.2);
//        gsl_matrix_set(opt_constraints->H,4,3,0);
//        gsl_matrix_set(opt_constraints->H,4,4,0);
//
//        gsl_matrix_set(opt_constraints->H,5,0,-20);
//        gsl_matrix_set(opt_constraints->H,5,1,-20);
//        gsl_matrix_set(opt_constraints->H,5,2,-20);
//        gsl_matrix_set(opt_constraints->H,5,3,0);
//        gsl_matrix_set(opt_constraints->H,5,4,0);
//        gsl_matrix_set(opt_constraints->H,6,0,0.2);
//        gsl_matrix_set(opt_constraints->H,6,1,0.2);
//        gsl_matrix_set(opt_constraints->H,6,2,0.2);
//        gsl_matrix_set(opt_constraints->H,6,3,0.2);
//        gsl_matrix_set(opt_constraints->H,6,4,0);
//
//        gsl_matrix_set(opt_constraints->H,7,0,-20);
//        gsl_matrix_set(opt_constraints->H,7,1,-20);
//        gsl_matrix_set(opt_constraints->H,7,2,-20);
//        gsl_matrix_set(opt_constraints->H,7,3,-20);
//        gsl_matrix_set(opt_constraints->H,7,4,0);
//        gsl_matrix_set(opt_constraints->H,8,0,0.2);
//        gsl_matrix_set(opt_constraints->H,8,1,0.2);
//        gsl_matrix_set(opt_constraints->H,8,2,0.2);
//        gsl_matrix_set(opt_constraints->H,8,3,0.2);
//        gsl_matrix_set(opt_constraints->H,8,4,0.2);
//
//        gsl_matrix_set(opt_constraints->H,9,0,-20);
//        gsl_matrix_set(opt_constraints->H,9,1,-20);
//        gsl_matrix_set(opt_constraints->H,9,2,-20);
//        gsl_matrix_set(opt_constraints->H,9,3,-20);
//        gsl_matrix_set(opt_constraints->H,9,4,-20);
    return opt_constraints;
}

/**
 * Set up GUROBI environment and solve qp
 */
void compute_optimal_control_qp(gsl_matrix *low_u,
                                double *low_cost,
                                gsl_matrix *P,
                                gsl_vector* q,
                                polytope *opt_constraints,
                                size_t time_horizon,
                                size_t n){


    //Initialization for qp in gurobi
    GRBenv   *env   = NULL;
    GRBmodel *model = NULL;
    int       error = 0;
    double    sol[time_horizon];
    int       optimstatus;
    double    cost;


    /* Create environment */

    error = GRBloadenv(&env, "qp.log");
    if (error) goto QUIT;

    /* Create an empty model */

    error = GRBnewmodel(env, &model, "qp", 0, NULL, NULL, NULL, NULL, NULL);
    if (error) goto QUIT;
    /* Add variables */

    error = GRBaddvars(model, (int)time_horizon, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
                       NULL);
    if (error) goto QUIT;

    /* Quadratic objective terms */

    error = gsl_matrix_to_qpterm_gurobi(P, model, time_horizon);
    if (error) goto QUIT;

    /* Linear objective term */

    error = gsl_vector_to_linterm_gurobi(q, model, time_horizon);
    if (error) goto QUIT;


    /* Add constraints*/

    error = polytope_to_constraints_gurobi(opt_constraints,model,time_horizon);
    if (error) goto QUIT;
    /* Optimize model */

    error = GRBoptimize(model);
    if (error) goto QUIT;

    /* Write model to 'qp.lp' */

    error = GRBwrite(model, "qp.lp");
    if (error) goto QUIT;

    /* Capture solution information */

    error = GRBgetintattr(model, GRB_INT_ATTR_STATUS, &optimstatus);
    if (error) goto QUIT;

    error = GRBgetdblattr(model, GRB_DBL_ATTR_OBJVAL, &cost);
    if (error) goto QUIT;

    error = GRBgetdblattrarray(model, GRB_DBL_ATTR_X, 0, (int)time_horizon, sol);
    if (error) goto QUIT;

    printf("\nOptimization complete\n");
    if (optimstatus == GRB_OPTIMAL) {
        printf("\nOptimal objective: %.4e\n", cost);

        for(size_t i=0;i<time_horizon;i++){
            printf("  u%d=%.4f", (int)i,sol[i]);

        }
        printf("\n");

    } else if (optimstatus == GRB_INF_OR_UNBD) {
        printf("\nModel is infeasible or unbounded\n");
    } else {
        printf("\nOptimization was stopped early\n");
    }

    if(cost < *low_cost){
        for(size_t i = 0; i<n; i++){
            for(size_t j = 0; j<time_horizon; j++){
                gsl_matrix_set(low_u,i, j,sol[j]);
            }
        }
        *low_cost = cost;
    }

    QUIT:

    /* Error reporting */

    if (error) {
        printf("ERROR: %s\n", GRBgeterrormsg(env));
        exit(1);
    }

    /* Free model */

    GRBfreemodel(model);

    /* Free environment */

    GRBfreeenv(env);
}

/**
 * Calculate (optimal) input that will be applied to take plant from current state (now) to target_cell.
 */
void get_input (gsl_matrix * low_u,
                current_state * now,
                discrete_dynamics * d_dyn,
                system_dynamics * s_dyn,
                int target_cell,
                cost_function * f_cost,
                size_t current_time_horizon,
                polytope **polytope_list_backup) {

    //Set input back to zero (safety precaution)
    gsl_matrix_set_zero(low_u);


    //Help variables:
    size_t n = now->x->size;
    size_t N = current_time_horizon;

    double low_cost = INFINITY;
    double err_weight = f_cost->distance_error_weight;

    //Set start region (depends on conservative path or not)
    polytope *P1;

    int start = now->current_cell;

    if (d_dyn->conservative == 1){
        // Take convex hull or polytope as starting polytope P1

        // if hull_of_region != NULL => hull was computed => several polytopes in that region
        if (d_dyn->regions[start]->hull_of_region->H != NULL){
            P1 = d_dyn->regions[start]->hull_of_region;
        } else{
            P1 = d_dyn->regions[start]->polytopes[0];
        }
    } else{
        // Take original proposition preserving cell as constraint
        // must be single polytope (ensuring convex)

        if (d_dyn->original_regions[start]->number_of_polytopes == 1){
            P1 = d_dyn->original_regions[start]->polytopes[0];
        } else {
            fprintf(stderr, "\nIn Region of polytopes(%d): `conservative = False` arg requires that original regions be convex\n", now->current_cell);
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

            search_better_path(low_u, now,s_dyn, P1, P3,d_dyn->ord, N, f_cost, &low_cost, polytope_list_backup, d_dyn->time_horizon);
            //Reset r vector to default values
            for (size_t j = n * (N - 1); j < n*N; j++){
                double * element_value = gsl_vector_ptr(f_cost->r, j);
                * element_value -= err_weight * xc[i];
                gsl_vector_set(f_cost->r, j, * element_value);
            }

        } else{
            search_better_path(low_u, now,s_dyn, P1, P3,d_dyn->ord, N, f_cost, &low_cost, polytope_list_backup, d_dyn->time_horizon);
        }
    }

    if (low_cost == INFINITY){
        //raise Exception
        fprintf(stderr, "\nget_input: Did not find any trajectory\n");
        exit(EXIT_FAILURE);
    }

};


/**
 * Calculates (optimal) input to reach desired state (P3) from current state (now) through convex optimization
 */
void search_better_path(gsl_matrix *low_u,
                        current_state *now,
                        system_dynamics *s_dyn,
                        polytope *P1,
                        polytope *P3,
                        int ord ,
                        size_t time_horizon,
                        cost_function * f_cost,
                        double *low_cost,
                        polytope **polytope_list_backup,
                        size_t total_time){

    //Auxiliary variables
    size_t N = time_horizon;
    size_t n = s_dyn->A->size2;
    size_t m = s_dyn->B->size2;


    //Build list of polytopes that the state is going to be in in the next N time steps
    polytope **polytope_list = malloc(sizeof(polytope)*(N+1));
    polytope_list[0] = polytope_alloc(P1->H->size1,P1->H->size2);
    gsl_matrix_memcpy(polytope_list[0]->H, P1->H);
    gsl_vector_memcpy(polytope_list[0]->G, P1->G);

    for (int i = 1; i < N; i++) {
        polytope_list[i] = polytope_alloc(P1->H->size1,P1->H->size2);
        gsl_matrix_memcpy(polytope_list[i]->H, P1->H);
        gsl_vector_memcpy(polytope_list[i]->G, P1->G);
    }
    polytope_list[N] = polytope_alloc(P3->H->size1, P3->H->size2);
    gsl_matrix_memcpy(polytope_list[N]->H, P3->H);
    gsl_vector_memcpy(polytope_list[N]->G, P3->G);

    size_t sum_polytope_sizes = 0;
    for(int i = 0; i<N+1; i++){
        sum_polytope_sizes += polytope_list[i]->H->size1;
    }
    gsl_matrix *L_full = gsl_matrix_alloc(sum_polytope_sizes+N*(s_dyn->U_set->H->size1), n+N*m);
    gsl_vector *M_full = gsl_vector_alloc(sum_polytope_sizes+N*(s_dyn->U_set->H->size1));
    gsl_matrix_set_zero(L_full);
    gsl_vector_set_zero(M_full);
    set_path_constraints(L_full, M_full, s_dyn, polytope_list, N);

    //Updating backup list of polytopes
    //If polytope list doesn't have to be initialized completely, old ones have first to be destroyed:
    if(N< total_time) {
        for (size_t i = total_time; i > total_time - N - 1; i--) {
            polytope_free(polytope_list_backup[i]);
        }
    }
    //List is updated (or created, if total_time == N)
    for(size_t i = total_time-N; i< total_time+1; i++){
        size_t k =i-(total_time-N);
        polytope_list_backup[i] = polytope_alloc(polytope_list[k]->H->size1,polytope_list[k]->H->size2);
        gsl_matrix_memcpy(polytope_list_backup[i]->H,polytope_list[k]->H);
        gsl_vector_memcpy(polytope_list_backup[i]->G,polytope_list[k]->G);
    }

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
        gsl_matrix * P = gsl_matrix_alloc(N*m, N*m);
        gsl_vector * q = gsl_vector_alloc(N*m);

        polytope *opt_constraints = set_cost_function(P, q, &L_u.matrix, &M_view.vector, now, s_dyn, f_cost, N);
        compute_optimal_control_qp(low_u, low_cost, P, q, opt_constraints, N, n);
        polytope_free(opt_constraints);
        gsl_vector_free(q);
        gsl_matrix_free(P);

    }
    gsl_matrix_free(L_full);
    gsl_vector_free(M_full);
};


/**
 * Compute a polytope that constraints the system over the next N time steps to fullfill the GR(1) specifications
 */
void set_path_constraints(gsl_matrix *L_full,
                          gsl_vector *M_full,
                          system_dynamics * s_dyn,
                          polytope **list_polytopes,
                          size_t N){
    //Disturbance assumed at every step and full dimension of s_dyn.Wset

    // Help variables
    size_t n = s_dyn->A->size2;  // State space dimension
    size_t p = s_dyn->E->size2;  // Disturbance space dimension
    size_t sum_polytope_dim = 0; // Sum of dimension n of all polytopes in the list
    for(size_t i = 0; i < N+1; i++){

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

    gsl_matrix *Gk = gsl_matrix_alloc(sum_polytope_dim, p*(N+1));

    /*
     *                          |0            0          0        0      0|
     *                          |H_1.E        0          0        0      0|
     *Gk =  H_diag.E_default  = |H_2.A.E    H_2.E        0        0      0| dim[sum_polytope_dim x p*N]
     *                          |H_3.A^2.E  H_3.A.E    H_3.E      0      0|
     *                          |H_4.A^3.E  H_4.A^3.E  H_4.A.E  H_4.E    0|
     * */
    gsl_matrix_set_zero(Gk);
    gsl_matrix *H_diag= gsl_matrix_alloc(sum_polytope_dim, n*(N+1));
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
    for(int i = 0; i<N+1; i++){

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
    gsl_matrix_view L_default_view = gsl_matrix_submatrix(s_dyn->aux_matrices->L_default,0,0,(N+1),(N+1));
    gsl_blas_dgemm(CblasNoTrans,CblasNoTrans,1.0, H_diag, &L_default_view.matrix ,0.0,&Lk.matrix);

    // Gk = H_diag.E_default
    gsl_matrix_view E_default_view = gsl_matrix_submatrix(s_dyn->aux_matrices->E_default,0,0,(N+1),(N+1));
    gsl_blas_dgemm(CblasNoTrans,CblasNoTrans,1.0, H_diag, &E_default_view.matrix,0.0,Gk);

    /*Find maxima of Gk.Dextremes*/
    //TODO: if Gk non zero else...
    gsl_matrix_view D_vertices_view = gsl_matrix_submatrix(s_dyn->aux_matrices->D_vertices,s_dyn->aux_matrices->D_vertices->size1-(N+1),0,(N+1),s_dyn->aux_matrices->D_vertices->size2);
    gsl_matrix * maxima = gsl_matrix_alloc(Gk->size1, D_vertices_view.matrix.size2);
    //Calculate Gk.Dextremes (extremum of each dimension of each polytope)
    gsl_blas_dgemm(CblasNoTrans, CblasNoTrans, 1.0, Gk, &D_vertices_view.matrix,0.0, maxima);
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

