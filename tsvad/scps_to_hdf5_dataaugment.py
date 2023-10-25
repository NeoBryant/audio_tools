#coding=utf-8
# File      :   scps_to_hdf5.py
# Time      :   2021/08/30 14:13:26
# Author    :   Jinghan Peng
# Desciption:   yb_featur数据增广后的，读取各scp，生成hdf5

import os
from numpy.core.numeric import outer
import vaex
from sklearn.model_selection import train_test_split
import collections
from tqdm import tqdm

def main():

    feats_scp  = "/data/pengjinghan/tsvad/1c8k_ol/fbank_x4aug_chunk/data/tdnn_combined/feats.scp"
    #"/data/pengjinghan/tsvad_finetune_train_data/testset-0315/fbank/data/feats.scp" #"/data/pengjinghan/tsvad/1c8k/feat_aug/data/tdnn_combined/feats.scp" 
    target_scp = "/data/pengjinghan/tsvad/1c8k_ol/target_chunk.scp"
    #"/data/pengjinghan/tsvad_finetune_train_data/testset-0315/data/target_chunk.scp" #"/data/pengjinghan/tsvad/1c8k/target_chunk.scp" 
    vector_scp = "/data/pengjinghan/tsvad/1c8k_ol/xvector/vector/vector.scp"
    #"/data/pengjinghan/tsvad_finetune_train_data/testset-0315/xvector/vector/vector.scp" #"/data/pengjinghan/tsvad/1c8k/xvector/vector/vector.scp" 
    out_dir    = "/data/pengjinghan/tsvad_train_data/speech_data_x4aug_ol/full"
    #"/data/pengjinghan/tsvad_finetune_train_data/testset-0315/train_data" #"/data/pengjinghan/tsvad_train_data/data_augx4" 
    os.makedirs(out_dir, exist_ok=True)
    
    
    """读feat路径"""
    utt2feat = collections.defaultdict(dict) #dict() # mandarin_00001-00000000_00016020(-babble,-music,-noise,-reverb)
    with open(feats_scp, 'r') as rf:
        process_tqdm = tqdm(rf.readlines())
        process_tqdm.set_description(f"Loading feats.scp")
        for line in process_tqdm:
            utt, path = line.strip().split()
            
            if "-babble" in utt or "-music" in utt or "-reverb" in utt or "-noise" in utt:
                raw_utt = utt[:utt.rfind("-")]
            else:
                raw_utt = utt
            utt2feat[raw_utt][utt] = path
        
    feat_utts = set(utt2feat.keys())
        
    """读target路径"""
    utt2target = collections.defaultdict(dict) # utt: mandarin_00001-00000000_00016020
    with open(target_scp, 'r') as rf:
        process_tqdm = tqdm(rf.readlines())
        process_tqdm.set_description(f"Loading target.scp")
        for line in process_tqdm:
            spk, path = line.strip().split()
            spk_notime, time = spk.split('-')
            utt = spk_notime[:spk_notime.rfind('_')]+"-"+time
            utt2target[utt][spk] = path # {'mandarin_06896-00000000_00016020': {'mandarin_06896_F1-00000000_00016020': '/data4/pengjinghan/tsvad/1c8k/target.ark:36'}})
    
    target_utts = set()
    for utt, spk_target in utt2target.items():
        if len(spk_target) == 2:
            target_utts.add(utt)

    """读vector路径"""
    spk2vector = dict()
    with open(vector_scp, 'r') as rf:
        process_tqdm = tqdm(rf.readlines())
        process_tqdm.set_description(f"Loading vector.scp")
        for line in process_tqdm:
            spk, path = line.strip().split()
            spk2vector[spk] = path # {'mandarin_03362_F2': '/data4/pengjinghan/tsvad/1c8k/xvector/vector/vector_save/vector.2.ark:18'}
            
    """write csv and hdf5"""
    # assert utt2feat.keys() == utt2target.keys() == utt2vector.keys()

    # utts = list(utt2feat.keys()) # 以原始spk为划分
    utt_list = list(feat_utts.intersection(target_utts))
    
    # utt_list = utt_list[:10000]
    utts_train, utts_val = train_test_split(utt_list, test_size=0.025, random_state=0, shuffle=False)
    
    # print(len(utts_train), len(utts_val))
    
    """ train """
    train_csv  = os.path.join(out_dir, "train.csv")
    train_hdf5 = os.path.join(out_dir, "train.hdf5")
    with open(train_csv, 'w') as wf:
        process_tqdm = tqdm(utts_train)
        process_tqdm.set_description(f"Train set")
        for raw_utt in process_tqdm:
            for utt, feat_path  in utt2feat[raw_utt].items():
                line = utt + "\t" + feat_path + "\t"
                # line = feat_path + "\t"
                vector_path_list = []
                for spk, target_path in utt2target[raw_utt].items():
                    line += target_path + "\t"
                    spk_notime = spk.split('-')[0]
                    vector_path = spk2vector[spk_notime]
                    vector_path_list.append(vector_path)
                line += vector_path_list[0] + "\t"
                line += vector_path_list[1] + "\n"
                wf.write(line)

    # os.system("sed -i '{}' {}".format("1i\\feat_path\ttarget_path1\ttarget_path2\tvector_path1\tvector_path2", train_csv))    
    os.system("sed -i '{}' {}".format("1i\\utt_id\tfeat_path\ttarget_path1\ttarget_path2\tvector_path1\tvector_path2", train_csv))
    df = vaex.from_csv(train_csv, sep="\t")
    df.export(train_hdf5)
    
    """ val """
    val_csv  = os.path.join(out_dir, "val.csv")
    val_hdf5 = os.path.join(out_dir, "val.hdf5")
    with open(val_csv, 'w') as wf:
        process_tqdm = tqdm(utts_val)
        process_tqdm.set_description(f"Valid set")
        for raw_utt in process_tqdm:
            for utt, feat_path  in utt2feat[raw_utt].items():
                if "-babble" in utt or "-music" in utt or "-reverb" in utt or "-noise" in utt:
                    # 验证集不用数据增广
                    continue

                line = utt + "\t" + feat_path + "\t"
                # line = feat_path + "\t"
                vector_path_list = []
                for spk, target_path in utt2target[raw_utt].items():
                    line += target_path + "\t"
                    spk_notime = spk.split('-')[0]
                    vector_path = spk2vector[spk_notime]
                    vector_path_list.append(vector_path)
                line += vector_path_list[0] + "\t"
                line += vector_path_list[1] + "\n"
                wf.write(line)
    
    # os.system("sed -i '{}' {}".format("1i\\feat_path\ttarget_path1\ttarget_path2\tvector_path1\tvector_path2", val_csv))    
    os.system("sed -i '{}' {}".format("1i\\utt_id\tfeat_path\ttarget_path1\ttarget_path2\tvector_path1\tvector_path2", val_csv))
    df = vaex.from_csv(val_csv, sep="\t")
    df.export(val_hdf5)


if __name__ == '__main__':
    main()
    