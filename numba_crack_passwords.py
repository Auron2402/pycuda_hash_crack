from __future__ import division
from numba import cuda
import numpy
import math

from password_cracker import PasswordCracker

cracker = PasswordCracker(['hhhyhyhgtuj'])
res = cracker.crack_gpu(target_hash="fd005671d7a0b03ddfb69dd7f151665b")
print(res)