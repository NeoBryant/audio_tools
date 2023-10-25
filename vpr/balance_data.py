import os 
import argparse
from multiprocessing import Pool
import math
import random
import vaex

parser = argparse.ArgumentParser()
parser.add_argument("--data_dir", type=str, required=True, help="feats.scp file in kaldi format")
parser.add_argument("--data_save", type=str, required=True, help="path to save csv and hdf5")
parser.add_argument("--csv_name", type=str, required=True, help="csv and hdf5 name")
args = parser.parse_args()


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


def worker(seg, data_save, process_id, max_len, min_len):
    try:
        f_path = os.path.join(data_save, "data_"+str(process_id))
        f_w = open(f_path, "w")
        for spk, utt_list in seg:
            if len(utt_list) >= max_len:
                utts = random.sample(utt_list, int(max_len))
                for utt, ark in utts:
                    f_w.write(utt + "\t" + ark + "\t" + spk + "\n")
            elif len(utt_list) <= min_len:
                utts = utt_list * math.ceil(min_len / len(utt_list))
                utts = random.sample(utts, int(min_len))
                for utt, ark in utts:
                    f_w.write(utt + "\t" + ark + "\t" + spk + "\n")
            else:
                for utt, ark in utt_list:
                    f_w.write(utt + "\t" + ark + "\t" + spk + "\n")
        f_w.close()
    except Exception as e:
        print(e)
    
def main():
    data_dir = args.data_dir
    data_save = args.data_save
    csv_name = args.csv_name
    num_process = 32
    rate = 0.5


    os.makedirs(data_save, exist_ok=True)

    feats_scp = os.path.join(data_dir, "feats.scp")
    spk2num_path = os.path.join(data_dir, "spk2num")
    spk2utt_path = os.path.join(data_dir, "spk2utt")
    spk2int_path = os.path.join(data_dir, "spk2label")

    if not os.path.exists(spk2num_path):
        os.system("python spk2num.py {} {}".format(spk2utt_path, spk2num_path))
    if not os.path.exists(spk2int_path):
        os.system("python spk2int.py {} {}".format(spk2utt_path, spk2int_path))

    feats_dict = read_data(feats_scp)
    spk2num_dict = read_data(spk2num_path, value_type="int")
    spk2int_dict = read_data(spk2int_path)
    spk2info = lisk_csv(feats_dict, spk2utt_path, spk2int_dict)

    uttnum_mean = sum(list(spk2num_dict.values())) / len(spk2num_dict)
    uttnum_max = max(list(spk2num_dict.values()))
    uttnum_min = min(list(spk2num_dict.values()))

    max_len = uttnum_mean + (uttnum_max - uttnum_mean) * rate
    min_len = uttnum_min + (uttnum_mean - uttnum_min) * (1-rate)


    each_num = math.ceil(len(spk2info) / num_process)
    spk2info_process = [spk2info[i:i + each_num] for i in range(0, len(spk2info), each_num)]

    pool = Pool(num_process)
    for i, seg in enumerate(spk2info_process):
        pool.apply_async(worker, args=(seg, data_save, i, max_len, min_len, ))
    pool.close()
    pool.join()
    
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
