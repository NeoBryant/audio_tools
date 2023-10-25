#coding=utf-8
# File      :   diar_plot.py
# Time      :   2021/09/10 17:06:14
# Author    :   Jinghan Peng
# Desciption:   根据音频和target绘制不同说话人波形标记图，只针对切片后的chunk进行绘图（由于命名规则限定）

import os
from pydub import AudioSegment

from tqdm import tqdm
import shutil
import collections
import random

import librosa
import librosa.display

import numpy as np
import matplotlib.pyplot as plt
import kaldiio

def main():
    ## chunk
    wav_dir = "/data/pengjinghan/tsvad/1c8k_ol/wav_chunk"
    #"/data/pengjinghan/tsvad_finetune_train_data/testset-0315/wav_chunk"
    #"/data4/pengjinghan/tsvad/1c8k/wav_replace_silence_chunk" # chunk后的音频路径
    targetlst_path = "/data/pengjinghan/tsvad/1c8k_ol/target_chunk.scp"
    #"/data/pengjinghan/tsvad_finetune_train_data/testset-0315/data/target_chunk.scp"
    #"/data4/pengjinghan/tsvad/1c8k/target_chunk.scp" # target_chunk.scp路径
    out_pics_dir = "/data/pengjinghan/tsvad/1c8k_ol/pic_chunk"
    #"/data/pengjinghan/tsvad_finetune_train_data/testset-0315/pic_chunk"
    #"/data4/pengjinghan/tsvad/1c8k/pics_chunk" # 输出图片目录路径
    
    os.makedirs(out_pics_dir, exist_ok=True)
    
    
    utt2target = collections.defaultdict(dict)
    with open(targetlst_path, 'r') as rf:
        for index, (line) in tqdm(enumerate(rf)):
            spk, target_path = line.strip().split()
            tmp = spk.split('-')[0]
            utt = tmp[:tmp.rfind('_')]+"-"+spk.split('-')[-1]
            
            target = kaldiio.load_mat(target_path)
            
            utt2target[utt][spk] = target.flatten().tolist()

            if index >= 200:
                break
            

    files = os.listdir(wav_dir)
    files.sort()
    for wav_file in tqdm(files):
        utt = wav_file.split(".wav")[0]
        if utt not in utt2target:
            continue
        
        spk2target = utt2target[utt]
        
        wav_path = os.path.join(wav_dir, wav_file)
        audio, sample_rate = librosa.load(path=wav_path, sr=8000, mono=True)
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
    
        # return


if __name__ == '__main__':
    main()
    