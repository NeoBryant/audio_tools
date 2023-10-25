#coding=utf-8
# File      :   concatenate_audio.py
# Time      :   2022/05/24 11:34:43
# Author    :   Jinghan Peng
# Desciption:   将同一人同位置同设备同信道的音频拼接为一条音频

import collections
import os, sys

from tqdm import tqdm
from multiprocessing import Pool
from pydub import AudioSegment


def work(sublines, process_id, utt2wav_path, out_dir):
    process_tqdm = tqdm(sublines)
    process_tqdm.set_description(f"Process {process_id}")
    
    for spk, device_position_channel_to_utt_list in process_tqdm:
        for device_position_channel, utt_list in device_position_channel_to_utt_list.items():
            # print(spk, device_position_channel, len(utt_list), utt_list[0])
            out_path = os.path.join(out_dir, f"{spk}-{device_position_channel}.wav")
            if os.path.exists(out_path):
                continue
            
            output_audio = AudioSegment.from_file(utt2wav_path[utt_list[0]], format='wav')

            for utt in tqdm(utt_list[1:]):
                wav_path = utt2wav_path[utt]
                audio = AudioSegment.from_file(wav_path, format='wav')
                output_audio += audio
         
            output_audio.export(out_path, format = 'wav')
            

def try_work(sublines, process_id, utt2wav_path, out_dir):
    try:
        work(sublines, process_id, utt2wav_path, out_dir)
    except Exception as e:
        print(e)
        raise e

def main():
    wav_scp_path = "/data2/pengjinghan/FFSVC_data/FFSVC2020_210/data_list/wav.scp"
    out_dir      = "/data2/pengjinghan/FFSVC_data/ffsvc2020_concat/wav"
    os.makedirs(out_dir, exist_ok=True)
    
    device_position_list = set()
    device_position_channel_list = set()
    spk_device_position_channel_list = set()
    
    spk_to_device_position_channel_to_utt_list = dict()
    utt2wav_path = dict()
    
    with open(wav_scp_path, 'r') as rf:
        for line in tqdm(rf.readlines()):
        
            utt, wav_path = line.strip().split()
            utt2wav_path[utt] = wav_path
            
            spk = utt.split('_')[0][1:]
            device_position = utt.split('_')[1][3:]
            channel = utt.split('_')[2]
            device_position_channel = device_position+'_'+channel
            spk_device_position_channel = spk+'-'+device_position_channel
            
            if spk not in spk_to_device_position_channel_to_utt_list:
                spk_to_device_position_channel_to_utt_list[spk] = collections.defaultdict(list)
            
            # spk_to_device_position_channel_to_utt_list[spk][device_position].append(utt)
            spk_to_device_position_channel_to_utt_list[spk][device_position_channel].append(utt)
            
            
            if device_position not in device_position_list:
                device_position_list.add(device_position)

            if device_position_channel not in device_position_channel_list:
                device_position_channel_list.add(device_position_channel)
                
            if spk_device_position_channel not in spk_device_position_channel_list:
                spk_device_position_channel_list.add(spk_device_position_channel)



    device_position_list = list(device_position_list)    
    device_position_list.sort()
    print(f"{len(device_position_list)} device position: {device_position_list}")
    # 15 device position: 
    # ['I0.25M', 'I1M', 'I3M', 'I5M', 'MIC', 
    # 'PAD0.25M', 'PAD1M', 'PAD3M', 'PAD5M', 
    # 'PCM-1.5M', 'PCM1M', 'PCM3M', 'PCM5M', 'PCML3M', 'PCMR3M']
    device_position_channel_list = list(device_position_channel_list)
    device_position_channel_list.sort()
    print(f"{len(device_position_channel_list)} device_position_channel: {device_position_channel_list}")
    """
    33 device_position_channel: 
    ['I0.25M_1', 'I1M_1', 'I3M_1', 'I5M_1', 'MIC_Tr2', 
    'PAD0.25M_1', 'PAD1M_1', 'PAD3M_1', 'PAD5M_1', 
    'PCM-1.5M_recorded10', 'PCM-1.5M_recorded14', 'PCM-1.5M_recorded2', 'PCM-1.5M_recorded6', 
    'PCM1M_recorded10', 'PCM1M_recorded14', 'PCM1M_recorded2', 'PCM1M_recorded6', 
    'PCM3M_recorded10', 'PCM3M_recorded14', 'PCM3M_recorded2', 'PCM3M_recorded6', 
    'PCM5M_recorded10', 'PCM5M_recorded14', 'PCM5M_recorded2', 'PCM5M_recorded6', 
    'PCML3M_recorded10', 'PCML3M_recorded14', 'PCML3M_recorded2', 'PCML3M_recorded6', 
    'PCMR3M_recorded10', 'PCMR3M_recorded14', 'PCMR3M_recorded2', 'PCMR3M_recorded6']
    """
    
    print(f"{len(spk_device_position_channel_list)} wavs to generate")
    # 同说话人同位置同设备同信道拼接后应有4303条音频

    
    return
    """输入"""
    threads = 32 # 进程数
    lines = list(spk_to_device_position_channel_to_utt_list.items())
    
    
    """多进程计算"""
    step = len(lines)//threads + 1
    pool = Pool(threads)
    for i in range(threads):
        sublines = lines[step*i:step*(i+1)]
        pool.apply_async(try_work, (sublines, i, utt2wav_path, out_dir))
    pool.close()
    pool.join()
    
    # print(f"{len(spk_to_device_position_to_utt_list)} spks")
    # for spk, device_position_to_utt_list in tqdm(spk_to_device_position_to_utt_list.items()):
    #     for device_position, utt_list in device_position_to_utt_list.items():
    #         print(spk, device_position, len(utt_list), utt_list[0])
    #         for utt in utt_list:
    #             # print(utt)
    #             pass
    #         return
    
    

if __name__ == '__main__':
    main()

