//
// Created by L.Jonathan Feldstein
//


#include <gsl/gsl_matrix.h>
#include "cimple_controller.h"

int main_computation_completed = 0;
//pthread_mutex_t poly_mutex = PTHREAD_MUTEX_INITIALIZER;
/**
 * "Constructor" Dynamically allocates the space for the get_input thread
 */
struct control_computation_arguments *cc_arguments_alloc(current_state *now, gsl_matrix* u, system_dynamics *s_dyn, discrete_dynamics *d_dyn, cost_function *f_cost, size_t current_time_horizon, int target_cell, polytope **polytope_list){

    struct control_computation_arguments *return_control_computation_arguments = malloc (sizeof (struct control_computation_arguments));

    return_control_computation_arguments->current_time_horizon =current_time_horizon;

    return_control_computation_arguments->target_cell = target_cell;

    return_control_computation_arguments->d_dyn = d_dyn;

    return_control_computation_arguments->f_cost = f_cost;

    return_control_computation_arguments->s_dyn = s_dyn;

    return_control_computation_arguments->now = now;

    return_control_computation_arguments->u = u;

    return_control_computation_arguments->polytope_list_backup = polytope_list;

    return return_control_computation_arguments;
};

/**
 * "Constructor" Dynamically allocates the space for the arguments of the safemode computation thread
 */
struct total_safemode_computation_arguments *sm_arguments_alloc(current_state *now, gsl_matrix * u, polytope *current, polytope *safe, system_dynamics * s_dyn, size_t time_horizon,cost_function *f_cost, polytope **polytope_list_safemode){

    struct total_safemode_computation_arguments *return_sm_arguments = malloc (sizeof (struct total_safemode_computation_arguments));

    return_sm_arguments->now = now;
    return_sm_arguments->u = u;
    return_sm_arguments->time_horizon = time_horizon;
    return_sm_arguments->current = current;
    return_sm_arguments->safe = safe;
    return_sm_arguments->s_dyn = s_dyn;
    return_sm_arguments->f_cost = f_cost;
    return_sm_arguments->polytope_list_backup = polytope_list_safemode;

    return return_sm_arguments;
};

/**
 * "Constructor" Dynamically allocates the space for the arguments of the next step towards safemode computation thread
 */
struct next_safemode_computation_arguments *next_sm_arguments_alloc(current_state *now, gsl_matrix * u, system_dynamics * s_dyn, size_t time_horizon,cost_function *f_cost, polytope **polytope_list_safemode){

    struct next_safemode_computation_arguments *return_sm_arguments = malloc (sizeof (struct next_safemode_computation_arguments));

    return_sm_arguments->now = now;
    return_sm_arguments->u = u;
    return_sm_arguments->time_horizon = time_horizon;
    return_sm_arguments->s_dyn = s_dyn;
    return_sm_arguments->f_cost = f_cost;
    return_sm_arguments->polytope_list_backup = polytope_list_safemode;

    return return_sm_arguments;
};

double randn (double mu, double sigma)
{
    double U1, U2, W, mult;
    static double X1, X2;
    static int call = 0;

    if (call == 1)
    {
        call = !call;
        return (mu + sigma * (double) X2);
    }

    do
    {
        U1 = -1 + ((double) rand () / RAND_MAX) * 2;
        U2 = -1 + ((double) rand () / RAND_MAX) * 2;
        W = pow (U1, 2) + pow (U2, 2);
    }
    while (W >= 1 || W == 0);

    mult = sqrt ((-2 * log (W)) / W);
    X1 = U1 * mult;
    X2 = U2 * mult;

    call = !call;

    return (mu + sigma * (double) X1);
}

void get_disturbance(gsl_vector *w, double mu, double sigma){
    for(size_t i = 0; i<w->size;i++){
        gsl_vector_set(w,i,randn(mu,sigma));
    }
};


