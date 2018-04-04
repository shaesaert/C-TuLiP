#include "cimple_safe_mode.h"

/**
 * Adds a node to the beginnin of the list
 */
void push_burn_node(burn_graph_node ** head, abstract_state *state) {
    burn_graph_node * new_node;
    new_node = malloc(sizeof(burn_graph_node));

    new_node->state = state;
    new_node->next = *head;
    *head = new_node;
};

/**
 * Given a set of abstract states (associated with the transitions going out from a state, where the function was called)
 * it finds the shortest distance to a state with an invariant set.
 */
abstract_state* fastest_burn(abstract_state **transitions,
                             int transitions_count){
    abstract_state* fastest = transitions[0];
    int distance = transitions[0]->distance_invariant_set;
    for(int i = 1; i<transitions_count; i++){
        if(transitions[i]->distance_invariant_set<distance){
            distance = transitions[i]->distance_invariant_set;
            fastest = transitions[i];
        }
    }
    return fastest;
};

/**
 * Given two polytopes, computes one step backwards from second polytope towards first polytope.
 */
polytope* previous_polytope(polytope *P1,
                            polytope *P2,
                            system_dynamics *s_dyn){
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
    gsl_vector_set_zero(D_hat);
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

    return precedent_polytope;
};

/**
 * Computes N-1 polytopes the system has to transition to go from origin to target in N time steps
 */
polytope ** compute_path(polytope *origin,
                         polytope *target,
                         system_dynamics *s_dyn,
                         int N){

    polytope **path = malloc(sizeof(polytope) * N);

    path[N] = target;
    path[0] = origin;
    for(int j = N-1; j>0;j--){
        path[j]=previous_polytope(origin, path[j+1], s_dyn);
    }

    return path;
};

polytope * compute_invariant_set(polytope* X){

    polytope *Y = NULL;
    return Y;

};

/**
 * 1) Runs through all abstract states,
 * 2) checks if invariant set is contained
 * 3) sets path for all cells in those states containing an invariant set if possible
 */
burn_graph_node *set_invariant_sets(discrete_dynamics *d_dyn, system_dynamics *s_dyn){

    int N = (int)d_dyn->time_horizon;

    burn_graph_node * head_node = NULL;
    head_node = malloc(sizeof(burn_graph_node));
    head_node->state = NULL;
    head_node->next = NULL;

    for(int i = 0; i< d_dyn->abstract_states_count; i++){
        bool found_set = false;
        for(int j=0; j<d_dyn->regions[i]->cells_count; j++){
            polytope *invariant_set = compute_invariant_set(d_dyn->regions[i]->cells[j]->polytope_description);
            if(invariant_set != NULL){
                found_set = true;
                d_dyn->regions[i]->invariant_set = d_dyn->regions[i]->cells[j];
                d_dyn->regions[i]->cells[j]->safe_mode = compute_path(d_dyn->regions[i]->cells[j]->polytope_description,
                                                                      invariant_set,
                                                                      s_dyn,
                                                                      N);
            }else{
                d_dyn->regions[i]->cells[j]->safe_mode = NULL;
            }
        }
        if(found_set){
            if(d_dyn->regions[i]->next_state == d_dyn->regions[i]){
                for(int j = 0; j < d_dyn->regions[i]->cells_count; j++){
                    if(d_dyn->regions[i]->cells[j]->safe_mode == NULL){
                        d_dyn->regions[i]->cells[j]->safe_mode = compute_path(d_dyn->regions[i]->cells[j]->polytope_description,
                                                                              d_dyn->regions[i]->invariant_set->polytope_description,
                                                                              s_dyn,
                                                                              N);
                    }
                }
            }
            if (head_node->state == NULL) {
                head_node->state = d_dyn->regions[i];
            }else{
                push_burn_node(&head_node,d_dyn->regions[i]);
            }
        }
    }
    return head_node;

};

/**
 * Gets list of states containing invariant sets.
 * Burns through transition system, setting all other safe mode paths.
 */
