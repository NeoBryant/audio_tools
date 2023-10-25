#coding=utf-8
# File      :   test_torchaudio_aug.py
# Time      :   2022/08/10 11:11:28
# Author    :   Jinghan Peng
# Desciption:   测试torchaudio的数据增强的效果

import os, sys
import sox
import torchaudio
import time
import torch
from scipy import signal as scisignal
import random
import math

def save_wav(waveform, filepath, sample_rate):
    """保存音频
    compression: Used for formats other than WAV. 
    format: ("wav", "mp3", "ogg", "vorbis", "amr-nb", "amb", "flac", "sph", "gsm", and "htk")
    """
    # waveform需要时normalize的音频
    torchaudio.backend.sox_io_backend.save(filepath=filepath, 
        src=waveform, 
        sample_rate=sample_rate, 
        channels_first=True, 
        format="wav")
    print("save successfully!")
    
# read noise wavs list        
def read_all_wav_files(wav_dir_list):
    wav_list = list()
    for wav_dir in wav_dir_list:
        for root, _, files in os.walk(wav_dir):
            for file_name in files:
                if file_name.endswith(".wav"): 
                    wav_list.append(os.path.join(root, file_name))
    return wav_list
            

def main():
    in_path = "/data2/pengjinghan/test_wav/AfQGUOMKCAQ.wav"
    noise_dir = ["/data3/pengjinghan/musan/music"]
    out_dir = "/data2/pengjinghan/test_wav"
    
    wav_list = read_all_wav_files(noise_dir)
    
    
    speech, sample_rate = torchaudio.backend.sox_io_backend.load(in_path,
        frame_offset=0 , 
        num_frames=-1, 
        normalize=True, 
        channels_first=True)
    print(speech.shape)
    
    random.seed(777)
    for i in range(10):
        # out_path = os.path.join(out_dir, f"rir_{i}.wav")
        out_path = os.path.join(out_dir, f"music_{i}.wav")
        rir_path = random.choice(wav_list)
        print(rir_path)
        noise_signal, noise_sr = torchaudio.backend.sox_io_backend.load(rir_path,
            frame_offset=0 , 
            num_frames=-1, 
            normalize=True, 
            channels_first=True)
        if noise_sr != sample_rate: # 重采样
            noise_signal = torchaudio.transforms.Resample(orig_freq=noise_sr, 
                                                        new_freq=sample_rate)(noise_signal)
        print(noise_signal.shape)
        noise_signal = noise_signal[:, :speech.shape[1]]
        snr_dur=[0,20]
         
        speech_power = speech.norm(p=2)
        noise_power  = noise_signal.norm(p=2)
        
        snr_db = snr_dur[0]+(snr_dur[1]-snr_dur[0])*random.random()

        snr = 10 ** (snr_db / 20) #math.exp(snr_db / 10)
        # snr = math.exp(snr_db / 10)
        scale = snr * noise_power / speech_power
        noisy_speech = (scale * speech + noise_signal) / 2
        
        
        save_wav(noisy_speech, out_path, sample_rate)
    
    
    
if __name__ == '__main__':
    main()

