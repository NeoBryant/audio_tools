#coding=utf-8
# File      :   torchaudio_feature.py
# Time      :   2022/07/14 16:26:47
# Author    :   Jinghan Peng
# Desciption:   

import os, sys
import torchaudio
import torchaudio.transforms as T
import ffmpeg
import numpy as np

def compute_fbank_feats(waveform, fbank_conf={}):
    """提取fbank特征
    Args:
        wavform (torch.tensor): 音频采样点序列
        fbank_conf (dict): fbank配置参数
    Returns:
        torch.tensor: fbank特征
    """
    fbank = torchaudio.compliance.kaldi.fbank(waveform=waveform,
        blackman_coeff=fbank_conf.get("blackman_coeff", 0.42), 
        channel=fbank_conf.get("channel", -1),
        dither=fbank_conf.get("dither", 0),
        energy_floor=fbank_conf.get("energy_floor", 1), 
        frame_length=fbank_conf.get("frame_length", 25),
        frame_shift=fbank_conf.get("frame_shift", 10),
        low_freq=fbank_conf.get("low_freq", 20),
        high_freq=fbank_conf.get("high_freq", 0),
        htk_compat=fbank_conf.get("htk_compat", False),
        min_duration=fbank_conf.get("min_duration", 0),
        num_mel_bins=fbank_conf.get("num_mel_bins", 23),
        preemphasis_coefficient=fbank_conf.get("preemphasis_coefficient", 0.97),
        remove_dc_offset=fbank_conf.get("remove_dc_offset", True),
        round_to_power_of_two=fbank_conf.get("round_to_power_of_two", True),
        sample_frequency=fbank_conf.get("sample_frequency", 16000),
        snip_edges=fbank_conf.get("snip_edges", True),
        subtract_mean=fbank_conf.get("subtract_mean", False),
        use_energy=fbank_conf.get("use_energy", True),
        raw_energy=fbank_conf.get("raw_energy", True),
        use_log_fbank=fbank_conf.get("use_log_fbank", True),
        use_power=fbank_conf.get("use_power", True),
        vtln_high=fbank_conf.get("vtln_high", -500),
        vtln_low=fbank_conf.get("vtln_low", 100),
        vtln_warp=fbank_conf.get("vtln_warp", 1), 
        window_type=fbank_conf.get('window_type', "povey")
    )

    return fbank


def main():
    mp3_path = "/data2/pengjinghan/test.mp3"
    wav_path = "/data2/pengjinghan/test.wav"
    
    new_freq = 16000
    
    mp3_waveform, sr = torchaudio.backend.sox_io_backend.load(mp3_path,
        frame_offset=0 , 
        num_frames=-1, 
        normalize=True, 
        channels_first=True)
    
    # mp3_waveform2, sr = torchaudio.load(mp3_path, )
    
    print(mp3_waveform.shape, sr, mp3_waveform)
    # mp3_waveform = mp3_waveform.mean(0)
    # print(mp3_waveform.shape, sr, mp3_waveform)

    mp3_waveform = torchaudio.transforms.Resample(orig_freq=sr, new_freq=new_freq)(mp3_waveform)
    print(mp3_waveform.shape, new_freq, mp3_waveform)

    # mp3_waveform.unsqueeze_(0)

    mp3_fbank = compute_fbank_feats(mp3_waveform)
    print(mp3_fbank.shape, mp3_fbank)
    
    print(" --------------- ")
    out, _ =(
        ffmpeg
        .input(mp3_path)
        .output('-', format='s16le', acodec='pcm_s16le', ac=1, ar=16000)
        .overwrite_output()
        .run(capture_stdout=True)
    )
    audio = (
        np
        .frombuffer(out, np.float32)
    )
    # print(out)
    # print(audio.shape)
    return
    

    print(" --------------- ")
    
    wav_waveform, sr = torchaudio.backend.sox_io_backend.load(wav_path,
        frame_offset=0 , 
        num_frames=-1, 
        normalize=True, 
        channels_first=True)
    
    wav_waveform = wav_waveform.float()
    print(wav_waveform.shape, sr, wav_waveform)
    wav_waveform = wav_waveform.mean(0)
    print(wav_waveform.shape, sr, wav_waveform)
    wav_waveform.unsqueeze_(0)
    
    wav_fbank = compute_fbank_feats(wav_waveform)
    print(wav_fbank.shape, wav_fbank)

    

if __name__ == '__main__':
    main()

