//
// Created by be107admin on 11.04.18.
//

#ifndef CIMPLE_CIMPLE_MINKSUM_WRAPPER_H
#define CIMPLE_CIMPLE_MINKSUM_WRAPPER_H

//#include <assert.h>
//#include "CommandlineOptions.hh"

#ifdef __cplusplus

#include "VPolytopeList.hh"

// C++ declarations (for example classes or functions that have C++ objects
//                   as parameters)
extern "C"
{
#endif
//dd_PolyhedraPtr returnPoly();
dd_PolyhedraPtr cdd_minkowski(dd_PolyhedraPtr A,
                              dd_PolyhedraPtr B);
// C declarations (for example your function f)

#ifdef __cplusplus
}
#endif
#endif //CIMPLE_CIMPLE_MINKSUM_WRAPPER_H //CIMPLE_CIMPLE_MINKSUM_WRAPPER_H
