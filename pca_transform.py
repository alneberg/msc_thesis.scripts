#!/usr/bin/env python
"""A script to calculate the pca transformed data for a dataset, will print gzip:ed output to output file"""

import pandas as pd

from sklearn.decomposition import PCA

import argparse
import sys

def main(args):
    data_df =  pd.read_table(args.data, index_col=0, compression='gzip')

    true_taxon = pd.read_table(args.true_taxon, index_col=0, sep=',', header=None, names=['contig_id', 'taxon', 'fraction_of_unamb_reads', 'unamb_reads_total'])

    val_cols = list(data_df.columns)
    val_cols.remove('length')

    pca = PCA()
    pca_obj = pca.fit(data_df[val_cols])
    pca_data = pca_obj.transform(data_df[val_cols])

    pca_df = pd.DataFrame(pca_data, index=data_df.index)
    pca_df['taxon'] = true_taxon['taxon']

    if args.pairplot:
        import matplotlib
        matplotlib.use('PDF')
        import matplotlib.pyplot as plt
        import seaborn as sns
        sns.set_context('paper')
        fig = sns.pairplot(pca_df[list(range(int(args.max_plot_col)+1)) + ['taxon']], hue='taxon')
        plt.tight_layout()
        fig.savefig(args.plot_output)

    pca_df.to_csv(args.output_file, sep='\t', compression='gzip')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("data")
    parser.add_argument("true_taxon")
    parser.add_argument("output_file")
    parser.add_argument("--pairplot", action='store_true', help="Use this tag to produce a paired scatter plot matrix")
    parser.add_argument("--max_plot_col", default=4, help="The highest dimension included in the paired scatter plot")
    parser.add_argument("--plot_output", default='pairplot.pdf', help="output file for the plot")
    args = parser.parse_args()

    main(args)
