#!/usr/bin/env python
DESC="""Samples contigs of random length from all sequence files in 
the sequence_dirs argument """
import fileinput
import sys
import os

from Bio import SeqIO
from logbook import Logger
from argparse import ArgumentParser

from bu.seq_sampling import sample_all

def main(args):
    """For each dir in sequence_dirs, open each file and sample 
    from those sequences"""
    seq_dirs = args.sequence_dirs
    seqs = []
    fraction = args.fraction
    for seq_dir in os.listdir(seq_dirs):
        seq_dir = os.path.join(seq_dirs,seq_dir)
        for f in os.listdir(seq_dir):
            # ncbi genomes end with fna
            if f.endswith(".fna"):
                with open(os.path.join(seq_dir,f), 'r') as seq_file:
                    original_seqs = SeqIO.parse(seq_file, "fasta")
                    seqs += sample_all(original_seqs, fraction)
    for i, seq in enumerate(seqs):
        seq.id = "contig_" + str(i)
        seq.description += "| " + str(seq.start_position)
    SeqIO.write(seqs, args.output_file, "fasta")

if __name__=="__main__":
    parser = ArgumentParser(description=DESC)
    parser.add_argument('sequence_dirs', help="Root path where all sequence files are located")
    parser.add_argument('output_file', help="File where all contigs end up.")
    parser.add_argument('--fraction', default=0.8, type=float,
                        help="fraction to sample from each sequence")
    args = parser.parse_args()
    main(args)
