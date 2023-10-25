#coding=utf-8
# File      :   gen_train_set_scp.py
# Time      :   2022/05/23 14:03:36
# Author    :   Jinghan Peng
# Desciption:   生成ffsvc2020 train/dev/supplement 集的表单

import collections
import os, sys
from tqdm import tqdm

def main():
    in_dir = "/data2/pengjinghan/FFSVC_data/FFSVC2020_210/train_dev"
    out_dir = "/data2/pengjinghan/FFSVC_data/FFSVC2020_210/data_list"
        
    utt2wav_path = dict()
    spk2utt_list = collections.defaultdict(list)
    utt2spk = dict()
    
    # train和supplement的近场iphone音频有重复
    for root, dirs, files in tqdm(os.walk(in_dir)):
        for name in files:
            file_path = os.path.join(root, name)
            if file_path.endswith(".wav") and ' ' not in file_path:
                utt = file_path.split('/')[-1].split('.wav')[0]
                spk = file_path.split('/')[-3][1:]

                utt = spk+"-"+utt

                utt2wav_path[utt] = file_path
                spk2utt_list[spk].append(utt)
                utt2spk[utt] = spk

    print(f"{len(spk2utt_list)} spks")
    print(f"{len(utt2wav_path)} utts")

    
    # wav.scp utt2spk
    utt_list = list(utt2wav_path.keys())
    utt_list.sort()
    wav_scp_path = os.path.join(out_dir, "wav.scp")
    utt2spk_path = os.path.join(out_dir, "utt2spk")
    with open(wav_scp_path, 'w') as wf1, open(utt2spk_path, 'w') as wf2:
        for utt in tqdm(utt_list):
            wav_path = utt2wav_path[utt]
            spk = utt2spk[utt]
            wf1.write(f"{utt} {wav_path}\n")
            wf2.write(f"{utt} {spk}\n")

    # spk2utt
    spk_list = list(spk2utt_list.keys())
    spk_list.sort()
    spk2utt_path = os.path.join(out_dir, "spk2utt")
    with open(spk2utt_path, 'w') as wf:
        for spk in tqdm(spk_list):
            utt_list = spk2utt_list[spk]
            utt_list.sort()
            wf.write(spk+" "+" ".join(utt_list)+"\n")

    # spk2utt_num，计算平均每个说话人有多少条utt
    # spk2utt_num = [len(utt_list) for utt_list in spk2utt_list.values()]
    # print("mean:",sum(spk2utt_num)/len(spk2utt_num))
    # print("max:",max(spk2utt_num), "min:",min(spk2utt_num))
    """
    mean: 17072.916
    max: 26102 min: 10332
    """
    
if __name__ == '__main__':
    main()

