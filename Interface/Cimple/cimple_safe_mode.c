#include <gsl/gsl_matrix.h>
#include "cimple_safe_mode.h"

/**
 * Adds a node to the beginning of the list
 */
void push_burn_node(burn_graph_node ** head,
                    abstract_state *state)
{

    burn_graph_node * new_node;
    new_node = malloc(sizeof(burn_graph_node));

    new_node->state = state;
    new_node->next = *head;
    *head = new_node;
};

/**
 * Remove a node from the beginning of the list
 */
void pop_burn_node(burn_graph_node ** head)
{

    burn_graph_node * next_node = NULL;

    next_node = (*head)->next;
    free(*head);
    *head = next_node;

};

/**
 * Delete and free memory of all nodes of a list
 */
void clear_burn_list(burn_graph_node **head)
{
    while (head !=NULL){
        pop_burn_node(head);
    }
};

/**
 * Given a set of abstract states (associated with the transitions going out from a state, where the function was called)
 * it finds the shortest distance to a state with an invariant set.
 */
abstract_state* fastest_burn(abstract_state **transitions,
                             int transitions_count)
{
    //Initialize
    abstract_state* fastest = transitions[0];
    int distance = transitions[0]->distance_invariant_set;

    //Check that there are more than 1 transition to evaluate, else trivial
    if(transitions_count >1){

        //Compare transitions
        for(int i = 1; i<transitions_count; i++){
            if(transitions[i]->distance_invariant_set<distance){
                distance = transitions[i]->distance_invariant_set;
                fastest = transitions[i];
            }
        }

    }

    return fastest;
}

/**
 * Given two polytopes, computes one step backwards from second polytope towards first polytope.
 */
polytope* previous_polytope(polytope *P1,
                            polytope *P2,
                            system_dynamics *s_dyn)
{

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
     *  H = |H1   0 |  OR  H = |H1    0 |
     *      |H2A H2B|          |H2A  H2B|
     *      | 0  HU |          |   HU   |
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
        gsl_matrix_view HU = gsl_matrix_submatrix(precedent_polytope->H,sum_dim, 0, s_dyn->U_set->H->size1,m+n);
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
    }
    gsl_vector_sub(precedent_polytope->G, D_hat);


    polytope *return_polytope = polytope_projection(precedent_polytope, n);

    //Clean up!
    gsl_matrix_free(Dist);
    gsl_vector_free(D_hat);
    polytope_free(precedent_polytope);

    return return_polytope;
};

/**
 * Computes N-1 polytopes the system has to transition to go from origin to target in N time steps
 */
polytope ** compute_path(polytope *origin,
                         polytope *target,
                         system_dynamics *s_dyn,
                         int N)
{

    //Initialize
    polytope **path = malloc(sizeof(polytope) * N);

    //Instead of just pointing path[N] = target, the memory is copied,
    // thus when the target polytope is freed somewhere the path stays complete
    path[N] = polytope_alloc(target->H->size1,target->H->size2);
    gsl_matrix_memcpy(path[N]->H,target->H);

    path[0] = polytope_alloc(origin->H->size1,origin->H->size2);
    gsl_matrix_memcpy(path[0]->H,origin->H);

    //Compute intermediate steps
    for(int j = N-1; j>0;j--){
        path[j]=previous_polytope(path[0], path[j+1], s_dyn);
    }

    return path;
};

