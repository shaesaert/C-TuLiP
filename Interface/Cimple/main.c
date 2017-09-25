
#include <stdio.h>
#include "find_controller.h"
void ACT_1(current_state * now, discrete_dynamics * d_dyn, system_dynamics * s_dyn, cost_function * f_cost){
    int target_cell =1;
    printf("Computing control sequence to go from cell %d to cell 1...", (*now).current_cell);
    fflush(stdout);

    gsl_matrix * u = gsl_matrix_alloc(now->x->size, d_dyn->time_horizon);
    get_input(u, now, d_dyn, s_dyn, target_cell, f_cost);
    printf("Applying it...");
    fflush(stdout);
    apply_control(now->x, u, s_dyn->A, s_dyn->B);
    printf("New state:");
    gsl_vector_print(now->x, "now->");
    fflush(stdout);
    // Clean up!
    gsl_matrix_free(u);
}
void ACT_2(current_state * now, discrete_dynamics * d_dyn, system_dynamics * s_dyn, cost_function * f_cost){
    int target_cell =2;
    printf("Computing control sequence to go from cell %d to cell 2...", (*now).current_cell);
    fflush(stdout);

    gsl_matrix * u = gsl_matrix_alloc(now->x->size, d_dyn->time_horizon);
    get_input(u, now, d_dyn, s_dyn, target_cell, f_cost);
    printf("Applying it...");
    fflush(stdout);
    apply_control(now->x, u, s_dyn->A, s_dyn->B);
    printf("New state:");
    gsl_vector_print(now->x, "now->");
    fflush(stdout);
    // Clean up!
    gsl_matrix_free(u);
}
void ACT_3(current_state * now, discrete_dynamics * d_dyn, system_dynamics * s_dyn, cost_function * f_cost){
    int target_cell =3;
    printf("Computing control sequence to go from cell %d to cell 3...", (*now).current_cell);
    fflush(stdout);

    gsl_matrix * u = gsl_matrix_alloc(now->x->size, d_dyn->time_horizon);
    get_input(u, now, d_dyn, s_dyn, target_cell, f_cost);
    printf("Applying it...");
    fflush(stdout);
    apply_control(now->x, u, s_dyn->A, s_dyn->B);
    printf("New state:");
    gsl_vector_print(now->x, "now->");
    fflush(stdout);
    // Clean up!
    gsl_matrix_free(u);
}
void ACT_8(current_state * now, discrete_dynamics * d_dyn, system_dynamics * s_dyn, cost_function * f_cost){
    int target_cell =8;
    printf("Computing control sequence to go from cell %d to cell 8...", (*now).current_cell);
    fflush(stdout);

    gsl_matrix * u = gsl_matrix_alloc(now->x->size, d_dyn->time_horizon);
    get_input(u, now, d_dyn, s_dyn, target_cell, f_cost);
    printf("Applying it...");
    fflush(stdout);
    apply_control(now->x, u, s_dyn->A, s_dyn->B);
    printf("New state:");
    gsl_vector_print(now->x, "now->");
    fflush(stdout);
    // Clean up!
    gsl_matrix_free(u);
}
void ACT_4(current_state * now, discrete_dynamics * d_dyn, system_dynamics * s_dyn, cost_function * f_cost){
    int target_cell =4;
    printf("Computing control sequence to go from cell %d to cell 4...", (*now).current_cell);
    fflush(stdout);

    gsl_matrix * u = gsl_matrix_alloc(now->x->size, d_dyn->time_horizon);
    get_input(u, now, d_dyn, s_dyn, target_cell, f_cost);
    printf("Applying it...");
    fflush(stdout);
    apply_control(now->x, u, s_dyn->A, s_dyn->B);
    printf("New state:");
    gsl_vector_print(now->x, "now->");
    fflush(stdout);
    // Clean up!
    gsl_matrix_free(u);
}
void ACT_5(current_state * now, discrete_dynamics * d_dyn, system_dynamics * s_dyn, cost_function * f_cost){
    int target_cell =5;
    printf("Computing control sequence to go from cell %d to cell 5...", (*now).current_cell);
    fflush(stdout);

    gsl_matrix * u = gsl_matrix_alloc(now->x->size, d_dyn->time_horizon);
    get_input(u, now, d_dyn, s_dyn, target_cell, f_cost);
    printf("Applying it...");
    fflush(stdout);
    apply_control(now->x, u, s_dyn->A, s_dyn->B);
    printf("New state:");
    gsl_vector_print(now->x, "now->");
    fflush(stdout);
    // Clean up!
    gsl_matrix_free(u);
}
void ACT_6(current_state * now, discrete_dynamics * d_dyn, system_dynamics * s_dyn, cost_function * f_cost){
    int target_cell =6;
    printf("Computing control sequence to go from cell %d to cell 6...", (*now).current_cell);
    fflush(stdout);

    gsl_matrix * u = gsl_matrix_alloc(now->x->size, d_dyn->time_horizon);
    get_input(u, now, d_dyn, s_dyn, target_cell, f_cost);
    printf("Applying it...");
    fflush(stdout);
    apply_control(now->x, u, s_dyn->A, s_dyn->B);
    printf("New state:");
    gsl_vector_print(now->x, "now->");
    fflush(stdout);
    // Clean up!
    gsl_matrix_free(u);
}
void ACT_7(current_state * now, discrete_dynamics * d_dyn, system_dynamics * s_dyn, cost_function * f_cost){
    int target_cell =7;
    printf("Computing control sequence to go from cell %d to cell 7...", (*now).current_cell);
    fflush(stdout);

    gsl_matrix * u = gsl_matrix_alloc(now->x->size, d_dyn->time_horizon);
    get_input(u, now, d_dyn, s_dyn, target_cell, f_cost);
    printf("Applying it...");
    fflush(stdout);
    apply_control(now->x, u, s_dyn->A, s_dyn->B);
    printf("New state:");
    gsl_vector_print(now->x, "now->");
    fflush(stdout);
    // Clean up!
    gsl_matrix_free(u);
}
void ACT_0(current_state * now, discrete_dynamics * d_dyn, system_dynamics * s_dyn, cost_function * f_cost){
    int target_cell =0;
    printf("Computing control sequence to go from cell %d to cell 0...", (*now).current_cell);
    fflush(stdout);

    gsl_matrix * u = gsl_matrix_alloc(now->x->size, d_dyn->time_horizon);
    get_input(u, now, d_dyn, s_dyn, target_cell, f_cost);
    printf("Applying it...");
    fflush(stdout);
    apply_control(now->x, u, s_dyn->A, s_dyn->B);
    printf("New state:");
    gsl_vector_print(now->x, "now->");
    fflush(stdout);
    // Clean up!
    gsl_matrix_free(u);
}

