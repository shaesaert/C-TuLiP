//
// Created by be107admin on 9/25/17.
//

#ifndef CIMPLE_GSL_LIBRARY_CIMPLE_EXTENSION_H
#define CIMPLE_GSL_LIBRARY_CIMPLE_EXTENSION_H

#include <gsl/gsl_blas.h>
#include <gurobi_c.h>

////////////////////////////////////////////////////////////////////////////////
// @fn gsl_matrix_from_array()
// @brief Converts an array to a gsl matrix
// @param gsl_matrix *matrix
// @param double *array
////////////////////////////////////////////////////////////////////////////////
void gsl_matrix_from_array(gsl_matrix *matrix,double *array, char* name);

////////////////////////////////////////////////////////////////////////////////
// @fn gsl_vector_from_array()
// @brief Converts an array to a gsl vector
// @param gsl_matrix *matrix
// @param double *array
////////////////////////////////////////////////////////////////////////////////
void gsl_vector_from_array(gsl_vector *vector, double *array, char* name);

////////////////////////////////////////////////////////////////////////////////
// @fn gsl_matrix_print()
// @brief Prints a gsl matrix readable to the output
// @param gsl_matrix *matrix
// @param char *name
////////////////////////////////////////////////////////////////////////////////
void gsl_matrix_print(gsl_matrix *matrix, char *name);

////////////////////////////////////////////////////////////////////////////////
// @fn gsl_vector_print()
// @brief Prints a gsl vector readable to the output
// @param gsl_matrix *matrix
// @param char *name
////////////////////////////////////////////////////////////////////////////////
void gsl_vector_print(gsl_vector *vector, char *name);

gsl_matrix * gsl_matrix_diag_from_vector(gsl_vector * X, double rest);

int gsl_matrix_to_qpterm_gurobi(gsl_matrix *P, GRBmodel *model, size_t N);

int gsl_vector_to_linterm_gurobi(gsl_vector *q, GRBmodel *model, size_t N);

#endif //CIMPLE_GSL_LIBRARY_CIMPLE_EXTENSION_H
