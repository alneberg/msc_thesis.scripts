#!/usr/bin/env python
"""A script to calculate the anosim statistic for a dataset"""

import pandas as pd

from skbio.stats.distance import anosim, DistanceMatrix
from scipy.spatial.distance import pdist, squareform

import argparse
import sys

def main(args):
    data_df =  pd.read_table(args.data, index_col=0)
    data_df_nonnull = data_df[data_df['taxon'].notnull()]

    val_cols = data_df_nonnull.columns
    val_cols.remove('taxon')

    dm = DistanceMatrix(squareform(pdist(data_df_nonnull[val_cols], metric='euclidean')))
    a = anosim(dm, data_df_nonnull['taxon'], permutations=0)

    a_df = pd.DataFrame(a).T
    a_df.index = [args.data_name]

    a_df.to_csv(sys.stdout, header=None)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("data")
    parser.add_argument("data_name")
    args = parser.parse_args()

    main(args)
