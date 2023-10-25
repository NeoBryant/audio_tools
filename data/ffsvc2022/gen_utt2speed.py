#coding=utf-8
# File      :   gen_utt2speed.py
# Time      :   2022/06/28 18:42:02
# Author    :   Jinghan Peng
# Desciption:   对于dev集生产utt2speed，根据标签语速speed、normal、faster

import os, sys
from tqdm import tqdm

def main():
    in_path = "/data2/pengjinghan/FFSVC_data/Dev_Test_FFSVC2022/dev_meta_list"
    out_path = "/data2/pengjinghan/FFSVC_data/Dev_Test_FFSVC2022/dev/data_list/utt2speed"
    
    with open(in_path, 'r') as rf, open(out_path, 'w') as wf:
        for line in tqdm(rf.readlines()[1:]):
            # T0344_344I1M_1_0307_normal ffsvc22_dev_000000
            Original_Name, FFSVC2022_Name = line.strip().split()
            spk = Original_Name.split('_')[0][1:]
            speed = Original_Name.split('_')[-1]
        
            wf.write(f"{spk}-{FFSVC2022_Name}.wav {speed}\n")


if __name__ == '__main__':
    main()

