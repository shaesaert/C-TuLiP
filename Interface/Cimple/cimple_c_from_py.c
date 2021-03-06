
//
// Autogenerated code. Based on code created by L.J. Feldstein
//

#include "cimple_c_from_py.h"

void system_alloc(current_state **now, system_dynamics **s_dyn, cost_function **f_cost,discrete_dynamics **d_dyn){

    //Set help variables

    size_t time_horizon = 5;
    int abstract_states_count= 10;
    int number_of_original_regions= 5;
    int closed_loop = 1;
    int conservative = 1;
    int ord =2;
    size_t n =1;
    size_t m =1;
    size_t p =1;
    size_t u_set_size =2;
    size_t w_set_size =2;
    double distance_weight =3;

    int default_cell = 1;
    size_t total_number_polytopes = 10;
    int polytopes_in_region[10] = {1,1,1,1,1,1,1,1,1,1};
    size_t original_total_number_polytopes = 7;
    int orig_polytopes_in_region[5] = {1,1,1,1,3};

    size_t *polytope_sizes= malloc(total_number_polytopes * sizeof(size_t));
    size_t *hull_sizes= malloc(abstract_states_count * sizeof(size_t));
    size_t *original_polytope_sizes= malloc(original_total_number_polytopes * sizeof(size_t));
    size_t *original_hull_sizes= malloc(number_of_original_regions * sizeof(size_t));
    memcpy(polytope_sizes, ((size_t []){2,2,2,2,2,2,2,2,2,2}),10* sizeof(polytope_sizes[0]));
    memcpy(hull_sizes, ((size_t []){2,2,2,2,2,2,2,2,2,2}),10* sizeof(hull_sizes[0]));
    memcpy(original_polytope_sizes, ((size_t []){2,2,2,2,2,2,2}),7* sizeof(original_polytope_sizes[0]));
    memcpy(original_hull_sizes, ((size_t []){2,2,2,2,2}),5* sizeof(original_hull_sizes[0]));
    int transitions_in_sizes[10] = {1, 1, 2, 3, 4, 2, 2, 3, 2, 0};
    int transitions_out_sizes[10] = {2, 2, 1, 2, 2, 1, 2, 1, 1, 6};

    *now = state_alloc(n,default_cell);
    *s_dyn = system_dynamics_alloc(n, m, p, w_set_size, u_set_size, time_horizon);
    *f_cost = cost_function_alloc(n, m, time_horizon, distance_weight);
    *d_dyn = discrete_dynamics_alloc(polytopes_in_region, polytope_sizes,  hull_sizes, orig_polytopes_in_region, original_polytope_sizes, original_hull_sizes, transitions_in_sizes, transitions_out_sizes, n, abstract_states_count, number_of_original_regions, closed_loop, conservative, ord, time_horizon);

    free(polytope_sizes);
    free(hull_sizes);
    free(original_polytope_sizes);
    free(original_hull_sizes);
}