int main(){

    //Set help variables
    size_t time_horizon = 5;
    int initial_cell = 1;
    int number_of_regions= 10;
    int number_of_original_regions= 5;
    int closed_loop = 1;
    int conservative = 1;
    int ord =2;
    size_t n =1;
    size_t m =1;
    size_t p =1;
    size_t d_ext_i = 5;
    size_t d_ext_j = 32;
    size_t d_one_i = 1;
    size_t d_one_j = 2;
    size_t u_set_size =2;
    size_t w_set_size =2;
    double distance_weight =3;

    double *initial_state = malloc(n* sizeof (double));

    // Initialize state:
    current_state *now = state_alloc(n,initial_cell);
    gsl_vector_from_array(now->x, initial_state, "now->x");

    //Clean up!
    free(initial_state);

    // Transform system dynamics from python to C
    system_dynamics *s_dyn = system_dynamics_alloc(n, m, p, w_set_size, u_set_size, time_horizon, d_ext_i, d_ext_j, d_one_i, d_one_j);
    double *sys_A = malloc(n* n* sizeof (double));
    memcpy(sys_A, (double []){1.0},1* sizeof(double));
    gsl_matrix_from_array(s_dyn->A, sys_A, "s_dyn->A");
    free(sys_A);
    double *sys_B = malloc(n* m* sizeof (double));
    memcpy(sys_B, (double []){1.0},1* sizeof(double));
    gsl_matrix_from_array(s_dyn->B, sys_B,"s_dyn->B");
    free(sys_B);
    double *sys_E = malloc(n* p* sizeof (double));
    memcpy(sys_E, (double []){1.0},1* sizeof(double));
    gsl_matrix_from_array(s_dyn->E, sys_E, "s_dyn->E");
    free(sys_E);
    double *sys_K = malloc(n* sizeof (double));
    memcpy(sys_K, (double []){0.0},1* sizeof(double));
    gsl_vector_from_array(s_dyn->K, sys_K, "s_dyn->K");
    free(sys_K);
    double *sys_USetH = malloc(u_set_size* n* sizeof (double));
    memcpy(sys_USetH, (double []){1.0,-1.0},2* sizeof(double));
    gsl_matrix_from_array(s_dyn->U_set->H, sys_USetH, "s_dyn->U_set->H");
    free(sys_USetH);
    double *sys_WSetH = malloc(w_set_size* n* sizeof (double));
    memcpy(sys_WSetH, (double []){1.0,-1.0},2* sizeof(double));
    gsl_matrix_from_array(s_dyn->W_set->H, sys_WSetH,"s_dyn->W_set->H");
    free(sys_WSetH);
    double *sys_USetG = malloc(u_set_size* sizeof (double));
    memcpy(sys_USetG, (double []){1.0,1.0},2* sizeof(double));
    gsl_vector_from_array(s_dyn->U_set->G, sys_USetG, "s_dyn->U_set->G");
    free(sys_USetG);
    double *sys_WSetG = malloc(w_set_size* sizeof (double));
    memcpy(sys_WSetG, (double []){0.1,0.1},2* sizeof(double));
    gsl_vector_from_array(s_dyn->W_set->G, sys_WSetG, "s_dyn->W_set->G");
    free(sys_WSetG);
    double *sys_help_A_k = malloc(n* n*time_horizon* sizeof (double));
    memcpy(sys_help_A_k, (double []){1.0,1.0,1.0,1.0,1.0},5* sizeof(double));
    gsl_matrix_from_array(s_dyn->helper_functions->A_K, sys_help_A_k, "s_dyn->helper_functions->A_K");
    free(sys_help_A_k);
    double *sys_help_A_n = malloc(n* n* sizeof (double));
    memcpy(sys_help_A_n, (double []){1.0},1* sizeof(double));
    gsl_matrix_from_array(s_dyn->helper_functions->A_N, sys_help_A_n, "s_dyn->helper_functions->A_N");
    free(sys_help_A_n);
    double *sys_help_A_K_2 = malloc(n* time_horizon * n * time_horizon* sizeof (double));
    memcpy(sys_help_A_K_2, (double []){1.0,0.0,0.0,0.0,0.0,1.0,1.0,0.0,0.0,0.0,1.0,1.0,1.0,0.0,0.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0,1.0,1.0,1.0},25* sizeof(double));
    gsl_matrix_from_array(s_dyn->helper_functions->A_K_2, sys_help_A_K_2, "s_dyn->helper_functions->A_K_2");
    free(sys_help_A_K_2);
    double *sys_help_A_N_2 = malloc(n* time_horizon * n * sizeof (double));
    memcpy(sys_help_A_N_2, (double []){1.0,1.0,1.0,1.0,1.0},5* sizeof(double));
    gsl_matrix_from_array(s_dyn->helper_functions->A_N_2, sys_help_A_N_2, "s_dyn->helper_functions->A_N_2");
    free(sys_help_A_N_2);
    double *sys_help_E_diag = malloc(n*time_horizon* p*time_horizon* sizeof (double));
    memcpy(sys_help_E_diag, (double []){1.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0},25* sizeof(double));
    gsl_matrix_from_array(s_dyn->helper_functions->E_diag, sys_help_E_diag, "s_dyn->helper_functions->E_diag");
    free(sys_help_E_diag);
    double *sys_help_B_diag = malloc(n*time_horizon* m*time_horizon* sizeof (double));
    memcpy(sys_help_B_diag, (double []){1.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0},25* sizeof(double));
    gsl_matrix_from_array(s_dyn->helper_functions->B_diag, sys_help_B_diag, "s_dyn->helper_functions->B_diag");
    free(sys_help_B_diag);
    double *sys_help_K_hat = malloc(n* time_horizon* sizeof (double));
    memcpy(sys_help_K_hat, (double []){0.0,0.0,0.0,0.0,0.0},5* sizeof(double));
    gsl_vector_from_array(s_dyn->helper_functions->K_hat, sys_help_K_hat, "s_dyn->helper_functions->K_hat");
    free(sys_help_K_hat);
    double *sys_help_D_vertices = malloc(d_ext_i* d_ext_j* sizeof(double));
    memcpy(sys_help_D_vertices, (double []){0.1,-0.1,0.1,-0.1,0.1,-0.1,0.1,-0.1,0.1,-0.1,0.1,-0.1,0.1,-0.1,0.1,-0.1,0.1,-0.1,0.1,-0.1,0.1,-0.1,0.1,-0.1,0.1,-0.1,0.1,-0.1,0.1,-0.1,0.1,-0.1,0.1,0.1,-0.1,-0.1,0.1,0.1,-0.1,-0.1,0.1,0.1,-0.1,-0.1,0.1,0.1,-0.1,-0.1,0.1,0.1,-0.1,-0.1,0.1,0.1,-0.1,-0.1,0.1,0.1,-0.1,-0.1,0.1,0.1,-0.1,-0.1,0.1,0.1,0.1,0.1,-0.1,-0.1,-0.1,-0.1,0.1,0.1,0.1,0.1,-0.1,-0.1,-0.1,-0.1,0.1,0.1,0.1,0.1,-0.1,-0.1,-0.1,-0.1,0.1,0.1,0.1,0.1,-0.1,-0.1,-0.1,-0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1},160* sizeof(double));
    gsl_matrix_from_array(s_dyn->helper_functions->D_vertices, sys_help_D_vertices, "s_dyn->helper_functions->D_vertices");
    free(sys_help_D_vertices);
    double *sys_help_D_one_step = malloc(d_one_i* d_one_j* sizeof(double));
    memcpy(sys_help_D_one_step, (double []){0.1,-0.1},2* sizeof(double));
    gsl_matrix_from_array(s_dyn->helper_functions->D_one_step, sys_help_D_one_step,"s_dyn->helper_functions->D_one_step");
    free(sys_help_D_one_step);
    double *sys_help_L_default = malloc(n*time_horizon * (n+m*(time_horizon))* sizeof (double));
    memcpy(sys_help_L_default, (double []){1.0,0.0,0.0,0.0,0.0,0.0,1.0,1.0,0.0,0.0,0.0,0.0,1.0,1.0,1.0,0.0,0.0,0.0,1.0,1.0,1.0,1.0,0.0,0.0,1.0,1.0,1.0,1.0,1.0,0.0},30* sizeof(double));
    gsl_matrix_from_array(s_dyn->helper_functions->L_default, sys_help_L_default, "s_dyn->helper_functions->L_default");
    free(sys_help_L_default);
    double *sys_help_E_default = malloc(n* time_horizon* p* time_horizon* sizeof (double));
    memcpy(sys_help_E_default, (double []){0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,1.0,1.0,0.0,0.0,0.0,1.0,1.0,1.0,0.0,0.0,1.0,1.0,1.0,1.0,0.0},25* sizeof(double));
    gsl_matrix_from_array(s_dyn->helper_functions->E_default, sys_help_E_default, "s_dyn->helper_functions->E_default");
    free(sys_help_E_default);
    double *sys_help_Ct = malloc(n*time_horizon*m*time_horizon*sizeof(double));
    memcpy(sys_help_Ct, (double []){1.0,0.0,0.0,0.0,0.0,1.0,1.0,0.0,0.0,0.0,1.0,1.0,1.0,0.0,0.0,1.0,1.0,1.0,1.0,0.0,1.0,1.0,1.0,1.0,1.0},25* sizeof(double));
    gsl_matrix_from_array(s_dyn->helper_functions->Ct, sys_help_Ct, "s_dyn->helper_functions->Ct");
    free(sys_help_Ct);
    double *sys_help_MU = malloc(u_set_size*time_horizon * sizeof(double));
    memcpy(sys_help_MU, (double []){1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0},10* sizeof(double));
    gsl_vector_from_array(s_dyn->helper_functions->MU, sys_help_MU, "s_dyn->helper_functions->MU");
    free(sys_help_MU);
    double *sys_help_GU = malloc(u_set_size*time_horizon* p*time_horizon* sizeof(double));
    memcpy(sys_help_GU, (double []){0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0},50* sizeof(double));
    gsl_matrix_from_array(s_dyn->helper_functions->GU, sys_help_GU,"s_dyn->helper_functions->GU");
    free(sys_help_GU);
    double *sys_help_LU = malloc(u_set_size*time_horizon * (n+m*(time_horizon))* sizeof (double));
    memcpy(sys_help_LU, (double []){0.0,1.0,0.0,0.0,0.0,0.0,0.0,-1.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,-1.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,-1.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,-1.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,-1.0},60* sizeof(double));
    gsl_matrix_from_array(s_dyn->helper_functions->LU, sys_help_LU, "s_dyn->helper_functions->LU");
    free(sys_help_LU);

    // Set cost function
    cost_function *f_cost = cost_function_alloc(n, m, time_horizon, distance_weight);
    double *cf_R = malloc(n* time_horizon* n* time_horizon* sizeof (double));
    memcpy(cf_R, (double []){0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0},25* sizeof(double));
    gsl_matrix_from_array(f_cost->R, cf_R, "f_cost->R");
    free(cf_R);
    double *cf_Q = malloc(m* time_horizon* m* time_horizon* sizeof (double));
    memcpy(cf_Q, (double []){1.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0},25* sizeof(double));
    gsl_matrix_from_array(f_cost->Q, cf_Q, "f_cost->Q");
    free(cf_Q);
    double *cf_r = malloc(n* time_horizon* sizeof (double));
    memcpy(cf_r, (double []){0.0,0.0,0.0,0.0,0.0},5* sizeof(double));
    gsl_vector_from_array(f_cost->r, cf_r, "f_cost->r");
    free(cf_r);

    size_t total_number_polytopes = 10;
    int polytopes_in_region[10] = {1,1,1,1,1,1,1,1,1,1};
    size_t original_total_number_polytopes = 7;
    int orig_polytopes_in_region[5] = {1,1,1,1,3};

    size_t *polytope_sizes= malloc(total_number_polytopes * sizeof(size_t));
    size_t *hull_sizes= malloc(number_of_regions * sizeof(size_t));
    size_t *original_polytope_sizes= malloc(original_total_number_polytopes * sizeof(size_t));
    size_t *original_hull_sizes= malloc(number_of_original_regions * sizeof(size_t));
    memcpy(polytope_sizes, (size_t []){2,2,2,2,2,2,2,2,2,2},10* sizeof(polytope_sizes[0]));
    memcpy(hull_sizes, (size_t []){2,2,2,2,2,2,2,2,2,2},10* sizeof(hull_sizes[0]));
    memcpy(original_polytope_sizes, (size_t []){2,2,2,2,2,2,2},7* sizeof(original_polytope_sizes[0]));
    memcpy(original_hull_sizes, (size_t []){2,2,2,2,2},5* sizeof(original_hull_sizes[0]));

    double **left_side = malloc(total_number_polytopes* sizeof(double*));
    double **right_side = malloc(total_number_polytopes* sizeof(double*));
    double **hulls_left_side = malloc(number_of_regions*sizeof(double*));
    double **hulls_right_side = malloc(number_of_regions*sizeof(double*));
    for (int i = 0; i < total_number_polytopes; i++) {
        left_side[i] = malloc(polytope_sizes[i]* n * sizeof(double));
        right_side[i] = malloc(polytope_sizes[i] * sizeof(double));

    }
    for (int i = 0; i < number_of_regions; i++) {
        hulls_left_side[i] = malloc(hull_sizes[i]* n * sizeof(double));
        hulls_right_side[i] = malloc(hull_sizes[i] * sizeof(double));

    }
    memcpy(left_side[0], (double []){1.0,-1.0},2* sizeof(double));
    memcpy(right_side[0], (double []){84.50000000000004,-80.0},2* sizeof(double));
    memcpy(hulls_left_side[0], (double []){1.0,-1.0},2* sizeof(double));
    memcpy(hulls_right_side[0], (double []){84.50000000000004,-80.0},2* sizeof(double));
    memcpy(left_side[1], (double []){1.0,-1.0},2* sizeof(double));
    memcpy(right_side[1], (double []){78.0,-76.0},2* sizeof(double));
    memcpy(hulls_left_side[1], (double []){1.0,-1.0},2* sizeof(double));
    memcpy(hulls_right_side[1], (double []){78.0,-76.0},2* sizeof(double));
    memcpy(left_side[2], (double []){1.0,-1.0},2* sizeof(double));
    memcpy(right_side[2], (double []){74.0,-72.0},2* sizeof(double));
    memcpy(hulls_left_side[2], (double []){1.0,-1.0},2* sizeof(double));
    memcpy(hulls_right_side[2], (double []){74.0,-72.0},2* sizeof(double));
    memcpy(left_side[3], (double []){-1.0,1.0},2* sizeof(double));
    memcpy(right_side[3], (double []){-60.49999999999999,65.0},2* sizeof(double));
    memcpy(hulls_left_side[3], (double []){-1.0,1.0},2* sizeof(double));
    memcpy(hulls_right_side[3], (double []){-60.49999999999999,65.0},2* sizeof(double));
    memcpy(left_side[4], (double []){-1.0,1.0},2* sizeof(double));
    memcpy(right_side[4], (double []){-78.0,80.0},2* sizeof(double));
    memcpy(hulls_left_side[4], (double []){-1.0,1.0},2* sizeof(double));
    memcpy(hulls_right_side[4], (double []){-78.0,80.0},2* sizeof(double));
    memcpy(left_side[5], (double []){-1.0,1.0},2* sizeof(double));
    memcpy(right_side[5], (double []){-74.0,76.0},2* sizeof(double));
    memcpy(hulls_left_side[5], (double []){-1.0,1.0},2* sizeof(double));
    memcpy(hulls_right_side[5], (double []){-74.0,76.0},2* sizeof(double));
    memcpy(left_side[6], (double []){-1.0,1.0},2* sizeof(double));
    memcpy(right_side[6], (double []){-67.5,72.0},2* sizeof(double));
    memcpy(hulls_left_side[6], (double []){-1.0,1.0},2* sizeof(double));
    memcpy(hulls_right_side[6], (double []){-67.5,72.0},2* sizeof(double));
    memcpy(left_side[7], (double []){-1.0,1.0},2* sizeof(double));
    memcpy(right_side[7], (double []){-65.0,67.5},2* sizeof(double));
    memcpy(hulls_left_side[7], (double []){-1.0,1.0},2* sizeof(double));
    memcpy(hulls_right_side[7], (double []){-65.0,67.5},2* sizeof(double));
    memcpy(left_side[8], (double []){1.0,-1.0},2* sizeof(double));
    memcpy(right_side[8], (double []){85.0,-84.50000000000004},2* sizeof(double));
    memcpy(hulls_left_side[8], (double []){1.0,-1.0},2* sizeof(double));
    memcpy(hulls_right_side[8], (double []){85.0,-84.50000000000004},2* sizeof(double));
    memcpy(left_side[9], (double []){-1.0,1.0},2* sizeof(double));
    memcpy(right_side[9], (double []){-60.0,60.49999999999999},2* sizeof(double));
    memcpy(hulls_left_side[9], (double []){-1.0,1.0},2* sizeof(double));
    memcpy(hulls_right_side[9], (double []){-60.0,60.49999999999999},2* sizeof(double));

    double **original_left_side = malloc(original_total_number_polytopes* sizeof(double));
    double **original_right_side = malloc(original_total_number_polytopes* sizeof(double));
    double **original_hulls_left_side = malloc(number_of_original_regions*sizeof(double));
    double **original_hulls_right_side = malloc(number_of_original_regions*sizeof(double));
    for (int i = 0; i < original_total_number_polytopes; i++) {
        original_left_side[i] = malloc(original_polytope_sizes[i]* n * sizeof(double));
        original_right_side[i] = malloc(original_polytope_sizes[i] * sizeof(double));

    }
    for (int i = 0; i < number_of_original_regions; i++) {
        original_hulls_left_side[i] = malloc(original_hull_sizes[i]* n * sizeof(double));
        original_hulls_right_side[i] = malloc(original_hull_sizes[i] * sizeof(double));

    }
    memcpy(original_left_side[0], (double []){1.0,-1.0},2* sizeof(double));
    memcpy(original_right_side[0], (double []){85.0,-80.0},2* sizeof(double));
    memcpy(original_hulls_left_side[0], (double []){1.0,-1.0},2* sizeof(double));
    memcpy(original_hulls_right_side[0], (double []){85.0,-80.0},2* sizeof(double));
    memcpy(original_left_side[1], (double []){1.0,-1.0},2* sizeof(double));
    memcpy(original_right_side[1], (double []){78.0,-76.0},2* sizeof(double));
    memcpy(original_hulls_left_side[1], (double []){1.0,-1.0},2* sizeof(double));
    memcpy(original_hulls_right_side[1], (double []){78.0,-76.0},2* sizeof(double));
    memcpy(original_left_side[2], (double []){1.0,-1.0},2* sizeof(double));
    memcpy(original_right_side[2], (double []){74.0,-72.0},2* sizeof(double));
    memcpy(original_hulls_left_side[2], (double []){1.0,-1.0},2* sizeof(double));
    memcpy(original_hulls_right_side[2], (double []){74.0,-72.0},2* sizeof(double));
    memcpy(original_left_side[3], (double []){1.0,-1.0},2* sizeof(double));
    memcpy(original_right_side[3], (double []){65.0,-60.0},2* sizeof(double));
    memcpy(original_hulls_left_side[3], (double []){1.0,-1.0},2* sizeof(double));
    memcpy(original_hulls_right_side[3], (double []){65.0,-60.0},2* sizeof(double));
    memcpy(original_left_side[4], (double []){-1.0,1.0},2* sizeof(double));
    memcpy(original_right_side[4], (double []){-78.0,80.0},2* sizeof(double));
    memcpy(original_left_side[5], (double []){-1.0,1.0},2* sizeof(double));
    memcpy(original_right_side[5], (double []){-74.0,76.0},2* sizeof(double));
    memcpy(original_left_side[6], (double []){-1.0,1.0},2* sizeof(double));
    memcpy(original_right_side[6], (double []){-65.0,72.0},2* sizeof(double));
    memcpy(original_hulls_left_side[4], (double []){1.0,-1.0},2* sizeof(double));
    memcpy(original_hulls_right_side[4], (double []){80.0,-65.0},2* sizeof(double));

    discrete_dynamics *d_dyn = discrete_dynamics_alloc(polytopes_in_region, polytope_sizes,  hull_sizes, orig_polytopes_in_region, original_polytope_sizes, original_hull_sizes, n, number_of_regions, number_of_original_regions, closed_loop, conservative, ord, time_horizon);


    int polytope_count = 0;
    for(int i = 0; i< number_of_regions; i++){
        for(int j = 0; j< d_dyn->regions[i]->number_of_polytopes; j++){
            polytope_from_arrays(d_dyn->regions[i]->polytopes[j],polytope_sizes[j+polytope_count] ,n,left_side[j+polytope_count],right_side[j+polytope_count],"d_dyn->regions[i]->polytopes[j]");
        }
        polytope_count +=d_dyn->regions[i]->number_of_polytopes;
        polytope_from_arrays(d_dyn->regions[i]->hull_of_region,hull_sizes[i],n,hulls_left_side[i],hulls_right_side[i],"d_dyn->regions[i]->hull_of_region" );
    }


    int original_polytope_count = 0;
    for(int i = 0; i< number_of_original_regions; i++){
        for(int j = 0; j< d_dyn->original_regions[i]->number_of_polytopes; j++){
            polytope_from_arrays(d_dyn->original_regions[i]->polytopes[j],original_polytope_sizes[j+original_polytope_count] ,n,original_left_side[j+original_polytope_count],original_right_side[j+original_polytope_count], "d_dyn->original_regions[i]->polytopes[j]");
        }
        polytope_from_arrays(d_dyn->original_regions[i]->hull_of_region,original_hull_sizes[i],n,original_hulls_left_side[i],original_hulls_right_side[i], "d_dyn->original_regions[i]->hull_of_region" );
    }
    //Clean up!
    for (int i = 0; i < total_number_polytopes; i++) {
        free(left_side[i]);
        free(right_side[i]);
    }
    for (int i = 0; i < number_of_regions; i++) {
        free(hulls_left_side[i]);
        free(hulls_right_side[i]);
    }
    for (int i = 0; i < original_total_number_polytopes; i++) {
        free(original_left_side[i]);
        free(original_right_side[i]);
    }
    for (int i = 0; i < number_of_original_regions; i++) {
        free(original_hulls_left_side[i]);
        free(original_hulls_right_side[i]);
    }
    free(polytope_sizes);
    free(hull_sizes);
    free(left_side);
    free(right_side);
    free(hulls_left_side);
    free(hulls_right_side);
    free(original_polytope_sizes);
    free(original_hull_sizes);
    free(original_left_side);
    free(original_right_side);
    free(original_hulls_left_side);
    free(original_hulls_right_side);

    ACT_0(now, d_dyn, s_dyn, f_cost);
    system_dynamics_free(s_dyn);
    discrete_dynamics_free(d_dyn, number_of_regions, number_of_original_regions);
    cost_function_free(f_cost);
    state_free(now);

}
