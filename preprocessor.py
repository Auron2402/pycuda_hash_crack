from mpi4py import MPI
import pandas as pd
import password_cracker
import numpy

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()


def preprocess(filename):
    print(f'I have rank {rank} in a size {size} cluster.')
    # read file, split file in chunks
    if rank == 0:
        unprocessed_data = pd.read_csv(f'wordlists/{filename}.txt', sep="\n", encoding='latin-1', header=None,
                                       squeeze=True, error_bad_lines=False, quoting=3)
        unprocessed_data = [str(x) for x in unprocessed_data]
        unprocessed_chunks = numpy.array_split(unprocessed_data, size, axis=0)
    else:
        unprocessed_chunks = None

    # scatter data to nodes
    data = comm.scatter(unprocessed_chunks, root=0)

    # call jonas preprocessing
    processed_data = password_cracker.prepare_wordlist(data)

    # gather data from nodes
    recvbuf = comm.gather(processed_data, root=0)

    # flatten array, write to npy file
    if rank == 0:
        flat_list = [item for sublist in recvbuf for item in sublist]
        numpy.save(f'wordlists/{filename}.npy', flat_list)
