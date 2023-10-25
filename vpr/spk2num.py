import os
import sys

spk2utt = sys.argv[1]
spk2num = sys.argv[2]

f_w = open(spk2num, "w")
with open(spk2utt, "r") as f:
    for line in f.readlines():
        lines = line.strip().split()
        spk, lens = lines[0], len(lines)-1
        f_w.write(spk + " " + str(lens) + "\n")
