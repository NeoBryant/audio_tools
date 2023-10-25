#coding=utf-8
# File      :   change_wav_speed.py
# Time      :   2022/06/06 10:43:33
# Author    :   Jinghan Peng
# Desciption:   对音频进行变速不变调处理，基于audiotsm，然后拼接音频

import os, sys
import shutil
from tqdm import tqdm
import random
from multiprocessing import Pool


import audiotsm
import audiotsm.io.wav
import audiotsm.io.array

from pydub import AudioSegment
from argparse import ArgumentParser

"""
pip install audiotsm
"""

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--arg", type=str, help="", 
                        default="")

    args = parser.parse_args()
    return args

def work(sublines, process_id, out_dir, speed_list=[]):
    process_tqdm = tqdm(sublines)
    process_tqdm.set_description(f"Process {process_id}")
    for utt, wav_path in process_tqdm:
        # print(utt, wav_path)
        concat_audio = AudioSegment.from_file(wav_path, format='wav') # 原音频
        for speed in speed_list:
            out_path = os.path.join(out_dir, f"{utt}-sp{speed}.wav")
            
            # 定义reader & writer
            with audiotsm.io.wav.WavReader(wav_path) as reader:
                samplerate = reader.samplerate # 采样率
                writer =  audiotsm.io.wav.WavWriter(out_path, 1, samplerate)
                
                # 定义WSLOA算法，并运行
                # WSOLA(Waveform similarity-based Overlap-Add)
                wsola = audiotsm.wsola(channels=1, speed=speed)
                wsola.run(reader, writer)

            audio = AudioSegment.from_file(out_path, format='wav')
            concat_audio += audio
            os.remove(out_path)
        
        out_path = os.path.join(out_dir, f"{utt}.wav")
        concat_audio.export(out_path, format = 'wav')

        
def try_work(sublines, process_id, out_dir, speed_list):
    try:
        work(sublines, process_id, out_dir, speed_list)
    except Exception as e:
        print(e)
        raise e

def main():
    args = parse_args()
    """输入"""
    threads = 10 # 进程数
    lines = []
    
    in_dir = "/data2/pengjinghan/FFSVC_data/Dev_Test_FFSVC2022/dev/data_list/enroll/wav.scp"
    out_dir = "/data3/pengjinghan/Dev_Test_FFSVC2022/dev/wav_sp_concat/enroll"
    os.makedirs(out_dir, exist_ok=True)
    
    utt2file_path = dict()
    if os.path.isdir(in_dir):
        for wav_file in os.listdir(in_dir):
            file_path = os.path.join(in_dir, wav_file)
            utt = wav_file.split('.wav')[0]
            utt2file_path[utt] = file_path
    elif os.path.isfile(in_dir):
        with open(in_dir, 'r') as rf:
            for line in rf.readlines():
                utt, file_path = line.strip().split()
                utt = utt.split('-')[-1].split('.wav')[0]
                utt2file_path[utt] = file_path
    
    lines = list(utt2file_path.items())
    
    # speed_list = [random.choice([0.7,0.8,0.9]), random.choice([1.1,1.2,1.3,1.4])]
    speed_list = [0.95, 1.05]
            
    """多进程计算"""
    step = len(lines)//threads + 1
    pool = Pool(threads)
    for i in range(threads):
        sublines = lines[step*i:step*(i+1)]
        pool.apply_async(try_work, (sublines, i, out_dir, speed_list))
    pool.close()
    pool.join()

if __name__ == '__main__':
    main()

