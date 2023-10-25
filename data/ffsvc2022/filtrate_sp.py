#coding=utf-8
# File      :   filtrate_sp.py
# Time      :   2022/06/01 18:13:02
# Author    :   Jinghan Peng
# Desciption:   去掉表单中的变速变调三倍增强

import os, sys
from tqdm import tqdm

def main():
    in_dir = "/data3/pengjinghan/ffsvc2020_voxceleb12_fbank81_16k_cut_1200/data_list"
    out_dir = "/data3/pengjinghan/ffsvc2020_voxceleb12_fbank81_16k_cut_1200/data_list_no_sp"
    
    os.makedirs(out_dir, exist_ok=True)
    
    file_name_list = ["feats.scp", "utt2spk", "utt2num_frames"]
    for file_name in file_name_list:
        in_path = os.path.join(in_dir, file_name)
        out_path = os.path.join(out_dir, file_name)
        if not os.path.isfile(in_path):
            print(f"Not exist: {in_path}")
            continue
        with open(in_path, 'r') as rf, open(out_path, 'w') as wf:
            for line in tqdm(rf.readlines()):
                utt, _ = line.strip().split()
                if utt.startswith("sp0.9-") or utt.startswith("sp1.1-"):
                    pass
                else:
                    wf.write(line)
                    
    
    

if __name__ == '__main__':
    main()

