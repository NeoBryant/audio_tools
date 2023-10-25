#coding=utf-8
# File      :   score_fusion.py
# Time      :   2022/07/07 17:11:37
# Author    :   Jinghan Peng
# Desciption:   

import os, sys
from tqdm import tqdm
from argparse import ArgumentParser

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--scores_paths", type=str, nargs='+', help="", 
        default=[
            "/data2/pengjinghan/FFSVC_test/scores_fusion/dev/score-0704_refine_resnet152-asnorm_0.2939",
            "/data2/pengjinghan/FFSVC_test/scores_fusion/dev/score-0705_refine_resnet221-asnorm_0.3237",
            "/data2/pengjinghan/FFSVC_test/scores_fusion/dev/score-repvgg_a1-asnorm_0.3910",
            "/data2/pengjinghan/FFSVC_test/scores_fusion/dev/score-repvgg_a2-asnorm_0.3536"
    ])
    parser.add_argument("--weight", type=float, nargs='+',  help="", 
        # default=[0.25,0.25,0.25,0.25])
        default=[0.3923,0.2394,0.1658,0.2025])
    parser.add_argument("--output_path", type=str, help="", 
        default="/data2/pengjinghan/FFSVC_test/backend_test/fusion/data/scores_4system")

    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    
    scores_paths = args.scores_paths
    weight = args.weight
    output_path = args.output_path
    
    assert len(scores_paths) == len(weight)
    
    system_num = len(scores_paths)
    
    list_pair2score = [dict() for i in range(system_num)]
    pair_list = list()
    for index, (scores_path) in enumerate(scores_paths):
        with open(scores_path, 'r') as rf:
            for line in rf.readlines():
                line = line.strip().split()
                pair = line[0]+" "+line[1]
                score = float(line[-1])
                
                list_pair2score[index][pair] = score

                if index == 0:
                    pair_list.append(pair)
                    
                    
    with open(output_path, 'w') as wf:
        for pair in tqdm(pair_list):
            fuse_score = 0
            for index in range(system_num):
                fuse_score += (list_pair2score[index][pair] * weight[index])
            
            wf.write(f"{pair} {fuse_score}\n")
                    
                


if __name__ == '__main__':
    main()

