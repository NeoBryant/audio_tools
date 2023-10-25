#coding=utf-8
# File      :   find_2channel_8kHz_wav.py
# Time      :   2021/09/01 16:04:08
# Author    :   Jinghan Peng
# Desciption:   统计音频时长

import os
import wave
from tqdm import tqdm

def main():
    in_dir = "/data/pengjinghan/origin_data/mandarin/1c_8kHz_audio/wav_replaced_with_silence"
    number_target_wav = 0
    sum_time = 0
    for fn in os.listdir(in_dir):
        if fn.endswith(".wav"):
            file_path = os.path.join(in_dir, fn)
            try:
                with wave.open(file_path) as wf:
                    frames     = wf.getnframes()  # 帧总数
                    sampleRate = wf.getframerate()  # 采样频率
                    channels   = wf.getnchannels()
                    time     = frames / sampleRate  # 声音信号的长度
                    print(time)    
                    sum_time += time          
            except:
                continue
    
    print("sum", sum_time)
    # print(number_target_wav)


if __name__ == '__main__':
    main()
    