void next_safemode_input(gsl_matrix *u, current_state *now, polytope *current, polytope *next, system_dynamics *s_dyn, cost_function *f_cost){

    size_t n = s_dyn->A->size1;
    size_t m = s_dyn->B->size2;
    gsl_matrix *constraintH = gsl_matrix_alloc(current->H->size1+next->H->size1+(s_dyn->U_set->H->size1), n+m);
    gsl_vector *constraintG = gsl_vector_alloc(current->H->size1+next->H->size1+(s_dyn->U_set->H->size1));
    gsl_matrix_set_zero(constraintH);
    gsl_vector_set_zero(constraintG);
    polytope **polytope_list= malloc(sizeof(polytope)*2);
    polytope_list[0] = polytope_alloc(current->H->size1,current->H->size2);
    gsl_matrix_memcpy(polytope_list[0]->H, current->H);
    gsl_vector_memcpy(polytope_list[0]->G, current->G);
    polytope_list[1] = polytope_alloc(next->H->size1,next->H->size2);
    gsl_matrix_memcpy(polytope_list[1]->H, next->H);
    gsl_vector_memcpy(polytope_list[1]->G, next->G);
    set_path_constraints(constraintH, constraintG, s_dyn, polytope_list, 1);
    for(int i = 0; i< 2; i++){
        polytope_free(polytope_list[i]);
    }
    free(polytope_list);

    // Remove first constraints on x(0) they are obviously already satisfied
    // L_x = L[{(polytope[0]+1),(dim_n(L))},{1,n}]
    gsl_matrix_view constraint_x = gsl_matrix_submatrix(constraintH, current->H->size1, 0, (constraintH->size1)-(current->H->size1), n);
    // L_u = L[{(polytope[0]+1),(dim_n(L))},{(n+1),(dim_m(L))}]
    gsl_matrix_view constraint_u = gsl_matrix_submatrix(constraintH, current->H->size1, n, (constraintH->size1)-(current->H->size1), constraintH->size2 - n);
    // M_view = M[{(polytope[0]+1),(dim_n(M))}]
    gsl_vector_view constraint_g = gsl_vector_subvector(constraintG, current->H->size1, constraintG->size-current->H->size1);

    //M = M-(L_x.x)
    gsl_vector * L_x_dot_X0 = gsl_vector_alloc((constraintH->size1)-(current->H->size1));
    gsl_blas_dgemv(CblasNoTrans, 1.0, &constraint_x.matrix, now->x, 0.0, L_x_dot_X0);
    gsl_vector_sub(&constraint_g.vector, L_x_dot_X0);
    //Clean up!
    gsl_vector_free(L_x_dot_X0);
    //Currently quadratic problem could be changed in future
    gsl_matrix * P = gsl_matrix_alloc(m, m);
    gsl_vector * q = gsl_vector_alloc(m);

    polytope *opt_constraints = set_cost_function(P, q, &constraint_u.matrix, &constraint_g.vector, now, s_dyn, f_cost, 1);
    double low_cost = INFINITY;

    compute_optimal_control_qp(u, &low_cost, P, q, opt_constraints, 1, n);
    if (low_cost == INFINITY){
        //raise Exception
        fprintf(stderr, "(safe_mode) Houston we have a problem: No trajectory found. System is going to crash.");
        exit(EXIT_FAILURE);
    }

};


void * timer(void * arg){
    struct timeval sec;
    double* total_time_p = (double*)arg;
    double total_time = *total_time_p;
    int seconds = (int)floor(total_time);
    int u_seconds;
    u_seconds = (int)floor(total_time * pow(10,6) - seconds * pow(10,6));
    sec.tv_sec = seconds;
    sec.tv_usec = u_seconds;
    printf("Time runs: %d.%d", (int)sec.tv_sec, (int)sec.tv_usec);
    select(0,NULL,NULL,NULL,&sec);
    pthread_exit(0);
};

