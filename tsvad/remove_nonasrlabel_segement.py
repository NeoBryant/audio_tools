#coding=utf-8
# File      :   replace_nonasrlabel_with_silence.py
# Time      :   2021/09/01 19:36:00
# Author    :   Jinghan Peng
# Desciption:   根据asr标注结果，删除无标注段(静音或噪声)，生成新的音频

import os
from pydub import AudioSegment
from multiprocessing import Pool

from tqdm import tqdm
import shutil
import collections
import random

import librosa
import librosa.display

import numpy as np
import matplotlib.pyplot as plt


def replace_nonasrlabel_with_silence(utt, wav_path, aliword_path, out_wav_dir, out_target_wav_dir, out_pics_dir, out_target_path):
    """处理单条音频
    """
    input_audio = AudioSegment.from_file(wav_path)
    dur  = input_audio.duration_seconds # 音频时长,秒
    durms = int(dur*1000) # 毫秒
    spks2time = collections.defaultdict(list)
    vad_bi_time_list = [0 for i in range(durms)] # vad二值序列
    spk2target = dict() # 每个说话人的 target 二值序列

    """读取asr标签"""
    with open(aliword_path, 'r') as rf:
        for line in rf.readlines():
            # print(line)
            line = line.strip().split()
            if len(line) >= 3:
                spk, begms, endms = line[:3]
                begms, endms = int(begms), int(endms)
                if begms == endms:
                    continue
                if spk != 'N':
                    if spk not in spk2target:
                        spk2target[spk] = ['0' for i in range(durms)]

                    for i in range(begms, endms+1):
                        if i < durms: 
                            vad_bi_time_list[i] = 1   # vad
                            spk2target[spk][i]  = '1'  # target，后面写入target.lst文件
                    spks2time[spk].append((begms, endms))

    # assert len(spks) == 2 # 已经全部验证过
    
    """ 二值序列转化为（beg，end）时间对"""
    vad_time_list = list()
    for i in range(len(vad_bi_time_list)):
        if i==0 or vad_bi_time_list[i]!=vad_bi_time_list[i-1]:
            begms = i
        
        if i==len(vad_bi_time_list)-1 or vad_bi_time_list[i]!=vad_bi_time_list[i+1]:
            endms = i
            assert endms > begms
            vad_time_list.append((begms, endms, vad_bi_time_list[i]))
            
    
    """ 保留有效音部分，删除静音部分，保存新生成的音频 """
    out_path = os.path.join(out_wav_dir, f"{utt}.wav")
    output_audio = AudioSegment.empty()
    for begms, endms, isValid in vad_time_list:   
        if isValid:
            sub_audio = input_audio[begms: endms+1]
            output_audio += sub_audio
    output_audio.export(out_path, format='wav')
    
    """ 用nnvad或能量vad再过滤一遍"""
    # To-do
    
    """ 更新target，并保存 """
    # 每毫秒的标签都会存储
    for spk, spk_target_lst in spk2target.items():
        spk_target_lst_ms = [0 for i in range((sum(vad_bi_time_list)))] # 记录每毫秒的标签
        j = 0
        for i in range(len(vad_bi_time_list)):
            if vad_bi_time_list[i] == 1:
                spk_target_lst_ms[j] = int(spk_target_lst[i])
                j += 1
        spk_target_lst_frame = ['0' for i in range(len(spk_target_lst_ms)//10)] # 记录每帧的标签
        for i in range(len(spk_target_lst_frame)):
            if sum(spk_target_lst_ms[i*10:(i+1)*10]) >= 5:
                spk_target_lst_frame[i] = '1'
            else:
                spk_target_lst_frame[i] = '0'
        spk2target[spk] = spk_target_lst_frame
        
    
    with open(out_target_path, 'a') as wf:
        for spk, values in spk2target.items():
            wf.write(f"{utt}_{spk} "+" ".join(values)+"\n")
    
    """ 分别保存目标说话人的音频 """
    for spk, time_list in spks2time.items():
        out_target_wav_path = os.path.join(out_target_wav_dir, f"{utt}_{spk}.wav")
        output_audio = AudioSegment.empty()
        for begms, endms in time_list:
            output_audio += input_audio[begms: endms]
        output_audio.export(out_target_wav_path, format='wav')        

    """画图"""
    save_pics = False
    if save_pics:
        try:
            audio, sample_rate = librosa.load(path=out_path, sr=8000, mono=True)
            audio_dur = librosa.get_duration(audio, sr=sample_rate) # 音频时长
            plt.figure(figsize=(40, 7))
            for index, (spk, values) in enumerate(spk2target.items()):
                if index ==  0:
                    # spk1 = [int(i) for i in values]
                    spk1 = [0 for i in range(len(values)*10)]
                    for i in range(len(values)):
                        for j in range(10):
                            spk1[i*10+j] = int(values[i])
                else:
                    # spk2 = [-1*int(i) for i in values]
                    spk2 = [0 for i in range(len(values)*10)]
                    for i in range(len(values)):
                        for j in range(10):
                            spk2[i*10+j] = -1*int(values[i])
                    
                    x = np.arange(0, len(values)/100, 0.001)
                    if len(x) > len(spk2):
                        x = x[:len(spk2)-len(x)]
                    elif len(x) < len(spk2):
                        x = x[:len(x)-len(spk2)]
                    
            #音频波形图
            ax1 = plt.subplot(2,1,1)
            ax1.set_ylabel('Pred and Label')
            ax1.plot(np.arange(audio.size) / sample_rate, audio, 'grey')
            ax1.set_xlim([0, int(audio_dur) + 1])
            ax1.tick_params(axis='y', labelcolor='grey')
            ax1.set_ylabel('Signal')
            ax1.set_ylim([-1, 1])
            ax1.set_title('Label')
            #标签
            ax2 = ax1.twinx()
            ax2.plot(x, spk1, 'r', label='spk1', linewidth=1)
            ax2.plot(x, spk2, 'b', label='spk2', linewidth=1)
            ax2.tick_params(axis='y', labelcolor='r')
            ax2.set_ylim([-1.1, 1.1])
            #保存
            plt.savefig(os.path.join(out_pics_dir, f"{utt}.png"))
            plt.close()
        except Exception as e:
            print(e)
            raise e

def work(sublines, out_wav_dir, out_target_wav_dir, out_pics_dir, out_target_path, process_id):
    for utt, wav_path, aliword_path in tqdm(sublines):
        replace_nonasrlabel_with_silence(utt, 
                                        wav_path, 
                                        aliword_path, 
                                        out_wav_dir, 
                                        out_target_wav_dir, 
                                        out_pics_dir, 
                                        out_target_path)


def try_work(sublines, out_wav_dir, out_target_wav_dir, out_pics_dir, out_target_path, process_id):
    try:
        work(sublines, out_wav_dir, out_target_wav_dir, out_pics_dir, out_target_path, process_id)
        print(f"{process_id} thread Done")
    except Exception as e:
        print(e)
        raise e

def prepare_dir(dir_):
    if os.path.isdir(dir_):
        shutil.rmtree(dir_)
    os.makedirs(dir_)

def main():
    threads = 42
    
    # 输入路径
    wavscp_path = "/data4/pengjinghan/tsvad/1c8k/wav_1c8k_2spk.scp" # 总数 34336
    aliword_dir = "/data4/pengjinghan/tsvad/raw/asr" # 对应音频的asr标注文件所在目录路径

    # 输出路径
    out_wav_dir = "/data4/pengjinghan/tsvad/1c8k/wav_remove_silence" 
    out_target_wav_dir = "/data4/pengjinghan/tsvad/1c8k/wav_split_target_spk"
    out_target_dir = "/data4/pengjinghan/tsvad/1c8k/target_split"
    out_target_sum_path = "/data4/pengjinghan/tsvad/1c8k/target.lst"
    out_pics_dir = "/data4/pengjinghan/tsvad/1c8k/pics"

    # 创建目录
    prepare_dir(out_target_dir)
    # prepare_dir(out_pics_dir)
    prepare_dir(out_target_wav_dir)
    prepare_dir(out_wav_dir)

    """读取wav.scp"""
    input_lines = list()
    with open(wavscp_path, 'r') as rf:
        lines = rf.readlines()
        lines.sort()
        # random.seed(1)
        # random.shuffle(lines)
        
        for index in range(len(lines)):
            line = lines[index]
            wav_path = line.strip()
            utt = wav_path.split("/")[-1].split(".wav")[0]
            aliword_path = os.path.join(aliword_dir, f"{utt}.txt")

            input_lines.append((utt, wav_path, aliword_path))
            
            if index >= 9999:
                break
    
    """多进程计算"""
    threads = min(len(input_lines), threads)
    step = len(input_lines)//threads + 1
    print(f"Process {step} wavs for each thread, total {threads} thread")
    pool = Pool(threads)
    for i in range(threads):
        sublines = input_lines[step*i:step*(i+1)]
        out_target_path = os.path.join(out_target_dir, f"target.{i}.split")
        pool.apply_async(try_work, (sublines, out_wav_dir, out_target_wav_dir, out_pics_dir, out_target_path, i))
    pool.close()
    pool.join()


    """汇总target_lst"""
    with open(out_target_sum_path, 'w') as wf:
        for target_fn in os.listdir(out_target_dir):
            with open(os.path.join(out_target_dir, target_fn), 'r') as rf:
                lines = rf.readlines()
                wf.writelines(lines)


if __name__ == '__main__':
    main()
    