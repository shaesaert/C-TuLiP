#include "cimple_c_from_py.h"
#include "setoper.h"
#include <cdd.h>

int main(){

    polka_initialize(false,5,100);

    dd_set_global_constants();
    // Initialize state:
    system_dynamics *s_dyn;
    cost_function *f_cost;
    discrete_dynamics *d_dyn;
    current_state *now;

    system_alloc(&now, &s_dyn, &f_cost, &d_dyn);
    system_init(now, s_dyn, f_cost, d_dyn);

    double sec = 2;
    ACT(3, now, d_dyn, s_dyn, f_cost, sec);


    system_dynamics_free(s_dyn);
    discrete_dynamics_free(d_dyn);
    cost_function_free(f_cost);
    state_free(now);

    dd_free_global_constants();
}