void * main_computation(void *arg){


    control_computation_arguments *cc_arguments = (control_computation_arguments *)arg;
    long j = 0;
    for(long i=0;i<10000;i++){
        j=j+1;
    }

    get_input(cc_arguments->u, cc_arguments->now, cc_arguments->d_dyn, cc_arguments->s_dyn, cc_arguments->target_cell, cc_arguments->f_cost, cc_arguments->current_time_horizon, cc_arguments->polytope_list_backup);

    main_computation_completed = 1;


    pthread_exit(NULL);
};

void * total_safe_mode_computation(void *arg){


    total_safemode_computation_arguments *sm_arg = (total_safemode_computation_arguments *)arg;

    //Auxiliary variables
    size_t N = sm_arg->time_horizon;
    size_t n = sm_arg->s_dyn->A->size1;
    size_t m = sm_arg->s_dyn->B->size2;

    //Build list of polytopes that the state is going to be in in the next N time steps
    sm_arg->polytope_list_backup[0] = polytope_alloc(sm_arg->current->H->size1,sm_arg->current->H->size2);
    gsl_matrix_memcpy(sm_arg->polytope_list_backup[0]->H, sm_arg->current->H);
    gsl_vector_memcpy(sm_arg->polytope_list_backup[0]->G, sm_arg->current->G);
    sm_arg->polytope_list_backup[N] = polytope_alloc(sm_arg->safe->H->size1,sm_arg->safe->H->size2);
    gsl_matrix_memcpy(sm_arg->polytope_list_backup[N]->H, sm_arg->safe->H);
    gsl_vector_memcpy(sm_arg->polytope_list_backup[N]->G, sm_arg->safe->G);


    //check partition system is in after i time steps
    for (size_t i = N; i > 1; i--){
        poly_t *sm_polytope;

        //TODO: check if target polytope full dim
        matrix_t* constraints = matrix_alloc((int)sm_arg->current->H->size1+(int)sm_arg->polytope_list_backup[i]->H->size1+(int)sm_arg->s_dyn->U_set->H->size1, (int)n+(int)m+2,false);
        constraints = solve_feasible_closed_loop2(sm_arg->current, sm_arg->polytope_list_backup[i], sm_arg->s_dyn, constraints);
        //Project precedent polytope onto lower dim
        sm_polytope = poly_of_constraints(constraints);
        poly_print(sm_polytope);
        poly_t *reduced_sm_polytope = poly_remove_dimensions(sm_polytope, (int)m);

        poly_free(sm_polytope);
        poly_minimize(reduced_sm_polytope);

        sm_arg->polytope_list_backup[i-1] = polytope_alloc((size_t)reduced_sm_polytope->C->nbrows,n);

        polytope_from_constraints(sm_arg->polytope_list_backup[i-1], reduced_sm_polytope->C);
        poly_free(reduced_sm_polytope);

    }
    size_t time_step = sm_arg->time_horizon;
    for(size_t i = sm_arg->time_horizon+1; i>0; i--){
        if (polytope_check_state(sm_arg->polytope_list_backup[i-1], sm_arg->now->x)){
            time_step = i-1;
            break;
        }
    }
    //compute one safe step

    if(time_step !=sm_arg->time_horizon){
        next_safemode_input(sm_arg->u, sm_arg->now, sm_arg->polytope_list_backup[time_step], sm_arg->polytope_list_backup[time_step+1], sm_arg->s_dyn, sm_arg->f_cost);
    }else{
        gsl_matrix_set_zero(sm_arg->u);
    }

    pthread_exit(NULL);
};

