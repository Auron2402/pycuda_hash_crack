from mpi4py import MPI
import password_cracker
import numpy
import bigmpi4py as BM

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()


def preprocess(filename):
    print(f'I have rank {rank} in a size {size} cluster.')
    # read file, split file in chunks
    if rank == 0:
        with open(f'wordlists/{filename}.txt', 'r', encoding='latin-1') as myfile:
            content = myfile.readlines()
    else:
        content = None

    # scatter data to nodes
    recv_data = BM.scatter(content, comm)

    # call jonas preprocessing
    processed_data = password_cracker.prepare_wordlist(recv_data)
    del recv_data  # free up memory

    # gather data from nodes
    recvbuf = BM.gather(processed_data, comm)
    del processed_data  # free up memory

    # write to npy file
    if rank == 0:
        numpy.save(f'wordlists/{filename}.npy', recvbuf)
