#coding=utf-8
# File      :   check_ark.py
# Time      :   2022/06/01 15:10:01
# Author    :   Jinghan Peng
# Desciption:   检查ark表单的ark文件是否存在

import os, sys

from tqdm import tqdm
import kaldiio
import numpy as np

def main():
    in_path = "/data3/pengjinghan/ffsvc2020_concat_rand_speed_cut_1200/data_list/feats.scp"
    
    with open(in_path, 'r') as rf:
        for line in tqdm(rf.readlines()):
            utt, feat_path = line.strip().split()
            ark_path = feat_path.split(':')[0]
            if not os.path.exists(ark_path):
                print(ark_path)
                return
            
            feat = kaldiio.load_mat(feat_path)
            print(feat.shape)
            
            return

if __name__ == '__main__':
    main()

