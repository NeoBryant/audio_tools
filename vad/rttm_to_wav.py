#coding=utf-8
# File      :   rttm2wav.py
# Time      :   2021/09/08 09:46:53
# Author    :   Jinghan Peng
# Desciption:   读取rttm，将wav音频进行切割再拼接，生成有效音和无效音两部分音频

import os
from pydub import AudioSegment
from decimal import Decimal
import collections

from tqdm import tqdm
from multiprocessing import Pool

from argparse import ArgumentParser

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--wav_dir", type=str, help="path to dir of wavs", 
                        default="")
    parser.add_argument("--rttm_path", type=str, help="path to rttm file", 
                        default="")
    parser.add_argument("--out_dir", type=str, help="path of dir to save wavs", 
                        default="")
    parser.add_argument("--num_process", type=int, default=4)
    parser.add_argument("--save_method", type=str, default="both", help="both | speech")
    
    args = parser.parse_args()
    return args

def gen_wav(utt, wav_path, time_pair_list, out_dir, save_method):
    """根据给定音频的路径及其有效时间戳序列，生成新的音频

    Args:
        utt (str): utt 
        wav_path (str): the path of the wav
        time_pair_list (list): list of time pair
        out_dir (list): the path of dir to save wavs
        save_method (str): the method to output wavs
    """
    audio = AudioSegment.from_file(wav_path, format='wav')
    
    if save_method == "both":
        audio_dict = dict()
        for begms, endms, index in time_pair_list:
            if index not in audio_dict.keys():
                audio_dict[index] = AudioSegment.empty()
            audio_dict[index] += audio[begms: endms]
            # audio_dict[index] += AudioSegment.silent(duration=10000, frame_rate=8000)
        for key, val in audio_dict.items():
            out_path = os.path.join(out_dir, f"{utt}_{key}.wav")
            val.export(out_path, format = 'wav')
            
    elif save_method == "speech":
        output_audio = AudioSegment.empty()
        for begms, endms, index in time_pair_list:
            if index == "1":
                output_audio += audio[begms: endms]
        
        out_path = os.path.join(out_dir, f"{utt}.wav")
        output_audio.export(out_path, format = 'wav')

def work(sublines, process_id, utt2path, out_dir, save_method):
    """根据rttm结果剪切音频并保存"""    
    process_tqdm = tqdm(sublines)
    process_tqdm.set_description(f"Process {process_id}")
    for utt, time_pair_list in process_tqdm:
        try:
            wav_path = utt2path[utt]
            gen_wav(utt, wav_path, time_pair_list, out_dir, save_method)
        except Exception as e:
            print(e)

def try_work(sublines, process_id, utt2path, out_dir, save_method):
    try:
        work(sublines, process_id, utt2path, out_dir, save_method)
    except Exception as e:
        print(e)
        raise e

def rttm2wav(wav_dir, rttm_path, out_dir, threads=1, save_method="both"):
    """将音频有效音片段切割再合并
    args:
        wav_dir (str):  音频所在目录路径
        rttm_path (str): rttm文件路径
        out_dir (str):  生成新音频保存路径
    """
    os.makedirs(out_dir, exist_ok=True)
    
    """保存utt和音频路径"""
    utt2path = dict() # utt->音频路径
    if os.path.isdir(wav_dir):
        for r, _, fs in os.walk(wav_dir):
            for f in fs:
                if f.endswith('.wav'):
                    utt = f.split('.wav')[0]
                    utt2path[utt] = os.path.join(r, f)
    elif os.path.isfile(wav_dir):
        with open(wav_dir, 'r') as rf:
            for line in rf.readlines():
                utt, wav_path = line.strip().split()
                utt2path[utt] = wav_path
    
    """读取rttm，保存时间序列对"""
    utt2refs = collections.defaultdict(list) # utt->list((begms, endms, str(index)),...)
    with open(rttm_path, 'r') as rf: # 读取rttm
        for line in rf:
            line  = line.strip().split()
            utt   = line[1]
            begms = int(Decimal(line[3]) * Decimal('1000'))
            endms = begms + int(Decimal(line[4]) * Decimal('1000'))
            index = line[-3] # 类型，1->有效音，0->无效音
            utt2refs[utt].append((begms, endms, str(index)))
                    
    """多进程计算"""
    lines = list(utt2refs.items())
        
    step = len(lines)//threads + 1
    pool = Pool(threads)
    for i in range(threads):
        sublines = lines[step*i:step*(i+1)]
        pool.apply_async(try_work, (sublines, i, utt2path, out_dir, save_method))
    pool.close()
    pool.join()
    

def main(args):
    rttm2wav(args.wav_dir, args.rttm_path, args.out_dir, args.num_process, args.save_method)

if __name__ == '__main__':
    args = parse_args()
    main(args)
   
