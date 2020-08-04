from mpi4py import MPI
import numpy
import pandas as pd
import password_cracker
import os
import preprocessor

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

filename = "rockyou"

# read data or preprocess it b4 reading it

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
    chunks = numpy.array_split(complete_data, size, axis=0)
else:
    chunks = None

# send data
password_list = comm.scatter(chunks, root=0)

# crack password on nodes
testhash = "a68d45a5f47c05263f2991543dd044d0"
result = password_cracker.crack_gpu(password_list=password_list, target_hash=testhash)

# recieve data
recvbuf = comm.gather(result, root=0)

# print result
if rank == 0:
    print('ERGEBNIS: \n')
    flat_list = [item for sublist in recvbuf for item in sublist]
    for ergebnis in flat_list:
        print(ergebnis)

# For windows pleps only:
# mpiexec /np 8 python mpi_test.py
