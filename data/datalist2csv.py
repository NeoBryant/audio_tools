#coding=utf-8
# File      :   wavs2csv.py
# Time      :   2022/07/22 14:51:19
# Author    :   Jinghan Peng
# Desciption:   将音频进行划分，并判断是否添加变速变调增强，最终生成csv文件

import argparse
import collections
from genericpath import isfile
import os
from tqdm import tqdm
import vaex
# from tools.data.generate_class2index import generate_class2indices

import subprocess
import json
import math
from multiprocessing import Pool

import torchaudio

def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_dir", type=str, default="/data3/pengjinghan/voxceleb_dataset/data_list", help="wav.scp file in kaldi format")
    parser.add_argument("--out_dir", type=str, default="/data3/pengjinghan/voxceleb_dataset/data_list/dataset_nosp", help="output directory")
    parser.add_argument("--csv_name", type=str, default="data", help="output csv name")
    
    parser.add_argument("--duration", type=float, default=12, help="duration of speech segment")
    parser.add_argument("--min_dur", type=float, default=12, help="min duration of speech segment")
    parser.add_argument("--max_dur", type=float, default=12, help="max duration of speech segment")
    
    parser.add_argument("--speed_aug", type=bool, default=False, help="speed aug [0.9, 1.1]")
    parser.add_argument("--speed_list", type=list, default=[0.9, 1.1], help="speed aug [0.9, 1.1]")
    
    args = parser.parse_args()
    return args

# def get_waveform_info(filename):
#     """返回音频的时长和采样率
#     """
#     stderr = open(os.devnull, 'w')
#     stdin = open(os.devnull)
#     proc = subprocess.Popen(['ffprobe', '-i', filename, '-show_streams',
#             '-select_streams', 'a', '-print_format', 'json'],
#         stderr=stderr,
#         stdin=stdin,
#         stdout=subprocess.PIPE)
#     prop = json.loads(proc.stdout.read())
    
#     duration = float(prop['streams'][0]['duration'])
#     sample_rate = int(prop['streams'][0]['sample_rate'])
    
#     return {"duration":duration, "sample_rate":sample_rate}


def work(sublines, process_id, args):
    process_tqdm = tqdm(sublines)
    process_tqdm.set_description(f"Process {process_id}")
    
    csv_path = os.path.join(args.out_dir, "split", f"{args.csv_name}.{process_id}.csv")
    with open(csv_path, 'w') as wf:
        for utt, wav_path, label, speed in process_tqdm:
            
            info = torchaudio.backend.sox_io_backend.info(wav_path)
            duration = info.num_frames / info.sample_rate
          
            if args.duration == -1 or (duration >= args.min_dur and duration <= args.max_dur):
                wf.write(f"{utt}\t{wav_path}\t{label}\t{0}\t{duration}\t{speed}\n")
            else:
                num_segments = math.ceil(duration / args.duration) # 切片的片段数量
                last_segment_dur = duration % args.duration
                
                if last_segment_dur == 0: # 每个片段的时长都符合要求
                    for i in range(num_segments):
                        wf.write(f"{utt}\t{wav_path}\t{label}\t{args.duration*i}\t{args.duration}\t{speed}\n")
                elif last_segment_dur <= args.max_dur - args.duration: # 最后一个片段和前一个片段合为一个片段
                    for i in range(num_segments):
                        if i != num_segments-1:
                            wf.write(f"{utt}\t{wav_path}\t{label}\t{args.duration*i}\t{args.duration}\t{speed}\n")
                        else:
                            wf.write(f"{utt}\t{wav_path}\t{label}\t{args.duration*i}\t{args.duration+last_segment_dur}\n")
                elif last_segment_dur >= args.min_dur: # 最后一个片段单独作为一个片段
                    for i in range(num_segments):
                        if i != num_segments-1:
                            wf.write(f"{utt}\t{wav_path}\t{label}\t{args.duration*i}\t{args.duration}\t{speed}\n")
                        else:
                            wf.write(f"{utt}\t{wav_path}\t{label}\t{args.duration*i}\t{last_segment_dur}\t{speed}\n")
                else:
                    for i in range(num_segments): # 最后一个片段的时长不符合，需丢弃
                        if i != num_segments-1:
                            wf.write(f"{utt}\t{wav_path}\t{label}\t{args.duration*i}\t{args.duration}\t{speed}\n")
                

