#!/usr/bin/env python
"""Reads through the true clustering file and collapses the classification 
if it is consistent for all subcontigs."""

import fileinput
import sys
import os

from logbook import Logger
import pandas as pd
from argparse import ArgumentParser

def main(args):
    t = pd.read_table(args.true_clustering, sep=',', names=["contig_id", "cluster", "not_sure1", "not_sure2"], index_col=0)
    
    clustering = {}
    for contig in t.index:
        real_contig = contig.split('.')[0]
        if real_contig in clustering:
            if clustering[real_contig] != t['cluster'].ix[contig]:
                sys.stderr.write("{0} had multiple assignments. \n".format(real_contig))
        else:
            clustering[real_contig] = t['cluster'].ix[contig]
    
    df_out = pd.DataFrame.from_dict(clustering, orient='index')
    df_out.to_csv(sys.stdout, header=None) 

if __name__=="__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('true_clustering', help=("Csv file containing contig id and true clustering in the first two columns. "
                                                "Contig ids names the same id root before a dot will be collapsed together."))
    args = parser.parse_args()
    main(args)
