# -*- mode: Makefile -*-
#---------------------------------------
CC ?= /usr/bin/gcc

CFLAGS ?= -std=c99 -Wall -Werror -O0 -g -m64 -pthread -DGMPRATIONAL
CXXFLAGS ?= -std=c++11 -m64 -pthread -DGMPRATIONAL
LDFLAGS = -lm \
          -lgsl \
          -lgslcblas \
          -ldl \
          -lutil
          -lpthread \
          -ltime \
          -lcddgmp \
          -lgmp \
          -lgmpxx \
          -L/opt/gurobi752/linux64/lib/ \
          -L/usr/local/include/MINKSUM_1.8/lib-src/libMINKSUM.a \
          -lgurobi75


INC = -I/usr/include \
      -I/opt/gurobi752/linux64/include/ \
      -I/usr/local/include/MINKSUM_1.8/lib-src \
      -I/usr/local/include/MINKSUM_1.8/src \
      -I/usr/local/include/MINKSUM_1.8/wrap-gmp-gmpxx

src = $(wildcard *.c)
obj = $(src:.c=.o)

cimple: $(obj)
	$(CC) -o cimple $^ $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) $(INC) $< -o $@

.PHONY: clean
clean:
	rm -f $(obj) cimple
