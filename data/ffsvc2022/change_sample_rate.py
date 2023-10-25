#coding=utf-8
# File      :   change_sample_rate.py
# Time      :   2022/05/23 12:11:48
# Author    :   Jinghan Peng
# Desciption:   修改音频采样率并另存为新音频

import os, sys

from tqdm import tqdm
from multiprocessing import Pool
from argparse import ArgumentParser

        
def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--in_dir", type=str, help="", 
                        default="/data1/pengjinghan/tsvad_test_data/5vocal/wav_16k")
    parser.add_argument("--out_dir", type=str, help="", 
                        default="/data1/pengjinghan/tsvad_test_data/5vocal/wav")
    args = parser.parse_args()
    return args

def work(sublines, process_id, sample_rate=8000):
    process_tqdm = tqdm(sublines)
    process_tqdm.set_description(f"Process {process_id}")
    for wav_path, out_path in process_tqdm:
        
        cmd = f"ffmpeg -loglevel quiet -i {wav_path} -ar {sample_rate} {out_path}"
        os.system(cmd)

def try_work(sublines, process_id):
    try:
        work(sublines, process_id)
    except Exception as e:
        print(e)
        raise e

def main():
    args = parse_args()
    
    """输入"""
    in_dir = args.in_dir
    out_dir = args.out_dir
    threads = 32 # 进程数
    lines = []
    
    os.makedirs(out_dir, exist_ok=True)
    
    for wav_name in tqdm(os.listdir(in_dir)):
        wav_path = os.path.join(in_dir, wav_name)
        out_path = os.path.join(out_dir, wav_name)
    
        lines.append((wav_path, out_path))
    
    """多进程计算"""
    step = len(lines)//threads + 1
    pool = Pool(threads)
    for i in range(threads):
        sublines = lines[step*i:step*(i+1)]
        pool.apply_async(try_work, (sublines, i))
    pool.close()
    pool.join()


if __name__ == "__main__":
    main()
