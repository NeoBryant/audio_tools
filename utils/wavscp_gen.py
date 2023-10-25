#!/usr/bin/env python
#coding=utf-8
# File      :   wavscp_gen.py
# Time      :   2021/08/06 17:42:40
# Author    :   Peng Jinghan 
# Desciption:   根据音频所在目录路径，生成为wav.scp

import os, sys
from argparse import ArgumentParser

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--wav_dir", type=str, help="path to dir of wavs", 
                        default="")
    parser.add_argument("--output_path", type=str, help="path to wav.scp", 
                        default="")
    
    args = parser.parse_args()
    return args

def main(args):
    wav_dir     = args.wav_dir
    wavscp_path = args.output_path

    assert os.path.isdir(wav_dir)
    
    output_dir = os.path.dirname(wavscp_path)
    os.makedirs(output_dir, exist_ok=True)

    utt2wav_path = dict()
    with open(wavscp_path, 'w') as wf:
        for r, _, flns in os.walk(wav_dir):
            for f in flns:
                if f.endswith(".wav"):
                    wave_path = os.path.join(r, f) 
                    utt       = f.split(".wav")[0]
                    # wf.write(f"{utt} {wave_path}\n")
                    utt2wav_path[utt] = wave_path
    
    utt_list = list(utt2wav_path)
    utt_list.sort()

    with open(wavscp_path, 'w') as wf:
        for utt in utt_list:
            wave_path = utt2wav_path[utt]
            wf.write(f"{utt} {wave_path}\n")
    
    cmd = f"python wavscp_to_utt2spk.py --wavscp_path {wavscp_path} --output_dir {output_dir}"
    os.system(cmd)

if __name__ == "__main__":
    args = parse_args()
    main(args)