#!/bin/bash

set -uo pipefail # leave out -e so you can see failures, all the jobs were failing before even writing to error file.
IFS=$'\n\t'

source ~/miniconda3/etc/profile.d/conda.sh
conda activate interproscan || { echo "Conda failed to activate" >&2; exit 1; } #sbatch job fails before even activating the env, so to see what causes it.

nextflow run ebi-pf-team/interproscan6 \
    -profile slurm,singularity \
    --input fasta_files/Zea_mays.fa \
    --datadir data
    --formats json,tsv \
    --outdir results \
    --goterms \
    --pathways

# All fasta files work and have no issues, except Avena fasta, which is too big!
# Always deactivate safely
set +u
conda deactivate
set -u
