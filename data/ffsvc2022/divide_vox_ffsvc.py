#coding=utf-8
# File      :   divide_vox_ffsvc.py
# Time      :   2022/06/14 11:35:00
# Author    :   Jinghan Peng
# Desciption:   将vox+ffsvc的表单划分开为vox和ffsvc数据集表单

import os, sys
import shutil
from tqdm import tqdm

def main():
    in_dir        = "/data3/pengjinghan/ffsvc2020_voxceleb12_fbank81_16k_cut_1200/data_list/dataset/train"
    out_vox_dir   = "/data3/pengjinghan/ffsvc2020_voxceleb12_fbank81_16k_cut_1200/data_list/dataset/train_vox"
    out_ffsvc_dir = "/data3/pengjinghan/ffsvc2020_voxceleb12_fbank81_16k_cut_1200/data_list/dataset/train_ffsvc"
    
    os.makedirs(out_vox_dir, exist_ok=True)
    os.makedirs(out_ffsvc_dir, exist_ok=True)
    
    
    # utt2spk
    vox_utt_set = set()
    vox_spk_set = set()
    ffsvc_utt_set = set()
    ffsvc_spk_set = set()
    
    
    utt2spk_path = os.path.join(in_dir, "utt2spk")
    out_vox_utt2spk_path = os.path.join(out_vox_dir, "utt2spk")
    out_ffsvc_utt2spk_path = os.path.join(out_ffsvc_dir, "utt2spk")
    with open(utt2spk_path, 'r') as rf, open(out_vox_utt2spk_path, 'w') as wf1, open(out_ffsvc_utt2spk_path, 'w') as wf2:
        for line in tqdm(rf.readlines()):
            utt, spk = line.strip().split()
            if "id" in utt: # vox
                wf1.write(line)
                vox_utt_set.add(utt)
                if spk not in vox_spk_set:
                    vox_spk_set.add(spk)
            else: # ffsvc
                wf2.write(line)
                ffsvc_utt_set.add(utt)
                if spk not in ffsvc_spk_set:
                    ffsvc_spk_set.add(spk)
                
    print(f"vox utt: {len(vox_utt_set)}")
    print(f"vox spk: {len(vox_spk_set)}")
    print(f"ffsvc utt: {len(ffsvc_utt_set)}")
    print(f"ffsvc spk: {len(ffsvc_spk_set)}")
    
    # spk2utt
    out_vox_spk2utt_path = os.path.join(out_vox_dir, "spk2utt")
    out_ffsvc_spk2utt_path = os.path.join(out_ffsvc_dir, "spk2utt")
    
    cmd = f"./../../utils/utt2spk_to_spk2utt.pl {out_vox_utt2spk_path} > {out_vox_spk2utt_path}"
    os.system(cmd)
    cmd = f"./../../utils/utt2spk_to_spk2utt.pl {out_ffsvc_utt2spk_path} > {out_ffsvc_spk2utt_path}"
    os.system(cmd)
    
    # feats.scp
    featsscp_path = os.path.join(in_dir, "feats.scp")
    out_vox_featsscp_path = os.path.join(out_vox_dir, "feats.scp")
    out_ffsvc_featsscp_path = os.path.join(out_ffsvc_dir, "feats.scp")
    with open(featsscp_path, 'r') as rf, open(out_vox_featsscp_path, 'w') as wf1, open(out_ffsvc_featsscp_path, 'w') as wf2:
        for line in tqdm(rf.readlines()):
            utt, _ = line.strip().split()
            if "id" in utt: # vox
                wf1.write(line)
            else: # ffsvc
                wf2.write(line)
                
    # utt2num_frames
    utt2num_frames_path = os.path.join(in_dir, "utt2num_frames")
    out_vox_utt2num_frames_path = os.path.join(out_vox_dir, "utt2num_frames")
    out_ffsvc_utt2num_frames_path = os.path.join(out_ffsvc_dir, "utt2num_frames")
    with open(utt2num_frames_path, 'r') as rf, open(out_vox_utt2num_frames_path, 'w') as wf1, open(out_ffsvc_utt2num_frames_path, 'w') as wf2:
        for line in tqdm(rf.readlines()):
            utt, _ = line.strip().split()
            if "id" in utt: # vox
                wf1.write(line)
            else: # ffsvc
                wf2.write(line)
                
    # spk2num
    spk2num_path = os.path.join(in_dir, "spk2num")
    out_vox_spk2num_path = os.path.join(out_vox_dir, "spk2num")
    out_ffsvc_spk2num_path = os.path.join(out_ffsvc_dir, "spk2num")
    with open(spk2num_path, 'r') as rf, open(out_vox_spk2num_path, 'w') as wf1, open(out_ffsvc_spk2num_path, 'w') as wf2:
        for line in tqdm(rf.readlines()):
            spk, _ = line.strip().split()
            if "id" in spk: # vox
                wf1.write(line)
            else: # ffsvc
                wf2.write(line)

    # spk2label
    shutil.copyfile(os.path.join(in_dir, "spk2label"), os.path.join(out_vox_dir, "spk2label"))
    shutil.copyfile(os.path.join(in_dir, "spk2label"), os.path.join(out_ffsvc_dir, "spk2label"))

if __name__ == '__main__':
    main()

