//
// Created by be107admin on 9/25/17.
//

#ifndef CIMPLE_POLYTOPE_LIBRARY_CIMPLE_H
#define CIMPLE_POLYTOPE_LIBRARY_CIMPLE_H

#include "cimple_gsl_library_extension.h"

/**
 * H left side of polytope (sometimes noted A or L)
 * G right side of polytope (sometimes noted b or M)
 *
 *      H.x <= G
 *
 * Chebyshev center is a possible definition  of the "center" of the polytope.
 */
typedef struct polytope{

    gsl_matrix * H;
    gsl_vector * G;
    double *chebyshev_center;

}polytope;

/**
 * @brief "Constructor" Dynamically allocates the space a polytope needs
 * @param k H.size1 == G.size
 * @param n H.size2
 * @return
 */
struct polytope *polytope_alloc(size_t k, size_t n);

/**
 * @brief "Destructor" Deallocates the dynamically allocated to the polytope
 * @param polytope
 */
void polytope_free(polytope *polytope);

/**
 * Convex region of several (number_of_polytopes) polytopes (array of polytopes**)
 * hull_of_region is the convex hull of polytopes in that region
 * hull.A = NULL if only one polytope exists in that region
 */
typedef struct region_of_polytopes{

    int number_of_polytopes;
    polytope **polytopes;
    polytope *hull_of_region;

}region_of_polytopes;

/**
 *
 * @param k
 * @param k_hull
 * @param n
 * @param number_of_polytopes
 * @return
 */
struct region_of_polytopes *region_of_polytopes_alloc(size_t k[],size_t k_hull, size_t n, int number_of_polytopes);
void region_of_polytopes_free(region_of_polytopes * region_of_polytopes);


void polytope_from_arrays(polytope *polytope, size_t k, size_t n, double *left_side, double *right_side, char*name);

int state_in_polytope(polytope *polytope, gsl_vector *x);

void polytope_project(polytope *polytope, size_t new_dimension);

void polytope_reduce(polytope *polytope);

#endif //CIMPLE_POLYTOPE_LIBRARY_CIMPLE_H
