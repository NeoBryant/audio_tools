#coding=utf-8
# File      :   biaozhu2rttm.py
# Time      :   2022/06/09 15:08:55
# Author    :   Jinghan Peng
# Desciption:   

import os, sys
from decimal import Decimal

def time2sec(time):
    """将时分秒字符串转化为秒数
    """
    hour, minute, second = time.split(":")
    hour, minute, second = Decimal(hour), Decimal(minute), Decimal(second)
    second += minute * 60 + hour * 3600
    # minute, second = time.split(":")
    # minute, second = Decimal(minute), Decimal(second)
    # second += minute * 60

    return second

def main():
    in_dir = "/data1/pengjinghan/tsvad_test_data/5vocal/data/biaozhu/"
    rttm_path = "/data1/pengjinghan/tsvad_test_data/5vocal/data/rttm"
    
    with open(rttm_path, 'w') as wf:
        for file_name in os.listdir(in_dir):
            file_path = os.path.join(in_dir, file_name)
            utt = file_name.split('.')[0]
            with open(file_path, 'r') as rf:
                for line in rf.readlines():
                    # F1 00:00:00.027 00:00:00.989  
                    spk, beg_t, end_t = line.strip().split()
                    beg_s, end_s = time2sec(beg_t), time2sec(end_t)
                    
                    # SPEAKER 18_03 0 0.644 1.128 <NA> <NA> M1 <NA> <NA>
                    wf.write(f"SPEAKER {utt} 0 {beg_s} {end_s-beg_s} <NA> <NA> {spk} <NA> <NA>\n")
                    
                    
                
if __name__ == '__main__':
    main()

