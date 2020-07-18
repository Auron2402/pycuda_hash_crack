import pycuda.driver as cuda
import pycuda.autoinit
from pycuda.compiler import SourceModule

import numpy

#generate test array
testarray = numpy.random.rand(5, 5)

#internet says only single precision
testarray = testarray.astype(numpy.float32)

#send to gpu
testarray_gpu = cuda.mem_alloc(testarray.nbytes)
cuda.memcpy_htod(testarray_gpu, testarray)

#generate C function to use on data (only x2 right now)
#i have no idead what this does but it says it doubles ... jonas this is your part to niceify
mod = SourceModule("""
__global__ void doublify(float *a)
{
    int idx = threadIdx.x + threadIdx.y*4;
    a[idx] *= 2;
}
""")

#execute dis shit
func = mod.get_function("doublify")
func(testarray_gpu, block=(5, 5, 1))

#get data back
testarray_result = numpy.empty_like(testarray)
cuda.memcpy_dtoh(testarray_result, testarray_gpu)

#print result for showcase
print("AUSGANGSWERT \n")
print(testarray)
print("\n\n\nErgebnis:\n")
print(testarray_result)