def try_work(sublines, process_id, args):
    try:
        work(sublines, process_id, args)
    except Exception as e:
        print(e)
        raise e


def main():
    args = parse_opt()
    
    assert args.min_dur <= args.duration <= args.max_dur
    
    speed_aug = args.speed_aug # 是否变速变调增强
    speed_list = args.speed_list # 变速变调倍率列表
    
    threads = 32
    
    out_dir = args.out_dir
    os.makedirs(out_dir, exist_ok=True)
    
    utt2spk = dict()
    spk_set = set()
    with open(os.path.join(args.in_dir, "utt2spk"), 'r') as rf:
        for line in tqdm(rf.readlines()):
            utt, spk = line.strip().split()
            utt2spk[utt] = spk
            if speed_aug:
                for speed in speed_list:
                    speed_utt, speed_spk = f"sp{speed}-{utt}", f"sp{speed}-{spk}"
                    utt2spk[speed_utt] = speed_spk
            if spk not in spk_set:
                spk_set.add(spk)   
    
    if speed_aug:
        print(f"num raw utts: {len(utt2spk)//3}, after speed aug: {len(utt2spk)}")
        print(f"num raw spks: {len(spk_set)}")
    else:
        print(f"num raw utts: {len(utt2spk)}")
        print(f"num raw spks: {len(spk_set)}")
    
    if os.path.exists(os.path.join(args.in_dir, "spk2label")):
        spk2label = {line.strip().split()[0]:int(line.strip().split()[1]) for line in open(os.path.join(args.in_dir, "spk2label"))}
    else:
        spk_list_sort = list(spk_set)
        spk_list_sort.sort()
        spk2label = {spk:i for i, (spk) in enumerate(spk_list_sort)}

    raw_spks_list = list(spk2label.keys())
    num_spks = len(spk2label) # 说话人数量
    
    if speed_aug:
        for speed_index, (speed) in enumerate(speed_list):
            for raw_spk in raw_spks_list:
                spk2label[f"sp{speed}-{raw_spk}"] = spk2label[raw_spk]+(speed_index+1)*num_spks
                
        print(f"number of speakers after speed aug: {len(spk2label)}")
    
    # write spk2label
    with open(os.path.join(out_dir, "spk2label"), 'w') as wf:
        for spk, label in spk2label.items():
            wf.write(f"{spk} {label}\n")

    # generate list to divide for each subprocess
    lines = list()    
    with open(os.path.join(args.in_dir, "wav.scp"), 'r') as rf:
        for line in tqdm(rf.readlines()):
            utt, wav_path = line.strip().split()
            label = spk2label[utt2spk[utt]]
            lines.append((utt,wav_path,label,1))
            if speed_aug:
                for speed in speed_list:
                    speed_utt = f"sp{speed}-{utt}"
                    label = spk2label[utt2spk[speed_utt]]
                    lines.append((speed_utt,wav_path,label,speed))
    
    # csv_dir = os.path.join(out_dir, 'csv')
    split_csv_dir = os.path.join(out_dir, "split")
    os.makedirs(split_csv_dir, exist_ok=True)
    
    """多进程计算"""
    step = len(lines)//threads + 1
    pool = Pool(threads)
    for i in range(threads):
        sublines = lines[step*i:step*(i+1)]
        pool.apply_async(try_work, (sublines, i, args))
    pool.close()
    pool.join()    
    
    """汇总各进程计算结果"""
    csv_path = os.path.join(out_dir, f"{args.csv_name}.csv")
    with open(csv_path, 'w') as wf:
        wf.write("utt_id\taudio_filepath\tlabel\toffset\tduration\tspeed\n")
        for split_file in os.listdir(split_csv_dir):
            split_filepath = os.path.join(split_csv_dir, split_file)
            with open(split_filepath, 'r') as rf:
                wf.writelines(rf.readlines())
                    
    
    """ convert csv to h5 file """
    # df = vaex.from_csv(csv_path, sep="\t")
    # df = df.sort(by="utt_id")
    
    # hdf5_dir = os.path.join(out_dir, 'hdf5')
    # os.makedirs(hdf5_dir, exist_ok=True)
    # hdf5_path = os.path.join(hdf5_dir, f"{args.csv_name}.hdf5")
    
    # df.export(hdf5_path)                
    

if __name__ == "__main__":
    main()