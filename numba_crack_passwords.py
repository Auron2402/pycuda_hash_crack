from __future__ import division
from numba import cuda
import numpy
import math

from password_cracker import PasswordCracker

cracker = PasswordCracker(['test'])
cracker.crack_gpu()