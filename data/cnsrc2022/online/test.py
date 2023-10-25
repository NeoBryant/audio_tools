#coding=utf-8
# File      :   test.py
# Time      :   2022/04/19 14:46:26
# Author    :   Jinghan Peng
# Desciption:   

import os, sys
from tqdm import tqdm

def main():
    valid_path = "/data3/pengjinghan/exp/data/cnsrc2022/data_list/dataset/valid.json"
    train_path = "/data3/pengjinghan/exp/data/cnsrc2022/data_list/dataset/train.json"
    
    valid_label_set = set()
    with open(valid_path, 'r') as rf:
        for line in tqdm(rf.readlines()):
            line = line.strip()
            data = eval(line)
            valid_label_set.add(data["label"])
    
    print(len(valid_label_set))

    other_label_set = set()
    train_label_set = set()
    with open(train_path, 'r') as rf:
        for line in tqdm(rf.readlines()):
            line = line.strip()
            data = eval(line)
            train_label_set.add(data["label"])
            
            if data["label"] not in valid_label_set:
                other_label_set.add(data["label"])
    
    print(len(train_label_set))
    print(other_label_set)
    print(train_label_set.difference(valid_label_set))

if __name__ == '__main__':
    main()

