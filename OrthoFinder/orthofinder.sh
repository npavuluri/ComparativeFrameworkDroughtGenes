#!/bin/bash

set -uo pipefail # leave out -e so you can see failures, all the jobs were failing before even writing to error file.
IFS=$'\n\t'

source ~/miniconda3/etc/profile.d/conda.sh
conda activate orthofinder_3.1


orthofinder -t 96 -f /home/students/n.pavuluri/orthofinder_droughtDB_3.1

# Always deactivate safely
set +u
conda deactivate
set -u

