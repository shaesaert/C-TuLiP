//===========================================================================
// This software contains Caltech/JPL confidential information.
//
// Copyright 2009-2017, by the California Institute of Technology.
// ALL RIGHTS RESERVED. United States Government Sponsorship Acknowledged.
// Any commercial use must be negotiated with the Office of Technology
// Transfer at the California Institute of Technology.
//
// This software may be subject to US export control laws and
// regulations. By accepting this document, the user agrees to comply
// with all applicable U.S. export laws and regulations, including the
// International Traffic and Arms Regulations, 22 C.F.R. 120-130 and the
// Export Administration Regulations, 15 C.F.R. 730-744. User has the
// responsibility to obtain export licenses, or other export authority as
// may be required before exporting such information to foreign countries
// or providing access to foreign persons.
//===========================================================================
//
//       File: Ctrl_modesImpl.c
// Created on: 21-Sep-2017 23:54:46
//     Author: shaesaert@jpl.nasa.gov
// SCACmdLine: -c -sm Strategy -sm Ctrl_modes ../Alice3_gen.xml
//
// This file was stubbed by the JPL StateChart Autocoders, which converts UML
// Statecharts, in XML, to a C variant of Miro Samek's Quantum Framework.
//===========================================================================
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
#include <Measure.h>

int32_t Ctrl_modesImpl_verbosity_level = 0;

extern bool allow_trans;
double u=0;
double x_state=0;
double target_min=0;
double target_max=5;
double target_mean=2.5;



Ctrl_modesImpl *Ctrl_modesImpl_Constructor (Ctrl_modesImpl *mepl) {
    strncpy(mepl->machineName, "Ctrl_modes", 128);
    mepl->machineName[128-1] = '\0';  // null-terminate to be sure

    AttributeMapper_init(mepl);

    return mepl;
}

void Ctrl_modesImpl_set_qactive (Ctrl_modesImpl *mepl, QActive *active) {
    mepl->active = active;
}

int32_t Ctrl_modesImpl_get_verbosity () {
    return Ctrl_modesImpl_verbosity_level;
}
////////////////////////////////////////////
// FEEDBACK
////////////////////////////////////////////
double feedback() {
    u = target_mean-x_state;
    if (u>2){
        u=2;
    }
    else if (u<-2) {
        u=-2;
    }
    return u;
}
/*
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


}*/
////////////////////////////////////////////
// Action and guard implementation methods
////////////////////////////////////////////

void Ctrl_modesImpl_act_m0 (Ctrl_modesImpl *mepl) {
    //printf("%s.act_m0() default action implementation invoked\n", mepl->machineName);
    target_min=15;
    target_mean=17.5;
    target_max=20;
    x_state=x_state+feedback();
}

void Ctrl_modesImpl_act_m1 (Ctrl_modesImpl *mepl) {
    //printf("%s.act_m1() default action implementation invoked\n", mepl->machineName);
    target_min=10;
    target_mean=12.5;
    target_max=15;
    x_state=x_state+feedback();
}

void Ctrl_modesImpl_act_m2 (Ctrl_modesImpl *mepl) {
    //printf("%s.act_m2() default action implementation invoked\n", mepl->machineName);
    target_min=5;
    target_mean=7.5;
    target_max=10;
    x_state=x_state+feedback();
}

void Ctrl_modesImpl_act_m3 (Ctrl_modesImpl *mepl) {
    //printf("%s.act_m3() default action implementation invoked\n", mepl->machineName);
    target_min=0;
    target_mean=2.5;
    target_max=5;
    x_state=x_state+feedback();
}

void Ctrl_modesImpl_at_RTI (Ctrl_modesImpl *mepl) {
    //printf("%s.at_RTI() default action implementation invoked\n", mepl->machineName);
    printf("%s.at_RTI() measure x \n", mepl->machineName);
    // Measure state (in fact we already know it, so just print it):

    printf("x =  %lf\n",x_state);
    if (target_min <= x_state && x_state <= target_max) {
        allow_trans = true ;
        meas_env(mepl);
    }
    else {
        LogEvent_log("compute control & apply control");
        x_state=x_state+feedback();
    }
}

void Ctrl_modesImpl_entry (Ctrl_modesImpl *mepl) {
    //printf("%s.entry() default action implementation invoked\n", mepl->machineName);
}
