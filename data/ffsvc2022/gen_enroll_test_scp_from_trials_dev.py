#coding=utf-8
# File      :   gen_enroll_test_scp_from_trials_dev.py
# Time      :   2022/05/19 16:25:37
# Author    :   Jinghan Peng
# Desciption:   根据trials_eval生成开发集的注册集和验证集的表单文件

import collections
import os, sys
from tqdm import tqdm

def write_scp(out_dir, utt2spk, utt2wav_path, utt_list):
    os.makedirs(out_dir, exist_ok=True)
    wavscp_path = os.path.join(out_dir, "wav.scp")
    utt2spk_path = os.path.join(out_dir, "utt2spk")
    spk2utt_path = os.path.join(out_dir, "spk2utt")
    
    utt_list.sort()
    
    with open(wavscp_path, 'w') as wf1, open(utt2spk_path, 'w') as wf2:
        for utt in tqdm(utt_list):
            # ffmpeg -v 8 -i /data3/pengjinghan/cnsrc_backend_test/data/test_data/eval/enroll/id00800-enroll.flac -ar 16000 -f wav -acodec pcm_s16le -|
            wf1.write(f"{utt2spk[utt]}-{utt} {utt2wav_path[utt]}\n")
            wf2.write(f"{utt2spk[utt]}-{utt} {utt2spk[utt]}\n")

    cmd = f"./../../utils/utt2spk_to_spk2utt.pl {utt2spk_path} > {spk2utt_path}"
    os.system(cmd)


def main():
    dev_meta_list_path = "/data2/pengjinghan/FFSVC_data/Dev_Test_FFSVC2022/dev_meta_list"
    trials_dev_keys_path = "/data2/pengjinghan/FFSVC_data/Dev_Test_FFSVC2022/trials_dev_keys"
    wav_dir = "/data2/pengjinghan/FFSVC_data/Dev_Test_FFSVC2022/dev/wav"
    out_dir = "/data2/pengjinghan/FFSVC_data/Dev_Test_FFSVC2022/dev/data_list"
    
    # read wav path
    utt2wav_path = dict()
    for wav_name in os.listdir(wav_dir):
        wav_path = os.path.join(wav_dir, wav_name)        
        utt2wav_path[wav_name] = wav_path
    
    # read dev_meta_list
    spk_set = set()
    utt2spk = dict()
    with open(dev_meta_list_path, 'r') as rf:
        for line in tqdm(rf.readlines()[1:]):
            Original_Name, FFSVC2022_Name = line.strip().split()
            FFSVC2022_Name = FFSVC2022_Name+".wav"
            # T0344_344I1M_1_0307_normal
            spk = Original_Name.split('_')[0][1:]
            
            utt2spk[FFSVC2022_Name] = spk
            if spk not in spk_set:
                spk_set.add(spk)
    
    
    print(f"{len(spk_set)} spks in dev_meta_list")
    print(f"{len(utt2spk)} utts in dev_meta_list")
    # return

    # read trials_dev_keys
    enroll_set = set()
    test_set = set() 
    with open(trials_dev_keys_path, 'r') as rf, open(os.path.join(out_dir, "trials"), 'w') as wf:
        for line in tqdm(rf.readlines()):
            label, enroll, test = line.strip().split()
            if enroll not in enroll_set:
                enroll_set.add(enroll)
            if test not in test_set:
                test_set.add(test)
    
            if label == "1":
                wf.write(f"{utt2spk[enroll]}-{enroll} {utt2spk[test]}-{test} target\n")
            else:
                wf.write(f"{utt2spk[enroll]}-{enroll} {utt2spk[test]}-{test} nontarget\n")


    # write 
    ## enroll
    enroll_out_dir = os.path.join(out_dir, "enroll")
    enroll_set = list(enroll_set)
    print(f"{len(enroll_set)} enroll utts")
    write_scp(enroll_out_dir, utt2spk, utt2wav_path, enroll_set)
    
    ## test
    test_out_dir = os.path.join(out_dir, "test")
    test_set = list(test_set)
    print(f"{len(test_set)} test utts")
    write_scp(test_out_dir, utt2spk, utt2wav_path, test_set)


if __name__ == '__main__':
    main()

