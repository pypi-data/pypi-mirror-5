# Makefile for PyMTGP64 (CUDA version)

#DEBUG = -DDEBUG -g -O0

#ARCH = -arch=compute_11
ARCH = -arch=compute_13
#VERB = -Xptxas=-v
#ABI = -m32
ABI = -m64
CUDAPATH = /usr/local/cuda-5.0


NVCC =nvcc ${ABI} ${DEBUG} ${ARCH} -D__STDC_FORMAT_MACROS -I. \
	 -D__STDC_CONSTANT_MACROS ${VERB} -I$(CUDAPATH)/include/ --compiler-options '-fPIC' -O2
CC = g++ -Wall ${ABI} ${DEBUG}  -D__STDC_FORMAT_MACROS  -I. \
	 -D__STDC_CONSTANT_MACROS -fPIC -O2

CUDALINK = -lcuda -lcudart -L$(CUDAPATH)/lib64/

#.SUFFIXES:	.cu .cubin .ptx .bin

all:  objects sample64-cuda pymtgp64

objects: mtgp-print.o mtgp64-fast.o mtgp64dc-param-11213.o mtgp64-cuda.o

sample64-cuda: sample.cpp \
	mtgp64-cuda.o \
	mtgp64dc-param-11213.o \
	mtgp64-fast.o \
	mtgp-print.o
	${CC} -o $@ sample.cpp \
	mtgp64-cuda.o \
	mtgp64dc-param-11213.o \
	mtgp64-fast.o \
	mtgp-print.o \
	${CUDALINK}

mtgp64-cuda.o: mtgp64-cuda.cu mtgp-util.cuh
	${NVCC} -o $@ -c mtgp64-cuda.cu

mtgp64-fast.o: mtgp64-fast.c  mtgp64-fast.h
	${CC} -c -o mtgp64-fast.o mtgp64-fast.c 

pymtgp64: objects
	python setup.py build

install: pymtgp64
	python setup.py install --home $(HOME)/

test:   
	python pymtgp64_test.py
.c.o:
	${CC} -c -o $@ $<

.cpp.o:
	${CC} -c -o $@ $<

clean:
	rm -rf *.o *~ *.cubin *.ptx *.dSYM
	rm -fr build
