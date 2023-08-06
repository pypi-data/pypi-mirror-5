/* \file mtgp64-cuda.cu
   \author R. Samadi (LESIA - Observatoire de Paris)
  
  This source file is part of the Python module PyMTGP64. 
  
  It is the CUDA implementation of MTGP, the Mersenne Twister for 
  Graphic Processors by Mutsuo Saito and Makoto Matsumoto (Hiroshima University).
  It provides random generators for uniform, Normal and Poisson distributions. 
  Only 64-bit floating numbers are generated.

  This source file was adapted from the original file named mtgp64-cuda.cu 
  and developped by Mutsuo Saito and Makoto Matsumoto (see copyright below).

Copyright (c) 2013 by R. Samadi (LESIA - Observatoire de Paris)

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
#include <stdio.h>
#include <cuda.h>
#include <stdint.h>
#include <inttypes.h>
#include <errno.h>
#include <stdlib.h>
#include <math.h>

#include "sample-cuda.h"
#include "mtgp-util.cuh"
//#include "mtgp-print.h"
#include "mtgp64-fast.h"
#include "mtgp64-const.h"
#include<sm_13_double_functions.h>

#define PI 3.14159265358979311599796346854418516

extern const int mtgpdc_params_11213_num;
extern mtgp64_params_fast_t mtgp64dc_params_fast_11213[];


/**
 * kernel I/O
 * This structure must be initialized before first use.
 */
struct mtgp64_kernel_status_t {
    uint64_t status[MTGPDC_N];
};

/*
 * Generator Parameters.
 */
__constant__ uint32_t pos_tbl[BLOCK_NUM_MAX];
__constant__ uint32_t sh1_tbl[BLOCK_NUM_MAX];
__constant__ uint32_t sh2_tbl[BLOCK_NUM_MAX];
__constant__ uint32_t mask[2];
__constant__ uint32_t param_tbl[BLOCK_NUM_MAX][TBL_SIZE];
__constant__ uint32_t temper_tbl[BLOCK_NUM_MAX][TBL_SIZE];
__constant__ uint32_t double_temper_tbl[BLOCK_NUM_MAX][TBL_SIZE];

/**
 * Shared memory
 * The generator's internal status vector.
 */
__shared__ uint32_t status[2][LARGE_SIZE]; /* 512 * 3 elements, 12288 bytes. */

/**
 * The function of the recursion formula calculation.
 *
 * @param[out] RH 32-bit MSBs of output
 * @param[out] RL 32-bit LSBs of output
 * @param[in] X1H MSBs of the farthest part of state array.
 * @param[in] X1L LSBs of the farthest part of state array.
 * @param[in] X2H MSBs of the second farthest part of state array.
 * @param[in] X2L LSBs of the second farthest part of state array.
 * @param[in] YH MSBs of a part of state array.
 * @param[in] YL LSBs of a part of state array.
 * @param[in] bid block id.
 */
__device__ void para_rec(uint32_t *RH,
			 uint32_t *RL,
			 uint32_t X1H,
			 uint32_t X1L,
			 uint32_t X2H,
			 uint32_t X2L,
			 uint32_t YH,
			 uint32_t YL,
			 int bid) {
    uint32_t XH = (X1H & mask[0]) ^ X2H;
    uint32_t XL = (X1L & mask[1]) ^ X2L;
    uint32_t MAT;

    XH ^= XH << sh1_tbl[bid];
    XL ^= XL << sh1_tbl[bid];
    YH = XL ^ (YH >> sh2_tbl[bid]);
    YL = XH ^ (YL >> sh2_tbl[bid]);
    MAT = param_tbl[bid][YL & 0x0f];
    *RH = YH ^ MAT;
    *RL = YL;
}

/**
 * The tempering function.
 *
 * @param[in] VH MSBs of the output value should be tempered.
 * @param[in] VL LSBs of the output value should be tempered.
 * @param[in] TL LSBs of the tempering helper value.
 * @param[in] bid block id.
 * @return[in] the tempered value.
 */
__device__ uint64_t temper(uint32_t VH,
			   uint32_t VL,
			   uint32_t TL,
			   int bid) {
    uint32_t MAT;
    uint64_t r;
    TL ^= TL >> 16;
    TL ^= TL >> 8;
    MAT = temper_tbl[bid][TL & 0x0f];
    VH ^= MAT;
    r = ((uint64_t)VH << 32) | VL;
    return r;
}

/**
 * The tempering and converting function.
 * By using the preset-ted table, converting to IEEE format
 * and tempering are done simultaneously.
 *
 * @param[in] VH MSBs of the output value should be tempered.
 * @param[in] VL LSBs of the output value should be tempered.
 * @param[in] TL LSBs of the tempering helper value.
 * @param[in] bid block id.
 * @return the tempered and converted value.
 */
__device__ uint64_t temper_double(uint32_t VH,
				  uint32_t VL,
				  uint32_t TL,
				  int bid) {
    uint32_t MAT;
    uint64_t r;
    TL ^= TL >> 16;
    TL ^= TL >> 8;
    MAT = double_temper_tbl[bid][TL & 0x0f];
    r = ((uint64_t)VH << 32) | VL;
    r = (r >> 12) ^ ((uint64_t)MAT << 32);
    return r;
}
/**
 * The tempering and converting function.
 * By using the preset-ted table, converting to IEEE format
 * and tempering are done simultaneously.
 *
 * @param[in] VH MSBs of the output value should be tempered.
 * @param[in] VL LSBs of the output value should be tempered.
 * @param[in] TL LSBs of the tempering helper value.
 * @param[in] bid block id.
 * @return the tempered and converted value.
 */
__device__ uint64_t temper_double_open(uint32_t VH,
				  uint32_t VL,
				  uint32_t TL,
				  int bid) {
    uint32_t MAT;
    uint64_t r;
    TL ^= TL >> 16;
    TL ^= TL >> 8;
    MAT = double_temper_tbl[bid][TL & 0x0f];
    r = ((uint64_t)VH << 32) | VL;
    r = (  ( r >> 12 ) ^ ((uint64_t)MAT << 32) ) | 1 ; 
    return r;
}

/**
 * Read the internal state vector from kernel I/O data, and
 * put them into shared memory.
 *
 * @param[out] status shared memory.
 * @param[in] d_status kernel I/O data
 * @param[in] bid block id
 * @param[in] tid thread id
 */
__device__ void status_read(uint32_t status[2][LARGE_SIZE],
			    const mtgp64_kernel_status_t *d_status,
			    int bid,
			    int tid) {
    uint64_t x;

    x = d_status[bid].status[tid];
    status[0][LARGE_SIZE - N + tid] = x >> 32;
    status[1][LARGE_SIZE - N + tid] = x & 0xffffffff;
    if (tid < N - THREAD_NUM) {
	x = d_status[bid].status[THREAD_NUM + tid];
	status[0][LARGE_SIZE - N + THREAD_NUM + tid] = x >> 32;
	status[1][LARGE_SIZE - N + THREAD_NUM + tid] = x & 0xffffffff;
    }
    __syncthreads();
}

