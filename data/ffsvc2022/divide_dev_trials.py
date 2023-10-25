#coding=utf-8
# File      :   divide_dev_trials.py
# Time      :   2022/05/26 15:25:46
# Author    :   Jinghan Peng
# Desciption:   

import collections
import os, sys

from tqdm import tqdm

def main():
    trials_path = "/data2/pengjinghan/FFSVC_data/Dev_Test_FFSVC2022/dev/data_list/trials"
    dev_meta_list_path = "/data2/pengjinghan/FFSVC_data/Dev_Test_FFSVC2022/dev_meta_list"

    out_dir = "/data2/pengjinghan/FFSVC_data/Dev_Test_FFSVC2022/dev/data_list/trials_divide"
    os.makedirs(out_dir, exist_ok=True)

    utt2visit = dict() # 采集时间
    utt2device = dict() # 设备
    utt2position = dict() # 设备距离
    utt2speed = dict() # 语速
    utt2spk = dict()
    
    
    with open(dev_meta_list_path, 'r') as rf:
        for line in tqdm(rf.readlines()[1:]):
            Original_Name, FFSVC2022_Name = line.strip().split()
            visit_spk, device_position, channel, utt, speed = Original_Name.split('_')
            
            visit = visit_spk[0] # 采集时间
            spk = visit_spk[1:] # spk
            
            device_position = device_position[3:]
            if 'I' in device_position:
                device = device_position[0]
                position = device_position[1:]
            elif "PAD" in device_position:
                device = device_position[:3]
                position = device_position[3:]
            else:
                print("ERROR")
            
            utt2visit[FFSVC2022_Name] = visit
            utt2device[FFSVC2022_Name] = device
            utt2position[FFSVC2022_Name] = position
            utt2speed[FFSVC2022_Name] = speed
            utt2spk[FFSVC2022_Name] = spk
            
    # read trials
    device2trials = collections.defaultdict(list) # 测试集设备
    position2trials = collections.defaultdict(list) # 测试集位置
    speed2trials = collections.defaultdict(list) # 语速是否相同
    
    with open(trials_path, 'r') as rf:
        for line in tqdm(rf.readlines()):
            enroll_utt, test_utt, label = line.strip().split()
            
            enroll_utt = enroll_utt[enroll_utt.find('-')+1:].split(".wav")[0]
            test_utt = test_utt[test_utt.find('-')+1:].split(".wav")[0]
            
            enroll_device = utt2device[enroll_utt]
            test_device = utt2device[test_utt]
            
            enroll_position = utt2position[enroll_utt]
            test_position = utt2position[test_utt]
            
            enroll_speed = utt2speed[enroll_utt]
            test_speed = utt2speed[test_utt]
            
            # record
            device2trials[test_device].append(line)
            position2trials[test_position].append(line)
            if enroll_speed == test_speed:
                speed2trials["same_speed"].append(line)
            else:
                speed2trials["different_speed"].append(line)
                
    # enroll全部为iphone，0.25M，
    
    # device
    device_trials_out_dir = os.path.join(out_dir, "trials_device")
    os.makedirs(device_trials_out_dir, exist_ok=True)
    for device, trials in tqdm(device2trials.items()):
        out_path = os.path.join(device_trials_out_dir, f"trials-{device}")
        with open(out_path, 'w') as wf:
            for line in trials:
                wf.write(line)
    
    # position
    position_trials_out_dir = os.path.join(out_dir, "trials_position")
    os.makedirs(position_trials_out_dir, exist_ok=True)
    for position, trials in tqdm(position2trials.items()):
        out_path = os.path.join(position_trials_out_dir, f"trials-{position}")
        with open(out_path, 'w') as wf:
            for line in trials:
                wf.write(line)

    # speech speed
    speed_out_dir = os.path.join(out_dir, "trials_speed")
    os.makedirs(speed_out_dir, exist_ok=True)
    for speed, trials in tqdm(speed2trials.items()):
        out_path = os.path.join(speed_out_dir, f"trials-{speed}")
        with open(out_path, 'w') as wf:
            for line in trials:
                wf.write(line)
    

if __name__ == '__main__':
    main()

