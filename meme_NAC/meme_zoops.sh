#!/bin/bash

set -uo pipefail # leave out -e so you can see failures, all the jobs were failing before even writing to error file.
IFS=$'\n\t'

source ~/miniconda3/etc/profile.d/conda.sh
conda activate meme || { echo "Conda failed to activate" >&2; exit 1; } #sbatch job fails before even activating the env, so to see what causes it.

meme ./NAC_combined.fa -protein -mod zoops -nmotifs 20 -minw 10 -maxw 50 -evt 0.000001 -oc ./ -maxsize 1000000 -minsites 800 -searchsize 0 -brief 100000 #-brief flag gives the full output and using fimo is not necessary anymore. #-searchsize flag is necessary because meme doesn't find the motifs in all your sequences but rather samples a set which could be < 500 and then uses fimo to find the already discovered motifs in remaining sequences.

# Always deactivate safely
set +u
conda deactivate
set -u

