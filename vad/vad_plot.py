#coding=utf-8
# File      :   show_plot.py
# Time      :   2021/08/13 14:33:43
# Author    :   Jinghan Peng
# Desciption:   将音频波形图、及其预测结果/标注答案保存为图片

import os, sys
import collections

import numpy as np
import matplotlib.pyplot as plt

import librosa
import librosa.display

from decimal import Decimal

from subprocess import *
from multiprocessing import Pool

import argparse

def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument("--wavs_dir", 
                        type=str, #required=True,
                        default="/data1/pengjinghan/test_data/nnvad标注已完成20210806/testset-0315/data/rttm_gt")
    parser.add_argument("--groundtruth_dir", 
                        type=str,
                        default="/data1/pengjinghan/test_data/nnvad标注已完成20210806/testset-0315/data/rttm_mab") 
    parser.add_argument("--predicted_dir", 
                        type=str, #required=True,
                        default="/data1/pengjinghan/test_projects/8k_0725/testset-0315/results/rttm_smoothed_new")
    parser.add_argument("--out_dir", 
                        type=str, #required=True,
                        default="/data1/pengjinghan/test_projects/8k_0725/testset-0315/results/eval_new")
    parser.add_argument("--num_workers", 
                        type=int, 
                        default=20)

    args = parser.parse_args()
    return args


def get_timelist(rttm_list, audio_dur, pg):
    """根据单个utt的rttm序列，生成时间序列推理结果"""
    y = np.zeros(int(audio_dur*1000))
    for start, duration, typ in rttm_list:
        start, duration = int(Decimal(start)*1000), int(Decimal(duration)*1000)
        y[start:start+duration] = int(typ) * pg

    return y

def get_rttmlist(rttm_file_path):
    """读取rttm文件，返回utt->list(开始时间，持续时间，是否为有效音)"""
    utt2rttm_list = collections.defaultdict(list) # key:utt, value:list(starttime, durationtime, type)
    with open(rttm_file_path, 'r') as file:
        for line in file.readlines():
            _, uttid, _, start, duration, _, _, typ, _, _ = line.strip('\n').split(' ')
            utt2rttm_list[uttid].append([start, duration, typ])
    return utt2rttm_list

def draw_plot(wavs, predicted, groundtruth, audio_files, out_dir):
    for index, (wav) in enumerate(wavs):
        print("plot", wav)
        
        audio, sample_rate = librosa.load(path=audio_files[wav], sr=8000, mono=True)
        audio_dur = librosa.get_duration(audio, sr=sample_rate) # 音频时长
        
        pred = get_timelist(predicted[wav], audio_dur, 1)
        gt   = get_timelist(groundtruth[wav], audio_dur, -1)
        x    = np.arange(0, audio_dur, 0.001)
        # assert pred.shape == gt.shape
        
        plt.figure(figsize=(40, 7))

        """音频波形图"""
        ax1 = plt.subplot(2,1,1)
        ax1.set_ylabel('Pred and Label')
        ax1.plot(np.arange(audio.size) / sample_rate, audio, 'grey')
        ax1.set_xlim([0, int(audio_dur) + 1])
        ax1.tick_params(axis='y', labelcolor='grey')
        ax1.set_ylabel('Signal')
        ax1.set_ylim([-1, 1])
        ax1.set_title('Pred and Label')

        """推理结果和标签"""
        ax2 = ax1.twinx()
        ax2.plot(x, pred, 'r', label='pred', linewidth=1)
        ax2.plot(x, gt, 'b', label='label', linewidth=1)
        ax2.tick_params(axis='y', labelcolor='r')
        ax2.set_ylim([-1.1, 1.1])

        """fbank频谱图"""
        ax3 = plt.subplot(2,1,2)
        S = librosa.feature.melspectrogram(y=audio, sr=sample_rate, n_mels=64, fmax=8000)
        S_dB = librosa.power_to_db(S, ref=np.max)
        librosa.display.specshow(S_dB, x_axis='time', y_axis='mel', sr=sample_rate, fmax=8000)
        ax3.set_title('Mel-frequency spectrogram')
        ax3.grid()

        plt.savefig(os.path.join(out_dir, "{}.png".format(wav)))
        plt.close()
        

def main(args):
    """参数"""
    wavs_dir        = args.wavs_dir
    predicted_dir   = args.predicted_dir
    groundtruth_dir = args.groundtruth_dir
    out_dir         = args.out_dir
    threads         = args.num_workers


    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    
    predicted = get_rttmlist(predicted_dir)
    print("Get predicted rttm...Done!")
    groundtruth = get_rttmlist(groundtruth_dir)
    print("Get groundtruth rttm...Done")
    
    audio_files = dict()
    for root, dirs, files in os.walk(wavs_dir):
        for fn in files:
            if fn.endswith(".wav"):
                audio_files[fn.split('.wav')[0]] = os.path.join(root, fn)
    # assert wavs == set(groundtruth) == set(predicted) # 判断音频是否匹配
    
    lines = audio_files.keys() & groundtruth.keys() & predicted.keys()
    lines = list(lines)
    lines.sort()
    
    threads = min(threads, len(lines))
    step = len(lines)//threads + 1
    print("Sum {} wavs of each process".format(step))
    pool = Pool(threads)
    for i in range(threads):
        sub_lines = lines[step*i:step*(i+1)]
        pool.apply_async(draw_plot, (sub_lines, predicted, groundtruth, audio_files, out_dir))
    pool.close()
    pool.join()


if __name__ == "__main__":
    args = parse_opt()
    main(args)
