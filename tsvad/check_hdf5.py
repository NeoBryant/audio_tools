#coding=utf-8
# File      :   check_hdf5.py
# Time      :   2022/01/21 16:03:51
# Author    :   Jinghan Peng
# Desciption:   检查生成的hdf5的每个ark路径是否正确

import os, sys
import kaldiio
from tqdm import tqdm
import vaex


def main():
    # hdf5_path = "/data/pengjinghan/tsvad_train_data/data_augx4/train.hdf5"
    
    # data = vaex.open(hdf5_path)
    # num_data = len(data)
    # for i in tqdm(range(num_data)):
    #     item = data[i]
    #     utt_id = item[0]
    #     ark_paths = item[1:]
    #     if utt_id != "mandarin_41719-00144180_00160200-music":
    #         continue
        
    #     for ark_path in ark_paths:
    #         mat = kaldiio.load_mat(ark_path)
    
    csv_path = "/data/pengjinghan/tsvad_train_data/data_augx4/train.csv"
    with open(csv_path, 'r') as rf:
        lines = rf.readlines() 
        lines = lines[1:]
        for line in tqdm(lines):
            line = line.strip().split()
            utt_id = line[0]
            # if utt_id != "mandarin_24164-00128160_00144180-reverb": #"mandarin_41719-00144180_00160200-music":
            #     continue
            feat_ark_paths = line[1]
            
            try:
                mat = kaldiio.load_mat(feat_ark_paths)
            except:
                print(utt_id)
            
            
    
if __name__ == '__main__':
    main()

