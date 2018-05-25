cmake_minimum_required(VERSION 3.8)
project(Cimple)

set(CMAKE_C_STANDARD 99)
find_package(PkgConfig REQUIRED)
find_path(GUROBI_INCLUDE_DIR NAMES gurobi_c.h PATHS "/opt/gurobi752/linux64/include")
find_library(GUROBI_LIBRARY NAMES gurobi75 PATHS "/opt/gurobi752/linux64/lib")
set(GUROBI_INCLUDE_DIRS "${GUROBI_INCLUDE_DIR}" )
set(GUROBI_LIBRARIES "${GUROBI_LIBRARY}")
pkg_check_modules( gsl REQUIRED gsl )
include_directories(${GUROBI_INCLUDE_DIRS})
set(MINKSUM_DIR
        "/usr/local/include/MINKSUM_1.8/lib-src"
        "/usr/local/include/MINKSUM_1.8/src"
        "/usr/local/include/MINKSUM_1.8/wrap-gmp-gmpxx"
        )
include_directories(${MINKSUM_DIR})
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -std=c99 -Wall -Werror -O0 -g -m64 -pthread -DGMPRATIONAL")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -m64 -pthread -DGMPRATIONAL")
set(SOURCE_FILES
        main.c
        cimple_minksum_wrapper.cpp
        cimple_minksum_wrapper.h
        cimple_auxiliary_functions.c
        cimple_auxiliary_functions.h
        cimple_controller.c
        cimple_controller.h
        cimple_system.c
        cimple_system.h
        cimple_c_from_py.c
        cimple_c_from_py.h
        cimple_gsl_library_extension.c
        cimple_gsl_library_extension.h
        cimple_polytope_library.c
        cimple_polytope_library.h
        cimple_mpc_computation.c
        cimple_mpc_computation.h
        cimple_safe_mode.c
        cimple_safe_mode.h)
add_executable(Cimple ${SOURCE_FILES} ${MINKSUM_SOURCE})
target_link_libraries( Cimple
        ${gsl_LIBRARIES}
        ${GUROBI_LIBRARIES}
        /usr/local/include/MINKSUM_1.8/lib-src/libMINKSUM.a
        -lgurobi75
        -lcddgmp
        -lgmp
        -lgmpxx
        -lm)