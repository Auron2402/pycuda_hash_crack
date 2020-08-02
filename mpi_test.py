from mpi4py import MPI
import numpy
import pandas as pd
import password_cracker

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

# generate data




# read data
if rank == 0:
    # rockyou has 14.344.395 lines
    complete_data = pd.read_csv('wordlists/rockyou.txt', sep="\n", encoding='latin-1', header=None, squeeze=True, error_bad_lines=False)
else:
    complete_data = None



# read and split data
if rank == 0:
    chunks = numpy.array_split(complete_data, size, axis=0)
else:
    chunks = None

#send data
data = comm.scatter(chunks, root=0)
# print('rank', rank, 'has data:', len(data))

# crack password on nodes
crackme = password_cracker.PasswordCracker(data.tolist())
testhash = "5f0c3c9a829e2b7aa376f3710160dc37"
result = crackme.crack_gpu(target_hash=testhash)

# recieve data
recvbuf = comm.gather(result, root=0)

if rank == 0:
    flat_list = [item for sublist in recvbuf for item in sublist]
    for ergebnis in flat_list:
        print('ERGEBNIS: ' + ergebnis)

# For windows pleps only:
# mpiexec /np 8 python mpi_test.py
