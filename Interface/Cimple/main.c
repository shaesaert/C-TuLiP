#include "cimple_c_from_py.h"

int main(){

    polka_initialize(false,5,100);

    // Initialize state:
    system_dynamics *s_dyn;
    cost_function *f_cost;
    discrete_dynamics *d_dyn;
    current_state *now;

    system_dynamics *s_dyn2;
    cost_function *f_cost2;
    discrete_dynamics *d_dyn2;
    current_state *now2;

    system_alloc(&now, &s_dyn, &f_cost, &d_dyn);
    system_init(now, s_dyn, f_cost, d_dyn);

    system_alloc(&now2, &s_dyn2, &f_cost2, &d_dyn2);
    system_init(now2, s_dyn2, f_cost2, d_dyn2);
    double sec = 2;
    ACT(3, now, d_dyn, s_dyn, f_cost, now2, d_dyn2, s_dyn2, f_cost2, sec);


    system_dynamics_free(s_dyn);
    discrete_dynamics_free(d_dyn);
    cost_function_free(f_cost);
    state_free(now);
    system_dynamics_free(s_dyn2);
    discrete_dynamics_free(d_dyn2);
    cost_function_free(f_cost2);
    state_free(now2);
}