/**
 * Read the internal state vector from shared memory, and
 * write them into kernel I/O data.
 *
 * @param[out] status shared memory.
 * @param[in] d_status kernel I/O data
 * @param[in] bid block id
 * @param[in] tid thread id
 */
__device__ void status_write(mtgp64_kernel_status_t *d_status,
			     const uint32_t status[2][LARGE_SIZE],
			     int bid,
			     int tid) {
    uint64_t x;

    x = (uint64_t)status[0][LARGE_SIZE - N + tid] << 32;
    x = x | status[1][LARGE_SIZE - N + tid];
    d_status[bid].status[tid] = x;
    if (tid < N - THREAD_NUM) {
	x = (uint64_t)status[0][4 * THREAD_NUM - N + tid] << 32;
	x = x | status[1][4 * THREAD_NUM - N + tid];
	d_status[bid].status[THREAD_NUM + tid] = x;
    }
    __syncthreads();
}

/**
 * kernel function.
 * This function generates 64-bit unsigned integers in d_data
 *
 * @param[in,out] d_status kernel I/O data
 * @param[out] d_data output
 * @param[in] size number of output data requested.
 */
__global__ void mtgp64_uint64_kernel(mtgp64_kernel_status_t* d_status,
				     uint64_t* d_data, int size) {
    const int bid = blockIdx.x;
    const int tid = threadIdx.x;
    int pos = pos_tbl[bid];
    uint32_t YH;
    uint32_t YL;
    uint64_t o;

    // copy status data from global memory to shared memory.
    status_read(status, d_status, bid, tid);

    // main loop
    for (int i = 0; i < size; i += LARGE_SIZE) {

#if defined(DEBUG) && defined(__DEVICE_EMULATION__)
	if ((i == 0) && (bid == 0) && (tid <= 1)) {
	    printf("status[0][LARGE_SIZE - N + tid]:%08x\n",
		   status[0][LARGE_SIZE - N + tid]);
	    printf("status[1][LARGE_SIZE - N + tid]:%08x\n",
		   status[1][LARGE_SIZE - N + tid]);
	    printf("status[0][LARGE_SIZE - N + tid + 1]:%08x\n",
		   status[0][LARGE_SIZE - N + tid + 1]);
	    printf("status[1][LARGE_SIZE - N + tid + 1]:%08x\n",
		   status[1][LARGE_SIZE - N + tid + 1]);
	    printf("status[0][LARGE_SIZE - N + tid + pos]:%08x\n",
		   status[0][LARGE_SIZE - N + tid + pos]);
	    printf("status[1][LARGE_SIZE - N + tid + pos]:%08x\n",
		   status[1][LARGE_SIZE - N + tid + pos]);
	    printf("sh1:%d\n", sh1_tbl[bid]);
	    printf("sh2:%d\n", sh2_tbl[bid]);
	    printf("high_mask:%08x\n", mask[0]);
	    printf("low_mask:%08x\n", mask[1]);
	    for (int j = 0; j < 16; j++) {
		printf("tbl[%d]:%08x\n", j, param_tbl[0][j]);
	    }
	}
#endif
	para_rec(&YH,
		 &YL,
		 status[0][LARGE_SIZE - N + tid],
		 status[1][LARGE_SIZE - N + tid],
		 status[0][LARGE_SIZE - N + tid + 1],
		 status[1][LARGE_SIZE - N + tid + 1],
		 status[0][LARGE_SIZE - N + tid + pos],
		 status[1][LARGE_SIZE - N + tid + pos],
		 bid);
	status[0][tid] = YH;
	status[1][tid] = YL;
#if defined(DEBUG) && defined(__DEVICE_EMULATION__)
	if ((i == 0) && (bid == 0) && (tid <= 1)) {
	    printf("status[0][tid]:%08x\n",	status[0][tid]);
	    printf("status[1][tid]:%08x\n",	status[1][tid]);
	}
#endif
	o = temper(YH,
		   YL,
		   status[1][LARGE_SIZE - N + tid + pos - 1],
		   bid);
#if defined(DEBUG) && defined(__DEVICE_EMULATION__)
	if ((i == 0) && (bid == 0) && (tid <= 1)) {
	    printf("o:%016" PRIx64 "\n", o);
	}
#endif
	d_data[size * bid + i + tid] = o;
	__syncthreads();
	para_rec(&YH,
		 &YL,
		 status[0][(4 * THREAD_NUM - N + tid) % LARGE_SIZE],
		 status[1][(4 * THREAD_NUM - N + tid) % LARGE_SIZE],
		 status[0][(4 * THREAD_NUM - N + tid + 1) % LARGE_SIZE],
		 status[1][(4 * THREAD_NUM - N + tid + 1) % LARGE_SIZE],
		 status[0][(4 * THREAD_NUM - N + tid + pos) % LARGE_SIZE],
		 status[1][(4 * THREAD_NUM - N + tid + pos) % LARGE_SIZE],
		 bid);
	status[0][tid + THREAD_NUM] = YH;
	status[1][tid + THREAD_NUM] = YL;
	o = temper(YH,
		   YL,
		   status[1][(4 * THREAD_NUM - N + tid + pos - 1) % LARGE_SIZE],
		   bid);
	d_data[size * bid + THREAD_NUM + i + tid] = o;
	__syncthreads();
	para_rec(&YH,
		 &YL,
		 status[0][2 * THREAD_NUM - N + tid],
		 status[1][2 * THREAD_NUM - N + tid],
		 status[0][2 * THREAD_NUM - N + tid + 1],
		 status[1][2 * THREAD_NUM - N + tid + 1],
		 status[0][2 * THREAD_NUM - N + tid + pos],
		 status[1][2 * THREAD_NUM - N + tid + pos],
		 bid);
	status[0][tid + 2 * THREAD_NUM] = YH;
	status[1][tid + 2 * THREAD_NUM] = YL;
	o = temper(YH,
		   YL,
		   status[1][tid + pos - 1 + 2 * THREAD_NUM - N],
		   bid);
	d_data[size * bid + 2 * THREAD_NUM + i + tid] = o;
	__syncthreads();
    }
    // write back status for next call
    status_write(d_status, status, bid, tid);
}

/**
 * kernel function.
 * This function generates double precision floating point numbers 
 * uniformly distributed in the range ]0,1[  (opened interval).
 *
 * @param[in,out] d_status kernel I/O data
 * @param[out] d_data output. IEEE double precision format.
 * @param[in] size number of output data requested.
 */
