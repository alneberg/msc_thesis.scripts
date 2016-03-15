#!/usr/bin/env python
DESC="""Calculates validation scores for a clustering result. """
import sys
import os
import pandas as pd
from sklearn import metrics

from argparse import ArgumentParser

def main(args):
    df = pd.read_table(args.clustering_result, sep=',', index_col=0, names=['contigs', 'clusters'])
    true_df = pd.read_table(args.correct_result, sep=',', index_col=0, header=None)
    taxa_to_int = {}
    for i, taxa in enumerate(true_df[1].unique()):
        taxa_to_int[taxa] = i

    df['true_labels'] = true_df[1].apply(lambda x: taxa_to_int[x])
    metrics_d = {}
    metrics_d['adj_rand'] = metrics.adjusted_rand_score(df['clusters'], df['true_labels'])
    metrics_d['completeness'] = metrics.completeness_score(df['true_labels'], df['clusters'])
    metrics_d['homogeneity_score'] = metrics.homogeneity_score(df['true_labels'], df['clusters'])
    print(pd.Series(metrics_d))

if __name__=="__main__":
    parser = ArgumentParser(description=DESC)
    parser.add_argument('clustering_result', help="Csv file containing clustering results.")
    parser.add_argument('correct_result',
                        help=("Correct clustering file, for "
                              "all contigs"))
    args = parser.parse_args()
    main(args)
