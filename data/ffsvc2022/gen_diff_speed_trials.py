#coding=utf-8
# File      :   compute_cos_from_diff_speed.py
# Time      :   2022/06/28 17:48:58
# Author    :   Jinghan Peng
# Desciption:   注册音频做变速，然后取分数最大值/平均值作为最终分数

import collections
import os, sys

def main():
    trials_path = "/data2/pengjinghan/FFSVC_data/Dev_Test_FFSVC2022/dev/data_list/trials"
    out_path = "/data2/pengjinghan/FFSVC_data/Dev_Test_FFSVC2022/dev/data_list_sp/trials"
    
    postfix_list = ["normal", "fast", "faster", "slow", "slower"]
    
    
    with open(trials_path, 'r') as rf, open(out_path, 'w') as wf:
        for line in rf.readlines():
            enroll_utt, test_utt, isTarget = line.strip().split()
            
            for postfix in postfix_list:
                sub_enroll_utt = enroll_utt.split(".wav")[0]+f"-{postfix}.wav"
                wf.write(f"{sub_enroll_utt} {test_utt} {isTarget}\n")
    

if __name__ == '__main__':
    main()

