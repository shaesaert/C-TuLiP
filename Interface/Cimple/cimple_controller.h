//
// Created by L. Jonathan Feldstein
//

#ifndef CIMPLE_CIMPLE_CONTROLLER_H
#define CIMPLE_CIMPLE_CONTROLLER_H

#include <stddef.h>
#include <math.h>
#include "cimple_system.h"
#include <gsl/gsl_matrix.h>
#include <gsl/gsl_blas.h>
#include "cimple_polytope_library.h"
#include <pthread.h>
#include "cimple_mpc_computation.h"


/**
 * @brief Action to get plant from current abstract state to target_abs_state.
 *
 * @param target target region the plant is supposed to reach
 * @param now current state of the plant
 * @param d_dyn discrete abstraction of the system
 * @param s_dyn system dynamics including auxiliary matrices
 * @param f_cost cost function to be minimized on the path
 */
void ACT(int target,
         current_state * now,
         discrete_dynamics * d_dyn,
         system_dynamics * s_dyn,
         cost_function * f_cost,
         double sec);
/**
 * @brief Apply the calculated control to the current state using system dynamics
 * @param x current state at time [0]
 * @param u matrix with next N inputs calculated by the MPC controller
 * @param A system dynamics
 * @param B input dynamics
 */
void apply_control(gsl_vector *x,
                   gsl_vector *u,
                   gsl_matrix *A,
                   gsl_matrix *B,
                   gsl_matrix *E,
                   gsl_vector *w,
                   size_t current_time);

/**
 * Fill a vector with gaussian distributed noise
 * @param w
 */
void simulate_disturbance(gsl_vector *w,
                     double mu,
                     double sigma);


void * main_computation(void *arg);


#endif //CIMPLE_CIMPLE_CONTROLLER_H
