//
// Created by L. J. Feldstein
//

#ifndef CIMPLE_INIT_C_FROM_PY_H
#define CIMPLE_INIT_C_FROM_PY_H
#include "system.h"
#include "find_controller.h"
void system_alloc(current_state **now, system_dynamics **s_dyn, cost_function **f_cost,discrete_dynamics **d_dyn);
void system_init(current_state *now, system_dynamics *s_dyn,cost_function *f_cost ,discrete_dynamics *d_dyn);
#endif //CIMPLE_INIT_C_FROM_PY_H
