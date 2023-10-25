#coding=utf-8
# File      :   vad_to_rttm.py
# Time      :   2021/08/10 14:20:20
# Author    :   Jinghan Peng
# Desciption:   读取kaldi能量vad生成的vad.scp，转化为rttm和aliword.txt


import os, sys
import kaldiio
from kaldiio import WriteHelper
from decimal import Decimal
import collections

"""
将kaldi的vad结果转化为rttm和aliword.txt
"""

def vad_to_rttm(utt, vad):
    rttm_list = [] # 存储当前utt的rttm结果

    for index, (isValid) in enumerate(vad):
        isValid = int(isValid)
        if index < len(vad)-1: # 若不是最后一帧
            if index == 0: # 若是第一帧
                start_time = 0
                duration_time = 1
                last_isValid = isValid
            else: # 不是第一帧
                if isValid != last_isValid:
                    line = "SPEAKER "+utt+" 0 "+"{} ".format(float(start_time)/100)+ \
                        "{}".format(float(duration_time)/100)+ \
                        " <NA> <NA> {} <NA> <NA>\n".format(last_isValid)
                    rttm_list.append(line)
                    # ---
                    last_isValid = isValid
                    start_time = index
                    duration_time = 1
                else:
                    duration_time += 1
                    continue
        else: # 最后一帧
            if isValid != last_isValid:
                line = "SPEAKER "+utt+" 0 "+"{} ".format(float(start_time)/100)+ \
                            "{}".format(float(duration_time)/100)+ \
                            " <NA> <NA> {} <NA> <NA>\n".format(last_isValid)
                rttm_list.append(line)
                start_time = index
                duration_time = 1
                line = "SPEAKER "+utt+" 0 "+"{} ".format(float(start_time)/100)+ \
                            "{}".format(float(duration_time)/100)+ \
                            " <NA> <NA> {} <NA> <NA>\n".format(isValid)
                rttm_list.append(line)
            else:
                duration_time += 1
                line = "SPEAKER "+utt+" 0 "+"{} ".format(float(start_time)/100)+ \
                            "{}".format(float(duration_time)/100)+ \
                            " <NA> <NA> {} <NA> <NA>\n".format(isValid)
                rttm_list.append(line)

    return rttm_list


def rttm_to_aliword(rttm_path, out_path, valid_typ, unvalid_typ):
    dic = collections.defaultdict(list)
    with open(rttm_path, 'r') as rf:
        for index, line in enumerate(rf.readlines()):
            line = line.strip().split()
            utt = line[1]
            starttime, durationtime = int(Decimal(line[3])*100), int(Decimal(line[4])*100)
            isValid = bool(int(line[7]))
            
            #vocal_serialnum, cut_serialnum = utt.split('-')
            dic[utt].append([durationtime, isValid])
    
    with open(out_path, 'w') as wf:
        for index, (key, value) in enumerate(dic.items()):
            line = key
            for i, (frames, isValid) in enumerate(value):
                label = valid_typ if isValid else unvalid_typ
                if i < len(value)-1:
                    line += " "+label+" "+str(frames)+" ;"
                else:
                    frames += 2
                    line += " "+label+" "+str(frames)
            wf.write(line+"\n")


def smooth(vad):
    """平滑处理"""
    N = 10
    T1 = 8
    T2 = 10
    
    vad = vad.tolist()
    duration = len(vad)
    smoothed_varray = [0 for i in range(duration)] # 存储平滑后的结果
    inSentence = False    # 是否在句子中
    for index in range(duration):
        if index < duration-N+1:
            window = vad[index:index+N] # 平滑窗
        else:
            window = vad[index:] # 平滑窗
        num_valid_frames   = window.count(1)         # 平滑窗内有效帧数量
        num_unvalid_frames = N - num_valid_frames  # 平滑窗内无效帧数量
        
        if vad[index] and num_valid_frames >= T1: # 若达到进入句子的条件
            if not inSentence: # 若当前状态没在句子中，则修改状态为在句子中
                inSentence = True
        elif num_unvalid_frames >= T2: # 若达到离开句子的条件
            if inSentence: # 若当前状态是在句子中，则修改状态为不在句子中
                inSentence = False
        
        smoothed_varray[index] = 1 if inSentence else 0

    return smoothed_varray

def main(scp_path, rttm_path, isSmooth):
    """通过vad结果，生成rttm
    """
    with open(scp_path, 'r') as rf, open(rttm_path, 'w') as wf:
        for line in rf.readlines():
            utt, vad_path = line.strip().split()
            vad = kaldiio.load_mat(vad_path)
            
            if isSmooth:  # 平滑处理
                vad = smooth(vad)
            
            rttm_list = vad_to_rttm(utt, vad)

            for item in rttm_list:
                wf.write(item)            
    print("Generated rttm file!")
    


if __name__ == "__main__":
    
    isSmooth    = False # 是否平滑
    
    scp_path     = "/data/pengjinghan/tsvad/tmp/kaldi-vad/data/vad.scp"
    rttm_path    = "/data/pengjinghan/tsvad/silence/data/rttm"

    main(scp_path, rttm_path, isSmooth)

    