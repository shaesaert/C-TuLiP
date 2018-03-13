#
#
# Implementation of Minimizing the Number of internal States in Incomplete specified sequential NEtworks
# By A. Grasselli and F. Luccio
#
#
#
import itertools
from tulip import transys


def _inverse_dict(my_map, set_value = False):
    if not set_value:
        nv_map = {v: k for k, v in my_map.items()}
    else:
        nv_map = {frozenset(v): k for k, v in my_map.items()}

    return nv_map

class Mealynum(transys.MealyMachine):

    def __init__(self, ctrl, outputs=None):
        transys.MealyMachine.__init__(self)

        # >> > m = MealyMachine()
        # >> > pure_signal = {'present', 'absent'}
        # >> > m.add_inputs([('tick', pure_signal)])
        # >> > m.add_outputs([('go', pure_signal), ('stop', pure_signal)])
        # >> > m.states.add_from(['red', 'green', 'yellow'])
        # >> > m.states.initial.add('red')
        # define inputs numerically
        self.x_name = self._x(ctrl)  # numeric keys + names
        self.x = self.x_name.keys()  # create set with inputs
        self.add_inputs({'x': self.x})

        # define outputs
        self.z_name = self._z(ctrl, outputs)
        self.z = self.z_name.keys()
        self.add_outputs({'z': self.z})

        # define states
        self.s_name = self._s(ctrl)
        self.s = self.s_name.keys()
        self.states.add_from(self.s)

        self.react_S = dict()
        ## create transitions
        s_inv = _inverse_dict(self.s_name)
        x_inv = _inverse_dict(self.x_name, set_value=True)
        z_inv = _inverse_dict(self.z_name, set_value=True)
        for from_state, to_state, label_dict in ctrl.transitions(data=True):
            label = dict()
            for x_key in x_inv.keys():
                if x_key < frozenset(list(label_dict.items())):
                    label['x'] = x_inv[x_key]
                    pass

            for z_key in z_inv.keys():
                if z_key < frozenset(list(label_dict.items())):
                    label['z'] = z_inv[z_key]
                    pass

            self.transitions.add(s_inv[from_state], s_inv[to_state], label)




    def _x(self, ctrl):
        input_values = map(lambda key: list(ctrl.inputs[key]),ctrl.inputs.keys())
        input_list = list(itertools.product(*input_values))
        # create dictionary
        x_dict = dict()
        for u in range(len(input_list)):
            index = 0
            x = set()
            for input in ctrl.inputs.keys():
                x |= frozenset([(input, 1 == input_list[u][index])])
                index += 1
            x_dict[u] = x
        return x_dict

    def _z(self, ctrl, outputs):
        if outputs is None:
            outputs = ctrl.outputs.keys()
        output_values = map(lambda key: list(ctrl.outputs[key]),outputs)
        output_list = list(itertools.product(*output_values))
        # create dictionary
        z_dict = dict()
        for u in range(len(output_list)):
            z_set = set()
            index = 0
            for output in outputs:
                z_set |= frozenset([(output, 1 == output_list[u][index])])
                index += 1
            z_dict[u] = z_set
        return z_dict

    def _s(self, ctrl):
        s_dict = dict(list(enumerate(ctrl.states())))
        return s_dict


