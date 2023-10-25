#coding=utf-8
# File      :   compute_cos_from_diff_speed.py
# Time      :   2022/06/28 17:48:58
# Author    :   Jinghan Peng
# Desciption:   注册音频做变速，然后取分数最大值/平均值作为最终分数

import collections
import os, sys

def main():
    score_path = "/data2/pengjinghan/FFSVC_test/project/20220621-repvgg_a2-stats_std-sc-vox_ffsvc-refine-enroll_sp/scores/enroll_VS_test/score_raw"
    trials_path = "/data2/pengjinghan/FFSVC_data/Dev_Test_FFSVC2022/dev/data_list/trials"
    out_path = "/data2/pengjinghan/FFSVC_data/Dev_Test_FFSVC2022/dev/data_list_sp/score_raw"
    
    
    
    pair_set = set()
    with open(trials_path, 'r') as rf:
        for line in rf.readlines():
            enroll_utt, test_utt = line.strip().split()[:2]
            pair_set.add(enroll_utt+" "+test_utt)
    
    print(f"trials pairs: {len(pair_set)}")
    
    pair2scores = collections.defaultdict(list)
    with open(score_path, 'r') as rf:
        for line in rf.readlines():
            enroll_utt, test_utt, score = line.strip().split()
            score = float(score)
            changed_speed = enroll_utt.split('-')[-1].split(".wav")[0] # 调速的倍速
            enroll_utt = enroll_utt[:enroll_utt.rfind("-")]+".wav"
            if changed_speed in ("normal", "fast", "slow"):
                pair2scores[enroll_utt+" "+test_utt].append(score)

    with open(out_path, 'w') as wf:
        for pair, score_list in pair2scores.items():
            # score = sum(score_list)/len(score_list) # 均值
            score = max(score_list) # 最大值
            # score = max(score_list) # 最小值
            
            wf.write(f"{pair} {score}\n")
            


if __name__ == '__main__':
    main()

