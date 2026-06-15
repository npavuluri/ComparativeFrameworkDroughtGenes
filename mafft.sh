#!/bin/bash
#SBATCH -J mafft
#SBATCH -o ./%x.%j.%N.out
#SBATCH -D ./
#SBATCH -e ./%x.%j.%N.err
#SBATCH --get-user-env
#SBATCH --partition=CPU
#SBATCH --mem=50G
#SBATCH --nodes=1
#SBATCH --cpus-per-task=96

set -uo pipefail # leave out -e so you can see failures, all the jobs were failing before even writing to error file.
IFS=$'\n\t'

source ~/miniconda3/etc/profile.d/conda.sh
conda activate mafft || { echo "Conda failed to activate" >&2; exit 1; } #sbatch job fails before even activating the env, so to see what causes it.

mafft NAC.fa > NAC_aligned.fa

# Always deactivate safely
set +u
conda deactivate
set -u