void burning_method(burn_graph_node *seeds, discrete_dynamics *d_dyn, system_dynamics *s_dyn) {

    bool graph_burnt = false;
    int N = (int)d_dyn->time_horizon;
    burn_graph_node *current_burning = seeds;
    int burning_round = 0;
    while(!graph_burnt){
        burning_round +=1;
        burn_graph_node *next_burning = current_burning;
        while (current_burning != NULL) {
            if(current_burning->state->distance_invariant_set == NULL){
                for(int i = 0; i<current_burning->state->cells_count;i++){
                    if(current_burning->state->cells[i]->safe_mode == NULL){
                        current_burning->state->cells[i]->safe_mode = compute_path(current_burning->state->cells[i]->polytope_description,
                                                                                             current_burning->state->next_state->hull_over_polytopes,
                                                                                             s_dyn,
                                                                                             N);
                    }

                }
                current_burning->state->distance_invariant_set = burning_round;
            }
            current_burning = current_burning->next;
        }
        while(next_burning != NULL){
            for(int i = 0;i<next_burning->state->transitions_in_count;i++){
                if(next_burning->state->transitions_in[i]->distance_invariant_set == NULL){
                    push_burn_node(&current_burning,next_burning->state->transitions_in[i]);
                }
            }
            next_burning = next_burning->next;
        }
        if(current_burning == NULL){
            graph_burnt = true;
        }
    }
    while (seeds !=NULL){
        if(seeds->state->next_state != seeds->state){
            abstract_state* fastest = fastest_burn(seeds->state->transitions_out,seeds->state->transitions_out_count);
            for(int i = 0; i< seeds->state->cells_count; i++){
                if(seeds->state->cells[i]->safe_mode == NULL){
                    seeds->state->cells[i]->safe_mode = compute_path(seeds->state->cells[i]->polytope_description, fastest->hull_over_polytopes,s_dyn,N);
                }
            }
        }
        seeds = seeds->next;
    }
}

/**
 * Set the safe_mode path for every cell in every abstract_state:
 * 1) Compute invariant sets
 * 2) Find path towards invariant sets for other abstract_states
 */
void compute_safe_mode(discrete_dynamics *d_dyn, system_dynamics *s_dyn){

    burn_graph_node * invariant_sets = set_invariant_sets(d_dyn, s_dyn);
    burning_method(invariant_sets, d_dyn, s_dyn);
    free(invariant_sets);
};


