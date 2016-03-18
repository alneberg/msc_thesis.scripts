#!/usr/bin/env python
"""A script to calculate the composition data from a contigs fasta file"""
import pandas as pd
from Bio import SeqIO

import os
import numpy as np

from itertools import product, tee
from collections import Counter, OrderedDict

import argparse
import sys

def generate_feature_mapping(kmer_len):
    BASE_COMPLEMENT = {"A":"T","T":"A","G":"C","C":"G"}
    kmer_hash = {}
    counter = 0
    for kmer in product("ATGC",repeat=kmer_len):
        if kmer not in kmer_hash:
            kmer_hash[kmer] = counter
            rev_compl = tuple([BASE_COMPLEMENT[x] for x in reversed(kmer)])
            kmer_hash[rev_compl] = counter
            counter += 1
    return kmer_hash, counter

def window(seq,n):
    els = tee(seq,n)
    for i,el in enumerate(els):
        for _ in range(i):
            next(el, None)
    return zip(*els)

def _calculate_composition(comp_file, length_threshold, kmer_len):
    #Generate kmer dictionary
    feature_mapping, nr_features = generate_feature_mapping(kmer_len)

    # Store composition vectors in a dictionary before creating dataframe
    composition_d = OrderedDict()
    contig_lengths = OrderedDict()
    for seq in SeqIO.parse(comp_file,"fasta"):
        seq_len = len(seq)
        if seq_len<= length_threshold:
            continue
        contig_lengths[seq.id] = seq_len
        # Create a list containing all kmers, translated to integers
        kmers = [
                feature_mapping[kmer_tuple]
                for kmer_tuple
                in window(str(seq.seq).upper(), kmer_len)
                if kmer_tuple in feature_mapping
                ]
        # numpy.bincount returns an array of size = max + 1
        # so we add the max value and remove it afterwards
        # numpy.bincount was found to be much more efficient than
        # counting manually or using collections.Counter
        kmers.append(nr_features - 1)
        composition_v = np.bincount(np.array(kmers))
        composition_v[-1] -= 1
        # Adding pseudo counts before storing in dict
        composition_d[seq.id] = composition_v + np.ones(nr_features)
    composition = pd.DataFrame.from_dict(composition_d, orient='index', dtype=float)
    contig_lengths = pd.Series(contig_lengths, dtype=float)
    return composition, contig_lengths

def main(args):
    composition, contig_lengths = _calculate_composition(args.comp_file, args.length_threshold, args.kmer_len)
    composition['length'] = contig_lengths
    composition.to_csv(args.output_file, sep='\t', compression='gzip')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("comp_file", help="Contigs Fasta file")
    parser.add_argument("output_file")
    parser.add_argument("--length_threshold", default=0, type=int, help="The length threshold to use when filtering which contigs to include")
    parser.add_argument("--kmer_len", default=1, type=int, help="The kmer length to use")
    args = parser.parse_args()

    main(args)
