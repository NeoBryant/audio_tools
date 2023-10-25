#coding=utf-8
# File      :   combine_csv.py
# Time      :   2022/01/24 14:41:44
# Author    :   Jinghan Peng
# Desciption:   根据给定rttm时间戳文件，生成音频和对应target

"""
todo: 增加重叠音频段
"""

import collections
from decimal import Decimal
import enum
import os, sys
from tqdm import tqdm
import random 
import numpy as np
from kaldiio import WriteHelper

from pydub import AudioSegment

def main():
    # 输入
    in_paths = ["/data/pengjinghan/tsvad_test_project/20220121train_20220125test/testset-0315/cluster_postprocess/rttm",
                "/data/pengjinghan/tsvad_test_project/20220121train_20220125test/jz/cluster_postprocess/rttm",
                "/data/pengjinghan/tsvad_test_project/20220121train_20220125test/p1/cluster_postprocess/rttm",
                "/data/pengjinghan/tsvad_test_project/20220121train_20220125test/jz_p2/cluster_postprocess/rttm"]
    
    wavscp_paths = ["/data/pengjinghan/tsvad_test_project/20220121train_20220125test/testset-0315/nnvad/data/wav.scp",
                    "/data/pengjinghan/tsvad_test_project/20220121train_20220125test/jz/nnvad/data/wav.scp",
                    "/data/pengjinghan/tsvad_test_project/20220121train_20220125test/p1/nnvad/data/wav.scp",
                    "/data/pengjinghan/tsvad_test_project/20220121train_20220125test/jz_p2/nnvad/data/wav.scp"]
    
    
    out_dir = "/data/pengjinghan/tsvad_finetune_train_data/20220125_x4_testdataset"
    
    # 
    out_wav_dir = os.path.join(out_dir, 'wav') # 保存音频 
    out_target_speaker_wav_dir = os.path.join(out_dir, 'wav_split_target_spk') # 保存目标说话人音频 
    out_data_dir = os.path.join(out_dir, 'data') # 保存target
    os.makedirs(out_wav_dir, exist_ok=True)
    os.makedirs(out_target_speaker_wav_dir, exist_ok=True)
    os.makedirs(out_data_dir, exist_ok=True)
    
    
    threshold_dur = 5 # 每个说话人的时长阈值
    target_speaker_num = 2 # 目标说话人数量
    
    num_target_sentence = 1000 # 语音句子数量
    
    min_silence_durms = 100 # 最短静音段时长，单位：毫秒
    max_silence_durms = 1000 # 最长静音段时长，单位：毫秒
    
    utt2spk_to_timestamp = dict() # 音频的说话人的时间戳
    utt2spk_to_dur       = dict() # 音频说说话人的时长
    
    """read rttm"""
    for in_path in in_paths:
        with open(in_path, 'r') as rf:
            for line in tqdm(rf.readlines()):
                _, utt, _, begs, durs, _, _, spk, _, _ = line.strip().split()
                
                begs = Decimal(begs)
                durs = Decimal(durs)
                
                # 时间戳
                if utt not in utt2spk_to_timestamp:
                    utt2spk_to_timestamp[utt] = collections.defaultdict(list) #{spk: list()} #[spk] = collections.defaultdict(list)            
                utt2spk_to_timestamp[utt][spk].append((begs, durs))
            
                # 时长
                if utt not in utt2spk_to_dur:
                    utt2spk_to_dur[utt] = dict()
                
                if spk not in utt2spk_to_dur[utt]:
                    utt2spk_to_dur[utt][spk] = durs
                else:
                    utt2spk_to_dur[utt][spk] += durs
            
        
    """read wav.scp"""
    utt2wav = dict()
    for wavscp_path in wavscp_paths:
        with open(wavscp_path, 'r') as rf:
            for line in rf.readlines():
                utt, wav_path = line.strip().split()
                utt2wav[utt] = wav_path
            
    """ process """
    out_target_path = os.path.join(out_data_dir, "target")
    scp_save = f"ark,scp:{out_target_path}.ark,{out_target_path}.scp"
    with WriteHelper(scp_save) as writer:
        for utt in tqdm(utt2spk_to_timestamp.keys()):
            spk_to_dur = list(utt2spk_to_dur[utt].items())
            spk_to_dur.sort(key=lambda x:x[1], reverse=True) # 按说话人时长降序排序
            
            """ 过滤说话人时长太短的音频 """
            if len(spk_to_dur) < target_speaker_num: # 去掉说话人数量少于目标说话人数量的utt
                continue
            elif spk_to_dur[1][1] < Decimal(str(threshold_dur)): # 去掉目标说话人时长最多的两个说话人时长小于5秒的音频
                continue
            
            spk_to_dur = spk_to_dur[:target_speaker_num]
            
            """ 获取时间戳 """
            spk_to_timestamp = utt2spk_to_timestamp[utt]
            target_spk_to_timestamp = list() # 每个目标说话人的时间戳
            for spk, _ in spk_to_dur:
                target_spk_to_timestamp.append(spk_to_timestamp[spk])

            """ 读取音频 """
            wav_path = utt2wav[utt]
            audio = AudioSegment.from_file(wav_path, format='wav') # 读取音频
            frames_per_second = audio.frame_rate # 采样率
            
            """ 保存说话人音频 """
            for spk_id, timestamp in enumerate(target_spk_to_timestamp):
                out_spk_audio = AudioSegment.empty()
                for sentence_begs, sentence_durs in timestamp:
                    sentence_begms = int(sentence_begs*1000)
                    sentnce_endms  = sentence_begms + int(sentence_durs*1000)
                    sentence_audio = audio[sentence_begms : sentnce_endms]
                    out_spk_audio += sentence_audio

                out_spk_wav_path = os.path.join(out_target_speaker_wav_dir, f"{utt}_{spk_id}.wav")
                out_spk_audio.export(out_spk_wav_path, format='wav')
        
            """ 生成模拟音频（合并所有目标说话人人声为一个utt）"""
            target_ms_list = [[] for i in range(target_speaker_num)] # target0/1标签以ms为单位
            out_audio = AudioSegment.empty() # 输出音频
            
            for i in range(num_target_sentence):
                # silence 
                isInsertSilence = random.choice([True, False]) # 是否插入静音段落
                if isInsertSilence:
                    silence_durms = random.randint(min_silence_durms, max_silence_durms) # 1s~10s静音时间(秒为最小单位)
                    silence_audio = AudioSegment.silent(duration=silence_durms, frame_rate=frames_per_second)
                    out_audio += silence_audio
                    for j in range(target_speaker_num):
                        target_ms_list[j] += [0 for k in range(silence_durms)] # target
                
                # speaker speech
                sentence_spk = i%target_speaker_num  # 轮流选择说话人
                sentence_id = random.randint(0, len(target_spk_to_timestamp[sentence_spk])-1)
                sentence_begs, sentence_durs = target_spk_to_timestamp[sentence_spk][sentence_id]
                sentence_begms = int(sentence_begs*1000)
                sentnce_endms  = sentence_begms + int(sentence_durs*1000)
                sentence_audio = audio[sentence_begms : sentnce_endms]
                out_audio += sentence_audio
                
                # target
                for j in range(target_speaker_num):
                    if j == sentence_spk:
                        target_ms_list[j] += [1 for k in range(int(sentence_durs*1000))]
                    else:
                        target_ms_list[j] += [0 for k in range(int(sentence_durs*1000))]
                
            """ 保存target标签 """
            ## 将ms级标签转化为帧级标签
            durframe = len(target_ms_list[0]) // 10 # 帧数
            for spk_id, target_ms in enumerate(target_ms_list):
                target_frame = np.zeros((1, durframe), dtype='float32')
                # 毫秒标签->帧级标签
                for i in range(durframe):
                    if sum(target_ms[i*10:(i+1)*10]) > 5:
                        target_frame[0][i] = 1
                writer(f"{utt}_{spk_id}", target_frame)   
            
            """ 保存模拟生成音频 """
            out_wav_path = os.path.join(out_wav_dir, f"{utt}.wav")
            out_audio.export(out_wav_path, format='wav')
            # print(f"Save at: {out_wav_path}")
            # return

if __name__ == '__main__':
    main()
    