#coding=utf-8
# File      :   wavscp_to_utt2spk.py
# Time      :   2021/08/11 17:04:30
# Author    :   Jinghan Peng
# Desciption:   

import os
from argparse import ArgumentParser

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--wavscp_path", type=str, help="path of wav.scp", 
                        default="/data3/pengjinghan/weixin_fbank8k_without_tel_encode/data/tdnn/wav.scp")
    parser.add_argument("--output_dir", type=str, help="path of dir to generate utt2spk and spk2utt ", 
                        default="/data3/pengjinghan/weixin_fbank8k_without_tel_encode/data/tdnn/")
    parser.add_argument("--split_char", type=str, choices=['-','_'], help="char to split the spk string from utt string", default='-')
    
    args = parser.parse_args()
    return args

def main(args):
    wavscp_path = args.wavscp_path
    utt2spk_path = os.path.join(args.output_dir, 'utt2spk')
    spk2utt_path = os.path.join(args.output_dir, 'spk2utt')
    
    """读取wav.scp生成utt2spk"""
    with open(wavscp_path, 'r') as rf, open(utt2spk_path, 'w') as wf:
        for line in rf.readlines():
            utt = line.strip().split()[0]
            spk = utt.split(args.split_char)[0]
            wf.write("{} {}\n".format(utt, spk))

    """调用perl脚本将utt2spk转为spk2utt"""
    cmd = f"./utt2spk_to_spk2utt.pl {utt2spk_path} > {spk2utt_path}"
    os.system(cmd)
    
if __name__ == "__main__":
    args = parse_args()
    main(args)
