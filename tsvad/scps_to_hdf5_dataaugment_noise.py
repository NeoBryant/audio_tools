#coding=utf-8
# File      :   scps_to_hdf5.py
# Time      :   2021/08/30 14:13:26
# Author    :   Jinghan Peng
# Desciption:   yb_featur数据增广后的，读取各scp，生成hdf5

import os
from random import random
from numpy.core.numeric import outer
import vaex
from sklearn.model_selection import train_test_split
import collections
from tqdm import tqdm
import random

def main():
    feats_scp  = "/data1/pengjinghan/tsvad/invalid_sound/wav_chunk/data/feats.scp" 
    target_scp = "/data1/pengjinghan/tsvad/invalid_sound/wav_chunk/data/target.scp" 
    vector_scp = "/data1/pengjinghan/tsvad/1c8k/xvector/vector/vector.scp" 
    out_dir    = "/data1/pengjinghan/tsvad_train_data/unspeech_dataaugment_full" 
    os.makedirs(out_dir, exist_ok=True)
    
    num_target_speaker = 2
    
    """读特征"""
    type2utt = collections.defaultdict(list) # {music:[utt1,utt2],bobao:[],busytone:[]}
    utt2feat = collections.defaultdict(dict) #dict() # mandarin_00001-00000000_00016020(-babble,-music,-noise,-reverb)
    with open(feats_scp, 'r') as rf:
        for line in tqdm(rf.readlines()):
            utt, path = line.strip().split()

            if "-babble" in utt or "-music" in utt or "-reverb" in utt or "-noise" in utt:
                raw_utt = utt[:utt.rfind("-")]
            else:
                raw_utt = utt
                type_ = raw_utt.split('-')[0]
                type2utt[type_].append(raw_utt)
            
            utt2feat[raw_utt][utt] = path
    
    """读target标签"""
    # utt2target = collections.defaultdict(dict) # utt: mandarin_00001-00000000_00016020
    utt2target = dict()
    with open(target_scp, 'r') as rf:
        for line in tqdm(rf.readlines()):
            utt, path = line.strip().split()
            utt2target[utt] = path # {'mandarin_06896-00000000_00016020': '/data4/pengjinghan/tsvad/1c8k/target.ark:36'})
           
    """读vector"""
    spk2vector = dict()
    with open(vector_scp, 'r') as rf:
        for line in tqdm(rf.readlines()):
            spk, path = line.strip().split()
            spk2vector[spk] = path # {'mandarin_03362_F2': '/data4/pengjinghan/tsvad/1c8k/xvector/vector/vector_save/vector.2.ark:18'}

    spk2vector = list(spk2vector.items())
    
   
    """write csv and hdf5"""
    utts_train = list()
    utts_val   = list()
    for type_, sub_utts in type2utt.items():
        sub_utts_train, sub_utts_val = train_test_split(sub_utts, test_size=0.05, random_state=0, shuffle=False)
        utts_train += sub_utts_train
        utts_val   += sub_utts_val
    
    # train
    train_csv  = os.path.join(out_dir, "train.csv")
    train_hdf5 = os.path.join(out_dir, "train.hdf5")
    with open(train_csv, 'w') as wf:
        for raw_utt in tqdm(utts_train):
            for utt, feat_path  in utt2feat[raw_utt].items():                
                line = utt + "\t" + feat_path + "\t" # utt, feat
                
                for i in range(num_target_speaker): # target 
                    target_path = utt2target[raw_utt]
                    line += target_path + "\t"
            
                for i in range(num_target_speaker): # vector
                    rand_index = random.randint(0,len(spk2vector)-1)
                    if i != num_target_speaker-1:
                        line += spk2vector[rand_index][-1] + "\t"
                    else:
                        line += spk2vector[rand_index][-1] + "\n"
                wf.write(line)
                   
    os.system("sed -i '{}' {}".format("1i\\utt_id\tfeat_path\ttarget_path1\ttarget_path2\tvector_path1\tvector_path2", train_csv))
    df = vaex.from_csv(train_csv, sep="\t")
    df.export(train_hdf5)
    
    # val
    val_csv  = os.path.join(out_dir, "val.csv")
    val_hdf5 = os.path.join(out_dir, "val.hdf5")
    with open(val_csv, 'w') as wf:
        for raw_utt in tqdm(utts_val):
            for utt, feat_path  in utt2feat[raw_utt].items():
                line = utt + "\t" + feat_path + "\t" # utt, feat

                for i in range(num_target_speaker): # target 
                    target_path = utt2target[raw_utt]
                    line += target_path + "\t"
            
                for i in range(num_target_speaker): # vector
                    rand_index = random.randint(0,len(spk2vector)-1)
                    if i != num_target_speaker-1:
                        line += spk2vector[rand_index][-1] + "\t"
                    else:
                        line += spk2vector[rand_index][-1] + "\n"
                wf.write(line)
    
    os.system("sed -i '{}' {}".format("1i\\utt_id\tfeat_path\ttarget_path1\ttarget_path2\tvector_path1\tvector_path2", val_csv))
    # os.system("sed -i '{}' {}".format("1i\\feat_path\ttarget_path1\ttarget_path2\tvector_path1\tvector_path2", val_csv))
    df = vaex.from_csv(val_csv, sep="\t")
    df.export(val_hdf5)


if __name__ == '__main__':
    main()
    