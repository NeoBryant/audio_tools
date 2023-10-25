import os
import tqdm
import math
import random
import codecs
import argparse
import sys
import shutil
import collections
from data_utils import generate_list_file, read2data, check_file


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default="/data3/pengjinghan/ffsvc2020_voxceleb12_fbank81_16k_cut_1200/data_list_no_sp")
    parser.add_argument("--save_list_dir", type=str, help="", default="/data3/pengjinghan/ffsvc2020_voxceleb12_fbank81_16k_cut_1200/data_list_no_sp/dataset_valid_155")
    parser.add_argument("--valid_spks", type=int, default=155) #6000) #6149) #18447)
    parser.add_argument("--valid_utts_pspk", type=int, default=10)
    parser.add_argument("--augs_drop", type=int, default=0)
    args = parser.parse_args()
    return args


def del_augement(utt, augs):  
    s = utt.split("-")
    aug = list(set(augs).intersection(set(s)))
    if len(aug) != 0:
        utt_origin = utt.replace("-" + aug[0], "")
        return utt_origin
    else:
        return utt


def valid_sample(spk2utt, valid_spks, valid_utts_pspk, spk2num=""):
    print(valid_spks)
    spk2utt_dict = read2data(spk2utt, is_list=True)
    if not os.path.exists(spk2num):
        spk2num_list = []
        for key, value in spk2utt_dict.items():
            spk2num_list.append((key, len(value)))
    else:
        spk2num_list = read2data(spk2num, data_type="list", value_type="int")
    spk2num_sort = sorted(spk2num_list, key=lambda x: (x[1], x[0]), reverse=True)
    
    ffsvc_spk2num_sort = list()
    for key, value in tqdm.tqdm(spk2num_sort):
        if "id" not in key:
            ffsvc_spk2num_sort.append((key, value))
    print(len(ffsvc_spk2num_sort))
    valid_spk_select = random.sample([i[0] for i in ffsvc_spk2num_sort], valid_spks)
    # valid_spk_select = random.sample([i[0] for i in spk2num_sort], valid_spks)
    
    valid_utts = []
    for spk in valid_spk_select:
        assert len(spk2utt_dict[spk]) > valid_utts_pspk, "spk {} has too little utt"
        utt_sample = random.sample(spk2utt_dict[spk], valid_utts_pspk)
        valid_utts += (utt_sample)
    return valid_utts


def utt_augs_add(val_utts, augs=None):
    val_augs = []
    for utt in val_utts:
        data_root = del_augement(utt, augs)
        utt_aug = [data_root]
        for aug_type in augs:
            s1 = data_root.split("-")
            s1.insert(-1, aug_type)
            s2 = data_root.split("-")
            s2.append(aug_type)
            utt_aug.append("-".join(s1))
            utt_aug.append("-".join(s2))
        val_augs += utt_aug
    return val_augs


def data_div(feats_scp, spk2utt, save_list_dir, valid_spks, valid_utts_pspk, augs=None, spk2num=""):
    feats_dict = read2data(feats_scp)
    utts_all = set(feats_dict.keys())
    valid_utts = valid_sample(spk2utt, valid_spks, valid_utts_pspk, spk2num=spk2num)
    if augs is not None:
        val_augs = utt_augs_add(valid_utts, augs)
        # val_augs = get_augement(valid_utts, augs)
        train_utts = utts_all - set(val_augs)
    else:
        train_utts = utts_all - set(valid_utts)

    with open(os.path.join(save_list_dir, "valid", "feats.scp"), "w") as f_val:
        print("Writing validation feats.scp")
        for utt in tqdm.tqdm(valid_utts):
            f_val.write(utt + " " + feats_dict[utt] + "\n")
    
    with open(os.path.join(save_list_dir, "train", "feats.scp"), "w") as f_train:
        print("Writing train feats.scp")
        for utt in tqdm.tqdm(train_utts):
            f_train.write(utt + " " + feats_dict[utt] + "\n")


def main():
    args = parse_opt()
    train_dir = os.path.join(args.save_list_dir, "train")
    val_dir = os.path.join(args.save_list_dir, "valid")
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(val_dir, exist_ok=True)

    file_lists = check_file(args.data_dir, ["feats.scp", "spk2utt", "utt2spk", "utt2num_frames"])
    feats_scp, spk2utt, utt2spk, utt2num_frames = file_lists

    if args.augs_drop:
        augs_mark = ["noise", "reverb", "babble", "music"]
    else:
        augs_mark = None

    data_div(feats_scp, spk2utt, args.save_list_dir, 
             args.valid_spks, args.valid_utts_pspk, 
             augs=augs_mark,
             spk2num=os.path.join(args.data_dir, "spk2num"))

    generate_list_file(os.path.join(train_dir, "feats.scp"), train_dir, utt2spk, utt2num_frames)
    generate_list_file(os.path.join(val_dir, "feats.scp"), val_dir, utt2spk, utt2num_frames)
    shutil.copy(os.path.join(train_dir, "spk2label"), val_dir)


if __name__ == "__main__":
    main()
