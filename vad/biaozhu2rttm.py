#coding=utf-8
# File      :   biaozhu2rttm.py
# Time      :   2021/12/15 15:08:51
# Author    :   Jinghan Peng
# Desciption:   将数据组的标注结果转化为rttm


import os, sys
from decimal import Decimal
import wave
from pydub import AudioSegment


def time2sec(time):
    """将时分秒字符串转化为秒数
    """
    hour, minute, second = time.split(":")
    hour, minute, second = Decimal(hour), Decimal(minute), Decimal(second)
    second += minute * 60 + hour * 3600
    # minute, second = time.split(":")
    # minute, second = Decimal(minute), Decimal(second)
    # second += minute * 60

    return second

def biaozhu2bitime_valid(valid_list, duration):
    """数据组标注结果转化为01时间序列段"""
    duration_ms = int(duration * 1000)
    bitime = [0 for i in range(duration_ms)]
    for beg, end in valid_list:
        beg_ms = int(beg * 1000)
        end_ms = int(end * 1000)
        for i in range(beg_ms, end_ms):
            bitime[i] = 1

    """01序列转化为（开始时间，结束时间，类型）"""
    beg = 0
    last_type = bitime[0]
    new_valid_list = []
    for i in range(len(bitime)):
        if i < len(bitime)-1:
            if bitime[i] != last_type:
                end = i-1
                new_valid_list.append((Decimal(str(beg))/Decimal("1000"), Decimal(str(end))/Decimal("1000"), last_type))
                beg = i
                last_type = bitime[i]
        else: # 最后一毫秒
            end = i-1
            new_valid_list.append((Decimal(str(beg))/Decimal("1000"), Decimal(str(end))/Decimal("1000"), last_type))

    result = []
    for beg, end, typ in new_valid_list:
        if typ == 1:
            result.append((beg, end))
    return result

