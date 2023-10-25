#coding=utf-8
# File      :   copy_feats.py
# Time      :   2021/09/08 11:51:22
# Author    :   Jinghan Peng
# Desciption:   将多进程并行提取的feats.ark整合为一个ark和scp，方便服务器间传输文件

import os 
import sys
import tqdm
import math
from multiprocessing import Pool


def split_file(file_path, save_dir, num_process):
    f_name = os.path.basename(file_path)
    os.makedirs(save_dir, exist_ok=True)
    f_r = open(file_path, "r")
    utt_list = f_r.readlines()
    each_num = int(math.ceil(len(utt_list) / num_process))
    utt_process = [utt_list[i:i + each_num] for i in range(0, len(utt_list), each_num)]
    file_list = []
    for i, utt_seg in enumerate(utt_process):
        seg_name = f_name.replace(".scp", "") + "_" + str(i) + ".scp"
        seg_path = os.path.join(save_dir, seg_name)
        with open(seg_path, "w") as f:
            for utt_i in utt_seg:
                f.write(utt_i)
        file_list.append(seg_path)
    f_r.close()
    return file_list


def copy_feats(feats_scp, process_id, save_ark_dir, kaldi_root):
    data_save = os.path.join(save_ark_dir, "data." + str(process_id))
    cmd = "{}/src/featbin/copy-feats --compress=true scp,p:{} ark,scp:{}.ark,{}.scp".format(kaldi_root, feats_scp, data_save, data_save)
    os.system(cmd)
    print("{} cut finished ........".format(process_id))

def worker(feats_scp, process_id, save_ark_dir, kaldi_root):
    try:
        copy_feats(feats_scp, process_id, save_ark_dir, kaldi_root)
    except Exception as e:
        print(e)
        raise e

if __name__ == "__main__":
    feats_scp = sys.argv[1]  # feats.scp的路径
    data_save = sys.argv[2]  # 保存ark和scp的目录路径
    kaldi_root = sys.argv[3] # kaldi的路径
    num_process = int(sys.argv[4]) # 进程数

    os.makedirs(data_save, exist_ok=True)
    split_dir = os.path.join(data_save, "split")
    
    split_list = split_file(feats_scp, os.path.join(split_dir, "feats_split"), num_process)

    pool = Pool(num_process)
    for process_id, feats_list in tqdm.tqdm(enumerate(split_list)):
        pool.apply_async(worker, args=(feats_list, process_id, split_dir, kaldi_root,))
    pool.close()
    pool.join()

    os.system("cat {}/data*.scp > {}".format(split_dir, os.path.join(data_save, "feats.scp")))
