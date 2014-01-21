#!/usr/bin/env python
DESC="""Runs validation on all result files and appends to results dataframe """
import fileinput
import sys
import os
import re
import subprocess
import pandas as p

from logbook import Logger
from argparse import ArgumentParser

def main(args):
    """For each dir in result_dirs, run validate and collect 
    result into csv output_file. """
    result_dirs = args.result_dirs
    stats = {}
    filtered_result = re.compile('clustering(_gt(\w+))*.csv')
    for result_dir in os.listdir(result_dirs):
        result_path = os.path.join(result_dirs, result_dir)
        
        clustering_files = filter(filtered_result.match, os.listdir(result_path))
        gt_file = filter(lambda x: 'gt' in x, clustering_files)[0]
        threshold = filtered_result.match(gt_file).groups()[-1]
        regular_clustering_file = filter(lambda x: 'gt' not in x, clustering_files)[0]

        stats_gt = run_validate(os.path.join(result_path, gt_file),
                                args.validation_correct_file,
                                args.validate_path)
        stats_regular = run_validate(os.path.join(result_path, 
                                                  regular_clustering_file),
                                     args.validation_correct_file,
                                     args.validate_path)
        columns_different = ["Rand", "Rec.", "M", "N", "S", "Prec.", "AdjRand", "NMI"]
        for column in columns_different:
            stats_regular[column + "_gt"] = stats_gt[column]
        stats_regular["gt"] = threshold
        
        stats[result_dir] = stats_regular

    stats_df = p.DataFrame.from_dict(stats, orient="index")
    stats_df.to_csv(args.output_file)

def run_validate(cfile, sfile, validate_path):
    validate_so = subprocess.check_output(['perl', validate_path, 
                                           '--sfile={}'.format(sfile),
                                           '--cfile={}'.format(cfile) ])
    headers = validate_so.split('\n')[0].split('\t')
    stats = validate_so.split('\n')[1].split('\t')
    stats_dict = dict(zip(headers, stats))

    return stats_dict

if __name__=="__main__":
    parser = ArgumentParser(description=DESC)
    parser.add_argument('result_dirs', help="Root path where all result directories are located")
    parser.add_argument('validation_correct_file',
                        help=("Correct clustering file, for "
                              "all contigs"))
    parser.add_argument('output_file', help="File where all contigs end up.")
    parser.add_argument('validate_path', help="Path to validation script.")
    args = parser.parse_args()
    main(args)