def valid(in_dir, wav_dir, out_path_gt, out_path_mab, out_dir):
    
    with open(out_path_gt, 'w') as wf1, open(out_path_mab, 'w') as wf2:
        for fn in os.listdir(in_dir):
            # if fn != "004.wavf.txt":
            #     continue
            typs = set()
            if fn.endswith(".txt"):
                # print(fn)
                utt = fn.split('.')[0]
                wav_fp = os.path.join(wav_dir, "{}.wav".format(utt))
                out_wav_fp = os.path.join(out_dir, "{}.wav".format(utt))
                if not os.path.isfile(out_wav_fp):
                    os.system(f"cp {wav_fp} {out_wav_fp}") # 复制音频
                
                audio = AudioSegment.from_file(wav_fp)
                duration = audio.duration_seconds # 音频时长
                duration = Decimal(str(duration))

                with open(os.path.join(in_dir, fn), 'r') as rf:
                    valid_list = []
                    unvalid_list = []
                    for line in rf.readlines():
                        typ, start_time, end_time = line.strip().split()
                        start_sec = time2sec(start_time)
                        end_sec = time2sec(end_time)

                        if typ in ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9",
                                   "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9",
                                   "W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8", "W9"):
                            valid_list.append((start_sec, end_sec))
                        elif typ in ("bobao", "cailing", "mangyin", "yinyue", "bobaocailing", "UNK"):
                            if typ in ("cailing", "yinyue"):
                                typ_ = 2
                            elif typ == "mangyin":
                                typ_ = 3
                            elif typ in ("bobao", "bobaocailing"):
                                typ_ = 4
                            elif typ in ("UNK"):
                                typ_ = 5
                            else:
                                print("[Error] no such typ!")
                            unvalid_list.append((start_sec, end_sec, typ_))
                        else:
                            print("[Error] Unknown type '{}' ".format(typ))
                           
                
                """ -------- 人声转化为rttm -------- """
                rttm_list = []
                valid_list = biaozhu2bitime_valid(valid_list, duration) # 去除重复

                if len(valid_list) == 0:# 若为空，即该条音频没有有效音
                    line = "SPEAKER {} 0 0.000 {} <NA> <NA> 0 <NA> <NA>".format(utt, round(duration, 3))
                    rttm_list.append(line)
                
                elif len(valid_list) ==  1: # 若音频只有一段有效音
                    (start_sec, end_sec) = valid_list[0]

                    if start_sec > 0: # 若该段有效音不是从0开始段
                        line = "SPEAKER {} 0 0.000 {} <NA> <NA> 0 <NA> <NA>".format(utt, start_sec)
                        rttm_list.append(line)

                    line = "SPEAKER {} 0 {} {} <NA> <NA> 1 <NA> <NA>".format(utt, start_sec, end_sec-start_sec)
                    rttm_list.append(line)

                    if end_sec < duration: # 若该段有效音不是一直到音频结束
                        line = "SPEAKER {} 0 {} {} <NA> <NA> 0 <NA> <NA>".format(utt, end_sec, round((duration-end_sec), 3))
                        rttm_list.append(line)

                else: # 若音频有两段以上到有效音段
                    valid_list.sort()
                    for index, (start_sec, end_sec) in enumerate(valid_list):
                        if index == 0: # 第一段有效音
                            if start_sec > 0:
                                line = "SPEAKER {} 0 0.000 {} <NA> <NA> 0 <NA> <NA>".format(utt, start_sec)
                                rttm_list.append(line)
                                line = "SPEAKER {} 0 {} {} <NA> <NA> 1 <NA> <NA>".format(utt, start_sec, end_sec-start_sec)
                                rttm_list.append(line)
                            else:
                                line = "SPEAKER {} 0 {} {} <NA> <NA> 1 <NA> <NA>".format(utt, start_sec, end_sec-start_sec)
                                rttm_list.append(line)
                        else: 
                            last_end_sec = valid_list[index-1][1]
                            line = "SPEAKER {} 0 {} {} <NA> <NA> 0 <NA> <NA>".format(utt, last_end_sec, start_sec-last_end_sec)
                            rttm_list.append(line)
                            line = "SPEAKER {} 0 {} {} <NA> <NA> 1 <NA> <NA>".format(utt, start_sec, end_sec-start_sec)
                            rttm_list.append(line)
                            if index == len(valid_list)-1:
                                if end_sec < duration:
                                    line = "SPEAKER {} 0 {} {} <NA> <NA> 0 <NA> <NA>".format(utt, end_sec, round((duration-end_sec), 3))
                                    rttm_list.append(line)
            
                
                for line in rttm_list: # 写rttm文件中
                    wf1.write(line+"\n")

                
                """ -------- 忙音、播报声、彩铃 转化为rttm -------- """
                rttm_list = []
                if len(unvalid_list) == 0:# 若为空，即该条音频没有特殊音
                    line = "SPEAKER {} 0 0.000 {} <NA> <NA> 0 <NA> <NA>".format(utt, round(duration, 3))
                    rttm_list.append(line)

                elif len(unvalid_list) ==  1: # 若音频只有一段有效音
                    (start_sec, end_sec, typ_) = unvalid_list[0]

                    if start_sec > 0: # 若该段特殊音不是从0开始段
                        line = "SPEAKER {} 0 0.000 {} <NA> <NA> 0 <NA> <NA>".format(utt, start_sec)
                        rttm_list.append(line)

                    line = "SPEAKER {} 0 {} {} <NA> <NA> {} <NA> <NA>".format(utt, start_sec, end_sec-start_sec, typ_)
                    rttm_list.append(line)

                    if end_sec < duration: # 若该段有效音不是一直到音频结束
                        line = "SPEAKER {} 0 {} {} <NA> <NA> 0 <NA> <NA>".format(utt, end_sec, round((duration-end_sec), 3))
                        rttm_list.append(line)

                else: # 若音频有两段以上到有效音段
                    unvalid_list.sort()
                    for index, (start_sec, end_sec, typ_) in enumerate(unvalid_list):
                        if index == 0:
                            if start_sec > 0:
                                line = "SPEAKER {} 0 0.000 {} <NA> <NA> 0 <NA> <NA>".format(utt, start_sec)
                                rttm_list.append(line)
                                line = "SPEAKER {} 0 {} {} <NA> <NA> {} <NA> <NA>".format(utt, start_sec, end_sec-start_sec, typ_)
                                rttm_list.append(line)
                            else:
                                line = "SPEAKER {} 0 {} {} <NA> <NA> {} <NA> <NA>".format(utt, start_sec, end_sec-start_sec, typ_)
                                rttm_list.append(line)
                        else:
                            last_end_sec = unvalid_list[index-1][1]
                            line = "SPEAKER {} 0 {} {} <NA> <NA> 0 <NA> <NA>".format(utt, last_end_sec, start_sec-last_end_sec)
                            rttm_list.append(line)
                            line = "SPEAKER {} 0 {} {} <NA> <NA> {} <NA> <NA>".format(utt, start_sec, end_sec-start_sec, typ_)
                            rttm_list.append(line)
                            if index == len(unvalid_list)-1:
                                if end_sec < duration:
                                    line = "SPEAKER {} 0 {} {} <NA> <NA> 0 <NA> <NA>".format(utt, end_sec, round((duration-end_sec), 3))
                                    rttm_list.append(line)

                for line in rttm_list: # 写rttm文件中
                    wf2.write(line+"\n")


if __name__ == "__main__":


    in_dir   = "/data1/pengjinghan/test_data/nnvad_16k_wx_wav20211202" # 标注文件所在目录路径
    wav_dir  = "/data1/pengjinghan/test_data/nnvad_16k_wx_wav20211202" # 音频文件所在目录路径
    
    out_path_gt  = "/data1/pengjinghan/test_data/16k_testdata_with_raw_biaozhu/wx/data/rttm" # 人声rttm文件路径
    out_path_mab = "/data1/pengjinghan/test_data/16k_testdata_with_raw_biaozhu/wx/data/rttm_sp" # 特殊声音rttm文件路径
    out_dir      = "/data1/pengjinghan/test_data/16k_testdata_with_raw_biaozhu/wx/wav"  # 保存音频目录路径
    
    valid(in_dir, wav_dir, out_path_gt, out_path_mab, out_dir)
    

"""
SPEAKER 23_02 0 0.0 0.014 <NA> <NA> 0 <NA> <NA>
"""