#!/bin/bash

set -uo pipefail # leave out -e so you can see failures, all the jobs were failing before even writing to error file.
IFS=$'\n\t'

source ~/miniconda3/etc/profile.d/conda.sh
conda activate interproscan 

# Make sure the files exist first
ls -la test/Avena_sativa.fa.split/

# Corrected loop
for file in test/Avena_sativa.fa.split/Avena_sativa.part_???.fa; do
    # Check if file exists (in case no matches)
    [ -f "$file" ] || continue
    
    echo "Processing $file"
    base=$(basename "$file" .fa)
    
    nextflow run ebi-pf-team/interproscan6 \
        -profile slurm,singularity \
        --input "$file" \
        --datadir data \
        --formats json,tsv \    
        --outdir "results/$base" \
        --goterms \
        --pathways
done

# Always deactivate safely
set +u
conda deactivate
set -u
