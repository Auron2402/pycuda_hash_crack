#!/usr/bin/env bash
echo "local PC:"
rsync -r . hpcv234h@cshpc.rrze.fau.de:/home/hpc/rzku/hpcv234h/pycuda_hash_crack
#ssh hpcv234h@cshpc.rrze.fau.de 'bash -s' < run_on_cluster.sh