#coding=utf-8
# File      :   filtrate_aug_scp.py
# Time      :   2022/03/28 14:10:37
# Author    :   Jinghan Peng
# Desciption:   过滤vox数据中spx3变速变调的feats.scp，输出原始vox+ffsvc3xsp的feats.scp

import os, sys
from tqdm import tqdm
from argparse import ArgumentParser

def parse_args():
    parser = ArgumentParser()

    parser.add_argument("--in_dir", type=str, help="feats.scp, utt2spk, spk2utt, utt2num_frames", 
                        default="/data3/pengjinghan/ffsvc2020_voxceleb12_fbank81_16k_cut_1200/data_list")

    parser.add_argument("--out_dir", type=str, help="", 
                        default="/data3/pengjinghan/ffsvc2020_voxceleb12_fbank81_16k_cut_1200/data_list_vox_ffsvc3xsp")
    
    args = parser.parse_args()
    return args

def is_augmentation(utt):
    """根据utt名判断是否为数据增强"""
    
    # 变速变调
    if "id" in utt and ("sp1.1-" in utt or "sp0.9-" in utt):
        return True
    
    return False

def write_utt2other(utt_set, in_path, out_path):
    """读取in_path，若在utt_set中，则写入out_path"""
    with open(in_path, 'r') as rf, open(out_path, 'w') as wf:
        for line in tqdm(rf.readlines()):
            utt = line.strip().split()[0]
            if utt in utt_set:
                wf.write(line)

def main(args):
    in_dir = args.in_dir
    out_dir = args.out_dir 
    os.makedirs(out_dir, exist_ok=True)
    
    
    # feats.scp
    raw_utt_set = set()
    feats_scp_path = os.path.join(in_dir, "feats.scp")
    if os.path.isfile(feats_scp_path):
        with open(feats_scp_path, 'r') as rf, open(os.path.join(out_dir, "feats.scp"), 'w') as wf:
            for line in tqdm(rf.readlines()):
                utt = line.strip().split()[0]
                if not is_augmentation(utt):
                    raw_utt_set.add(utt)
                    wf.write(line)
    else:
        print(f"[WARNING] {feats_scp_path} not exist!")
    
    print(f"raw utt: {len(raw_utt_set)}")
    
    # utt2num_frames
    utt2num_frames_path = os.path.join(in_dir, "utt2num_frames")
    if os.path.isfile(utt2num_frames_path):
        out_utt2num_frames = os.path.join(out_dir, "utt2num_frames")
        write_utt2other(raw_utt_set, utt2num_frames_path, out_utt2num_frames)
    else:
        print(f"[WARNING] {utt2num_frames_path} not exist!")
        
    
    # utt2spk, spk2utt
    utt2spk_path = os.path.join(in_dir, "utt2spk")
    if os.path.isfile(utt2spk_path):
        out_utt2spk = os.path.join(out_dir, "utt2spk")
        write_utt2other(raw_utt_set, utt2spk_path, out_utt2spk)
        
        # 调用perl脚本将utt2spk转为spk2utt
        out_spk2utt = os.path.join(out_dir, "spk2utt")
        cmd = f"./../../utils/utt2spk_to_spk2utt.pl {out_utt2spk} > {out_spk2utt}"
        os.system(cmd)
    else:
        print(f"[WARNING] {utt2spk_path} not exist!")
    
        
if __name__ == '__main__':
    args = parse_args()
    main(args)

