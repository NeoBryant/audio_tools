#coding=utf-8
# File      :   test_sox_speed_aug.py
# Time      :   2022/08/09 11:12:10
# Author    :   Jinghan Peng
# Desciption:   

import os, sys
import sox
import torchaudio
import time
import torch

def main():
    in_path = "/data3/pengjinghan/test_wav/AfQGUOMKCAQ.wav"
    out_path = "/data3/pengjinghan/test_wav/sp2-AfQGUOMKCAQ.wav"
    
    # waveform, sr = torchaudio.backend.sox_io_backend.load(in_path,
    #             frame_offset=0 , 
    #             num_frames=-1, 
    #             normalize=False, 
    #             channels_first=False)
    # waveform = waveform.numpy()
    # print(waveform.shape)
    # print(waveform[100:,0])
    
    for i in range(1):
        waveform, sr = torchaudio.backend.sox_io_backend.load(in_path,
                frame_offset=0 , 
                num_frames=32320, 
                normalize=False, 
                channels_first=False)
        
        waveform.squeeze_(1)
        
        beg_time = time.time()
        
        waveform = waveform.unsqueeze(1).numpy()
        # sox -t wav /data6/pengjinghan/ffsvc2020_data/ffsvc2020_data/wav/dev/T0549/549PCM5M/T0549_549PCM5M_recorded6_0305_normal.wav -t wav - speed 1.1
        tfm = sox.Transformer()
        tfm.speed(1.1)
        # array_out = tfm.build_array(input_filepath=in_path)
        # beg_time = time.time()
        ta_array_out = tfm.build_array(input_array=waveform, sample_rate_in=sr)
        # print(f"{time.time() - beg_time} s")
        # sox_array_out = tfm.build_array(input_filepath=in_path)
        
        # print(type(ta_array_out))
        ta_array_out = torch.from_numpy(ta_array_out.copy())
        # print(type(ta_array_out))
        
        print(f"{ta_array_out.shape}, {time.time() - beg_time} s")
        print(ta_array_out[100:200])
        
        waveform, sr = torchaudio.backend.sox_io_backend.load(in_path,
                frame_offset=0 , 
                num_frames=32320, 
                normalize=False, 
                channels_first=True)
        print(f"raw wav shape: {waveform.shape}")
        beg_time = time.time()

        effects = [
            ["speed", "1.1"],
            ["rate", f"{sr}"],
        ]
        sox_effect_waveform, sample_rate_n = torchaudio.sox_effects.apply_effects_tensor(waveform, sr, effects)
        print(f"{sox_effect_waveform.shape}, {sample_rate_n}, {time.time() - beg_time} s")
        sox_effect_waveform = sox_effect_waveform.squeeze(0)
        print(sox_effect_waveform[100:200])
        
        diff = torch.sum(sox_effect_waveform - ta_array_out)
        print(diff)
    
    # print(type(ta_array_out), ta_array_out.shape)
    # print(ta_array_out[100:])
    # # tfm.build_file(in_path, out_path)
    
    # print(type(sox_array_out), sox_array_out.shape)
    # print(sox_array_out[100:])
    # if ta_array_out.any() == sox_array_out.any():
    #     print("same")

if __name__ == '__main__':
    main()

