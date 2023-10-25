#coding=utf-8
# File      :   gen_online_data_manifest.py
# Time      :   2022/04/18 19:25:02
# Author    :   Jinghan Peng
# Desciption:   读取wav.scp，并根据chunksize转化为online的表单文件

import argparse
import os, sys
import random
import math
# import kaldiio
# from kaldiio import WriteHelper
from multiprocessing import Pool
from tqdm import tqdm
import json
import collections
from pydub import AudioSegment

def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, help="the dir of wav.scp and utt2spk", default="/data3/pengjinghan/exp/data/cnsrc2022/data_list")
    parser.add_argument("--save_dir", type=str, default="/data3/pengjinghan/exp/data/cnsrc2022/data_list/data_cut")
    
    parser.add_argument("--chunk_type", type=str, help="sequential", default="sequential")
    
    parser.add_argument("--chunk_size", type=float, help="seconds", default=2.0)
    parser.add_argument("--chunk_min", type=float, help="seconds", default=1.0)
    parser.add_argument("--chunk_max", type=float, help="seconds", default=2.0)
    
    parser.add_argument("--num_process", type=int, default=40)
    args = parser.parse_args()
    return args

def get_spk2utt_from_utt2spk(utt2spk_path):
    spk2utt = collections.defaultdict(list)
    with open(utt2spk_path, 'r') as rf:
        for line in rf.readlines():
            utt, spk = line.strip().split()
            spk2utt[spk].append(utt)
    return spk2utt

def get_spk2utt_from_spk2utt(spk2utt_path):
    spk2utt = dict()
    with open(spk2utt_path, 'r') as rf:
        for line in rf.readlines():
            line = line.strip().split()
            spk = line[0]
            utt = line[1:]
            spk2utt[spk] = utt
    return spk2utt

def get_utt2wavpath_from_wavscp(wavscp_path):
    utt2wavpath = dict()
    with open(wavscp_path, 'r') as rf:
        for line in rf.readlines():
            utt, wav_path = line.strip().split() 
            utt2wavpath[utt] = wav_path
    return utt2wavpath

def work(sublines, process_id, manifest_path, chunk_size, chunk_min):
    process_tqdm = tqdm(sublines)
    process_tqdm.set_description(f"Process {process_id}")
    with open(manifest_path, 'w') as wf:
        for spk, utt, wav_path in process_tqdm:
            audio = AudioSegment.from_file(wav_path, format='wav')
            audio_dur = audio.duration_seconds
            audio_sr = audio.frame_rate
            for i in range(math.ceil(audio_dur/chunk_size)):
                offset = i*chunk_size
                if offset + chunk_size <= audio_dur:
                    duration = chunk_size
                elif audio_dur - offset >= chunk_min:
                    duration = audio_dur - offset
                else:
                    break
                
                res = {"audio_filepath":wav_path, "offset":offset,"duration":duration,
                        "label":spk, "orig_sr":audio_sr,"text":""}
                json_data = json.dumps(res)
                wf.write(json_data+'\n')
    

def try_work(sublines, process_id, manifest_path, chunk_size, chunk_min):
    try:
        work(sublines, process_id, manifest_path, chunk_size, chunk_min)
    except Exception as e:
        print(e)
        raise e
    
# {"audio_filepath": "exp/features/online/noise/RIRS_NOISES/real_rirs_isotropic_noises/RVB2014_type1_noise_largeroom1_1.wav", 
# "offset": 0, 
# "duration": 3.0, 
# "label": "RVB2014_type1_noise_largeroom1_1.wav", 
# "orig_sr": 16000, 
# "text": ""}

def get_utt2dur_sr(utt2wavpath):
    utt2dur_sr = dict()
    for utt, wavpath in utt2wavpath.items():
        audio = AudioSegment.from_file(wavpath, format='wav')
        audio_dur = audio.duration_seconds
        audio_sr = audio.frame_rate
        utt2dur_sr[utt] = {"dur":audio_dur, "sr":audio_sr}
    return utt2dur_sr

def main():
    args = parse_opt()
    os.makedirs(args.save_dir, exist_ok=True)
    wavscp_path  = os.path.join(args.data_dir, "wav.scp")
    spk2utt_path = os.path.join(args.data_dir, "spk2utt")
    utt2spk_path = os.path.join(args.data_dir, "utt2spk")
    
    manifest_path = os.path.join(args.save_dir, "data_cut.manifest.json")
    split_dir = os.path.join(args.save_dir, "split")
    os.makedirs(split_dir, exist_ok=True)
    
    utt2wavpath = get_utt2wavpath_from_wavscp(wavscp_path)
    if os.path.isfile(spk2utt_path):
        spk2utt = get_spk2utt_from_spk2utt(spk2utt_path)
    elif os.path.isfile(utt2spk_path):
        spk2utt = get_spk2utt_from_utt2spk(utt2spk_path)
        
    lines = list()
    for spk, utts in tqdm(spk2utt.items()):
        for utt in utts:
            lines.append((spk, utt, utt2wavpath[utt]))
    
    """多进程计算"""
    step = len(lines)//args.num_process + 1
    pool = Pool(args.num_process)
    for i in range(args.num_process):
        sublines = lines[step*i:step*(i+1)]
        sub_manifest_path = os.path.join(split_dir, f"data_cut.manifest.{i}.json")
        pool.apply_async(try_work, (sublines, i, sub_manifest_path, args.chunk_size, args.chunk_min))
    pool.close()
    pool.join()
    
    
    """汇总"""
    cmd = f"cat {split_dir}/* > {manifest_path}"
    os.system(cmd)
    print("Done!")
    
    
if __name__ == "__main__":
    main()
