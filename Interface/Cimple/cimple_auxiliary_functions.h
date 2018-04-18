#ifndef CIMPLE_CIMPLE_AUXILIARY_FUNCTIONS_H
#define CIMPLE_CIMPLE_AUXILIARY_FUNCTIONS_H

/**
 * @brief Macro computes number of an array.
 *
 * Remark: It is defined as a Macro so that it can be used independently of the type of the array
 * e.g. int a[2]; =>N_ELEMS(a)=2
 *      polytope b[3]; =>N_ELEMS(a)=2 (this is an array of 3 polytopes that's why it is not "polytope*")
 */
#define N_ELEMS(x)  (sizeof(x) / sizeof((x)[0]))

#include <stdio.h>
#include <string.h>
#include <pthread.h>
#include <stddef.h>
#include <math.h>
#include <stdbool.h>
#include <gsl/gsl_matrix.h>
#include <gsl/gsl_blas.h>


/**
 * @brief Generates random numbers with normal distribution
 * @param mu
 * @param sigma
 * @return
 */
double randn (double mu,
              double sigma);

/**
 * @brief Timer simulating one time step in discrete control
 * @param arg
 * @return
 */
void * timer(void * arg);

/**
 * @brief Breaks infinte loop in a pthread
 * @param mtx
 * @return
 */
int needQuit(pthread_mutex_t *mtx);
#endif //CIMPLE_CIMPLE_AUXILIARY_FUNCTIONS_H
