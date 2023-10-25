#coding=utf-8
# File      :   gen_utt2channel_from_sr.py
# Time      :   2022/06/17 10:11:47
# Author    :   Jinghan Peng
# Desciption:   根据音频采样率判断音频信道，16k为ipad，48k为iphone

import os, sys
from pydub import AudioSegmentfrom 
from tqdm import tqdm

def main():
    in_dir = ""
    out_path = ""
    
    for file in tqdm(os.listdir(in_dir)):
        file_path = os.path.join(in_dir, file)
        audio = AudioSegment.from_file(file_path, format='wav')
        sr = audio.sample_rate
        print(file, sr)
        return

if __name__ == '__main__':
    main()
