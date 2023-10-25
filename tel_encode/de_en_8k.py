#coding=utf-8
# File      :   de_en_8k.py
# Time      :   2021/08/23 10:56:06
# Author    :   Jinghan Peng
# Desciption:   16kHz音频编码为8kHz电话信道音频（由郑渝师兄提供，经过一点修改）


import os
import sys
from multiprocessing import Pool, Manager
import subprocess
from random import randint
import time
os.environ['LD_LIBRARY_PATH']='ilbcbin'

def getFileByDir(dir):
	fileList = []
 	uttList  = []
	for r,_, fs in os.walk(dir):
		for f in fs:
			if f.endswith(".wav"):
				fileList.append(os.path.join(r, f))
				uttList.append(f.split(".wav")[0])
	return fileList, uttList

def getFileByScp(dir):
	fileList = []
	uttList  = []
	with open(dir, 'r') as rf:
		for line in rf.readlines():
			utt, path = line.strip().split()
			fileList.append(path)
			uttList.append(utt)
	return fileList, uttList
	
def iterList(l, uttList, num_thread):
    
    # assert (len(l)==len(uttList))
    
	size = len(l)
	step = size // num_thread
	for i in range(num_thread):
		if i == num_thread - 1:
			yield l[i * step:], uttList[i * step:]
		else:
			yield l[i * step: ( i + 1 )* step], uttList[i * step: ( i + 1 )* step]
    
def gsm(file, output):
	filename = os.path.basename(file)
	basename = os.path.basename(os.path.dirname(file))
	basename = basename + filename[:-4]
	cmd =  "ffmpeg -y -i {} -ar 8000 -ac 1 8k-{}.wav".format(file, basename)
	ret = os.system(cmd)
	cmd =  "./getpcm 8k-{}.wav 8k-{}.pcm".format(basename, basename)
	ret = os.system(cmd)
	cmd = "gsm-bin/toast -l 8k-{}.pcm".format(basename)
	ret = os.system(cmd)
	cmd = "gsm-bin/toast -l -d 8k-{}.pcm.gsm".format(basename)
	ret = os.system(cmd)
	cmd = "./getwav 8k-{}.pcm {} 8000".format(basename, output)
	ret = os.system(cmd)
	os.remove("8k-{}.wav".format(basename))
	os.remove("8k-{}.pcm".format(basename))

def amr(file, output):
	model = randint(4, 8)
	filename = os.path.basename(file)
	basename = os.path.basename(os.path.dirname(file))
	basename = basename + filename[:-4]
	cmd =  "ffmpeg -y -i {} -ar 8000 -ac 1 8k-{}.wav".format(file, basename)
	print(cmd)
	ret = os.system(cmd)
	cmd =  "./amrwb-code/encoder {} 8k-{}.wav 8k-{}.bin".format(model, basename, basename)
	ret = os.system(cmd)
	cmd = "./amrwb-code/decoder 8k-{}.bin 8k-{}.pcm".format(basename, basename)
	ret = os.system(cmd)
	cmd = "./getwav 8k-{}.pcm {} 8000".format(basename, output)
	ret = os.system(cmd)
	os.remove("8k-{}.wav".format(basename))
	os.remove("8k-{}.bin".format(basename))
	os.remove("8k-{}.pcm".format(basename))


def g729(file, output):
	basename = os.path.basename(file)
	filename =  basename
	basename = basename[:-4]
	cmd =  "./getpcm {} 8k-{}.pcm".format(file, basename)
	os.system(cmd)
	cmd = "g729abin/coder 8k-{}.pcm 8k-{}.pcm.g729".format(basename, basename)
	os.system(cmd)
	cmd = "g729abin/decoder 8k-{}.pcm.g729 8k-{}.pcm".format(basename,basename)
	os.system(cmd)
	cmd = "./getwav 8k-{}.pcm {} 8000".format(basename, output)
	os.system(cmd)

def ilbc(file, output):
	basename = os.path.basename(file)
	filename =  basename
	basename = basename[:-4]
	cmd =  "./getpcm {} 8k-{}.pcm".format(file, basename)
	os.system(cmd)
	cmd = "ilbcbin/ilbc_test 20 8k-{}.pcm 8k-{}.pcm.ilbc 8k-{}.pcm2".format(basename, basename, basename)
	os.system(cmd)
	cmd = "mv 8k-{}.pcm2 8k-{}.pcm".format(basename,basename)
	os.system(cmd)
	cmd = "./getwav 8k-{}.pcm {} 8000".format(basename, output)
	os.system(cmd)

def work(fileList, uttList, old_path, new_path):
	for index, (file) in enumerate(fileList):
		# respath = file.replace(old_path, new_path)
		new_utt = "{}.wav".format(uttList[index]) # 转码后新音频名
		respath = os.path.join(new_path, new_utt) # 转码新音频路径
		
		assert not os.path.exists(respath) # 确保新音频路径不存在文件，保证不覆盖其他音频文件
  
		os.makedirs(os.path.dirname(respath), exist_ok=True)
		# #os.system("ffmpeg -i {} -ar 8000 -ac 1 {}".format(file, respath))
		r = randint(0, 1) # 随机选择一种方式进行转码
		
		if r == 0:
			gsm(file, respath)
		elif r == 1:
			amr(file, respath)
		#else:
		#    g729(file, respath)


def process(fileList, uttList, old_path, new_path):
    try:
        work(fileList, uttList, old_path, new_path)
    except Exception as e:
        print(e)

if __name__ == '__main__':

	dir_input = "/data1/pengjinghan/between_40_1000/rename/wav-sort_utt_num-first_half.scp" # 输入音频的scp或目录路径
	dir_output = "/data4/pengjinghan/8k_tel_encode"											# 输出路径
	
	if os.path.isdir(dir_input):
		fileList, uttList = getFileByDir(dir_input)
	elif os.path.isfile(dir_input) and dir_input.endswith(".scp"):
		fileList, uttList = getFileByScp(dir_input)
  
	assert len(fileList) == len(uttList)
	
	num_thread = 40
	pool = Pool(num_thread)
	for subFileList, subUttList in iterList(fileList, uttList, num_thread):
		pool.apply_async(process, args=(subFileList, subUttList, dir_input, dir_output))
	pool.close()
	pool.join()
	
	print("Done!")