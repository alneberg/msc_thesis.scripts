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

def taxonomy_dict(taxonomy_file, con_to_gen, level):
    tax_df = p.io.parsers.read_csv(taxonomy_file, sep='\t', index_col = 0)
    if not level in tax_df.columns:
        raise ValueError
    gen_to_tax = tax_df[level].to_dict()
    con_to_tax = {}
    for con, gen in con_to_gen.iteritems():
        con_to_tax[con] = gen_to_tax[gen]
    return con_to_tax

def main(args):
    """For each contig in input file, parse sequence id from contig id."""
    contig_file = args.contig_file
    results = {}
    if args.level != 'contig':
        assert args.genomes_top_dir
        con_to_gen = genome_id_dict(args.genomes_top_dir)
        if args.level != 'genome':
            assert args.taxonomy_file
            con_to_tax = taxonomy_dict(args.taxonomy_file, con_to_gen, args.level)
        else:
            con_to_tax = con_to_gen

    with open(contig_file, 'r') as seq_file:
        contigs = SeqIO.parse(seq_file, "fasta")
        for contig in contigs:
            if args.level != 'contig':
                results[contig.id] = con_to_tax[parse_contig_id(contig)]
            else:
                results[contig.id] = parse_contig_id(contig)
    results = p.DataFrame.from_dict(results, orient="index")
    results_notnull = results[results[0].notnull()]
    results_notnull.to_csv(args.output_file, sep=',', header=None)

if __name__=="__main__":
    parser = ArgumentParser(description=DESC)
    parser.add_argument('contig_file', help="File with contigs.")
    parser.add_argument('output_file', help="File where correct clustering end up.")
    parser.add_argument('--genomes_top_dir', 
            help="The path to where the genome sequence files are located") 
    parser.add_argument('--taxonomy_file', 
            help="Tsv file containing full taxonomy for each genome "
            "represented in the contigs.")
    parser.add_argument('--level', default='contig',
            help="Taxonomic level to use, default contig")
    parser.add_argument('--filter-nones', action='store_true',
            help="Remove all results where the taxonomy would be empty") 
    args = parser.parse_args()
    main(args)
