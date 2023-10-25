#coding=utf-8
# File      :   statis_embedding_norms.py
# Time      :   2022/06/08 10:45:13
# Author    :   Jinghan Peng
# Desciption:   统计数据集不同距离采样的音频的embedding的模长

import collections
import os, sys
from tqdm import tqdm
import kaldiio
import numpy as np

def main():
    vector_path = "/data2/pengjinghan/FFSVC_test/project/20220602-repvgg_a1-stats_std-sc-downsample_wav/enroll_vector/xvector_raw.scp"
    dev_meta_list_path = "/data2/pengjinghan/FFSVC_data/Dev_Test_FFSVC2022/dev_meta_list"
    
    
    utt2device = dict()
    utt2position = dict()
    utt2speed = dict()
    with open(dev_meta_list_path, 'r') as rf:
        for line in tqdm(rf.readlines()[1:]):
            # T0344_344I1M_1_0307_normal ffsvc22_dev_000000
            Original_Name, FFSVC2022_Name = line.strip().split()
            speed = Original_Name.split('_')[-1]
            device_position = Original_Name.split('_')[1][3:]
            if 'I' in device_position:
                device = 'I'
                position = device_position[1:]
            else:
                device = "PAD"
                position = device_position[3:]
                
            utt2speed[FFSVC2022_Name] = speed
            utt2device[FFSVC2022_Name] = device
            utt2position[FFSVC2022_Name] = position
            
    
    ipad_position2norms = {"0.25M": list(),
                      "1M":list(),
                      "-1.5M":list(),
                      "3M":list(),
                      "L3M":list(),
                      "R3M":list(),
                      "5M":list(),} #collections.defaultdict(list)     
    
    iphone_position2norms = {"0.25M": list(),
                      "1M":list(),
                      "-1.5M":list(),
                      "3M":list(),
                      "L3M":list(),
                      "R3M":list(),
                      "5M":list(),} #collections.defaultdict(list)

    speed2norms = {"slow":list(),"normal":list(),"fast":list(),}
    
    with open(vector_path, 'r') as rf:
        for line in tqdm(rf.readlines()):
            utt, vector_path = line.strip().split()
            utt = utt.split('-')[-1].split(".wav")[0]
            
            vector = kaldiio.load_mat(vector_path)
            norm = np.linalg.norm(vector)
            
            device = utt2device[utt]
            position = utt2position[utt]
            if device == "I":
                iphone_position2norms[position].append(norm)
            else:
                ipad_position2norms[position].append(norm)
          
          
            speed = utt2speed[utt]
            speed2norms[speed].append(norm)
          
    # device and position
    print(" ------- iphone -------")  
    print("position \t mean_norm \t utt_num")
    for position, norm_list in iphone_position2norms.items():
        if len(norm_list)>0:
            mean_norm = sum(norm_list)/len(norm_list)
            print(f"{position} \t {mean_norm} \t {len(norm_list)}")
        
    print(" ------- ipad -------")  
    print("position \t mean_norm \t utt_num")
    for position, norm_list in ipad_position2norms.items():
        if len(norm_list)>0:
            mean_norm = sum(norm_list)/len(norm_list)
            print(f"{position} \t {mean_norm} \t {len(norm_list)}")
            
    # speech speed
    print(" ------- iphone & ipad -------")  
    print("speed \t mean_norm \t utt_num")
    for speed, norm_list in speed2norms.items():
        if len(norm_list)>0:
            mean_norm = sum(norm_list)/len(norm_list)
            print(f"{speed} \t {mean_norm} \t {len(norm_list)}")
    

if __name__ == '__main__':
    main()


"""
模型：epoch_2_18095,lr=8.0e-04,145:/data2/pengjinghan/exp/ffsvc_producing/20220602-repvgg_a1-stats_std-sc
ffsvc2022 dev 注册集
 ------- iphone -------
position 	 mean_norm 	 utt_num
0.25M 	 17.586865973385088  2997

ffsvc2022 dev 测试集
 ------- iphone -------
position 	 mean_norm 	 utt_num
1M 	     16.13531164941217 	 5063
-1.5M 	 14.129417916209173  5094
3M 	     14.78240650954296 	 4996
L3M 	 14.933903970397212  5137
R3M 	 14.713875259536197  5020
5M 	     15.053410695035799  5007
 ------- ipad -------
position 	 mean_norm 	 utt_num
0.25M 	 17.16783204349952 	 4992
1M 	     16.04585623406695 	 4990
-1.5M 	 14.821211071826527  5026
3M 	     15.122826121565486  5076
L3M 	 14.902916431519934  5131
R3M 	 15.197519670295716  5000
5M 	     15.329370198993509  5014
"""