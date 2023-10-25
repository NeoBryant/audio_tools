#coding=utf-8
# File      :   multichannel_to_singlechannel.py
# Time      :   2022/06/17 18:23:38
# Author    :   Jinghan Peng
# Desciption:   多声道转单声道

import os, sys
from scipy.io import wavfile
import numpy as np
from pydub import AudioSegment
from tqdm import tqdm
from multiprocessing import Pool
from argparse import ArgumentParser

import wave


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--arg", type=str, help="", 
                        default="")

    args = parser.parse_args()
    return args

def split_stereo(input_path, out_wav_path, output_dir, utt):
    # default stereo
    samplerate, data = wavfile.read(input_path)
    if data.shape[-1] == 2:
        left = []
        right = []
        # print(data.shape)
        for item in data:
            left.append(item[0])
            right.append(item[1])
                 
        wavfile.write(os.path.join(output_dir, f"{utt}-1.wav"), samplerate, np.array(left))
        wavfile.write(os.path.join(output_dir, f"{utt}-2.wav"), samplerate, np.array(right))
        os.remove(out_wav_path)
    
        
    

def work(sublines, process_id, out_dir):
    process_tqdm = tqdm(sublines)
    process_tqdm.set_description(f"Process {process_id}")
    for file_path in process_tqdm:
        utt = file_path.split('/')[-1].split('.')[0]
        
        # audio = AudioSegment.from_file(file_path, format='wav')
        # channel_num = audio.channels
        # channel_num = wave.open(file_path).getnchannels()
        # print(channel_num, file_path)
        # return 
        out_wav_path = os.path.join(out_dir, f"{utt}.wav")
        # cmd = f"ffmpeg -loglevel quiet -i {file_path} -ac 2 {out_wav_path}"
        cmd = f"ffmpeg -loglevel quiet -i {file_path} {out_wav_path}"
        os.system(cmd)
        
        split_stereo(out_wav_path, out_wav_path, out_dir, utt)
        # os.remove(out_wav_path)
    
        
        

def try_work(sublines, process_id, out_dir):
    try:
        work(sublines, process_id, out_dir)
    except Exception as e:
        print(e)
        raise e




def main():
    
    args = parse_args()
    in_dir  = "/home/zhaomiao/data/NIST-SRE-04-10/SRE05/r101_1_1/train/data"
    out_dir = "/data1/pengjinghan/NIST-SRE-04-10-data"
    os.makedirs(out_dir, exist_ok=True)
    
    """输入"""
    threads = 32 #32 # 进程数
    lines = []

    for file in tqdm(os.listdir(in_dir)):
        file_path = os.path.join(in_dir, file)
        lines.append(file_path)
            
    """多进程计算"""
    step = len(lines)//threads + 1
    pool = Pool(threads)
    for i in range(threads):
        sublines = lines[step*i:step*(i+1)]
        pool.apply_async(try_work, (sublines, i, out_dir))
    pool.close()
    pool.join()
    
    
if __name__ == '__main__':
    main()

