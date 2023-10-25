#coding=utf-8
# File      :    filtrate_dur_wav.py
# Time      :   2022/03/15 12:00:43
# Author    :   Jinghan Peng
# Desciption:   按音频时长过滤音频（将满足音频时长限制的音频按相同目录结构进行复制）

import os, sys
from pydub import AudioSegment
from tqdm import tqdm


def main():
    in_dir = "/home/pengjinghan/20220323_20utt_8k_mixvad-post_wav"
    out_dir = "/home/pengjinghan/20220323_20utt_8k_mixvad-post_wav-filtrate_10s"


    os.makedirs(out_dir, exist_ok=True)

    time_threshold = 10 # 过滤短音频，单位：秒

    for root, dirs, files in tqdm(os.walk(in_dir)):
        for file in files:
            fp = os.path.join(root, file)
            audio = AudioSegment.from_file(fp, format='wav')
            dur = audio.duration_seconds

            if dur >= time_threshold:
                out_path = fp.replace(in_dir, out_dir)

                sub_out_dir = out_path[:out_path.rfind('/')]

                os.makedirs(sub_out_dir, exist_ok=True)

                cmd = f"cp {fp} {out_path}"
                os.system(cmd)

if __name__ == '__main__':
    main()

