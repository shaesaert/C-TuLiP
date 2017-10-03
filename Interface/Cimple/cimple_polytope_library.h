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

///**
// * list of vectors
// *
// * Idea: list of matrix row views, to build an easily changeable (reduced) matrix/polytope
// */
//typedef struct polytope_list{
//    gsl_vector *vector;
//    double value;
//    struct polytope_list* node;
//}polytope_list;

/**
 * @brief "Constructor" Dynamically allocates the space a polytope needs
 * @param k H.size1 == G.size
 * @param n H.size2
 * @return
 */
struct polytope *polytope_alloc(size_t k, size_t n);

/**
 * @brief "Destructor" Deallocates the dynamically allocated memory of the polytope
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
 * @brief "Constructor" Dynamically allocates the space a region of polytope needs
 *
 * Allocates memory space according to the number_of_polytopes and their respective sizes
 *
 * @param k Array with the number of rows of each polytope dim([number_of_polytopes])
 * @param k_hull number of rows of convex hull polytope of the region
 * @param n system_dynamics size (e.g. s_dyn.A.size1)
 * @param number_of_polytopes
 * @return
 */
struct region_of_polytopes *region_of_polytopes_alloc(size_t k[],size_t k_hull, size_t n, int number_of_polytopes);

/**
 * @brief "Destructor" Deallocates the dynamically allocated memory of the region of polytopes
 * @param region_of_polytopes
 */
void region_of_polytopes_free(region_of_polytopes * region_of_polytopes);

/**
 * @brief Converts two C arrays to a polytope consistent of a left side matrix (i.e. H) and right side vector (i.e. G)
 * @param polytope empty polytope with allocated memory
 * @param k number of rows of polytope (H.size1 or G.size)
 * @param n dimension of polytope = system_dynamics size (e.g. s_dyn.A.size1)
 * @param left_side C array to be converted to left side matrix
 * @param right_side C array to be converted to right side vector
 * @param name name of polytope, will be displayed to user terminal to inform about successfull initialization
 */
void polytope_from_arrays(polytope *polytope, size_t k, size_t n, double *left_side, double *right_side, char*name);

/**
 * @brief Checks whether a state is in a certain polytope
 * @param polytope
 * @param x state to be checked
 * @return 0 if state is not in polytope or 1 if it is
 */
int state_in_polytope(polytope *polytope, gsl_vector *x);

/**
 * @brief Projects polytope on lower dimensions (e.g. new_dimension = n => projects polytope on first n columns)
 * @param polytope
 * @param new_dimension number of dimensions to project on
 */
void polytope_project(polytope *polytope, size_t new_dimension);

/**
 * @brief Reduces redundant number of rows of polytope
 *
 * Removes redundant inequalities in the hyperplane representation
 * of the polytope with the algorithm described at
 * http://www.ifor.math.ethz.ch/~fukuda/polyfaq/node24.html
 * by solving one LP for each facet
 *
 * Warning:
 * - nonEmptyBounded == 0 case does not exist
 *
 * @param polytope
 */
void polytope_reduce(polytope *polytope);

//void polytope_list_push(polytope_list **list_head, gsl_vector * newVector, double newValue);


#endif //CIMPLE_POLYTOPE_LIBRARY_CIMPLE_H
