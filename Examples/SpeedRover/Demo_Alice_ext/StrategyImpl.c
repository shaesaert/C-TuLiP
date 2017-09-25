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
//       File: StrategyImpl.c
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
#include <StrategyImpl.h>
#include <StatechartSignals.h>


int32_t StrategyImpl_verbosity_level = 0;
bool allow_trans = true;


StrategyImpl *StrategyImpl_Constructor (StrategyImpl *mepl) {
    strncpy(mepl->machineName, "Strategy", 128);
    mepl->machineName[128-1] = '\0';  // null-terminate to be sure

    AttributeMapper_init(mepl);
    AttributeMapper_set(mepl, "read_guard", 1);
    mepl->read_guard = 1;

    return mepl;
}

void StrategyImpl_set_qactive (StrategyImpl *mepl, QActive *active) {
    mepl->active = active;
}

int32_t StrategyImpl_get_verbosity () {
    return StrategyImpl_verbosity_level;
}


////////////////////////////////////////////
// Action and guard implementation methods
////////////////////////////////////////////


bool StrategyImpl_read_guard (StrategyImpl *mepl) {
    bool rv = allow_trans;
    //bool rv = AttributeMapper_get(mepl, "read_guard");
    //printf("%s.read_guard() == %s\n", mepl->machineName, AttributeMapper_booltostr(rv));
    return rv;  // or could use mepl->read_guard;
}

void StrategyImpl_init (StrategyImpl *mepl) {
    //printf("%s.init() default action implementation invoked\n", mepl->machineName);
}

void StrategyImpl_set_guard (StrategyImpl *mepl) {
    allow_trans = false;
    //printf("%s.set_guard() default action implementation invoked\n", mepl->machineName);
}
