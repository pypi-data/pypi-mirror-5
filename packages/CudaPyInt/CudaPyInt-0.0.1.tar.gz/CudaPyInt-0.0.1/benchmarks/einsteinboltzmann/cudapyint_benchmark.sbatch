#!/bin/bash -l
#SBATCH --job-name="$1 shared False 3" 
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1 
#SBATCH --ntasks-per-node=1
#SBATCH --time=00:59:00 
#======START=============================== 
echo "On which nodes it executes" 
echo $SLURM_JOB_NODELIST 
echo "Now run CudaPyint..."
cd /users/jakeret/workspace/CudaPyInt/benchmarks/einsteinboltzmann
aprun -B python ./run_benchmarks_cmd2.py shared False 3 $1
#======END=================================

