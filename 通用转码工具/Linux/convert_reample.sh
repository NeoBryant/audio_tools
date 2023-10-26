#!/bin/sh

src=$1
dst=$2
samp_rate=$3
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
            echo "resample $src_dir_or_file to $dst_dir_or_file"
            ./common_convert --op=resample --input_file=${src_dir_or_file} --output_file=${dst_dir_or_file} --sample_freq=${samp_rate}
        fi
    done
}

if [ ! -d $dst ]
then
    mkdir -p $dst
fi

getdir $src $dst