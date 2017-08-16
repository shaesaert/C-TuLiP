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
//       File: AliceImpl.c
// Created on: 11-Aug-2017 13:30:52
//     Author: shaesaert@jpl.nasa.gov
// SCACmdLine: -c -sm Alice -sm Ctrl_modes ../Alice3_gen.xml
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
#include <AliceImpl.h>
#include <StatechartSignals.h>


int32_t AliceImpl_verbosity_level = 0;
bool allow_trans = true;


AliceImpl *AliceImpl_Constructor (AliceImpl *mepl) {
    strncpy(mepl->machineName, "Alice", 128);
    mepl->machineName[128-1] = '\0';  // null-terminate to be sure

    AttributeMapper_init(mepl);
    AttributeMapper_set(mepl, "read_guard", 1);
    mepl->read_guard = 1;

    return mepl;
}

void AliceImpl_set_qactive (AliceImpl *mepl, QActive *active) {
    mepl->active = active;
}

int32_t AliceImpl_get_verbosity () {
    return AliceImpl_verbosity_level;
}


////////////////////////////////////////////
// Action and guard implementation methods
////////////////////////////////////////////


bool AliceImpl_read_guard (AliceImpl *mepl) {
    bool rv = allow_trans;
    return rv;  // or could use mepl->read_guard;
}

void AliceImpl_init (AliceImpl *mepl) {
    //printf("%s.init() default action implementation invoked\n", mepl->machineName);
}

void AliceImpl_set_guard (AliceImpl *mepl) {
    //printf("%s.set_guard() default action implementation invoked\n", mepl->machineName);
    allow_trans = false;
}
