/* \file pymtgp64.c
   \author R. Samadi (LESIA - Observatoire de Paris)
  
  PyMTGP64 : 
 
  This Python module is an interface to MTGP, the Mersenne Twister for 
  Graphic Processors by Mutsuo Saito and Makoto Matsumoto (Hiroshima University).
  It provides random generators for uniform, Normal and Poisson distributions. 
  Only 64-bit floating numbers are handled.

Copyright (c) 2013 R. Samadi (LESIA - Observatoire de Paris)

This is a free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
 
This software is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
 
You should have received a copy of the GNU General Public License
along with this code.  If not, see <http://www.gnu.org/licenses/>.

 

Copyright (c) 2009, 2010 Mutsuo Saito, Makoto Matsumoto and Hiroshima
University.
Copyright (c) 2011, 2012 Mutsuo Saito, Makoto Matsumoto, Hiroshima
University and University of Tokyo.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above
      copyright notice, this list of conditions and the following
      disclaimer in the documentation and/or other materials provided
      with the distribution.
    * Neither the name of the Hiroshima University, The Uinversity
      of Tokyo nor the names of its contributors may be used to
      endorse or promote products derived from this software without
      specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

#include <Python.h>
#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <numpy/arrayobject.h>
#include <time.h>
#include <stdint.h>

#include "mtgp64-const.h"

const char* ProgName = "PyMTGP64";
const char* VersionStr = "1.0";

const char* doc_string = "\t\t\tPyMTGP64\n\n\
This Python module is an interface to MTGP, the Mersenne Twister for Graphic Processors (mtgp64) \n\
by Mutsuo Saito and Makoto Matsumoto (Hiroshima University).\n\
For more details see http://www.math.sci.hiroshima-u.ac.jp/~m-mat/MT/MTGP/ and the reference below.\n\
\n\
The module provides random generators for uniform, Normal and Poisson distributions. Only 64-bit floating numbers are generated.\n\
The random generator for the Poisson distribution exists in two forms.\n\
In the first one the distribution is computed for a single value of the characteristic mean 'lambda'.\n\ 
In the second form, each generated random number can have is own mean value 'lambda'. \n\ 
This is particularly suited for generating Photon noise for a large image. \n\
\n\
The module implements and provides the following methods:\n\
* seeds = init(seed,device=device,block=block) : Initialize the module\n\
* x = uniform(n) : Generates n uniformly distributed random numbers on the real-interval ]0,1[\n\
* (x,y) = normal(n) : Generates two random series of size n Normally distributed\n\
* x = poisson(lambda,n) : Generates a Poisson distribution of mean lambda and size n\n\
* x = poisson_multlamb(lambda) : As poisson() with multiple values of lambda (one for each generated random number)\n\
* free() : Free the state of the pseudo-random number generator\n\
* seeds = seed(value) : Initialize the seed value\n\
* seeds = block_seeds(seeds) : Initialize the seed associated with each block\n\
* block_num() : Return the number of blocks\n\
* device() : Return the device index\n\
\n\
Reference: Mutsuo Saito, Makoto Matsumoto, Variants of Mersenne Twister Suitable for Graphic Processors, \n\
Transactions on Mathematical Software, 39 (2013), pp. 12:1--12:20, DOI:10.1145/2427023.24270249\n \
\n\
R. Samadi (LESIA - Observatoire de Paris), Nov. 2013\n";

// global variables used by the module:
static struct  mtgp64_kernel_status_t * status = NULL ;  // =NULL  if not yet initialised 
static int block_num = 2 ;
static int device = 0 ; 

// variables and functions implemented elsewhere:
extern const int PARAM_NUM_MAX ;
extern uint64_t * make_uint64_random( struct  mtgp64_kernel_status_t  * d_status, long  num_data, int block_num , int verbose ) ;
extern double * make_double_random( struct  mtgp64_kernel_status_t  * d_status, long  num_data, int block_num , int verbose ) ;
extern struct mtgp64_kernel_status_t * init_status(int block_num, int device ) ;
extern void free_status(struct  mtgp64_kernel_status_t *  d_status ) ; 
extern void init_seeds (struct mtgp64_kernel_status_t * d_status, int  block_num, uint64_t * seeds ) ;
extern int make_double_normal_random(struct mtgp64_kernel_status_t* d_status,  long num_data, int block_num ,  double * * h_data1,  double * *  h_data2, int verbose ) ;
extern long * make_poisson_random(struct mtgp64_kernel_status_t* d_status, long num_data, int block_num, double lam , int verbose ) ;
extern double *  make_poisson_multlam_random(struct mtgp64_kernel_status_t* d_status, long  num_data,  int block_num, double * lam,  int verbose ) ;
extern int get_suitable_block_num(int device, int *max_block_num,
					 int *mp_num, int word_size,
					 int thread_num, int large_size); 

static  void allocation_error() 
{
  PyErr_SetString(PyExc_MemoryError,"PyMTGP64: memory allocation error");
}


int check_init( ) {
  
  if (status == NULL) 
    {
      PyErr_SetString(PyExc_RuntimeError,"PyMTGP64: the module must first be initialised");
      return 0;
    }
  return 1 ; 
}

static PyObject* pymtgp_block_num()
{
  if (check_init()) return Py_BuildValue("i",block_num) ; 
  return Py_None ; 	
}

static PyObject* pymtgp_device()
{  
  if (check_init()) return Py_BuildValue("i",device) ; 
  return Py_None ; 
}

static PyObject* pymtgp_free()
{
  if (status) {
    free_status(status);
    status = NULL ;
  }
  return Py_BuildValue("i",1) ; 
}

uint64_t *  init_block_seeds(uint64_t seed) {

  uint64_t * seeds ;
  int i ; 
  
  seeds = (uint64_t * ) malloc( block_num*sizeof(uint64_t)) ;
  if (seeds == NULL) {
     allocation_error() ;
     pymtgp_free();
     return  NULL ;
   }
   for(  i=0 ; i < block_num ; i++) seeds[i] = seed ;
   init_seeds(status,  block_num,  seeds ) ;
   free(seeds) ; 

   // generated the seeds (one per block)
   seeds = make_uint64_random(status, block_num  , block_num , 0) ;
   if (seeds == NULL) {
     allocation_error() ;
     pymtgp_free();
     return NULL ;
   }
//   for (i=0;i<  block_num  ; i++) fprintf(stderr,"%i %ld\n",i,seeds[i]);
   init_seeds(status,  block_num,  seeds ) ;

   return seeds ;
}

 
static PyObject* pymtgp_block_seeds(PyObject *self, PyObject *args)
{
  PyArrayObject * Oseeds = NULL ; 
  char msg[512];

  if (!PyArg_ParseTuple(args,"O", &Oseeds ))
    return Py_None;


  if( ! check_init() ) {
    return Py_None ;
  }

  if ( (PyArray_TYPE (Oseeds) != NPY_UINT64) &&  (PyArray_TYPE (Oseeds) != NPY_LONG) &&  (PyArray_TYPE (Oseeds) != NPY_INT64)   ) 
    {
      PyErr_SetString(PyExc_ValueError,"PyMTGP64: the input array must an unsigned 64-bit integer or signed 64-bit integer ");
      return Py_None ;

    }
  
   int nd = PyArray_NDIM(Oseeds) ;
   
   if ((nd !=1)) 
    {
      PyErr_SetString(PyExc_ValueError,"PyMTGP64: the input array must be an 1D array");
      //      PyErr_WarnEx(NULL,"PyMTGP64: the input array must be an 1D array",1);
     return Py_None;
    }

    int n = PyArray_DIM(Oseeds,0) ;

   if ((n != block_num )) 
    {
      sprintf(msg,"PyMTGP64: the input array must have a size equal than the block number (bock_num = %d)",block_num);
      PyErr_SetString(PyExc_ValueError,msg);
      return Py_None;
    }

  init_seeds(status,  block_num, ( uint64_t * ) PyArray_DATA(Oseeds) ) ;
  return Py_BuildValue("O",  Oseeds) ;
}

static PyObject* pymtgp_seed(PyObject *self, PyObject *args)
{
  uint64_t seed ;
  uint64_t * seeds = NULL ;
  PyArrayObject * Oseeds = NULL ; 

  if( ! check_init() ) {
    return Py_None ;
  }
  if (!PyArg_ParseTuple(args,"K", &seed ))    return Py_None;

  seeds = init_block_seeds(seed) ;

  if(seeds) {    
      int nd = 1 ;
      npy_intp dims [1] = {block_num} ;
      Oseeds = (PyArrayObject *) PyArray_SimpleNewFromData(nd, dims, NPY_UINT64,seeds) ;
      Oseeds->flags |= NPY_OWNDATA;
      return Py_BuildValue("N",  Oseeds) ;
    }    
  PyErr_SetString(PyExc_RuntimeError,"PyMTGP64: unable to initialize the seeds");
  
  return Py_None ; 
}

static PyObject*  pymtgp_init(PyObject *self, PyObject *args, PyObject *kwds)
{
  uint64_t seed ;
  uint64_t * seeds ;
  PyArrayObject * Oseeds = NULL ; 
  int mb, mp;
  int  block_num_max  ; 
  block_num = 0 ;
  char msg[512];
  static char *kwlist[] = {"","device","block", NULL};

  if (!PyArg_ParseTupleAndKeywords(args,kwds,"K|ii",kwlist , &seed,&device,&block_num ))
    return Py_None;

  if( status != NULL) {
    pymtgp_free();
  }
  if(block_num <=0) {
    block_num = get_suitable_block_num(device,
					   &mb,
					   &mp,
					   sizeof(uint64_t),
					   THREAD_NUM,
					   LARGE_SIZE);
    sprintf(msg,"PyMTGP64: the suitable number of blocks for device %d is a multiple of %d, or %d. We choose by default %d\n", device , block_num,     (mb - 1) * mp, block_num);
    PyErr_WarnEx(NULL,msg,1);
    
 }
  if (BLOCK_NUM_MAX < PARAM_NUM_MAX) {
    block_num_max = BLOCK_NUM_MAX;
  } else {
    block_num_max = PARAM_NUM_MAX;
  }

  if (block_num < 1 || block_num > block_num_max) {
    sprintf(msg,"PyMTGP64: block_num (%d) should be between 1 and %d\n",block_num , block_num_max);
    PyErr_SetString(PyExc_ValueError,msg);
    return Py_None;
  }

  status = init_status(block_num, device) ; 
  if (status == NULL) {
     allocation_error() ;
     return Py_None ; 
  }
  seeds =  init_block_seeds(seed) ; 
  if ( seeds == NULL ) {
    PyErr_SetString(PyExc_RuntimeError,"PyMTGP64: unable to initialize the seeds");
    return Py_None;
  }
  
  int nd = 1 ;
  npy_intp dims [1] = {block_num} ;
  Oseeds = (PyArrayObject *) PyArray_SimpleNewFromData(nd, dims, NPY_UINT64,seeds) ;
  Oseeds->flags |= NPY_OWNDATA;
  return Py_BuildValue("N",  Oseeds) ;
}

static PyObject* uniform(PyObject *self, PyObject *args)
{

  PyArrayObject * Ox = NULL;
  long int n ; 

  if (!PyArg_ParseTuple(args,"l",&n))
    return NULL;

  if( ! check_init() ) {
    return NULL ;
  }

    int nd = 1 ;
    npy_intp dims [1] = {n} ;
    double * values ;
    values = make_double_random(status,n,block_num,0);
    if (values)  {
      Ox = (PyArrayObject *) PyArray_SimpleNewFromData(nd, dims, NPY_DOUBLE,values) ;
      Ox->flags |= NPY_OWNDATA;
    }
    else
      {
	allocation_error() ;
	return Py_None ; 
      }
    return  Py_BuildValue("N",  Ox  ) ;
}

static PyObject* poisson(PyObject *self, PyObject *args)
{

  PyArrayObject * Ox  ; 
  double lambda ; 
  Ox = NULL;
  long  n  ; 
  long * values ; 

  if (!PyArg_ParseTuple(args,"dl", &lambda , &n ))
    return NULL;

   if( ! check_init() ) {
    return NULL ;
  }


    int nd = 1 ;
    npy_intp dims [1] = {n} ;
    values = make_poisson_random(status,n,block_num,lambda,0); 
  if (values)  {
      Ox = (PyArrayObject *) PyArray_SimpleNewFromData(nd, dims, NPY_LONG,values) ;
      Ox->flags |= NPY_OWNDATA;
    }
    else
      {
        allocation_error() ;
        return Py_None ;
      }
  return  Py_BuildValue("N",  Ox  ) ;
}

static PyObject* poisson_multlam(PyObject *self, PyObject *args)
{

  PyArrayObject * Ox  ; 
  PyArrayObject * Olam  ; 
  Ox = NULL; Olam = NULL ;
  double * values ; 
  long n ,i ;

  if (!PyArg_ParseTuple(args,"O", &Olam ))
    return NULL;

   if( ! check_init() ) {
    return NULL ;
  }

   if( PyArray_NDIM(Olam) !=1   )
    {
      PyErr_SetString(PyExc_ValueError,"PyMTGP64: lambda must be an 1D array");
      return 0;
    }
   n = PyArray_DIM(Olam,0) ; // number elements in Olam

    if ( PyArray_TYPE (Olam) != NPY_DOUBLE   ) 
    {
      PyErr_SetString(PyExc_ValueError,"PyMTGP64: lambda must be an array of double (64 bits)");
      return 0;
    }
  
    int nd = 1 ;
    npy_intp dims [1] = {n} ;    

    values = make_poisson_multlam_random(status,n,block_num,  (double *)  PyArray_DATA(Olam),  0 ); 

  if (values)  {
    Ox = (PyArrayObject *) PyArray_SimpleNew(nd, dims, NPY_LONG) ; 
  
    for ( i=0 ; i <n ; i++)  
      ((long * )	PyArray_DATA(Ox))[i] = (long ) ( round(values[i]) )  ; 
      
    
    Ox->flags |= NPY_OWNDATA;
    free(values);
  }
    else
      {
        return Py_None ;
      }
  return  Py_BuildValue("N",  Ox  ) ;
}

static PyObject* normal(PyObject *self, PyObject *args)
{

  PyArrayObject * Ox , * Oy ; 
  double  * x , * y   ; 
  long int n ; 
  int ok ; 
  Ox = NULL;
  Oy = NULL;
  x = NULL ;
  y = NULL ; 

  if (!PyArg_ParseTuple(args,"l",  &n))
    return NULL;
    int nd = 1 ;
    npy_intp dims [1] = {n} ;

    ok = make_double_normal_random(status,n,block_num,&x,&y,0);

    if ( ok & (x !=NULL) & (y != NULL) )  {
      Ox = (PyArrayObject *) PyArray_SimpleNewFromData(nd, dims, NPY_DOUBLE,x) ;
      Ox->flags |= NPY_OWNDATA;
      Oy = (PyArrayObject *) PyArray_SimpleNewFromData(nd, dims, NPY_DOUBLE,y) ;
      Oy->flags |= NPY_OWNDATA;
    }
    else {
	if (x) free(x) ;
	if (y) free(y) ; 
      	allocation_error() ;
	return Py_None ; 
    }

  return   Py_BuildValue("NN",  Ox , Oy ) ;
}

static PyMethodDef pymtgpMethods[] = 
  {
    {"uniform",uniform, METH_VARARGS,"x = uniform(mt,n)\n\nGenerates n uniformly distributed random numbers in the real interval ]0,1[  (opened interval)."},
    {"normal",normal, METH_VARARGS,"(x,y) = normal(n)\n\nGenerates two random series of size n Normally distributed with zero mean and variance one. "},
    {"poisson",poisson, METH_VARARGS,"x = poisson(lambda,n)\n\nGenerates a Poisson distribution of mean lambda and size n."},
    {"poisson_multlam",poisson_multlam, METH_VARARGS,"x = poisson_multlamb(lambda)\n\nGenerates a Poisson distribution. While poisson works with a single value of 'lambda', this functions considers multiple values of lambda. i.e one for each generated random number. lambda must have as many elements as the number of random values desired. "},
    {"init",pymtgp_init, METH_VARARGS | METH_KEYWORDS,"seeds = init(seed,device=device,block=block)\n\nFunction used to initialise the seed, the GPU device and the pseudo-random number generator. Return the seeds associated with each block."},
    {"free",pymtgp_free, METH_NOARGS,"free()\nFree the state of the pseudo-random number generator."},
     {"seed",pymtgp_seed, METH_VARARGS,"seeds= seed(value)\nInitialize the seed value (a single unsigned 64-bit integer). Returns the seed associated with each block (array of  unsigned 64-bit integers). "},
    {"block_seeds",pymtgp_block_seeds, METH_VARARGS,"block_seeds(seeds)\nInitialize the seed associated with each block. 'seeds' must be an array of  unsigned 64-bit integers. "},
    {"block_num",pymtgp_block_num, METH_NOARGS,"block_num()\nReturn the number of blocks."},
    {"device",pymtgp_device, METH_NOARGS,"device()\nReturn the device index on which PyMTGP is operating."},
    {NULL, NULL, 0, NULL}
  };


PyMODINIT_FUNC initpymtgp64(void)
{
  //  (void)Py_InitModule("pymtgp64", pymtgpMethods);
  (void) Py_InitModule3("pymtgp64",pymtgpMethods  , doc_string  ) ; 
  import_array();
  
}
 