void *next_safemode_computation(void *arg){
    next_safemode_computation_arguments *sm_arg = (next_safemode_computation_arguments *)arg;
    size_t time_step = sm_arg->time_horizon;
    for(size_t i = sm_arg->time_horizon; i>=0; i++){
        if (polytope_check_state(sm_arg->polytope_list_backup[i], sm_arg->now->x)){
            time_step = i;
            break;
        }
    }
    //compute one safe step
    if(time_step !=sm_arg->time_horizon){
        next_safemode_input(sm_arg->u, sm_arg->now, sm_arg->polytope_list_backup[time_step], sm_arg->polytope_list_backup[time_step+1], sm_arg->s_dyn, sm_arg->f_cost);
    }else{
        gsl_matrix_set_zero(sm_arg->u);
    }
    pthread_exit(0);
};
int check_backup(gsl_vector *x_real, gsl_vector *u, gsl_matrix *A, gsl_matrix *B, polytope *check_polytope){
    gsl_vector *x_test = gsl_vector_alloc(x_real->size);
    gsl_vector_memcpy(x_test, x_real);
    gsl_vector *x_temp = gsl_vector_alloc(x_test->size);

    gsl_vector *Btu = gsl_vector_alloc(x_test->size);
    //A.x
    gsl_blas_dgemv(CblasNoTrans, 1, A, x_test, 0, x_temp);
    //B.u
    gsl_blas_dgemv(CblasNoTrans, 1, B, u, 0 , Btu);
    //update x[k-1] => x[k]
    gsl_vector_set_zero(x_test);
    gsl_vector_add(x_test, x_temp);
    gsl_vector_add(x_test, Btu);
    gsl_vector_free(Btu);
    gsl_vector_free(x_temp);
    if(polytope_check_state(check_polytope,x_test)){

        gsl_vector_free(x_test);
        return 1;
    }else{

        gsl_vector_free(x_test);
        return 0;
    }

}
/**
 * Action to get plant from current cell to target cell.
 */
