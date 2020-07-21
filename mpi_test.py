from mpi4py import MPI
import numpy
import pandas as pd

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

# generate data




# read data
if rank == 0:
    # rockyou has 14.344.395 lines
    complete_data = pd.read_csv('rockyou.txt', sep="\n", encoding='latin-1', header=None, squeeze=True, error_bad_lines=False)
else:
    complete_data = None



# read and split data
if rank == 0:
    chunks = numpy.array_split(complete_data, size, axis=0)
else:
    chunks = None

#send data
data = comm.scatter(chunks, root=0)
print('rank', rank, 'has data:', len(data))

# For windows pleps only:
# mpiexec /np 8 python mpi_test.py
