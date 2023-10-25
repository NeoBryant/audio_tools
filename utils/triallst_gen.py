#coding=utf-8
# File      :   triallst_gen.py
# Time      :   2021/08/12 16:01:25
# Author    :   Jinghan Peng
# Desciption:   读取wav.scp，生成trial.lst

from argparse import ArgumentParser

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--wavscp_path", type=str, help="path of wav.scp", 
                        default="/data3/pengjinghan/wx_mh_data/wav.scp")
    parser.add_argument("--triallst_path", type=str, help="path to trial.lst", 
                        default="/data3/pengjinghan/wx_mh_data/trial.lst")

    args = parser.parse_args()
    return args

def main(args):
    in_path  = args.wavscp_path
    out_path = args.triallst_path

    """读取wav.scp"""
    utts = []
    with open(in_path, 'r') as rf:
        for line in rf.readlines():
            utt, fp = line.strip().split()
            utts.append(utt)
    
    """写trial.lst"""
    with open(out_path, 'w') as wf:
        for utt in utts:
            spk = utt.split("-")[0]
            for index in range(len(utts)):
                other_utt = utts[index]
                other_spk = other_utt.split("-")[0]
                isTarget = "target" if spk == other_spk else "nontarget"

                wf.write("{} {} {}\n".format(utt, other_utt, isTarget))


if __name__ == "__main__":
    args = parse_args()
    main(args)