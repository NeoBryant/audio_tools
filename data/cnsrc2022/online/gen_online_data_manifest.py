#coding=utf-8
# File      :   gen_online_data_manifest.py
# Time      :   2022/04/18 19:25:02
# Author    :   Jinghan Peng
# Desciption:   csv转化为nemo的表单json文件格式

from decimal import Decimal
import os, sys
from tqdm import tqdm
import json

def main():
    csv_path = "/data3/pengjinghan/exp/egs/online/voxceleb2_dev/valid.csv"
    #"/data3/pengjinghan/exp/egs/online/voxceleb2_dev/train.csv"
    #"/data3/pengjinghan/exp/egs/online/voxceleb2_dev/valid.csv"
    json_path = "/data3/pengjinghan/exp/data/vox_train/valid.json"
    #"/data3/pengjinghan/exp/data/vox_train/train.json"
    #"/data3/pengjinghan/exp/data/vox_train/valid.json"
    
    
    # index	audio_filepath	offset	duration	label	orig_sr	text
    # {"audio_filepath": "exp/features/online/noise/RIRS_NOISES/real_rirs_isotropic_noises/RVB2014_type1_noise_largeroom1_1.wav", "offset": 0, "duration": 3.0, "label": "RVB2014_type1_noise_largeroom1_1.wav", "orig_sr": 16000, "text": ""}
    with open(csv_path, 'r') as rf, open(json_path, 'w') as wf:
        keys = rf.readline().strip().split('\t')
        values = rf.readlines()[1:]
        for value in tqdm(values):
            value = value.strip().split('\t')
            res = dict()
            for i in range(len(keys)):
                
                if keys[i] in ("index","orig_sr"):
                    value[i] = int(value[i])
                elif keys[i] in ("offset","duration"):
                    value[i] = float(value[i])
                    
                res[keys[i]] = value[i]
            
            
            json_data = json.dumps(res)
            wf.write(json_data+'\n')
            


if __name__ == '__main__':
    main()

