#coding=utf-8
# File      :   cut_mfcc.py
# Time      :   2021/09/03 14:18:55
# Author    :   Jinghan Peng
# Desciption:   根据feats.scp和target.lst，切割特征，生成新的feat和target的ark和scp


import os
import kaldiio
import kaldi_io
import numpy as np
from tqdm import tqdm
import collections

def main():
    featsscp_path  = "/data/pengjinghan/origin_data/mandarin/1c_8kHz_audio/mfcc/data/feats.scp"
    targetlst_path = "/data/pengjinghan/origin_data/mandarin/1c_8kHz_audio/target.lst"
    out_dir        = "/data/pengjinghan/tsvad/segment"
    
    os.makedirs(out_dir, exist_ok=True)

    segment_size = 1600 # 16秒 = 1600帧
    
    """读取target.lst"""
    utt2target = collections.defaultdict(dict)
    with open(targetlst_path, 'r') as rf:
        for line in tqdm(rf.readlines()):
            line = line.strip().split()
            spk = line[0]
            utt = spk[:spk.rfind('_')]
            target = [int(i) for i in line[1:]]
            target = np.array(target, dtype='float32')
            utt2target[utt][spk] = target

    """读取feats.scp，进行切割并写入ark和scp"""
    feat_ark_scp   = f'ark:| copy-feats --compress=true ark:- ark,scp:{out_dir}/feats.ark,{out_dir}/feats.scp'
    target_ark_scp = f'ark:| copy-feats --compress=true ark:- ark,scp:{out_dir}/target.ark,{out_dir}/target.scp'

    with open(featsscp_path, 'r') as rf, \
        kaldi_io.open_or_fd(feat_ark_scp, 'w') as wf1, \
        kaldi_io.open_or_fd(target_ark_scp, 'w') as wf2:
        for line in tqdm(rf.readlines()):
            utt, path = line.strip().split()
            feat = kaldiio.load_mat(path)
            nframes = feat.shape[0]

            target = utt2target[utt]
            spks   = list(target.keys())
            
            steps = nframes//segment_size
            for i in range(steps):
                frame_str = "{:>06}_{:>06}".format(i*segment_size, (i+1)*segment_size)
                # 特征
                new_feat_utt   = f"{utt}-{frame_str}"                
                segment_feat   = feat[i*segment_size:(i+1)*segment_size]
                kaldi_io.write_mat(wf1, segment_feat, key=new_feat_utt)

                # 标签
                for spk in spks:
                    new_target_utt = f"{spk}-{frame_str}"
                    segment_target = np.expand_dims(target[spk][i*segment_size:(i+1)*segment_size], 0) # kaldi的ark必须是2维numpy
                    kaldi_io.write_mat(wf2, segment_target, key=new_target_utt)

    # """查看ark"""
    # /data/liumin/speakin-kaldi/src/featbin/copy-feats ark:target.ark ark,t:- | less


if __name__ == "__main__":
    main()
