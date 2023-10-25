#coding=utf-8
# File      :   gen_online_data_manifest.py
# Time      :   2022/04/18 19:25:02
# Author    :   Jinghan Peng
# Desciption:   根据online表单文件划分训练集和测试集

import os, sys
import math
import random
# import codecs
import argparse
import sys
import shutil
import collections
import json
from tqdm import tqdm


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest_path", type=str, help="", default="/data3/pengjinghan/exp/data/cnsrc2022/data_list/data_cut/data_cut.manifest.json")
    parser.add_argument("--save_dir", type=str, help="", default="/data3/pengjinghan/exp/data/cnsrc2022/data_list/dataset")
    parser.add_argument("--valid_spks", type=int, default=2751)
    parser.add_argument("--valid_utts_pspk", type=int, default=1)
    args = parser.parse_args()
    return args

def main():
    args = parse_opt()
    
    os.makedirs(args.save_dir, exist_ok=True)
    

    """read manifest"""
    spk2index_list = collections.defaultdict(list)
    index2data = dict()
    with open(args.manifest_path, 'r') as rf:
        for index, (line) in tqdm(enumerate(rf.readlines())):
            index += 1 # from 1 start
            data = {"index":index} 
            # data = eval(line.strip())
            data.update(eval(line.strip())) # str->dict
            
            spk = data["label"]
            spk2index_list[spk].append(index)
            index2data[index] = data

    print(f" num of spks: {len(spk2index_list.keys())}")
    
    """get valid utt list"""
    valid_index_list = list() # all valid indexs
    spk2index_list = list(spk2index_list.items())
    random.shuffle(spk2index_list)
    spk2index_list = spk2index_list[:args.valid_spks]
    for spk, index_list in spk2index_list:
        if len(index_list) > args.valid_utts_pspk:
            sub_valid_index_list = random.sample(index_list, args.valid_utts_pspk)
            valid_index_list.extend(sub_valid_index_list)
        else:
            print(f"{spk} has only {len(index_list)} utt(s)")

    
    print(f" num of valid utts: {len(valid_index_list)}")
    print(f" num of train utts: {len(index2data) - len(valid_index_list)}")
    
    """write manifest"""
    train_manifest_path = os.path.join(args.save_dir, "train.json")
    valid_manifest_path = os.path.join(args.save_dir, "valid.json")
    with open(train_manifest_path, 'w') as wf1, open(valid_manifest_path, 'w') as wf2: 
        for index, data in tqdm(index2data.items()):
            json_data = json.dumps(data)
            if index in valid_index_list:
                wf2.write(json_data+"\n")
            else:
                wf1.write(json_data+"\n")
    
    

if __name__ == "__main__":
    main()