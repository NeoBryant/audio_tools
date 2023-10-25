#coding=utf-8
# File      :   score.py
# Time      :   2021/08/10 14:31:33
# Author    :   Jinghan Peng
# Desciption:   对vad推理结果进行评估，评估指标包括查准率、召回率、F1 score、错误接受率、错误拒绝率、错误率


import os
from re import L
import sys
import collections
from decimal import Decimal
import argparse
from easydict import EasyDict as edict


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rttm_gt", type=str, #required=True,
                        default="/data1/pengjinghan/test_data/nnvad标注已完成20210806/testset-0315/data/rttm_gt")
    parser.add_argument("--rttm_sp", type=str,
                        default="") 
    parser.add_argument("--rttm_pred", type=str, #required=True,
                        default="/data1/pengjinghan/test_projects/8k_0725/testset-0315/results/rttm_smoothed_new")
    parser.add_argument("--out_path", type=str, #required=True,
                        default="/data1/pengjinghan/test_projects/8k_0725/testset-0315/results/eval_new")
    parser.add_argument("--collar", type=float, 
                        default=0.0)
    
    args = parser.parse_args()
    return args

def get_config(args=None):
    conf = edict()
    if args is not None:
        for key in vars(args):

            setattr(conf, key, getattr(args, key))
    return conf

def get_bitimelist(rttm_file_path):
    dic = collections.defaultdict(list)
    with open(rttm_file_path, 'r') as file:
        for line in file.readlines():
            _, uttid, _, start, duration, _, _, typ, _, _ = line.strip().split()
            start, duration = int(Decimal(start)*1000), int(Decimal(duration)*1000)
            typ = int(typ)
            dic[uttid].append((start, duration, typ))

    for uttid, lines in dic.items(): # 以开始时间排序
        lines.sort(key=lambda x: x[0], reverse=False) 

    bidic = dict() 
    for uttid, timelist in dic.items():
        bilist = []
        for start, duration, typ in timelist:
            bilist += [typ]*duration
        bidic[uttid] = bilist
    return bidic

def add_collars(groundtruth, predicted, collar=0):
    """ non-score collar: 在标注有效音片段边界，(-collar,+collar)范围内，不进行统计;
        <collar> is the no-score zone around reference speaker segment boundaries.  
        (Speaker Diarization output is not evaluated within +/- collar seconds of a reference speaker segment boundary.).
    """
    collar = int(collar*1000) # 将collar从秒变换为毫秒单位
    for utt in set(groundtruth.keys()):
        gbilist = groundtruth[utt]
        pbilist = predicted[utt]

        # collar处理
        index = 0
        while index < len(gbilist)-1:
            if gbilist[index] == 0 and gbilist[index+1] == 1: # 有效音标注句子左边界
                for i in range(collar): # 标注
                    if index+i < len(gbilist): # 标注结果左边界的(index,index+collar)
                        gbilist[index+i] = 0
                        pbilist[index+i] = 0
                    else: break
                    if index-i > 0:
                        pbilist[index-i] = 0
                    else: break
                index += collar
            elif gbilist[index] == 1 and gbilist[index+1] == 0: # 有效音标注句子右边界
                for i in range(collar): # 标注
                    if index-i > 0: # 标注结果右边界(-collar,)
                        gbilist[index-i] = 0
                        pbilist[index-i] = 0
                    else: break
                    if index+i < len(pbilist):
                        pbilist[index+i] = 0
                    else: break
                index += 1
            else:
                index += 1
                
        groundtruth[utt] = gbilist
        predicted[utt]   = pbilist

    return groundtruth, predicted

