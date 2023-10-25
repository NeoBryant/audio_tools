#coding=utf-8
# File      :   gen_utt2channel_from_sr.py
# Time      :   2022/06/17 10:11:47
# Author    :   Jinghan Peng
# Desciption:   根据音频采样率判断音频信道，16k为ipad，48k/44.1k为iphone

import os, sys
from pydub import AudioSegment
from tqdm import tqdm
from multiprocessing import Pool
from argparse import ArgumentParser

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--arg", type=str, help="", 
                        default="")

    args = parser.parse_args()
    return args

def work(sublines, process_id, sub_out_path):
    process_tqdm = tqdm(sublines)
    process_tqdm.set_description(f"Process {process_id}")

    # sr: {16000, 44100, 48000}
    with open(sub_out_path, 'w') as wf:
        for utt, file_path in process_tqdm:
            audio = AudioSegment.from_file(file_path, format='wav')
            sr = audio.frame_rate
            wf.write(f"{utt} {sr}\n") 
    

def try_work(sublines, process_id, sub_out_path):
    try:
        work(sublines, process_id, sub_out_path)
    except Exception as e:
        print(e)
        raise e

def main():
    # args = parse_args()
    in_dir = "/data2/pengjinghan/FFSVC_data/FFSVC2020_210/data_list_I/wav.scp"
    out_dir = "/data2/pengjinghan/FFSVC_data/FFSVC2020_210/data_list_I"
    
    """输入"""
    threads = 32 # 进程数
    lines = []
    if os.path.isdir(in_dir):
        for file in tqdm(os.listdir(in_dir)):
            file_path = os.path.join(in_dir, file)
            lines.append((file, file_path))
    elif os.path.isfile(in_dir):
        with open(in_dir, 'r') as rf:
            for line in tqdm(rf.readlines()):
                utt, file_path = line.strip().split()
                lines.append((utt, file_path))
            
    """多进程计算"""
    step = len(lines)//threads + 1
    pool = Pool(threads)
    for i in range(threads):
        sublines = lines[step*i:step*(i+1)]
        sub_out_path = os.path.join(out_dir, f"utt2sr.{i}.split")
        pool.apply_async(try_work, (sublines, i, sub_out_path))
    pool.close()
    pool.join()

    out_path = os.path.join(out_dir, f"utt2sr")
    with open(out_path, 'w') as wf:
        for i in range(threads):
            sub_out_path = os.path.join(out_dir, f"utt2sr.{i}.split")
            with open(sub_out_path, 'r') as rf:
                wf.writelines(rf.readlines())
            os.remove(sub_out_path)

if __name__ == '__main__':
    main()
