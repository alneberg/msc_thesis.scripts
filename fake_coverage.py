#!/usr/bin/env python
DESC="""Reads sequences and outputs table with zeros for each id. """
import fileinput
import sys
import os

from Bio import SeqIO
from logbook import Logger
from argparse import ArgumentParser

def main(args):
    """For each sequence in sequence_file, output zero to one column. """
    seqs = args.sequence_file
    covs = {}
    with open(seqs, 'r') as seq_file:
        for seq in SeqIO.parse(seq_file, "fasta"):
            covs[seq.id] = 0
    s = p.Series(covs)
    s.to_csv(args.output_file)

if __name__=="__main__":
    parser = ArgumentParser(description=DESC)
    parser.add_argument('sequence_file', help="File where sequences are located")
    parser.add_argument('output_file', help="File where fake coverage end up.")
    args = parser.parse_args()
    main(args)