def validvoice_evaluate(cfg):
    """对有效音进行评估，计算查准率和召回率时只统计含有有效音的音频
    """
    rttm_groundtruth_path = cfg.rttm_gt   # 标注的答案rttm文件路径
    rttm_predicted_path   = cfg.rttm_pred   # nnvad预测结果rttm文件路径
    out_path              = cfg.out_path   # 评估结果输出路径
    collar                = cfg.collar           # 单位：秒

    groundtruth = get_bitimelist(rttm_groundtruth_path) # 标注的答案
    predicted   = get_bitimelist(rttm_predicted_path)     # nnvad预测结果

    assert set(groundtruth.keys()) == set(predicted.keys()) and collar >= 0
    
    """"rttm对齐"""
    for utt in set(groundtruth.keys()):
        gbilist = groundtruth[utt]
        pbilist = predicted[utt]
        # 对齐    
        if len(gbilist) > len(pbilist): 
            pbilist += [0]*(len(gbilist)-len(pbilist))
        elif len(gbilist) < len(pbilist):
            gbilist += [0]*(len(pbilist)-len(gbilist))
        groundtruth[utt] = gbilist 
        predicted[utt]   = pbilist 
        
    """collar处理"""
    if collar > 0: # collar
        groundtruth, predicted = add_collars(groundtruth, predicted, collar=collar) # 添加collar
        print("Add collar...Done!")

    """统计"""
    lst = []
    for utt in set(predicted.keys()):
        gbilist = groundtruth[utt]
        pbilist = predicted[utt]
        
        total_time = len(gbilist) # 音频时长，单位毫秒
        TP, FP, FN = 0, 0, 0
        for i in range(total_time):
            # 有效音
            if gbilist[i] == 1 and pbilist[i] == 1: TP += 1
            elif gbilist[i] == 0 and pbilist[i] == 1: FP += 1
            elif gbilist[i] == 1 and pbilist[i] == 0: FN += 1
            # 非有效音

        if pbilist.count(1) > 0: # 精确率
            precision = float(TP)/pbilist.count(1)  
        else:
            if gbilist.count(1) > 0:
                precision = 0
            else:
                precision = 1
        if gbilist.count(1) > 0: # 召回率
            recall = float(TP)/gbilist.count(1)  
        else:
            recall = 1 
        
        
        F1_score = 2*(recall*precision)/(recall+precision)
        FAR = float(FP)/gbilist.count(0) if gbilist.count(0) > 0 else 0   # 错误接受率
        FRR = 1 - recall                   # 错误拒绝率
        ER = float(FP+FN)/total_time       # 错误率

        hasValidVoice = True if gbilist.count(1) > 0 else False

        lst.append((utt, precision, recall, F1_score, FAR, FRR, ER, hasValidVoice))
    
    """保存评估结果"""
    num_eval = 6 # 评估指标数量：查准率、召回率、F1 score、错误接受率、错误拒绝率，错误率
    with open(out_path, 'w') as wf:
        lst.sort() # 按utt id排序
        line = "{:<10}{:<10}{:<10}{:<10}{:<10}{:<10}{}".format("Precision", "Recall", "F1_score", "FAR", "FRR", "ER","utt id") 
        print(line)
        wf.write(line+"\n")
        sums = [0] * num_eval
        number_hasValidVoice = 0
        for index, (utt, precision, recall, F1_score, FAR, FRR, ER, hasValidVoice) in enumerate(lst):

            line = "{:<10.2%}{:<10.2%}{:<10.2%}{:<10.2%}{:<10.2%}{:<10.2%}{}".format(precision, recall, F1_score, FAR, FRR, ER, utt)  
            print(line)
            wf.write(line+"\n")
            if hasValidVoice:
                number_hasValidVoice += 1
                for i in range(num_eval):
                    sums[i] += lst[index][i+1]

        average = [sums[i]/number_hasValidVoice for i in range(num_eval)]
        line = "{:<10.2%}{:<10.2%}{:<10.2%}{:<10.2%}{:<10.2%}{:<10.2%}{}".format(average[0], average[1], average[2], 
                                                                        average[3], average[4], average[5], "平均值") 
        print(line+"\n")
        wf.write(line+"\n\n")
        
