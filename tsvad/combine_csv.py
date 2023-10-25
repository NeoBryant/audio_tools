#coding=utf-8
# File      :   combine_csv.py
# Time      :   2021/12/17 14:41:44
# Author    :   Jinghan Peng
# Desciption:   合并多个相同结构的csv为一个csv

import os, sys
import pandas as pd
from argparse import ArgumentParser

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--csv_paths", type=str, nargs='+', required=True)
    parser.add_argument("--out_path", type=str, required=True)
    
    args = parser.parse_args()
    return args

def main(args):
    
    with open(args.out_path, 'w') as wf:
        for csv_path in args.csv_paths:
            assert os.path.exists(csv_path)
            with open(csv_path, 'r') as rf:
                lines = rf.readlines()
                headline = lines[0]
                values = lines[1:]
                wf.writelines(values)

    os.system("sed -i '{}' {}".format(f"1i\\{headline}", args.out_path))

if __name__ == '__main__':
    args = parse_args()
    main(args)
    