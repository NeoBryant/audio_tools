#coding=utf-8
# File      :   compute_enroll_mean_embedding.py
# Time      :   2022/06/06 17:37:27
# Author    :   Jinghan Peng
# Desciption:   计算enroll/test的mean vector（原始、music、babble、noise、reverb）


import os, sys
import collections
from tqdm import tqdm

import numpy as np
import kaldiio
from kaldiio import WriteHelper

class incre_std_avg():
    def __init__(self, h_avg=0, h_std=0, n=0):
        self.avg = h_avg
        self.std = h_std
        self.n = n

    def incre_in_list(self, new_list):
        avg_new = np.mean(new_list)
        incre_avg = (self.n*self.avg+len(new_list)*avg_new) / (self.n+len(new_list))
        std_new = np.std(new_list)
        incre_std = np.sqrt((self.n*(self.std**2+(incre_avg-self.avg)**2)+len(new_list)
                                * (std_new**2+(incre_avg-avg_new)**2))/(self.n+len(new_list)))
        self.avg = incre_avg
        self.std = incre_std
        self.n += len(new_list)

    def incre_in_value(self, value):
        incre_avg = (self.n*self.avg+value)/(self.n+1)
        incre_std = np.sqrt((self.n*(self.std**2+(incre_avg-self.avg)
                                        ** 2)+(incre_avg-value)**2)/(self.n+1))
        self.avg = incre_avg
        self.std = incre_std
        self.n += 1

def main():
    in_path = "/data2/pengjinghan/FFSVC_test/backend_test/EAD/project/20220602-repvgg_a1-stats_std-sc/test_vector/xvector_raw.scp"
    out_dir = "/data2/pengjinghan/FFSVC_test/backend_test/EAD/test_aug/mean_embedding"
    os.makedirs(out_dir, exist_ok=True)
    
    
    utt2vector_path = collections.defaultdict(list)
    
    with open(in_path, 'r') as rf:
        for line in tqdm(rf.readlines()):
            utt, vector_path = line.strip().split()
            if "-babble" in utt or "-music" in utt or "-noise" in utt or "-reverb" in utt:
                raw_utt = utt[:utt.rfind('-')]
            else:
                raw_utt = utt
                
            utt2vector_path[raw_utt].append(vector_path)        
    
    

    save_name = os.path.join(out_dir, "xvector")
    scp_save = "ark,scp:{}.ark,{}.scp".format(save_name, save_name)
    with WriteHelper(scp_save) as writer:
        for utt, vector_path_list in tqdm(utt2vector_path.items()):
            c = incre_std_avg()
            assert len(vector_path_list) == 5
            for vector_path in vector_path_list:
                vector = kaldiio.load_mat(vector_path)
                c.incre_in_value(vector)
                vector_average = c.avg
                
            writer(utt, vector_average)
    

if __name__ == '__main__':
    main()