def specialvoice_evaluate(cfg):
    """对忙音、彩铃声、播报声 进行评估，计算查准率和召回率时只统计含有有效音的音频
    """
    rttm_mab_path         = cfg.rttm_sp   # 彩铃、忙音、播报声的标注答案rttm文件路径
    rttm_predicted_path   = cfg.rttm_pred   # nnvad预测结果rttm文件路径
    out_path              = cfg.out_path   # 评估结果输出路径

    groundtruth = get_bitimelist(rttm_mab_path) # 标注的答案
    predicted   = get_bitimelist(rttm_predicted_path)     # nnvad预测结果

    assert set(groundtruth.keys()) == set(predicted.keys())
    
    wavs = list(predicted.keys())
    wavs.sort()

    sum_me = {"sum":0,"num":0}
    sum_be = {"sum":0,"num":0}
    sum_ae = {"sum":0,"num":0}
    lst = []
    for utt in wavs:
        gbilist = groundtruth[utt]
        pbilist = predicted[utt]
        if len(gbilist) > len(pbilist):
            pbilist += [0]*(len(gbilist)-len(pbilist))
        elif len(gbilist) < len(pbilist):
            gbilist += [0]*(len(pbilist)-len(gbilist))

        hasMusic    = True if 2 in gbilist else False
        hasBusytone = True if 3 in gbilist else False
        hasBobao    = True if 4 in gbilist else False

        if hasMusic: # 处理彩铃
            error_music_frames = 0
            music_frames = gbilist.count(2)
            for i in range(len(gbilist)):
                if gbilist[i] == 2 and pbilist[i] == 1:
                    error_music_frames += 1
            lst.append([utt, float(error_music_frames)/music_frames])
            sum_me["sum"] += float(error_music_frames)/music_frames
            sum_me["num"] += 1
        else:
            lst.append([utt, -1])
        
        if hasBusytone: # 处理忙音
            error_busytone_frames = 0
            busytone_frames = gbilist.count(3)
            for i in range(len(gbilist)):
                if gbilist[i] == 3 and pbilist[i] == 1:
                    error_busytone_frames += 1
            lst[-1].append(float(error_busytone_frames)/busytone_frames)
            sum_be["sum"] += float(error_busytone_frames)/busytone_frames
            sum_be["num"] += 1
        else:
            lst[-1].append(-1)

        if hasBobao: # 处理播报声
            error_bobao_frames = 0
            bobao_frames = gbilist.count(4)
            for i in range(len(gbilist)):
                if gbilist[i] == 4 and pbilist[i] == 1:
                    error_bobao_frames += 1
            lst[-1].append(float(error_bobao_frames)/bobao_frames)
            sum_ae["sum"] += float(error_bobao_frames)/bobao_frames
            sum_ae["num"] += 1
        else:
            lst[-1].append(-1)

    with open(out_path, 'a') as wf:
        line = "{:<10}{:<10}{:<10}{}".format("Music_ER", "Busy_ER", "Alert_ER", "utt id") 
        print(line)
        wf.write(line+"\n")
        for utt, me, be, ae in lst:
            me = "{:<.2%}".format(me) if me != -1 else ""
            be = "{:<.2%}".format(be) if be != -1 else ""
            ae = "{:<.2%}".format(ae) if ae != -1 else ""
            line = "{:<10}{:<10}{:<10}{}".format(me, be, ae, utt)  
            print(line)
            wf.write(line+"\n")

        mean_me = "{:<.2%}".format(float(sum_me["sum"])/sum_me["num"]) if sum_me["num"]>0 else ""
        mean_be = "{:<.2%}".format(float(sum_be["sum"])/sum_be["num"]) if sum_be["num"]>0 else ""
        mean_ae = "{:<.2%}".format(float(sum_ae["sum"])/sum_ae["num"]) if sum_ae["num"]>0 else ""

        line = "{:<10}{:<10}{:<10}{}".format(mean_me, mean_be, mean_ae, "平均值")  
        print(line)
        wf.write(line+"\n")

if __name__ == "__main__":
    opt = parse_opt()
    cfg = get_config(opt)


    validvoice_evaluate(cfg) 
    if cfg.rttm_sp != "":
        specialvoice_evaluate(cfg)

"""
"""