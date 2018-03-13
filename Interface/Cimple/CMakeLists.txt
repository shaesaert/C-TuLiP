cmake_minimum_required(VERSION 3.8)
project(Cimple)

set(CMAKE_C_STANDARD 99)
find_package( PkgConfig REQUIRED)
find_package(PythonLibs REQUIRED)
pkg_check_modules( gsl REQUIRED gsl )
include_directories(anaconda/envs/Python27/include/python2.7
        /anaconda/envs/Python27/lib
        /anaconda/envs/Python27/include/python2.7/site-packages
        /Users/shaesaert/Documents/GitHub/cvxopt_github/src/C
        /Users/shaesaert/Documents/GitHub/cvxopt_github/src/python
        /anaconda/envs/Python27/include ${PYTHON_INCLUDE_DIRS} )

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS}  -std=c99 -Wall -O0 -g")

set(SOURCE_FILES main.c cimple_controller.c cimple_controller.h cimple_system.c cimple_system.h cimple_c_from_py.c cimple_c_from_py.h act_impl.c act_impl.h cimple_gsl_library_extension.c cimple_gsl_library_extension.h cimple_polytope_library.c cimple_polytope_library.h)
add_executable(Cimple ${SOURCE_FILES})
target_link_libraries( Cimple ${gsl_LIBRARIES} ${PYTHON_LIBRARIES})
