#coding=utf-8
# File      :   filtrate_2spk_from_aliword.py
# Time      :   2021/09/01 17:59:05
# Author    :   Jinghan Peng
# Desciption:   从单声道8kHz采样率的wav音频的wav.scp中过滤掉没有标准txt标注文件，或有标注文件但说话人不是两个人音频

import os
from tqdm.std import tqdm

def isSpkNumEq2(aliword_fp):
    try:
        spk_set = set()
        with open(aliword_fp, 'r') as rf:
            for line in rf.readlines():
                line = line.strip().split()
                if line != []:
                    spk = line[0]   
                    if spk not in spk_set:
                        spk_set.add(spk)
        
        if len(spk_set) == 2 and 'N' not in spk_set:
            return True
        elif len(spk_set) == 3 and 'N' in spk_set:
            return True
        else:
            return False
    except:
        return False

def main():
    # in_path = "/data/pengjinghan/origin_data/mandarin/1c_8kHz_audio/wav_raw.scp"
    in_path = "/data4/pengjinghan/tsvad/1c8k/wav_1c8k.scp"
    aliword_dir = "/data4/pengjinghan/tsvad/raw/asr"
    # out_path = "/data1/pengjinghan/origin_data/mandarin/1c_8kHz_audio/wav_filtrate.scp"
    out_path = "/data4/pengjinghan/tsvad/1c8k/wav_1c8k_2spk.scp"
    count = 0
    with open(in_path, 'r') as rf, open(out_path, 'w') as wf:
        for line in tqdm(rf.readlines()):
            wave_fp = line.strip()
            utt = wave_fp.split("/")[-1].split(".wav")[0]
            aliword_fp = os.path.join(aliword_dir, f"{utt}.txt")
            if os.path.exists(aliword_fp):
                if isSpkNumEq2(aliword_fp):
                    wf.write(f"{wave_fp}\n")
                    count += 1
    
    print(count)

if __name__ == '__main__':
    main()
    