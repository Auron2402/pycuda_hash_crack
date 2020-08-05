from mpi4py import MPI
import pandas as pd
import password_cracker
import numpy
import bigmpi4py as BM

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

class StringConverter(dict):
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return str

    def get(self, default=None):
        return str


def preprocess(filename):
    print(f'I have rank {rank} in a size {size} cluster.')
    # read file, split file in chunks
    if rank == 0:
        # # read data
        # unprocessed_data = pd.read_csv(f'wordlists/{filename}.txt', sep="\n", encoding='latin-1', header=None,
        #                                squeeze=True, error_bad_lines=False, quoting=3)
        #
        # # split and cast to string
        # #unprocessed_chunks = numpy.array_split(unprocessed_data.astype(dtype='str'), size)
        # #del unprocessed_data  # free up memory
        myfile = open(f'wordlists/{filename}.txt', 'r', encoding='latin-1')
        content = myfile.read().split('\n')
    else:
        unprocessed_chunks = None
        unprocessed_data = None
        content = None

    # scatter data to nodes
    recv_data = BM.scatter(content, comm)
    # recv_data = comm.scatter(unprocessed_chunks, root=0)
    # del unprocessed_chunks  # free up memory

    # call jonas preprocessing
    processed_data = password_cracker.prepare_wordlist(recv_data)
    del recv_data  # free up memory

    # gather data from nodes
    recvbuf = BM.gather(processed_data, comm)
    # recvbuf = comm.gather(processed_data, root=0)
    del processed_data  # free up memory

    # flatten array, write to npy file
    if rank == 0:
        #flat_list = [item for sublist in recvbuf for item in sublist]
        numpy.save(f'wordlists/{filename}.npy', recvbuf)
