#coding=utf-8
# File      :   diar_rttm_to_vad_rttm.py
# Time      :   2021/08/10 14:27:45
# Author    :   Jinghan Peng
# Desciption:   将话者分离的rttm转化为有效音的rttm


import os
import sys
import collections
from decimal import Decimal

def main(in_dir, out_dir):
    """"将F、M等说话人标签转化为1"""
    dic = collections.defaultdict(list)
    with open(in_dir, 'r') as rf: 
        last_uttid = ""
        for line in rf.readlines():
            line = line.strip('\n').split(' ')
            now_uttid = line[1]
            if now_uttid != last_uttid:
                if now_uttid in dic: continue
                else: last_uttid = now_uttid
            line[3], line[4] = Decimal(line[3]), Decimal(line[4]) 
            line[7] = '1'  # 将AB换为1
            dic[line[1]].append(line)
    
    for uttid, lines in dic.items(): # 以开始时间排序
        lines.sort(key=lambda x: x[3], reverse=False)
    
    """合并重叠时间段"""
    dic_nooverlap = collections.defaultdict(list)
    for uttid, lines in dic.items(): # 对于每个utt
        start_time = lines[0][3]
        final_end_time = 0
        for index, (line) in enumerate(lines):
            now_end_time = line[3]+line[4]
            if now_end_time > final_end_time: 
                final_end_time = now_end_time 
            if index < len(lines)-1:
                next_start_time = lines[index+1][3]
                next_end_time = lines[index+1][3]+lines[index+1][4]
                if final_end_time < next_start_time: # 记录
                    line[3], line[4] = start_time, final_end_time-start_time
                    dic_nooverlap[uttid].append(line)
                    start_time = next_start_time
                else: # 当前结束时间大于下一段有效音开始时间，即有重叠
                    final_end_time = now_end_time if now_end_time > next_end_time else next_end_time
                    continue # 若有重叠
            else: # 最后一个
                line[3], line[4] = start_time, final_end_time-start_time
                dic_nooverlap[uttid].append(line)
                start_time = next_start_time
    
    """添加无效音段"""
    if not os.path.isdir(out_dir[:out_dir.rfind('/')]):
        os.makedirs(out_dir[:out_dir.rfind('/')])
    with open(out_dir, 'w') as wf:
        for uttid, lines in dic_nooverlap.items():
            zero_line = lines[0].copy()
            zero_line[7] = '0'
            start_time = lines[0][3]
            if start_time > Decimal('0'): # 判断0开始是否为有效音
                zero_line[3], zero_line[4] = str(Decimal('0.0')), str(start_time)
                wf.write(' '.join(zero_line)+'\n')
            for i in range(len(lines)):
                # 添加有效音时段
                lines[i][3], lines[i][4] = str(lines[i][3]), str(lines[i][4])
                wf.write(' '.join(lines[i])+'\n')
                if i < len(lines)-1:
                    # 添加无效音时段
                    zero_line[3] = str(Decimal(lines[i][3])+Decimal(lines[i][4]))
                    zero_line[4] = str(Decimal(lines[i+1][3])-Decimal(zero_line[3]))
                    wf.write(' '.join(zero_line)+'\n')


if __name__ == "__main__":
    in_dir  = sys.argv[1] # "/data1/pengjinghan/rttm_script/8k/p1/data/rttm"
    out_dir = sys.argv[2] # "/data1/pengjinghan/rttms_results/p1/rttm_groundtruth_v3"
    main(in_dir, out_dir)


"""
python trans_rttm.py /data1/pengjinghan/rttm_script/8k/p1/data/rttm /data1/pengjinghan/rttms_results/p1/rttm_groundtruth_v3
python trans_rttm.py /data1/pengjinghan/rttm_script/8k/testset-0315/data/rttm /data1/pengjinghan/rttms_results/testset-0315/rttm_groundtruth_v3
python trans_rttm.py /data1/pengjinghan/rttm_script/8k/VoxConverse/data/rttm /data1/pengjinghan/rttms_results/VoxConverse/rttm_groundtruth_v3
"""