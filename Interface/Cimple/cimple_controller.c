//
// Created by L.Jonathan Feldstein
//


#include <gsl/gsl_matrix.h>
#include "cimple_controller.h"

int main_computation_completed = 0;
/**
 * Action to get plant from current cell to target cell.
 */
void ACT(int target,
         current_state * now,
         discrete_dynamics * d_dyn,
         system_dynamics * s_dyn,
         cost_function * f_cost,
         double sec){
    printf("\nComputing control sequence to go from cell %d to cell %d...\n", (*now).current_cell, target);
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
//                pthread_t safe_mode_computation_id;
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
//                total_safemode_computation_arguments *total_sm_arguments = sm_arguments_alloc(now, u_safemode, current, safe, s_dyn, d_dyn->time_horizon, f_cost, polytope_list_safemode);
//                pthread_create(&safe_mode_computation_id, NULL, total_safe_mode_computation, (void*)total_sm_arguments);
//                pthread_join(safe_mode_computation_id, NULL);

                control_computation_arguments *cc_arguments = cc_arguments_alloc(now, &u.matrix, s_dyn, d_dyn,f_cost, current_time_horizon, target, polytope_list_backup);
                pthread_create(&main_computation_id, NULL, main_computation, (void*)cc_arguments);
                pthread_join(main_computation_id, NULL);

                //Clean up
                polytope_free(safe);
                polytope_free(current);
                free(cc_arguments);
//                free(total_sm_arguments);
            }else{
//                pthread_t next_safemode_id;
                pthread_t main_computation_id;
//                next_safemode_computation_arguments *next_sm_arguments = next_sm_arguments_alloc(now, u_safemode, s_dyn, d_dyn->time_horizon, f_cost, polytope_list_safemode);
//                pthread_create(&next_safemode_id, NULL, next_safemode_computation, (void*)next_sm_arguments);
//                pthread_join(next_safemode_id, NULL);
                control_computation_arguments *cc_arguments = cc_arguments_alloc(now, &u.matrix, s_dyn, d_dyn,f_cost, current_time_horizon, target, polytope_list_backup);
                pthread_create(&main_computation_id, NULL, main_computation, (void*)cc_arguments);
                pthread_join(main_computation_id, NULL);
                free(cc_arguments);
//                free(next_sm_arguments);
            }

        }

        printf("\nApplying it...\n");
        fflush(stdout);
        gsl_vector *w = gsl_vector_alloc(s_dyn->E->size2);
        simulate_disturbance(w, 0, 0.01);
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
        printf("\nNew state:");
        gsl_vector_print(now->x, "now->");
        printf("\nNew Cell: %d\n", now->current_cell);
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
};
/**
 * Simulation of system:
 *
 * Apply the calculated control to the current state using system dynamics
 */
void apply_control(gsl_vector *x,
                   gsl_vector *u,
                   gsl_matrix *A,
                   gsl_matrix *B,
                   gsl_matrix *E,
                   gsl_vector* w,
                   size_t current_time) {
    printf("\nApply_control time(%d)\n", (int) current_time);
    gsl_vector_print(x, "x");
    fflush(stdout);
    gsl_vector *x_temp = gsl_vector_alloc(x->size);
    //Apply input to state of next N time steps
    // x[k+1] = A.x[k] + B.u[k+1]
    gsl_vector_set_zero(x_temp);
    printf("\nApply_control: u[%d] = ", (int)current_time);
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
    printf("\nTemporary state: x[%d] = ", (int)current_time+1);
    gsl_vector_print(x,"x");
    fflush(stdout);
    gsl_vector_free(Btu);
};

/**
 * @brief Generate gaussian distributed random variable
 * @param mu
 * @param sigma
 * @return
 */
double randn (double mu,
              double sigma) {
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
};

/**
 * @brief Simulate disturbance by filling p-dimensional vector with gaussian random variables
 * @param w Vector to be filled
 * @param mu Mean of distribution
 * @param sigma Variance of distribution
 */
void simulate_disturbance(gsl_vector *w,
                     double mu,
                     double sigma){
    for(size_t i = 0; i<w->size;i++){
        gsl_vector_set(w,i,randn(mu,sigma));
    }
};

/**
 * @brief Timer simulating one time step in discrete control
 * @param arg
 * @return
 */
void * timer(void * arg){
    struct timeval sec;
    double* total_time_p = (double*)arg;
    double total_time = *total_time_p;
    int seconds = (int)floor(total_time);
    int u_seconds;
    u_seconds = (int)floor(total_time * pow(10,6) - seconds * pow(10,6));
    sec.tv_sec = seconds;
    sec.tv_usec = u_seconds;
    printf("\nTime runs: %d.%d\n", (int)sec.tv_sec, (int)sec.tv_usec);
    select(0,NULL,NULL,NULL,&sec);
    pthread_exit(0);
};

/**
 * @brief Computation of control towards target given by ACT()
 * @param arg
 * @return
 */
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




