from mpi4py import MPI

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

if rank == 0:
    with open('rockyou.txt', 'r', encoding='latin-1') as dictionary:
        data = dictionary.readlines()
else:
    data = None

data = comm.scatter(data, root=0)
print('rank', rank, 'has data:', len(data))

# For windows pleps only:
# mpiexec /np 8 python mpi_test.py
