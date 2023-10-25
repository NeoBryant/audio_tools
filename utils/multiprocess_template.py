#coding=utf-8
# File      :   multiprocess_template.py
# Time      :   2021/08/10 16:20:13
# Author    :   Jinghan Peng
# Desciption:   多进程处理脚本的模型

import os, sys
from tqdm import tqdm
from multiprocessing import Pool
from argparse import ArgumentParser

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--arg", type=str, help="", 
                        default="")

    args = parser.parse_args()
    return args

def work(sublines, process_id):
    process_tqdm = tqdm(sublines)
    process_tqdm.set_description(f"Process {process_id}")
    for line in process_tqdm:
        pass
    return

def try_work(sublines, process_id):
    try:
        work(sublines, process_id)
    except Exception as e:
        print(e)
        raise e

def main():
    args = parse_args()
    
    """输入"""
    threads = 1 # 进程数
    lines = []
            
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
