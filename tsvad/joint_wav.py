#coding=utf-8
# File      :   joint_wav.py
# Time      :   2021/12/15 14:16:37
# Author    :   Jinghan Peng
# Desciption:   将多条拼接音频为一条音频


import os, sys
from tqdm import tqdm
from pydub import AudioSegment

def main():
    
    # in_dir = "/data1/pengjinghan/tsvad/invalid_sound/0702_bobao/split"
    # in_paths = list()
    # for in_path in os.listdir(in_dir):
    #     in_paths.append(os.path.join(in_dir, in_path))
    in_paths = ["/data1/pengjinghan/tsvad/invalid_sound/office_noise/145147_08002_in_0707.wav",
                "/data1/pengjinghan/tsvad/invalid_sound/office_noise/13795270616_20210901180212.wav",
                "/data1/pengjinghan/tsvad/invalid_sound/office_noise/15316523052_20210817102340.wav",
                "/data1/pengjinghan/tsvad/invalid_sound/office_noise/17606758543_20210830100326.wav",
                "/data1/pengjinghan/tsvad/invalid_sound/office_noise/n_office_0715_1_8k.wav",
                "/data1/pengjinghan/tsvad/invalid_sound/office_noise/n_office_0715_2_8k.wav",
                "/data1/pengjinghan/tsvad/invalid_sound/office_noise/n_office_0715_3_8k.wav",
                "/data1/pengjinghan/tsvad/invalid_sound/office_noise/n_office_0715_4_8k.wav",
                "/data1/pengjinghan/tsvad/invalid_sound/youxiaoyin-0226/noise-00001.wav"]
        
    out_path = "/data1/pengjinghan/tsvad/invalid_sound/sum/noise.wav"

    out_audio = AudioSegment.empty()
    for in_path in tqdm(in_paths):
        audio = AudioSegment.from_file(in_path)
        out_audio += audio
    
    out_audio.export(out_path, format='wav')


if __name__ == '__main__':
    main()
    