//
// Created by Sofie Haesaert on 9/23/17.
//
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <log_event.h>
#include <qf_port.h>
#include <qassert.h>
#include <assert.h>
#include <Ctrl_modesImpl.h>
#include <StatechartSignals.h>
#include <Strategy.h>
#include <Ctrl_modes.h>


double env_history=1;
double env=1;


////////////////////////////////////////////
// Model environment updates
////////////////////////////////////////////


void meas_env(Ctrl_modesImpl *mepl) {
    LogEvent_log("Measure environment\n");
    QEvent *newEv;
    env=rand() %3; // between 0 and 2
    printf("%f Measure environment\n", env);
    env=env -1 + env_history;
    if (env < 2) {
        env_history = 1;
        printf("%fLIDON0_STERON0_SIG \n", env);
        newEv = Q_NEW(QEvent, LIDON0_STERON0_SIG );
        QF_publish(newEv);

    }
    else if (env == 2) {
        env_history = 2;
        printf("%fLIDON0_STERON1_SIG \n", env);
        newEv = Q_NEW(QEvent, LIDON0_STERON1_SIG );
        QF_publish(newEv);


    }
    else if (env > 2) {
        env_history = 3;
        printf("%fLIDON1_STERON1_SIG \n", env);
        newEv = Q_NEW(QEvent, LIDON1_STERON1_SIG );
        QF_publish(newEv);

    }


}