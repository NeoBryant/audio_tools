import argparse
import os
import random
import math
import kaldiio
from kaldiio import WriteHelper
from multiprocessing import Pool
from glob import glob
import shutil
import tqdm
import sys
import re
import collections

from data_utils import generate_list_file, KaldiDataset, ChunkSamples


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default="")
    parser.add_argument("--save_ark_dir", type=str, default="/data6/zhengyu/data_1013_shiyan")
    parser.add_argument("--save_scp_dir", type=str, default="/data6/zhengyu/data_1013_shiyan/data_list")
    parser.add_argument("--chunk_type", type=str, help="speaker_balance,sequential", default="sequential")
    parser.add_argument("--chunk_size", type=int, default=1200)
    parser.add_argument("--chunk_min", type=int, default=600)
    parser.add_argument("--chunk_max", type=int, default=1500)
    parser.add_argument("--kaldi_root", type=str, default="/data5/liumin/speakin-kaldi")
    parser.add_argument("--num_process", type=int, default=40)
    args = parser.parse_args()
    return args


def generate_utt2num_frames(feats_sample, frame_path):
    f_w = open(frame_path, "w")
    with open(feats_sample, "r") as f:
        for line in f.readlines():
            line = line.strip().replace("[", " ")
            line = line.replace("]", "")
            lines = re.split('[:\ ]', line)
            start, ends = int(lines[-2]), int(lines[-1])
            num_frames = ends - start + 1
            f_w.write(lines[0] + " " + str(num_frames) + "\n")
    f_w.close()


def convert(cuts_list, save_path):
    f = open(save_path, "w")
    for line in cuts_list:
        line_new = []
        line_new.append(line[0])
        line_new.append(line[1] + "[{}:{}]".format(line[2], line[3]))
        f.write(" ".join(line_new) + "\n")
    f.close()


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


def write_feat(feats_scp, process_id, save_ark_dir, kaldi_root):
    data_save = os.path.join(save_ark_dir, "data_cut." + str(process_id))
    cmd = "{}/src/featbin/copy-feats --compress=true scp:{} ark,scp:{}.ark,{}.scp".format(kaldi_root, feats_scp, data_save, data_save)
    os.system(cmd)
    print("{} cut finished ........".format(process_id))


def data_cut(num_process, cuts_list, save_ark_dir, save_scp_dir, data_name, kaldi_root):
    """
    Args:
        feats_scp: feats.scp of raw data
        save_ark_dir: a directory to save *.ark of cut data
        save_scp_dir: a directory to save feats.scp of cut data
    """
    pool = Pool(num_process)
    for process_id, feats_list in tqdm.tqdm(enumerate(cuts_list)):
        pool.apply_async(write_feat, args=(feats_list, process_id, save_ark_dir, kaldi_root))
    pool.close()
    pool.join()

    scp_list = glob(os.path.join(save_ark_dir, data_name + "*.scp"))
    content = []
    for scp in scp_list:
        with open(scp, 'rb') as f:
            content = content + f.readlines()
    with open(os.path.join(save_scp_dir, 'feats.scp'), 'wb') as f:
        f.writelines(content)


def main():
    args = parse_opt()
    os.makedirs(args.save_ark_dir, exist_ok=True)
    os.makedirs(args.save_scp_dir, exist_ok=True)
    utt2spk_path = os.path.join(args.data_dir, "utt2spk")
    if not os.path.exists(os.path.join(args.save_scp_dir, "feat_samples.scp")):
        dataset = KaldiDataset.load_data_dir(args.data_dir)

        dataset_samples = ChunkSamples(dataset, args.chunk_size, chunk_type=args.chunk_type, chunk_min=args.chunk_min, chunk_max=args.chunk_max, 
                                chunk_num_selection=-1, scale=1, overlap=0., drop_last=False)
        cuts_list = dataset_samples.chunk_samples

        convert(cuts_list, os.path.join(args.save_scp_dir, "feat_samples.scp"))
    cuts_list = split_file(os.path.join(args.save_scp_dir, "feat_samples.scp"), os.path.join(args.save_scp_dir, "split"), args.num_process)
    data_cut(args.num_process, cuts_list, args.save_ark_dir, args.save_scp_dir, data_name="data", kaldi_root=args.kaldi_root)

    feats_path_new = os.path.join(args.save_scp_dir, "feats.scp")
    generate_utt2num_frames(os.path.join(args.save_scp_dir, "feat_samples.scp"), os.path.join(args.save_scp_dir, "utt2num_frames"))
    generate_list_file(feats_path_new, args.save_scp_dir, utt2spk_path, is_cut=True)

if __name__ == "__main__":
    main()
