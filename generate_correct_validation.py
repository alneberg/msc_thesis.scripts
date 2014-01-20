#!/usr/bin/env python
DESC="""Looks at the contig header and generates a result file that can be used with validate.py"""
import fileinput
import sys
import os

import pandas as p
import numpy as np
from Bio import SeqIO
from logbook import Logger
from argparse import ArgumentParser

def main(args):
    """For each contig in input file, parse genome id from contig id."""
    contig_file = args.contig_file
    results = {}
    with open(contig_file, 'r') as seq_file:
        contigs = SeqIO.parse(seq_file, "fasta")
        for contig in contigs:
            results[contig.id] = contig.description.split(" ")[1]
    results = p.DataFrame.from_dict(results, orient="index")
    results.to_csv(args.output_file, sep=',', header=None)

if __name__=="__main__":
    parser = ArgumentParser(description=DESC)
    parser.add_argument('contig_file', help="File with contigs.")
    parser.add_argument('output_file', help="File where correct clustering end up.")
    args = parser.parse_args()
    main(args)
