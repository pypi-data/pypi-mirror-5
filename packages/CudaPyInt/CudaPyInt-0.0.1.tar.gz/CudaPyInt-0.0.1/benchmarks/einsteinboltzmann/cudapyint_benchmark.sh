#!/bin/bash -l
sbatch cudapyint_benchmark.sbatch 100
sbatch cudapyint_benchmark.sbatch 400
sbatch cudapyint_benchmark.sbatch 1000
sbatch cudapyint_benchmark.sbatch 4000
sbatch cudapyint_benchmark.sbatch 10000

