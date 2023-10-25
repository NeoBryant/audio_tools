#coding=utf-8
# File      :   gen_enroll_test_scp_from_trials_eval.py
# Time      :   2022/05/19 15:54:02
# Author    :   Jinghan Peng
# Desciption:   根据trials_eval生成测试集的注册集和验证集的表单文件

import os, sys
from tqdm import tqdm

def write_scp(out_dir, utt_list, utt2wav_path):
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "wav.scp")
    
    utt_list.sort()
    with open(out_path, 'w') as wf:
        for utt in tqdm(utt_list):
            wf.write(f"{utt} {utt2wav_path[utt]}\n")
    
    cmd = f"python ../../utils/wavscp_to_utt2spk.py --wavscp_path {out_path} --output_dir {out_dir} --split_char '-'" 
    os.system(cmd)

def main():
    trials_eval_path = "/data2/pengjinghan/FFSVC_data/Dev_Test_FFSVC2022/trials_eval"
    wav_dir = "/data2/pengjinghan/FFSVC_data/Dev_Test_FFSVC2022/eval/wav"
    out_dir = "/data2/pengjinghan/FFSVC_data/Dev_Test_FFSVC2022/eval/data_list"
    
    
    # read wav paths
    utt2wav_path = dict()
    for wav_name in os.listdir(wav_dir):
        wav_path = os.path.join(wav_dir, wav_name)        
        utt2wav_path[wav_name] = wav_path
        
    # read trials
    enroll_set = set()
    test_set = set()
    with open(trials_eval_path, 'r') as rf:
        for line in tqdm(rf.readlines()):
            enroll, test = line.strip().split()
            if enroll not in enroll_set:
                enroll_set.add(enroll)
            if test not in test_set:
                test_set.add(test)
    
    # write
    ## enroll 
    enroll_out_dir = os.path.join(out_dir, "enroll")
    enroll_set = list(enroll_set)
    write_scp(enroll_out_dir, enroll_set, utt2wav_path)
    
    ## test 
    test_out_dir = os.path.join(out_dir, "test")
    test_set = list(test_set)
    write_scp(test_out_dir, test_set, utt2wav_path)
    
    print("Done!")
    

if __name__ == '__main__':
    main()