polytope *pre_alpha(polytope *R_i,
                    gsl_matrix *A,
                    gsl_matrix *B,
                    polytope *W_set,
                    polytope *U_set,
                    polytope *scaled_unit_cube)
{
    size_t n = A->size2;
    size_t m = B->size2;
    polytope *W_set_scaled = polytope_minkowski(W_set, scaled_unit_cube);
    polytope *R_i_scaled = polytope_pontryagin(R_i, W_set_scaled);

    polytope *P0 = polytope_alloc(R_i_scaled->H->size1+U_set->H->size1, n+m);
    gsl_matrix_set_zero(P0->H);
    gsl_matrix_view H_P2_1 = gsl_matrix_submatrix(P0->H, 0, 0, R_i_scaled->H->size1, n);
    gsl_blas_dgemm(CblasNoTrans,CblasNoTrans, 1.0, R_i_scaled->H, A, 0.0, &H_P2_1.matrix);
    gsl_matrix_view H_P2_2 = gsl_matrix_submatrix(P0->H, 0, n, R_i_scaled->H->size1, m);
    gsl_blas_dgemm(CblasNoTrans,CblasNoTrans, 1.0, R_i_scaled->H, B, 0.0, &H_P2_2.matrix);
    if (U_set->H->size2 == m){
        gsl_matrix_view HU = gsl_matrix_submatrix(P0->H,R_i_scaled->H->size1, n, U_set->H->size1,m);
        gsl_matrix_memcpy(&HU.matrix,U_set->H);
    } else if (U_set->H->size2 == m+n){
        // transforms U_set.H from |constraints_ input constraints_state| to |constraints_state constraints_input|
        /*
         * |m m m m n n n|    |n n n m m m m|
         * |m m m m n n n| => |n n n m m m m|
         * |m m m m n n n|    |n n n m m m m|
         */
        gsl_matrix_view HU = gsl_matrix_submatrix(P0->H,R_i_scaled->H->size1, 0, U_set->H->size1,m+n);
        gsl_matrix * exchange_matrix = gsl_matrix_alloc(n+m,n+m);
        gsl_matrix_set_zero(exchange_matrix);
        gsl_matrix_view eye_m = gsl_matrix_submatrix(exchange_matrix, 0, n, m, m);
        gsl_matrix_set_identity(&eye_m.matrix);
        gsl_matrix_view eye_n = gsl_matrix_submatrix(exchange_matrix, m, 0, n, n);
        gsl_matrix_set_identity(&eye_n.matrix);
        gsl_blas_dgemm(CblasNoTrans,CblasNoTrans,1.0, U_set->H,exchange_matrix, 0.0, &HU.matrix);
    }
    gsl_vector_set_zero(P0->G);
    gsl_vector_view G_P1 = gsl_vector_subvector(P0->G, 0, R_i_scaled->G->size);
    gsl_vector_memcpy(&G_P1.vector, R_i_scaled->G);
    gsl_vector_view G_P2 = gsl_vector_subvector(P0->G, R_i_scaled->G->size,U_set->G->size);
    gsl_vector_memcpy(&G_P2.vector, U_set->G);

    polytope *pre_R_1 = polytope_projection(P0, n);
    polytope_free(P0);
    return pre_R_1;
}
polytope * compute_invariant_set(polytope* X,
                                 gsl_matrix *A,
                                 gsl_matrix *B,
                                 polytope *W_set,
                                 polytope *U_set,
                                 double alpha)
{
    polytope * scaled_unit_cube = polytope_scaled_unit_cube(alpha, (int)X->H->size2);

    polytope *R_i = polytope_alloc(X->H->size1,X->H->size2);
    gsl_matrix_memcpy(R_i->H,X->H);
    gsl_vector_memcpy(R_i->G,X->G);
    polytope *pre_R_i = pre_alpha(R_i,A,B,W_set,U_set,scaled_unit_cube);
    polytope *R_i_plus = polytope_unite_inequalities(pre_R_i, X);
    dd_ErrorType err = dd_NoError;
    dd_WriteMatrix(stdout,dd_CopyGenerators(polytope_to_cdd(R_i_plus,&err)));

    polytope *R_scaled = polytope_minkowski(R_i_plus, scaled_unit_cube);
    while(!(polytope_is_subset(R_i, R_scaled))){
        polytope_free(pre_R_i);
        polytope_free(R_scaled);
        polytope_free(R_i);
        R_i = R_i_plus;
        pre_R_i = pre_alpha(R_i,A,B,W_set,U_set,scaled_unit_cube);
        R_i_plus = polytope_unite_inequalities(pre_R_i, X);
        R_scaled = polytope_minkowski(R_i_plus, scaled_unit_cube);
    }
    polytope_free(pre_R_i);
    polytope_free(R_i_plus);
    polytope_free(R_scaled);
    return R_i;

};

bool has_transition(abstract_state *state,
                    abstract_state *transition)
{
    bool transition_found = false;
    for(int i = 0; i<state->transitions_in_count; i++){
        if(state->transitions_in[i] == transition){
            transition_found = true;
        }
    }

    return transition_found;
};
/**
 * 1) Runs through all abstract states,
 * 2) checks if invariant set is contained
 * 3) sets path for all cells in those states containing an invariant set if possible
 */
