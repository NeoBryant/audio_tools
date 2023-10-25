#coding=utf-8
# File      :   compute_wavs_sum_size.py
# Time      :   2021/12/07 10:14:25
# Author    :   Jinghan Peng
# Desciption:   计算wav.scp里所有音频的总大小

import os, sys
from tqdm import tqdm

def convert_size(raw_size):
    # units_name = ["B", "KB", "MB", "GB", "TB"]
    # units = [0 for i in range(len(units_name))]
    # unit = 0
    
    # while raw_size > 0:
    #     units[unit] = raw_size%1024
    #     raw_size = raw_size//1024
    #     # print(units[unit], units_name[unit], raw_size)
    #     unit += 1
    
    # size_str = ""
    # for i in range(1,len(units_name)+1):
    #     if units[-i] != 0:
    #         size_str = size_str + str(units[-i]) + units_name[-i] + " "

    GB = raw_size / (1024**3)
    size_str = "{:.2f} GB".format(GB)
    
    return size_str

def main():
    in_path = "/data1/pengjinghan/language_data/GuangDongHua-wav.scp"
    size = 0
    
    print("input:", in_path)
    with open(in_path, 'r') as rf:
        for line in tqdm(rf.readlines()):
            _, wav_path = line.strip().split()
            file_size = os.path.getsize(wav_path) # 以字节为单位
            size += file_size
    
    print(size, "B")
    h_size = convert_size(size)
    print(h_size)
    
if __name__ == '__main__':
    main()
    