from __future__ import division
from numba import cuda
import numpy
import math

from password_cracker import PasswordCracker

cracker = PasswordCracker(['test'])
cracker.crack_gpu(target_hash="098f6bcd4621d373cade4e832627b4f6")