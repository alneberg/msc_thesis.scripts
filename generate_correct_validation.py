#!/usr/bin/env python
DESC="""Looks at the contig header and generates a result file that can be used with validate.py. 
if the genome tag is used, the reference genomes top directory needs to be supplied and the script will
iterate over all reference genome sequence headers but use the genome name as correct clustering."""
import fileinput
import sys
import os

import pandas as p
import numpy as np
from Bio import SeqIO
from logbook import Logger
from argparse import ArgumentParser

def parse_contig_id(seq):
    return seq.description.split(" ")[1]

def parse_seq_id(seq):
    return seq.description.split(" ")[0]

def genome_id_dict(genome_root_path):
    con_to_gen = {}
    for seq_dir in os.listdir(genome_root_path):
        seq_dir_path = os.path.join(genome_root_path, seq_dir)
        for f in os.listdir(seq_dir_path):
            # ncbi genomes end with fna
            if f.endswith(".fna"):
                with open(os.path.join(seq_dir_path, f)) as seq_file:
                    original_seqs = SeqIO.parse(seq_file, "fasta")
                    for seq in original_seqs:
                        con_to_gen[parse_seq_id(seq)] = seq_dir
    return con_to_gen

def main(args):
    """For each contig in input file, parse sequence id from contig id."""
    contig_file = args.contig_file
    results = {}
    if args.genome:
        assert args.genomes_top_dir
        con_to_gen = genome_id_dict(args.genomes_top_dir)
    with open(contig_file, 'r') as seq_file:
        contigs = SeqIO.parse(seq_file, "fasta")
        for contig in contigs:
            if args.genome:
                results[contig.id] = con_to_gen[parse_contig_id(contig)]
            else:
                results[contig.id] = parse_contig_id(contig)
    results = p.DataFrame.from_dict(results, orient="index")
    results.to_csv(args.output_file, sep=',', header=None)

if __name__=="__main__":
    parser = ArgumentParser(description=DESC)
    parser.add_argument('contig_file', help="File with contigs.")
    parser.add_argument('output_file', help="File where correct clustering end up.")
    parser.add_argument('-g', '--genome', action='store_true', 
            help="Use genome level instead of sequence level")
    parser.add_argument('--genomes_top_dir', 
            help="The path to where the genome sequence files are located") 
    args = parser.parse_args()
    main(args)
