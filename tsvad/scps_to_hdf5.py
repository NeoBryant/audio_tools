#coding=utf-8
# File      :   scps_to_hdf5.py
# Time      :   2021/08/30 14:13:26
# Author    :   Jinghan Peng
# Desciption:   读取各scp，生成hdf5

import os
from numpy.core.numeric import outer
import vaex
from sklearn.model_selection import train_test_split
import collections
from tqdm import tqdm

def main():
    
    feats_scp  = "/data1/pengjinghan/tsvad/1c8k/data/feats.scp" 
    target_scp = "/data1/pengjinghan/tsvad/1c8k/target.scp" 
    vector_scp = "/data1/pengjinghan/tsvad/1c8k/xvector/vector/vector.scp" 
    out_dir    = "/data1/pengjinghan/tsvad_train_data/100" 
    os.makedirs(out_dir, exist_ok=True)
    
    """读特征"""
    utt2feat = dict() # mandarin_00001-00000000_00016020
    with open(feats_scp, 'r') as rf:
        for line in tqdm(rf.readlines()):
            utt, path = line.strip().split()
            utt2feat[utt] = path

    """读target标签"""
    utt2target = collections.defaultdict(dict) # utt: mandarin_00001-00000000_00016020
    with open(target_scp, 'r') as rf:
        for line in tqdm(rf.readlines()):
            spk, path = line.strip().split()
            spk_notime, time = spk.split('-')
            utt = spk_notime[:spk_notime.rfind('_')]+"-"+time
            utt2target[utt][spk] = path

    """读vector"""
    spk2vector = dict()
    with open(vector_scp, 'r') as rf:
        for line in tqdm(rf.readlines()):
            spk, path = line.strip().split()
            spk2vector[spk] = path
            

   
    """write csv and hdf5"""
    # assert utt2feat.keys() == utt2target.keys() == utt2vector.keys()

    utts = list(utt2feat.keys())
    utts = utts[:100]
    
    utts_train, utts_val = train_test_split(utts, test_size=0.05, random_state=0, shuffle=False)
    
    # train
    train_csv  = os.path.join(out_dir, "train.csv")
    train_hdf5 = os.path.join(out_dir, "train.hdf5")
    with open(train_csv, 'w') as wf:
        for utt in tqdm(utts_train):
            feat_path = utt2feat[utt]
            line = utt + "\t" + feat_path + "\t"
            # line = feat_path + "\t"
            vector_path_list = []
            for spk, target_path in utt2target[utt].items():
                line += target_path + "\t"
                spk_notime = spk.split('-')[0]
                vector_path = spk2vector[spk_notime]
                vector_path_list.append(vector_path)
            line += vector_path_list[0] + "\t"
            line += vector_path_list[1] + "\n"
            wf.write(line)
            # wf.write(utt2feat[utt] + "\t" + utt2target[utt] + "\t" + utt2vector[utt] + "\n")
    
    os.system("sed -i '{}' {}".format("1i\\utt_id\tfeat_path\ttarget_path1\ttarget_path2\tvector_path1\tvector_path2", train_csv))
    # os.system("sed -i '{}' {}".format("1i\\feat_path\ttarget_path1\ttarget_path2\tvector_path1\tvector_path2", train_csv))
    df = vaex.from_csv(train_csv, sep="\t")
    df.export(train_hdf5)

    # val
    val_csv  = os.path.join(out_dir, "val.csv")
    val_hdf5 = os.path.join(out_dir, "val.hdf5")
    # with open(val_csv, 'w') as wf:
    #     for utt in utts_val:
    #         wf.write(utt2feat[utt] + "\t" + utt2target[utt] + "\t" + utt2vector[utt] + "\n")
    with open(val_csv, 'w') as wf:
        for utt in tqdm(utts_val):
            feat_path = utt2feat[utt]
            line = utt + "\t" + feat_path + "\t"
            # line = feat_path + "\t"
            vector_path_list = []
            for spk, target_path in utt2target[utt].items():
                line += target_path + "\t"
                spk_notime = spk.split('-')[0]
                vector_path = spk2vector[spk_notime]
                vector_path_list.append(vector_path)
            line += vector_path_list[0] + "\t"
            line += vector_path_list[1] + "\n"
            wf.write(line)

    os.system("sed -i '{}' {}".format("1i\\utt_id\tfeat_path\ttarget_path1\ttarget_path2\tvector_path1\tvector_path2", val_csv))
    # os.system("sed -i '{}' {}".format("1i\\feat_path\ttarget_path1\ttarget_path2\tvector_path1\tvector_path2", val_csv))
    df = vaex.from_csv(val_csv, sep="\t")
    df.export(val_hdf5)


if __name__ == '__main__':
    main()
    