void system_init(current_state *now, system_dynamics *s_dyn,cost_function *f_cost ,discrete_dynamics *d_dyn){

    //Set help variables

    size_t time_horizon = 5;
    int abstract_states_count= 10;
    int number_of_original_regions= 5;
    size_t n =1;
    size_t m =1;
    size_t p =1;
    size_t u_set_size =2;
    size_t w_set_size =2;
    double *initial_state = malloc(n* sizeof (double));
    memcpy(initial_state, (double []){77.0},1* sizeof(initial_state[0]));

    // Initialize state:
    gsl_vector_from_array(now->x, initial_state, "now->x");

    //Clean up!
    free(initial_state);

    // Transform system dynamics from python to C
    double *sys_A = malloc(n* n* sizeof (double));
    memcpy(sys_A, ((double []){1.0}),1* sizeof(double));
    gsl_matrix_from_array(s_dyn->A, sys_A, "s_dyn->A");
    free(sys_A);
    double *sys_B = malloc(n* m* sizeof (double));
    memcpy(sys_B, ((double []){1.0}),1* sizeof(double));
    gsl_matrix_from_array(s_dyn->B, sys_B,"s_dyn->B");
    free(sys_B);
    double *sys_E = malloc(n* p* sizeof (double));
    memcpy(sys_E, ((double []){1.0}),1* sizeof(double));
    gsl_matrix_from_array(s_dyn->E, sys_E, "s_dyn->E");
    free(sys_E);
    double *sys_K = malloc(n* sizeof (double));
    memcpy(sys_K, ((double []){0.0}),1* sizeof(double));
    gsl_vector_from_array(s_dyn->K, sys_K, "s_dyn->K");
    free(sys_K);
    double *sys_USetH = malloc(u_set_size* n* sizeof (double));
    memcpy(sys_USetH, ((double []){1.0,-1.0}),2* sizeof(double));
    gsl_matrix_from_array(s_dyn->U_set->H, sys_USetH, "s_dyn->U_set->H");
    free(sys_USetH);
    double *sys_WSetH = malloc(w_set_size* n* sizeof (double));
    memcpy(sys_WSetH, ((double []){1.0,-1.0}),2* sizeof(double));
    gsl_matrix_from_array(s_dyn->W_set->H, sys_WSetH,"s_dyn->W_set->H");
    free(sys_WSetH);
    double *sys_USetG = malloc(u_set_size* sizeof (double));
    memcpy(sys_USetG, ((double []){1.0,1.0}),2* sizeof(double));
    gsl_vector_from_array(s_dyn->U_set->G, sys_USetG, "s_dyn->U_set->G");
    free(sys_USetG);
    double *sys_WSetG = malloc(w_set_size* sizeof (double));
    memcpy(sys_WSetG, ((double []){0.1,0.1}),2* sizeof(double));
    gsl_vector_from_array(s_dyn->W_set->G, sys_WSetG, "s_dyn->W_set->G");
    free(sys_WSetG);
    double *sys_help_A_K = malloc(n* time_horizon * n * time_horizon* sizeof (double));
    memcpy(sys_help_A_K, ((double []){1.0,0.0,0.0,0.0,0.0,1.0,1.0,0.0,0.0,0.0,1.0,1.0,1.0,0.0,0.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0,1.0,1.0,1.0}),25* sizeof(double));
    gsl_matrix_from_array(s_dyn->aux_matrices->A_K, sys_help_A_K, "s_dyn->aux_matrices->A_K");
    free(sys_help_A_K);
    double *sys_help_A_N = malloc(n* time_horizon * n * sizeof (double));
    memcpy(sys_help_A_N, ((double []){1.0,1.0,1.0,1.0,1.0}),5* sizeof(double));
    gsl_matrix_from_array(s_dyn->aux_matrices->A_N, sys_help_A_N, "s_dyn->aux_matrices->A_N");
    free(sys_help_A_N);
    double *sys_help_E_diag = malloc(n*time_horizon* p*time_horizon* sizeof (double));
    memcpy(sys_help_E_diag, ((double []){1.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0}),25* sizeof(double));
    gsl_matrix_from_array(s_dyn->aux_matrices->E_diag, sys_help_E_diag, "s_dyn->aux_matrices->E_diag");
    free(sys_help_E_diag);
    double *sys_help_B_diag = malloc(n*time_horizon* m*time_horizon* sizeof (double));
    memcpy(sys_help_B_diag, ((double []){1.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0}),25* sizeof(double));
    gsl_matrix_from_array(s_dyn->aux_matrices->B_diag, sys_help_B_diag, "s_dyn->aux_matrices->B_diag");
    free(sys_help_B_diag);
    double *sys_help_K_hat = malloc(n* time_horizon* sizeof (double));
    memcpy(sys_help_K_hat, ((double []){0.0,0.0,0.0,0.0,0.0}),5* sizeof(double));
    gsl_vector_from_array(s_dyn->aux_matrices->K_hat, sys_help_K_hat, "s_dyn->aux_matrices->K_hat");
    free(sys_help_K_hat);
    double *sys_help_L_default = malloc(n*(time_horizon+1) * (n+m*(time_horizon))* sizeof (double));
    memcpy(sys_help_L_default, ((double []){1.0,0.0,0.0,0.0,0.0,0.0,1.0,1.0,0.0,0.0,0.0,0.0,1.0,1.0,1.0,0.0,0.0,0.0,1.0,1.0,1.0,1.0,0.0,0.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0,1.0,1.0,1.0,1.0}),36* sizeof(double));
    gsl_matrix_from_array(s_dyn->aux_matrices->L_default, sys_help_L_default, "s_dyn->aux_matrices->L_default");
    free(sys_help_L_default);
    double *sys_help_E_default = malloc(n* time_horizon* p* time_horizon* sizeof (double));
    memcpy(sys_help_E_default, ((double []){0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,1.0,1.0,0.0,0.0,0.0,1.0,1.0,1.0,0.0,0.0,1.0,1.0,1.0,1.0,0.0}),25* sizeof(double));
    gsl_matrix_from_array(s_dyn->aux_matrices->E_default, sys_help_E_default, "s_dyn->aux_matrices->E_default");
    free(sys_help_E_default);
    double *sys_help_Ct = malloc(n*time_horizon*m*time_horizon*sizeof(double));
    memcpy(sys_help_Ct, ((double []){1.0,0.0,0.0,0.0,0.0,1.0,1.0,0.0,0.0,0.0,1.0,1.0,1.0,0.0,0.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0,1.0,1.0,1.0}),25* sizeof(double));
    gsl_matrix_from_array(s_dyn->aux_matrices->Ct, sys_help_Ct, "s_dyn->aux_matrices->Ct");
    free(sys_help_Ct);
    double *sys_help_MU = malloc(u_set_size*time_horizon * sizeof(double));
    memcpy(sys_help_MU, ((double []){1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0}),10* sizeof(double));
    gsl_vector_from_array(s_dyn->aux_matrices->MU, sys_help_MU, "s_dyn->aux_matrices->MU");
    free(sys_help_MU);
    double *sys_help_GU = malloc(u_set_size*time_horizon* p*time_horizon* sizeof(double));
    memcpy(sys_help_GU, ((double []){0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0}),50* sizeof(double));
    gsl_matrix_from_array(s_dyn->aux_matrices->GU, sys_help_GU,"s_dyn->aux_matrices->GU");
    free(sys_help_GU);
    double *sys_help_LU = malloc(u_set_size*time_horizon * (n+m*(time_horizon))* sizeof (double));
    memcpy(sys_help_LU, ((double []){0.0,1.0,0.0,0.0,0.0,0.0,0.0,-1.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,-1.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,-1.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,-1.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,-1.0}),60* sizeof(double));
    gsl_matrix_from_array(s_dyn->aux_matrices->LU, sys_help_LU, "s_dyn->aux_matrices->LU");
    free(sys_help_LU);

    // Set cost function
    double *cf_R = malloc(n* time_horizon* n* time_horizon* sizeof (double));
    memcpy(cf_R, ((double []){0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0}),25* sizeof(double));
    gsl_matrix_from_array(f_cost->R, cf_R, "f_cost->R");
    free(cf_R);
    double *cf_Q = malloc(m* time_horizon* m* time_horizon* sizeof (double));
    memcpy(cf_Q, ((double []){1.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0}),25* sizeof(double));
    gsl_matrix_from_array(f_cost->Q, cf_Q, "f_cost->Q");
    free(cf_Q);
    double *cf_r = malloc(n* time_horizon* sizeof (double));
    memcpy(cf_r, ((double []){0.0,0.0,0.0,0.0,0.0}),5* sizeof(double));
    gsl_vector_from_array(f_cost->r, cf_r, "f_cost->r");
    free(cf_r);

    size_t total_number_polytopes = 10;
    size_t original_total_number_polytopes = 7;

    size_t *polytope_sizes= malloc(total_number_polytopes * sizeof(size_t));
    size_t *hull_sizes= malloc(abstract_states_count * sizeof(size_t));
    size_t *original_polytope_sizes= malloc(original_total_number_polytopes * sizeof(size_t));
    size_t *original_hull_sizes= malloc(number_of_original_regions * sizeof(size_t));
    memcpy(polytope_sizes, ((size_t []){2,2,2,2,2,2,2,2,2,2}),10* sizeof(polytope_sizes[0]));
    memcpy(hull_sizes, ((size_t []){2,2,2,2,2,2,2,2,2,2}),10* sizeof(hull_sizes[0]));
    memcpy(original_polytope_sizes, ((size_t []){2,2,2,2,2,2,2}),7* sizeof(original_polytope_sizes[0]));
    memcpy(original_hull_sizes, ((size_t []){2,2,2,2,2}),5* sizeof(original_hull_sizes[0]));

    double **left_side = malloc(total_number_polytopes* sizeof(double*));
    double **right_side = malloc(total_number_polytopes* sizeof(double*));
    double **hulls_left_side = malloc(abstract_states_count*sizeof(double*));
    double **hulls_right_side = malloc(abstract_states_count*sizeof(double*));
    double **cheby = malloc(total_number_polytopes * sizeof(double*));
    double **hull_cheby = malloc(abstract_states_count*sizeof(double*));
    for (int i = 0; i < total_number_polytopes; i++) {
        left_side[i] = malloc(polytope_sizes[i]* n * sizeof(double));
        right_side[i] = malloc(polytope_sizes[i] * sizeof(double));
        cheby[i] = malloc(n*sizeof(double));
    }
    for (int i = 0; i < abstract_states_count; i++) {
        hulls_left_side[i] = malloc(hull_sizes[i]* n * sizeof(double));
        hulls_right_side[i] = malloc(hull_sizes[i] * sizeof(double));
        hull_cheby[i] = malloc(n*sizeof(double));

    }
    memcpy(left_side[0], ((double []){1.0,-1.0}),2* sizeof(double));
    memcpy(right_side[0], ((double []){84.50000000000004,-80.0}),2* sizeof(double));
    memcpy(cheby[0], ((double []){82.25000000000003}),1* sizeof(double));
    memcpy(hulls_left_side[0], ((double []){1.0,-1.0}),2* sizeof(double));
    memcpy(hulls_right_side[0], ((double []){84.50000000000004,-80.0}),2* sizeof(double));
    memcpy(hull_cheby[0], ((double []){82.25000000000003}),1* sizeof(double));
    memcpy(left_side[1], ((double []){1.0,-1.0}),2* sizeof(double));
    memcpy(right_side[1], ((double []){78.0,-76.0}),2* sizeof(double));
    memcpy(cheby[1], ((double []){77.0}),1* sizeof(double));
    memcpy(hulls_left_side[1], ((double []){1.0,-1.0}),2* sizeof(double));
    memcpy(hulls_right_side[1], ((double []){78.0,-76.0}),2* sizeof(double));
    memcpy(hull_cheby[1], ((double []){77.0}),1* sizeof(double));
    memcpy(left_side[2], ((double []){1.0,-1.0}),2* sizeof(double));
    memcpy(right_side[2], ((double []){74.0,-72.0}),2* sizeof(double));
    memcpy(cheby[2], ((double []){73.0}),1* sizeof(double));
    memcpy(hulls_left_side[2], ((double []){1.0,-1.0}),2* sizeof(double));
    memcpy(hulls_right_side[2], ((double []){74.0,-72.0}),2* sizeof(double));
    memcpy(hull_cheby[2], ((double []){73.0}),1* sizeof(double));
    memcpy(left_side[3], ((double []){-1.0,1.0}),2* sizeof(double));
    memcpy(right_side[3], ((double []){-60.49999999999999,65.0}),2* sizeof(double));
    memcpy(cheby[3], ((double []){62.75}),1* sizeof(double));
    memcpy(hulls_left_side[3], ((double []){-1.0,1.0}),2* sizeof(double));
    memcpy(hulls_right_side[3], ((double []){-60.49999999999999,65.0}),2* sizeof(double));
    memcpy(hull_cheby[3], ((double []){62.75}),1* sizeof(double));
    memcpy(left_side[4], ((double []){-1.0,1.0}),2* sizeof(double));
    memcpy(right_side[4], ((double []){-78.0,80.0}),2* sizeof(double));
    memcpy(cheby[4], ((double []){79.0}),1* sizeof(double));
    memcpy(hulls_left_side[4], ((double []){-1.0,1.0}),2* sizeof(double));
    memcpy(hulls_right_side[4], ((double []){-78.0,80.0}),2* sizeof(double));
    memcpy(hull_cheby[4], ((double []){79.0}),1* sizeof(double));
    memcpy(left_side[5], ((double []){-1.0,1.0}),2* sizeof(double));
    memcpy(right_side[5], ((double []){-74.0,76.0}),2* sizeof(double));
    memcpy(cheby[5], ((double []){75.0}),1* sizeof(double));
    memcpy(hulls_left_side[5], ((double []){-1.0,1.0}),2* sizeof(double));
    memcpy(hulls_right_side[5], ((double []){-74.0,76.0}),2* sizeof(double));
    memcpy(hull_cheby[5], ((double []){75.0}),1* sizeof(double));
    memcpy(left_side[6], ((double []){-1.0,1.0}),2* sizeof(double));
    memcpy(right_side[6], ((double []){-67.5,72.0}),2* sizeof(double));
    memcpy(cheby[6], ((double []){69.75}),1* sizeof(double));
    memcpy(hulls_left_side[6], ((double []){-1.0,1.0}),2* sizeof(double));
    memcpy(hulls_right_side[6], ((double []){-67.5,72.0}),2* sizeof(double));
    memcpy(hull_cheby[6], ((double []){69.75}),1* sizeof(double));
    memcpy(left_side[7], ((double []){-1.0,1.0}),2* sizeof(double));
    memcpy(right_side[7], ((double []){-65.0,67.5}),2* sizeof(double));
    memcpy(cheby[7], ((double []){66.25}),1* sizeof(double));
    memcpy(hulls_left_side[7], ((double []){-1.0,1.0}),2* sizeof(double));
    memcpy(hulls_right_side[7], ((double []){-65.0,67.5}),2* sizeof(double));
    memcpy(hull_cheby[7], ((double []){66.25}),1* sizeof(double));
    memcpy(left_side[8], ((double []){1.0,-1.0}),2* sizeof(double));
    memcpy(right_side[8], ((double []){85.0,-84.50000000000004}),2* sizeof(double));
    memcpy(cheby[8], ((double []){84.75000000000003}),1* sizeof(double));
    memcpy(hulls_left_side[8], ((double []){1.0,-1.0}),2* sizeof(double));
    memcpy(hulls_right_side[8], ((double []){85.0,-84.50000000000004}),2* sizeof(double));
    memcpy(hull_cheby[8], ((double []){84.75000000000003}),1* sizeof(double));
    memcpy(left_side[9], ((double []){-1.0,1.0}),2* sizeof(double));
    memcpy(right_side[9], ((double []){-60.0,60.49999999999999}),2* sizeof(double));
    memcpy(cheby[9], ((double []){60.25}),1* sizeof(double));
    memcpy(hulls_left_side[9], ((double []){-1.0,1.0}),2* sizeof(double));
    memcpy(hulls_right_side[9], ((double []){-60.0,60.49999999999999}),2* sizeof(double));
    memcpy(hull_cheby[9], ((double []){60.25}),1* sizeof(double));

    double **original_left_side = malloc(original_total_number_polytopes* sizeof(double));
    double **original_right_side = malloc(original_total_number_polytopes* sizeof(double));
    double **original_hulls_left_side = malloc(number_of_original_regions*sizeof(double));
    double **original_hulls_right_side = malloc(number_of_original_regions*sizeof(double));
    double **original_cheby = malloc(original_total_number_polytopes * sizeof(double*));
    double **original_hull_cheby = malloc(number_of_original_regions*sizeof(double*));
    for (int i = 0; i < original_total_number_polytopes; i++) {
        original_left_side[i] = malloc(original_polytope_sizes[i]* n * sizeof(double));
        original_right_side[i] = malloc(original_polytope_sizes[i] * sizeof(double));
        original_cheby[i] = malloc(n*sizeof(double));

    }
    for (int i = 0; i < number_of_original_regions; i++) {
        original_hulls_left_side[i] = malloc(original_hull_sizes[i]* n * sizeof(double));
        original_hulls_right_side[i] = malloc(original_hull_sizes[i] * sizeof(double));
        original_hull_cheby[i] = malloc(n*sizeof(double));

    }
    memcpy(original_left_side[0], ((double []){1.0,-1.0}),2* sizeof(double));
    memcpy(original_right_side[0], ((double []){85.0,-80.0}),2* sizeof(double));
    memcpy(original_cheby[0], ((double []){82.5}),1* sizeof(double));
    memcpy(original_hulls_left_side[0], ((double []){1.0,-1.0}),2* sizeof(double));
    memcpy(original_hulls_right_side[0], ((double []){85.0,-80.0}),2* sizeof(double));
    memcpy(original_hull_cheby[0], ((double []){82.5}),1* sizeof(double));
    memcpy(original_left_side[1], ((double []){1.0,-1.0}),2* sizeof(double));
    memcpy(original_right_side[1], ((double []){78.0,-76.0}),2* sizeof(double));
    memcpy(original_cheby[1], ((double []){77.0}),1* sizeof(double));
    memcpy(original_hulls_left_side[1], ((double []){1.0,-1.0}),2* sizeof(double));
    memcpy(original_hulls_right_side[1], ((double []){78.0,-76.0}),2* sizeof(double));
    memcpy(original_hull_cheby[1], ((double []){77.0}),1* sizeof(double));
    memcpy(original_left_side[2], ((double []){1.0,-1.0}),2* sizeof(double));
    memcpy(original_right_side[2], ((double []){74.0,-72.0}),2* sizeof(double));
    memcpy(original_cheby[2], ((double []){73.0}),1* sizeof(double));
    memcpy(original_hulls_left_side[2], ((double []){1.0,-1.0}),2* sizeof(double));
    memcpy(original_hulls_right_side[2], ((double []){74.0,-72.0}),2* sizeof(double));
    memcpy(original_hull_cheby[2], ((double []){73.0}),1* sizeof(double));
    memcpy(original_left_side[3], ((double []){1.0,-1.0}),2* sizeof(double));
    memcpy(original_right_side[3], ((double []){65.0,-60.0}),2* sizeof(double));
    memcpy(original_cheby[3], ((double []){62.5}),1* sizeof(double));
    memcpy(original_hulls_left_side[3], ((double []){1.0,-1.0}),2* sizeof(double));
    memcpy(original_hulls_right_side[3], ((double []){65.0,-60.0}),2* sizeof(double));
    memcpy(original_hull_cheby[3], ((double []){62.5}),1* sizeof(double));
    memcpy(original_left_side[4], ((double []){-1.0,1.0}),2* sizeof(double));
    memcpy(original_right_side[4], ((double []){-78.0,80.0}),2* sizeof(double));
    memcpy(original_cheby[4], ((double []){79.0}),1* sizeof(double));
    memcpy(original_left_side[5], ((double []){-1.0,1.0}),2* sizeof(double));
    memcpy(original_right_side[5], ((double []){-74.0,76.0}),2* sizeof(double));
    memcpy(original_cheby[5], ((double []){75.0}),1* sizeof(double));
    memcpy(original_left_side[6], ((double []){-1.0,1.0}),2* sizeof(double));
    memcpy(original_right_side[6], ((double []){-65.0,72.0}),2* sizeof(double));
    memcpy(original_cheby[6], ((double []){68.5}),1* sizeof(double));
    memcpy(original_hulls_left_side[4], ((double []){-1.0,1.0}),2* sizeof(double));
    memcpy(original_hulls_right_side[4], ((double []){-65.0,80.0}),2* sizeof(double));
    memcpy(original_hull_cheby[4], ((double []){72.5}),1* sizeof(double));

    int polytope_count = 0;
    for(int i = 0; i< abstract_states_count; i++){
        for(int j = 0; j< d_dyn->abstract_states_set[i]->cells_count; j++){
            polytope_from_arrays(d_dyn->abstract_states_set[i]->cells[j]->polytope_description,left_side[j+polytope_count],right_side[j+polytope_count], cheby[j+polytope_count],"d_dyn->abstract_states_set[i]->cells[j]");
        }
        polytope_count +=d_dyn->abstract_states_set[i]->cells_count;
        polytope_from_arrays(d_dyn->abstract_states_set[i]->convex_hull,hulls_left_side[i],hulls_right_side[i], hull_cheby[i], "d_dyn->abstract_states_set[i]->convex_hull" );
    }

    d_dyn->abstract_states_set[0]->transitions_in_count = 1;
    d_dyn->abstract_states_set[0]->transitions_in[0] = d_dyn->abstract_states_set[9];
    d_dyn->abstract_states_set[1]->transitions_in_count = 1;
    d_dyn->abstract_states_set[1]->transitions_in[0] = d_dyn->abstract_states_set[0];
    d_dyn->abstract_states_set[2]->transitions_in_count = 2;
    d_dyn->abstract_states_set[2]->transitions_in[0] = d_dyn->abstract_states_set[0];
    d_dyn->abstract_states_set[2]->transitions_in[1] = d_dyn->abstract_states_set[9];
    d_dyn->abstract_states_set[3]->transitions_in_count = 3;
    d_dyn->abstract_states_set[3]->transitions_in[0] = d_dyn->abstract_states_set[1];
    d_dyn->abstract_states_set[3]->transitions_in[1] = d_dyn->abstract_states_set[2];
    d_dyn->abstract_states_set[3]->transitions_in[2] = d_dyn->abstract_states_set[9];
    d_dyn->abstract_states_set[4]->transitions_in_count = 4;
    d_dyn->abstract_states_set[4]->transitions_in[0] = d_dyn->abstract_states_set[3];
    d_dyn->abstract_states_set[4]->transitions_in[1] = d_dyn->abstract_states_set[5];
    d_dyn->abstract_states_set[4]->transitions_in[2] = d_dyn->abstract_states_set[7];
    d_dyn->abstract_states_set[4]->transitions_in[3] = d_dyn->abstract_states_set[8];
    d_dyn->abstract_states_set[5]->transitions_in_count = 2;
    d_dyn->abstract_states_set[5]->transitions_in[0] = d_dyn->abstract_states_set[3];
    d_dyn->abstract_states_set[5]->transitions_in[1] = d_dyn->abstract_states_set[9];
    d_dyn->abstract_states_set[6]->transitions_in_count = 2;
    d_dyn->abstract_states_set[6]->transitions_in[0] = d_dyn->abstract_states_set[4];
    d_dyn->abstract_states_set[6]->transitions_in[1] = d_dyn->abstract_states_set[6];
    d_dyn->abstract_states_set[7]->transitions_in_count = 3;
    d_dyn->abstract_states_set[7]->transitions_in[0] = d_dyn->abstract_states_set[4];
    d_dyn->abstract_states_set[7]->transitions_in[1] = d_dyn->abstract_states_set[6];
    d_dyn->abstract_states_set[7]->transitions_in[2] = d_dyn->abstract_states_set[9];
    d_dyn->abstract_states_set[8]->transitions_in_count = 2;
    d_dyn->abstract_states_set[8]->transitions_in[0] = d_dyn->abstract_states_set[1];
    d_dyn->abstract_states_set[8]->transitions_in[1] = d_dyn->abstract_states_set[9];
    d_dyn->abstract_states_set[9]->transitions_in_count = 0;
    d_dyn->abstract_states_set[0]->transitions_out_count = 2;
    d_dyn->abstract_states_set[0]->transitions_out[0] = d_dyn->abstract_states_set[1];
    d_dyn->abstract_states_set[0]->transitions_out[1] = d_dyn->abstract_states_set[2];
    d_dyn->abstract_states_set[1]->transitions_out_count = 2;
    d_dyn->abstract_states_set[1]->transitions_out[0] = d_dyn->abstract_states_set[3];
    d_dyn->abstract_states_set[1]->transitions_out[1] = d_dyn->abstract_states_set[8];
    d_dyn->abstract_states_set[2]->transitions_out_count = 1;
    d_dyn->abstract_states_set[2]->transitions_out[0] = d_dyn->abstract_states_set[3];
    d_dyn->abstract_states_set[3]->transitions_out_count = 2;
    d_dyn->abstract_states_set[3]->transitions_out[0] = d_dyn->abstract_states_set[4];
    d_dyn->abstract_states_set[3]->transitions_out[1] = d_dyn->abstract_states_set[5];
    d_dyn->abstract_states_set[4]->transitions_out_count = 2;
    d_dyn->abstract_states_set[4]->transitions_out[0] = d_dyn->abstract_states_set[6];
    d_dyn->abstract_states_set[4]->transitions_out[1] = d_dyn->abstract_states_set[7];
    d_dyn->abstract_states_set[5]->transitions_out_count = 1;
    d_dyn->abstract_states_set[5]->transitions_out[0] = d_dyn->abstract_states_set[4];
    d_dyn->abstract_states_set[6]->transitions_out_count = 2;
    d_dyn->abstract_states_set[6]->transitions_out[0] = d_dyn->abstract_states_set[6];
    d_dyn->abstract_states_set[6]->transitions_out[1] = d_dyn->abstract_states_set[7];
    d_dyn->abstract_states_set[7]->transitions_out_count = 1;
    d_dyn->abstract_states_set[7]->transitions_out[0] = d_dyn->abstract_states_set[4];
    d_dyn->abstract_states_set[8]->transitions_out_count = 1;
    d_dyn->abstract_states_set[8]->transitions_out[0] = d_dyn->abstract_states_set[4];
    d_dyn->abstract_states_set[9]->transitions_out_count = 6;
    d_dyn->abstract_states_set[9]->transitions_out[0] = d_dyn->abstract_states_set[0];
    d_dyn->abstract_states_set[9]->transitions_out[1] = d_dyn->abstract_states_set[2];
    d_dyn->abstract_states_set[9]->transitions_out[2] = d_dyn->abstract_states_set[3];
    d_dyn->abstract_states_set[9]->transitions_out[3] = d_dyn->abstract_states_set[5];
    d_dyn->abstract_states_set[9]->transitions_out[4] = d_dyn->abstract_states_set[7];
    d_dyn->abstract_states_set[9]->transitions_out[5] = d_dyn->abstract_states_set[8];

    int original_polytope_count = 0;
    for(int i = 0; i< number_of_original_regions; i++){
        for(int j = 0; j< d_dyn->original_regions[i]->cells_count; j++){
            polytope_from_arrays(d_dyn->original_regions[i]->cells[j]->polytope_description ,original_left_side[j+original_polytope_count],original_right_side[j+original_polytope_count], original_cheby[j+original_polytope_count], "d_dyn->original_regions[i]->cells[j]");
        }
        original_polytope_count +=d_dyn->original_regions[i]->cells_count;
        polytope_from_arrays(d_dyn->original_regions[i]->convex_hull, original_hulls_left_side[i],original_hulls_right_side[i], original_hull_cheby[i],"d_dyn->original_regions[i]->convex_hull" );
    }
    //Clean up!
    for (int i = 0; i < total_number_polytopes; i++) {
        free(left_side[i]);
        free(right_side[i]);
        free(cheby[i]);
    }
    for (int i = 0; i < abstract_states_count; i++) {
        free(hulls_left_side[i]);
        free(hulls_right_side[i]);
        free(hull_cheby[i]);
    }
    for (int i = 0; i < original_total_number_polytopes; i++) {
        free(original_left_side[i]);
        free(original_right_side[i]);
        free(original_cheby[i]);
    }
    for (int i = 0; i < number_of_original_regions; i++) {
        free(original_hulls_left_side[i]);
        free(original_hulls_right_side[i]);
        free(original_hull_cheby[i]);
    }
    free(polytope_sizes);
    free(hull_sizes);
    free(left_side);
    free(right_side);
    free(cheby);
    free(hulls_left_side);
    free(hulls_right_side);
    free(hull_cheby);
    free(original_polytope_sizes);
    free(original_hull_sizes);
    free(original_left_side);
    free(original_right_side);
    free(original_cheby);
    free(original_hulls_left_side);
    free(original_hulls_right_side);
    free(original_hull_cheby);

}