__global__ void mtgp64_double_kernel(mtgp64_kernel_status_t* d_status,
				     double* d_data, int size)
{

    const int bid = blockIdx.x;
    const int tid = threadIdx.x;
    int pos = pos_tbl[bid];
    uint32_t YH;
    uint32_t YL;
    uint64_t o;

    // copy status data from global memory to shared memory.
    status_read(status, d_status, bid, tid);

    // main loop
    for (int i = 0; i < size; i += LARGE_SIZE) {
	para_rec(&YH,
		 &YL,
		 status[0][LARGE_SIZE - N + tid],
		 status[1][LARGE_SIZE - N + tid],
		 status[0][LARGE_SIZE - N + tid + 1],
		 status[1][LARGE_SIZE - N + tid + 1],
		 status[0][LARGE_SIZE - N + tid + pos],
		 status[1][LARGE_SIZE - N + tid + pos],
		 bid);
	status[0][tid] = YH;
	status[1][tid] = YL;
	o = temper_double_open(YH,
			  YL,
			  status[1][LARGE_SIZE - N + tid + pos - 1],
			  bid);
	((uint64_t *) d_data)[size * bid + i + tid] = o  ;
	d_data[size * bid + i + tid] -= 1. ;
	__syncthreads();
	para_rec(&YH,
		 &YL,
		 status[0][(4 * THREAD_NUM - N + tid) % LARGE_SIZE],
		 status[1][(4 * THREAD_NUM - N + tid) % LARGE_SIZE],
		 status[0][(4 * THREAD_NUM - N + tid + 1) % LARGE_SIZE],
		 status[1][(4 * THREAD_NUM - N + tid + 1) % LARGE_SIZE],
		 status[0][(4 * THREAD_NUM - N + tid + pos) % LARGE_SIZE],
		 status[1][(4 * THREAD_NUM - N + tid + pos) % LARGE_SIZE],
		 bid);
	status[0][tid + THREAD_NUM] = YH;
	status[1][tid + THREAD_NUM] = YL;
	o = temper_double_open(
	    YH,
	    YL,
	    status[1][(4 * THREAD_NUM - N + tid + pos - 1) % LARGE_SIZE],
	    bid);
	((uint64_t *) d_data)[size * bid + THREAD_NUM + i + tid] = o  ;
	d_data[size * bid + THREAD_NUM + i + tid] -= 1. ;
	__syncthreads();
	para_rec(&YH,
		 &YL,
		 status[0][2 * THREAD_NUM - N + tid],
		 status[1][2 * THREAD_NUM - N + tid],
		 status[0][2 * THREAD_NUM - N + tid + 1],
		 status[1][2 * THREAD_NUM - N + tid + 1],
		 status[0][2 * THREAD_NUM - N + tid + pos],
		 status[1][2 * THREAD_NUM - N + tid + pos],
		 bid);
	status[0][tid + 2 * THREAD_NUM] = YH;
	status[1][tid + 2 * THREAD_NUM] = YL;
	o = temper_double_open(YH,
			  YL,
			  status[1][tid + pos - 1 + 2 * THREAD_NUM - N],
			  bid);
	((uint64_t *)d_data)[size * bid + 2 * THREAD_NUM + i + tid] = o  ;
	d_data[size * bid + 2 * THREAD_NUM + i + tid] -= 1. ;
	__syncthreads();
    }
    // write back status for next call
    status_write(d_status, status, bid, tid);
}

/*
	void mtgp64_double_normal_kernel(mtgp64_kernel_status_t* d_status, double * d_data1,  double * d_data2, int size)

	Computes two sets of normally distributed values from two given sets of uniformly distributed values.


  INPUTS:
  mtgp64_kernel_status_t * d_status : pointer to the structure containing the state vectors
  int block_size : number of values per block

  INPUTS/OUTPUTS:
  double d_data1[n], d_data2[n]:  contain as inputs two given sets of uniformly distributed values, and as outpus the random numbers distributed according to the Normal distribution.  The size of the arrays are  n = block_size * block_number


 R. Samadi
*/

__global__ void mtgp64_double_normal_kernel(mtgp64_kernel_status_t* d_status, double * d_data1,  double * d_data2, int size)

{
    const int bid = blockIdx.x;
    const int tid = threadIdx.x;
    double r1,r2 ;
    int j ;

    //  loop for the calculation of the normally distributed values
    for (int i = 0; i < size; i += THREAD_NUM ) {
      j = size * bid + i + tid ;
      r1 = sqrt(-2.*log(d_data1[j]))  ;
      r2 = d_data2[j] ; 
      d_data1[j] = r1 * cos(2.* PI * r2) ;
      d_data2[j] = r1 * sin(2.* PI * r2) ;
    }
}

/* log-gamma function to support some of these distributions. The 
 * algorithm comes from SPECFUN by Shanjie Zhang and Jianming Jin and their
 * book "Computation of Special Functions", 1996, John Wiley & Sons, Inc.
 */
__device__ double loggam(double x)
{
    double x0, x2, xp, gl, gl0;
    long k, n;
    
    double a[10] = {8.333333333333333e-02,-2.777777777777778e-03,
         7.936507936507937e-04,-5.952380952380952e-04,
         8.417508417508418e-04,-1.917526917526918e-03,
         6.410256410256410e-03,-2.955065359477124e-02,
         1.796443723688307e-01,-1.39243221690590e+00};
    x0 = x;
    n = 0;
    if ((x == 1.0) || (x == 2.0))
    {
        return 0.0;
    }
    else if (x <= 7.0)
    {
        n = (long)(7 - x);
        x0 = x + n;
    }
    x2 = 1.0/(x0*x0);
    xp = 2*PI;
    gl0 = a[9];
    for (k=8; k>=0; k--)
    {
        gl0 *= x2;
        gl0 += a[k];
    }
    gl = gl0/x0 + 0.5*log(xp) + (x0-0.5)*log(x0) - x0;
    if (x <= 7.0)
    {
        for (k=1; k<=n; k++)
        {
            gl -= log(x0-1.0);
            x0 -= 1.0;
        }
    }
    return gl;
}


