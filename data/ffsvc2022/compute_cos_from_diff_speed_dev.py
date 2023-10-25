#coding=utf-8
# File      :   compute_cos_from_diff_speed.py
# Time      :   2022/06/28 17:48:58
# Author    :   Jinghan Peng
# Desciption:   注册音频做变速，然后取分数最大值/平均值作为最终分数

import collections
import os, sys

from tqdm import tqdm

def main():
    score_path = "/data2/pengjinghan/FFSVC_test/project/20220621-repvgg_a2-stats_std-sc-vox_ffsvc-refine-enroll_sp/scores/enroll_VS_test/score_raw"
    trials_path = "/data2/pengjinghan/FFSVC_data/Dev_Test_FFSVC2022/dev/data_list/trials"
    out_path = "/data2/pengjinghan/FFSVC_data/Dev_Test_FFSVC2022/dev/data_list_sp/score_raw"
    
    utt2speed_path = "/data2/pengjinghan/FFSVC_data/Dev_Test_FFSVC2022/dev/data_list/utt2speed"
    
    utt2speed = dict()
    with open(utt2speed_path, 'r') as rf:
        for line in rf.readlines():
            utt, speed = line.strip().split()
            utt2speed[utt] = speed
    
    pair_set = set()
    with open(trials_path, 'r') as rf:
        for line in rf.readlines():
            enroll_utt, test_utt = line.strip().split()[:2]
            pair_set.add(enroll_utt+" "+test_utt)
    
    print(f"trials pairs: {len(pair_set)}")
    
    pair2scores = collections.defaultdict(dict)
    with open(score_path, 'r') as rf:
        for line in rf.readlines():
            enroll_utt, test_utt, score = line.strip().split()
            score = float(score)
            changed_speed = enroll_utt.split('-')[-1].split(".wav")[0]
            enroll_utt = enroll_utt[:enroll_utt.rfind("-")]+".wav"
            pair2scores[enroll_utt+" "+test_utt][changed_speed] = score


    with open(out_path, 'w') as wf:
        for pair, score_dict in tqdm(pair2scores.items()):
            # score = sum(score_list)/len(score_list) # 均值
            # score = max(score_list)
            enroll_utt, test_utt = pair.split()
            enroll_speed, test_speed = utt2speed[enroll_utt], utt2speed[test_utt]
            
            # method 1
            # if enroll_speed == test_speed: # 语速相同
            #     score = score_list["normal"]
            # elif enroll_speed in ("slow", "normal") and test_speed in ("normal", "fast"):
            #     score = score_list["fast"]
            # else:
            #     score = score_list["slow"]
            
            # method 2
            if enroll_speed == "slow" and test_speed == "fast":
                # score = score_dict["faster"]
                score_list = list(score_dict.values())
                # score = sum(score_list)/len(score_list)
                # score = max(score_list)
                score = min(score_list)
            # elif enroll_speed == "fast" and test_speed == "slow":
            #     score = score_dict["slower"]
            else:
                score = score_dict["normal"]
            
                 
            # method 3
            # if enroll_speed == "slow" and test_speed == "fast":
            #     score = score_list["faster"]
            # elif enroll_speed == "fast" and test_speed == "slow":
            #     score = score_list["slower"]
            # elif (enroll_speed == "slow" and test_speed == "normal") or (enroll_speed == "normal" and test_speed == "fast"):
            #     score = score_list["fast"]
            # elif (enroll_speed == "fast" and test_speed == "normal") or (enroll_speed == "normal" and test_speed == "slow"):
            #     score = score_list["slow"]
            # else:
            #     score = score_list["normal"]    
                
            wf.write(f"{pair} {score}\n")


if __name__ == '__main__':
    main()

