#coding=utf-8
# File      :   data_balance_online.py
# Time      :   2022/07/19 11:13:55
# Author    :   Jinghan Peng
# Desciption:   基于torchaudio的online dataset划分训练集和测试集，同时生成spk2label

import os
import tqdm
import math
import random
import codecs
import argparse
import sys
import shutil
import collections


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default="/data3/pengjinghan/voxceleb_dataset/data_list")
    parser.add_argument("--save_list_dir", type=str, default="/data3/pengjinghan/voxceleb_dataset/data_list/dataset")
    parser.add_argument("--valid_spks", type=int, default=5994)
    parser.add_argument("--valid_utts_pspk", type=int, default=1)
    args = parser.parse_args()
    return args


def check_file(data_dir, except_file=["wav.scp", "spk2utt", "utt2spk"]):
    file_lists = []
    print("except file: {}".format(" ".join(except_file)))
    for file_name in except_file:
        file_list = os.path.join(data_dir, file_name)
        if os.path.exists(file_list):
            print("check {} exists".format(file_list))
            file_lists.append(file_list)
        else:
            raise Exception("not found {}".format(file_list))
    return file_lists


def read2data(path, is_list=False, data_type="dict", value_type="str"):
    if data_type == "dict":
        data = {}
    elif data_type == "list":
        data = []
    else:
        RuntimeError("no this data_type !")
    with open(path, "r") as f:
        for line in f.readlines():
            line = line.strip()
            key = line.split()[0]
            if is_list:
                value = line.split()[1:]
            else:
                value = line.split()[1]

            if value_type == "int":
                value = int(value)
            elif value_type == "float":
                value = float(value)
            else:
                RuntimeError("no this value_type !")

            if data_type == "dict":
                data[key] = value
            else:
                data.append((key, value))
    return data

def valid_sample(spk2utt, valid_spks, valid_utts_pspk, spk2num=""):
    spk2utt_dict = read2data(spk2utt, is_list=True)
    if not os.path.exists(spk2num):
        spk2num_list = []
        for key, value in spk2utt_dict.items():
            spk2num_list.append((key, len(value)))
    else:
        spk2num_list = read2data(spk2num, data_type="list", value_type="int")
    spk2num_sort = sorted(spk2num_list, key=lambda x: (x[1], x[0]), reverse=True)
    valid_spk_select = random.sample([i[0] for i in spk2num_sort], valid_spks) # 选择的valid的spk列表
    
    valid_utts = list()
    for spk in valid_spk_select:
        assert len(spk2utt_dict[spk]) > valid_utts_pspk, "spk {} has too little utt"
        utt_sample = random.sample(spk2utt_dict[spk], valid_utts_pspk)                
        valid_utts += (utt_sample)
    return valid_utts

def data_div(wav_scp, spk2utt, save_list_dir, valid_spks, valid_utts_pspk, spk2num=""):
    utt2wav_path = read2data(wav_scp)
    utts_all = set(utt2wav_path.keys())
    print(f"numbe of utts: {len(utts_all)}")
    valid_utts = valid_sample(spk2utt, valid_spks, valid_utts_pspk, spk2num=spk2num)

    train_utts = list(utts_all - set(valid_utts))

    with open(os.path.join(save_list_dir, "valid", "wav.scp"), "w") as f_val:
        print("Writing validation wav.scp")
        valid_utts.sort()
        print(f"number of valid utts: {len(set(valid_utts))}")
        for utt in tqdm.tqdm(valid_utts):
            f_val.write(utt + " " + utt2wav_path[utt] + "\n")
    
    with open(os.path.join(save_list_dir, "train", "wav.scp"), "w") as f_train:
        print("Writing train wav.scp")
        train_utts.sort()
        for utt in tqdm.tqdm(train_utts):
            f_train.write(utt + " " + utt2wav_path[utt] + "\n")


def gen_spk2label(spk2utt, out_dir):
    spk2utt_dict = read2data(spk2utt, is_list=True)
    spks_all = list(spk2utt_dict.keys())
    spks_all.sort()
    
    with open(os.path.join(out_dir, "spk2label"), 'w') as wf:
        for index, (spk) in enumerate(spks_all):
            wf.write(f"{spk} {index}\n")


def generate_list_file(wav_scp, save_list_dir, raw_utt2spk):
    """
    generate wav_scp, uid2classes and utt2spk according to wav.scp
    (the subset of raw wav.scp or the wav.scp of cut data) and raw utt2spk
    Args:
        wav_scp: path of wav.scp
        save_list_dir: the directory to save spk2utt, uid2classes and utt2spk
        raw_utt2spk: the path of raw utt2spk
    """
    utt2wav_path = read2data(wav_scp) # 当前dataset的utt2wav_path
    raw_utt2spk_dict = read2data(raw_utt2spk) # 总的utt2spk

    spk2utt = collections.defaultdict(list)
    with open(os.path.join(save_list_dir, "utt2spk"), "w") as f_utt2spk, \
        open(os.path.join(save_list_dir, "spk2utt"), "w") as f_spk2utt, \
        open(os.path.join(save_list_dir, "spk2num"), "w") as f_spk2num, \
        open(os.path.join(save_list_dir, "spk2label"), "w") as f_spk2label:
                
        print("Writing utt2spk")
        utts_all = list(utt2wav_path.keys())
        utts_all.sort()
        for utt in tqdm.tqdm(utts_all):
            spk = raw_utt2spk_dict[utt]
            f_utt2spk.write(f"{utt} {spk}\n")
            spk2utt[spk].append(utt)

        spks_all = list(spk2utt.keys())
        spks_all.sort()
        print("Writing spk2utt spk2num spk2label")
        for i, (spk) in tqdm.tqdm(enumerate(spks_all)):
            utt_list = spk2utt[spk]
            f_spk2utt.write(spk + " " + " ".join(utt_list) + "\n")
            f_spk2num.write(spk + " " + str(len(utt_list)) + "\n")
            f_spk2label.write(spk + " " + str(i) + "\n")
    
            
def main():
    args = parse_opt()
    train_dir = os.path.join(args.save_list_dir, "train")
    val_dir = os.path.join(args.save_list_dir, "valid")
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(val_dir, exist_ok=True)

    file_lists = check_file(args.data_dir, ["wav.scp", "spk2utt", "utt2spk"])
    wav_scp_path, spk2utt_path, utt2spk_path = file_lists


    data_div(wav_scp_path, spk2utt_path, args.save_list_dir, 
             args.valid_spks, args.valid_utts_pspk, 
             spk2num=os.path.join(args.data_dir, "spk2num"))
    
    generate_list_file(os.path.join(train_dir, "wav.scp"), train_dir, utt2spk_path)
    generate_list_file(os.path.join(val_dir, "wav.scp"), val_dir, utt2spk_path)

    # gen_spk2label(spk2utt, train_dir)
    shutil.copy(os.path.join(train_dir, "spk2label"), val_dir)
    

if __name__ == '__main__':
    main()

