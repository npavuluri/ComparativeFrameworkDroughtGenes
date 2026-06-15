#!/bin/bash

set -uo pipefail # leave out -e so you can see failures, all the jobs were failing before even writing to error file.
IFS=$'\n\t'

source ~/miniconda3/etc/profile.d/conda.sh
conda activate iqtree || { echo "Conda failed to activate" >&2; exit 1; } #sbatch job fails before even activating the env, so to see what causes it.

# Let IQ-TREE find the best model 
iqtree -s NAC_aligned.fasta -m MFP -mset LG,WAG,JTT -nt 32 -pre NAC_full -bb 1000 -alrt 1000 #-bb for bootstrap which resolves the trees, MFP is ModelFinderPlus.
# Check model_test.iqtree for best model recommendation

# Always deactivate safely
set +u
conda deactivate
set -u
