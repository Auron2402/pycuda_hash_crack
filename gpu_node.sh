#!/bin/bash -l
#
#SBATCH --nodes=1
#SBATCH -tasks-per-node=1
#SBATCH -job-name=CodeBreakerCuda
#SBATCH --export=NONE

# script start here
echo "tinyGPU Node:"

# not sure why we need this
unset SLURM_EXPORT_ENV

# goto project dir
# shellcheck disable=SC2164
cd pycuda_hash_crack || exit

# load required modules
module load python/3.7-anaconda
module load cuda/10.2

# configure environment vars for conda
source /apps/python/3.7-anaconda/etc/profile.d/conda.sh
# activate virtual conda env
conda activate myenv

# start project
python3 numba_test.py