void ACT(int target,
         current_state * now,
         discrete_dynamics * d_dyn,
         system_dynamics * s_dyn,
         cost_function * f_cost,
         current_state * now2,
         discrete_dynamics * d_dyn2,
         system_dynamics * s_dyn2,
         cost_function * f_cost2,
         double sec){
    printf("Computing control sequence to go from cell %d to cell %d...", (*now).current_cell, target);
    fflush(stdout);
    //Setup threads and start timer

    gsl_matrix * u_backup = gsl_matrix_alloc(s_dyn->B->size2, d_dyn->time_horizon);
    gsl_matrix_set_zero(u_backup);
    polytope **polytope_list_backup = malloc(sizeof(polytope)*(d_dyn->time_horizon+1));
    polytope **polytope_list_safemode = malloc(sizeof(polytope)*(d_dyn->time_horizon+1));
    for(size_t i=0; i<d_dyn->time_horizon;i++){

        //Create timer thread
        pthread_t timer_id;
        pthread_create(&timer_id, NULL, timer, &sec);

        //Check whether backup is good


        size_t current_time_horizon = d_dyn->time_horizon-i;
        gsl_matrix_view u = gsl_matrix_submatrix(u_backup, 0, i, u_backup->size1, (u_backup->size2-i));
        int backup_applicable = 0;
        gsl_matrix *u_safemode = gsl_matrix_alloc(s_dyn->B->size2,1);
//        if(i != 0){
//            backup_applicable = check_backup(now->x, &u_last.vector ,s_dyn->A,s_dyn->B, polytope_list_backup[i]);
//        }
        if(backup_applicable){
            pthread_t main_computation_id;
            control_computation_arguments *cc_arguments = cc_arguments_alloc(now, &u.matrix, s_dyn, d_dyn,f_cost, current_time_horizon, target, polytope_list_backup);
            pthread_create(&main_computation_id, NULL, main_computation, (void*)cc_arguments);
            pthread_join(main_computation_id, NULL);
            free(cc_arguments);

        }else{
            if(i==0){
                pthread_t main_computation_id;
                pthread_t safe_mode_computation_id;
                polytope *current = polytope_alloc(d_dyn->regions[now->current_cell]->polytopes[0]->H->size1,d_dyn->regions[now->current_cell]->polytopes[0]->H->size2);
                gsl_matrix_memcpy(current->H, d_dyn->regions[now->current_cell]->polytopes[0]->H);
                gsl_vector_memcpy(current->G,d_dyn->regions[now->current_cell]->polytopes[0]->G);

                polytope *safe = polytope_alloc(d_dyn->regions[now->current_cell]->polytopes[0]->H->size1,d_dyn->regions[now->current_cell]->polytopes[0]->H->size2);
                gsl_matrix_memcpy(safe->H, d_dyn->regions[now->current_cell]->polytopes[0]->H);
                gsl_vector_memcpy(safe->G,d_dyn->regions[now->current_cell]->polytopes[0]->G);
//                for (int j = 0; j < d_dyn->regions[now->current_cell]->number_of_polytopes; j++) {
//                    if (polytope_check_state(d_dyn->regions[now->current_cell]->polytopes[j], now->x)){
//
//                        polytope *current = polytope_alloc(d_dyn->regions[now->current_cell]->polytopes[0]->H->size1,d_dyn->regions[now->current_cell]->polytopes[0]->H->size2);
//                        gsl_matrix_memcpy(current->H, d_dyn->regions[now->current_cell]->polytopes[0]->H);
//                        gsl_vector_memcpy(current->G,d_dyn->regions[now->current_cell]->polytopes[0]->G);
//
//                        polytope *safe = polytope_alloc(d_dyn->regions[now->current_cell]->polytopes[0]->H->size1,d_dyn->regions[now->current_cell]->polytopes[0]->H->size2);
//                        gsl_matrix_memcpy(safe->H, d_dyn->regions[now->current_cell]->polytopes[0]->H);
//                        gsl_vector_memcpy(safe->G,d_dyn->regions[now->current_cell]->polytopes[0]->G);
//                        break;
//                    }
//                }
                total_safemode_computation_arguments *total_sm_arguments = sm_arguments_alloc(now, u_safemode, current, safe, s_dyn, d_dyn->time_horizon, f_cost, polytope_list_safemode);
                pthread_create(&safe_mode_computation_id, NULL, total_safe_mode_computation, (void*)total_sm_arguments);

                control_computation_arguments *cc_arguments = cc_arguments_alloc(now2, &u.matrix, s_dyn2, d_dyn2,f_cost2, current_time_horizon, target, polytope_list_backup);
                pthread_create(&main_computation_id, NULL, main_computation, (void*)cc_arguments);
                pthread_join(safe_mode_computation_id, NULL);

                pthread_join(main_computation_id, NULL);
                polytope_free(safe);
                polytope_free(current);
                free(cc_arguments);
                free(total_sm_arguments);
            }else{
                pthread_t next_safemode_id;
                pthread_t main_computation_id;
                next_safemode_computation_arguments *next_sm_arguments = next_sm_arguments_alloc(now, u_safemode, s_dyn, d_dyn->time_horizon, f_cost, polytope_list_safemode);
                pthread_create(&next_safemode_id, NULL, next_safemode_computation, (void*)next_sm_arguments);
                control_computation_arguments *cc_arguments = cc_arguments_alloc(now, &u.matrix, s_dyn, d_dyn,f_cost, current_time_horizon, target, polytope_list_backup);
                pthread_create(&main_computation_id, NULL, main_computation, (void*)cc_arguments);
                pthread_join(next_safemode_id, NULL);
                pthread_join(main_computation_id, NULL);
                free(cc_arguments);
                free(next_sm_arguments);
            }

        }

        printf("Applying it...");
        fflush(stdout);
        gsl_vector *w = gsl_vector_alloc(s_dyn->E->size2);
        get_disturbance(w, 0, 0.1);
        //get timer back
        pthread_join(timer_id, NULL);
        if(main_computation_completed){
            gsl_vector_view u_apply = gsl_matrix_column(&u.matrix,0);
            apply_control(now->x, &u_apply.vector, s_dyn->A, s_dyn->B, s_dyn->E, w, i);
            main_computation_completed = 0;

        }else if(backup_applicable){

            gsl_vector_view u_apply = gsl_matrix_column(u_backup,i);
            apply_control(now->x, &u_apply.vector, s_dyn->A, s_dyn->B, s_dyn->E, w, i);

        }else{
        //goto safemode
            gsl_vector_view u_safe = gsl_matrix_column(u_safemode,0);
            apply_control(now->x, &u_safe.vector, s_dyn->A, s_dyn->B, s_dyn->E, w, i);

        }

        int new_cell_found = 0;
        for (int j = 0; j < d_dyn->regions[now->current_cell]->number_of_polytopes; j++) {
            if (polytope_check_state(d_dyn->regions[now->current_cell]->polytopes[j], now->x)){
                new_cell_found = 1;
                break;
            }
        }
        if(!new_cell_found){
            for (int j = 0; j < d_dyn->regions[target]->number_of_polytopes; j++) {
                if (polytope_check_state(d_dyn->regions[target]->polytopes[j], now->x)){
                    new_cell_found = 1;
                    now->current_cell=target;
                    break;
                }
            }
        }
        if(!new_cell_found){
            for(int k=0; k<d_dyn->number_of_regions;k++){
                for (int j = 0; j < d_dyn->regions[k]->number_of_polytopes; j++) {
                    if (polytope_check_state(d_dyn->regions[k]->polytopes[j], now->x)){
                        now->current_cell=k;
                        break;
                    }
                }
            }
        }
        gsl_vector_free(w);
        printf("New state:");
        gsl_vector_print(now->x, "now->");
        printf("New Cell: %d\n", now->current_cell);
        fflush(stdout);
        gsl_matrix_free(u_safemode);
    }
    gsl_matrix_free(u_backup);

    for(int i = 0; i< d_dyn->time_horizon+1; i++){
        polytope_free(polytope_list_safemode[i]);
    }
    free(polytope_list_safemode);
    for(int i = 0; i< d_dyn->time_horizon+1; i++){
        polytope_free(polytope_list_backup[i]);
    }
    free(polytope_list_backup);
}

