#coding=utf-8
# File      :   gen_spk_map.py
# Time      :   2022/06/09 11:48:39
# Author    :   Jinghan Peng
# Desciption:   生成base模型的spk2label转换到refine模型的spk2label的label映射关系文件spk_map.map

import os, sys
from tqdm import tqdm

def read_spk2label(path):
    spk2label = dict()
    with open(path, 'r') as rf:
        for line in rf.readlines():
            spk, label = line.strip().split()
            spk2label[spk] = label
    return spk2label


def main():
    base_spk2label_path = "/data2/pengjinghan/exp/traindata/cnsrc/data_list_weixin_cnsrc_24w_new/dataset/train/spk2label"
    #"/data3/pengjinghan/ffsvc2020_voxceleb12_fbank81_16k_cut_1200/data_list_vox_ffsvc3xsp/dataset/train/spk2label"
    #"/data3/pengjinghan/voxceleb12/data_list/dataset/train/spk2label"
    #"/data3/pengjinghan/ffsvc2020_voxceleb12_fbank81_16k_cut_1200/data_list_vox_ffsvc3xsp/dataset/train/spk2label"
    #"/data3/pengjinghan/ffsvc2020_voxceleb12_fbank81_16k_cut_1200/data_list/dataset/train/spk2label"
    #"/data3/pengjinghan/ffsvc2020_voxceleb12_fbank81_16k_cut_1200/data_list/dataset/train/spk2label"
    #"/data3/pengjinghan/ffsvc2020_voxceleb12_fbank81_16k_cut_1200/data_list_no_sp/dataset_v2/train/spk2label"
    #"/data3/pengjinghan/ffsvc2020_voxceleb12_fbank81_16k_cut_1200/data_list/dataset/train/spk2label"
    refine_spk2label_path = "/data2/pengjinghan/exp/traindata/cnsrc/data_list_cnsrc_1w_cut_nosp/dataset/train/spk2label"
    #"/data2/pengjinghan/FFSVC_data/FFSVC2020_210/data_list/dataset/train/spk2label"
    #"/data3/pengjinghan/ffsvc2020_voxceleb12_fbank81_16k_cut_1200/data_list_vox_ffsvc3xsp/dataset/train/spk2label"
    #"/data3/pengjinghan/ffsvc2020_fbank_concat_cut_1200/data_list_nosp/dataset/train/spk2label"
    #"/data3/pengjinghan/ffsvc2020_voxceleb12_fbank81_16k_cut_1200/data_list_no_sp/dataset_v2/train/spk2label"
    #"/data3/pengjinghan/ffsvc2020_voxceleb12_fbank81_16k_cut_1200/data_list_vox_ffsvc3xsp/dataset/train/spk2label"
    #"/data3/pengjinghan/ffsvc2020_voxceleb12_fbank81_16k_cut_1200/data_list_vox_ffsvc3xsp/dataset/train/spk2label"
    #"/data3/pengjinghan/ffsvc2020_fbank_concat_cut_1200/data_list/dataset/train/spk2label"
    #"/data3/pengjinghan/ffsvc2020_fbank_concat_cut_1200/data_list_nosp/dataset/train/spk2label"
    #"/data3/pengjinghan/ffsvc2020_fbank_concat_cut_1200/data_list_nosp/dataset/train/spk2label"
    
    out_path = "/data2/pengjinghan/exp/traindata/cnsrc/data_list_cnsrc_1w_cut_nosp/dataset/train/spk_map.map"
    #"/data2/pengjinghan/FFSVC_data/FFSVC2020_210/data_list/dataset/train/spk_map.map"
    #"/data3/pengjinghan/ffsvc2020_voxceleb12_fbank81_16k_cut_1200/data_list_vox_ffsvc3xsp/dataset/train/spk_map_no_reserved_weight.map"
    #"/data3/pengjinghan/ffsvc2020_fbank_concat_cut_1200/data_list_nosp/dataset/train/spk_map.map"
    #"/data3/pengjinghan/ffsvc2020_voxceleb12_fbank81_16k_cut_1200/data_list_no_sp/dataset_v2/train/spk_map.map"
    #"/data3/pengjinghan/ffsvc2020_voxceleb12_fbank81_16k_cut_1200/data_list_vox_ffsvc3xsp/dataset/train/spk_map.map"
    #"/data3/pengjinghan/ffsvc2020_fbank_concat_cut_1200/data_list/dataset/train/spk_map.map"
    #"/data3/pengjinghan/ffsvc2020_fbank_concat_cut_1200/data_list_nosp/dataset/train/spk_map.map"
    #"/data3/pengjinghan/ffsvc2020_fbank_concat_cut_1200/data_list_nosp/dataset/train/spk_map.map"
    
    base_spk2label = read_spk2label(base_spk2label_path)
    refine_spk2label = read_spk2label(refine_spk2label_path)
    
    with open(out_path, 'w') as wf:
        for spk, refine_label in tqdm(refine_spk2label.items()):
            if spk in base_spk2label:
                base_label = base_spk2label[spk]
        
                wf.write(f"{base_label} {refine_label}\n")
            else:
                print(f"[warning] {spk} not exists in {base_spk2label_path}")



if __name__ == '__main__':
    main()

