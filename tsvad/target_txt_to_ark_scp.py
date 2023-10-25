#coding=utf-8
# File      :   target_txt_to_ark_scp.py
# Time      :   2021/09/14 14:16:03
# Author    :   Jinghan Peng
# Desciption:   target的txt文本文件转化为kaldi的ark、scp文件进行存储

import os
import kaldiio
import kaldi_io
import numpy as np
from tqdm import tqdm
import collections


def main():
    targetlst_path = "/data1/pengjinghan/tsvad/invalid_sound/wav_chunk/data/target_chunk.lst"
    out_dir        = "/data1/pengjinghan/tsvad/invalid_sound/wav_chunk/data"
    
    target_ark_scp = f'ark:| copy-feats --compress=true ark:- ark,scp:{out_dir}/target.ark,{out_dir}/target.scp'
    with open(targetlst_path, 'r') as rf, kaldi_io.open_or_fd(target_ark_scp, 'w') as wf:
        for line in tqdm(rf.readlines()):
            """读取target.lst"""
            line = line.strip().split()
            utt = line[0]
            target = [int(i) for i in line[1:]]
            target = np.array(target, dtype='float32')
            target = np.expand_dims(target, 0)
            
            # -----
            kaldi_io.write_mat(wf, target, key=utt)
            

if __name__ == '__main__':
    main()
    