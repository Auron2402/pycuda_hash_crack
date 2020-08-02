from __future__ import division
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
def crack_password(arr, out_hashes, target_hash, matching_hash):
    #md5 = hashlib.md5(pw.encode('utf-8')).hexdigest()
    #output = True
    # Define the four auxiliary functions that produce one 32-bit word.
    F = lambda x, y, z: (x & y) | (~x & z)
    G = lambda x, y, z: (x & z) | (y & ~z)
    H = lambda x, y, z: x ^ y ^ z
    I = lambda x, y, z: y ^ (x | ~z)

    # Define the left rotation function, which rotates `x` left `n` bits.
    rotate_left = lambda x, n: (x << n) | (x >> (32 - n))

    # Define a function for modular addition.
    modular_add = lambda a, b: (a + b) % pow(2, 32)

    out_hashes[0][0] = A = 0x67452301
    out_hashes[0][1] = B = 0xEFCDAB89
    out_hashes[0][2] = C = 0x98BADCFE
    out_hashes[0][3] = D = 0x10325476

    # Execute the four rounds with 16 operations each.
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

        # The MD5 algorithm uses modular addition. Note that we need a
        # temporary variable here. If we would put the result in `A`, then
        # the expression `A = D` below would overwrite it. We also cannot
        # move `A = D` lower because the original `D` would already haveX
        # been overwritten by the `D = C` expression.
        temp = modular_add(temp, arr[0][k])
        temp = modular_add(temp, T[i])
        temp = modular_add(temp, A)
        temp = rotate_left(temp, s[i % 4])
        temp = modular_add(temp, B)

        # Swap the registers for the next operation.
        A = D
        D = C
        C = B
        B = temp

    
    # Update the buffers with the results from this chunk.
    out_hashes[0][0] = modular_add(out_hashes[0][0], A)
    out_hashes[0][1] = modular_add(out_hashes[0][1], B)
    out_hashes[0][2] = modular_add(out_hashes[0][2], C)
    out_hashes[0][3] = modular_add(out_hashes[0][3], D)

    if (target_hash[0] == out_hashes[0][0] and
        target_hash[1] == out_hashes[0][1] and
        target_hash[2] == out_hashes[0][2] and
        target_hash[3] == out_hashes[0][3]):
        matching_hash = out_hashes[0]


class PasswordCracker:

    def __init__(self, password_list: List[str]) -> None:
        super().__init__()
        self.password_list: List[str] = password_list

    def crack_gpu(self, target_hash:str) -> typing.List[str]:
        pw1 = PasswordCracker.__str_to_int_arr(self.password_list[0])
        arr = np.array([pw1], dtype=np.uint32)
        target_hash_arr = np.array([int(target_hash[i:i+8],16) for i in range(0,len(target_hash),8)], dtype=np.uint32)
        print(f"arr: {arr}")
        out_hashes = np.zeros((1, 4), dtype=np.uint32)
        # TODO: Parallel gpu execution
        matching_hash = np.array(4, dtype=np.uint32)
        crack_password[1, 1](arr, out_hashes, target_hash_arr, matching_hash)
        #crack_password(arr, out_hashes, target_hash_arr, matching_hash)
        print(out_hashes)
        A = struct.unpack("<I", struct.pack(">I", out_hashes[0][0]))[0]
        B = struct.unpack("<I", struct.pack(">I", out_hashes[0][1]))[0]
        C = struct.unpack("<I", struct.pack(">I", out_hashes[0][2]))[0]
        D = struct.unpack("<I", struct.pack(">I", out_hashes[0][3]))[0]
        print(f"my: {format(A, '08x')}{format(B, '08x')}{format(C, '08x')}{format(D, '08x')}")
        print(f"py: {hashlib.md5(self.password_list[0].encode('utf-8')).hexdigest()}")
        return []

    def crack_cpu(self):
        pass
    
    @staticmethod
    def __str_to_int_arr(s: str):
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
        assert(result.length() == 512)
        print(result)
        X = [result[(x * 32) : (x * 32) + 32] for x in range(16)]
        X = [int.from_bytes(word.tobytes(), byteorder="little") for word in X]
        return X
        



# cracker = PasswordCracker(['a'])
# cracker.crack_gpu()