import os
import datetime

from mpi4py import MPI
import string
import numpy as np

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

# Only master checks for wordlist settings
if rank == 0:
    minimum = int(input('Mindestlänge (1 wenn kein min): ')) - 1
    maximum = int(input('Maximale länge: '))
    alphabet = None
    if input('Hat kleinbuchstaben= (y/n): ') == "y":
        alphabet = string.ascii_lowercase
    if input('Hat grossbuchstaben? (y/n): ') == "y":
        if alphabet is not None:
            alphabet += string.ascii_uppercase
        else:
            alphabet = string.ascii_uppercase
    if input('Hat Zahlen? (y/n): ') == "y":
        if alphabet is not None:
            alphabet += string.digits
        else:
            alphabet = string.digits
    if input('Hat sonderzeichen? (y/n): ') == "y":
        if alphabet is not None:
            alphabet += string.punctuation
        else:
            alphabet = string.punctuation
else:
    minimum = None
    maximum = None
    alphabet = None

# Boradcast wordlist settings to slaves
minimum = comm.bcast(minimum, root=0)
maximum = comm.bcast(maximum, root=0)
alphabet = comm.bcast(alphabet, root=0)

#starttime = datetime.datetime.now()

result = []

# set min and max range
for x in range(maximum):
    if x < minimum:
        continue

    #init array
    output = []
    i = 0
    for letter in alphabet:
        # every process handles his own slice of the init alphabet
        if i % size == rank:
            output.append(letter)
        i+=1

    # append letters to existing letters in array
    for y in range(x):
        newoutput = []
        for z in output:
            for letter in alphabet:
                newoutput.append(z + letter)
        output = newoutput
    result.append(output)

#looptime = datetime.datetime.now()

# this is no parallel writing but its still better than no writing at all so STFU!
f = open(f'wordlists/test_{rank}.txt', "w")
for line in result:
    for entry in line:
        f.write(entry + '\n')
f.close()

####### THIS WAS ONLY FOR TESTINT PURPOUSE
# paralleltime = datetime.datetime.now()
#
# buffer = np.hstack(result)
#
# recvbuf = comm.gather(buffer, root=0)
#
# if rank == 0:
#     writeout = np.hstack(recvbuf)
#     f = open(f'wordlists/test_single.txt', "w")
#     for entry in writeout:
#         f.write(entry + '\n')
#     f.close()
#     print("looptime: " + str(looptime - starttime))
#     print("parallelwrite: " + str(paralleltime - looptime))
#     print("gathertime: " + str(datetime.datetime.now() - paralleltime))
#





# # FROM HERE THIS SHIT DOES NOT WORK! EITHER FIX IT OR SEND DATA INSTEAD OF WRITE DATA
# amode = MPI.MODE_WRONLY|MPI.MODE_CREATE
# fh = MPI.File.Open(comm, "wordlists/test.txt", amode)
# offset = comm.Get_rank()*buffer.nbytes
#
# fh.Write_at_all(offset, buffer)
# fh.Close()



# mpiexec /np 8 python wordlist_generator.py