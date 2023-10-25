#coding=utf-8
# File      :   data_div_csv.py
# Time      :   2022/08/09 15:15:46
# Author    :   Jinghan Peng
# Desciption:   

import collections
import os, sys
import argparse
from tqdm import tqdm
import random
import vaex

def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_path", type=str, default="/data3/pengjinghan/voxceleb_dataset/data_list/dataset_nosp/data.csv", help="")
    parser.add_argument("--out_dir", type=str, default="/data3/pengjinghan/voxceleb_dataset/data_list/dataset_nosp/instance", help="output directory")
    
    parser.add_argument("--valid_spks", type=int, default=5994) #17982)
    parser.add_argument("--valid_utts_pspk", type=int, default=1)
    
    args = parser.parse_args()
    return args


def main():
    args = parse_opt()
    
    spk2lines = collections.defaultdict(list)
    sample_set = set()
    
    with open(args.in_path, 'r') as rf:
        lines = rf.readlines()
        title_line = lines[0]
        # title_list = title_line.strip().split()
        for line in tqdm(lines[1:]):
            label = line.strip().split()[2]
            spk2lines[label].append(line)
            
            sample_set.add(line)

    
    print(f"num samples: {len(sample_set)}")
    print(f"num spks: {len(spk2lines)}")
    assert len(spk2lines) >= args.valid_spks, f"[ERROR] Requires valid_spks is equal to or less than the number of speakers"
    
    spks_list = list(spk2lines.keys())
    valid_spk_select = random.sample(spks_list, args.valid_spks) # 选择的valid的spk列表
    
    
    valid_lines = list()
    for spk in valid_spk_select:
        if len(spk2lines[spk]) > args.valid_utts_pspk: 
            utt_sample = random.sample(spk2lines[spk], args.valid_utts_pspk)            
            valid_lines.extend(utt_sample)
        else:
            print(f"spk {spk} has too little utt({len(spk2lines[spk])} utts)")
            
            
    """ write csv """
    # valid
    print(f"valid sample num: {len(valid_lines)}")
    valid_csv_dir = os.path.join(args.out_dir, "valid", "csv")
    os.makedirs(valid_csv_dir, exist_ok=True)
    with open(os.path.join(valid_csv_dir, "valid.csv"), 'w') as wf:
        wf.write(title_line)
        wf.writelines(valid_lines)

    # train
    train_csv_dir = os.path.join(args.out_dir, "train", "csv")
    os.makedirs(train_csv_dir, exist_ok=True)
    train_lines = list(sample_set - set(valid_lines))
    print(f"train sample num: {len(train_lines)}")
    with open(os.path.join(train_csv_dir, "train.csv"), 'w') as wf:
        wf.write(title_line)
        wf.writelines(train_lines)
        
    
    """ csv to hdf5"""
    # valid
    df = vaex.from_csv(os.path.join(valid_csv_dir, "valid.csv"), sep="\t")
    df = df.sort(by="utt_id")
    valid_hdf5_dir = os.path.join(args.out_dir, "valid", 'hdf5')
    os.makedirs(valid_hdf5_dir, exist_ok=True)
    hdf5_path = os.path.join(valid_hdf5_dir, f"valid.hdf5")
    df.export(hdf5_path)          
    
    # train
    df = vaex.from_csv(os.path.join(train_csv_dir, "train.csv"), sep="\t")
    df = df.sort(by="utt_id")
    train_hdf5_dir = os.path.join(args.out_dir, "train", 'hdf5')
    os.makedirs(train_hdf5_dir, exist_ok=True)
    hdf5_path = os.path.join(train_hdf5_dir, f"train.hdf5")
    df.export(hdf5_path)      
    

if __name__ == '__main__':
    main()

