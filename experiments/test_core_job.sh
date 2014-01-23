#!/bin/bash
#SBATCH -A b2010008
#SBATCH -p core
#SBATCH -n 1
#SBATCH -t 01:45:00
#SBATCH -J test_core_job
#SBATCH -o "/home/alneberg/glob/msc_thesis/log/slurm/slurm-%j.test_core_job.out"
concoct --composition_file /proj/b2010008/nobackup/projects/hmp-mock/metassemble/assemblies/ray/noscaf/noscaf_41/ma-contigs.fa --coverage_file /home/alneberg/totally_bogus/coverage.tsv
