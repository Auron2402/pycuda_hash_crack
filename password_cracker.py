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


T = np.array([math.floor(pow(2, 32) * abs(math.sin(i + 1))) for i in range(64)])
s1 = np.array([7, 12, 17, 22])
s2 = np.array([5, 9, 14, 20])
s3 = np.array([4, 11, 16, 23])
s4 = np.array([6, 10, 15, 21])

# CUDA kernel
@cuda.jit
def crack_password(arr, out_hashes, target_hash, matching_hash_index):
    # Thread id in a 1D block
    tx = cuda.threadIdx.x
    # Block id in a 1D grid
    ty = cuda.blockIdx.x
    # Block width, i.e. number of threads per block
    bw = cuda.blockDim.x
    # Compute flattened index inside the array
    pos = tx + ty * bw
    #pos = 0
    if pos < arr.size:  # Check array boundaries
        F = lambda x, y, z: (x & y) | (~x & z)
        G = lambda x, y, z: (x & z) | (y & ~z)
        H = lambda x, y, z: x ^ y ^ z
        I = lambda x, y, z: y ^ (x | ~z)

        rotate_left = lambda x, n: (x << n) | (x >> (32 - n))
        modular_add = lambda a, b: (a + b) % pow(2, 32)

        out_hashes[pos][0] = A = 0x67452301
        out_hashes[pos][1] = B = 0xEFCDAB89
        out_hashes[pos][2] = C = 0x98BADCFE
        out_hashes[pos][3] = D = 0x10325476

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


        out_hashes[pos][0] = modular_add(out_hashes[pos][0], A)
        out_hashes[pos][1] = modular_add(out_hashes[pos][1], B)
        out_hashes[pos][2] = modular_add(out_hashes[pos][2], C)
        out_hashes[pos][3] = modular_add(out_hashes[pos][3], D)

        if (target_hash[0] == out_hashes[pos][0] and
            target_hash[1] == out_hashes[pos][1] and
            target_hash[2] == out_hashes[pos][2] and
            target_hash[3] == out_hashes[pos][3]):
            matching_hash_index[0] = pos


def str_to_int_arr(s: str):
    s = str(s)
    bit_array = bitarray(endian="big")
    bit_array.frombytes(s.encode("utf-8"))
    bit_array.append(1)
    while bit_array.length() % 512 != 448:
        bit_array.append(0)
    bit_array = bitarray(bit_array, endian="little")
    length = (len(s) * 8) % pow(2, 64)
    length_bit_array = bitarray(endian="little")
    length_bit_array.frombytes(struct.pack("<Q", length))

    result = bit_array.copy()
    result.extend(length_bit_array)
    if result.length() != 512: # ignore very large passwords
        print(f"too long (ignored): {s}")
        return str_to_int_arr("")
    #print(result)
    X = [result[(x * 32) : (x * 32) + 32] for x in range(16)]
    X = [int.from_bytes(word.tobytes(), byteorder="little") for word in X]
    return X


def int_arr_to_str(arr):
    X = [int(i) for i in arr]
    X = [i.to_bytes(4, byteorder="little") for i in X]
    X = X[0:-2] # remove lenght
    X = reduce(lambda t1, t2: t1 + t2, X)
    while True:
        if X[-1] == 0:
            X = X[0:-1]
        elif X[-1] == 128:
            X = X[0:-1]
            break
    return X.decode("utf-8")


# turns stringlists to int arrays for easyer gpu processing
def prepare_wordlist(password_list: List[str]):
    passwords = [str_to_int_arr(pw) for pw in password_list]
    arr = np.array(passwords, dtype=np.uint32)
    return arr


def crack_gpu(password_list, target_hash: str) -> typing.List[str]:
    print(f"preparation phase (cpu)")
    arr = password_list
    target_hash_arr = [int(target_hash[i:i+8],16) for i in range(0,len(target_hash),8)]
    target_hash_arr = np.array([struct.unpack(">I", struct.pack("<I", i))[0] for i in target_hash_arr], dtype=np.uint32)
    #print(f"arr: {arr}")
    #print(target_hash_arr)
    out_hashes = np.zeros((1, 4), dtype=np.uint32)
    # TODO: Parallel gpu execution
    matching_hash_index = np.array([-1], dtype=np.int64)

    THREADS_PER_BLOCK = 512
    BLOCKS_PER_GRID = (len(arr) + (THREADS_PER_BLOCK - 1)) // THREADS_PER_BLOCK # only 1 "Grid"
    print(f"cracking phase (gpu)")
    crack_password[BLOCKS_PER_GRID, THREADS_PER_BLOCK](arr, out_hashes, target_hash_arr, matching_hash_index)
    #crack_password(arr, out_hashes, target_hash_arr, matching_hash_index)
    #print(out_hashes)
    #A = struct.unpack("<I", struct.pack(">I", out_hashes[0][0]))[0]
    #B = struct.unpack("<I", struct.pack(">I", out_hashes[0][1]))[0]
    #C = struct.unpack("<I", struct.pack(">I", out_hashes[0][2]))[0]
    #D = struct.unpack("<I", struct.pack(">I", out_hashes[0][3]))[0]
    #print(f"my: {format(A, '08x')}{format(B, '08x')}{format(C, '08x')}{format(D, '08x')}")
    #print(f"py: {hashlib.md5(self.password_list[0].encode('utf-8')).hexdigest()}")
    print(f"finished")
    if matching_hash_index[0] != -1:
        return [int_arr_to_str(password_list[matching_hash_index[0]])]
    return []


        



# cracker = PasswordCracker(['a'])
# cracker.crack_gpu()