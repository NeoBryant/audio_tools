#coding=utf-8
# File      :   online_dataset.py
# Time      :   2022/07/15 14:18:39
# Author    :   Jinghan Peng
# Desciption:   测试torchaudio提取的fbank与kaldi的fbank的区别

import os, sys
import torch, torchaudio
import numpy as np
import random

import kaldiio
from tqdm import tqdm

# load wav
from scipy.io import wavfile
import soundfile as sf
import librosa

def _get_sample(path, resample=None):
    effects = [
        ["remix", "1"]
    ]
    if resample:
        effects.extend([
            ["lowpass", f"{resample // 2}"],
            ["rate", f'{resample}'],
        ])
    return torchaudio.sox_effects.apply_effects_file(path, effects=effects)

def load_wav(path, max_frames=200, fs=16000,train_mode=False):
    signal,fs = _get_sample(path,resample=fs)
    signalsize = signal.shape[1]
    if train_mode:
        max_audio = max_frames * 160-160
        if signalsize <= max_audio:
            signal = signal[0]
            signal = signal.repeat(max_audio//signalsize+1)[:max_audio]
        else:
            startframe = np.array([np.int64(random.random()*(signalsize-max_audio))])[0]
            signal = signal[0,startframe:startframe+max_audio]
        return signal
    else:
        return signal[0]


def load_wav_np(wav_path, method="wavfile", sr=16000):
    assert method in ("wavfile", "soundfile", "librosa", "torchaudio")
    
    if method == "wavfile":
        fs, audio = wavfile.read(wav_path)
        audio = torch.from_numpy(audio).float()
    elif method == "soundfile":
        audio, fs = sf.read(wav_path)
        audio = torch.from_numpy(audio)
    elif method == "librosa":
        audio, fs = librosa.load(wav_path, sr=sr)
        audio = torch.from_numpy(audio)
    elif method == "torchaudio":
        audio, fs = torchaudio.load(wav_path, frame_offset=0 , num_frames=-1, normalize=False, channels_first=True)
        audio = audio.float()
    
    if len(audio.shape) == 1:
        audio.unsqueeze_(0)    
    
    return audio, fs

def get_torchaudio_fbank(wav_path):
    waveform = load_wav(wav_path, max_frames=200, fs=16000, train_mode=False)
    waveform.unsqueeze_(0)
    sr = 16000
    print(waveform.shape, waveform)
    
    # waveform, sr = load_wav_np(wav_path, method="torchaudio")
    # if sr != 16000: # 重采样
    #     waveform = torchaudio.transforms.Resample(orig_freq=sr, new_freq=16000)(waveform)
    # print(waveform.shape, waveform)
    
    # fbank = torchaudio.compliance.kaldi.fbank(waveform=waveform,
    #     blackman_coeff= 0.42, 
    #     channel= - 1, 
    #     dither = 0.0, 
    #     energy_floor = 1.0, 
    #     frame_length = 25.0, 
    #     frame_shift = 10.0, 
    #     low_freq = 20.0,
    #     high_freq = 7600.0, 
    #     htk_compat = False, 
    #     min_duration = 0.0, 
    #     num_mel_bins = 80, 
    #     preemphasis_coefficient = 0.97, 
    #     remove_dc_offset = True, 
    #     round_to_power_of_two = True, 
    #     sample_frequency = 16000.0, 
    #     snip_edges = True, 
    #     subtract_mean = False, 
    #     use_energy = True, 
    #     raw_energy = True, 
    #     use_log_fbank = True, 
    #     use_power = True, 
    #     vtln_high = -500.0, 
    #     vtln_low = 100.0, 
    #     vtln_warp = 1.0, 
    #     window_type = 'hamming')
    
    fbank = torchaudio.compliance.kaldi.fbank(waveform=waveform,
        sample_frequency = 16000.0, 
        frame_length = 25.0, 
        frame_shift = 10.0, 
        low_freq = 20.0,
        high_freq = 7600.0,
        num_mel_bins = 80, 
        snip_edges = True, 
        window_type = 'hamming',
        dither = 0.0, 
        use_energy = True,         
    )
    
    return fbank, sr


def main():
    wavscp_path = "/data2/pengjinghan/FFSVC_test/project/20220618-repvgg_a2-stats_std-sc-vox/test/data/wav.scp"
    kaldi_fbank_path = "/data2/pengjinghan/FFSVC_test/project/20220618-repvgg_a2-stats_std-sc-vox/test/data/feats.scp"
    
    utt2wav_path = dict()
    with open(wavscp_path, 'r') as rf:
        for line in tqdm(rf.readlines()):
            utt, wav_path = line.strip().split()
            utt2wav_path[utt] = wav_path


    utt2feat_path = dict()
    with open(kaldi_fbank_path, 'r') as rf:
        for line in tqdm(rf.readlines()):
            utt, feat_path = line.strip().split()
            utt2feat_path[utt] = feat_path          
    
    
    utt_list = list(utt2wav_path.keys())
    for utt in tqdm(utt_list):
        
        torchaudio_fbank, sr = get_torchaudio_fbank(utt2wav_path[utt])
        if sr == 16000:
            print(utt, utt2wav_path[utt])
            
            print("torchaudio fbank")
            print(torchaudio_fbank, torchaudio_fbank.shape)
            
            print("kaldi fbank")
            kaldi_fbank = kaldiio.load_mat(utt2feat_path[utt])
            print(kaldi_fbank, kaldi_fbank.shape)
            return


if __name__ == '__main__':
    main()

