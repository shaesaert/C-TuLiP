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
//       File: Ctrl_modesImpl.h
// Created on: 11-Aug-2017 13:30:51
//     Author: shaesaert@jpl.nasa.gov
// SCACmdLine: -c -sm Alice -sm Ctrl_modes ../Alice3_gen.xml
//
// This file was stubbed by the JPL StateChart Autocoders, which converts UML
// Statecharts, in XML, to a C variant of Miro Samek's Quantum Framework.
//===========================================================================
#ifndef CTRL_MODESIMPL_H
#define CTRL_MODESIMPL_H

#include <qf_port.h>
#include <qassert.h>

typedef struct Ctrl_modesImpl {
    char machineName[128];
    /** Cache of pointer to the container QActive object, for ease of access */
    QActive *active;
} Ctrl_modesImpl;

Ctrl_modesImpl *Ctrl_modesImpl_Constructor (Ctrl_modesImpl *mepl);  // Default constructor
void Ctrl_modesImpl_set_qactive (Ctrl_modesImpl *mepl, QActive *active);
int32_t Ctrl_modesImpl_get_verbosity ();
////////////////////////////////////////////
// Action and guard implementation methods
////////////////////////////////////////////
void Ctrl_modesImpl_act_m0 (Ctrl_modesImpl *mepl);
void Ctrl_modesImpl_act_m1 (Ctrl_modesImpl *mepl);
void Ctrl_modesImpl_act_m2 (Ctrl_modesImpl *mepl);
void Ctrl_modesImpl_act_m3 (Ctrl_modesImpl *mepl);
void Ctrl_modesImpl_at_RTI (Ctrl_modesImpl *mepl);
void Ctrl_modesImpl_entry (Ctrl_modesImpl *mepl);

#endif  /* CTRL_MODESIMPL_H */
