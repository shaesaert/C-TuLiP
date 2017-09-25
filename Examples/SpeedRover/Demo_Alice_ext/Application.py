
import sys
sys.path.append('autocode')

import Strategy
import Ctrl_modes

def update():
    strategy.win.update()
    control_modes.win.update()

strategy = Strategy.Strategy("strategy:Strategy")
strategy.canvas.scale("all", 0.0, 0.0, 1.00, 1.00)
strategy.win.geometry('979x755+14+58')
control_modes = Ctrl_modes.Ctrl_modes("control_modes:Ctrl_modes")
control_modes.canvas.scale("all", 0.0, 0.0, 1.00, 1.00)
control_modes.win.geometry('979x755+14+58')


mapCharts = {

    'strategy:Strategy': strategy,
    'control_modes:Ctrl_modes': control_modes,

}
