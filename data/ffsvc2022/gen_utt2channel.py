#coding=utf-8
# File      :   gen_utt2channel.py
# Time      :   2022/06/06 15:59:22
# Author    :   Jinghan Peng
# Desciption:   生成utt2channel文件，dev可以根据dev_meta_list判断，eval只能通过音频采样率判断，只有iphone(48kHz)和ipad(16kHz)两种

import os, sys
from tqdm import tqdm


def main():
    in_path  = "/data2/pengjinghan/FFSVC_data/Dev_Test_FFSVC2022/dev_meta_list"
    out_path = "/data2/pengjinghan/FFSVC_data/Dev_Test_FFSVC2022/dev/data_list/utt2channel"
    
    with open(in_path, 'r') as rf, open(out_path, 'w') as wf:
        for line in tqdm(rf.readlines()[1:]):
            # T0344_344I1M_1_0307_normal ffsvc22_dev_000000
            Original_Name, FFSVC2022_Name = line.strip().split()
            spk = Original_Name.split('_')[0][1:]
            device_positin = Original_Name.split('_')[1][3:]
            
            if "I" in device_positin:
                device = "I"
            elif "PAD" in device_positin:
                device = "PAD"
            
            wf.write(f"{spk}-{FFSVC2022_Name}.wav {device}\n")


if __name__ == '__main__':
    main()

