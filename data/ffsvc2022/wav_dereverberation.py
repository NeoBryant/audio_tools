#coding=utf-8
# File      :   dereverberation.py
# Time      :   2022/06/06 18:46:08
# Author    :   Jinghan Peng
# Desciption:   对音频进行降混响

"""
pip install nara-wpe

https://nara-wpe.readthedocs.io/en/latest/
"""


import os, sys
import shutil
# import IPython
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
from tqdm import tqdm

from nara_wpe.wpe import wpe
from nara_wpe.wpe import get_power
from nara_wpe.utils import stft, istft, get_stft_center_frequencies
from nara_wpe import project_root

from multiprocessing import Pool
from argparse import ArgumentParser

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--in_dir", type=str, help="", 
                        default="/data2/pengjinghan/FFSVC_data/Dev_Test_FFSVC2022/dev/wav_16k")
    parser.add_argument("--out_dir", type=str, help="", 
                        default="/data2/pengjinghan/FFSVC_data/Dev_Test_FFSVC2022/dev/wav_dereverb")

    args = parser.parse_args()
    return args

def work(sublines, process_id, delay, iterations, taps, sampling_rate, statistics_mode):
    process_tqdm = tqdm(sublines)
    process_tqdm.set_description(f"Process {process_id}")
    
    for wav_path, out_path in process_tqdm:
        dereverb(wav_path, out_path, 
            delay=delay, 
            iterations=iterations, 
            taps=taps, 
            sampling_rate=sampling_rate,
            statistics_mode=statistics_mode)
        

def try_work(sublines, process_id, delay, iterations, taps, sampling_rate, statistics_mode):
    try:
        work(sublines, process_id, delay, iterations, taps, sampling_rate, statistics_mode)
    except Exception as e:
        print(e)
        raise e


def dereverb(in_path, out_path, delay=3, iterations=5, taps=10, sampling_rate=16000, statistics_mode='full'):
    stft_options = dict(size=512, shift=128)
    
    # channels = 1 #8
    # sampling_rate = 48000 #16000
    # delay = 3
    # iterations = 5
    # taps = 10
    # alpha=0.9999

    signal = sf.read(in_path)[0]
    signal = [signal]
    y = np.stack(signal, axis=0)
    Y = stft(y, **stft_options).transpose(2, 0, 1)
    
    Z = wpe(Y,
        taps=taps,
        delay=delay,
        iterations=iterations,
        statistics_mode=statistics_mode
    ).transpose(1, 2, 0)
    z = istft(Z, size=stft_options['size'], shift=stft_options['shift'])

    sf.write(out_path, z[0], sampling_rate)
    
    
    
def main():
    args = parse_args()
    
    """输入"""
    threads = 32 # 进程数
    lines = []

    in_dir  = args.in_dir
    out_dir = args.out_dir
    assert in_dir != out_dir
    
    os.makedirs(out_dir, exist_ok=True)
    
    # dereverb params
    delay = 3
    iterations = 10 #100 #5 # 迭代次数
    taps = 10 # 过滤命令
    sampling_rate = 16000 # 采样率
    statistics_mode = 'full'
    
    
    
    for file_name in tqdm(os.listdir(in_dir)):
        # utt = file_name.split(".wav")[0]
        
        wav_path = os.path.join(in_dir, file_name)
        out_path = os.path.join(out_dir, file_name)
        lines.append((wav_path, out_path))
        # dereverb(wav_path, out_path, 
        #          delay=delay, 
        #          iterations=iterations, 
        #          taps=taps, 
        #          sampling_rate=sampling_rate
        #          statistics_mod=statistics_mode)

            
    """多进程计算"""
    step = len(lines)//threads + 1
    pool = Pool(threads)
    for i in range(threads):
        sublines = lines[step*i:step*(i+1)]
        pool.apply_async(try_work, (sublines, i, delay, iterations, taps, sampling_rate, statistics_mode))
    pool.close()
    pool.join()


if __name__ == '__main__':
    main()

