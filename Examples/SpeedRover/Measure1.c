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

double env=1;


////////////////////////////////////////////
// Model environment updates
////////////////////////////////////////////


void meas_env(Ctrl_modesImpl *mepl) {
    LogEvent_log("Measure environment\n");
    QEvent *newEv;
    env=rand() %2; // between 0 and 1
    if (env == 0) {
        printf("%fLIDON0_SIG \n", env);
        newEv = Q_NEW(QEvent, LIDON0_SIG );
        QF_publish(newEv);

    }
    else if (env == 1) {
        printf("%fLIDON1_SIG \n", env);
        newEv = Q_NEW(QEvent, LIDON1_SIG );
        QF_publish(newEv);


    }


}