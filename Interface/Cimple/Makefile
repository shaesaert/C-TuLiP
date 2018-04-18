# -*- mode: Makefile -*-
#---------------------------------------
CC ?= /usr/bin/gcc

CFLAGS ?= -std=c99 -Wall -Werror -O0 -g -m64 -pthread -DGMPFLOAT
CXXFLAGS ?= -std=c++11 -m64 -pthread -DGMPFLOAT
LDFLAGS = -lm -lgsl -lgslcblas -ldl -lutil -lpthread -ltime -lcddgmp -lgmp -L/opt/gurobi752/linux64/lib/ -lgurobi75

INC = -I/usr/include -I/opt/gurobi752/linux64/include/ -I/usr/local/include/MINKSUM_1.8/lib-src -I/usr/local/include/MINKSUM_1.8/src -I/usr/local/include/MINKSUM_1.8/wrap-gmp-gmpxx -I/usr/local/include/MINKSUM_1.8/external/include

src = $(wildcard *.c)
obj = $(src:.c=.o)

cimple: $(obj)
	$(CC) -o cimple $^ $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) $(INC) $< -o $@

.PHONY: clean
clean:
	rm -f $(obj) cimple
