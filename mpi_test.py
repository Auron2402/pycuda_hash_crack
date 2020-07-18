from mpi4py import MPI
import numpy

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

if rank == 0:
    # with open('rockyou.txt', 'r', encoding='latin-1') as dictionary:
    #     data = dictionary.readlines()
    complete_data = numpy.loadtxt('rockyou_smol.txt', dtype=str, delimiter='\n', encoding='latin-1')
    chunks = numpy.array_split(complete_data, size, axis=0)


else:
    chunks = None

data = comm.scatter(chunks, root=0)
print('rank', rank, 'has data:', len(data))

# For windows pleps only:
# mpiexec /np 8 python mpi_test.py
