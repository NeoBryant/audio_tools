#coding=utf-8
# File      :   utt2dur_gen.py
# Time      :   2022/02/15 10:42:05
# Author    :   Jinghan Peng
# Desciption:   根据wav.scp生成utt2dur

import os, sys
from matplotlib import cm
from tqdm import tqdm
from multiprocessing import Pool
from pydub import AudioSegment

from argparse import ArgumentParser

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--wavscp_path", type=str, help="path of wav.scp", 
                        default="/data/pengjinghan/wx_data/datalist/filtrate_repeated_wxid/wav.scp")
    parser.add_argument("--output_dir", type=str, help="path of dir to generate utt2spk and spk2utt ", 
                        default="/data/pengjinghan/wx_data/datalist/filtrate_repeated_wxid")
    
    args = parser.parse_args()
    return args


def work(sublines, process_id, sub_out_path):
    process_tqdm = tqdm(sublines)
    process_tqdm.set_description(f"Process {process_id}")
    
    with open(sub_out_path, 'w') as wf:
        for utt, wav_path in process_tqdm:
            try:
                audio = AudioSegment.from_file(wav_path, format='wav')
                dur = audio.duration_seconds
                wf.write(f"{utt} {dur}\n")
            except:
                print(f"[ERROR] {wav_path}")

def try_work(sublines, process_id, sub_out_path):
    try:
        work(sublines, process_id, sub_out_path)
    except Exception as e:
        print(e)
        raise e

def main(args):
    """输入"""
    threads = 16 # 进程数
    lines = list()
    
    sub_out_dir = os.path.join(args.output_dir, "split")
    os.makedirs(sub_out_dir, exist_ok=True)
    
    """处理"""
    utt2path = dict()
    with open(args.wavscp_path, 'r') as rf:
        for line in tqdm(rf.readlines()):  
            utt, path = line.strip().split()
            if utt not in utt2path:
                utt2path[utt] = path
    
    lines = list(utt2path.items())
    print(f"computing: {len(lines)}")              
    
    """多进程计算"""
    step = len(lines)//threads + 1
    pool = Pool(threads)
    for i in range(threads):
        sublines = lines[step*i:step*(i+1)]
        sub_out_path = os.path.join(sub_out_dir, f"utt2dur.{i}.split")
        pool.apply_async(try_work, (sublines, i, sub_out_path))
    pool.close()
    pool.join()

    """合并各进程split"""
    cmd = f"cat {sub_out_dir}/* > {args.output_dir}/utt2dur"
    os.system(cmd)

if __name__ == "__main__":
    args = parse_args()
    main(args)
