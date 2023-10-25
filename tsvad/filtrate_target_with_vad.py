#coding=utf-8
# File      :   diar_plot.py
# Time      :   2022/01/14 10:31:14
# Author    :   Jinghan Peng
# Desciption:   根据vad结果更新asr标签所得target


import os, sys
from tqdm import tqdm
import collections
import kaldiio
from kaldiio import WriteHelper
import numpy as np

def main():
    target_path = "/data4/pengjinghan/tsvad/1c8k/target.scp"
    vad_path    = "/data4/pengjinghan/tsvad/1c8k/vad_project/data/vad.scp"
    out_path    = "/data4/pengjinghan/tsvad/1c8k/target_with_vad"
    
    
    # vad
    utt2vad_path = dict()
    with open(vad_path, 'r') as rf:
        for line in tqdm(rf.readlines()):    
            utt, path = line.strip().split()
            utt2vad_path[utt] = path
            
            
    # target
    scp_save = f"ark,scp:{out_path}.ark,{out_path}.scp"
    
    utt2target_path = collections.defaultdict(dict)
    with open(target_path, 'r') as rf, WriteHelper(scp_save) as writer:
        for line in tqdm(rf.readlines()):
            spk, target_path = line.strip().split()
            utt = spk[:spk.rfind('_')]
            target = kaldiio.load_mat(target_path) # target序列
            new_target = np.copy(target)
            
            
            vad_path = utt2vad_path[utt]
            vad = kaldiio.load_mat(vad_path) # vad序列，比target序列少2个元素（帧）
                        
            num_frames = vad.shape[-1] # vad帧数
            for i in range(num_frames):
                if vad[i] == 0:
                    new_target[0][i] = 0
            
            writer(spk, new_target)


if __name__ == "__main__":
    main()