/**
 * Apply the calculated control to the current state using system dynamics
 */
void apply_control(gsl_vector *x, gsl_vector *u, gsl_matrix *A, gsl_matrix *B,gsl_matrix *E, gsl_vector* w, size_t current_time) {
    printf("apply_control time(%d) ", (int) current_time);
    gsl_vector_print(x, "x");
    fflush(stdout);
    gsl_vector *x_temp = gsl_vector_alloc(x->size);
    //Apply input to state of next N time steps
    // x[k+1] = A.x[k] + B.u[k+1]
    gsl_vector_set_zero(x_temp);
    printf("apply_control: u[%d] = ", (int)current_time);
    gsl_vector_print(u,"u");
    fflush(stdout);
    gsl_vector *Btu = gsl_vector_alloc(x->size);

    //A.x
    gsl_blas_dgemv(CblasNoTrans, 1, A, x, 0, x_temp);
    //B.u
    gsl_blas_dgemv(CblasNoTrans, 1, B, u, 0 , Btu);
    //update x[k-1] => x[k]
    gsl_vector_set_zero(x);
    gsl_vector_add(x, x_temp);
    gsl_vector_add(x, Btu);
    //E.w
    gsl_vector_set_zero(x_temp);
    gsl_blas_dgemv(CblasNoTrans, 1, E, w, 0, x_temp);
    gsl_vector_add(x,x_temp);
    gsl_vector_free(x_temp);
    printf("Temporary state: x[%d] = ", (int)current_time+1);
    gsl_vector_print(x,"x");
    fflush(stdout);
    gsl_vector_free(Btu);
};
