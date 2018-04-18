//
// Created by be107admin on 11.04.18.
//
#include "cimple_minksum_wrapper.h"

VPolytope cdd_to_VPolytope(dd_PolyhedraPtr original){
    dd_MatrixPtr vertices = dd_CopyGenerators(original);
    VPolytope returnPolytope;
    for (int i = 0; i < vertices->rowsize; i++) {
        double is_vertex = dd_get_d(vertices->matrix[i][0]);
        if(is_vertex == 1){
            Vector vertex(vertices->colsize-1);
            for (int j = 1; j < vertices->colsize; j++) {
                double value = dd_get_d(vertices->matrix[i][j]);
                vertex[j-1] = value;
            }
            returnPolytope.append(vertex);
        }

    }
    return returnPolytope;
};

dd_PolyhedraPtr VPolytope_to_cdd(VPolytope *original){
    dd_PolyhedraPtr returnPolytope;


    dd_MatrixPtr vertices_matrix = dd_CreateMatrix((*original).coldim(),(*original).rowdim()+1);
    vertices_matrix->representation = dd_Generator;
    dd_ErrorType err;

    for (size_type i = 0; i < (*original).coldim(); ++i) {
        // build cdd's matrix row by row
        // recall that the coefficient matrix m is transposed for efficiency reason

        // because the first column contains a one
        dd_set_d(vertices_matrix->matrix[i][0], 1);

        for (size_type j = 0; j < (*original).rowdim(); ++j) {
            dd_set_d(vertices_matrix->matrix[i][j+1], (*original)[i][j].get_d());
        }
    }

    returnPolytope = dd_DDMatrix2Poly(vertices_matrix, &err);
    return returnPolytope;
};

//extern "C" dd_PolyhedraPtr returnPoly(){
//    dd_MatrixPtr constraints;
//    constraints = dd_CreateMatrix(2, 2);
//    dd_set_d(constraints->matrix[0][0],1.2);
//    dd_set_d(constraints->matrix[1][0],1);
//    dd_set_d(constraints->matrix[0][1],-10);
//    dd_set_d(constraints->matrix[1][1],1);
//
//    constraints->representation=dd_Inequality;
//    dd_ErrorType err =dd_NoError;
//
//    dd_PolyhedraPtr newPoly = dd_DDMatrix2Poly(constraints, &err);
//    VPolytope polyA = cdd_to_VPolytope(newPoly);
//    dd_FreePolyhedra(newPoly);
//    dd_PolyhedraPtr returnPoly = VPolytope_to_cdd(&polyA);
//    dd_FreeMatrix(constraints);
//    return returnPoly;
//};
//
extern "C" dd_PolyhedraPtr cdd_minkowski(dd_PolyhedraPtr A,
                                              dd_PolyhedraPtr B) {

    VPolytope polytope_A = cdd_to_VPolytope(A);
    VPolytope polytope_B = cdd_to_VPolytope(B);
    VPolytopeList polytopeList;
    polytopeList.append(polytope_A);
    polytopeList.append(polytope_B);

    VPolytope output;
    polytopeList.incMinkSumSetup();
    while (polytopeList.hasMoreVertices()) {
        SumVertex sumVertex = polytopeList.incExploreStepFast();
        output.append(sumVertex.coord());
    }

    dd_PolyhedraPtr returnPolytope = VPolytope_to_cdd(&output);
    return returnPolytope;
};