burn_graph_node *set_invariant_sets(discrete_dynamics *d_dyn,
                                    system_dynamics *s_dyn)
{

    //Initialize graph
    burn_graph_node * head_node = NULL;
    head_node = malloc(sizeof(burn_graph_node));
    head_node->state = NULL;
    head_node->next = NULL;
    int N = (int)d_dyn->time_horizon;
    double unit_cube_scale = 1;
    //Create graph by
    // 1) running through all abstract_states and
    // 2) check whether it contains an invariant set
    for(int i = 0; i< d_dyn->abstract_states_count; i++){
        bool found_set = false;
        for(int j=0; j<d_dyn->regions[i]->cells_count; j++){
            //Try to compute invariant set
            polytope *invariant_set = compute_invariant_set(d_dyn->regions[i]->cells[j]->polytope_description,
                                                            s_dyn->A,
                                                            s_dyn->B,
                                                            s_dyn->W_set,
                                                            s_dyn->U_set,
                                                            unit_cube_scale);

            //if invariant set is found
            if(invariant_set != NULL){
                found_set = true;
                //Set invariant_set cell to A cell containing an invariant set
                //(may be more than one invariant set!!)
                d_dyn->regions[i]->invariant_set = d_dyn->regions[i]->cells[j];
                //Compute path for rest of cell to invariant set (may be just a subset of that polytope)
                d_dyn->regions[i]->cells[j]->safe_mode = compute_path(d_dyn->regions[i]->cells[j]->polytope_description,
                                                                      invariant_set,
                                                                      s_dyn,
                                                                      N);
            }else{
                //Set NULL because later safe_mode==NULL cells will be picked out
                d_dyn->regions[i]->cells[j]->safe_mode = NULL;
            }
        }

        //If abstract state contains at least one invariant set it is appended to the graph
        if(found_set){
            //Check whether state has a transition to itself
            if(has_transition(d_dyn->regions[i], d_dyn->regions[i])){
                //if yes compute the safe_mode path for the cells that do not contain an invariant set
                for(int j = 0; j < d_dyn->regions[i]->cells_count; j++){
                    if(d_dyn->regions[i]->cells[j]->safe_mode == NULL){
                        d_dyn->regions[i]->cells[j]->safe_mode = compute_path(d_dyn->regions[i]->cells[j]->polytope_description,
                                                                              d_dyn->regions[i]->invariant_set->polytope_description,
                                                                              s_dyn,
                                                                              N);
                    }
                }
            }
            //Append state to graph
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
//void burning_method(burn_graph_node *seeds,
//                    discrete_dynamics *d_dyn,
//                    system_dynamics *s_dyn)
//{
//
//    //Initialize needed variables
//    bool graph_burnt = false;
//    int N = (int)d_dyn->time_horizon;
//    burn_graph_node *current_burning = seeds;
//    int burning_round = 0;
//
//
//    while(!graph_burnt){
//        burning_round +=1;
//        burn_graph_node *next_burning = current_burning;
//        while (current_burning != NULL) {
//            if(current_burning->state->distance_invariant_set == INFINITY){
//                for(int i = 0; i<current_burning->state->cells_count;i++){
//                    if(current_burning->state->cells[i]->safe_mode == NULL){
//                        current_burning->state->cells[i]->safe_mode = compute_path(current_burning->state->cells[i]->polytope_description,
//                                                                                             current_burning->state->next_state->hull_over_polytopes,
//                                                                                             s_dyn,
//                                                                                             N);
//                    }
//
//                }
//                current_burning->state->distance_invariant_set = burning_round;
//            }
//            current_burning = current_burning->next;
//        }
//        while(next_burning != NULL){
//            for(int i = 0;i<next_burning->state->transitions_in_count;i++){
//                if(next_burning->state->transitions_in[i]->distance_invariant_set == NULL){
//                    push_burn_node(&current_burning,next_burning->state->transitions_in[i]);
//                }
//            }
//            next_burning = next_burning->next;
//        }
//        if(current_burning == NULL){
//            graph_burnt = true;
//        }
//    }
//    while (seeds !=NULL){
//        if(seeds->state->next_state != seeds->state){
//            abstract_state* fastest = fastest_burn(seeds->state->transitions_out,seeds->state->transitions_out_count);
//            for(int i = 0; i< seeds->state->cells_count; i++){
//                if(seeds->state->cells[i]->safe_mode == NULL){
//                    seeds->state->cells[i]->safe_mode = compute_path(seeds->state->cells[i]->polytope_description, fastest->hull_over_polytopes,s_dyn,N);
//                }
//            }
//        }
//        seeds = seeds->next;
//    }
//};

/**
 * Set the safe_mode path for every cell in every abstract_state:
 * 1) Compute invariant sets
 * 2) Find path towards invariant sets for other abstract_states
 */
//void compute_safe_mode(discrete_dynamics *d_dyn,
//                       system_dynamics *s_dyn)
//{
//
//    burn_graph_node * invariant_sets = set_invariant_sets(d_dyn, s_dyn);
//    burning_method(invariant_sets, d_dyn, s_dyn);
//    free(invariant_sets);
//};

//gsl_vector *one_step_input(polytope *A, polytope *B)
//{
//    gsl_vector *u;
//    return u;
//};

//abstract_state *find_current_state(gsl_vector *x,
//                                   discrete_dynamics *d_dyn)
//{
//    abstract_state *now;
//    return now;
//};
//
//void *apply_safe_mode(current_state *now,
//                      discrete_dynamics *d_dyn,
//                      system_dynamics *s_dyn,
//                      void *arg)
//{
//
//    //find correct cell
//    cell * current_cell = NULL;
//    int N = (int)d_dyn->time_horizon;
//    int found = 0;
//    int i;
//    for(i = 0; i < d_dyn->regions[now->current_abs_state]->cells_count; i++){
//        found = polytope_check_state(d_dyn->regions[now->current_abs_state]->cells[i]->polytope_description, now->x);
//        if(found){
//            current_cell = d_dyn->regions[now->current_abs_state]->cells[i];
//            break;
//        }
//    }
//
//    //if not found check all other regions all other cells
//    if(current_cell ==NULL){
//        for(i = 0; i<d_dyn->abstract_states_count; i++){
//            for(int j = 0; j < d_dyn->regions[i]->cells_count; j++){
//                found = polytope_check_state(d_dyn->regions[i]->cells[j]->polytope_description, now->x);
//                if(found){
//                    now->current_abs_state = i;
//                    current_cell = d_dyn->regions[i]->cells[j];
//                }
//            }
//        }
//    }
//    int safe_mode_state = 0;
//    found = 0;
//    for(i = N; i>0; i--){
//        found = polytope_check_state(current_cell->safe_mode[i], now->x);
//        if(found){
//            safe_mode_state = i;
//            break;
//        }
//    }
//    pthread_mutex_t *mx = arg;
//
//    //while ! in invariant set
//    while(d_dyn->regions[now->current_abs_state]->invariant_set == NULL && !needQuit(mx)){
//        //find polytope of safe_mode
//        int check = polytope_check_state(current_cell->safe_mode[safe_mode_state], now->x);
//        if(!check){
//            safe_mode_state = 0;
//            found = 0;
//            for(i = N; i>0; i--){
//                found = polytope_check_state(current_cell->safe_mode[i], now->x);
//                if(found){
//                    safe_mode_state = i;
//                    break;
//                }
//            }
//        }
//
//        //linear combination to next polytope in line
//        gsl_vector *u = one_step_input(current_cell->safe_mode[safe_mode_state],
//                                               current_cell->safe_mode[safe_mode_state+1]);
//        gsl_vector *w = gsl_vector_alloc(s_dyn->E->size2);
//        simulate_disturbance(w, 0, 0.01);
//        apply_control(now->x, u, s_dyn->A, s_dyn->B, s_dyn->E, w, (size_t)safe_mode_state);
//
//    }
//
//    //while not interrupted stay in invariant set
//
//    while( !needQuit(mx) ) {
//        int check = polytope_check_state(d_dyn->regions[now->current_abs_state]->invariant_set->polytope_description, now->x);
//        if(!check){
//            safe_mode_state = 0;
//            found = 0;
//            for(i = N; i>0; i--){
//                found = polytope_check_state(current_cell->safe_mode[i], now->x);
//                if(found){
//                    safe_mode_state = i;
//                    break;
//                }
//            }
//        }
//        one_step_input(d_dyn->regions[now->current_abs_state]->invariant_set->polytope_description, d_dyn->regions[now->current_abs_state]->invariant_set->polytope_description);
//    }
//    return NULL;
//};
