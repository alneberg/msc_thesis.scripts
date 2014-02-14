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
        if not clustering_files:
            continue
        gt_file = filter(lambda x: 'gt' in x, clustering_files)[0]
        threshold = filtered_result.match(gt_file).groups()[-1]
        regular_clustering_file = filter(lambda x: 'gt' not in x, clustering_files)[0]

        stats_gt = run_validate(os.path.join(result_path, gt_file),
                                args.validation_correct_file,
                                args.validate_path, suffix=args.name)
        stats_regular = run_validate(os.path.join(result_path, 
                                                  regular_clustering_file),
                                     args.validation_correct_file,
                                     args.validate_path, suffix=args.name)
        columns_different = ["Rand", "Rec.", "M", "N", "S", "Prec.", "AdjRand", "NMI"]
        columns_different = [col + args.name for col in columns_different]
        for column in columns_different:
            stats_regular[column + "_gt"] = stats_gt[column]
        
        stats[result_dir] = stats_regular
    stats_df = p.DataFrame.from_dict(stats, orient="index")
    if os.path.isfile(args.output_file) and args.merge_files:
        original_df = p.io.parsers.read_csv(args.output_file, index_col=0)
        original_df = original_df.join(stats_df, how='outer')
        original_df.to_csv(args.output_file)
    else:
        stats_regular["gt"] = threshold
        stats_df.to_csv(args.output_file)

def run_validate(cfile, sfile, validate_path, suffix=""):
    validate_so = subprocess.check_output(['perl', validate_path, 
                                           '--sfile={}'.format(sfile),
                                           '--cfile={}'.format(cfile) ])
    headers = [h + suffix for h in validate_so.split('\n')[0].split('\t')]
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
    parser.add_argument('--name', default="", help="Name of run, to be appended to table columns.") 
    parser.add_argument('--merge_files', action='store_true',
            help="Merge with existing output file, otherwise overwrite")
    args = parser.parse_args()
    main(args)
