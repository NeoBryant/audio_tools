#coding=utf-8
# File      :   cut_wav.py
# Time      :   2021/12/15 14:39:17
# Author    :   Jinghan Peng
# Desciption:   切割无效音频为小的chunk

import os, sys
from re import L
import wave
from pydub import AudioSegment
from pydub.utils import make_chunks
from tqdm import tqdm

from multiprocessing import Pool
import collections

def main():
    wav_dir = "/data1/pengjinghan/tsvad/invalid_sound/sum"
    
    out_wav_dir  = "/data1/pengjinghan/tsvad/invalid_sound/wav_chunk/wav"
    out_data_dir = "/data1/pengjinghan/tsvad/invalid_sound/wav_chunk/data"
    os.makedirs(out_wav_dir, exist_ok=True)
    os.makedirs(out_data_dir, exist_ok=True)
    
    wav_length = 16.02 # 单位: 秒，=16020秒
    chunk_length_ms    = int(wav_length*1000)
    chunk_length_frame = int(wav_length*100)
    
    
    """对音频进行切割chunk"""
    with open(os.path.join(out_data_dir, 'target_chunk.lst'), 'w') as wf:
        for file in os.listdir(wav_dir):
            wav_path = os.path.join(wav_dir, file) # 输入音频路径
            utt      = file.split(".wav")[0]
            audio    = AudioSegment.from_file(wav_path)    # 输入音频
            duration = audio.duration_seconds
            print(f"Processing {file}")
            print(f"{duration}s audio is going to be cut to {int(duration//wav_length)} chunk with chunk_size={wav_length}s")
            chunks   = make_chunks(audio, chunk_length_ms) # 切片
            
            """"对每个chunk"""
            for index, chunk in tqdm(enumerate(chunks)):
                if chunk.duration_seconds != wav_length: # 最后一个块可能长度不够而丢弃
                    continue
                
                """保存chunk音频"""
                chunk_name = utt+"-{0:08d}_{1:08d}.wav".format(index*chunk_length_ms, (index+1)*chunk_length_ms)
                chunk_path = os.path.join(out_wav_dir, chunk_name)
                chunk.export(chunk_path, format="wav") # 保存剪切后的样本音频
                print("Exporting", chunk_path)

                """记录chunk的target"""
                chunk_utt = chunk_name.split('.wav')[0]
                target_chunk_length_frame = chunk_length_frame - 2 # 特征要比音频时长小2秒
                target_line = ' '.join(['0' for i in range(target_chunk_length_frame)])
                
                wf.write(f"{chunk_utt} {target_line}\n")

if __name__ == "__main__":
    main()