#!/bin/sh

src=$1
dst=$2
start_time=$3
duration_time=$4
wav_suffix=".wav"

getdir() {
    for element in `ls $1`
    do
        src_dir_or_file=$1"/"$element
        dst_dir_or_file=$2"/"$element
        if [ -d $src_dir_or_file ] && [ ! -d $dst_dir_or_file ]
        then
            mkdir -p $dst_dir_or_file
        fi
        if [ -d $src_dir_or_file ]
        then
            getdir $src_dir_or_file $dst_dir_or_file
        else
            ./common_convert --op=trim --input_file=${src_dir_or_file} --output_file=${dst_dir_or_file} \
                             --start_time=${start_time} --duration_time=${duration_time}
        fi
    done
}

if [ ! -d $dst ]
then
    mkdir -p $dst
fi

getdir $src $dst