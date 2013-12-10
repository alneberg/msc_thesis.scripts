#!/usr/bin/env python
DESC="""Creates symlinks within given directory to first n files in
given source dir"""
import sys
import os

from logbook import Logger
from argparse import ArgumentParser
import random

def main(args):
    """For each dir in sequence_dirs, create a symlink to it from 
    output_dir. """
    seq_dirs = args.sequence_dirs
    dir_count = 0
    source = args.output_dir
    entries = (fn for fn in os.listdir(seq_dirs))
    if args.random:
        entries = random.sample(entries, args.n)
    for seq_dir in sorted(entries):
        if dir_count >= args.n:
            break
        add_genome(seq_dirs, seq_dir, args)
        dir_count += 1

def add_genome(seq_dirs, seq_dir, args):
    seq_dir_path = os.path.join(seq_dirs,seq_dir)
    source_path = os.path.join(args.output_dir, seq_dir)
    os.symlink(seq_dir_path, source_path)


if __name__=="__main__":
    parser = ArgumentParser(description=DESC)
    parser.add_argument('sequence_dirs', help="Root path where all sequence files are located")
    parser.add_argument('output_dir', help="File where all symlinks end up.")
    parser.add_argument('-n', default=60, type=int,
                        help="Number of files to link to")
    parser.add_argument('--random', action="store_true",
                        help="Choose the genomes randomly")
    args = parser.parse_args()
    main(args)
