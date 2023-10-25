#coding=utf-8
# File      :   gather_result_eer_minc.py
# Time      :   2022/08/03 09:59:22
# Author    :   Jinghan Peng
# Desciption:   将EER和minDCF输出打分结果整理为表格的形式，方便呈现

import os, sys
import collections
# from colorama import init, Fore, Back, Style


def main():
    in_path = "/data2/pengjinghan/online_dataset_test/test/0802-resnet34-mqmha-sc-ip-vox-offline/results"
    out_path = "/data2/pengjinghan/online_dataset_test/test/0802-resnet34-mqmha-sc-ip-vox-offline/results_table"
    
    dataset_type_list = set()
    model2result = collections.defaultdict(dict)
    model2name = dict()
    with open(in_path, 'r') as rf:
        lines = rf.readlines()
        for index, (line) in enumerate(lines):
            if line.startswith("-------"):
                dataset_type = line.strip().split()[1].split("_enroll")[0]
                if dataset_type.startswith("voxceleb1_"):
                    dataset_type = dataset_type.split("voxceleb1_")[-1]
                # elif dataset_type.startswith(""):
                    
                if dataset_type not in dataset_type_list:
                    dataset_type_list.add(dataset_type)
                
                model_path = lines[index+1].strip()
                model_name = model_path.split('/')[-1].rstrip(".pth") #.split("checkpoint_epoch_")[-1] #.strip("checkpoint_")
                
                clean_model_name = model_name.split("checkpoint_epoch_")[-1]
                if '_' in clean_model_name:
                    epoch, steps = clean_model_name.split('_')
                    epoch, steps = int(epoch), int(steps)
                else:
                    epoch = int(clean_model_name)
                    steps = 0
                
                # print(epoch, steps)
                # return
                
                EER = lines[index+2].strip().split()[2].rstrip(',')
                minDCF = lines[index+3].strip().split()[2]
                
                # model2result[model_name][dataset_type] = {"EER": EER, "minDCF": minDCF}
                model2result[model_name][dataset_type] = {"EER": EER, "minDCF": minDCF}
                model2name[(epoch, steps)] = model_name
                
    dataset_type_list = list(dataset_type_list)
    dataset_type_list.sort() # ['voxceleb1_E', 'voxceleb1_H', 'voxceleb1_O', 'voxceleb1_O_clean', 'voxsrc20_dev', 'voxsrc21_val']
    dataset_type_list = ['O_clean', 'O', 'E', 'H', 'voxsrc20_dev', 'voxsrc21_val']
    
    # print(dataset_type_list)
    
    model_list = list(model2name.keys())
    model_list.sort()
    
    with open(out_path, 'w') as wf:
        line = "{:<30} {}\t\t\t{}\t\t{}\t\t{}\t{}\t{}".format("models",dataset_type_list[0],dataset_type_list[1],
                                                                    dataset_type_list[2],dataset_type_list[3],
                                                                    dataset_type_list[4],dataset_type_list[5])
        print(line)
        wf.write(line+"\n")
        for model in model_list:
            model_name = model2name[model]
            # for dataset_type in dataset_type_list:
            
            line = "{:<30} {} {}\t{} {}\t{} {}\t{} {}\t{} {}\t{} {}".format(model_name, 
                                    model2result[model_name][dataset_type_list[0]]["EER"], 
                                    model2result[model_name][dataset_type_list[0]]["minDCF"],
                                    model2result[model_name][dataset_type_list[1]]["EER"], 
                                    model2result[model_name][dataset_type_list[1]]["minDCF"],
                                    model2result[model_name][dataset_type_list[2]]["EER"], 
                                    model2result[model_name][dataset_type_list[2]]["minDCF"],
                                    model2result[model_name][dataset_type_list[3]]["EER"], 
                                    model2result[model_name][dataset_type_list[3]]["minDCF"],
                                    model2result[model_name][dataset_type_list[4]]["EER"], 
                                    model2result[model_name][dataset_type_list[4]]["minDCF"],
                                    model2result[model_name][dataset_type_list[5]]["EER"], 
                                    model2result[model_name][dataset_type_list[5]]["minDCF"],)
            print(line)
            wf.write(line+"\n")

if __name__ == '__main__':
    main()

