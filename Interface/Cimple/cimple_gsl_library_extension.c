//
// Created by be107admin on 9/25/17.
//

#include "cimple_gsl_library_extension.h"

void gsl_matrix_print(gsl_matrix *matrix, char *name){
    printf("\n%s =\n", name);
    for(size_t i = 0; i < matrix->size1; i++){
        for(size_t j = 0; j<matrix->size2; j++){
            double k = gsl_matrix_get(matrix, i, j);
            printf(" %.3f,", k);
        }
        printf("\n");
    }
}
void gsl_vector_print(gsl_vector *vector, char *name){
    printf("\n%s =\n", name);
    for(size_t i = 0; i < vector->size; i++){
        double k = gsl_vector_get(vector, i);
        printf(" %.3f,", k);
        printf("\n");
    }
}
void gsl_vector_from_array(gsl_vector *vector, double *array, char* name){
    for(size_t j = 0; j<vector->size; j++){
        gsl_vector_set(vector, j, array[j]);
    }
    gsl_vector_print(vector, name);
    fflush(stdout);
};

void gsl_matrix_from_array(gsl_matrix *matrix, double *array, char* name){
    for(size_t i = 0; i < matrix->size1; i++){
        for(size_t j = 0; j<matrix->size2; j++){
            gsl_matrix_set(matrix, i, j, array[j+matrix->size2*i]);
        }
    }
    gsl_matrix_print(matrix, name);
    fflush(stdout);
};

gsl_matrix * gsl_matrix_diag_from_vector(gsl_vector * X){
    gsl_matrix * mat = gsl_matrix_alloc(X->size, X->size);
    gsl_vector_view diag = gsl_matrix_diagonal(mat);
    gsl_matrix_set_all(mat, 0.0); //or whatever number you like
    gsl_vector_memcpy(&diag.vector, X);
    return mat;
}

int gsl_matrix_to_qpterm_gurobi(gsl_matrix *P, GRBmodel *model, size_t N){

    int error = 0;
    int qrow[N*N];
    int qcol[N*N];
    double qval[N*N];
    for(size_t i = 0; i < N; i++){
        for(size_t j = 0; j < N; j++){
            qrow[i*N+j]=(int)i;
            qcol[i*N+j]=(int)j;
            qval[i*N+j]=gsl_matrix_get(P,i,j);
        }
    }
    error = GRBaddqpterms(model, (int)(N*N), qrow, qcol, qval);

    return error;
};

int gsl_vector_to_linterm_gurobi(gsl_vector *q, GRBmodel *model, size_t N){

    int error = 0;
    for(size_t i =0; i < N; i++){
        error = GRBsetdblattrelement(model, GRB_DBL_ATTR_OBJ, 0, gsl_vector_get(q,i));
        if(error){
            return error;
        }
    }
    return error;
};
