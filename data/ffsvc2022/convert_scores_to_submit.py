#coding=utf-8
# File      :   convert_scores_to_submit.py
# Time      :   2022/06/21 16:59:58
# Author    :   Jinghan Peng
# Desciption:   将scores_raw转化为提交的文件格式

import os, sys
from tqdm import tqdm

def main():
    scores_raw_path = "/data2/pengjinghan/FFSVC_test/project/20220617-repvgg_a1-stats_std-sc-vox_ffsvc-refine-eval/scores/enroll_VS_test/score_raw"
    out_dir = "/data2/pengjinghan/FFSVC_test/eval_submit/20220617-repvgg_a1-stats_std-sc-vox_ffsvc-refine-eval"
    os.makedirs(out_dir, exist_ok=True)
    
    scores_txt_path = os.path.join(out_dir, "scores.txt")
    
    # 只取分数，去掉enroll和test
    cmd = "awk '{print $3}' "+scores_raw_path+" > "+scores_txt_path
    os.system(cmd)
    
    # with open(scores_raw_path, 'r') as rf, open(scores_txt_path, 'w') as wf:
    #     for line in tqdm(rf.readlines()):
    #         enroll, test, score = line.strip().split()
    #         wf.write(f"{score}\n")
    
    # # 压缩
    # scores_zip = os.path.join(out_dir, "scores.zip")
    # cmd = f"zip scores.zip {scores_txt_path}"
    # os.system(cmd)


if __name__ == '__main__':
    main()

