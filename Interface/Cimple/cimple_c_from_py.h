//
// Created by L. J. Feldstein
//

#ifndef CIMPLE_INIT_C_FROM_PY_H
#define CIMPLE_INIT_C_FROM_PY_H

#include "cimple_system.h"
#include "cimple_controller.h"
#include "cimple_gsl_library_extension.h"

/**
 * @brief Allocates the needed memory space on the heap for all major structs, that get reused a lot
 *
 * The memory space is allocated outside of main(),
 * so that main() doesn't need to be changed every time the python code is executed.
 *
 * @param now state of plant
 * @param s_dyn system dynamics including auxiliary matrices
 * @param f_cost cost function matrices as defined by user
 * @param d_dyn discrete abstraction as generated by TuLiP
 */
void system_alloc(current_state **now, system_dynamics **s_dyn, cost_function **f_cost,discrete_dynamics **d_dyn);

/**
 * @brief Initializes C structs based on content from python objects as given by TuLiP
 *
 * The python codes hard codes the python objects into C compound literals that are directly (mem)copied
 * into dynamic arrays. (Whithout being stored at any time)
 * The dynamics arrays fill up the matrices and polytopes. Lastly dynamic arrays are deleted
 *
 * @param now state of plant
 * @param s_dyn system dynamics including auxiliary matrices
 * @param f_cost cost function matrices as defined by user
 * @param d_dyn discrete abstraction as generated by TuLiP
 */
void system_init(current_state *now, system_dynamics *s_dyn,cost_function *f_cost ,discrete_dynamics *d_dyn);
#endif //CIMPLE_INIT_C_FROM_PY_H