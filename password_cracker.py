from __future__ import division

from functools import reduce
from typing import List
from numba import cuda
import numpy as np
import math
import hashlib
from enum import Enum
from bitarray import bitarray
import struct
import typing

T_ = np.array([math.floor(pow(2, 32) * abs(math.sin(i + 1))) for i in range(64)])
s1_ = np.array([7, 12, 17, 22])
s2_ = np.array([5, 9, 14, 20])
s3_ = np.array([4, 11, 16, 23])
s4_ = np.array([6, 10, 15, 21])

# CUDA kernel
@cuda.jit
def crack_password(arr, target_hash, matching_hash_index):
    T = cuda.const.array_like(T_)
    s1 = cuda.const.array_like(s1_)
    s2 = cuda.const.array_like(s2_)
    s3 = cuda.const.array_like(s3_)
    s4 = cuda.const.array_like(s4_)

    # Thread id in a 1D block
    tx = cuda.threadIdx.x
    # Block id in a 1D grid
    ty = cuda.blockIdx.x
    # Block width, i.e. number of threads per block
    bw = cuda.blockDim.x
    # Compute flattened index inside the array
    pos = tx + ty * bw
    #pos = 0
    if pos < arr.shape[0]:  # Check array boundaries
        F = lambda x, y, z: (x & y) | (~x & z)
        G = lambda x, y, z: (x & z) | (y & ~z)
        H = lambda x, y, z: x ^ y ^ z
        I = lambda x, y, z: y ^ (x | ~z)

        rotate_left = lambda x, n: (x << n) | (x >> (32 - n))
        modular_add = lambda a, b: (a + b) % pow(2, 32)

        o0 = A = 0x67452301
        o1 = B = 0xEFCDAB89
        o2 = C = 0x98BADCFE
        o3 = D = 0x10325476

        for i in range(4 * 16):
            if 0 <= i <= 15:
                k = i
                s = s1
                temp = F(B, C, D)
            elif 16 <= i <= 31:
                k = ((5 * i) + 1) % 16
                s = s2
                temp = G(B, C, D)
            elif 32 <= i <= 47:
                k = ((3 * i) + 5) % 16
                s = s3
                temp = H(B, C, D)
            elif 48 <= i <= 63:
                k = (7 * i) % 16
                s = s4
                temp = I(B, C, D)

            temp = modular_add(temp, arr[pos][k])
            temp = modular_add(temp, T[i])
            temp = modular_add(temp, A)
            temp = rotate_left(temp, s[i % 4])
            temp = modular_add(temp, B)

            A = D
            D = C
            C = B
            B = temp

        o0 = modular_add(o0, A)
        o1 = modular_add(o1, B)
        o2 = modular_add(o2, C)
        o3 = modular_add(o3, D)

        if (target_hash[0] == o0 and
            target_hash[1] == o1 and
            target_hash[2] == o2 and
            target_hash[3] == o3):
            #matching_hash_index[0] = -10
            #from pdb import set_trace; set_trace()
            cuda.atomic.compare_and_swap(matching_hash_index, -1, pos)



def str_to_int_arr(s: str):
    #s = str(s)
    #bytes = s.encode("utf-8")
    bit_array = bitarray(endian="big")
    bit_array.frombytes(s.encode("utf-8"))
    bit_array.append(1)
    bit_array.extend('0' * (448 - bit_array.length()))
    #while bit_array.length() % 512 != 448:
    #    bit_array.append(0)
    bit_array1 = bit_array
    bit_array = bitarray(bit_array, endian="little")
    length = len(s) * 8
    length_bit_array = bitarray(endian="little")
    length_bit_array.frombytes(struct.pack("<Q", length))

    #result = bit_array.copy()
    bit_array.extend(length_bit_array)
    if bit_array.length() != 512: # ignore very large passwords
        #print(f"too long (ignored): {s}")
        del bit_array
        del bit_array1
        del length_bit_array
        return str_to_int_arr("")
    #print(result)
    X = [bit_array[(x * 32) : (x * 32) + 32] for x in range(16)]
    X = [int.from_bytes(word.tobytes(), byteorder="little") for word in X]
    del bit_array
    del bit_array1
    del length_bit_array
    return X


def int_arr_to_str(arr):
    X = [int(i) for i in arr]
    X = [i.to_bytes(4, byteorder="little") for i in X]
    X = X[0:-2] # remove length
    X = reduce(lambda t1, t2: t1 + t2, X)
    while True:
        if X[-1] == 0:
            X = X[0:-1]
        elif X[-1] == 128:
            X = X[0:-1]
            break
    return X.decode("utf-8")


# turns stringlists to int arrays for easier gpu processing
def prepare_wordlist(password_list: List[str]):
    arr = np.zeros((len(password_list),16), dtype=np.uint32)
    for i in range(len(password_list)):
        arr[i] = str_to_int_arr(password_list[i])
    #passwords = [str_to_int_arr(pw) for pw in password_list]
    #arr = np.array(passwords, dtype=np.uint32)
    return arr


def crack_gpu(password_list, target_hash: str, gpu_id:int) -> typing.List[str]:
    #if gpu_id != 0:
    cuda.select_device(gpu_id)
    arr = password_list
    target_hash_arr = [int(target_hash[i:i+8],16) for i in range(0,len(target_hash),8)]
    target_hash_arr = np.array([struct.unpack(">I", struct.pack("<I", i))[0] for i in target_hash_arr], dtype=np.uint32)
    matching_hash_index = np.array([-1], dtype=np.int32)
    THREADS_PER_BLOCK = 512
    BLOCKS_PER_GRID = (arr.shape[0] + (THREADS_PER_BLOCK - 1)) // THREADS_PER_BLOCK # only 1 "Grid"
    target_hash_arr = cuda.to_device(target_hash_arr)
    matching_hash_index = cuda.to_device(matching_hash_index)
    arr = cuda.to_device(arr)
    print(f"cracking phase (gpu{gpu_id})")
    crack_password[BLOCKS_PER_GRID, THREADS_PER_BLOCK](arr, target_hash_arr, matching_hash_index)
    print(f"finished (gpu{gpu_id})")
    matching_hash_index = matching_hash_index.copy_to_host()
    if matching_hash_index[0] != -1:
        return [int_arr_to_str(password_list[matching_hash_index[0]])]
    return []


        



# cracker = PasswordCracker(['a'])
# cracker.crack_gpu()