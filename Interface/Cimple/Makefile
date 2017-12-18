# -*- mode: Makefile -*-
#---------------------------------------
CC ?= /usr/bin/gcc

CFLAGS ?= -std=c99 -g -Wall -Werror -O0 -c -DPOLKA_NUM=1
 
LDFLAGS = -lm -lz -lgsl -lgslcblas -ldl -lutil -lpthread -lpython2.7 -lpolkai

INC = -I/usr/include -I/usr/include/python2.7 

src = $(wildcard *.c)
obj = $(src:.c=.o)

cimple: $(obj)
	$(CC) -o cimple $^ $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) $(INC) $< -o $@

.PHONY: clean
clean:
	rm -f $(obj) cimple