void apply_safe_mode(current_state *now, polytope* current_polytope){

};
//int check_backup(gsl_vector *x_real,
//                 gsl_vector *u,
//                 gsl_matrix *A,
//                 gsl_matrix *B,
//                 polytope *check_polytope){
//    gsl_vector *x_test = gsl_vector_alloc(x_real->size);
//    gsl_vector_memcpy(x_test, x_real);
//    gsl_vector *x_temp = gsl_vector_alloc(x_test->size);
//
//    gsl_vector *Btu = gsl_vector_alloc(x_test->size);
//    //A.x
//    gsl_blas_dgemv(CblasNoTrans, 1, A, x_test, 0, x_temp);
//    //B.u
//    gsl_blas_dgemv(CblasNoTrans, 1, B, u, 0 , Btu);
//    //update x[k-1] => x[k]
//    gsl_vector_set_zero(x_test);
//    gsl_vector_add(x_test, x_temp);
//    gsl_vector_add(x_test, Btu);
//    gsl_vector_free(Btu);
//    gsl_vector_free(x_temp);
//    if(polytope_check_state(check_polytope,x_test)){
//
//        gsl_vector_free(x_test);
//        return 1;
//    }else{
//
//        gsl_vector_free(x_test);
//        return 0;
//    }
//
//};
//
//void safe_mode_polytopes(system_dynamics *s_dyn,
//                         polytope *current_polytope,
//                         polytope *safe_polytope,
//                         size_t time_horizon,
//                         polytope **polytope_list_safemode){
//
//    //Auxiliary variables
//    size_t N = time_horizon;
//    size_t n = s_dyn->A->size1;
////    size_t m = s_dyn->B->size2;
//
//
//    //Build list of polytopes that the state is going to be in in the next N time steps
//    polytope_list_safemode[0] = polytope_alloc(current_polytope->H->size1,current_polytope->H->size2);
//
//    gsl_matrix_memcpy(polytope_list_safemode[0]->H, current_polytope->H);
//    gsl_vector_memcpy(polytope_list_safemode[0]->G, current_polytope->G);
//    polytope_list_safemode[N] = polytope_alloc(safe_polytope->H->size1,safe_polytope->H->size2);
//    gsl_matrix_memcpy(polytope_list_safemode[N]->H, safe_polytope->H);
//    gsl_vector_memcpy(polytope_list_safemode[N]->G, safe_polytope->G);
//
//    //check partition system is in after i time steps
//    for (size_t i = N; i > 1; i--){
//
////        poly_t *p_universe, *new_polytope, *reduced_polytope;
////        p_universe = poly_universe((int)n+(int)m);
//        //TODO: check if target polytope full dim
////        new_polytope = solve_feasible_closed_loop(p_universe,current_polytope, polytope_list_safemode[i], s_dyn);
//        polytope *precedent = previous_polytope(current_polytope, polytope_list_safemode[i], s_dyn);
//        // Project precedent polytope onto lower dim
////
////        polytope_from_constraints(precedent, new_polytope->C);
////        reduced_polytope = poly_remove_dimensions(new_polytope, (int)m);
//        polytope *projected = polytope_alloc(precedent->H->size1,n);
//        polytope_projection(precedent, projected, n);
//        polytope_free(precedent);
//
////        poly_free(new_polytope);
////        poly_minimize(reduced_polytope);
//
////
//        polytope_list_safemode[i-1] = polytope_minimize(projected);
//        polytope_free(projected);
////        polytope_list_safemode[i-1] = polytope_alloc((size_t)reduced_polytope->C->nbrows,n);
////        polytope_from_constraints(polytope_list_safemode[i-1], reduced_polytope->C);
////        poly_free(reduced_polytope);
////        poly_free(p_universe);
//
//    }
//
//};
//
//void next_safemode_input(gsl_matrix *u,
//                         current_state *now,
//                         polytope *current,
//                         polytope *next,
//                         system_dynamics *s_dyn,
//                         cost_function *f_cost){
//
//    size_t n = s_dyn->A->size1;
//    size_t m = s_dyn->B->size2;
//    gsl_matrix *constraintH = gsl_matrix_alloc(current->H->size1+next->H->size1+(s_dyn->U_set->H->size1), n+m);
//    gsl_vector *constraintG = gsl_vector_alloc(current->H->size1+next->H->size1+(s_dyn->U_set->H->size1));
//    gsl_matrix_set_zero(constraintH);
//    gsl_vector_set_zero(constraintG);
//    polytope **polytope_list= malloc(sizeof(polytope)*2);
//    polytope_list[0] = polytope_alloc(current->H->size1,current->H->size2);
//    gsl_matrix_memcpy(polytope_list[0]->H, current->H);
//    gsl_vector_memcpy(polytope_list[0]->G, current->G);
//    polytope_list[1] = polytope_alloc(next->H->size1,next->H->size2);
//    gsl_matrix_memcpy(polytope_list[1]->H, next->H);
//    gsl_vector_memcpy(polytope_list[1]->G, next->G);
//    set_path_constraints(constraintH, constraintG, s_dyn, polytope_list, 1);
//    for(int i = 0; i< 2; i++){
//        polytope_free(polytope_list[i]);
//    }
//    free(polytope_list);
//
//    // Remove first constraints on x(0) they are obviously already satisfied
//    // L_x = L[{(polytope[0]+1),(dim_n(L))},{1,n}]
//    gsl_matrix_view constraint_x = gsl_matrix_submatrix(constraintH, current->H->size1, 0, (constraintH->size1)-(current->H->size1), n);
//    // L_u = L[{(polytope[0]+1),(dim_n(L))},{(n+1),(dim_m(L))}]
//    gsl_matrix_view constraint_u = gsl_matrix_submatrix(constraintH, current->H->size1, n, (constraintH->size1)-(current->H->size1), constraintH->size2 - n);
//    // M_view = M[{(polytope[0]+1),(dim_n(M))}]
//    gsl_vector_view constraint_g = gsl_vector_subvector(constraintG, current->H->size1, constraintG->size-current->H->size1);
//
//    //M = M-(L_x.x)
//    gsl_vector * L_x_dot_X0 = gsl_vector_alloc((constraintH->size1)-(current->H->size1));
//    gsl_blas_dgemv(CblasNoTrans, 1.0, &constraint_x.matrix, now->x, 0.0, L_x_dot_X0);
//    gsl_vector_sub(&constraint_g.vector, L_x_dot_X0);
//    //Clean up!
//    gsl_vector_free(L_x_dot_X0);
//    //Currently quadratic problem could be changed in future
//    gsl_matrix * P = gsl_matrix_alloc(m, m);
//    gsl_vector * q = gsl_vector_alloc(m);
//
//    polytope *opt_constraints = set_cost_function(P, q, &constraint_u.matrix, &constraint_g.vector, now, s_dyn, f_cost, 1);
//    double low_cost = INFINITY;
//
//    compute_optimal_control_qp(u, &low_cost, P, q, opt_constraints, 1, n);
//    if (low_cost == INFINITY){
//        //raise Exception
//        fprintf(stderr, "\n(safe_mode) Houston we have a problem: No trajectory found. System is going to crash.\n");
//        exit(EXIT_FAILURE);
//    }
//
//};
//
//void *next_safemode_computation(void *arg){
//    next_safemode_computation_arguments *sm_arg = (next_safemode_computation_arguments *)arg;
//    size_t time_step = sm_arg->time_horizon;
//    for(size_t i = sm_arg->time_horizon; i>=0; i++){
//        if (polytope_check_state(sm_arg->polytope_list_backup[i], sm_arg->now->x)){
//            time_step = i;
//            break;
//        }
//    }
//    //compute one safe step
//    if(time_step !=sm_arg->time_horizon){
//        next_safemode_input(sm_arg->u, sm_arg->now, sm_arg->polytope_list_backup[time_step], sm_arg->polytope_list_backup[time_step+1], sm_arg->s_dyn, sm_arg->f_cost);
//    }else{
//        gsl_matrix_set_zero(sm_arg->u);
//    }
//    pthread_exit(0);
//};
//void * total_safe_mode_computation(void *arg){
//
//
//    total_safemode_computation_arguments *sm_arg = (total_safemode_computation_arguments *)arg;
//
//    //Auxiliary variables
//    size_t N = sm_arg->time_horizon;
//    size_t n = sm_arg->s_dyn->A->size1;
//    size_t m = sm_arg->s_dyn->B->size2;
//
//    //Build list of polytopes that the state is going to be in in the next N time steps
//    sm_arg->polytope_list_backup[0] = polytope_alloc(sm_arg->current->H->size1,sm_arg->current->H->size2);
//    gsl_matrix_memcpy(sm_arg->polytope_list_backup[0]->H, sm_arg->current->H);
//    gsl_vector_memcpy(sm_arg->polytope_list_backup[0]->G, sm_arg->current->G);
//    sm_arg->polytope_list_backup[N] = polytope_alloc(sm_arg->safe->H->size1,sm_arg->safe->H->size2);
//    gsl_matrix_memcpy(sm_arg->polytope_list_backup[N]->H, sm_arg->safe->H);
//    gsl_vector_memcpy(sm_arg->polytope_list_backup[N]->G, sm_arg->safe->G);
//
//
//    //check partition system is in after i time steps
//    for (size_t i = N; i > 1; i--){
//        poly_t *sm_polytope;
//        poly_t *p_universe;
//        p_universe = poly_universe((int)n+(int)m);
//        //TODO: check if target polytope full dim
//        sm_polytope = solve_feasible_closed_loop(p_universe, sm_arg->current, sm_arg->polytope_list_backup[i], sm_arg->s_dyn);
//        //Project precedent polytope onto lower dim
//        poly_print(sm_polytope);
//        poly_t *reduced_sm_polytope = poly_remove_dimensions(sm_polytope, (int)m);
//
//        poly_free(sm_polytope);
//        poly_minimize(reduced_sm_polytope);
//
//        sm_arg->polytope_list_backup[i-1] = polytope_alloc((size_t)reduced_sm_polytope->C->nbrows,n);
//
//        polytope_from_constraints(sm_arg->polytope_list_backup[i-1], reduced_sm_polytope->C);
//        poly_free(reduced_sm_polytope);
//        poly_free(p_universe);
//
//    }
//    size_t time_step = sm_arg->time_horizon;
//    for(size_t i = sm_arg->time_horizon+1; i>0; i--){
//        if (polytope_check_state(sm_arg->polytope_list_backup[i-1], sm_arg->now->x)){
//            time_step = i-1;
//            break;
//        }
//    }
//    //compute one safe step
//
//    if(time_step !=sm_arg->time_horizon){
//        next_safemode_input(sm_arg->u, sm_arg->now, sm_arg->polytope_list_backup[time_step], sm_arg->polytope_list_backup[time_step+1], sm_arg->s_dyn, sm_arg->f_cost);
//    }else{
//        gsl_matrix_set_zero(sm_arg->u);
//    }
//
//    pthread_exit(NULL);
//};
//
//
///**
// * Calculate recursively polytope (return_polytope) system needs to be in, to reach P2 in one time step
// */
//poly_t * solve_feasible_closed_loop(poly_t *p_universe,
//                                    polytope *P1,
//                                    polytope *P2,
//                                    system_dynamics *s_dyn){
//    // one step backwards in time
//
//    size_t n = s_dyn->A->size2;  // State space dimension;
//    size_t m = s_dyn->B->size2;  // Input space dimension;
//    size_t p = s_dyn->E->size2;  // Disturbance space dimension;
//
//
//    size_t sum_dim = P1->H->size1+P2->H->size1;
//
//    polytope *precedent_polytope = polytope_alloc(sum_dim+s_dyn->U_set->H->size1, n+m);
//
//    // FOR precedent_polytope G
//    /*
//     *     |   P1_G      |
//     * G = |P2_G - P2_H.K|
//     *     |     0       |
//     */
//    gsl_vector_set_zero(precedent_polytope->G);
//    gsl_vector_view G_P1 = gsl_vector_subvector(precedent_polytope->G, 0, P1->G->size);
//    gsl_vector_memcpy(&G_P1.vector, P1->G);
//    gsl_vector_view G_P2 = gsl_vector_subvector(precedent_polytope->G, P1->G->size,P2->G->size);
//    gsl_vector_memcpy(&G_P2.vector, P2->G);
//    gsl_vector * P2_HdotK = gsl_vector_alloc(P2->G->size);
//    gsl_blas_dgemv(CblasNoTrans,1.0, P2->H, s_dyn->K, 0.0, P2_HdotK);
//    gsl_vector_sub(&G_P2.vector, P2_HdotK);
//    //Clean up!
//    gsl_vector_free(P2_HdotK);
//
//    // FOR Dist
//    /*
//     *         |  0   |
//     * Dist =  |P2_H.E|
//     *         |  0   |
//     */
//    gsl_matrix *Dist = gsl_matrix_alloc(sum_dim+s_dyn->U_set->H->size1, p);
//    gsl_matrix_set_zero(Dist);
//    gsl_matrix_view Dist_P2 = gsl_matrix_submatrix(Dist, P1->H->size1, 0, P2->H->size1, Dist->size2);
//    gsl_blas_dgemm(CblasNoTrans,CblasNoTrans, 1.0, P2->H, s_dyn->E, 0.0, &Dist_P2.matrix);
//
//    // FOR precedent_polytope H
//    /*
//     *  H = |H1   0 |
//     *      |H2A H2B|
//     *      |  HU   |
//     */
//    gsl_matrix_set_zero(precedent_polytope->H);
//
//    gsl_matrix_view H_P1 = gsl_matrix_submatrix(precedent_polytope->H, 0, 0, P1->H->size1, n);
//    gsl_matrix_memcpy(&H_P1.matrix, P1->H);
//    gsl_matrix_view H_P2_1 = gsl_matrix_submatrix(precedent_polytope->H, P1->H->size1, 0, P2->H->size1, n);
//    gsl_blas_dgemm(CblasNoTrans,CblasNoTrans, 1.0, P2->H, s_dyn->A, 0.0, &H_P2_1.matrix);
//    gsl_matrix_view H_P2_2 = gsl_matrix_submatrix(precedent_polytope->H, P1->H->size1, n, P2->H->size1, m);
//    gsl_blas_dgemm(CblasNoTrans,CblasNoTrans, 1.0, P2->H, s_dyn->B, 0.0, &H_P2_2.matrix);
//
//    if (s_dyn->U_set->H->size2 == m){
//        gsl_matrix_view HU = gsl_matrix_submatrix(precedent_polytope->H,sum_dim, n, s_dyn->U_set->H->size1,m);
//        gsl_matrix_memcpy(&HU.matrix,s_dyn->U_set->H);
//    } else if (s_dyn->U_set->H->size2 == m+n){
//        // transforms U_set.H from |constraints_ input constraints_state| to |constraints_state constraints_input|
//        /*
//         * |m m m m n n n|    |n n n m m m m|
//         * |m m m m n n n| => |n n n m m m m|
//         * |m m m m n n n|    |n n n m m m m|
//         */
//        gsl_matrix_view HU = gsl_matrix_submatrix(precedent_polytope->H,sum_dim, n, s_dyn->U_set->H->size1,m);
//        gsl_matrix * exchange_matrix = gsl_matrix_alloc(n+m,n+m);
//        gsl_matrix_set_zero(exchange_matrix);
//        gsl_matrix_view eye_m = gsl_matrix_submatrix(exchange_matrix, 0, n, m, m);
//        gsl_matrix_set_identity(&eye_m.matrix);
//        gsl_matrix_view eye_n = gsl_matrix_submatrix(exchange_matrix, m, 0, n, n);
//        gsl_matrix_set_identity(&eye_n.matrix);
//        gsl_blas_dgemm(CblasNoTrans,CblasNoTrans,1.0, s_dyn->U_set->H,exchange_matrix, 0.0, &HU.matrix);
//    }
//
//    // Get disturbance sets
//    gsl_vector * D_hat = gsl_vector_alloc(precedent_polytope->G->size);
//    gsl_vector_set_zero(D_hat);
//    if (!(gsl_matrix_isnull(Dist))){
//        gsl_matrix * maxima = gsl_matrix_alloc(Dist->size1, s_dyn->aux_matrices->D_one_step->size2);
//        //Calculate Dist.Dextremes (extremum of each dimension of each polytope)
//        gsl_blas_dgemm(CblasNoTrans, CblasNoTrans, 1.0, Dist, s_dyn->aux_matrices->D_one_step,0.0, maxima);
//        //find the maximum for each dimension of each polytope
//        for(size_t i = 0; i < sum_dim; i++){
//            gsl_vector_view max_row = gsl_matrix_row(maxima, i);
//            gsl_vector_set(D_hat, i, gsl_vector_max(&max_row.vector));
//        }
//        gsl_matrix_free(maxima);
//    } else{
//        gsl_vector_set_zero(D_hat);
//    }
//    gsl_matrix_free(Dist);
//    gsl_vector_sub(precedent_polytope->G, D_hat);
//    //Clean up!
//    gsl_vector_free(D_hat);
//
//    matrix_t* constraints = matrix_alloc((int)P1->H->size1+(int)P2->H->size1+(int)s_dyn->U_set->H->size1, (int)n+(int)m+2,false);
//    polytope_to_constraints(constraints, precedent_polytope);
//    polytope_free(precedent_polytope);
//    matrix_free(constraints);
//    return poly_add_constraints(p_universe, constraints);
//};
