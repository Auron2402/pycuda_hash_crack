from mpi4py import MPI
import numpy
import pandas as pd
import password_cracker
import os
import preprocessor
import sys
import bigmpi4py as BM

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

# get parameters from call and save them
filename = "rockyou"  # if no 2nd argument is set, set rockyou
hash_to_crack = sys.argv[1]
if len(sys.argv) == 3:
    filename = sys.argv[2]


# if not already done, preprocess data
if not os.path.exists(f'wordlists/{filename}.npy'):
    if rank == 0:
        print('Have to Preprocess data')
    need_to_preprocess = True
else:
    need_to_preprocess = False

if need_to_preprocess:
    preprocessor.preprocess(filename)
    if rank == 0:
        print('Preprocessing done. Saved as .npy file')

# read and split data
if rank == 0:
    complete_data = numpy.load(f'wordlists/{filename}.npy')
    #chunks = numpy.array_split(complete_data, size, axis=0)
else:
    complete_data = None

# send data
password_list = BM.scatter(complete_data, comm)

# crack password on nodes
result = password_cracker.crack_gpu(password_list=password_list, target_hash=hash_to_crack, gpu_id=rank)

# recieve data
recvbuf = BM.gather(result, comm)

# print result
if rank == 0:
    print('result: \n')
    #flat_list = [item for sublist in recvbuf for item in sublist]
    for ergebnis in recvbuf:
        print(ergebnis)

# For windows pleps only:
# mpiexec /np 8 python mpi_test.py a68d45a5f47c05263f2991543dd044d0 HashesOrg