/*
  void mtgp64_poisson_kernel(mtgp64_kernel_status_t* d_status, long * d_data, int block_size , double lam)
  
  Compute Poisson-distributed random numbers.

  
  INPUTS:
  mtgp64_kernel_status_t * d_status : pointer to the structure containing the state vectors
  int block_size : number of values per block
  double lam : mean value ('lambda') of the Poisson distribution

  OUTPUTS:
  
  double d_data[n]:  the random numbers distributed according to the Poisson distribution.  The size of the array is assumed to be  n = block_size * block_number

  Adapted from rk_poisson_mult and rk_poisson_ptrsand by Robert Kern (robert.kern@gmail.com)

  R. Samadi
*/
__global__ void mtgp64_poisson_kernel(mtgp64_kernel_status_t* d_status, long * d_data, int block_size , double lam)
{

  const int bid = blockIdx.x;
  const int tid = threadIdx.x;
  int pos = pos_tbl[bid];
  uint32_t YH;
  uint32_t YL;
  uint64_t o;
  long k;
  double U, V, slam, loglam, a, b, invalpha, vr, us;
  double prod, enlam;
  int fac[3] = {3,4,2} ;
  int j , m  ; 
  bool cont ; 
  bool notall ;
  __shared__ bool flag[THREAD_NUM] ; 

  if (lam>=10) {
    slam = sqrt(lam);
    loglam = log(lam);
    b = 0.931 + 2.53*slam;
    a = -0.059 + 0.02483*b;
    invalpha = 1.1239 + 1.1328/(b-3.4);
    vr = 0.9277 - 3.6224/(b-2);
  }
  else enlam = exp(-lam);

  // copy status data from global memory to shared memory.
  status_read(status, d_status, bid, tid);

  // main loop
  for (int i = 0; i < block_size; i += THREAD_NUM ) {
    m = block_size * bid + tid  + i ; 
    if( lam<10) {
      k = 0;
      prod = 1.0;
    }
    j = 0 ;
    cont = 1 ;
    notall = 1; 
    flag[tid] = 0 ; 
    while (cont || notall) {
      // generating the random number U
      para_rec(&YH,
	       &YL,
	       status[0][(fac[j]*THREAD_NUM - N + tid) % LARGE_SIZE],
	       status[1][(fac[j]*THREAD_NUM - N + tid) % LARGE_SIZE],
	       status[0][(fac[j]*THREAD_NUM - N + tid + 1) % LARGE_SIZE],
	       status[1][(fac[j]*THREAD_NUM - N + tid + 1) % LARGE_SIZE],
	       status[0][(fac[j]*THREAD_NUM - N + tid + pos) % LARGE_SIZE],
	       status[1][(fac[j]*THREAD_NUM - N + tid + pos) % LARGE_SIZE],
	       bid);
      status[0][tid + j*THREAD_NUM] = YH;
      status[1][tid + j*THREAD_NUM] = YL;
	
      o = temper_double_open(
			YH,
			YL,
			status[1][(fac[j]*THREAD_NUM - N + tid + pos - 1) % LARGE_SIZE],
			bid);
      * ( ( uint64_t * )  (&U) ) = o ; 
      U = 2. - U  ;
      j = (j +1) % 3 ;
      __syncthreads();

      if( lam >= 10) {
	// generating the random number V
	para_rec(&YH,
		 &YL,
		 status[0][(fac[j]*THREAD_NUM - N + tid) % LARGE_SIZE],
		 status[1][(fac[j]*THREAD_NUM - N + tid) % LARGE_SIZE],
		 status[0][(fac[j]*THREAD_NUM - N + tid + 1) % LARGE_SIZE],
		 status[1][(fac[j]*THREAD_NUM - N + tid + 1) % LARGE_SIZE],
		 status[0][(fac[j]*THREAD_NUM - N + tid + pos) % LARGE_SIZE],
		 status[1][(fac[j]*THREAD_NUM - N + tid + pos) % LARGE_SIZE],
		 bid);
	status[0][tid + j*THREAD_NUM] = YH;
	status[1][tid + j*THREAD_NUM] = YL;
	o = temper_double_open(
			  YH,
			  YL,
			  status[1][(fac[j]*THREAD_NUM - N + tid + pos - 1) % LARGE_SIZE],
			  bid);
	* ( ( uint64_t * )  (&V) ) = o ; 
        j = (j +1) % 3 ;
	__syncthreads();
	if (cont) {
	V = 2. - V  ; 
	U = U - 0.5;
        us = 0.5 - fabs(U);
        k = (long)floor((2*a/us + b)*U + lam + 0.43);
        if ((us >= 0.07) && (V <= vr))
	  {
	    d_data[m] = k ;
	    cont = 0 ;
	  }
        else if ((k < 0) ||
            ((us < 0.013) && (V > us)))
	  {
            cont = 1 ;
	  }
        else if ((log(V) + log(invalpha) - log(a/(us*us)+b)) <=
            (-lam + k*loglam - loggam(k+1)))
	  {
	    d_data[m] = k ; 
            cont = 0 ;
	  }
	} // end if (cont)
      } // end if( lam >=10)
      else if (lam >0.)
	{
	  if(cont) {
	  prod *= U;
	  if (prod > enlam)
	    {
	      k += 1;            
	      cont = 1 ;
	    }
	  else  {
		d_data[m] = k;
            	cont = 0 ;
		}
	 } // end if (cont)
	} //end else if ( lam >0)
      else {
	d_data[m] = 0 ; 
	cont = 0 ;
      }
     	if(  ! cont ) flag[tid] = 1 ;
	__syncthreads();
	notall = 0 ;
	for (int p=0 ; (p<THREAD_NUM) & (! notall) ; p++ ) notall = notall || (! flag[p] ) ; 
	__syncthreads();
    } // end while(cont)
  } // end for loop
    // write back status for next call
  status_write(d_status, status, bid, tid);
}

