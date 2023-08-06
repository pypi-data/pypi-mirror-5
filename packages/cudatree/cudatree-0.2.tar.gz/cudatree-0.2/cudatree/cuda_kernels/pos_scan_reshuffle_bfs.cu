#include<stdio.h>
#include<math.h>
#include<stdint.h>
#define IDX_DATA_TYPE %s
#define THREADS_PER_BLOCK %s

#define WARP_SIZE 32
#define WARP_MASK 0x1f

texture<char, 1> tex_mark;

__global__ void scan_reshuffle(
                          uint8_t* mark_table,
                          uint8_t* si_idx,
                          IDX_DATA_TYPE* sorted_indices_1,
                          IDX_DATA_TYPE* sorted_indices_2,
                          uint32_t* begin_end_idx,
                          IDX_DATA_TYPE* split,
                          uint32_t n_features,
                          uint32_t stride
                          ){  
  
  __shared__ IDX_DATA_TYPE last_sum;
   
#if defined(__CUDA_ARCH__) && __CUDA_ARCH__ >= 300
  uint16_t lane_id = threadIdx.x & WARP_MASK;
  uint16_t warp_id = threadIdx.x / WARP_SIZE;
  __shared__ IDX_DATA_TYPE shared_pos_table[THREADS_PER_BLOCK / WARP_SIZE];
#else
  __shared__ IDX_DATA_TYPE shared_pos_table[THREADS_PER_BLOCK];
#endif 
  
  IDX_DATA_TYPE reg_start_idx = begin_end_idx[2 * blockIdx.x];
  IDX_DATA_TYPE reg_stop_idx = begin_end_idx[2 * blockIdx.x + 1];
  IDX_DATA_TYPE reg_split_idx = split[blockIdx.x];
  IDX_DATA_TYPE n;
  
  
  if(reg_split_idx == reg_stop_idx)
    return;
  

  IDX_DATA_TYPE *p_sorted_indices_in;
  IDX_DATA_TYPE *p_sorted_indices_out;

  if(si_idx[blockIdx.x] == 0){
    p_sorted_indices_in = sorted_indices_1;
    p_sorted_indices_out = sorted_indices_2;
  }else{
    p_sorted_indices_in = sorted_indices_2;
    p_sorted_indices_out = sorted_indices_1;
  }
  
  for(uint16_t shuffle_feature_idx = blockIdx.y; shuffle_feature_idx < n_features; shuffle_feature_idx += gridDim.y){
    uint32_t offset = shuffle_feature_idx * stride;

    if(threadIdx.x == 0)
      last_sum = 0;

    for(IDX_DATA_TYPE i = reg_start_idx; i < reg_stop_idx; i += blockDim.x){
      uint8_t side = 0;
      IDX_DATA_TYPE idx = i + threadIdx.x;
      IDX_DATA_TYPE reg_pos;
      IDX_DATA_TYPE si_idx; 
      
      if(idx < reg_stop_idx){
        si_idx = p_sorted_indices_in[offset + idx];
        side = tex1Dfetch(tex_mark, si_idx);
      }

      reg_pos = side;

#if defined(__CUDA_ARCH__) && __CUDA_ARCH__ >= 300

      for(uint16_t s = 1; s < WARP_SIZE; s *= 2){
        n = __shfl_up((int)reg_pos, s);
        if(lane_id >= s)
          reg_pos += n;
      }

      if(lane_id == WARP_SIZE - 1)
        shared_pos_table[warp_id] = reg_pos;
     
      __syncthreads();
     
      if(threadIdx.x == 0)
        for(uint16_t l = 1; l < blockDim.x / WARP_SIZE - 1; ++l)
          shared_pos_table[l] += shared_pos_table[l-1];

      __syncthreads();
      
      if(warp_id > 0)
        reg_pos += shared_pos_table[warp_id - 1];
      
      reg_pos += last_sum; 

#else
      shared_pos_table[threadIdx.x] = side;
      
      __syncthreads();

      for(uint16_t s = 1; s < blockDim.x; s *= 2){
        if(threadIdx.x >= s)
          n = shared_pos_table[threadIdx.x - s];
        else
          n = 0;
        __syncthreads();
        shared_pos_table[threadIdx.x] += n;
        __syncthreads();
      }
      
      reg_pos = shared_pos_table[threadIdx.x] + last_sum;
#endif

      if(idx < reg_stop_idx){
        IDX_DATA_TYPE out_pos = (side == 1)? reg_start_idx + reg_pos - 1 : reg_split_idx + 1 + idx - reg_start_idx - reg_pos;
        p_sorted_indices_out[offset + out_pos] = si_idx;   
      }

      __syncthreads();

      if(threadIdx.x == blockDim.x - 1)
        last_sum = reg_pos;
    }
     
    __syncthreads();
  }

}

