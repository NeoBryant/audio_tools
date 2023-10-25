#coding=utf-8
# File      :   test_torchaudio_readspeed.py
# Time      :   2022/08/08 16:27:50
# Author    :   Jinghan Peng
# Desciption:   测试torchaudio读取音频耗时情况

import os, sys
import torchaudio
import time
import random

def main():
    in_dir = "/data2/pengjinghan/test_wav"
    # file_list = ["1m.wav", "5m.wav", "10m.wav", "30m.wav", "60m.wav", "3h.wav", "9h.wav"]
    file_list = ["3h.wav", "9h.wav"]
    
    for file_name in file_list: #os.listdir(in_dir):
        wav_path = os.path.join(in_dir, file_name)

        beg_time = time.time()
        info = torchaudio.backend.sox_io_backend.info(wav_path)
        total_duration = info.num_frames / info.sample_rate # 音频总时长
    
        duration = 2.02 # 需要读取的音频段时长
        offset = random.random() * (total_duration - duration)  #np.array([np.int64(random.random()*(info.num_frames-duration))])[0]
        start_samples = int(offset * info.sample_rate) # 开始读取的采样点位置
        duration_samples = int(duration * info.sample_rate) #if duration != None else -1
        # duration_samples = 12 * info.sample_rate
    
    
        waveform, sr = torchaudio.backend.sox_io_backend.load(wav_path,
            frame_offset=16000 * 3 * 60 * 60,
            num_frames=duration_samples, 
            normalize=False, 
            channels_first=True)
        
        end_time = time.time()
        print(f"{file_name} - read time: {end_time - beg_time} s!")
        
        
    

if __name__ == '__main__':
    main()

