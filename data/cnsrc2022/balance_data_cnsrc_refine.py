import collections
from functools import singledispatch
import os 
import argparse
from multiprocessing import Pool
import math
import random
import vaex
from tqdm import tqdm



def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, #required=True, 
        default="/data1/pengjinghan/CNSRC_fbank81_16k_cut/dataset_nosp/train",
        help="feats.scp file in kaldi format")

    parser.add_argument("--data_save", type=str, #required=True, 
        default="/data1/pengjinghan/CNSRC_fbank81_16k_cut/dataset_nosp/train/instance_balance",
        help="path to save csv and hdf5")
    parser.add_argument("--csv_name", type=str, #required=True, 
        default="train",
        help="csv and hdf5 name")
    parser.add_argument("--batch_size", type=int, #required=True, 
        default=64,
        help="the size of a batch")
    parser.add_argument("--num_spks", type=int, #required=True, 
        default=16,
        help="the number of speakers in a batch")
    parser.add_argument("--num_gpus", type=int, #required=True, 
        default=1,
        help="the number of gpus to train")
    
    
    args = parser.parse_args()
    return args

def read_data(path, value_type="str", is_list=False):
    data_dict = {}
    with open(path, "r") as f:
        for line in f.readlines():
            if is_list:
                utt, info = line.strip().split()[0], line.strip().split()[1:]
            else:
                utt, info = line.strip().split()
            if value_type == "int":
                data_dict[utt] = int(info)
            elif value_type == "float":
                data_dict[utt] = float(info)
            else:
                data_dict[utt] = info
    return data_dict


def lisk_csv(feats_dict, spk2utt_path, spk2int):
    """
    """
    data_list = []
    with open(spk2utt_path, "r") as f:
        for line in f.readlines():
            spk, info = line.strip().split()[0], line.strip().split()[1:]
            label = spk2int[spk]
            info_save = []
            for utt in info:
                info_save.append((utt, feats_dict[utt]))
            data_list.append((label, info_save))
    return data_list

def get_genre2utt_list(utt_list):
    """将utt list中根据场景不同划分列表"""
    genre2utt_list = collections.defaultdict(list)
    for utt, ark in utt_list:
        if utt.startswith("sp0.9-") or utt.startswith("sp1.1-"):
            genre = utt.split('-')[1]
        else:
            genre = utt.split('-')[0]
        genre = genre[genre.find('_')+1:]
        genre2utt_list[genre].append((utt, ark))
    
    return genre2utt_list

def worker(seg, data_save, process_id, batch_size, num_spks_per_batch, num_gpus):
    """
    seg(dict): {spk:[(utt,ark),...],...}
    """
    try:
        
        f_path = os.path.join(data_save, "data_"+str(process_id))
        write_list = list() # [(spk,utt,atk),...]
        
        """read data"""
        total_num_utts = 0 # 总共的utt数量
        spk_to_genre2utt_list = dict() # {spk: {genre:[utt],...}, ...}
        spk2max_num_utts_for_genre = dict() # 每个说话人的各场景utt数量的最大值
        for spk, utt_list in tqdm(seg):
            total_num_utts += len(utt_list)
            genre2utt_list = get_genre2utt_list(utt_list) # 一个spk的{genre:[(utt,ark),...],...}
            genre2utt_list = list(genre2utt_list.items()) # [(genre, [(utt,ark),...]), ...]
            spk_to_genre2utt_list[spk] = genre2utt_list
            
            if spk not in spk2max_num_utts_for_genre:
                spk2max_num_utts_for_genre[spk] = len(utt_list)
            elif len(utt_list) > spk2max_num_utts_for_genre[spk]:
                spk2max_num_utts_for_genre[spk] = len(utt_list)
        

    
        spk_to_genre2utt_list = list(spk_to_genre2utt_list.items()) # [(spk,{genre:[utt]}), ...]
        """process"""
        num_utts_per_spk_per_batch = batch_size//num_spks_per_batch # 每张卡的一个batch里每个说话人的utt数量
        
        print(f" num of spks: {len(spk_to_genre2utt_list)}")
        print(f" num of utts: {total_num_utts}")
        print(f" batch size: {batch_size}")
        print(f" num of spks in a batch: {num_spks_per_batch}")
        print(f" num of utts per spk in a batch: {num_utts_per_spk_per_batch}")
        
        found_utts_set = set() # 记录已经见过的utt，防止部分utt重复写
        spk2found_utts_set = collections.defaultdict(set) # 记录每个spk已写的utt集合 {spk:(utt,...),...}
        for i in range(100): 
            batch_spk_to_genre2utt_list = spk_to_genre2utt_list[i%len(spk_to_genre2utt_list):(i+num_spks_per_batch)%len(spk_to_genre2utt_list)]
            
            for spk, genre2utt_list in batch_spk_to_genre2utt_list:
                max_num_utts_for_genre = spk2max_num_utts_for_genre[spk]
                
                found_num_utts = 0 # 已经得到的utt数量
                while found_num_utts < num_utts_per_spk_per_batch:
                    for genre, utt_list in genre2utt_list:
                        for utt, ark in utt_list:
                            pass
                            
                    
                
            return
        
        print(f" found num of utts: {len(found_utts_set)}")
        
        """write csv"""
        with open(f_path, "w") as f_w:
            for spk, utt, ark in write_list:
                f_w.write(utt + "\t" + ark + "\t" + spk + "\n")
        
        
        
    except Exception as e:
        print(e)

