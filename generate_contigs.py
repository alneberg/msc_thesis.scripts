#!/usr/bin/env python
DESC="""Samples contigs of random length from all sequence files in 
the sequence_dirs argument """
import fileinput
import sys
import os

from Bio import SeqIO
from logbook import Logger


def main(args):
    """For each dir in sequence_dirs, open each file and sample 
    50 % from those sequences"""
    seq_dirs = args.sequence_dirs
    seqs = []
    for seq_dir in os.listdir(seq_dirs):
        for f in os.listdir(seq_file):
            # ncbi genomes end with fna
            if f.endswith(".fna"):
                with open(os.path.join(), 'r') as seq_file:
                    original_seqs = SeqIO.parse(seq_file, "fasta"))
                    seqs.append(sample_all(original_seqs))
    SeqIO.write(seqs, args.output_file, "fasta")

if __name__=="__main__":
    parser = ArgumentParser(description=DESC)
    parser.add_argument('sequence_dirs', help="Root path where all sequence files are located")
    parser.add_argument('output_file', help="File where all contigs end up.")
    args = parser.parse_args()
    main(args)
