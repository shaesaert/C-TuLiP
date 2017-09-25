

#include "qep_port.h"
#include "application.h"
#include "qassert.h"

#include <termios.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>


#define MYQUEUESIZE 10

  StrategyImpl strategyImpl;
  Strategy strategy;
  const QEvent * strategy_queuestorage[MYQUEUESIZE];
  Ctrl_modesImpl control_modesImpl;
  Ctrl_modes control_modes;
  const QEvent * control_modes_queuestorage[MYQUEUESIZE];
  
void applicationStart(int qsize)
{

  StrategyImpl_Constructor(&strategyImpl);
  Strategy_Constructor(&strategy, "strategy", &strategyImpl, 0);
  QActive_start((QActive *) & strategy, 1, strategy_queuestorage,  MYQUEUESIZE, NULL, 0, NULL);
  Ctrl_modesImpl_Constructor(&control_modesImpl);
  Ctrl_modes_Constructor(&control_modes, "control_modes", &control_modesImpl, 0);
  QActive_start((QActive *) & control_modes, 2, control_modes_queuestorage,  MYQUEUESIZE, NULL, 0, NULL);

}

////////////////////////////////////////////////////////////////////////////////
//@fn setGuardAttribute()
//@brief 
//@param 
//@return 
////////////////////////////////////////////////////////////////////////////////
void setGuardAttribute (const char *sm, const char *attr, const char *val) {
	printf("Got sm '%s', attr name '%s', and value '%s'\n", sm, attr, val);
	
	if (strcasecmp(sm, "strategy") == 0) {
	   AttributeMapper_set(&(strategyImpl), attr, AttributeMapper_strtobool(val));
	}
	if (strcasecmp(sm, "control_modes") == 0) {
	   AttributeMapper_set(&(control_modesImpl), attr, AttributeMapper_strtobool(val));
	}
}
