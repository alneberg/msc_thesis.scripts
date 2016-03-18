#!/usr/bin/env python
"""A script to calculate the anosim statistic for a dataset"""

import pandas as pd

from skbio.stats.distance import anosim, DistanceMatrix
from scipy.spatial.distance import pdist, squareform

import argparse
import sys

def main(args):
    pca_df =  pd.read_table(args.pca_data, index_col=0)
    pca_df_nonnull = pca_df[pca_df['taxon'].notnull()]
    dm = DistanceMatrix(squareform(pdist(pca_df_nonnull[[0,1,2]], metric='euclidean')))
    a = anosim(dm, pca_df_nonnull['taxon'], permutations=0)

    a_df = pd.DataFrame(a).T
    a_df.index = [args.data_name]

    a_df.to_csv(sys.stdout, header=None)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("pca_data")
    parser.add_argument("data_name")
    args = parser.parse_args()

    main(args)
