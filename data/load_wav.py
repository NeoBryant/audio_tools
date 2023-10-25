#coding=utf-8
# File      :   test.py
# Time      :   2022/07/18 11:50:55
# Author    :   Jinghan Peng
# Desciption:   

import os, sys
import numpy as np

from scipy.io import wavfile

import soundfile as sf
from pydub import AudioSegment

import librosa

import torchaudio
import time

def main():
    in_path = "/data2/pengjinghan/test_wav/60m.wav"
    
    out_path = "/data2/pengjinghan/test_wav/60m.wav"
    
    # cmd = f"ffmpeg -i {in_path} -ar 8000 {out_path}"
    # os.system(cmd)
    
    # fs, audio = wavfile.read(out_path)
    # print(f"scipy read: {audio.shape}, {type(audio)}")
    
    # audio = AudioSegment.from_file(out_path, format='wav')
    # print(f"pydub read: {type(audio)}")
    
    beg_time = time.time()
    audio, fs = sf.read(out_path, start=160000, frames=32320)
    end_time = time.time()
    print(f"soundfile read: {audio.shape}, {type(audio)}, {end_time-beg_time} s")
    print(audio)
    
    beg_time = time.time()
    audio, sr = torchaudio.backend.sox_io_backend.load(out_path,
            frame_offset=160000, 
            num_frames=32320, 
            normalize=False, 
            channels_first=True)
    end_time = time.time()
    print(f"torchaudio read: {audio.shape}, {type(audio)}, {end_time-beg_time} s")
    print(audio)
    
    beg_time = time.time()
    audio, fs = librosa.load(out_path, sr=16000, offset=10, duration=2.02)
    end_time = time.time()
    print(f"librosa read: {audio.shape}, {type(audio)}, {end_time-beg_time} s")
    print(audio)

    # audio, fs = torchaudio.load(out_path)
    # print(f"torchaudio read: {audio.shape}, {type(audio)}")
    
    # 
    # audio, fs = torchaudio.load(in_path)
    # print(audio.shape, audio)

if __name__ == '__main__':
    main()

