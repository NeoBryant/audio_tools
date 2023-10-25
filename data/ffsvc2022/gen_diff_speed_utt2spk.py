#coding=utf-8
# File      :   gen_diff_speed_utt2spk.py
# Time      :   2022/06/28 16:00:06
# Author    :   Jinghan Peng
# Desciption:   配合for_vpr_v2中使用spk_mean, 将不同调速的utt的spk设为一个

import os, sys

def main():
    wav_dir = "/data2/pengjinghan/FFSVC_data/Dev_Test_FFSVC2022/dev/wav_sp"
    raw_utt2spk = "/data2/pengjinghan/FFSVC_data/Dev_Test_FFSVC2022/dev/data_list/enroll/utt2spk"
    out_dir = "/data2/pengjinghan/FFSVC_data/Dev_Test_FFSVC2022/dev/data_list_sp/enroll"
    
    
    raw2spk = dict()
    raw2utt = dict()
    with open(raw_utt2spk, 'r') as rf:
        for line in rf.readlines():
            utt, spk = line.strip().split()
            raw_utt = utt.split('-')[-1]
            raw2utt[raw_utt] = utt
            raw2spk[raw_utt] = spk
    
    # wav.scp
    utt_list = list()
    wav_scp_path = os.path.join(out_dir, "wav.scp")
    with open(wav_scp_path, 'w') as wf:
        for wav_file in os.listdir(wav_dir):
            raw_utt = wav_file.split('-')[0]+".wav"
            spk = raw2spk[raw_utt]
            wav_path = os.path.join(wav_dir, wav_file)
            wf.write(f"{spk}-{wav_file} {wav_path}\n")
            utt_list.append(wav_file)
            
     
    # utt2spk
    utt2spk_path = os.path.join(out_dir, "utt2spk")
    utt_list.sort()
    with open(utt2spk_path, 'w') as wf:
        for utt in utt_list:
            raw_utt = utt.split('-')[0]+".wav"
            spk = raw2spk[raw_utt]
            new_spk = raw2utt[raw_utt]
            wf.write(f"{spk}-{utt} {new_spk}\n")

    # spk2utt
    spk2utt_path = os.path.join(out_dir, "spk2utt")
    cmd = f"./../../utils/utt2spk_to_spk2utt.pl {utt2spk_path} > {spk2utt_path}"
    os.system(cmd)

if __name__ == '__main__':
    main()

