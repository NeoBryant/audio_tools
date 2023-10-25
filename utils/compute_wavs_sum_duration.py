#coding=utf-8
# File      :   compute_wavs_sum_size.py
# Time      :   2021/12/07 10:14:25
# Author    :   Jinghan Peng
# Desciption:   计算wav.scp里所有音频的总时长

import os, sys
from tqdm import tqdm
from pydub import AudioSegment

def convert_time(raw):

    # seconds = raw%60
    # minutes = (raw//60)%60
    hour = raw/3600
    
    size_str = "{:.2f} hours".format(hour)

    return size_str

def main():
    in_path = "/data1/pengjinghan/language_data/English-wav.scp"
    time = 0
    
    print("input:", in_path)
    with open(in_path, 'r') as rf:
        for line in tqdm(rf.readlines()):
            _, wav_path = line.strip().split()
            try: 
                audio = AudioSegment.from_file(wav_path, format='wav')
                wav_dur = audio.duration_seconds # 以秒为单位
                
                time += wav_dur
            except:
                print(f"[ERROR] Can not get the wav ({wav_path})'s duration!")
            
    
    print(time, " s")
    h_time = convert_time(time)
    print(h_time)
    
if __name__ == '__main__':
    main()
    