/*
  void mtgp64_poisson_multlam_kernel(mtgp64_kernel_status_t* d_status, double * d_data,  int block_size )

  Compute Poisson-distributed random numbers.

  While mtgp64_poisson_kernel works with a single value of 'lambda', this version considers multiple values of lambda (one for each generated random number).
  
  INPUTS:
  d_status : pointer to the structure containing the state vectors
  block_size : number of values per block

  INPUTS/OUTPUTS:
  
  double d_data[n]:  contains as input the lambda values (mean value of the Poisson distribution),
  and as output the random numbers distributed according to the Poisson distribution.  
  The size of the array is assumed to be  n = block_size * block_number


  Adapted from rk_poisson_mult and rk_poisson_ptrsand by Robert Kern (robert.kern@gmail.com)

  R. Samadi
*/
__global__ void mtgp64_poisson_multlam_kernel(mtgp64_kernel_status_t* d_status, double * d_data,  int block_size )
{
const int bid = blockIdx.x;
  const int tid = threadIdx.x;
  int pos = pos_tbl[bid];
  uint32_t YH;
  uint32_t YL;
  uint64_t o;
  long k;
  double U, V, slam, loglam, a, b, invalpha, vr, us;
  double prod, enlam , lam ;
  int fac[3] = {3,4,2} ;
  int j , m , l  ; 
  bool cont ; 
  bool notall ;
  __shared__ bool flag[THREAD_NUM] ; 

  // copy status data from global memory to shared memory.
  status_read(status, d_status, bid, tid);

  // main loop
  for (int i = 0; i < block_size; i += THREAD_NUM ) {
    m = block_size * bid + tid  + i ; 
    lam = d_data[m] ;
    if( lam<10) {
      k = 0;
      prod = 1.0;
    }
    else {
       slam = sqrt(lam);
      loglam = log(lam);
      b = 0.931 + 2.53*slam;
      a = -0.059 + 0.02483*b;
      invalpha = 1.1239 + 1.1328/(b-3.4);
      vr = 0.9277 - 3.6224/(b-2);
    }
    j = 0 ;
    cont = 1 ;
    notall = 1; 
    flag[tid] = 0 ; 
    while (cont || notall) {
      // generating the random number U
      para_rec(&YH,
	       &YL,
	       status[0][(fac[j]*THREAD_NUM - N + tid) % LARGE_SIZE],
	       status[1][(fac[j]*THREAD_NUM - N + tid) % LARGE_SIZE],
	       status[0][(fac[j]*THREAD_NUM - N + tid + 1) % LARGE_SIZE],
	       status[1][(fac[j]*THREAD_NUM - N + tid + 1) % LARGE_SIZE],
	       status[0][(fac[j]*THREAD_NUM - N + tid + pos) % LARGE_SIZE],
	       status[1][(fac[j]*THREAD_NUM - N + tid + pos) % LARGE_SIZE],
	       bid);
      status[0][tid + j*THREAD_NUM] = YH;
      status[1][tid + j*THREAD_NUM] = YL;
	
      o = temper_double_open(
			YH,
			YL,
			status[1][(fac[j]*THREAD_NUM - N + tid + pos - 1) % LARGE_SIZE],
			bid);
      * ( ( uint64_t * )  (&U) ) = o ; 
      U = 2. - U  ;
      j = (j +1) % 3 ;
      __syncthreads();
	// generating the random number V
	para_rec(&YH,
		 &YL,
		 status[0][(fac[j]*THREAD_NUM - N + tid) % LARGE_SIZE],
		 status[1][(fac[j]*THREAD_NUM - N + tid) % LARGE_SIZE],
		 status[0][(fac[j]*THREAD_NUM - N + tid + 1) % LARGE_SIZE],
		 status[1][(fac[j]*THREAD_NUM - N + tid + 1) % LARGE_SIZE],
		 status[0][(fac[j]*THREAD_NUM - N + tid + pos) % LARGE_SIZE],
		 status[1][(fac[j]*THREAD_NUM - N + tid + pos) % LARGE_SIZE],
		 bid);
	status[0][tid + j*THREAD_NUM] = YH;
	status[1][tid + j*THREAD_NUM] = YL;
	o = temper_double_open(
			  YH,
			  YL,
			  status[1][(fac[j]*THREAD_NUM - N + tid + pos - 1) % LARGE_SIZE],
			  bid);
	* ( ( uint64_t * )  (&V) ) = o ; 
        j = (j +1) % 3 ;
	__syncthreads();

	if (cont) {
      if( lam >= 10) {
	V = 2. - V  ; 
	U = U - 0.5;
        us = 0.5 - fabs(U);
        k = (long)floor((2*a/us + b)*U + lam + 0.43);
        if ((us >= 0.07) && (V <= vr))
	  {
	    d_data[m] = k ;
	    cont = 0 ;
	  }
        else if ((k < 0) ||
            ((us < 0.013) && (V > us)))
	  {
            cont = 1 ;
	  }
        else if ((log(V) + log(invalpha) - log(a/(us*us)+b)) <=
            (-lam + k*loglam - loggam(k+1)))
	  {
	    d_data[m] = k ; 
            cont = 0 ;
	  }
      } // end if( lam >=10)
      else if (lam >0.)
	{
	  l = 0 ;
	  while( (l<2) && (cont) ) {
	    if(l ==0)  prod *= U;
	    else prod *= V;
	    if (prod > enlam)
	      {
		k += 1;            
		cont = 1 ;
	      }
	    else  {
	      d_data[m] = k;
	      cont = 0 ;
	    }
	    l ++ ; 
	  } // end while( (l<2) && (cont) ) 
	} //end else if ( lam >0)
      else{
	d_data[m] = 0 ; 
	cont = 0 ;
 	} 
	}// end if (cont)
	if(  ! cont ) flag[tid] = 1 ;
	__syncthreads();
	notall = 0 ;
	for (int p=0 ; (p<THREAD_NUM) & (! notall) ; p++ ) notall = notall || (! flag[p] ) ; 
	__syncthreads();
    } // end while(cont)
  } // end for loop
    // write back status for next call
  status_write(d_status, status, bid, tid);
}



/**
 * This function initializes kernel I/O data and setups the seed of each block.
 * 
 * 
 * INPUTS:
 * d_status: output kernel I/O data.
 * params: MTGP64 parameters. needed for the initialization.
 * int block_num: the number of blocks
 * uint64_t seeds[block_num]: the block seeds
 * 
 */
extern "C" __host__ void make_kernel_data64(mtgp64_kernel_status_t *d_status,
			mtgp64_params_fast_t params[],
				 int block_num , uint64_t * seeds)
{
    mtgp64_kernel_status_t* h_status
	= (mtgp64_kernel_status_t *) malloc(
	    sizeof(mtgp64_kernel_status_t) * block_num);

    if (h_status == NULL) {
	printf("failure in allocating host memory for kernel I/O data.\n");
	exit(8);
    }
    for (int i = 0; i < block_num; i++) {
	mtgp64_init_state(&(h_status[i].status[0]), &params[i], seeds[i]);
    }
#if defined(DEBUG)
    printf("h_status[0].status[0]:%016"PRIx64"\n", h_status[0].status[0]);
    printf("h_status[0].status[0]:%016"PRIx64"\n", h_status[0].status[1]);
    printf("h_status[0].status[0]:%016"PRIx64"\n", h_status[0].status[2]);
    printf("h_status[0].status[0]:%016"PRIx64"\n", h_status[0].status[3]);
#endif
    ccudaMemcpy(d_status, h_status,
		sizeof(mtgp64_kernel_status_t) * block_num,
		cudaMemcpyHostToDevice);
    free(h_status);
}




/**
 * This function sets constants in device memory.
 * @param[in] params input, MTGP64 parameters.
 */
__host__ void make_constant(const mtgp64_params_fast_t params[],
		   int block_num) {
    const int size1 = sizeof(uint32_t) * block_num;
    const int size2 = sizeof(uint32_t) * block_num * TBL_SIZE;
    uint32_t *h_pos_tbl;
    uint32_t *h_sh1_tbl;
    uint32_t *h_sh2_tbl;
    uint32_t *h_param_tbl;
    uint32_t *h_temper_tbl;
    uint32_t *h_double_temper_tbl;
    uint32_t *h_mask;
    h_pos_tbl = (uint32_t *)malloc(size1);
    h_sh1_tbl = (uint32_t *)malloc(size1);
    h_sh2_tbl = (uint32_t *)malloc(size1);
    h_param_tbl = (uint32_t *)malloc(size2);
    h_temper_tbl = (uint32_t *)malloc(size2);
    h_double_temper_tbl = (uint32_t *)malloc(size2);
    h_mask = (uint32_t *)malloc(sizeof(uint32_t) * 2);
    if (h_pos_tbl == NULL
	|| h_sh1_tbl == NULL
	|| h_sh2_tbl == NULL
	|| h_param_tbl == NULL
	|| h_temper_tbl == NULL
	|| h_double_temper_tbl == NULL
	|| h_mask == NULL
	) {
	printf("failure in allocating host memory for constant table.\n");
	exit(1);
    }
    h_mask[0] = params[0].mask >> 32;
    h_mask[1] = params[0].mask & 0xffffffffU;
    for (int i = 0; i < block_num; i++) {
	h_pos_tbl[i] = params[i].pos;
	h_sh1_tbl[i] = params[i].sh1;
	h_sh2_tbl[i] = params[i].sh2;
	for (int j = 0; j < TBL_SIZE; j++) {
	    h_param_tbl[i * TBL_SIZE + j] = params[i].tbl[j] >> 32;
	    h_temper_tbl[i * TBL_SIZE + j] = params[i].tmp_tbl[j] >> 32;
	    h_double_temper_tbl[i * TBL_SIZE + j]
		= params[i].dbl_tmp_tbl[j] >> 32;
	}
    }
    // copy from malloc area only
    ccudaMemcpyToSymbol(pos_tbl, h_pos_tbl, size1);
    ccudaMemcpyToSymbol(sh1_tbl, h_sh1_tbl, size1);
    ccudaMemcpyToSymbol(sh2_tbl, h_sh2_tbl, size1);
    ccudaMemcpyToSymbol(param_tbl, h_param_tbl, size2);
    ccudaMemcpyToSymbol(temper_tbl, h_temper_tbl, size2);
    ccudaMemcpyToSymbol(double_temper_tbl, h_double_temper_tbl, size2);
    ccudaMemcpyToSymbol(mask, &h_mask, sizeof(uint32_t) * 2);
    free(h_pos_tbl);
    free(h_sh1_tbl);
    free(h_sh2_tbl);
    free(h_param_tbl);
    free(h_temper_tbl);
    free(h_double_temper_tbl);
    free(h_mask);
}


