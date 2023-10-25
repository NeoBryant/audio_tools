#coding=utf-8
# File      :   find_2channel_8kHz_wav.py
# Time      :   2021/09/01 16:04:08
# Author    :   Jinghan Peng
# Desciption:   过滤找到单声道、8kHz采用率

import os
import wave
from tqdm import tqdm

def main():
    in_dir = "/data4/pengjinghan/tsvad/raw/wav"
    # out_path = "/data/pengjinghan/origin_data/mandarin/1c_8kHz_audio/wav_raw.scp"
    out_path = "/data4/pengjinghan/tsvad/1c8k/wav_1c8k.scp"
    number_target_wav = 0

    with open(out_path, 'w') as wf2:
        for fn in tqdm(os.listdir(in_dir)):
            if fn.endswith(".wav"):
                file_path = os.path.join(in_dir, fn)
                try:
                    with wave.open(file_path) as wf:
                        # frames     = wf.getnframes()  # 帧总数
                        sampleRate = wf.getframerate()  # 采样频率
                        channels   = wf.getnchannels()
                        # time     = frames / sampleRate  # 声音信号的长度
                        if sampleRate == 8000 and channels == 1:
                            # aliword_path = file_path.replace(".wav", ".txt")
                            # if os.path.exists(aliword_path):
                            # print(file_path)
                            wf2.write(f"{file_path}\n")
                            number_target_wav += 1
                except:
                    continue

    print("1c8k wav sum:", number_target_wav)


if __name__ == '__main__':
    main()
    