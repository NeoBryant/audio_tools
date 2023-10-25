#coding=utf-8
# File      :   csv2hdf5.py
# Time      :   2021/12/17 14:37:40
# Author    :   Jinghan Peng
# Desciption:   读取csv转化为hdf5

import os, sys
import vaex
from argparse import ArgumentParser

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--csv_path", type=str, required=True)
    parser.add_argument("--hdf5_path", type=str, required=True)
    
    args = parser.parse_args()
    return args

def main(args):
    assert os.path.exists(args.csv_path)
    
    df = vaex.from_csv(args.csv_path, sep="\t")
    df.export(args.hdf5_path)


if __name__ == '__main__':
    args = parse_args()
    main(args)
    