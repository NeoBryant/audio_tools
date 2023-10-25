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
    rir_dir = ["/data3/pengjinghan/RIRS_NOISES/simulated_rirs/mediumroom", "/data3/pengjinghan/RIRS_NOISES/simulated_rirs/smallroom"]
    rir_path = "/data3/pengjinghan/RIRS_NOISES/pointsource_noises/noise-free-sound-0842.wav"
    #"/data3/pengjinghan/RIRS_NOISES/real_rirs_isotropic_noises/RWCP_type4_rir_p70r.wav"
    #"/data3/pengjinghan/RIRS_NOISES/pointsource_noises/noise-free-sound-0842.wav"
    out_dir = "/data2/pengjinghan/test_wav"
    
    wav_list = read_all_wav_files(rir_dir)
    
    
    speech, sample_rate = torchaudio.backend.sox_io_backend.load(in_path,
        frame_offset=0 , 
        num_frames=-1, 
        normalize=True, 
        channels_first=True)
    print(speech.shape)
    random.seed(777)
    for i in range(10):
        # out_path = os.path.join(out_dir, f"rir_{i}.wav")
        out_path = os.path.join(out_dir, f"rir_scipy_{i}.wav")
        rir_path = random.choice(wav_list)
        print(rir_path)
        rir_raw, rir_sr = torchaudio.backend.sox_io_backend.load(rir_path,
            frame_offset=0 , 
            num_frames=-1, 
            normalize=True, 
            channels_first=True)
        if rir_sr != sample_rate: # 重采样
            rir_raw = torchaudio.transforms.Resample(orig_freq=rir_sr, 
                                                        new_freq=sample_rate)(rir_raw)
        print(rir_raw.shape)
        
        use_torchaudio = False #True
        
        if use_torchaudio:
            rir = rir_raw
            # rir = rir_raw[:, int(sample_rate * 1.01) : int(sample_rate * 1.3)]
            rir = rir / torch.norm(rir, p=2)
            RIR = torch.flip(rir, [1])
            print("RIR ", RIR.shape)
            print("speech", speech.shape)
            speech_ = torch.nn.functional.pad(speech, (RIR.shape[1] - 1, 0))
            print("speech_", speech_.shape)
            augmented = torch.nn.functional.conv1d(speech_.unsqueeze(0), RIR.unsqueeze(0), dilation=1)[0]
            
            print("augmented ", augmented.shape)
            save_wav(augmented, out_path, sample_rate)
        else:            
            rir = rir_raw / torch.norm(rir_raw, p=2)
            # RIR = torch.flip(rir, [1])
            print(rir.shape)
            signal_rir = scisignal.convolve(speech, rir, mode='same')
            signal_rir = torch.from_numpy(signal_rir)
            print(signal_rir.shape)
            
            save_wav(signal_rir, out_path, sample_rate)
    
    
    
if __name__ == '__main__':
    main()

