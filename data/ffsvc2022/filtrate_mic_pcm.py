#coding=utf-8
# File      :   filtrate_mic_pcm.py
# Time      :   2022/06/10 11:01:02
# Author    :   Jinghan Peng
# Desciption:   过滤掉ffsvc训练集中的麦克风和PCM数据，只留下Iphone和Ipad音频

import os, sys
from tqdm import tqdm

def main():
    in_dir  = "/data2/pengjinghan/ffsvc2020_fbank_concat_cut_1200/data_list_nosp"
    out_dir = "/data2/pengjinghan/ffsvc2020_fbank_concat_cut_1200/data_list_nosp_iphone_ipad"
    
    os.makedirs(out_dir, exist_ok=True)
    
    # utt2spk
    utt2spk = dict()
    utt2spk_path = os.path.join(in_dir, "utt2spk")
    out_utt2spk_path = os.path.join(out_dir, "utt2spk")
    with open(utt2spk_path, 'r') as rf, open(out_utt2spk_path, 'w') as wf:
        for line in tqdm(rf.readlines()):
            utt, spk = line.strip().split()
            if "PCM" in utt or "MIC" in utt:
                continue
            utt2spk[utt] = spk
            wf.write(line)
    
    print(f"{len(utt2spk)} utts(iphone & ipad)")
    
    # spk2utt
    out_spk2utt_path = os.path.join(out_dir, "spk2utt")
    cmd = f"./../../utils/utt2spk_to_spk2utt.pl {out_utt2spk_path} > {out_spk2utt_path}"
    os.system(cmd)
    
    # utt2num_frames
    utt2num_frames_path = os.path.join(in_dir, "utt2num_frames")
    out_utt2num_frames_path = os.path.join(out_dir, "utt2num_frames")
    with open(utt2num_frames_path, 'r') as rf, open(out_utt2num_frames_path, 'w') as wf:
        for line in tqdm(rf.readlines()):
            utt, _ = line.strip().split()
            if utt in utt2spk:
                wf.write(line)
                
    # feats.scp
    feats_scp_path = os.path.join(in_dir, "feats.scp")
    out_feats_scp_path = os.path.join(out_dir, "feats.scp")
    with open(feats_scp_path, 'r') as rf, open(out_feats_scp_path, 'w') as wf:
        for line in tqdm(rf.readlines()):
            utt, _ = line.strip().split()
            if utt in utt2spk:
                wf.write(line)

if __name__ == '__main__':
    main()

