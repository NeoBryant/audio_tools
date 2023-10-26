#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import sys

exe_file = "exe\\common_convert.exe"
wav_suffix=".wav"

def process(input_dir, output_dir):
    # 创建文件夹
    input_dir = input_dir.rstrip('\\')
    output_dir = output_dir.rstrip('\\')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    file_list = os.listdir(input_dir)
    for file in file_list:
        file_path = os.path.join(input_dir, file)
        if os.path.isdir(file_path):
            sub_input_dir = file_path
            sub_output_dir = os.path.join(output_dir, file)
            print (file, sub_input_dir)
            process(sub_input_dir, sub_output_dir)
        if os.path.isfile(file_path):
            name, ext = os.path.splitext(file)
            input_file = file_path
            output_name = name + wav_suffix
            output_file = os.path.join(output_dir, output_name)
            param = exe_file + " --op=alaw2wav " + "--input_file=\"" + input_file + "\" --output_file=\"" + output_file + "\""
            os.system(param)

if __name__ == "__main__":
    # execute only if run as a script
    if len(sys.argv) != 3:
        print ('Error, invalid input params')
        print ("Usage: python common_alaw2wav.py input_dir output_dir")
        exit(-1)
    process(sys.argv[1], sys.argv[2])