# def worker(seg, data_save, process_id, rate=1):
#     """
#     seg(dict): {spk:[(utt,ark),...],...}
#     """
    
#     try:
#         f_path = os.path.join(data_save, "data_"+str(process_id))
#         write_list = list()
#         with open(f_path, "w") as f_w:
#             for spk, utt_list in tqdm(seg):
#                 # utt_list=[(utt,feat_path),...]
#                 genre2utt_list = get_genre2utt_list(utt_list) # 一个spk的{genre:[utt,...],...}
#                 if "singing" in genre2utt_list and len(genre2utt_list.keys()) >= 2: # 若该spk有singing场景utt，且还有其他场景utt
#                     # singing场景
#                     num_utt_of_other_genre = len(utt_list) - len(genre2utt_list["singing"]) # 除singsing外的其他场景的utt总数
#                     if num_utt_of_other_genre > len(genre2utt_list["singing"]): # 若其他场景的utt数量多于singing场景的utt数量
#                         for utt, ark in genre2utt_list["singing"]:
#                             f_w.write(utt + "\t" + ark + "\t" + spk + "\n")
                        
#                         num_utt_of_each_other_genre = num_utt_of_other_genre // (len(genre2utt_list.keys()) - 1) # 每个场景的utt数量
#                         for genre, sub_utt_list in genre2utt_list.items():
#                             if genre != "singing":
#                                 if len(sub_utt_list) >= num_utt_of_each_other_genre:
#                                     utts = random.sample(sub_utt_list, num_utt_of_each_other_genre)
#                                 else:
#                                     utts = sub_utt_list * math.ceil(num_utt_of_each_other_genre / len(sub_utt_list))
#                                     utts = random.sample(utts, num_utt_of_each_other_genre)
                                    
#                                 for utt, ark in utts:
#                                     f_w.write(utt + "\t" + ark + "\t" + spk + "\n")
#                     else:
#                         for genre, sub_utt_list in genre2utt_list.items():
#                             for utt, ark in sub_utt_list:
#                                 f_w.write(utt + "\t" + ark + "\t" + spk + "\n")
                    
#                 else:# 若该spk没有singing场景或只有singing场景
#                     for genre, sub_utt_list in genre2utt_list.items():
#                         for utt, ark in sub_utt_list:
#                             f_w.write(utt + "\t" + ark + "\t" + spk + "\n")

#     except Exception as e:
#         print(e)
    
def main():
    args = parse_opt()
    data_dir = args.data_dir # 输入目录路径
    data_save = args.data_save # 输出目录路径
    csv_name = args.csv_name # 保存csv和hdf5文件的名字
    num_process = 1 #32 # 并行基础数
    # rate = 1 #0.5

    batch_size = args.batch_size
    num_spks_per_batch = args.num_spks
    num_gpus = args.num_gpus
    assert batch_size%num_spks_per_batch == 0 # 确保batch_size整除num_spks

    os.makedirs(data_save, exist_ok=True)

    feats_scp = os.path.join(data_dir, "feats.scp")
    spk2num_path = os.path.join(data_dir, "spk2num") # 每个spk的utt数量
    spk2utt_path = os.path.join(data_dir, "spk2utt") # 
    spk2int_path = os.path.join(data_dir, "spk2label") # 每个spk的标签

    if not os.path.exists(spk2num_path):
        os.system("python spk2num.py {} {}".format(spk2utt_path, spk2num_path))
    if not os.path.exists(spk2int_path):
        os.system("python spk2int.py {} {}".format(spk2utt_path, spk2int_path))

    feats_dict = read_data(feats_scp)
    spk2num_dict = read_data(spk2num_path, value_type="int")
    spk2int_dict = read_data(spk2int_path)
    spk2info = lisk_csv(feats_dict, spk2utt_path, spk2int_dict)


    
    # uttnum_mean = sum(list(spk2num_dict.values())) / len(spk2num_dict)
    # uttnum_max = max(list(spk2num_dict.values()))
    # uttnum_min = min(list(spk2num_dict.values()))

    # max_len = uttnum_mean + (uttnum_max - uttnum_mean) * rate
    # min_len = uttnum_min + (uttnum_mean - uttnum_min) * (1-rate)
    

    each_num = math.ceil(len(spk2info) / num_process)
    spk2info_process = [spk2info[i:i + each_num] for i in range(0, len(spk2info), each_num)]

    pool = Pool(num_process)
    for i, seg in enumerate(spk2info_process):
        pool.apply_async(worker, args=(seg, data_save, i, batch_size, num_spks_per_batch, num_gpus))
    pool.close()
    pool.join()
    
    return
    csv_data = os.path.join(data_save, "csv")
    hdf5_data = os.path.join(data_save, "hdf5")
    os.makedirs(csv_data, exist_ok=True)
    os.makedirs(hdf5_data, exist_ok=True)
    csv_path = os.path.join(csv_data, csv_name+".csv")
    hdf5_path = os.path.join(hdf5_data, csv_name+".hdf5")

    os.system("cat {}/data_* > {}".format(data_save, csv_path))
    os.system("rm {}/data_*".format(data_save))
    os.system("sed -i '{}' {}".format("1i\\utt_id\tark_path\tlabels", csv_path))

    df = vaex.from_csv(csv_path, sep="\t")
    df.sort(by="labels")
    df.export(hdf5_path)


if __name__ == "__main__":
    main()
