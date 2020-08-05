#!/bin/bash -l
#
#PBS -l nodes=1:ppn=16,walltime=00:60:00
#PBS -N CodeBreakerCuda

# script start here
echo "tinyGPU Node:"

# not sure why we need this
unset SLURM_EXPORT_ENV

# goto project dir
# shellcheck disable=SC2164
cd pycuda_hash_crack || exit

# load required modules
module load intelmpi/2019up05-intel
module load cuda/10.2
module load python/3.7-anaconda

# configure environment vars for conda
source /apps/python/3.7-anaconda/etc/profile.d/conda.sh
# activate virtual conda env
conda activate myenv

# start project
echo "running mpirun:"
mpirun -n 16 python mpi_test.py e10adc3949ba59abbe56e057f20f883e HashesOrg

