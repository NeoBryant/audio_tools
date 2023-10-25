#coding=utf-8
# File      :   cut_chunk_wav.py
# Time      :   2021/09/10 11:31:41
# Author    :   Jinghan Peng
# Desciption:   对音频进行切割chunk，对target也进行切割划分


import os, sys
from posixpath import split
from re import L
import wave
from pydub import AudioSegment
from pydub.utils import make_chunks
from tqdm import tqdm

import kaldiio
from kaldiio import WriteHelper

import numpy as np

from multiprocessing import Pool
import collections
# from collections import Counter

def main():
    wav_dir = "/data/pengjinghan/tsvad/1c8k_ol/wav_replace_silence"
    #"/data/pengjinghan/tsvad_finetune_train_data/20220125_x4_testdataset/wav" 
    #"/data4/pengjinghan/tsvad/1c8k/wav_replace_silence" # 输入音频目录路径
    targetlst_path = "/data/pengjinghan/tsvad/1c8k_ol/target.scp"
    #"/data/pengjinghan/tsvad_finetune_train_data/20220125_x4_testdataset/data/target.scp" 
    #"/data4/pengjinghan/tsvad/1c8k/target_with_vad.scp" # 输入target文件路径
    
    out_dir = "/data/pengjinghan/tsvad/1c8k_ol/wav_chunk"
    #"/data/pengjinghan/tsvad_finetune_train_data/20220125_x4_testdataset/wav_chunk" 
    #"/data4/pengjinghan/tsvad/1c8k/wav_replace_silence_chunk" # 输出音频目录路径
    out_targetlst_path = "/data/pengjinghan/tsvad/1c8k_ol/target_chunk"
    #"/data/pengjinghan/tsvad_finetune_train_data/20220125_x4_testdataset/data/target_chunk" 
    #"/data4/pengjinghan/tsvad/1c8k/target_chunk" # 输出target文件路径(无后缀)
    
    
    # out_targetlst_path = "/data4/pengjinghan/tsvad/1c8k/target_chunk.lst"
    # out_targetlst_split_dir = "/data4/pengjinghan/tsvad/1c8k/target_split_chunk"
    
    os.makedirs(out_dir, exist_ok=True)
    # os.makedirs(out_targetlst_split_dir, exist_ok=True)
    
    wav_length = 16.02 # 单位: 秒，=16020秒
    chunk_length_ms    = int(wav_length*1000)
    chunk_length_frame = int(wav_length*100)
    
    
    """读取targetlst_path"""
    utt2target_path = collections.defaultdict(dict) # utt->{spk1:target1,spk2:target2} 毫秒级标签
    with open(targetlst_path, 'r') as rf:
        # for line in tqdm(rf.readlines()):
        for line in tqdm(rf):
            spk, target_path = line.strip().split()
            utt = spk[:spk.rfind('_')]
            
            utt2target_path[utt][spk] = target_path

            
    """对音频进行切割chunk"""
    scp_save = f"ark,scp:{out_targetlst_path}.ark,{out_targetlst_path}.scp"
    # with open(out_targetlst_path, 'w') as wf:
    with WriteHelper(scp_save) as writer:
        files = os.listdir(wav_dir)
        files.sort()
        
        for file in tqdm(files):
            wav_path = os.path.join(wav_dir, file)
            utt = file.split(".wav")[0]
            
            audio  = AudioSegment.from_file(wav_path)    # 输入音频
            duration = audio.duration_seconds
            chunks = make_chunks(audio, chunk_length_ms) # 切片
            
        
            
            """读取标签"""
            spk2target = dict() # spk->target
            for spk, target_path in utt2target_path[utt].items():
                target = kaldiio.load_mat(target_path)
                target = target.flatten().tolist() # np.array->list
                spk2target[spk] = target

            
            """"对每个chunk"""
            for index, chunk in enumerate(chunks):
                if index == len(chunks)-1: # 最后一个块可能长度不够，直接丢掉
                    continue
                
                """保存音频"""
                chunk_name = utt+"-{0:08d}_{1:08d}.wav".format(index*chunk_length_ms, (index+1)*chunk_length_ms)
                chunk_path = os.path.join(out_dir, chunk_name)
                chunk.export(chunk_path, format="wav") # 保存剪切后的样本音频
                # print("Exporting", chunk_path)
                
                """保存target"""
                for spk, target in spk2target.items():
                    # target = kaldiio.load_mat(target_path)
                    # target = target.flatten().tolist() # np.array->list
                    
                    sub_spk = spk+"-{0:08d}_{1:08d}".format(index*chunk_length_ms, (index+1)*chunk_length_ms)
                    sub_target_frame = target[index*chunk_length_frame: (index+1)*chunk_length_frame-2] # 帧级（10ms）的标签
                    
                    sub_target_frame = np.array([sub_target_frame]) # 帧级（10ms）的标签
                    
                    # print(sub_target_frame.shape)
                    # for i in range(chunk_length_frame-2):
                    #     # 若该帧有5ms以上的标签都是1,则该帧为1
                    #     if sum(sub_target_ms[i*10:(i+1)*10]) > 5:
                    #         sub_target_frame[0][i] = 1
                    
                    writer(sub_spk, sub_target_frame)
                    # return
                    
if __name__ == "__main__":
    main()