/*
	Returns a number which is close to num_data and a mutliple of  LARGE_SIZE * block_num
*/

__host__ long get_num_unit( long num_data  , int block_num)
{
   long num_unit = LARGE_SIZE * block_num;
   int r;
   r = num_data % num_unit;
   if (r != 0) {
      num_unit = num_data + num_unit - r;
    }
   return num_unit ;
}


/**
 * host function.
 * This function calls corresponding kernel function.
 *
 * @param[in] d_status kernel I/O data.
 * @param[in] num_data number of data to be generated.
 */
extern "C"  __host__ uint64_t *  make_uint64_random(mtgp64_kernel_status_t* d_status,
			 long num_data, int block_num, int verbose = 0) {
    uint64_t* d_data;
    uint64_t* h_data;
    cudaError_t e;
    float gputime;
    long num_unit = get_num_unit(num_data,block_num) ;
    cudaEvent_t start;
    cudaEvent_t end;

    ccudaMalloc((void**)&d_data, sizeof(uint64_t) * num_unit);
    /* CUT_SAFE_CALL(cutCreateTimer(&timer)); */
    ccudaEventCreate(&start);
    ccudaEventCreate(&end);
    h_data = (uint64_t *) malloc(sizeof(uint64_t) * num_data);
    if (h_data == NULL) {
	printf("failure in allocating host memory for output data.\n");
	exit(1);
    }
    /* CUT_SAFE_CALL(cutStartTimer(timer)); */
    ccudaEventRecord(start, 0);
    if (cudaGetLastError() != cudaSuccess) {
	printf("error has been occured before kernel call.\n");	
	free(h_data) ; 
	exit(1);
    }

    /* kernel call */
    mtgp64_uint64_kernel<<< block_num, THREAD_NUM>>>(
	d_status, d_data, num_unit / block_num);
    cudaThreadSynchronize();

    e = cudaGetLastError();
    if (e != cudaSuccess) {
	printf("failure in kernel call.\n%s\n", cudaGetErrorString(e));	
	free(h_data) ; 
	exit(1);
    }
    /* CUT_SAFE_CALL(cutStopTimer(timer)); */
    ccudaEventRecord(end, 0);
    ccudaEventSynchronize(end);
    ccudaMemcpy(h_data, d_data, sizeof(uint64_t) * num_data,
		cudaMemcpyDeviceToHost);
    /* gputime = cutGetTimerValue(timer); */
    if (verbose) {
      ccudaEventElapsedTime(&gputime, start, end);
//      print_uint64_array(h_data, num_data, block_num);
      printf("generated numbers: %d\n", num_data);
      printf("Processing time: %f (ms)\n", gputime);
      printf("Samples per second: %E \n", num_data / (gputime * 0.001));
    }
    /* CUT_SAFE_CALL(cutDeleteTimer(timer)); */
    ccudaEventDestroy(start);
    ccudaEventDestroy(end);
    //free memories
    // free(h_data);
    ccudaFree(d_data);
    return h_data  ;
}

/**
 * host function.
 * This function calls corresponding kernel function.
 * It returns a pointer to an array containing <num_data> random values
 * A NULL pointer is returned in case of failure, 
 *
 * @param[in] d_status kernel I/O data.
 * @param[in] num_data number of data to be generated.
 */
extern "C"  __host__ double * make_double_random(mtgp64_kernel_status_t* d_status,
			long num_data, int block_num , int verbose = 0 ) {
    double* d_data;
    double* h_data;
    cudaError_t e;
    float gputime;
    long num_unit = get_num_unit(num_data,block_num) ;
    cudaEvent_t start;
    cudaEvent_t end;

    ccudaMalloc((void**)&d_data, sizeof(double) * num_unit);
    /* CUT_SAFE_CALL(cutCreateTimer(&timer)); */
    ccudaEventCreate(&start);
    ccudaEventCreate(&end);
    h_data = (double *) malloc(sizeof(double) * num_data);
    if (h_data == NULL) {
	fprintf(stderr,"failure in allocating host memory for output data.\n");
	return 0 ;
    }
    /* CUT_SAFE_CALL(cutStartTimer(timer)); */
    ccudaEventRecord(start, 0);
    if (cudaGetLastError() != cudaSuccess) {
	fprintf(stderr,"error has been occured before kernel call.\n");
	free(h_data) ; 
	return 0 ;
    }

    /* kernel call */
    mtgp64_double_kernel<<< block_num, THREAD_NUM >>>(
	d_status, d_data, num_unit / block_num);
    cudaThreadSynchronize();

    e = cudaGetLastError();
    if (e != cudaSuccess) {
	printf("failure in kernel call.\n%s\n", cudaGetErrorString(e));
	free(h_data) ; 
	return 0;
    }
    /* CUT_SAFE_CALL(cutStopTimer(timer)); */
    ccudaEventRecord(end, 0);
    ccudaEventSynchronize(end);
    ccudaMemcpy(h_data, d_data, sizeof(double) * num_data,
		cudaMemcpyDeviceToHost);
    /* gputime = cutGetTimerValue(timer); */
    if (verbose) {			  
    ccudaEventElapsedTime(&gputime, start, end);

//    print_double_array(h_data, num_data, block_num);
    printf("Generated numbers: %d\n", num_data);
    printf("Processing time: %f (ms)\n", gputime);
    printf("Samples per second: %E \n", num_data / (gputime * 0.001));
    }

    /* CUT_SAFE_CALL(cutDeleteTimer(timer)); */
    ccudaEventDestroy(start);
    ccudaEventDestroy(end);
    //free memories
//    free(h_data);
    ccudaFree(d_data);
    return h_data ; 
}

/**
 * host function.
 * This function calls corresponding kernel function.
 *
 * @param[in] d_status kernel I/O data.
 * @param[in] num_data number of data to be generated.
 */
