#coding=utf-8
# File      :   gen_spk_wav_from_rttm.py
# Time      :   2022/06/09 15:28:08
# Author    :   Jinghan Peng
# Desciption:   根据rttm过滤某一特定说话人的音频

import collections
from decimal import Decimal
import os, sys
from tqdm import tqdm
from pydub import AudioSegment

def main():
    # wav_dir = "/data1/pengjinghan/tsvad_test_data/5vocal/wav"
    # rttm_path = "/data1/pengjinghan/tsvad_test_data/5vocal/data/rttm"
    # out_dir = "/data1/pengjinghan/tsvad_test_data/5vocal/spk_wav"
    
    wav_dir = "/data1/pengjinghan/tsvad_test_data/5vocal/wav"
    rttm_path = "/data1/pengjinghan/tsvad_test_project/label_spk_test/tsvad_output/rttm_0.5_0.5"
    out_dir = "/data1/pengjinghan/tsvad_test_project/label_spk_test/tsvad_output/wav"
    
    
    os.makedirs(out_dir, exist_ok=True)
    
    time_length = 5 # 5秒
    
    utt2wav_path = dict()
    for file in os.listdir(wav_dir):
        file_path = os.path.join(wav_dir, file)
        utt = file.split(".wav")[0]
        utt2wav_path[utt] = file_path
        
    utt2spk_time_list = dict()
    with open(rttm_path, 'r') as rf:
        for line in tqdm(rf.readlines()):
            # SPEAKER 5-5 0 19.824 21.568 <NA> <NA> F2 <NA> <NA>
            line = line.strip().split()
            utt = line[1]
            beg_ms, dur_ms = int(Decimal(line[3])*Decimal("1000")), int(Decimal(line[4])*Decimal("1000"))
            end_ms = beg_ms+dur_ms
            
            spk = line[-3]
            if utt not in  utt2spk_time_list:
                utt2spk_time_list[utt] = collections.defaultdict(list)
            
            utt2spk_time_list[utt][spk].append((beg_ms, end_ms))
    
    
    for utt, spk_time_list in utt2spk_time_list.items():
        print(f" --- {utt} --- ")
        for spk, time_list in spk_time_list.items():
            time_ms = 0
            for beg_ms, end_ms in time_list:
                time_ms += (end_ms-beg_ms)
            print(spk, time_ms/1000)
    
    # return
    
    # 每个utt选第一个说话人进行过滤
    for utt, spk_time_list in utt2spk_time_list.items():
        # print(f" --- {utt} --- ")
        audio = AudioSegment.from_file(utt2wav_path[utt], format='wav')
        # spk_audio = AudioSegment.empty()
        for spk, time_list in spk_time_list.items():
            spk_audio = AudioSegment.empty()
            for beg_ms, end_ms in time_list:
                spk_audio += audio[beg_ms: end_ms]
            
            # spk_audio = spk_audio[:time_length*1000]
            
            out_path = os.path.join(out_dir, f"{utt}_{spk}.wav")
                
            spk_audio.export(out_path, format = 'wav')
            
            # break
    
        
        
if __name__ == '__main__':
    main()

