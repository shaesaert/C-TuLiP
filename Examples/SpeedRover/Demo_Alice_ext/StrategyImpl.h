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
//       File: StrategyImpl.h
// Created on: 21-Sep-2017 23:54:46
//     Author: shaesaert@jpl.nasa.gov
// SCACmdLine: -c -sm Strategy -sm Ctrl_modes ../Alice3_gen.xml
//
// This file was stubbed by the JPL StateChart Autocoders, which converts UML
// Statecharts, in XML, to a C variant of Miro Samek's Quantum Framework.
//===========================================================================
#ifndef STRATEGYIMPL_H
#define STRATEGYIMPL_H

#include <qf_port.h>
#include <qassert.h>


typedef struct StrategyImpl {
    char machineName[128];
    /** Cache of pointer to the container QActive object, for ease of access */
    QActive *active;
    bool read_guard;
} StrategyImpl;

StrategyImpl *StrategyImpl_Constructor (StrategyImpl *mepl);  // Default constructor
void StrategyImpl_set_qactive (StrategyImpl *mepl, QActive *active);
int32_t StrategyImpl_get_verbosity ();
////////////////////////////////////////////
// Action and guard implementation methods
////////////////////////////////////////////
bool StrategyImpl_read_guard (StrategyImpl *mepl);
void StrategyImpl_init (StrategyImpl *mepl);
void StrategyImpl_set_guard (StrategyImpl *mepl);

#endif  /* STRATEGYIMPL_H */
