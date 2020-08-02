from __future__ import division
from numba import cuda
import numpy
import math

from password_cracker import *


l = prepare_wordlist(['hhhyhyhgtuj'])
res = crack_gpu(l, "fd005671d7a0b03ddfb69dd7f151665b")
print(res)

#print(int_arr_to_str(str_to_int_arr("test")))