extern "C"  __host__  int  make_double_normal_random(mtgp64_kernel_status_t* d_status,
			long num_data, int block_num ,  double * * h_data1,  double * *  h_data2, int verbose = 0 ) {
    double * d_data1;
    double * d_data2;
    cudaError_t e;
    float gputime;
    long num_unit = get_num_unit(num_data,block_num) ;
    cudaEvent_t start;
    cudaEvent_t end;
    * h_data1 = NULL ; 
    * h_data2 = NULL ; 
    ccudaMalloc((void**)&d_data1, sizeof(double) * num_unit);
    ccudaMalloc((void**)&d_data2, sizeof(double) * num_unit);
    /* CUT_SAFE_CALL(cutCreateTimer(&timer)); */
    ccudaEventCreate(&start);
    ccudaEventCreate(&end);
    * h_data1 = (double *) malloc(sizeof(double) * num_data);
    if (* h_data1 == NULL) {
	fprintf(stderr,"failure in allocating host memory for output data.\n");
	return 0 ;
    }
    * h_data2 = (double *) malloc(sizeof(double) * num_data);
    if (* h_data2 == NULL) {
	fprintf(stderr,"failure in allocating host memory for output data.\n");
	return 0 ;
    }
    /* CUT_SAFE_CALL(cutStartTimer(timer)); */
    ccudaEventRecord(start, 0);
    if (cudaGetLastError() != cudaSuccess) {
	fprintf(stderr,"error has been occured before kernel call.\n");
	return 0 ;
    }

    /* kernel call */
    mtgp64_double_kernel<<< block_num, THREAD_NUM >>>(
	d_status, d_data1,  num_unit / block_num);
    cudaThreadSynchronize();

    /* kernel call */
    mtgp64_double_kernel<<< block_num, THREAD_NUM >>>(
        d_status, d_data2,  num_unit / block_num);
    cudaThreadSynchronize();

    /* kernel call */
    mtgp64_double_normal_kernel<<< block_num, THREAD_NUM >>>(
        d_status, d_data1, d_data2, num_unit / block_num);
    cudaThreadSynchronize();

    e = cudaGetLastError();
    if (e != cudaSuccess) {
	printf("failure in kernel call.\n%s\n", cudaGetErrorString(e));
	return 0;
    }
    /* CUT_SAFE_CALL(cutStopTimer(timer)); */
    ccudaEventRecord(end, 0);
    ccudaEventSynchronize(end);
    ccudaMemcpy(*h_data1, d_data1, sizeof(double) * num_data,
		cudaMemcpyDeviceToHost);
    ccudaMemcpy(*h_data2, d_data2, sizeof(double) * num_data,
		cudaMemcpyDeviceToHost);
    
    /* gputime = cutGetTimerValue(timer); */
    if (verbose) {			  
    ccudaEventElapsedTime(&gputime, start, end);

//    print_double_array(*h_data1, num_data, block_num);
    printf("Generated numbers: %d\n", num_data);
    printf("Processing time: %f (ms)\n", gputime);
    printf("Samples per second: %E \n", num_data / (gputime * 0.001));
    }

    /* CUT_SAFE_CALL(cutDeleteTimer(timer)); */
    ccudaEventDestroy(start);
    ccudaEventDestroy(end);
    //free memories
//    free(h_data);
    ccudaFree(d_data1);
    ccudaFree(d_data2);
    return 1 ; 
}


/**
 * host function.
 * This function calls corresponding kernel function.
 *
 * @param[in] d_status kernel I/O data.
 * @param[in] num_data number of data to be generated.
 * @param[in] lambda : mean value of the Poisson distribution
 */

extern "C"  __host__  long *  make_poisson_random(mtgp64_kernel_status_t* d_status, long num_data, int block_num, double lambda , int verbose = 0) {
    long* d_data;
    long* h_data;
    cudaError_t e;
    float gputime;
    long num_unit = get_num_unit(num_data,block_num) ;
    cudaEvent_t start;
    cudaEvent_t end;

    ccudaMalloc((void**)&d_data, sizeof(long) * num_unit);
    /* CUT_SAFE_CALL(cutCreateTimer(&timer)); */
    ccudaEventCreate(&start);
    ccudaEventCreate(&end);
    h_data = (long *) malloc(sizeof(long) * num_data);
    if (h_data == NULL) {
        printf("failure in allocating host memory for output data.\n");
        exit(1);
    }
    /* CUT_SAFE_CALL(cutStartTimer(timer)); */
    ccudaEventRecord(start, 0);
    if (cudaGetLastError() != cudaSuccess) {
        printf("error has been occured before kernel call.\n");
        free(h_data) ;
        exit(1);
    }
    /* kernel call */
    mtgp64_poisson_kernel<<< block_num, THREAD_NUM>>>(d_status, d_data, num_unit / block_num,lambda);
    cudaThreadSynchronize();

    e = cudaGetLastError();
    if (e != cudaSuccess) {
        printf("failure in kernel call.\n%s\n", cudaGetErrorString(e));
        free(h_data) ;
        exit(1);
    }
    /* CUT_SAFE_CALL(cutStopTimer(timer)); */
    ccudaEventRecord(end, 0);
    ccudaEventSynchronize(end);
    ccudaMemcpy(h_data, d_data, sizeof(long) * num_data,
                cudaMemcpyDeviceToHost);
    /* gputime = cutGetTimerValue(timer); */
    if (verbose) {
      ccudaEventElapsedTime(&gputime, start, end);
 //     print_uint64_array(h_data, num_data, block_num);
      printf("generated numbers: %d\n", num_data);
      printf("Processing time: %f (ms)\n", gputime);
      printf("Samples per second: %E \n", num_data / (gputime * 0.001));
    }
    /* CUT_SAFE_CALL(cutDeleteTimer(timer)); */
    ccudaEventDestroy(start);
    ccudaEventDestroy(end);
    //free memories
    // free(h_data);
    ccudaFree(d_data);
    return h_data  ;
}


/**
 * host function.
 * This function calls corresponding kernel function.
 *
 * @param[in] d_status kernel I/O data.
 * @param[in] lam[num_data]  the lambda values 
 *
 */

