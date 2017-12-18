#include "cimple_c_from_py.h"
#include "act_impl.h"

int main(){

    polka_initialize(false,5,100);

    // Initialize state:
    system_dynamics *s_dyn;
    cost_function *f_cost;
    discrete_dynamics *d_dyn;
    current_state *now;

    system_alloc(&now, &s_dyn, &f_cost, &d_dyn);
    system_init(now, s_dyn, f_cost, d_dyn);

    ACT_m3(now, d_dyn, s_dyn, f_cost);

    system_dynamics_free(s_dyn);
    discrete_dynamics_free(d_dyn);
    cost_function_free(f_cost);
    state_free(now);

}
