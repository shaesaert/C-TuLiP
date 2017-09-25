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
double FREEWAY=0;
double LIDON=0;
double STEREO=0;
double RADON=0;
char signame[]= "FREEWAY0_LIDON0_STEREO0_RADON0";

////////////////////////////////////////////
// Model environment updates
////////////////////////////////////////////
/*FREEWAY0_LIDON0_STEREO0_RADON0_SIG,*//* 0x000E *//*
FREEWAY0_LIDON0_STEREO0_RADON1_SIG,*//* 0x000F *//*
FREEWAY0_LIDON0_STEREO1_RADON0_SIG,*//* 0x0010 *//*
FREEWAY0_LIDON0_STEREO1_RADON1_SIG,*//* 0x0011 *//*
FREEWAY0_LIDON1_STEREO0_RADON0_SIG,*//* 0x0012 *//*
FREEWAY0_LIDON1_STEREO0_RADON1_SIG,*//* 0x0013 *//*
FREEWAY0_LIDON1_STEREO1_RADON0_SIG,*//* 0x0014 *//*
FREEWAY0_LIDON1_STEREO1_RADON1_SIG,*//* 0x0015 *//*
FREEWAY1_LIDON0_STEREO0_RADON0_SIG,*//* 0x0016 *//*
FREEWAY1_LIDON0_STEREO0_RADON1_SIG,*//* 0x0017 *//*
FREEWAY1_LIDON0_STEREO1_RADON0_SIG,*//* 0x0018 *//*
FREEWAY1_LIDON0_STEREO1_RADON1_SIG,*//* 0x0019 *//*
FREEWAY1_LIDON1_STEREO0_RADON0_SIG,*//* 0x001A *//*
FREEWAY1_LIDON1_STEREO0_RADON1_SIG,*//* 0x001B *//*
FREEWAY1_LIDON1_STEREO1_RADON0_SIG,*//* 0x001C *//*
FREEWAY1_LIDON1_STEREO1_RADON1_SIG,*//* 0x001D */

void meas_env(Ctrl_modesImpl *mepl) {
    LogEvent_log("Measure environment\n");
    QEvent *newEv;
    env = rand() %2; // between 0 and 1

    // Compose events:
    // Perfect
    FREEWAY = 1;
    LIDON = 1;
    STEREO = 1;
    RADON = 1;

    // Compose string for event
    strcpy(signame, "FREEWAY0_LIDON0_STEREO0_RADON0");
    if (FREEWAY == 1){
        signame[7]='1';
    }
    if (LIDON == 1){
        signame[14]='1';
    }
    if (STEREO == 1){
        signame[22]='1';
    }
    if (RADON == 1){
        signame[29]='1';
    }
    // Create right event
    if  (strcmp("FREEWAY0_LIDON0_STEREO0_RADON0",signame) == 0) {
        newEv = Q_NEW(QEvent, FREEWAY0_LIDON0_STEREO0_RADON0_SIG);

    }else if (strcmp("FREEWAY0_LIDON0_STEREO0_RADON1",signame) == 0){
            newEv = Q_NEW(QEvent,FREEWAY0_LIDON0_STEREO0_RADON1_SIG);

    } else if  (strcmp("FREEWAY0_LIDON0_STEREO1_RADON0",signame) == 0){
            newEv = Q_NEW(QEvent,FREEWAY0_LIDON0_STEREO1_RADON0_SIG);

    } else if  (strcmp("FREEWAY0_LIDON0_STEREO1_RADON1",signame) == 0){
        newEv = Q_NEW(QEvent,FREEWAY0_LIDON0_STEREO1_RADON1_SIG);

    } else if  (strcmp("FREEWAY0_LIDON1_STEREO0_RADON0",signame) == 0){
        newEv = Q_NEW(QEvent,FREEWAY0_LIDON1_STEREO0_RADON0_SIG);

    } else if  (strcmp("FREEWAY0_LIDON1_STEREO0_RADON1",signame) == 0){
        newEv = Q_NEW(QEvent,FREEWAY0_LIDON1_STEREO0_RADON1_SIG);

    } else if  (strcmp("FREEWAY0_LIDON1_STEREO1_RADON0",signame) == 0){
        newEv = Q_NEW(QEvent,FREEWAY0_LIDON1_STEREO1_RADON0_SIG);

    } else if  (strcmp("FREEWAY0_LIDON1_STEREO1_RADON1",signame) == 0){
        newEv = Q_NEW(QEvent,FREEWAY0_LIDON1_STEREO1_RADON1_SIG);

    } else if  (strcmp("FREEWAY1_LIDON0_STEREO0_RADON0",signame) == 0){
        newEv = Q_NEW(QEvent,FREEWAY1_LIDON0_STEREO0_RADON0_SIG);

    } else if  (strcmp("FREEWAY1_LIDON0_STEREO0_RADON1",signame) == 0){
        newEv = Q_NEW(QEvent,FREEWAY1_LIDON0_STEREO0_RADON1_SIG);

    } else if  (strcmp("FREEWAY1_LIDON0_STEREO1_RADON0",signame) == 0){
        newEv = Q_NEW(QEvent,FREEWAY1_LIDON0_STEREO1_RADON0_SIG);

    } else if  (strcmp("FREEWAY1_LIDON0_STEREO1_RADON1",signame) == 0){
        newEv = Q_NEW(QEvent,FREEWAY1_LIDON0_STEREO1_RADON1_SIG);

    } else if  (strcmp("FREEWAY0_LIDON1_STEREO0_RADON0",signame) == 0){
        newEv = Q_NEW(QEvent,FREEWAY1_LIDON1_STEREO0_RADON0_SIG);

    } else if  (strcmp("FREEWAY0_LIDON1_STEREO0_RADON1",signame) == 0){
        newEv = Q_NEW(QEvent,FREEWAY1_LIDON1_STEREO0_RADON1_SIG);

    } else if  (strcmp("FREEWAY0_LIDON1_STEREO1_RADON0",signame) == 0){
        newEv = Q_NEW(QEvent,FREEWAY1_LIDON1_STEREO1_RADON0_SIG);

    } else if  (strcmp("FREEWAY0_LIDON1_STEREO1_RADON1",signame) == 0){
        newEv = Q_NEW(QEvent,FREEWAY1_LIDON1_STEREO1_RADON1_SIG);

    } else {
        newEv = Q_NEW(QEvent,FREEWAY1_LIDON1_STEREO1_RADON1_SIG);


    }
    QF_publish(newEv);

}