extern "C"  __host__  double *  make_poisson_multlam_random(mtgp64_kernel_status_t* d_status , long num_data, int block_num, double * lam,  int verbose = 0) {
    double * d_data ;
    double * h_data ;
    double * x ;
    cudaError_t e;
    float gputime;
    long num_unit = get_num_unit(num_data,block_num) ;
    cudaEvent_t start;
    cudaEvent_t end;

    // allocation of the device memory
    ccudaMalloc((void**)&d_data, sizeof(double) * num_unit);

    // allocation of the output array 
    x = (double *) malloc(sizeof(double) * num_data);
    if (x == NULL) {
        printf("failure in allocating host memory for output data.\n");
        exit(1);
    }

    // the lambda values must be copied into d_data
    // we fist copy lam into a tempory array of size num_unit 
    // and fill the additional elements by zero.
    h_data =  (double *) malloc(sizeof(double) * num_unit);
    if (h_data== NULL) {
        printf("failure in allocating host memory\n");
        exit(1);
    }
    memcpy(h_data,lam,sizeof(double) * num_data);
    // we fill the additional elements by zero
    for (int i=num_data ; i < num_unit ; i++) h_data[i] = 0. ;

    // we finally copy h_data into the device data
    ccudaMemcpy(d_data, h_data, sizeof(double) * num_unit,cudaMemcpyHostToDevice);
    free(h_data) ;

    ccudaEventCreate(&start);
    ccudaEventCreate(&end);

    ccudaEventRecord(start, 0);
    if (cudaGetLastError() != cudaSuccess) {
        printf("error has been occured before kernel call.\n");
        exit(1);
    }
    /* kernel call */
    mtgp64_poisson_multlam_kernel<<< block_num, THREAD_NUM>>>(d_status, d_data, num_unit / block_num) ;
    cudaThreadSynchronize();

    e = cudaGetLastError();
    if (e != cudaSuccess) {
        printf("failure in kernel call.\n%s\n", cudaGetErrorString(e));
        exit(1);
    }
    /* CUT_SAFE_CALL(cutStopTimer(timer)); */
    ccudaEventRecord(end, 0);
    ccudaEventSynchronize(end);
    ccudaMemcpy(x, d_data, sizeof(double) * num_data,cudaMemcpyDeviceToHost);

    /* gputime = cutGetTimerValue(timer); */
    if (verbose) {
      ccudaEventElapsedTime(&gputime, start, end);
      printf("generated numbers: %d\n", num_data);
      printf("Processing time: %f (ms)\n", gputime);
      printf("Samples per second: %E \n", num_data / (gputime * 0.001));
    }
    /* CUT_SAFE_CALL(cutDeleteTimer(timer)); */
    ccudaEventDestroy(start);
    ccudaEventDestroy(end);
    //free memories
    ccudaFree(d_data);
    return x ;
}

/*
	 Allocate the memory for the structure d_status, initializes the device and d_status.
	 Returns a pointer to d_status
*/
extern "C"  __host__  mtgp64_kernel_status_t *  init_status (int block_num, int device )
{

	mtgp64_kernel_status_t* d_status;
	ccudaSetDevice(device);
	ccudaMalloc((void**)&d_status, sizeof(mtgp64_kernel_status_t) * block_num);	
	make_constant(MTGP64DC_PARAM_TABLE, block_num);
	return d_status ;
}

/*
	Initialize the seeds associated with each block.
*/

extern "C"  __host__  void init_seeds (mtgp64_kernel_status_t * d_status, int  block_num, uint64_t * seeds ) 
 {
   make_kernel_data64(d_status, MTGP64DC_PARAM_TABLE, block_num,seeds);
 }


/*
	Free the structure d_status from the memory.
*/
extern "C"  __host__  void free_status(mtgp64_kernel_status_t *  d_status ) {
	     ccudaFree(d_status);
 
}

/*
  Return a suitable value for block_num
 */
extern "C"  __host__  int get_suitable_block_num(int device,
					 int *max_block_num,
					 int *mp_num,
					 int word_size,
					 int thread_num,
					 int large_size)
{
  //    DENTER("get_suitable_block");
    cudaDeviceProp dev;
    CUdevice cuDevice;
    int max_thread_dev;
    int max_block, max_block_mem, max_block_dev;
    int major, minor, ver;
    //int regs, max_block_regs;

    ccudaGetDeviceProperties(&dev, device);
    cuDeviceGet(&cuDevice, device);
    cuDeviceComputeCapability(&major, &minor, cuDevice);
    //cudaFuncGetAttributes()
#if 0
    if (word_size == 4) {
	regs = 14;
    } else {
	regs = 16;
    }
    max_block_regs = dev.regsPerBlock / (regs * thread_num);
#endif
    max_block_mem = dev.sharedMemPerBlock / (large_size * word_size + 16);
    if (major == 9999 && minor == 9999) {
	return -1;
    }
    ver = major * 100 + minor;
    if (ver <= 101) {
	max_thread_dev = 768;
    } else if (ver <= 103) {
	max_thread_dev = 1024;
    } else if (ver <= 200) {
	max_thread_dev = 1536;
    } else {
	max_thread_dev = 1536;
    }
    max_block_dev = max_thread_dev / thread_num;
    if (max_block_mem < max_block_dev) {
	max_block = max_block_mem;
    } else {
	max_block = max_block_dev;
    }
#if 0
    if (max_block_regs < max_block) {
	max_block = max_block_regs;
    }
#endif
    *max_block_num = max_block;
    *mp_num = dev.multiProcessorCount;
    return max_block * dev.multiProcessorCount;
}


/*

  A simple example

 */
__host__ int sample_cuda(int argc, char** argv)
{
    // LARGE_SIZE is a multiple of 16
    int num_data = 10000000;
    int block_num;
    int block_num_max;
    int num_unit;
    int r;
    mtgp64_kernel_status_t* d_status;
    int device = 0;
    int mb, mp;
    uint64_t * seeds  ;

    ccudaSetDevice(device);

    if (argc >= 2) {
	errno = 0;
	block_num = strtol(argv[1], NULL, 10);
	if (errno) {
	    printf("%s number_of_block number_of_output\n", argv[0]);
	    return 1;
	}
	if (BLOCK_NUM_MAX < PARAM_NUM_MAX) {
	    block_num_max = BLOCK_NUM_MAX;
	} else {
	    block_num_max = PARAM_NUM_MAX;
	}
	if (block_num < 1 || block_num > block_num_max) {
	    printf("%s block_num should be between 1 and %d\n",
		   argv[0], block_num_max);
	    return 1;
	}
	errno = 0;
	num_data = strtol(argv[2], NULL, 10);
	if (errno) {
	    printf("%s number_of_block number_of_output\n", argv[0]);
	    return 1;
	}
	argc -= 2;
	argv += 2;
    } else {
	printf("%s number_of_block number_of_output\n", argv[0]);
	block_num = get_suitable_block_num(device,
					   &mb,
					   &mp,
					   sizeof(uint64_t),
					   THREAD_NUM,
					   LARGE_SIZE);
	if (block_num <= 0) {
	    printf("can't calculate suitable number of blocks.\n");
	    return 1;
	}
	printf("the suitable number of blocks for device 0 will be multiple of %d, or %d\n", block_num,(mb - 1) * mp);
	return 1;
    }
    num_unit = LARGE_SIZE * block_num;
    seeds = (uint64_t  * ) malloc( sizeof(uint64_t ) * block_num ) ;
    for (int i=0 ; i< block_num ; i++) seeds[i] = i + 1 ;
    ccudaMalloc((void**)&d_status, sizeof(mtgp64_kernel_status_t) * block_num);
    r = num_data % num_unit;
    if (r != 0) {
	num_data = num_data + num_unit - r;
    }
    printf("number of blocks : %d , number of unit: %d , number of random values: %d\n",block_num,num_unit,num_data);
    make_constant(MTGP64DC_PARAM_TABLE, block_num);
    make_kernel_data64(d_status, MTGP64DC_PARAM_TABLE, block_num,seeds);
    printf("generating 64-bit unsigned random numbers.\n");
    make_uint64_random(d_status, num_data, block_num,1);
    printf("generating double precision floating point random numbers.\n");
    make_double_random(d_status, num_data, block_num,1);

    //finalize
    ccudaFree(d_status);
    free(seeds) ;
    return 0;
}
